"""Run: python3 test_core.py  (checks the Revit-free logic; the Revit adapter can't run on Linux)"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "Bauser.extension", "lib"))
import bauser_core as c
import bauser_text as tx


def panel(i, typ, elev, x, y, area, openings=0):
    # gross = full panel size, 25% larger than net here (openings take the difference)
    return {"id": i, "mark": "", "type": typ, "level": "L", "elev": elev, "x": x, "y": y,
            "length_m": 1.0, "height_m": 1.0, "area_m2": area, "gross_m2": area * 1.25,
            "openings": openings}


P = [panel(3, "LSF 140", 3.0, 0.0, 0.0, 10.0, 1),   # level 2
     panel(1, "LSF 140", 0.0, 5.0, 0.0, 8.0, 2),     # level 1, right
     panel(2, "Drywall", 0.0, 1.0, 0.0, 4.0)]        # level 1, left

assert abs(c.ft2_to_m2(10.7639104) - 1.0) < 1e-6 and abs(c.ft_to_m(1) - 0.3048) < 1e-9

assert c.summarize_by_type(P) == [("Drywall", 1, 4.0, 0), ("LSF 140", 2, 18.0, 3)]
assert c.summarize_by_type(P, "gross") == [("Drywall", 1, 5.0, 0), ("LSF 140", 2, 22.5, 3)]

assert [(p["id"], m) for p, m in c.number_plan(P)] == [(2, "P-001"), (1, "P-002"), (3, "P-003")]

# rates + SINAPI reference code (label only)
R = {"LSF": (500.0, "")}
assert c.rate_info("lsf 140 wall", R) == (500.0, "")
assert c.rate_info("Other", R) == (c.DEFAULT_RATE, "")
assert c.rate_info("Drywall x", {"drywall": (101.0, "96358")}) == (101.0, "96358")

rows, t = c.cost_table(P, waste=0.10, rates={})
assert abs(t["net"] - 22.0 * c.DEFAULT_RATE) < 1e-6
assert abs(t["gross"] - t["net"] * 1.10) < 1e-6 and abs(t["per_m2"] - t["gross"] / 22.0) < 1e-6
assert abs(t["eur"] - t["gross"] / c.FX["EUR"]) < 1e-9
assert c.cost_table([], 0.05)[1]["per_m2"] == 0.0  # empty -> no ZeroDivisionError

# pricing basis: net is the default; gross prices the full panel size
assert c.cost_table(P, 0.10, {})[1]["net"] == t["net"]   # default basis is net
rows_g, tg = c.cost_table(P, waste=0.10, rates={}, basis="gross")
assert abs(tg["net"] - 27.5 * c.DEFAULT_RATE) < 1e-6 and abs(tg["area"] - 27.5) < 1e-9
assert c.cost_table(P, 0.10, {}, "net")[1]["net"] == t["net"]
assert rows_g[0]["area"] == rows_g[0]["panel"]["gross_m2"]

# budget sheet: one line per type, codes carried through, totals consistent with cost_table
lines, bt = c.budget_lines(P, waste=0.10, rates={"drywall": (101.0, "96358")})
assert [(l["desc"], l["code"], l["qty"]) for l in lines] == [("Drywall", "96358", 4.0), ("LSF 140", "", 18.0)]
assert abs(bt["net"] - (4.0 * 101.0 + 18.0 * c.DEFAULT_RATE)) < 1e-6
assert abs(bt["gross"] - bt["net"] * 1.10) < 1e-6

# number formats
assert c.fmt(1234.5, 2, "en") == "1,234.50" and c.fmt(1234.5, 2, "pt") == "1.234,50"
assert c.money(1234.5, "pt") == u"R$ 1.234,50" and c.money(1234.5, "en") == u"R$ 1,234.50"
assert c.eur(1234.5, "pt") == u"€ 1.234,50"
assert c.text(u"é") == u"é" and c.text(5) == "5"

# language: with no pyRevit available, lang() falls back to the Portuguese default
assert tx.lang() == "pt" and tx.t("panels") == u"Painéis"
assert tx.t("scope_sel", 3) == u"Seleção (3 paredes)"
assert all(len(v) == 2 and v[0] and v[1] for v in tx.STRINGS.values())  # every key has EN and PT

with tempfile.TemporaryDirectory() as d:
    f = os.path.join(d, "x.csv")
    c.write_csv(f, ["Mark", "Type"], [("P-001", "LSF é")])
    assert open(f, encoding="utf-8-sig").read().splitlines() == ["Mark,Type", "P-001,LSF é"]
    c.write_csv(f, ["A", "B"], [("1,5", "x")], ";")
    assert open(f, encoding="utf-8-sig").read().splitlines() == ["A;B", "1,5;x"]

print("core OK")
