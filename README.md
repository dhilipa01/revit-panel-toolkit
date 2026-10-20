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
Mark   Type                 Level     Openings    Area m²   Rate R$/m²    Cost R$
P-001  Facade Panel         Level 1          1       6.60       520.00   3,432.00
P-002  Facade Panel         Level 1          0       8.40       520.00   4,368.00
P-003  Partition Panel      Level 1          1       4.82       310.00   1,494.20
P-004  Facade Panel         Level 2          1       6.60       520.00   3,432.00

Basis        net area
Total        R$ 13,362.51  (with 5% waste)
Approx.      € 2,357.45  (EUR/BRL 5.6682, 2026-10-19)
```

The sample runs without Revit, on made-up panels and illustrative prices.

> Status: the logic is covered by tests that run outside Revit. The extension has not yet been run in a live Revit session. See [Verify in Revit](docs/VERIFY_IN_REVIT.md).

## Why

Panelised construction moves the production of prefabricated façade and interior wall panels into a factory. Each panel needs a quantity, a number and a price before production starts, and teams often take these from Revit schedules by hand. This extension reads them from the model, one ribbon button for each step. It is a small piece of a BIM-to-factory design workflow, and the cost estimate also gives an early view of feasibility.

Brazilian public clients also ask for a classification code on model elements and for a checkable list of required information.[^nbr15965] The Classify Panels and IDS Check buttons cover those two requests without tying the extension to any one company's setup.

## Features

- Counts panels by wall type, with quantity, openings and area.
- Numbers panels in one undoable transaction, level first, then left to right.
- Prices panels on net area or on full panel size, with a waste factor.
- Writes a classification code, such as an NBR 15965 code, to each wall type.[^classify]
- Checks panels against a buildingSMART Information Delivery Specification (IDS) file.[^ids]
- Shows BRL with an approximate EUR figure.
- Exports a per-panel CSV and a budget CSV with code, description, unit, quantity, unit price and total.
- Switches labels between Portuguese and English from the ribbon, and shows the ribbon in the language of Revit.
- Keeps the logic in plain Python, so it runs and is tested outside Revit.

## Installation

Requires Revit with pyRevit, on the default IronPython engine. pyRevit's WPF windows are not supported on the CPython engine.[^pyrevit]

```bash
git clone https://github.com/dhilipa01/revit-panel-toolkit.git
```

1. In Revit, open the pyRevit tab and choose Settings.
2. Under Custom Extension Directories, add the `src` folder of the clone.
3. Choose Save Settings and Reload.

The extension adds one ribbon tab with six buttons.

## Usage

Select some walls, or select nothing to use every wall in the model, then click a button.

| Button | What it does | Changes the model |
|---|---|---|
| Count Panels | Lists wall types with quantity, openings and area | No |
| Number Panels | Writes `P-001`, `P-002` and so on to the Mark parameter, by level and then by X | Yes, one undoable transaction |
| Panel Cost | Asks for a pricing basis and a waste factor, then shows the cost in BRL and approximate EUR | No |
| Classify Panels | Writes the classification code set for each wall type in `bauser_config.json`, to Classification Number or to Assembly Code | Yes, to the wall types, one undoable transaction |
| IDS Check | Asks for an `.ids` file and lists, for each panel, which requirements pass or fail | No |
| PT / EN | Switches the labels between Portuguese and English | No |

Panels are Revit walls. Net area is the wall Area parameter, with openings already subtracted.[^area] Full panel size is length times height, openings included. Net area is the default. The openings count comes from `HostObject.FindInserts`.[^findinserts] The full reference is in [docs/REFERENCE.md](docs/REFERENCE.md).

## Examples

Run the sample with no Revit and no dependencies:

```bash
python examples/panel_budget.py                      # net area, English
python examples/panel_budget.py --gross              # full panel size
python examples/panel_budget.py --lang pt budget.csv # Portuguese labels and format, also writes the budget CSV
python examples/panel_budget.py --help
```

The budget CSV, in Portuguese format:

```text
Código;Descrição;Un.;Qtd.;Preço unit. (R$);Total (R$)
;Painel de divisória;m2;4,82;310,00;1.494,20
;Painel de fachada;m2;21,60;520,00;11.232,00
;Perdas (5%);;;;636,31
;TOTAL (R$);;;;13.362,51
;TOTAL (EUR, aprox.);;;;2.357,45
```

Set a price, a SINAPI reference and a classification code for a wall type in `src/Bauser.extension/bauser_config.json`:

```json
{
  "rates": {
    "Facade": {
      "rate": 520.0,
      "sinapi": "",
      "classification": { "system": "NBR 15965", "code": "3E.02" }
    }
  },
  "ids_aliases": { "FireRating": ["Classificação de resistência ao fogo"] }
}
```

A wall type whose name contains "Facade" is then priced at R$ 520.00/m² and receives the code `3E.02` when you click Classify Panels. The code is a placeholder. The SINAPI reference is only a label.[^sinapi] The alias lets a Revit that shows translated parameter names satisfy an IDS property called `FireRating`. The Portuguese name in the example is illustrative, so use the name your Revit shows.

`examples/panel_requirements.ids` is an example IDS file. It asks that every wall carries a Mark, a classification in the NBR 15965 system and a fire rating. Click IDS Check, pick the file, and the window lists each panel against each requirement.

## Configuration

All settings are in `src/Bauser.extension/bauser_config.json`. Every key is optional, and a mistake in the file produces a message that names the key.

| Key | Default | Meaning |
|---|---|---|
| `default_rate` | `490.0` | Placeholder price in R$/m² for wall types with no entry in `rates` |
| `waste` | `0.05` | Default waste factor |
| `mark_prefix` | `"P-"` | Prefix for the Mark values |
| `fx` | EUR/BRL 5.6682, 2026-10-19 | Closing rate of the Banco Central do Brasil PTAX service, refreshed by hand[^ptax] |
| `rates` | `{}` | For each wall type name part: `rate`, an optional `sinapi` reference and an optional `classification` with `system` and `code` |
| `ids_aliases` | `{}` | For each IDS property name, a list of Revit parameter names that satisfy it |

Reload pyRevit after editing the file. The language of the windows is stored in the pyRevit configuration and switched with the PT / EN button. Prices and waste in this repository are demonstration values.

## Documentation

- [Reference](docs/REFERENCE.md): buttons, Revit parameters, formulas, CSV formats, the IDS check and module functions
- [Standards and sources](docs/STANDARDS.md): ABNT NBR 16970, NBR 15965, IDS, SINAPI, the BIM decrees, EU-Mercosur, exchange rates and Brazilian documentation norms
- [Roadmap](docs/ROADMAP.md)
- [Verify in Revit](docs/VERIFY_IN_REVIT.md)
- [Prompts](docs/PROMPTS.md): how AI was used and how its output was checked
- [Changelog](CHANGELOG.md)

## Development

```bash
python tests/test_core.py      # pricing, numbering, formats, configuration, CSV
python tests/test_ids.py       # the IDS reader and checker
python tests/test_adapter.py   # the real adapter and scripts against a small fake of pyRevit and the Revit API
pip install ruff && ruff check .
```

```text
src/Bauser.extension/   the pyRevit extension: ribbon tab, buttons, lib, bauser_config.json
tests/                  tests that run without Revit
examples/               runnable sample and an example IDS file
docs/                   reference, standards, roadmap, checklists
```

The code runs on IronPython 2.7 and on CPython 3. It uses no f-strings and no type hints, and accented text uses `u""` literals. A tag such as `v0.3.0` runs the release workflow, which tests the code and attaches a zip of the extension.

## Contributing

Open an issue before a large change, and run the three test files and `ruff check .` before a pull request. Start commit messages with `feat:`, `fix:`, `docs:` or `refactor:`.

## Licence

MIT. See [LICENSE](LICENSE).

[^nbr15965]: DNIT, "Caderno de Requisitos Técnicos BIM", 2023. https://www.gov.br/dnit/pt-br/assuntos/planejamento-e-pesquisa/bim-no-dnit/mosaico-de-servicos/documentos-tecnicos-bim/CRTBIM__2023_v2.pdf. Accessed 2026-10-20. Cited because it is a federal client document that names ABNT NBR 15965 as the classification system for model information and asks for a BIM Execution Plan that fixes the coding. The Santa Catarina state specification (https://www.sie.sc.gov.br/webdocs/sie/doc-tecnicos/labim/Caderno%20de%20Especifica%C3%A7%C3%B5es%20de%20Projetos%20em%20BIM_102018.pdf) goes further and requires at least one classification system in the model parameters.
[^classify]: Autodesk, "Parameter.Set(String) Method", Revit 2026 API reference. https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/956a1e23-cfe5-a60b-1ff9-0e8e33812774.htm. Accessed 2026-10-20. Cited because it states that the call returns false or throws when the parameter is read-only, which is why the button reports a read-only parameter instead of forcing it. The rename of the classification parameter in the Revit 2026 API is listed on https://www.revitapidocs.com/2026/news, a third-party site that reproduces Autodesk's list of API changes. An Autodesk Community answer says Classification Number does not exist for system families such as walls (https://forums.autodesk.com/t5/revit-architecture-forum/classification-number-omniclass-not-working-revit-2026/td-p/14126346). That is a user's statement and not Autodesk's, so the button falls back to Assembly Code. Whether either parameter accepts an arbitrary code has not been confirmed in Revit.
[^ids]: buildingSMART International, "What is Information Delivery Specification (IDS)". https://www.buildingsmart.org/what-is-information-delivery-specification-ids. Accessed 2026-10-20. Cited because it defines IDS as a machine-readable statement of the information a model must deliver, which is what the IDS Check button reads. The file structure used by the reader is the published 1.0 schema: https://raw.githubusercontent.com/buildingSMART/IDS/development/Schema/ids.xsd.
[^pyrevit]: pyRevit project, source files `pyrevitlib/pyrevit/forms/_cpy.py` and `_ipy.py`. https://github.com/pyrevitlabs/pyRevit. Read 2026-10-20. Cited because the CPython form module marks `WPFWindow` as unsupported while the IronPython one implements it, which is why this extension has to run on the IronPython engine.
[^area]: Jeremy Tammik, "Calculating Gross and Net Wall Areas", The Building Coder. https://jeremytammik.github.io/tbc/a/1296_spatial_calculator.htm. Accessed 2026-10-20. Cited because it states that the wall area parameter already has the hosted openings subtracted, so it can serve as the net figure. Autodesk Support adds that opening areas cannot be read directly as a parameter: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-create-parameter-that-extract-the-area-of-openings-in-the-walls-in-Revit.html.
[^findinserts]: Autodesk, "HostObject.FindInserts Method", Revit 2026 API reference. https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/58990230-38cb-3af7-fd25-96ed3215a43d.htm. Accessed 2026-10-20. Cited for the signature and return value of the call that lists the doors, windows and rectangular openings hosted in a wall. `Wall` inherits it from `HostObject`.
[^sinapi]: Caixa Econômica Federal, SINAPI. https://www.caixa.gov.br/poder-publico/modernizacao-gestao/sinapi/Paginas/default.aspx. Accessed 2026-10-20. Cited because SINAPI is the monthly Brazilian cost reference that budgets for works paid with federal money must start from, so a budget line needs a place for its composition code. Nothing is imported from SINAPI.
[^ptax]: Banco Central do Brasil, PTAX exchange rate service. https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/. Queried 2026-10-20. Cited as the source of the EUR/BRL closing rate of 2026-10-19. The service needs no key and lists ten currencies, which does not include ARS, UYU or PYG.
