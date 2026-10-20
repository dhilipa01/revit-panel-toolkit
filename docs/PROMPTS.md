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
5. Run the button in Revit on a small model with hand-counted answers.

## Worked examples

| Feature | Checked against | What the check changed |
|---|---|---|
| Count Panels | pyRevit `FilteredElementCollector` usage, parameter `HOST_AREA_COMPUTED` | Wall Area is already net of openings, which led to the net and full panel size options |
| Number Panels | pyRevit ReNumber (`ALL_MODEL_MARK`, `Parameter.Set`) | Same parameter, plus a confirm dialog and an undo note |
| Openings column | Autodesk `HostObject.FindInserts`, inherited by `Wall` | The call was added once the signature was confirmed |
| Full panel size | pyRevit wall tools use `get_BoundingBox(None)` with `Min.Z` and `Max.Z` | Height comes from the bounding box, not from Unconnected Height |
| Irregular walls | Autodesk `Wall.SketchId` and `Wall.CrossSection` | A warning for walls where length times height overstates the panel |
| Results window | pyRevit `WPFWindow`, `FindName`; `forms/_cpy.py` | WPF is unsupported on CPython, so the extension must use IronPython |
| Accented text | IronPython 2.7 string rules | Every accented literal became `u""` |

## Lessons

- A first draft written from memory looked right and was still unverified. Reading the pyRevit source found the CPython limit before it could fail in front of a user.
- Ask the model to list the API members it used. That list becomes the checklist.
- Prices, waste and the exchange rate are placeholders until a real source supplies them. The window says so.
