# Changelog

All notable changes to `capable-plots` are documented here. This project follows
[semantic versioning](https://semver.org/).

## [0.2.0] — unreleased

### Added
- Plotly parity via `capable_plots.plotly`: registers a plotly `Template`
  named `"capable_house"`, exposed as `cap.plotly_house`. Same palette,
  Times New Roman font, transparent backgrounds, hidden top/right axis lines,
  no grid, ink-black axes as the matplotlib `house` theme.
- `cap.plotly_house_ctx()` context manager sets and restores
  `plotly.io.templates.default`, mirroring `with cap.house:` for matplotlib.
- `cap.plotly_save(fig, name)` writes PNG + SVG via the kaleido backend,
  mirroring `cap.save` for matplotlib.
- `cap.plotly_figsize(name)` returns pixel dimensions matching the matplotlib
  `figsize` inch presets (12in × 7in `house-slide`, 5in × 5in `square`).
- New optional dependency extra: `pip install 'capable-plots[plotly]'`
  (installs `plotly>=5.20` + `kaleido>=0.2`).

## [0.1.0] — unreleased

Initial release.

### Added
- Universal styling core: `house` theme (context-manager / global),
  `style_axis`, `save` (300 dpi PNG + editable SVG),
  `figsize`, and `Palette`/`Gradient` color primitives with the Capable brand
  colors and a colorblind-safe default cycle.
- `assay` domain pack: canonical `four_pl` + bounded multi-start `fit_4pl` with
  an explicit `direction=` argument, `FitResult`, and the `dose_response` /
  `group_box` figure helpers.
- `fit_4pl` accepts optional per-parameter bound overrides (`bottom_bounds`,
  `top_bounds`, `logEC50_bounds`) alongside `hill_bounds`, so a single fitter can be
  tuned per assay modality instead of forking the function. Defaults unchanged.
- `Theme.customize(...)` derives a new theme from `house` with semantic knobs
  (`background`, `font`, `font_size`, `line_width`, `palette`) plus a raw-`rc` escape
  hatch. Returns a new theme; the default `house` is never mutated.
