"""The two Capable themes as executable matplotlib styles.

``house``  — pitch-deck: serif, transparent background, thick lines.
``nature`` — Nature Portfolio: Arial/sans, white background, thin lines.

Each ``Theme`` is usable three ways::

    cap.nature.apply()                      # set globally
    with cap.nature:                        # scoped, auto-restored
        ...
    fig, ax = plt.subplots(figsize=cap.figsize("nature-1col"))

Both faithfully encode the two house-style docs; fonts degrade to DejaVu when the
preferred family is unavailable, so figures never fail to render.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import matplotlib as mpl

from .color import CAPABLE, INK, PLACEBO

# The active theme drives transparent-background defaults in ``io.save``.
_active: Theme | None = None


@dataclass
class Theme:
    name: str
    rc: dict = field(default_factory=dict)
    transparent: bool = False

    def apply(self) -> Theme:
        """Set this theme's rcParams globally and mark it active."""
        global _active
        mpl.rcParams.update(self.rc)
        _active = self
        return self

    def __enter__(self):
        self._saved = mpl.rcParams.copy()
        self._prev_active = _active
        self.apply()
        return self

    def __exit__(self, *exc):
        global _active
        mpl.rcParams.update(self._saved)
        _active = self._prev_active
        return False


def active() -> Theme | None:
    """The theme most recently applied / entered, or ``None``."""
    return _active


# ── Shared editable-export settings (Illustrator-friendly) ──────────────────────
_EDITABLE = {
    "svg.fonttype": "none",   # SVG text stays text, not paths
    "pdf.fonttype": 42,       # embed TrueType so text is editable
    "ps.fonttype": 42,
}

# ── house: pitch-deck style ─────────────────────────────────────────────────────
house = Theme(
    name="house",
    transparent=True,
    rc={
        **_EDITABLE,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Palatino", "DejaVu Serif"],
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "axes.linewidth": 1.75,
        "axes.edgecolor": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.facecolor": "none",
        "figure.facecolor": "none",
        "savefig.facecolor": "none",
        "lines.linewidth": 1.75,
        "xtick.major.width": 1.5,
        "ytick.major.width": 1.5,
        "axes.prop_cycle": mpl.cycler(color=[CAPABLE, PLACEBO]),
    },
)

# ── nature: Nature Portfolio style ──────────────────────────────────────────────
nature = Theme(
    name="nature",
    transparent=False,
    rc={
        **_EDITABLE,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 8,
        "axes.titlesize": 8,
        "axes.labelsize": 8,
        "xtick.labelsize": 6,
        "ytick.labelsize": 6,
        "axes.linewidth": 0.75,
        "axes.edgecolor": "#000000",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.facecolor": "#ffffff",
        "figure.facecolor": "#ffffff",
        "savefig.facecolor": "#ffffff",
        "lines.linewidth": 0.75,
        "xtick.major.width": 0.75,
        "ytick.major.width": 0.75,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
    },
)

_THEMES = {t.name: t for t in (house, nature)}


def theme(name: str) -> Theme:
    try:
        return _THEMES[name]
    except KeyError:
        raise KeyError(f"unknown theme {name!r}; have {sorted(_THEMES)}") from None


# ── Standard figure sizes (inches) ──────────────────────────────────────────────
FIGSIZES = {
    "nature-1col": (3.5, 2.6),   # 89 mm
    "nature-2col": (7.2, 4.0),   # 183 mm
    "house-slide": (12.0, 7.0),  # pitch-deck panel
    "square": (5.0, 5.0),
}


def figsize(name: str) -> tuple[float, float]:
    try:
        return FIGSIZES[name]
    except KeyError:
        raise KeyError(f"unknown figsize {name!r}; have {sorted(FIGSIZES)}") from None
