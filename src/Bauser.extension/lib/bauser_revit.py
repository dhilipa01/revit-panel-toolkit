# -*- coding: utf-8 -*-
"""Thin Revit adapter: walls -> panel dicts, and writing marks back.

Only long-stable API calls are used (built-in parameters, FilteredElementCollector,
Transaction), so it behaves the same on Revit 2019-2026.
"""
from pyrevit import revit, DB

import bauser_text as tx
from bauser_core import ft_to_m, ft2_to_m2

BIP = DB.BuiltInParameter


def _eid(el):
    try:
        return el.Id.Value          # Revit 2024+
    except AttributeError:
        return el.Id.IntegerValue   # older


def _name(el):
    try:
        return DB.Element.Name.GetValue(el)   # IronPython-safe form
    except Exception:
        return el.Name


def _is_irregular(w):
    """Not a plain vertical rectangle: edited profile (Wall.SketchId, Revit 2022+) or a
    slanted / tapered cross section (Wall.CrossSection). Length x bounding-box height
    overstates the full panel size of these walls.
    """
    sketch = getattr(w, "SketchId", None)   # property added in Revit 2022
    edited = sketch is not None and sketch != DB.ElementId.InvalidElementId
    return edited or w.CrossSection != DB.WallCrossSection.Vertical


def _num(el, bip):
    p = el.get_Parameter(bip)
    return p.AsDouble() if (p is not None and p.HasValue) else 0.0


def get_panels(doc=None, uidoc=None):
    """Walls in the current selection, or every wall in the model if nothing is selected.

    -> (panels, scope_text)
    """
    doc = doc or revit.doc
    uidoc = uidoc or revit.uidoc
    picked = [doc.GetElement(i) for i in uidoc.Selection.GetElementIds()]
    walls = [e for e in picked if isinstance(e, DB.Wall)]
    if walls:
        scope = tx.t("scope_sel", len(walls))
    else:
        walls = list(DB.FilteredElementCollector(doc)
                     .OfCategory(DB.BuiltInCategory.OST_Walls)
                     .WhereElementIsNotElementType().ToElements())
        scope = tx.t("scope_model")

    panels = []
    for w in walls:
        t = doc.GetElement(w.GetTypeId())
        lvl = doc.GetElement(w.LevelId)
        loc = w.Location
        pt = loc.Curve.GetEndPoint(0) if isinstance(loc, DB.LocationCurve) else None
        length = _num(w, BIP.CURVE_ELEM_LENGTH)
        area = _num(w, BIP.HOST_AREA_COMPUTED)   # net: Revit already subtracts openings
        # full panel height = model bounding box Z extent (same call pyRevit's own wall tools use)
        bb = w.get_BoundingBox(None)
        if bb is not None:
            height = bb.Max.Z - bb.Min.Z
        else:
            height = _num(w, BIP.WALL_USER_HEIGHT_PARAM) or ((area / length) if length else 0.0)
        # doors, windows and rectangular openings hosted in this wall (Autodesk: HostObject.FindInserts)
        openings = len(list(w.FindInserts(True, False, False, False)))
        mark = w.get_Parameter(BIP.ALL_MODEL_MARK)
        panels.append({
            "element": w,
            "id": _eid(w),
            "mark": (mark.AsString() or "") if mark is not None else "",
            "type": _name(t) if t is not None else "?",
            "level": _name(lvl) if lvl is not None else "-",
            "elev": lvl.Elevation if lvl is not None else 0.0,
            "x": pt.X if pt is not None else 0.0,
            "y": pt.Y if pt is not None else 0.0,
            "length_m": ft_to_m(length),
            "height_m": ft_to_m(height),
            "area_m2": ft2_to_m2(area),
            "gross_m2": ft2_to_m2(length * height),
            "openings": openings,
            "irregular": _is_irregular(w),
        })
    return panels, scope


def set_marks(plan, doc=None):
    """Write the Mark parameter for [(panel, mark)] in one transaction. -> (done, skipped)"""
    doc = doc or revit.doc
    done = skipped = 0
    with revit.Transaction("Bauser: Number panels", doc=doc):
        for panel, mark in plan:
            p = panel["element"].get_Parameter(BIP.ALL_MODEL_MARK)
            if p is None or p.IsReadOnly:
                skipped += 1
                continue
            p.Set(mark)
            panel["mark"] = mark
            done += 1
    return done, skipped
