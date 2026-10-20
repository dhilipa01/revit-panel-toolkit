# Verify in Revit

The logic is tested outside Revit. These steps cover what only a live Revit session can show. Use a small model with two levels, about eight walls and two wall types, drawn from left to right.

## Buttons

1. Click Count Panels. The window opens and the counts match the model. If a plain pyRevit output window opens instead, the WPF window failed and the traceback is printed there.
2. Try Number Panels on a selection of two walls first. Ctrl+Z reverts it.
3. Run Panel Cost. Both CSV buttons save a file that Excel opens with the accents intact.
4. Click PT / EN. The labels change on the next click.

## Classification

1. Open the type properties of a wall type and note whether a Classification Number parameter (OmniClass Number before Revit 2026) is listed. An Autodesk Community answer says it is not listed for system families such as walls.
2. Set a classification code for that wall type in `bauser_config.json` and reload pyRevit.
3. Click Classify Panels. The result row names the parameter that was written, Classification Number or Assembly Code, and says Written.
4. Open the type properties again and read that parameter. It should hold the code.
5. If the row says Read-only or No parameter, note the Revit version and the parameter names that are listed. Whether either parameter accepts a code that is not in Revit's own classification file is not yet confirmed.
6. Ctrl+Z reverts the change for every wall of that type.

## IDS check

1. Click IDS Check and pick `examples/panel_requirements.ids`.
2. A wall with no Mark, no classification code or no Fire Rating parameter shows Fail for that requirement.
3. Give one wall type a Fire Rating value and a classification code, number the panels, and click again. That panel should pass all three requirements.
4. Look at a property name that differs only in spacing from the Revit one, such as `FireRating` against Fire Rating. It should match.
5. In a Revit with a translated interface, such as Portuguese, list the parameter name Revit shows for the fire rating, add it to `ids_aliases` in `bauser_config.json`, reload pyRevit, and click IDS Check again. The requirement should now pass.
5. The window says the check ran on Revit parameters, not on an IFC file. A model exported to IFC should also be checked with an IFC tool.

## Net area and full panel size

1. Take one plain wall with free ends and no openings. Its Area parameter should equal its Length times its height. If it does not, Revit's Area and this extension's length times height measure different things.
2. Add a door. Net area drops by the door cut, full panel size stays the same, and Openings shows 1.
3. Join two walls at a corner and compare both figures. A small difference would mean that Revit's Area uses trimmed faces while this extension uses the location line length. Sources disagree and Autodesk does not say.
4. Edit a wall profile, for example by notching a corner. The warning for the full panel size basis must appear.
5. Attach a wall top to a sloped roof. No warning appears, which is a known gap, and full panel size comes out too high.

## Other

- Walls that already share a Mark value elsewhere in the model can trigger Revit's duplicate Mark warning. Use a clean model for the check.
- Revit 2024 and later read ElementId values through a different property from earlier versions. The code handles both, and neither has been run on a real installation.
- Autodesk renamed the OmniClass and Uniformat parameters in the Revit 2026 API.[^rename] The code tries both names. Note which one your Revit version has.
- With the Revit interface in Brazilian Portuguese, the ribbon shows the Portuguese button titles. Check that all six titles and tooltips appear and that none is cut off.

[^rename]: revitapidocs.com, "API Changes 2026". https://www.revitapidocs.com/2026/news. Accessed 2026-10-20. Cited for the Revit 2026 API change that renamed `OMNICLASS_CODE` to `CLASSIFICATION_CODE` and `UNIFORMAT_CODE` to `ASSEMBLY_CODE`. The site is a third-party mirror of Autodesk's change list.
