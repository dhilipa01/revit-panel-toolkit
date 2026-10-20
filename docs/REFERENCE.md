# Reference

## Ribbon buttons

All six buttons sit on one ribbon panel named Panels, on the extension's tab.

| Button | Reads | Writes | Output |
|---|---|---|---|
| Count Panels | Walls: wall type, Area, bounding box, inserts | Nothing | Window with a table by wall type, CSV export |
| Number Panels | Walls: Level, location, wall type, Area | Mark (instance parameter), one transaction | Window with the numbered list, CSV export |
| Panel Cost | Walls, as above | Nothing | Window with a per-panel table, per-panel CSV, budget CSV |
| Classify Panels | Wall types and `bauser_config.json` | The classification parameter of each wall type (Classification Number, or Assembly Code when the type has none), one transaction | Window with one row per wall type, the parameter written, CSV export |
| IDS Check | Walls with all their parameters, and an `.ids` file | Nothing | Window with one row per panel and requirement, CSV export |
| PT / EN | pyRevit configuration | pyRevit configuration | Dialog |

Scope: the walls in the current selection. With no selection, every wall in the model.

## Revit data used

| Value | Source |
|---|---|
| Net area | Built-in parameter `HOST_AREA_COMPUTED` (Area). Revit subtracts hosted openings[^area] |
| Length | Built-in parameter `CURVE_ELEM_LENGTH` (Length) |
| Height | `Element.get_BoundingBox(None)`: Max.Z minus Min.Z. Falls back to Unconnected Height (`WALL_USER_HEIGHT_PARAM`)[^bbox] |
| Full panel size | Length times height, converted to m2 |
| Openings | `HostObject.FindInserts(True, False, False, False)`: doors, windows and rectangular wall openings[^findinserts] |
| Level and elevation | The wall's Base Constraint level and its `Elevation` |
| Mark | Built-in parameter `ALL_MODEL_MARK` |
| Irregular wall | `Wall.SketchId` (edited profile, Revit 2022 and later) or `Wall.CrossSection` other than vertical[^wall] |
| Classification code | Type parameter `CLASSIFICATION_CODE` (Classification Number), `OMNICLASS_CODE` (OmniClass Number) before the Revit 2026 API, then `ASSEMBLY_CODE` or `UNIFORMAT_CODE` (Assembly Code) as the fallback[^classparam] |
| All parameters | Every parameter of the wall and its type, by name, for the IDS check |

Revit stores lengths in feet. The adapter converts to metres and square metres.

## Pricing

```text
cost per panel = area x rate
total          = sum of panel costs x (1 + waste)
per m2         = total / sum of areas
EUR            = total / EUR/BRL rate
```

Area is net area by default. The full panel size option uses length times height. For walls with an edited profile or a slanted or tapered cross section, full panel size is an upper bound, and the Panel Cost button warns about them. Walls with an attached top or base are not detected.

## Numbering

Panels are ordered by level elevation, then X, then Y, then element id. Marks are the Mark prefix followed by a three-digit counter, for example `P-001`. Read-only Mark parameters are skipped and counted.

## Classification

Classify Panels looks at the wall type name of every panel. For each configured entry whose name part is found in the type name, it writes the code to the type's classification parameter. Types with no configured code are left alone and counted. The change applies to the wall type, so every wall of that type gets the code, and Ctrl+Z reverts it.

The code goes to the first writable parameter in this order: Classification Number (`CLASSIFICATION_CODE`, or `OMNICLASS_CODE` before the Revit 2026 API), then Assembly Code (`ASSEMBLY_CODE`, or `UNIFORMAT_CODE` before the Revit 2026 API).[^classparam] The result table names the parameter that was written.

The fallback exists because walls are a system family, and an Autodesk Community answer says that Classification Number does not exist for system families.[^community] Assembly Code does exist on wall types, but it is the parameter for a Uniformat code chosen from a list, so an NBR 15965 code in it is a compromise.[^assembly] A read-only parameter is reported as Read-only and not forced, because `Parameter.Set` fails on one.[^setstring]

Three things are not confirmed and need a live Revit session: whether Classification Number appears on a wall type at all, whether either parameter accepts a code that is not in Revit's own classification file, and which Revit versions behave which way. See [Verify in Revit](VERIFY_IN_REVIT.md).

