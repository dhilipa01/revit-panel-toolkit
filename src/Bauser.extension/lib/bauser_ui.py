# -*- coding: utf-8 -*-
"""One shared WPF results window for all the buttons.

If WPF fails for any reason, falls back to pyRevit's output window so the
button never dies silently.
"""
import os
import traceback

import clr
clr.AddReference("System.Data")
from System.Data import DataTable

from pyrevit import forms, script

import bauser_core as core
import bauser_text as tx

XAML = os.path.join(os.path.dirname(__file__), "results.xaml")


def _delimiter():
    return ";" if tx.lang() == "pt" else ","   # pt-BR Excel: ';' because ',' is the decimal mark


class ResultWindow(forms.WPFWindow):
    def __init__(self, title, subtitle, cards, columns, rows, csv_name, footnote="", budget=None):
        forms.WPFWindow.__init__(self, XAML)
        self._columns, self._rows, self._csv_name = columns, rows, csv_name
        self._budget = budget
        self.Title = "Bauser - " + title

        self._text("title", title)
        self._text("subtitle", subtitle)
        self._text("footnote", footnote)
        for i, (value, label) in enumerate(cards, 1):
            self._text("v%d" % i, value)
            self._text("l%d" % i, label)

        # DataTable binds reliably from both IronPython and CPython (plain objects don't).
        table = DataTable("rows")
        for c in columns:
            table.Columns.Add(c)
        for r in rows:
            row = table.NewRow()
            for i, v in enumerate(r):
                row[i] = core.text(v)
            table.Rows.Add(row)
        self.FindName("grid").ItemsSource = table.DefaultView

        export, close = self.FindName("btn_export"), self.FindName("btn_close")
        export.Content, close.Content = tx.t("btn_export"), tx.t("btn_close")
        export.Click += self.export_click
        close.Click += self.close_click
        if budget:
            from System.Windows import Visibility
            b = self.FindName("btn_budget")
            b.Content = tx.t("btn_budget")
            b.Visibility = Visibility.Visible
            b.Click += self.budget_click

    def _text(self, name, value):
        self.FindName(name).Text = value

    def close_click(self, sender, args):
        self.Close()

    def _save(self, name, columns, rows):
        path = forms.save_file(file_ext="csv", default_name=name)
        if not path:
            return
        try:
            core.write_csv(path, columns, rows, _delimiter())
            forms.alert(tx.t("saved") + "\n" + path, title="Bauser")
        except Exception as ex:
            forms.alert("%s\n%s" % (tx.t("save_failed"), ex), title="Bauser")

    def export_click(self, sender, args):
        self._save(self._csv_name, self._columns, self._rows)

    def budget_click(self, sender, args):
        columns, rows, name = self._budget
        self._save(name, columns, rows)


def show(title, subtitle, cards, columns, rows, csv_name, footnote="", budget=None):
    """cards: [(value, label)] x3. rows: tuples matching columns. budget: (columns, rows, csv_name)."""
    try:
        ResultWindow(title, subtitle, cards, columns, rows, csv_name, footnote, budget).ShowDialog()
    except Exception:
        out = script.get_output()
        out.print_md("### %s\n%s" % (title, subtitle))
        out.print_md("  \n".join("**%s** - %s" % (v, label) for v, label in cards))
        out.print_table([[core.text(c) for c in r] for r in rows], columns=columns)
        out.print_code(traceback.format_exc())  # so a WPF problem is visible, not hidden
