# -*- coding: utf-8 -*-
__title__ = "PT / EN\nIdioma"
__doc__ = "Switch the Bauser tab between Portuguese (default) and English."

from pyrevit import forms

import bauser_text as tx

tx.set_lang("en" if tx.lang() == "pt" else "pt")
forms.alert(tx.t("lang_set"), title="Bauser")