## IDS check

IDS Check reads a buildingSMART IDS 1.0 file[^ids] and tests the panels against it. It is a check on the Revit parameters, not on an IFC file. A model exported to IFC should still be validated with an IFC checker.

| IDS term | What the check does |
|---|---|
| Entity `IFCWALL`, `IFCWALLSTANDARDCASE` | Every panel is a wall. A specification for another entity matches no panel |
| Property | Looks for a Revit parameter of the wall or its type with the same name. Case, spaces and underscores are ignored, so `FireRating` matches `Fire Rating`. The property set is not checked. An empty value counts as missing |
| Classification | Compares the code in the type's classification parameter, and the system named for that wall type in `bauser_config.json` |
| Attribute | `Name` is the wall type name, `Tag` is the Mark, `Description` is the Description parameter. Other attributes are Not checked |
| Cardinality | `required`, `optional` and `prohibited` are handled for requirements |
| Values | A plain value, an enumeration or a pattern. A pattern must match the whole value, as in XML Schema |

Revit translates the names of its built-in parameters, so a Portuguese Revit shows a parameter such as Fire Rating under a Portuguese name, and a property called `FireRating` in the IDS file would not be found. The `ids_aliases` key in `bauser_config.json` lists, for each IDS property name, the Revit parameter names that satisfy it. Autodesk's help in Brazilian Portuguese confirms that the interface is translated, for example Código de montagem for Assembly Code.[^ptb] Which Portuguese name Revit shows for each parameter has to be read from the model.

Anything else gives a Not checked row and never a silent pass: other value restrictions, the facets `partOf` and `material`, and applicability that uses them. Each result row has the panel, the specification, the requirement, the result and a short detail.

## CSV formats

All exports are UTF-8 with a byte order mark. Portuguese uses `;` as the delimiter and a decimal comma. English uses `,` and a decimal point.

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
| `bauser_core.py` | Pure Python: unit conversion, configuration, pricing, numbering, grouping, classification plan, number formats, CSV. No Revit imports |
| `bauser_ids.py` | Pure Python: reads an IDS file and checks panels against it. No Revit imports |
| `bauser_revit.py` | Revit adapter: builds panels from walls, writes marks and classification codes |
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
| `classification_info(type_name, classes)` | `(system, code)` |
| `classification_plan(panels, classes)` | `(plan, missing)`: types that get a code, and types that have none |
| `IDS_ALIASES` | The configured IDS property aliases, passed to `bauser_ids.check` |
| `load_config(path)`, `apply_config(data)`, `parse_config(data)` | Read, apply and check the configuration |
| `fmt(value, digits, lang)`, `money(...)`, `eur(...)` | Formatted numbers, `en` or `pt` |
| `write_csv(path, header, rows, delimiter)` | Writes a UTF-8 CSV |

Functions in `bauser_ids.py`: `parse_ids(source)`, `check(panels, ids, aliases)` and `summarise(rows)`.

## Ribbon language

Each button folder has a `bundle.yaml` with a title and a tooltip in English (`en_us`) and Brazilian Portuguese (`pt_br`). pyRevit shows the one that matches the language of Revit.[^locales] The PT / EN button changes only the labels inside the windows.

A panel is a dict with the keys `id, mark, type, level, elev, x, y, length_m, height_m, area_m2, gross_m2, openings` and, when read from Revit, `irregular`, `properties`, `classification`, `classification_system`, `element` and `type_element`.

