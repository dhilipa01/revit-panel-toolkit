# -*- coding: utf-8 -*-
__title__ = "Count\nPanels"
__doc__ = "Count wall panels by type, with total area. Uses the selection, or the whole model if nothing is selected."

from pyrevit import forms

import bauser_core as core
import bauser_revit as rv
import bauser_text as tx
import bauser_ui as ui

L = tx.lang()
panels, scope = rv.get_panels()
if not panels:
    forms.alert(tx.t("no_walls"), title="Bauser", exitscript=True)

rows = core.summarize_by_type(panels)
total_area = sum(p["area_m2"] for p in panels)

ui.show(
    tx.t("count_title"),
    scope,
    [(str(len(panels)), tx.t("panels")),
     (str(len(rows)), tx.t("types")),
     (core.fmt(total_area, 1, L) + u" m²", tx.t("total_area"))],
    [tx.t("col_type"), tx.t("col_qty"), tx.t("col_openings"), tx.t("col_area")],
    [(t, q, o, core.fmt(a, 2, L)) for t, q, a, o in rows],
    "bauser_panel_count",
)
