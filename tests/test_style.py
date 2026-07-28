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


def test_svg_export_has_editable_text(tmp_path):
    with cap.house:
        fig, ax = plt.subplots()
        ax.set_title("Editable")
        (svg,) = cap.save(fig, tmp_path / "t", formats=("svg",))
        content = svg.read_text()
    # svg.fonttype='none' → the literal title text appears, not vectorized paths.
    assert "Editable" in content
    plt.close(fig)