[^area]: Jeremy Tammik, "Calculating Gross and Net Wall Areas", The Building Coder. https://jeremytammik.github.io/tbc/a/1296_spatial_calculator.htm. Accessed 2026-10-20. Cited because it states that the wall area parameter has the hosted openings subtracted, which is why that parameter is used as the net figure.
[^bbox]: Autodesk, "Element.BoundingBox Property", Revit 2026 API reference. https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/def2f9f2-b23a-bcea-43a3-e6de41b014c8.htm. Accessed 2026-10-20. Cited for the definition of the bounding box as a box that circumscribes all geometry of the element, which is why it overstates the height of edited, slanted and tapered walls.
[^findinserts]: Autodesk, "HostObject.FindInserts Method", Revit 2026 API reference. https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/58990230-38cb-3af7-fd25-96ed3215a43d.htm. Accessed 2026-10-20. Cited for the signature and the meaning of its four flags.
[^wall]: Autodesk, "Wall Class", Revit 2026 API reference. https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/b5891733-c602-12df-beab-da414b58d608.htm. Accessed 2026-10-20. Cited for the `SketchId` property, which is the invalid element id when a wall has no edited profile, and for the `CrossSection` property.
[^classparam]: revitapidocs.com, "API Changes 2026". https://www.revitapidocs.com/2026/news. Accessed 2026-10-20. Cited because it lists the Revit 2026 API change that renamed `OMNICLASS_CODE` ("OmniClass Number") to `CLASSIFICATION_CODE` ("Classification Number") and `UNIFORMAT_CODE` to `ASSEMBLY_CODE`. The site is a third-party mirror of Autodesk's change list, and the same text is mirrored at https://github.com/adskdimitrii/revit-api-ai-friendly-docs/blob/main/2026/ungrouped/Major-changes-and-renovations-to-the-Revit-API.md. The older names are listed in https://www.revitapidocs.com/2025/fb011c91-be7e-f737-28c7-3f1e1917a0e0.htm.
[^locales]: pyRevit project, `pyrevitlib/pyrevit/coreutils/applocales.py` and the bundle files of `extensions/pyRevitTools.extension`. https://github.com/pyrevitlabs/pyRevit. Read 2026-10-20. Cited because the locale table lists `pt_br` as a code for Brazilian Portuguese, and pyRevit's own extensions give titles and tooltips under `en_us` and `pt_br` keys in `bundle.yaml`, which is the format used here.
[^community]: "Classification Number (Omniclass) NOT working Revit 2026", Autodesk Community, 2026-05-12. https://forums.autodesk.com/t5/revit-architecture-forum/classification-number-omniclass-not-working-revit-2026/td-p/14126346. Accessed 2026-10-20. Cited because an answer in the thread says the classification can only be used in the family editor and does not exist for system families, while keynotes and assembly codes can be used for types of loadable and system families. It is a user's statement and not Autodesk's documentation.
[^setstring]: Autodesk, "Parameter.Set(String) Method", Revit 2026 API reference. https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/956a1e23-cfe5-a60b-1ff9-0e8e33812774.htm. Accessed 2026-10-20. Cited for the rule that the call throws `InvalidOperationException` when the parameter is read-only and returns a Boolean for success. The page does not say whether a particular parameter accepts arbitrary text.
[^ptb]: Autodesk, "Propriedades de tipo de paredes", Revit help in Brazilian Portuguese (2012 release). https://help.autodesk.com/view/RVT/2012/PTB/caas.html?url=caas%2Fvhelp%2Fhelp-dev-autodesk-com%2Fv%2FRevit%2Fptb%2F2012%2FHelp%2F0000-Guia-do-01%2F0325-Construi325%2F0327-Modelage327%2F0328-Paredes328%2F0332-Modifica332%2F0380-Propried380.html. Accessed 2026-10-20. Cited as Autodesk's own Portuguese wording for wall type parameters: Código de montagem, Descrição da montagem, Comentários do tipo and Marcação de tipo. The page is from an old release and the current names should be checked in the Revit version in use.
[^assembly]: Autodesk, "Uniformat Assembly Codes", Revit help. https://help.autodesk.com/cloudhelp/2014/ENU/Revit/files/GUID-5900EA95-9702-4054-A849-C0A70EABB2D1.htm. Accessed 2026-10-20. Cited because it says the Assembly Code parameter is a type property chosen from the Uniformat list, which is why an NBR 15965 code in it is a compromise and Classification Number is tried first.
[^ids]: buildingSMART International, "What is Information Delivery Specification (IDS)". https://www.buildingsmart.org/what-is-information-delivery-specification-ids. Accessed 2026-10-20. The element names, facets and cardinality values used by the reader come from the 1.0 schema, https://raw.githubusercontent.com/buildingSMART/IDS/development/Schema/ids.xsd, and its test cases at https://github.com/buildingSMART/IDS. Cited because the reader follows them.
