"""Plotly counterpart of the matplotlib house style.

Registers a plotly template ``"capable_house"`` mirroring ``house.rc``: serif
Times New Roman, transparent backgrounds, ink-black axes with the top/right
lines hidden, no grid, ``CAPABLE`` + ``PLACEBO`` as the categorical colorway.

Usable three ways::

    import plotly.express as px
    import capable_plots as cap

    fig = px.scatter(df, x="dose", y="response", template=cap.plotly_house)
    cap.plotly_save(fig, "figure1")                   # PNG + SVG via kaleido

    import plotly.io as pio                            # or set the global default
    pio.templates.default = cap.plotly_house

    with cap.plotly_house_ctx():                       # or scope it
        ...

Plotly is an optional dependency; the ImportError surfaces only when a helper
is called. Install with ``pip install 'capable-plots[plotly]'``.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from .color import CAPABLE, INK, PLACEBO
from .style import figsize as _figsize_inches

plotly_house = "capable_house"  # the registered template name


def _build_template():
    import plotly.graph_objects as go

    axis = dict(
        showline=True, linecolor=INK, linewidth=1.75,
        ticks="outside", tickcolor=INK, tickwidth=1.5,
        showgrid=False, zeroline=False, mirror=False,
        title=dict(font=dict(size=12)), tickfont=dict(size=12),
    )
    return go.layout.Template(layout=dict(
        font=dict(family="Times New Roman, Palatino, DejaVu Serif, serif",
                  size=12, color=INK),
        title=dict(font=dict(size=14, color=INK)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=[CAPABLE, PLACEBO],
        xaxis=axis, yaxis=axis,
        margin=dict(l=64, r=24, t=48, b=52),
    ))


def _register():
    """Register the ``capable_house`` template. Idempotent; raises ImportError
    with a friendly install hint if plotly is missing."""
    try:
        import plotly.io as pio
    except ImportError as e:
        raise ImportError(
            "plotly is required for capable_plots.plotly helpers — "
            "install with `pip install 'capable-plots[plotly]'`."
        ) from e
    if plotly_house not in pio.templates:
        pio.templates[plotly_house] = _build_template()


@contextmanager
def plotly_house_ctx():
    """Scoped default-template switch; restores the previous default on exit."""
    _register()
    import plotly.io as pio

    prev = pio.templates.default
    pio.templates.default = plotly_house
    try:
        yield plotly_house
    finally:
        pio.templates.default = prev


def plotly_figsize(name: str) -> dict:
    """Return ``{"width": px, "height": px}`` for a named figure size.

    Same presets as :func:`capable_plots.figsize`, converted at 96 dpi (the
    CSS standard). Pass straight to ``fig.update_layout(**...)``.
    """
    w_in, h_in = _figsize_inches(name)  # raises the friendly KeyError from style.py
    return {"width": round(w_in * 96), "height": round(h_in * 96)}


def plotly_save(
    fig,
    name: str | Path,
    *,
    scale: int = 2,
    formats: tuple[str, ...] = ("png", "svg"),
) -> list[Path]:
    """Save ``fig`` as ``name.<ext>`` for each format, mirroring :func:`.io.save`.

    Uses the kaleido static-image backend. ``scale=2`` yields the same apparent
    resolution as matplotlib's 300 dpi default for the standard ``figsize``
    presets.
    """
    _register()  # also validates that plotly is importable
    stem = Path(name)
    stem.parent.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for ext in formats:
        out = stem.with_suffix(f".{ext}")
        fig.write_image(out, scale=scale)
        written.append(out)
    return written


# Register at import so ``cap.plotly_house`` resolves immediately when plotly
# is installed; silently skip when it isn't — the ImportError surfaces later
# when a helper is actually called.
try:
    _register()
except ImportError:
    pass
