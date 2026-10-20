# -*- coding: utf-8 -*-
"""Read a buildingSMART IDS 1.0 file and check Revit panels against it.

Pure Python, no Revit imports. This is a Revit-side check, not an IFC validation. It reads the
requirements in an IDS file and tests them against the parameters of the Revit walls, so a model
can be checked before export. Use an IFC checker on the exported file for the formal result.

How IDS terms map to a panel (a dict, see bauser_core):
    entity IFCWALL, IFCWALLSTANDARDCASE   every panel is a wall, other entities are not applicable
    property <baseName>                    a Revit parameter of the wall or its type, matched by name
                                           with case, spaces and underscores ignored (FireRating
                                           matches Fire Rating). The property set is not checked.
    classification <value>, <system>       the classification parameter of the wall type, and the
                                           system named in the configuration
    attribute Name, Tag, Description       type name, Mark, and the Description parameter

Values: a plain value, an enumeration or a pattern. Other restrictions and the facets partOf and
material are reported as Not checked. IronPython 2.7 and CPython 3 compatible.
"""
import re
import xml.etree.ElementTree as ET

NS = "{http://standards.buildingsmart.org/IDS}"
XS = "{http://www.w3.org/2001/XMLSchema}"
WALL_ENTITIES = ("IFCWALL", "IFCWALLSTANDARDCASE")
PASS, FAIL, SKIP = "Pass", "Fail", "Not checked"


def _norm(s):
    return re.sub(r"[\s_]+", "", s or "").lower()


def _matcher(el):
    """An idsValue element -> {"kind": any|equals|in|regex|unsupported, ...}."""
    if el is None:
        return {"kind": "any"}
    simple = el.find(NS + "simpleValue")
    if simple is not None:
        return {"kind": "equals", "value": simple.text or ""}
    restriction = el.find(XS + "restriction")
    if restriction is None:
        return {"kind": "unsupported"}
    values = [e.get("value") for e in restriction.findall(XS + "enumeration")]
    patterns = [e.get("value") for e in restriction.findall(XS + "pattern")]
    others = [c for c in restriction if c.tag not in (XS + "enumeration", XS + "pattern")]
    if others or (values and patterns) or not (values or patterns):
        return {"kind": "unsupported"}
    return {"kind": "in", "values": values} if values else {"kind": "regex", "value": patterns[0]}


def _matches(m, text, loose=False):
    """True, False, or None when the restriction is not supported."""
    kind = m["kind"]
    if kind == "any":
        return True
    if kind == "unsupported":
        return None
    f = _norm if loose else (lambda s: s)
    if kind == "equals":
        return f(text) == f(m["value"])
    if kind == "in":
        return f(text) in [f(v) for v in m["values"]]
    return re.match("^(?:%s)$" % m["value"], text or "") is not None


def _describe(m):
    kind = m["kind"]
    if kind == "equals":
        return m["value"]
    if kind == "in":
        return " | ".join(m["values"])
    if kind == "regex":
        return "/%s/" % m["value"]
    return "any" if kind == "any" else "unsupported"


def _child(el, tag):
    return _matcher(el.find(NS + tag))


def _facet(el):
    kind = el.tag.replace(NS, "")
    facet = {"kind": kind, "cardinality": el.get("cardinality", "required")}
    if kind == "property":
        facet.update(name=_child(el, "baseName"), value=_child(el, "value"))
        facet["set"] = _describe(_child(el, "propertySet"))
    elif kind == "classification":
        facet.update(system=_child(el, "system"), value=_child(el, "value"))
    elif kind == "attribute":
        facet.update(name=_child(el, "name"), value=_child(el, "value"))
    elif kind == "entity":
        facet.update(name=_child(el, "name"))
    return facet


def parse_ids(source):
    """Parse an IDS 1.0 file (a path or a file object). -> {"title": str, "specs": [...]}

    Raises ValueError when the file is not IDS 1.0 XML.
    """
    try:
        root = ET.parse(source).getroot()
    except ET.ParseError as ex:
        raise ValueError("not valid XML: %s" % ex)
    if root.tag != NS + "ids":
        raise ValueError("not an IDS 1.0 file (root element %s)" % root.tag)
    title = root.findtext(NS + "info/" + NS + "title") or ""
    specs = []
    for sp in root.findall(NS + "specifications/" + NS + "specification"):
        app = sp.find(NS + "applicability")
        req = sp.find(NS + "requirements")
        specs.append({
            "name": sp.get("name", ""),
            "applicability": [_facet(e) for e in (app if app is not None else [])],
            "requirements": [_facet(e) for e in (req if req is not None else [])],
        })
    return {"title": title, "specs": specs}


