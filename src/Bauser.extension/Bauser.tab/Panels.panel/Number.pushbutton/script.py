# -*- coding: utf-8 -*-
__title__ = "Number\nPanels"
__doc__ = "Write sequential factory marks (P-001, P-002...) to the Mark parameter, ordered by level then left-to-right."

from pyrevit import forms

import bauser_core as core
import bauser_revit as rv
import bauser_text as tx
import bauser_ui as ui

L = tx.lang()
panels, scope = rv.get_panels()
if not panels:
    forms.alert(tx.t("no_walls"), title="Bauser", exitscript=True)

plan = core.number_plan(panels)
first, last = plan[0][1], plan[-1][1]

if not forms.alert(
    tx.t("number_confirm", len(plan), first, last),
    title=tx.t("number_dialog"), yes=True, no=True,
):
    forms.alert(tx.t("cancelled_nothing"), title="Bauser", exitscript=True)

done, skipped = rv.set_marks(plan)

ui.show(
    tx.t("number_title"),
    scope,
    [(str(done), tx.t("marks_written")),
     (str(skipped), tx.t("skipped")),
     ("%s - %s" % (first, last), tx.t("range"))],
    [tx.t("col_mark"), tx.t("col_type"), tx.t("col_level"), tx.t("col_openings"),
     tx.t("col_length"), tx.t("col_area")],
    [(p["mark"], p["type"], p["level"], p["openings"], core.fmt(p["length_m"], 2, L),
      core.fmt(p["area_m2"], 2, L)) for p, _ in plan],
    "bauser_panel_numbers",
    tx.t("number_note"),
)
