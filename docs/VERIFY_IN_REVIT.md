# Verify in Revit

The logic is tested outside Revit. These steps cover what only a live Revit session can show. Use a small model with two levels, about eight walls and two wall types, drawn from left to right.

## Buttons

1. Click Count Panels. The window opens and the counts match the model. If a plain pyRevit output window opens instead, the WPF window failed and the traceback is printed there.
2. Try Number Panels on a selection of two walls first. Ctrl+Z reverts it.
3. Run Panel Cost. Both CSV buttons save a file that Excel opens with the accents intact.
4. Click PT / EN. The labels change on the next click.

## Net area and full panel size

1. Take one plain wall with free ends and no openings. Its Area parameter should equal its Length times its height. If it does not, Revit's Area and this extension's length times height measure different things.
2. Add a door. Net area drops by the door cut, full panel size stays the same, and Openings shows 1.
3. Join two walls at a corner and compare both figures. A small difference would mean that Revit's Area uses trimmed faces while this extension uses the location line length. Sources disagree and Autodesk does not say.
4. Edit a wall profile, for example by notching a corner. The warning for the full panel size basis must appear.
5. Attach a wall top to a sloped roof. No warning appears, which is a known gap, and full panel size comes out too high.

## Other

- Walls that already share a Mark value elsewhere in the model can trigger Revit's duplicate Mark warning. Use a clean model for the check.
- Revit 2024 and later read ElementId values through a different property from earlier versions. The code handles both, and neither has been run on a real installation.
