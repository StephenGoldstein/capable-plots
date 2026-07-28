"""capable-plots: Capable Labs house style for figures + shared assay curve math.

Quick start::

    import capable_plots as cap

    with cap.nature:                                   # or cap.house
        fig, ax = plt.subplots(figsize=cap.figsize("nature-1col"))
        ax.plot(...)                                   # your normal matplotlib
        cap.style_axis(ax)
    cap.save(fig, "figure1")                           # 300dpi png + editable svg
"""
from __future__ import annotations

from . import assay
from .axes import style_axis
from .color import (
    CAPABLE,
    CAPABLE_PAIR,
    CAPABLE_SEQ,
    COLORBLIND,
    INK,
    PLACEBO,
    Gradient,
    Palette,
    colors,
)
from .io import save
from .style import FIGSIZES, Theme, active, figsize, house, nature, theme

__version__ = "0.1.0"

__all__ = [
    "CAPABLE",
    "CAPABLE_PAIR",
    "CAPABLE_SEQ",
    "COLORBLIND",
    "FIGSIZES",
    "INK",
    "PLACEBO",
    "Gradient",
    "Palette",
    "Theme",
    "__version__",
    "active",
    "assay",
    "colors",
    "figsize",
    "house",
    "nature",
    "save",
    "style_axis",
    "theme",
]
