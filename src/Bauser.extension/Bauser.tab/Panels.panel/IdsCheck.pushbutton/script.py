# -*- coding: utf-8 -*-
__title__ = "IDS\nCheck"
__doc__ = "Check the panels against a buildingSMART IDS 1.0 file: required properties, classification and attributes, tested on the Revit parameters."

from pyrevit import forms

import bauser_ids as ids
import bauser_revit as rv
import bauser_text as tx
import bauser_ui as ui

path = forms.pick_file(file_ext="ids", title=tx.t("ids_pick"))
if not path:
    forms.alert(tx.t("cancelled"), title="Bauser", exitscript=True)

try:
    spec = ids.parse_ids(path)
except (ValueError, IOError) as ex:
    forms.alert("%s\n%s" % (tx.t("ids_bad"), ex), title="Bauser", exitscript=True)

panels, scope = rv.get_panels()
if not panels:
    forms.alert(tx.t("no_walls"), title="Bauser", exitscript=True)

rows = ids.check(panels, spec)
if not rows:
    forms.alert(tx.t("ids_none"), title="Bauser", exitscript=True)
sm = ids.summarise(rows)

ui.show(
    tx.t("ids_title"),
    "%s: %s" % (spec["title"] or path, scope),
    [(str(len(spec["specs"])), tx.t("ids_specs")),
     (str(sm["panels"]), tx.t("ids_panels")),
     (str(sm[ids.FAIL]), tx.t("ids_failed"))],
    [tx.t("col_panel"), tx.t("col_spec"), tx.t("col_requirement"), tx.t("col_result"), tx.t("col_detail")],
    [(p, s, r, tx.t("res_" + state), d) for p, s, r, state, d in rows],
    "bauser_ids_check",
    tx.t("ids_note"),
)
