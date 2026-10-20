# Verify in Revit

The logic is tested outside Revit. These steps check the parts that only a live Revit session can. Use a small model: two levels, about eight walls, two wall types, drawn left to right.

## Buttons

1. **Count Panels.** The window opens and the counts match the model. If a plain pyRevit output window opens instead, the WPF window failed and the traceback is printed there.
2. **Number Panels.** Try it on a selection of two walls first. Ctrl+Z reverts it.
3. **Panel Cost.** Both CSV buttons save a file that Excel opens with correct accents.
4. **PT / EN.** The labels switch on the next click.

## Net area and full panel size

1. One plain wall, free ends, no openings. The Area parameter should equal Length times height. If not, Revit's Area and this extension's length times height measure different things.
2. Add a door. Net area drops by the door cut. Full panel size does not change. Openings shows 1.
3. Join two walls at a corner and compare both figures. A small difference means Revit's Area uses trimmed faces while this extension uses the location line length. Sources disagree and Autodesk does not say.
4. Edit a wall profile, for example notch a corner. The warning for the full panel size basis must appear.
5. Attach a wall top to a sloped roof. No warning appears, which is a known gap. Full panel size will be too high.

## Other

- Walls that already share a Mark value elsewhere in the model can trigger Revit's duplicate-Mark warning. Use a clean model for the check.
- Revit 2024 and later, and earlier versions, read ElementId values through different properties. Both are handled in code and neither has been run on a real install.
