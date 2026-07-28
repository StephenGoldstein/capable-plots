"""The recurring assay figures, pre-styled — the "million-times" plots.

These are the only *drawing* helpers in the package. Everything else styles a figure
you draw yourself. They assume the caller has passed already-cleaned data and (for
dose-response) an already-computed :class:`~capable_plots.assay.curves.FitResult`;
parsing, controls and NS/NC handling stay in the caller.
"""
from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes

from ..axes import style_axis
from .curves import FitResult, four_pl


def dose_response(
    ax: Axes,
    x,
    y,
    fit: FitResult,
    *,
    label: str | None = None,
    color: str | None = None,
    annotate: bool = True,
) -> Axes:
    """Plot points + fitted 4PL on a log-dose axis with the standard annotation.

    Annotation format: ``EC50 3.21 nM · Emax 87%`` (Emax omitted when unavailable).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    ax.set_xscale("log")
    ax.scatter(x, y, s=28, color=color, edgecolor="black", linewidth=0.5, zorder=3,
               label=label)

    xs = np.logspace(np.log10(x[x > 0].min()), np.log10(x.max()), 200)
    ax.plot(xs, four_pl(xs, *fit.params), color=color, zorder=2)

    ax.set_xlabel("Dose (nM)")
    if annotate:
        txt = f"EC50 {fit.EC50_nM:.3g} nM"
        if fit.Emax_pct is not None:
            txt += f" · Emax {fit.Emax_pct:.0f}%"
        ax.text(0.03, 0.03, txt, transform=ax.transAxes, va="bottom", ha="left")

    style_axis(ax)
    return ax


def group_box(
    ax: Axes,
    data,
    x: str,
    y: str,
    *,
    order=None,
    palette=None,
) -> Axes:
    """Transparent box (median/IQR) + individual points, per the house-style rules.

    Requires seaborn (install the ``seaborn`` extra). Significance annotation is left
    to the caller so the package stays free of statistical-test policy.
    """
    try:
        import seaborn as sns
    except ImportError as e:  # pragma: no cover - optional dependency
        raise ImportError("group_box needs seaborn: pip install 'capable-plots[seaborn]'") from e

    # hue=x + legend=False is seaborn's forward-compatible way to color by group.
    sns.boxplot(data=data, x=x, y=y, hue=x, legend=False, order=order, ax=ax,
                palette=palette,
                boxprops={"alpha": 0.5, "edgecolor": "black", "linewidth": 1.5},
                showfliers=False)
    sns.stripplot(data=data, x=x, y=y, hue=x, legend=False, order=order, ax=ax,
                  palette=palette,
                  alpha=1.0, edgecolor="black", linewidth=0.5, size=6, jitter=0.15)
    style_axis(ax)
    return ax
