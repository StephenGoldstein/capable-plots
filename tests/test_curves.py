"""Tests for the shared 4PL fitter — the logic that had silently diverged across
three copies. Both directions must recover known parameters and get the Emax sign
right."""
import numpy as np
import pytest

from capable_plots.assay import curves


def _doses(top_nM=10_000.0, dilution=4.0, n=8):
    return top_nM / dilution ** np.arange(n)


@pytest.mark.parametrize("direction,bottom,top", [
    ("descending", 1.0, 0.1),   # signal falls with dose (e.g. IP-One ratio)
    ("ascending", 0.1, 1.0),    # signal rises with dose (e.g. β-arrestin RLU)
])
def test_recovers_known_params(direction, bottom, top):
    x = _doses()
    true_logEC50 = np.log10(50.0)   # 50 nM
    true_hill = 1.0
    y = curves.four_pl(x, bottom, top, true_logEC50, true_hill)

    fit = curves.fit_4pl(x, y, direction=direction, ns_mean=bottom)

    assert fit.EC50_nM == pytest.approx(50.0, rel=0.05)
    assert fit.Hill == pytest.approx(true_hill, abs=0.15)
    assert fit.top == pytest.approx(top, abs=0.05)
    assert fit.R2 > 0.99
    assert not fit.flat_flag


def test_emax_sign_follows_direction():
    x = _doses()
    ns = 1.0
    # Descending: high-dose asymptote well below ns → positive activation.
    y_desc = curves.four_pl(x, ns, 0.2, np.log10(50.0), 1.0)
    f_desc = curves.fit_4pl(x, y_desc, direction="descending", ns_mean=ns, ref_top=0.2)
    assert f_desc.Emax_pct == pytest.approx(100.0, abs=5)

    # Ascending: high-dose asymptote well above ns → positive activation.
    y_asc = curves.four_pl(x, ns, 5.0, np.log10(50.0), 1.0)
    f_asc = curves.fit_4pl(x, y_asc, direction="ascending", ns_mean=ns, ref_top=5.0)
    assert f_asc.Emax_pct == pytest.approx(100.0, abs=5)


def test_flat_curve_flagged():
    x = _doses()
    y = np.full_like(x, 0.5) + np.random.default_rng(0).normal(0, 1e-4, x.size)
    fit = curves.fit_4pl(x, y, direction="descending", ns_mean=0.5)
    assert fit.flat_flag


def test_hill_bounds_respected():
    x = _doses()
    y = curves.four_pl(x, 1.0, 0.1, np.log10(50.0), 5.0)  # true hill above cap
    fit = curves.fit_4pl(x, y, direction="descending", ns_mean=1.0, hill_bounds=(0.6, 2.5))
    assert 0.6 <= fit.Hill <= 2.5


def test_bound_overrides_are_respected():
    x = _doses()
    y = curves.four_pl(x, 1.0, 0.1, np.log10(50.0), 1.0)
    # Force EC50 into a narrow window well away from the true 50 nM and confirm the
    # fitter honors the override (the fit is worse, but the constraint holds).
    fit = curves.fit_4pl(
        x, y, direction="descending", ns_mean=1.0,
        logEC50_bounds=(np.log10(200.0), np.log10(400.0)),
    )
    assert 200.0 <= fit.EC50_nM <= 400.0


def test_defaults_unchanged_by_override_support():
    # Same synthetic curve as the recovery test still recovers 50 nM with no overrides.
    x = _doses()
    y = curves.four_pl(x, 1.0, 0.1, np.log10(50.0), 1.0)
    fit = curves.fit_4pl(x, y, direction="descending", ns_mean=1.0)
    assert fit.EC50_nM == pytest.approx(50.0, rel=0.05)


def test_bad_direction_rejected():
    x = _doses()
    y = curves.four_pl(x, 1.0, 0.1, np.log10(50.0), 1.0)
    with pytest.raises(ValueError):
        curves.fit_4pl(x, y, direction="sideways")


def test_too_few_points_rejected():
    with pytest.raises(ValueError):
        curves.fit_4pl([1.0, 2.0, 3.0], [1.0, 0.5, 0.1], direction="descending")
