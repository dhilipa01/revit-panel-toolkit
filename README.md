<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/media/wordmark-dark.svg">
  <img src="docs/media/wordmark-light.svg" alt="revit-panel-toolkit" width="640">
</picture>

Calculate the number and price of wall panels from the Revit ribbon.

A pyRevit extension for panelised, industrialised construction.

[![CI](https://img.shields.io/github/actions/workflow/status/dhilipa01/revit-panel-toolkit/ci.yml?branch=main&style=flat-square&label=CI&labelColor=14213D&color=3A4A66)](https://github.com/dhilipa01/revit-panel-toolkit/actions/workflows/ci.yml)
[![Licence](https://img.shields.io/badge/licence-MIT-3A4A66?style=flat-square&labelColor=14213D)](LICENSE)
[![pyRevit](https://img.shields.io/badge/pyRevit-IronPython-3A4A66?style=flat-square&labelColor=14213D)](https://github.com/pyrevitlabs/pyRevit)

</div>

```text
$ python examples/panel_budget.py
Mark   Type             Level    Openings   Area m2   Rate R$/m2   Cost R$
P-001  Facade Panel     Level 1         1      6.60       520.00  3,432.00
P-002  Facade Panel     Level 1         0      8.40       520.00  4,368.00
P-003  Partition Panel  Level 1         1      4.82       310.00  1,494.20
P-004  Facade Panel     Level 2         1      6.60       520.00  3,432.00

Basis        net area
Total        R$ 13,362.51  (with 5% waste)
Approx.      € 2,357.45  (EUR/BRL 5.6682, 2026-10-19)
```

The sample runs without Revit, on made-up panels and illustrative prices.

> Status: the logic is covered by tests that run outside Revit. The extension has not yet been run in a live Revit session. See [Verify in Revit](docs/VERIFY_IN_REVIT.md).

## Why

Panelised construction moves the production of prefabricated façade and interior wall panels into a factory. Each panel needs a quantity, a number and a price before production starts, and teams often take these from Revit schedules by hand. This extension reads them from the model, one ribbon button for each step. It is a small piece of a BIM-to-factory design workflow, and the cost estimate also gives an early view of feasibility.

## Features

- Counts panels by wall type, with quantity, openings and area.
- Numbers panels in one undoable transaction, level first, then left to right.
- Prices panels on net area or on full panel size, with a waste factor.
- Shows BRL with an approximate EUR figure.
- Exports a per-panel CSV and a budget CSV with code, description, unit, quantity, unit price and total.
- Switches labels between Portuguese and English from the ribbon.
- Keeps the logic in plain Python, so it runs and is tested outside Revit.

## Installation

Requires Revit with pyRevit, on the default IronPython engine. pyRevit's WPF windows are not supported on the CPython engine.

```bash
git clone https://github.com/dhilipa01/revit-panel-toolkit.git
```

1. In Revit, open the pyRevit tab and choose Settings.
2. Under Custom Extension Directories, add the `src` folder of the clone.
3. Choose Save Settings and Reload.

The extension adds one ribbon tab with four buttons.

## Usage

Select some walls, or select nothing to use every wall in the model, then click a button.

| Button | What it does | Changes the model |
|---|---|---|
| Count Panels | Lists wall types with quantity, openings and area | No |
| Number Panels | Writes `P-001`, `P-002` and so on to the Mark parameter, by level and then by X | Yes, one undoable transaction |
| Panel Cost | Asks for a pricing basis and a waste factor, then shows the cost in BRL and approximate EUR | No |
| PT / EN | Switches the labels between Portuguese and English | No |

Panels are Revit walls. Net area is the wall Area parameter, with openings already subtracted. Full panel size is length times height, openings included. Net area is the default. The full reference is in [docs/REFERENCE.md](docs/REFERENCE.md).

## Examples

Run the sample with no Revit and no dependencies:

```bash
python examples/panel_budget.py                      # net area, English
python examples/panel_budget.py --gross              # full panel size
python examples/panel_budget.py --lang pt budget.csv # Portuguese format, also writes the budget CSV
python examples/panel_budget.py --help
```

The budget CSV, in Portuguese format:

```text
Code;Description;Unit;Qty;Unit price (R$);Total (R$)
;Facade Panel;m2;25,20;520,00;13.104,00
;Partition Panel;m2;6,72;310,00;2.083,20
;Waste (5%);;;;759,36
;TOTAL (R$);;;;15.946,56
;TOTAL (EUR, approx.);;;;2.813,34
```

Set a price and a reference code for a wall type in `src/Bauser.extension/lib/bauser_core.py`:

```python
RATES = {"Facade": (520.0, "")}   # wall type name contains "Facade": R$ 520.00/m2, no reference code
```

## Configuration

All settings are at the top of `src/Bauser.extension/lib/bauser_core.py`.

| Setting | Default | Meaning |
|---|---|---|
| `DEFAULT_RATE` | `490.0` | Placeholder price in R$/m² for wall types with no entry in `RATES` |
| `RATES` | `{}` | `{"type name part": (R$/m², "reference code")}`. The code is only a label |
| `WASTE` | `0.05` | Default waste factor |
| `MARK_PREFIX` | `"P-"` | Prefix for the Mark values |
| `FX` | EUR/BRL 5.6682, 2026-10-19 | BCB PTAX closing rate, refreshed by hand |

The language is stored in the pyRevit configuration and switched with the PT / EN button. Prices and waste in this repository are demonstration values.

## Documentation

- [Reference](docs/REFERENCE.md): buttons, Revit parameters, formulas, CSV formats and module functions
- [Standards and sources](docs/STANDARDS.md): ABNT NBR 16970, SINAPI, the BIM decrees, EU-Mercosur and exchange rates
- [Roadmap](docs/ROADMAP.md)
- [Verify in Revit](docs/VERIFY_IN_REVIT.md)
- [Prompts](docs/PROMPTS.md): how AI was used and how its output was checked

## Development

```bash
python tests/test_core.py      # pricing, numbering, formats, CSV
python tests/test_adapter.py   # the real adapter and scripts against a small fake of pyRevit and the Revit API
```

```text
src/Bauser.extension/   the pyRevit extension (ribbon tab, buttons, lib)
tests/                  tests that run without Revit
examples/               runnable sample
docs/                   reference, standards, roadmap, checklists
```

The code runs on IronPython 2.7 and on CPython 3. It uses no f-strings and no type hints, and accented text uses `u""` literals.

## Contributing

Open an issue before a large change, and run both test files before a pull request. Start commit messages with `feat:`, `fix:`, `docs:` or `refactor:`.

## Licence

MIT. See [LICENSE](LICENSE).
