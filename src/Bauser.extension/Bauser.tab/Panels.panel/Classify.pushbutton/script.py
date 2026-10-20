# -*- coding: utf-8 -*-
__title__ = "Classify\nPanels"
__doc__ = "Write the classification code set for each wall type in bauser_config.json (for example an NBR 15965 code) to the type's classification parameter."

from pyrevit import forms

import bauser_core as core
import bauser_revit as rv
import bauser_text as tx
import bauser_ui as ui

panels, scope = rv.get_panels()
if not panels:
    forms.alert(tx.t("no_walls"), title="Bauser", exitscript=True)

plan, missing = core.classification_plan(panels)
if not plan:
    forms.alert(tx.t("classify_none"), title="Bauser", exitscript=True)

if not forms.alert(tx.t("classify_confirm", len(plan)), title=tx.t("classify_dialog"), yes=True, no=True):
    forms.alert(tx.t("cancelled_nothing"), title="Bauser", exitscript=True)

results = rv.set_classifications(panels, plan)
written = sum(1 for r in results if r[4] == "written")

ui.show(
    tx.t("classify_title"),
    scope,
    [(str(written), tx.t("card_written")),
     (str(len(results) - written), tx.t("card_not_written")),
     (str(len(missing)), tx.t("card_no_code"))],
    [tx.t("col_type"), tx.t("col_system"), tx.t("col_code"), tx.t("col_panels"), tx.t("col_parameter"),
     tx.t("col_result")],
    [(typ, system, code, qty, name or "-", tx.t("state_" + state)) for typ, system, code, qty, state, name in results],
    "bauser_classification",
    tx.t("classify_note"),
)
