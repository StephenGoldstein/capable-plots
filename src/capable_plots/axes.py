"""Per-axis cleanup — the fiddly spine/tick work factored out of every script.

``style_axis`` enforces the shared house-style axis rules: drop the top and right
spines, force the remaining spines to a clean black intersection at the origin
(no gaps), and keep scientific-notation offset text sized to the tick labels
instead of letting matplotlib shrink it irregularly.
"""
from __future__ import annotations

from matplotlib.axes import Axes

from .color import INK


def style_axis(ax: Axes, *, offset_fontsize: float | None = None) -> Axes:
    """Apply Capable spine/tick conventions to an axis already drawn on.

    Works under either theme — linewidths/fonts come from the active rcParams;
    this only handles the structural cleanup that rcParams cannot express.
    """
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(True)
        ax.spines[side].set_color(INK)
    ax.tick_params(colors=INK)

    # Keep the sci-notation offset text from shrinking out of proportion.
    if offset_fontsize is None:
        offset_fontsize = ax.yaxis.get_ticklabels()[0].get_fontsize() \
            if ax.yaxis.get_ticklabels() else 8
    ax.xaxis.get_offset_text().set_fontsize(offset_fontsize)
    ax.yaxis.get_offset_text().set_fontsize(offset_fontsize)
    ax.grid(False)
    return ax
