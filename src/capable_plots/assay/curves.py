"""Shared 4-parameter-logistic (4PL) dose-response math.

One canonical implementation for every Capable functional assay. The only real
difference between assay modalities — whether the signal rises or falls with dose —
is an explicit ``direction`` argument, not a silently-diverged copy of the fitter.

The 4PL is written in canonical form so that, regardless of direction:

    bottom = low-dose asymptote      top = high-dose (max-response) asymptote

``Emax_pct`` is expressed relative to a reference compound's ``top`` and its sign
follows ``direction``, so the potency-vs-reference formula is declared exactly once.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import curve_fit

Direction = str  # "ascending" | "descending"


def four_pl(x, bottom, top, logEC50, hill):
    """Canonical 4PL. ``bottom`` = low-dose asymptote, ``top`` = high-dose asymptote."""
    return bottom + (top - bottom) / (1 + 10 ** ((logEC50 - np.log10(x + 1e-12)) * hill))


@dataclass
class FitResult:
    EC50_nM: float
    pEC50: float
    EC50_lo: float
    EC50_hi: float
    Hill: float
    top: float
    bottom: float
    R2: float
    Emax_pct: float | None
    flat_flag: bool
    params: tuple[float, float, float, float]  # (bottom, top, logEC50, hill)


def _r2(y, y_hat) -> float:
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0


def fit_4pl(
    x,
    y,
    *,
    direction: Direction,
    ns_mean: float | None = None,
    ref_top: float | None = None,
    hill_bounds: tuple[float, float] = (0.6, 2.5),
    bottom_bounds: tuple[float, float] | None = None,
    top_bounds: tuple[float, float] | None = None,
    logEC50_bounds: tuple[float, float] | None = None,
    n_starts: int = 6,
    flat_frac: float = 0.10,
) -> FitResult:
    """Bounded, multi-start 4PL fit.

    Parameters
    ----------
    direction : "ascending" or "descending"
        Whether response rises (e.g. β-arrestin RLU) or falls (e.g. IP-One HTRF
        ratio) with dose. Sets initial guesses and the sign of ``Emax_pct``.
    ns_mean : float, optional
        Unstimulated baseline; anchors the Emax calculation.
    ref_top : float, optional
        The reference compound's high-dose asymptote. When given, ``Emax_pct`` is
        reported relative to it; otherwise it is ``None``.
    hill_bounds : (float, float)
        Physical bounds on the Hill slope, clamped to prevent non-physical fits.
    bottom_bounds, top_bounds, logEC50_bounds : (float, float), optional
        Override the fit bounds for the low-dose asymptote, high-dose asymptote, and
        log10(EC50) respectively. Each defaults to a generous window around the observed
        data range. These overrides are what let a single fitter serve every assay
        modality — each caller passes the bounds its assay needs rather than forking the
        function. (logEC50 is in log10 nM.)
    flat_frac : float
        If the fitted response amplitude ``|top - bottom|`` is below this fraction of
        the baseline signal level (``ns_mean``, or the data median when ``ns_mean`` is
        not given), the curve is flagged flat (``flat_flag=True``). Measuring against
        the baseline — not the data's own min/max range — is what lets a genuinely flat,
        noisy curve be caught: its range is only noise.
    """
    if direction not in ("ascending", "descending"):
        raise ValueError(f"direction must be 'ascending' or 'descending', got {direction!r}")

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = np.isfinite(x) & np.isfinite(y) & (x > 0)
    x, y = x[ok], y[ok]
    if x.size < 4:
        raise ValueError("need at least 4 finite positive-dose points to fit a 4PL")

    ymin, ymax = float(y.min()), float(y.max())
    span = ymax - ymin
    logx = np.log10(x)
    lo_log, hi_log = logx.min() - 1.0, logx.max() + 1.0
    min_hill, max_hill = hill_bounds

    # Bounds default to a generous window around the observed range, but each may be
    # overridden per assay — this is what lets one fitter serve every modality.
    pad = 0.5 * span if span > 0 else 1.0
    b_lo, b_hi = bottom_bounds if bottom_bounds is not None else (ymin - pad, ymax + pad)
    t_lo, t_hi = top_bounds if top_bounds is not None else (ymin - pad, ymax + pad)
    e_lo, e_hi = logEC50_bounds if logEC50_bounds is not None else (lo_log, hi_log)
    lo = [b_lo, t_lo, e_lo, min_hill]
    hi = [b_hi, t_hi, e_hi, max_hill]

    if direction == "descending":
        bottom0, top0 = ymax, ymin   # high at low dose, low at high dose
    else:
        bottom0, top0 = ymin, ymax   # low at low dose, high at high dose
    # Keep initial guesses inside whatever bounds are in effect.
    bottom0 = min(max(bottom0, b_lo), b_hi)
    top0 = min(max(top0, t_lo), t_hi)

    best = None
    sweep_lo, sweep_hi = max(e_lo, logx.min()), min(e_hi, logx.max())
    for logec0 in np.linspace(sweep_lo, sweep_hi, n_starts):
        p0 = [bottom0, top0, logec0, 1.0]
        try:
            popt, pcov = curve_fit(four_pl, x, y, p0=p0, bounds=(lo, hi), maxfev=20000)
        except (RuntimeError, ValueError):
            continue
        r2 = _r2(y, four_pl(x, *popt))
        if best is None or r2 > best[2]:
            best = (popt, pcov, r2)

    if best is None:
        raise RuntimeError("4PL fit failed from all starting points")

    popt, pcov, r2 = best
    bottom, top, logEC50, hill = (float(v) for v in popt)
    perr = np.sqrt(np.diag(pcov))
    ec50 = 10 ** logEC50

    baseline = abs(ns_mean) if (ns_mean not in (None, 0)) else abs(float(np.median(y)))
    baseline = max(baseline, 1e-12)
    flat = abs(top - bottom) < flat_frac * baseline

    emax = None
    if ref_top is not None and ns_mean is not None:
        denom = (ns_mean - ref_top) if direction == "descending" else (ref_top - ns_mean)
        if denom != 0:
            num = (ns_mean - top) if direction == "descending" else (top - ns_mean)
            emax = 100.0 * num / denom

    return FitResult(
        EC50_nM=ec50,
        pEC50=-np.log10(ec50 * 1e-9),
        EC50_lo=10 ** max(logEC50 - 1.96 * perr[2], e_lo),
        EC50_hi=10 ** min(logEC50 + 1.96 * perr[2], e_hi),
        Hill=hill,
        top=top,
        bottom=bottom,
        R2=r2,
        Emax_pct=emax,
        flat_flag=flat,
        params=(bottom, top, logEC50, hill),
    )
