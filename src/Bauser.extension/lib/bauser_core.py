# -*- coding: utf-8 -*-
"""Pure-Python panel logic for the Bauser plugin.

No Revit imports, so it runs (and is tested) anywhere. IronPython 2.7 and
CPython 3 compatible: no f-strings, no type hints.

A "panel" is a plain dict:
    id, mark, type, level, elev, x, y, length_m, height_m, area_m2 (net), gross_m2, openings
plus an optional "element" key the Revit adapter uses to write marks back.
"""
import csv
import sys

try:
    _STR = basestring  # noqa: F821 (IronPython 2.7 / CPython 2)
except NameError:
    _STR = str

FT_TO_M = 0.3048
FT2_TO_M2 = FT_TO_M * FT_TO_M

# Demo assumptions. Edit here; a JSON file is the next step once real prices exist.
DEFAULT_RATE = 490.0  # R$/m2, placeholder (not a Bauser or SINAPI price)
# wall-type-name substring -> (R$/m2, SINAPI composition code or "").
# Example: {"Drywall": (101.0, "96358")}. The code is only a label; nothing is imported from SINAPI.
RATES = {}
WASTE = 0.05          # 5% waste factor
MARK_PREFIX = "P-"

# Static snapshot, refreshed by hand. Limit: it goes stale. Next step: a dated fetch
# from https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/ (no key needed).
FX = {"asof": "2026-10-19", "EUR": 5.6682}  # BRL per 1 EUR, BCB PTAX closing (sell)


def text(v):
    """Safe string for UI cells: keeps unicode text as is (str() would break on IronPython 2)."""
    return v if isinstance(v, _STR) else str(v)


def ft_to_m(v):
    return v * FT_TO_M


def ft2_to_m2(v):
    return v * FT2_TO_M2


def rate_info(type_name, rates=None):
    """First RATES key found in the type name wins (case-insensitive). -> (rate, sinapi_code)"""
    low = (type_name or "").lower()
    for key, val in (RATES if rates is None else rates).items():
        if key.lower() in low:
            return val
    return DEFAULT_RATE, ""


def fmt(v, d=2, lang="en"):
    """1234.5 -> '1,234.50' (en) or '1.234,50' (pt)."""
    s = ("{:,.%df}" % d).format(v)
    if lang == "pt":
        s = s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return s


def money(v, lang="en"):
    return u"R$ " + fmt(v, 2, lang)


def eur(v, lang="en"):
    return u"€ " + fmt(v, 2, lang)


def to_eur(brl):
    return brl / FX["EUR"]


# Pricing basis. net = Revit's area (openings already subtracted); gross = full panel size,
# length x height, openings included. Net is the default.
AREA_KEY = {"net": "area_m2", "gross": "gross_m2"}


def summarize_by_type(panels, basis="net"):
    """-> [(type, qty, area_m2, openings)] sorted by type name; area follows the pricing basis."""
    key = AREA_KEY[basis]
    acc = {}
    for p in panels:
        q, a, o = acc.get(p["type"], (0, 0.0, 0))
        acc[p["type"]] = (q + 1, a + p[key], o + p.get("openings", 0))
    return [(t, q, a, o) for t, (q, a, o) in sorted(acc.items())]


def number_plan(panels, prefix=MARK_PREFIX):
    """-> [(panel, mark)]. Order: level elevation, then X, then Y, then id (stable)."""
    ordered = sorted(panels, key=lambda p: (p["elev"], p["x"], p["y"], p["id"]))
    return [(p, "%s%03d" % (prefix, i)) for i, p in enumerate(ordered, 1)]


def cost_table(panels, waste=WASTE, rates=None, basis="net"):
    """Cost = area x rate x (1 + waste), area per the pricing basis. -> (rows, totals)

    rows: one dict per panel (panel, area, rate, code, cost).
    totals: net / waste / gross / area / per_m2 / eur  (net/gross here mean before/after waste).
    """
    key = AREA_KEY[basis]
    rows = []
    net = 0.0
    area = 0.0
    for p in sorted(panels, key=lambda p: (p["elev"], p["x"], p["y"], p["id"])):
        rate, code = rate_info(p["type"], rates)
        cost = p[key] * rate
        rows.append({"panel": p, "area": p[key], "rate": rate, "code": code, "cost": cost})
        net += cost
        area += p[key]
    extra = net * waste
    gross = net + extra
    return rows, {
        "net": net, "waste": extra, "gross": gross, "area": area,
        "per_m2": (gross / area) if area else 0.0, "eur": to_eur(gross),
    }


def budget_lines(panels, waste=WASTE, rates=None, basis="net"):
    """Budget sheet: one line per wall type. -> (lines, totals)

    line: code, desc, unit, qty (m2), price (R$/m2), total. Waste and EUR are added by the caller.
    """
    lines = []
    net = 0.0
    for typ, _count, area, _openings in summarize_by_type(panels, basis):
        rate, code = rate_info(typ, rates)
        lines.append({"code": code, "desc": typ, "unit": "m2", "qty": area,
                      "price": rate, "total": area * rate})
        net += area * rate
    extra = net * waste
    gross = net + extra
    return lines, {"net": net, "waste": extra, "gross": gross, "eur": to_eur(gross)}


def _s(v):
    if sys.version_info[0] == 2 and isinstance(v, unicode):  # noqa: F821 (py2 only)
        return v.encode("utf-8")
    return v


def write_csv(path, header, rows, delimiter=","):
    """UTF-8 CSV. pt-BR Excel wants ';' (it uses ',' as the decimal mark), so callers pass that."""
    if sys.version_info[0] == 2:
        f = open(path, "wb")
    else:
        f = open(path, "w", newline="", encoding="utf-8-sig")  # BOM: Excel opens UTF-8 cleanly
    try:
        w = csv.writer(f, delimiter=str(delimiter))
        w.writerow([_s(h) for h in header])
        for r in rows:
            w.writerow([_s(c) for c in r])
    finally:
        f.close()
