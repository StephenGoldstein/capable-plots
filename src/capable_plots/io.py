"""Saving conventions — one call, the right outputs every time.

Always writes a 300 dpi raster and an editable vector, with transparency defaulting
to what the active theme wants (``house`` → transparent background).
"""
from __future__ import annotations

from pathlib import Path

from matplotlib.figure import Figure

from . import style


def save(
    fig: Figure,
    name: str | Path,
    *,
    dpi: int = 300,
    formats: tuple[str, ...] = ("png", "svg"),
    transparent: bool | None = None,
    facecolor: str | None = None,
) -> list[Path]:
    """Save ``fig`` as ``name.<ext>`` for each format. Returns written paths.

    ``transparent`` defaults to the active theme's preference (see ``style.active``).
    Use ``transparent=True`` for slide-deck figures (background shows through) and
    ``transparent=False`` for standalone/analysis figures that need an opaque
    background. When opaque, the background is ``facecolor`` (default ``"white"``);
    this is set explicitly because the house theme's rcParams set
    ``savefig.facecolor="none"``, so without it even ``transparent=False`` would
    save with a clear background.

    Parent directories are created as needed.
    """
    if transparent is None:
        active = style.active()
        transparent = active.transparent if active is not None else False

    save_facecolor = None if transparent else (facecolor or "white")

    stem = Path(name)
    stem.parent.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for ext in formats:
        out = stem.with_suffix(f".{ext}")
        kw: dict = {}
        if save_facecolor is not None:
            kw["facecolor"] = save_facecolor
            kw["edgecolor"] = "none"
        fig.savefig(out, dpi=dpi, transparent=transparent, bbox_inches="tight", **kw)
        written.append(out)
    return written
