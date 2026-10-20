# -*- coding: utf-8 -*-
"""Thin Revit adapter: walls -> panel dicts, and writing marks and classification codes back.

It uses built-in parameters, FilteredElementCollector and transactions. Where Autodesk renamed a
member between versions (ElementId.Value, the classification parameter) both names are tried.
It has not been run on a real Revit installation; see docs/VERIFY_IN_REVIT.md.
"""
import bauser_core as core
import bauser_text as tx
from bauser_core import ft2_to_m2, ft_to_m
from pyrevit import DB, revit

BIP = DB.BuiltInParameter


# Candidate type parameters for a classification code, best first. Autodesk renamed OMNICLASS_CODE to
# CLASSIFICATION_CODE and UNIFORMAT_CODE to ASSEMBLY_CODE in the Revit 2026 API, so both names are tried.
# Walls are a system family, and Autodesk Community reports that the classification parameter does not
# exist for system families, so the Assembly Code parameter is the fallback.
_CLASSIFICATION_NAMES = ("CLASSIFICATION_CODE", "OMNICLASS_CODE", "ASSEMBLY_CODE", "UNIFORMAT_CODE")


def _classification_params(wall_type):
    """The classification parameters that exist on a wall type, best first."""
    found = []
    if wall_type is None:
        return found
    for name in _CLASSIFICATION_NAMES:
        bip = getattr(BIP, name, None)
        if bip is not None:
            p = wall_type.get_Parameter(bip)
            if p is not None:
                found.append(p)
    return found


def _read_properties(*elements):
    """Every readable parameter of the given elements as {name: text}. Later elements do not
    overwrite earlier ones, so pass the instance first and its type second."""
    props = {}
    for el in elements:
        if el is None:
            continue
        for p in el.Parameters:
            name = p.Definition.Name
            if name in props:
                continue
            value = p.AsValueString() or p.AsString()
            if value:
                props[name] = value
    return props


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
        class_value = next((p.AsString() for p in _classification_params(t) if p.AsString()), "")
        type_name = _name(t) if t is not None else "?"
        panels.append({
            "element": w,
            "type_element": t,
            "properties": _read_properties(w, t),
            "classification": class_value,
            "classification_system": core.classification_info(type_name)[0],
            "id": _eid(w),
            "mark": (mark.AsString() or "") if mark is not None else "",
            "type": type_name,
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


def set_classifications(panels, plan, doc=None):
    """Write the planned classification code to each wall type, in one transaction.

    plan: [(type name, system, code, panel count)] from core.classification_plan. The code goes to
    the first writable parameter from _classification_params.
    -> [(type name, system, code, panel count, "written" | "read-only" | "no parameter", parameter name)]
    """
    doc = doc or revit.doc
    types = {}
    for p in panels:
        types.setdefault(p["type"], p["type_element"])
    results = []
    with revit.Transaction("Bauser: Classify panels", doc=doc):
        for typ, system, code, qty in plan:
            candidates = _classification_params(types.get(typ))
            writable = [p for p in candidates if not p.IsReadOnly]
            if writable:
                writable[0].Set(code)
                state, name = "written", writable[0].Definition.Name
            elif candidates:
                state, name = "read-only", candidates[0].Definition.Name
            else:
                state, name = "no parameter", ""
            results.append((typ, system, code, qty, state, name))
    return results


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
