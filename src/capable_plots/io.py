"""Saving conventions — one call, the right outputs every time.

Always writes a 300 dpi raster and an editable vector, with transparency defaulting
to whatever the active theme wants (``house`` transparent, ``nature`` on white).
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
) -> list[Path]:
    """Save ``fig`` as ``name.<ext>`` for each format. Returns written paths.

    ``transparent`` defaults to the active theme's preference (see ``style.active``).
    Parent directories are created as needed.
    """
    if transparent is None:
        active = style.active()
        transparent = active.transparent if active is not None else False

    stem = Path(name)
    stem.parent.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for ext in formats:
        out = stem.with_suffix(f".{ext}")
        fig.savefig(out, dpi=dpi, transparent=transparent, bbox_inches="tight")
        written.append(out)
    return written
