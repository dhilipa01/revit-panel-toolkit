"""Price a small set of sample wall panels without Revit.

    python examples/panel_budget.py                 net area, English
    python examples/panel_budget.py --gross         full panel size
    python examples/panel_budget.py --lang pt       Portuguese number format
    python examples/panel_budget.py budget.csv      also write the budget CSV
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "Bauser.extension", "lib"))
import bauser_core as core  # noqa: E402
import bauser_text as tx  # noqa: E402

# Illustrative prices in R$/m2, matched on the wall type name. Not real prices.
RATES = {"facade": (520.0, ""), "partition": (310.0, ""), "fachada": (520.0, ""), u"divisória": (310.0, "")}
NAMES = {"en": ("Facade Panel", "Partition Panel", "Level 1", "Level 2"),
         "pt": ("Painel de fachada", u"Painel de divisória", u"Nível 1", u"Nível 2")}


def wall(i, typ, level, elev, x, length, height, opening_m2=0.0, openings=0):
    """A panel as the Revit adapter would build it. Net area excludes the openings."""
    return {"id": i, "mark": "", "type": typ, "level": level, "elev": elev, "x": x, "y": 0.0,
            "length_m": length, "height_m": height, "area_m2": length * height - opening_m2,
            "gross_m2": length * height, "openings": openings}


def sample(lang):
    facade, partition, level1, level2 = NAMES[lang]
    return [
        wall(1, facade, level1, 0.0, 0.0, 3.0, 2.8, 1.8, 1),
        wall(2, facade, level1, 0.0, 3.0, 3.0, 2.8, 0.0, 0),
        wall(3, partition, level1, 0.0, 6.0, 2.4, 2.8, 1.9, 1),
        wall(4, facade, level2, 2.8, 0.0, 3.0, 2.8, 1.8, 1),
    ]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("csv", nargs="?", help="write the budget CSV to this path")
    ap.add_argument("--gross", action="store_true", help="price full panel size instead of net area")
    ap.add_argument("--lang", choices=("en", "pt"), default="en")
    ap.add_argument("--waste", type=float, default=core.WASTE * 100, help="waste factor in percent")
    args = ap.parse_args()
    basis, L, waste = ("gross" if args.gross else "net"), args.lang, args.waste / 100.0

    def word(key):
        en, pt = tx.STRINGS[key]
        return pt if L == "pt" else en

    basis_name = {"en": {"net": "net area", "gross": "full panel size"},
                  "pt": {"net": u"área líquida", "gross": u"tamanho total do painel"}}[L][basis]
    labels = {"en": ("Basis", "Total", "Approx.", "with %s%% waste", "Wrote %s"),
              "pt": ("Base", "Total", "Aprox.", "com %s%% de perdas", "Gravado em %s")}[L]

    panels = sample(L)
    rows, totals = core.cost_table(panels, waste, RATES, basis)
    layout = "%-6s %-20s %-8s %9s %10s %12s %10s"
    print(layout % (word("col_mark"), word("col_type"), word("col_level"), word("col_openings"),
                    word("col_area"), word("col_rate"), word("col_cost")))
    for (p, mark), r in zip(core.number_plan(panels), rows):
        print(layout % (mark, p["type"], p["level"], p["openings"],
                        core.fmt(r["area"], 2, L), core.fmt(r["rate"], 2, L), core.fmt(r["cost"], 2, L)))
    print()
    print("%-12s %s" % (labels[0], basis_name))
    print("%-12s %s  (%s)" % (labels[1], core.money(totals["gross"], L), labels[3] % core.fmt(args.waste, 0, L)))
    print("%-12s %s  (EUR/BRL %s, %s)" % (
        labels[2], core.eur(totals["eur"], L), core.fmt(core.FX["EUR"], 4, L), core.FX["asof"]))

    if args.csv:
        lines, bt = core.budget_lines(panels, waste, RATES, basis)
        out = [(line["code"], line["desc"], line["unit"], core.fmt(line["qty"], 2, L), core.fmt(line["price"], 2, L),
                core.fmt(line["total"], 2, L)) for line in lines]
        out += [("", word("bud_waste") % core.fmt(args.waste, 0, L), "", "", "", core.fmt(bt["waste"], 2, L)),
                ("", word("bud_total_brl"), "", "", "", core.fmt(bt["gross"], 2, L)),
                ("", word("bud_total_eur"), "", "", "", core.fmt(bt["eur"], 2, L))]
        core.write_csv(args.csv, [word("bud_code"), word("bud_desc"), word("bud_unit"), word("bud_qty"),
                                  word("bud_price"), word("bud_total")], out, ";" if L == "pt" else ",")
        print("\n" + labels[4] % args.csv)


if __name__ == "__main__":
    main()