def _facet_label(f):
    k = f["kind"]
    if k == "property":
        return "property %s.%s%s" % (f["set"], _describe(f["name"]),
                                     "" if f["value"]["kind"] == "any" else " = " + _describe(f["value"]))
    if k == "classification":
        system = "" if f["system"]["kind"] == "any" else _describe(f["system"]) + " "
        return "classification %s%s" % (system, _describe(f["value"]))
    if k == "attribute":
        return "attribute %s%s" % (_describe(f["name"]),
                                   "" if f["value"]["kind"] == "any" else " = " + _describe(f["value"]))
    return k


def _attribute_value(panel, name):
    if name == "Name":
        return panel.get("type", "")
    if name == "Tag":
        return panel.get("mark", "")
    if name == "Description":
        return (panel.get("properties") or {}).get("Description", "")
    return None


def _candidates(panel, f, aliases=None):
    """The (name, value) pairs a facet looks at, or None when the facet cannot be checked.

    aliases maps an IDS property name to other Revit parameter names (all normalised, see check).
    """
    k = f["kind"]
    if k == "property":
        if f["name"]["kind"] == "unsupported":
            return None
        extra = (aliases or {}).get(_norm(f["name"]["value"]), []) if f["name"]["kind"] == "equals" else []
        return [(n, v) for n, v in (panel.get("properties") or {}).items()
                if v not in (None, "") and (_matches(f["name"], n, loose=True) or _norm(n) in extra)]
    if k == "classification":
        code = panel.get("classification") or ""
        if not code:
            return []
        sm = _matches(f["system"], panel.get("classification_system") or "")
        if sm is None:
            return None
        return [("classification", code)] if sm else []
    if k == "attribute":
        if f["name"]["kind"] != "equals":
            return None
        v = _attribute_value(panel, f["name"]["value"])
        if v is None:
            return None
        return [(f["name"]["value"], v)] if v != "" else []
    return None


def _shown(cands):
    return ", ".join("'%s'" % v for _n, v in cands)


def _evaluate(panel, f, aliases=None):
    """-> (state, detail). state is PASS, FAIL or SKIP."""
    cands = _candidates(panel, f, aliases)
    if cands is None:
        return SKIP, "unsupported facet or restriction"
    results = [_matches(f["value"], v) if "value" in f else True for _n, v in cands]
    if any(r is None for r in results):
        return SKIP, "unsupported value restriction"
    found = bool(cands)
    ok = any(results)
    card = f["cardinality"]
    if card == "prohibited":
        return (FAIL, "present but prohibited") if (found and ok) else (PASS, "")
    if card == "optional":
        return (PASS, "") if (not found or ok) else (FAIL, "value %s does not match" % _shown(cands))
    if not found:
        return FAIL, "missing"
    return (PASS, "") if ok else (FAIL, "value %s does not match" % _shown(cands))


def _applies(panel, spec, aliases=None):
    """True, False, or None when the applicability uses something that is not checked."""
    for f in spec["applicability"]:
        if f["kind"] == "entity":
            hit = [_matches(f["name"], e) for e in WALL_ENTITIES]
            if None in hit:
                return None
            if not any(hit):
                return False
        elif f["kind"] in ("property", "classification", "attribute"):
            state, _detail = _evaluate(panel, dict(f, cardinality="required"), aliases)
            if state == SKIP:
                return None
            if state == FAIL:
                return False
        else:
            return None
    return True


def check(panels, ids, aliases=None):
    """Check panels against the parsed IDS. -> list of rows, one per panel and requirement.

    A row is (panel label, specification, requirement, result, detail), result Pass, Fail or Not checked.
    A specification whose applicability is not supported gives one Not checked row.

    aliases: {IDS property name: [Revit parameter names]}, for a Revit whose parameter names are
    translated, so that FireRating can be satisfied by a parameter with a Portuguese name.
    Names are compared with case, spaces and underscores ignored.
    """
    aliases = dict((_norm(k), [_norm(x) for x in v]) for k, v in (aliases or {}).items())
    rows = []
    for spec in ids["specs"]:
        skipped = False
        for p in panels:
            label = p.get("mark") or "id %s" % p["id"]
            applies = _applies(p, spec, aliases)
            if applies is None:
                if not skipped:
                    rows.append(("-", spec["name"], "applicability", SKIP, "unsupported facet"))
                    skipped = True
                continue
            if not applies:
                continue
            for f in spec["requirements"]:
                state, detail = _evaluate(p, f, aliases)
                rows.append((label, spec["name"], _facet_label(f), state, detail))
    return rows


def summarise(rows):
    """-> {"Pass": n, "Fail": n, "Not checked": n, "panels": number of panels with a row}"""
    out = {PASS: 0, FAIL: 0, SKIP: 0}
    for r in rows:
        out[r[3]] += 1
    out["panels"] = len(set(r[0] for r in rows if r[0] != "-"))
    return out
