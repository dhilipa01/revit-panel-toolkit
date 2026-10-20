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

# Illustrative prices in R$/m2, matched on the wall type name. Not real prices.
RATES = {"facade": (520.0, ""), "partition": (310.0, "")}


def wall(i, typ, level, elev, x, length, height, opening_m2=0.0, openings=0):
    """A panel as the Revit adapter would build it. Net area excludes the openings."""
    return {"id": i, "mark": "", "type": typ, "level": level, "elev": elev, "x": x, "y": 0.0,
            "length_m": length, "height_m": height, "area_m2": length * height - opening_m2,
            "gross_m2": length * height, "openings": openings}


SAMPLE = [
    wall(1, "Facade Panel", "Level 1", 0.0, 0.0, 3.0, 2.8, 1.8, 1),
    wall(2, "Facade Panel", "Level 1", 0.0, 3.0, 3.0, 2.8, 0.0, 0),
    wall(3, "Partition Panel", "Level 1", 0.0, 6.0, 2.4, 2.8, 1.9, 1),
    wall(4, "Facade Panel", "Level 2", 2.8, 0.0, 3.0, 2.8, 1.8, 1),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("csv", nargs="?", help="write the budget CSV to this path")
    ap.add_argument("--gross", action="store_true", help="price full panel size instead of net area")
    ap.add_argument("--lang", choices=("en", "pt"), default="en")
    ap.add_argument("--waste", type=float, default=core.WASTE * 100, help="waste factor in percent")
    args = ap.parse_args()
    basis, L, waste = ("gross" if args.gross else "net"), args.lang, args.waste / 100.0

    rows, totals = core.cost_table(SAMPLE, waste, RATES, basis)
    print("Mark   Type             Level    Openings   Area m2   Rate R$/m2   Cost R$")
    for (p, mark), r in zip(core.number_plan(SAMPLE), rows):
        print("%-6s %-16s %-8s %8d %9s %12s %9s" % (
            mark, p["type"], p["level"], p["openings"],
            core.fmt(r["area"], 2, L), core.fmt(r["rate"], 2, L), core.fmt(r["cost"], 2, L)))
    print()
    print("Basis        %s area" % basis)
    print("Total        %s  (with %s%% waste)" % (core.money(totals["gross"], L), core.fmt(args.waste, 0, L)))
    print("Approx.      %s  (EUR/BRL %s, %s)" % (
        core.eur(totals["eur"], L), core.fmt(core.FX["EUR"], 4, L), core.FX["asof"]))

    if args.csv:
        lines, bt = core.budget_lines(SAMPLE, waste, RATES, basis)
        out = [(line["code"], line["desc"], line["unit"], core.fmt(line["qty"], 2, L), core.fmt(line["price"], 2, L),
                core.fmt(line["total"], 2, L)) for line in lines]
        out += [("", "Waste (%s%%)" % core.fmt(args.waste, 0, L), "", "", "", core.fmt(bt["waste"], 2, L)),
                ("", "TOTAL (R$)", "", "", "", core.fmt(bt["gross"], 2, L)),
                ("", "TOTAL (EUR, approx.)", "", "", "", core.fmt(bt["eur"], 2, L))]
        core.write_csv(args.csv, ["Code", "Description", "Unit", "Qty", "Unit price (R$)", "Total (R$)"],
                       out, ";" if L == "pt" else ",")
        print("\nWrote %s" % args.csv)


if __name__ == "__main__":
    main()
