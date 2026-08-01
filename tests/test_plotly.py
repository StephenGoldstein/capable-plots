"""Tests for the plotly counterpart of the house style."""
import pytest

pytest.importorskip("plotly")

import plotly.graph_objects as go
import plotly.io as pio

import capable_plots as cap


def test_plotly_house_registers_template():
    assert cap.plotly_house == "capable_house"
    assert cap.plotly_house in pio.templates


def test_plotly_house_ctx_scopes_default():
    prev = pio.templates.default
    with cap.plotly_house_ctx():
        assert pio.templates.default == cap.plotly_house
    assert pio.templates.default == prev


def test_template_palette_matches_matplotlib_house():
    tmpl = pio.templates[cap.plotly_house]
    assert list(tmpl.layout.colorway) == [cap.CAPABLE, cap.PLACEBO]


def test_template_axes_hide_top_right_and_grid_and_use_ink():
    tmpl = pio.templates[cap.plotly_house]
    for axis in (tmpl.layout.xaxis, tmpl.layout.yaxis):
        assert axis.showgrid is False
        assert axis.zeroline is False
        assert axis.showline is True
        assert axis.mirror is False  # no top/right mirror line
        assert axis.linecolor == cap.INK
        assert axis.tickcolor == cap.INK


def test_template_backgrounds_are_transparent():
    tmpl = pio.templates[cap.plotly_house]
    assert tmpl.layout.paper_bgcolor == "rgba(0,0,0,0)"
    assert tmpl.layout.plot_bgcolor == "rgba(0,0,0,0)"


def test_template_font_family_starts_with_times():
    tmpl = pio.templates[cap.plotly_house]
    assert tmpl.layout.font.family.split(",")[0] == "Times New Roman"


def test_plotly_figsize_returns_pixel_dict():
    fs = cap.plotly_figsize("house-slide")
    assert fs == {"width": 1152, "height": 672}


def test_plotly_figsize_unknown_raises():
    with pytest.raises(KeyError):
        cap.plotly_figsize("bogus")


def test_plotly_save_writes_png_and_svg(tmp_path):
    fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[1, 2, 3])])
    out = cap.plotly_save(fig, tmp_path / "fig1")
    names = {p.name for p in out}
    assert names == {"fig1.png", "fig1.svg"}
    for p in out:
        assert p.exists() and p.stat().st_size > 0


def test_template_used_via_string_kwarg():
    fig = go.Figure(data=[go.Scatter(x=[1, 2], y=[3, 4])], layout=dict(template=cap.plotly_house))
    assert fig.layout.template.layout.paper_bgcolor == "rgba(0,0,0,0)"
