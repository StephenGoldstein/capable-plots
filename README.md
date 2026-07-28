# capable-plots

Capable Labs' house style for matplotlib/seaborn figures, plus the shared
dose-response curve math used across our functional assays.

It is a **styling** library: you draw with normal matplotlib/seaborn, and
`capable-plots` makes it look right and saves it correctly. It is *not* a
plotting wrapper — the only drawing helpers are the handful of figures we make
constantly (dose-response, group box + strip).

## Install

```bash
pip install -e .            # from a clone, for development
pip install -e '.[seaborn]' # if you use group_box
```

## Quick start

```python
import matplotlib.pyplot as plt
import capable_plots as cap

with cap.house:
    fig, ax = plt.subplots(figsize=cap.figsize("house-slide"))
    ax.plot(x, y, color=cap.CAPABLE)
    cap.style_axis(ax)                              # spine/tick cleanup
cap.save(fig, "figure1")                            # 300dpi PNG + editable SVG
```

## Theme

| Theme       | Look                                           | Source style guide  |
|-------------|------------------------------------------------|---------------------|
| `cap.house` | pitch-deck: serif, transparent bg, thick lines | Capable house style |

One theme by design — simplicity first; more can be added later as additional
`Theme` instances. Use as a context manager (`with cap.house:`), globally
(`cap.house.apply()`), or just pull sizes/colors (`cap.figsize(...)`,
`cap.colors(...)`, `cap.CAPABLE`).

## Assay curve math

```python
from capable_plots.assay import curves, plots

fit = curves.fit_4pl(x, y, direction="descending",   # or "ascending"
                     ns_mean=ns, ref_top=ref_top)
plots.dose_response(ax, x, y, fit)                    # log axis + EC50/Emax annotation
```

One canonical 4PL fitter for every modality. Whether the signal rises or falls
with dose is a single explicit `direction=` argument — not three diverging copies.

## Scope / leak-safe boundary

This package holds only universal styling and generic science (textbook 4PL,
standard figure grammar). Program-specific details — targets, control handling,
the results tracker — live in the consuming workspace, which calls this package.
