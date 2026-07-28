# Changelog

All notable changes to `capable-plots` are documented here. This project follows
[semantic versioning](https://semver.org/).

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
