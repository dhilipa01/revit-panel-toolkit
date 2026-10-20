# Prompts

How AI was used to write this extension, and how its output was checked. The rule: the model drafts, sources verify, tests and Revit decide. No Revit API call is trusted until it is found in Autodesk's documentation or in real pyRevit code.

## Prompt template for Revit API code

```text
Context: pyRevit extension on the IronPython 2.7 engine (WPF windows are not supported on CPython),
Revit <version>. The code must also run on CPython 3 in tests: no f-strings, no type hints,
u"" literals for accented text.
Goal: <one button, one sentence>.
Inputs: <selection or whole model>. Output: <window, parameter write or CSV>.
Constraints: pure logic in lib/bauser_core.py with no Revit imports. Revit calls only in
lib/bauser_revit.py. Writes inside one transaction. Revit lengths are feet, convert to metres.
Ask: list every Revit API member you use, with its class, so each can be checked.
Do not invent members. If unsure, write "unverified".
```

## Checklist for each Revit call

1. Find the member in Autodesk's API documentation and note its class and signature.
2. Find the same idiom in real pyRevit code, such as the pyRevit repository's ReNumber tool and wall tools.
3. Put the logic in the pure module and cover it in `tests/test_core.py`.
4. Run the real adapter and scripts against the fake Revit in `tests/test_adapter.py`.
5. Break the code on purpose and confirm that a test fails. A test that cannot fail checks nothing.
6. Run the button in Revit on a small model with hand-counted answers.

## Worked examples

| Feature | Checked against | What the check changed |
|---|---|---|
| Count Panels | pyRevit `FilteredElementCollector` usage, parameter `HOST_AREA_COMPUTED`[^area] | Wall Area is already net of openings, which led to the net and full panel size options |
| Number Panels | pyRevit ReNumber, which uses `ALL_MODEL_MARK` and `Parameter.Set`[^renumber] | Same parameter, plus a confirm dialog and an undo note |
| Openings column | Autodesk `HostObject.FindInserts`, inherited by `Wall`[^findinserts] | The call was added once the signature was confirmed |
| Full panel size | A pyRevit wall tool uses `get_BoundingBox(None)` with `Min.Z` and `Max.Z`[^wallbbox]; Autodesk defines the box as circumscribing all geometry[^bbox] | Height comes from the bounding box, not from Unconnected Height |
| Irregular walls | Autodesk `Wall.SketchId` and `Wall.CrossSection`[^wall] | A warning for walls where length times height overstates the panel |
| Results window | pyRevit `WPFWindow` and `FindName`, and the CPython form module[^pyrevit] | WPF is unsupported on CPython, so the extension must use IronPython |
| Accented text | IronPython 2.7 string rules | Every accented literal became `u""` |
| Classification code | The Revit API parameter names[^rename], and a community answer on system families[^community] | The first search results showed only the older parameter names. Reading further found the rename in the Revit 2026 API, and a thread saying that walls have no Classification Number, so the adapter tries both names and falls back to Assembly Code |
| IDS parameter names | Autodesk's Portuguese help, which shows translated parameter names[^ptb] | A Portuguese Revit would not match `FireRating`, so the configuration gained an alias table |
| Ribbon titles | pyRevit's locale table and its own `bundle.yaml` files[^locales] | Titles and tooltips are given for `en_us` and `pt_br` and follow the language of Revit |
| IDS check | The published IDS 1.0 schema and its test cases[^idsschema] | The reader follows the real element names and cardinality values. The example file was validated against the schema structure |

## Notes

A first draft written from memory looked right and was still unverified. Reading the pyRevit source found the CPython limit before it could fail in front of a user. Asking the model to list the API members it used gives the checklist above. Prices, waste and the exchange rate are placeholders until a real source supplies them, and the window says so.

Two checks have limits that are worth stating. The IDS example was validated against the schema with the references to XML Schema built-ins relaxed, because the schema validator could not resolve them on their own, so the check covers structure and not the restriction syntax. And the fake Revit in `tests/test_adapter.py` shows that calls have the right shape, not that Revit behaves the same way.

