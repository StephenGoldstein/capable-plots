"""Color primitives for Capable figures.

First-class ``Palette`` (ordered, discrete) and ``Gradient`` (continuous) objects,
plus the Capable brand colors and a colorblind-safe default cycle. These are
data, not drawing — they work with any matplotlib/seaborn plot.
"""
from __future__ import annotations

from dataclasses import dataclass

from matplotlib.colors import LinearSegmentedColormap

# ── Brand colors (from the Capable pitch-deck house style) ──────────────────────
PLACEBO = "#b2b8b8"   # muted grey — control / placebo group
CAPABLE = "#83a9bc"   # muted blue — treatment / Capable group
INK = "#1a1a1a"       # near-black for text and axes


@dataclass(frozen=True)
class Palette:
    """An ordered, discrete set of colors. Sliceable and reversible."""

    name: str
    colors: tuple[str, ...]

    def __post_init__(self):
        object.__setattr__(self, "colors", tuple(self.colors))

    def __iter__(self):
        return iter(self.colors)

    def __len__(self):
        return len(self.colors)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Palette(f"{self.name}[{key.start}:{key.stop}]", self.colors[key])
        return self.colors[key]

    def __repr__(self):
        return f"Palette({self.name!r}, {list(self.colors)!r})"

    def reversed(self) -> Palette:
        return Palette(f"{self.name}_r", tuple(reversed(self.colors)))

    def as_list(self) -> list[str]:
        return list(self.colors)


@dataclass(frozen=True)
class Gradient:
    """A continuous colormap defined by ordered stop colors."""

    name: str
    colors: tuple[str, ...]

    def __post_init__(self):
        object.__setattr__(self, "colors", tuple(self.colors))

    def to_mpl(self, n: int = 256) -> LinearSegmentedColormap:
        return LinearSegmentedColormap.from_list(self.name, list(self.colors), N=n)

    def reversed(self) -> Gradient:
        return Gradient(f"{self.name}_r", tuple(reversed(self.colors)))


# ── Curated palettes ────────────────────────────────────────────────────────────
# Capable brand pair — placebo vs treatment.
CAPABLE_PAIR = Palette("capable_pair", (PLACEBO, CAPABLE))

# Okabe-Ito: an 8-color qualitative palette that is colorblind-safe.
COLORBLIND = Palette(
    "colorblind",
    (
        "#000000", "#e69f00", "#56b4e9", "#009e73",
        "#f0e442", "#0072b2", "#d55e00", "#cc79a7",
    ),
)

# Sequential gradient anchored on the brand blue.
CAPABLE_SEQ = Gradient("capable_seq", ("#f2f5f7", CAPABLE, "#2f5566"))

_PALETTES = {p.name: p for p in (CAPABLE_PAIR, COLORBLIND)}


def colors(name: str = "colorblind") -> Palette:
    """Look up a named palette (``"capable_pair"`` or ``"colorblind"``)."""
    try:
        return _PALETTES[name]
    except KeyError:
        raise KeyError(f"unknown palette {name!r}; have {sorted(_PALETTES)}") from None
