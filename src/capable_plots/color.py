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

# VIBRANT: an expanded, energetic qualitative palette for pitch decks and other
# high-contrast/marketing contexts where CAPABLE/PLACEBO read as too muted.
# 9 jewel-tone hues spanning the wheel, each with a LIGHT (background-safe) tint
# and a DARK (text-safe on white, ~7:1+ contrast) shade — the base hues alone
# are vivid brand accents, not body-text-safe at small sizes on white
# (CAPABLE/PLACEBO have the same limitation, at ~2.6:1 / ~1.8:1). Parallel
# order/length across all three: index i is the same hue's tint/base/shade.
VIBRANT = Palette("vibrant", (
    "#12B5A6",  # teal
    "#2D7DD2",  # sky
    "#7C5CFC",  # violet
    "#A64AC9",  # plum
    "#D6336C",  # magenta
    "#F0563D",  # coral
    "#F2A93B",  # gold
    "#A0B932",  # chartreuse
    "#2FA84F",  # emerald
))

VIBRANT_LIGHT = Palette("vibrant_light", (
    "#D5F6F3", "#D5E5F6", "#DCD5F6", "#ECD8F3", "#F6D5E1",
    "#F6DAD5", "#F6E9D5", "#EFF4D7", "#D7F4DF",
))

VIBRANT_DARK = Palette("vibrant_dark", (
    "#1F7A71", "#294B70", "#2D1782", "#5A2F6A", "#712841",
    "#7C2B1D", "#7D561C", "#606C2D", "#2E6B3E",
))

_PALETTES = {p.name: p for p in (CAPABLE_PAIR, COLORBLIND, VIBRANT, VIBRANT_LIGHT, VIBRANT_DARK)}


def colors(name: str = "colorblind") -> Palette:
    """Look up a named palette (``"capable_pair"``, ``"colorblind"``, ``"vibrant"``,
    ``"vibrant_light"``, or ``"vibrant_dark"``)."""
    try:
        return _PALETTES[name]
    except KeyError:
        raise KeyError(f"unknown palette {name!r}; have {sorted(_PALETTES)}") from None