[^area]: Jeremy Tammik, "Calculating Gross and Net Wall Areas", The Building Coder. https://jeremytammik.github.io/tbc/a/1296_spatial_calculator.htm. Accessed 2026-10-20. Cited for the statement that the wall area parameter has the hosted openings subtracted.
[^renumber]: pyRevit project, `extensions/pyRevitTools.extension/pyRevit.tab/Modify.panel/edit2.stack/ReNumber.pushbutton/script.py`. https://github.com/pyrevitlabs/pyRevit. Read 2026-10-20. Cited because it reads and writes the Mark parameter through `ALL_MODEL_MARK` inside a transaction, which is the idiom the Number Panels button follows.
[^findinserts]: Autodesk, "HostObject.FindInserts Method", Revit 2026 API reference. https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/58990230-38cb-3af7-fd25-96ed3215a43d.htm. Accessed 2026-10-20. Cited for the signature and the four flags.
[^wallbbox]: pyRevit project, `extensions/pyRevitTools.extension/pyRevit.tab/Drawing Set.panel/views.stack/Views.pulldown/Create Parallel Section.pushbutton/script.py`. https://github.com/pyrevitlabs/pyRevit. Read 2026-10-20. Cited because it reads `wall.get_BoundingBox(None)` and uses `Min.Z` and `Max.Z`, which is the call this extension uses for the height of a wall.
[^bbox]: Autodesk, "Element.BoundingBox Property", Revit 2026 API reference. https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/def2f9f2-b23a-bcea-43a3-e6de41b014c8.htm. Accessed 2026-10-20. Cited for the definition of the bounding box as one that circumscribes all geometry of the element.
[^wall]: Autodesk, "Wall Class", Revit 2026 API reference. https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/b5891733-c602-12df-beab-da414b58d608.htm. Accessed 2026-10-20. Cited for the `SketchId` and `CrossSection` properties.
[^pyrevit]: pyRevit project, `pyrevitlib/pyrevit/forms/_cpy.py` and `_ipy.py`. https://github.com/pyrevitlabs/pyRevit. Read 2026-10-20. Cited because the CPython module marks `WPFWindow` as unsupported and the IronPython module implements it.
[^rename]: revitapidocs.com, "API Changes 2026". https://www.revitapidocs.com/2026/news. Accessed 2026-10-20. Cited for the Revit 2026 API change that renamed `OMNICLASS_CODE` to `CLASSIFICATION_CODE` and `UNIFORMAT_CODE` to `ASSEMBLY_CODE`. The site is a third-party mirror of Autodesk's change list. The older names are in the 2025 enumeration listing at https://www.revitapidocs.com/2025/fb011c91-be7e-f737-28c7-3f1e1917a0e0.htm.
[^community]: "Classification Number (Omniclass) NOT working Revit 2026", Autodesk Community, 2026-05-12. https://forums.autodesk.com/t5/revit-architecture-forum/classification-number-omniclass-not-working-revit-2026/td-p/14126346. Accessed 2026-10-20. Cited for an answer saying that the classification does not exist for system families. It is a user's statement and not Autodesk's documentation.
[^ptb]: Autodesk, "Propriedades de tipo de paredes", Revit help in Brazilian Portuguese (2012 release). https://help.autodesk.com/view/RVT/2012/PTB/caas.html?url=caas%2Fvhelp%2Fhelp-dev-autodesk-com%2Fv%2FRevit%2Fptb%2F2012%2FHelp%2F0000-Guia-do-01%2F0325-Construi325%2F0327-Modelage327%2F0328-Paredes328%2F0332-Modifica332%2F0380-Propried380.html. Accessed 2026-10-20. Cited because it shows that parameter names such as Código de montagem are translated in the Portuguese interface.
[^locales]: pyRevit project, `pyrevitlib/pyrevit/coreutils/applocales.py` and the bundle files of `extensions/pyRevitTools.extension`. https://github.com/pyrevitlabs/pyRevit. Read 2026-10-20. Cited for the `pt_br` locale code and the `title` and `tooltip` format in `bundle.yaml`.
[^idsschema]: buildingSMART, IDS repository, `Schema/ids.xsd` and the test cases under `Documentation/ImplementersDocumentation/TestCases`. https://github.com/buildingSMART/IDS. Read 2026-10-20. Cited because the reader and its tests follow the element names, the cardinality values and the sample files in this repository.
