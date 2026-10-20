# -*- coding: utf-8 -*-
__title__ = "Panel\nCost"
__doc__ = "Explainable cost: area x unit rate x (1 + waste), in BRL with an approximate EUR figure. Rates are editable in lib/bauser_core.py."

from pyrevit import forms

import bauser_core as core
import bauser_revit as rv
import bauser_text as tx
import bauser_ui as ui

L = tx.lang()
panels, scope = rv.get_panels()
if not panels:
    forms.alert(tx.t("no_walls"), title="Bauser", exitscript=True)

basis_labels = {"net": tx.t("basis_net"), "gross": tx.t("basis_gross")}
choice = forms.CommandSwitchWindow.show(
    [basis_labels["net"], basis_labels["gross"]], message=tx.t("basis_prompt"))   # net is listed first
if choice is None:
    forms.alert(tx.t("cancelled"), title="Bauser", exitscript=True)
basis = "gross" if choice == basis_labels["gross"] else "net"
irregular = sum(1 for p in panels if p["irregular"])
if basis == "gross" and irregular:
    forms.alert(tx.t("irregular_note", irregular), title="Bauser")

answer = forms.ask_for_string(
    default=str(int(core.WASTE * 100)), prompt=tx.t("waste_prompt"), title=tx.t("waste_title"))
if answer is None:
    forms.alert(tx.t("cancelled"), title="Bauser", exitscript=True)
try:
    waste = float(answer.replace(",", ".")) / 100.0
except ValueError:
    forms.alert(tx.t("not_a_number", answer), title="Bauser", exitscript=True)

rows, totals = core.cost_table(panels, waste, basis=basis)
waste_txt = core.fmt(waste * 100, 0, L)
fx = (core.fmt(core.FX["EUR"], 4, L), core.FX["asof"])

# budget sheet: one line per wall type, then waste and totals (BRL, plus approximate EUR)
lines, bt = core.budget_lines(panels, waste, basis=basis)
budget_rows = [(l["code"], l["desc"], l["unit"], core.fmt(l["qty"], 2, L),
                core.fmt(l["price"], 2, L), core.fmt(l["total"], 2, L)) for l in lines]
budget_rows += [
    ("", tx.t("bud_waste", waste_txt), "", "", "", core.fmt(bt["waste"], 2, L)),
    ("", tx.t("bud_total_brl"), "", "", "", core.fmt(bt["gross"], 2, L)),
    ("", tx.t("bud_total_eur"), "", "", "", core.fmt(bt["eur"], 2, L)),
    ("", tx.t("bud_fx", *fx), "", "", "", ""),
    ("", tx.t("bud_basis", basis_labels[basis]), "", "", "", ""),
]

ui.show(
    tx.t("cost_title"),
    scope,
    [(core.money(totals["gross"], L), tx.t("card_total", waste_txt)),
     (core.eur(totals["eur"], L), tx.t("card_eur", *fx)),
     (core.money(totals["per_m2"], L) + u"/m²", tx.t("card_per_m2"))],
    [tx.t("col_mark"), tx.t("col_type"), tx.t("col_level"), tx.t("col_openings"), tx.t("col_area"),
     tx.t("col_rate"), tx.t("col_ref"), tx.t("col_cost")],
    [(r["panel"]["mark"] or "-", r["panel"]["type"], r["panel"]["level"], r["panel"]["openings"],
      core.fmt(r["area"], 2, L), core.fmt(r["rate"], 2, L),
      r["code"] or "-", core.fmt(r["cost"], 2, L)) for r in rows],
    "bauser_panel_cost",
    tx.t("cost_note") + u" " + tx.t("bud_basis", basis_labels[basis]),
    budget=([tx.t("bud_code"), tx.t("bud_desc"), tx.t("bud_unit"), tx.t("bud_qty"),
             tx.t("bud_price"), tx.t("bud_total")], budget_rows, "bauser_budget"),
)
