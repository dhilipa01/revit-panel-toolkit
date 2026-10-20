# Reference

## Ribbon buttons

All four buttons sit on one ribbon panel named Panels, on the extension's tab.

| Button | Reads | Writes | Output |
|---|---|---|---|
| Count Panels | Walls: wall type, Area, bounding box, inserts | Nothing | Window with a table by wall type, CSV export |
| Number Panels | Walls: Level, location, wall type, Area | Mark (instance parameter), one transaction | Window with the numbered list, CSV export |
| Panel Cost | Walls, as above | Nothing | Window with a per-panel table, per-panel CSV, budget CSV |
| PT / EN | pyRevit configuration | pyRevit configuration | Dialog |

Scope: the walls in the current selection. With no selection, every wall in the model.

## Revit data used

| Value | Source |
|---|---|
| Net area | Built-in parameter `HOST_AREA_COMPUTED` (Area). Revit subtracts hosted openings |
| Length | Built-in parameter `CURVE_ELEM_LENGTH` (Length) |
| Height | `Element.get_BoundingBox(None)`: Max.Z minus Min.Z. Falls back to Unconnected Height (`WALL_USER_HEIGHT_PARAM`) |
| Full panel size | Length times height, converted to m2 |
| Openings | `HostObject.FindInserts(True, False, False, False)`: doors, windows and rectangular wall openings |
| Level and elevation | The wall's Base Constraint level and its `Elevation` |
| Mark | Built-in parameter `ALL_MODEL_MARK` |
| Irregular wall | `Wall.SketchId` (edited profile, Revit 2022 and later) or `Wall.CrossSection` other than vertical |

Revit stores lengths in feet. The adapter converts to metres and square metres.

## Pricing

```text
cost per panel = area x rate
total          = sum of panel costs x (1 + waste)
per m2         = total / sum of areas
EUR            = total / FX["EUR"]
```

Area is net area by default. The full panel size option uses length times height. For walls with an edited profile or a slanted or tapered cross section, full panel size is an upper bound, and the Panel Cost button warns about them. Walls with an attached top or base are not detected.

## Numbering

Panels are ordered by level elevation, then X, then Y, then element id. Marks are `MARK_PREFIX` followed by a three-digit counter, for example `P-001`. Read-only Mark parameters are skipped and counted.

## CSV formats

Both exports are UTF-8 with a byte order mark. Portuguese uses `;` as the delimiter and a decimal comma. English uses `,` and a decimal point.

| File | Columns |
|---|---|
| Per-panel export | The columns of the window table |
| Budget export | Code, Description, Unit, Qty, Unit price (R$), Total (R$) |

The budget has one line per wall type, then waste, the total in R$, the total in EUR (approximate), the EUR/BRL rate with its date, and the pricing basis.

## Configuration

See the table in the [README](../README.md#configuration).

## Modules

| Module | Role |
|---|---|
| `bauser_core.py` | Pure Python: unit conversion, pricing, numbering, grouping, number formats, CSV. No Revit imports |
| `bauser_revit.py` | Revit adapter: builds panels from walls, writes marks |
| `bauser_ui.py` | WPF results window, falls back to the pyRevit output window if WPF fails |
| `bauser_text.py` | Portuguese and English strings, language setting |
| `results.xaml` | Layout of the results window |

Main functions in `bauser_core.py`:

| Function | Returns |
|---|---|
| `summarize_by_type(panels, basis)` | `[(type, quantity, area_m2, openings)]` |
| `number_plan(panels, prefix)` | `[(panel, mark)]` in numbering order |
| `cost_table(panels, waste, rates, basis)` | per-panel rows and totals |
| `budget_lines(panels, waste, rates, basis)` | one line per wall type and totals |
| `rate_info(type_name, rates)` | `(rate, reference code)` |
| `fmt(value, digits, lang)`, `money(...)`, `eur(...)` | Formatted numbers, `en` or `pt` |
| `write_csv(path, header, rows, delimiter)` | Writes a UTF-8 CSV |

A panel is a dict with the keys `id, mark, type, level, elev, x, y, length_m, height_m, area_m2, gross_m2, openings` and, when read from Revit, `irregular` and `element`.
