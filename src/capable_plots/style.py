"""The Capable house style as an executable matplotlib theme.

``house`` — pitch-deck: serif, transparent background, thick lines.

Usable three ways::

    cap.house.apply()                       # set globally
    with cap.house:                         # scoped, auto-restored
        ...
    fig, ax = plt.subplots(figsize=cap.figsize("house-slide"))

A single theme by design — simplicity first. More styles (e.g. a journal theme)
can be added later as additional ``Theme`` instances without touching callers.
Fonts degrade to DejaVu when the preferred family is unavailable, so figures never
fail to render.
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

# ── Standard figure sizes (inches) ──────────────────────────────────────────────
FIGSIZES = {
    "house-slide": (12.0, 7.0),  # pitch-deck panel
    "square": (5.0, 5.0),
}


def figsize(name: str) -> tuple[float, float]:
    try:
        return FIGSIZES[name]
    except KeyError:
        raise KeyError(f"unknown figsize {name!r}; have {sorted(FIGSIZES)}") from None
