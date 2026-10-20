# Changelog

All notable changes to this project are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [0.3.0] - 2026-10-20

### Added
- Documentation in Brazilian Portuguese: `README.pt-BR.md` and `docs/pt-BR/`, with the same footnoted sources.
- Portuguese ribbon titles and tooltips, one `bundle.yaml` for each button, shown according to the language of Revit.
- `ids_aliases` in `bauser_config.json`, so that a Revit with translated parameter names can satisfy an IDS property.
- A section on Brazilian documentation norms in `docs/STANDARDS.md`.

### Changed
- Classify Panels falls back to Assembly Code when the wall type has no Classification Number, and the result table names the parameter that was written.
- The example script prints its labels and sample panel names in the chosen language.

## [0.2.0] - 2026-10-20

### Added
- Classify Panels button: writes the classification code set for each wall type in `bauser_config.json`, for example an NBR 15965 code, to the type's classification parameter.
- IDS Check button: reads a buildingSMART IDS 1.0 file and checks the panels against it. See the limits in `docs/REFERENCE.md`.
- `bauser_config.json`: default rate, waste, Mark prefix, the EUR/BRL snapshot, and a rate, SINAPI reference and classification per wall type.
- `examples/panel_requirements.ids`: an example IDS file.
- `pyproject.toml` with the ruff configuration, a lint step in CI, and a release workflow that attaches a zip of the extension to a tag.
- `extension.json` for the pyRevit extension manager.

### Changed
- Rates, waste and the Mark prefix are no longer edited in `bauser_core.py`; they come from `bauser_config.json`.

## [0.1.0] - 2026-10-20

### Added
- Count Panels, Number Panels and Panel Cost buttons, a PT / EN switch, and per-panel and budget CSV export.
- Net area and full panel size pricing, openings per panel, and a warning for walls with an edited profile or a slanted or tapered section.
- Tests that run outside Revit, and CI.
