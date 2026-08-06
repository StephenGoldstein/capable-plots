"""Tests for the universal styling core — themes, axis cleanup, save."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import capable_plots as cap


def test_theme_context_restores_rcparams():
    before = matplotlib.rcParams["font.family"]
    with cap.house:
        assert matplotlib.rcParams["font.family"] == ["serif"]
        assert cap.active() is cap.house
    assert matplotlib.rcParams["font.family"] == before
    assert cap.active() is None


def test_house_is_transparent():
    assert cap.house.transparent is True


def test_editable_text_settings():
    with cap.house:
        assert matplotlib.rcParams["svg.fonttype"] == "none"
        assert matplotlib.rcParams["pdf.fonttype"] == 42


def test_customize_returns_new_theme_without_mutating_default():
    light = cap.house.customize(background="white", font="Helvetica",
                                font_size=9, line_width=0.8)
    # default is untouched
    assert cap.house.transparent is True
    assert cap.house.rc["figure.facecolor"] == "none"
    # derived theme reflects the overrides
    assert light.transparent is False
    assert light.rc["figure.facecolor"] == "white"
    assert light.rc["axes.facecolor"] == "white"
    assert light.rc["font.family"] == ["Helvetica", "DejaVu Sans"]
    assert light.rc["font.size"] == 9
    assert light.rc["lines.linewidth"] == 0.8
    assert light.rc["axes.linewidth"] == 0.8


def test_customize_transparent_keyword_and_palette_and_rc_escape_hatch():
    t = cap.house.customize(
        background="transparent",
        palette=cap.colors("colorblind"),
        rc={"figure.dpi": 222},
    )
    assert t.transparent is True
    assert t.rc["figure.facecolor"] == "none"
    assert t.rc["figure.dpi"] == 222  # raw escape hatch honored
    cycle_colors = t.rc["axes.prop_cycle"].by_key()["color"]
    assert cycle_colors == cap.colors("colorblind").as_list()


def test_customized_theme_applies_as_context_manager():
    light = cap.house.customize(background="white", font_size=9)
    with light:
        assert matplotlib.rcParams["font.size"] == 9
        assert cap.active() is light


def test_style_axis_removes_top_right_spines():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3])
    cap.style_axis(ax)
    assert not ax.spines["top"].get_visible()
    assert not ax.spines["right"].get_visible()
    assert ax.spines["left"].get_visible()
    plt.close(fig)


def test_save_writes_png_and_svg(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [3, 2, 1])
    out = cap.save(fig, tmp_path / "fig1")
    names = {p.name for p in out}
    assert names == {"fig1.png", "fig1.svg"}
    for p in out:
        assert p.exists() and p.stat().st_size > 0
    plt.close(fig)


def test_figsize_and_palette_lookup():
    assert cap.figsize("house-slide") == (12.0, 7.0)
    assert len(cap.colors("colorblind")) == 8
    assert cap.colors("capable_pair").as_list() == [cap.PLACEBO, cap.CAPABLE]


def test_vibrant_palette_family_is_parallel():
    # Same length and order across base/light/dark — index i is one hue's triad.
    assert len(cap.VIBRANT) == len(cap.VIBRANT_LIGHT) == len(cap.VIBRANT_DARK) == 9
    assert cap.colors("vibrant").as_list() == cap.VIBRANT.as_list()
    assert cap.colors("vibrant_light").as_list() == cap.VIBRANT_LIGHT.as_list()
    assert cap.colors("vibrant_dark").as_list() == cap.VIBRANT_DARK.as_list()


def test_svg_export_has_editable_text(tmp_path):
    with cap.house:
        fig, ax = plt.subplots()
        ax.set_title("Editable")
        (svg,) = cap.save(fig, tmp_path / "t", formats=("svg",))
        content = svg.read_text()
    # svg.fonttype='none' → the literal title text appears, not vectorized paths.
    assert "Editable" in content
    plt.close(fig)
