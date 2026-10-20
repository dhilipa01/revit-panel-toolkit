"""Run: python tests/test_adapter.py

Runs the real bauser_revit and bauser_ui modules and the button scripts against a
small fake of pyRevit and the Revit API, so typos and wrong call shapes show up on
Linux. It cannot show that the Revit API behaves the same way. See
docs/VERIFY_IN_REVIT.md for the checks that need Revit.
"""
import contextlib
import os
import re
import runpy
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, "src", "Bauser.extension")
sys.path.insert(0, os.path.join(EXT, "lib"))
import bauser_core as core   # pure module: safe to import before the fake pyRevit is installed


# ---- fake Revit API ---------------------------------------------------------
class Eid:
    def __init__(self, v):
        self.Value = v

    def __eq__(self, other):
        return isinstance(other, Eid) and self.Value == other.Value

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.Value)


class Elem:
    reg = {}

    def __init__(self, i, name):
        self.Id, self._name = Eid(i), name
        Elem.reg[i] = self


class Level(Elem):
    def __init__(self, i, name, elev):
        Elem.__init__(self, i, name)
        self.Elevation = elev


class TypeElem(Elem):
    """A wall type with a classification parameter and a Description parameter."""

    def __init__(self, i, name):
        Elem.__init__(self, i, name)
        self.p = {"CLASSIFICATION_CODE": Param(None, "")}
        self.Parameters = [DefParam("Description", "Panel type " + name)]

    def get_Parameter(self, bip):
        return self.p.get(bip)


class Param:
    HasValue = True

    def __init__(self, num=None, text=""):
        self.num, self.text, self.IsReadOnly = num, text, False

    def AsDouble(self):
        return self.num

    def AsString(self):
        return self.text

    def Set(self, v):
        self.text = v


class DefParam(Param):
    """A parameter as listed in Element.Parameters: it has a Definition and a value string."""

    def __init__(self, name, text):
        Param.__init__(self, None, text)
        self.Definition = types.SimpleNamespace(Name=name)

    def AsValueString(self):
        return self.text


class Pt:
    def __init__(self, x, y):
        self.X, self.Y = x, y


class Curve:
    def __init__(self, x, y):
        self.p = Pt(x, y)

    def GetEndPoint(self, i):
        return self.p


class LocationCurve:
    def __init__(self, x, y):
        self.Curve = Curve(x, y)


class Wall(Elem):
    def __init__(self, i, typ, lvl, x, length, area, height, openings=0, edited=False, slanted=False,
                 fire=False):
        Elem.__init__(self, i, "wall")
        self.typ, self.LevelId, self.Location = typ, Eid(lvl), LocationCurve(x, 0.0)
        self.n_open, self.bbox_h = openings, height
        self.Parameters = [DefParam("Fire Rating", "EI60")] if fire else []
        self.SketchId = Eid(55) if edited else Eid(-1)       # -1 = InvalidElementId (no profile sketch)
        self.CrossSection = "S" if slanted else "V"
        self.p = {"CURVE_ELEM_LENGTH": Param(length), "HOST_AREA_COMPUTED": Param(area),
                  "WALL_USER_HEIGHT_PARAM": Param(height), "ALL_MODEL_MARK": Param(None, "")}

    def GetTypeId(self):
        return Eid(self.typ)

    def get_Parameter(self, bip):
        return self.p[bip]

    def FindInserts(self, rect, shadows, embedded_walls, shared):
        assert (rect, shadows, embedded_walls, shared) == (True, False, False, False)
        return [Eid(900 + k) for k in range(self.n_open)]

    def get_BoundingBox(self, view):
        assert view is None
        return types.SimpleNamespace(Min=types.SimpleNamespace(Z=0.0), Max=types.SimpleNamespace(Z=self.bbox_h))


class Names(type):
    def __getattr__(cls, n):
        return n


class BuiltInParameter(metaclass=Names):
    pass


class BuiltInCategory(metaclass=Names):
    pass


class Collector:
    def __init__(self, doc): self.doc = doc
    def OfCategory(self, c): return self
    def WhereElementIsNotElementType(self): return self
    def ToElements(self): return [e for e in Elem.reg.values() if isinstance(e, Wall)]


class Element:
    Name = types.SimpleNamespace(GetValue=lambda e: e._name)


DB = types.SimpleNamespace(
    Wall=Wall, LocationCurve=LocationCurve, FilteredElementCollector=Collector,
    BuiltInParameter=BuiltInParameter, BuiltInCategory=BuiltInCategory, Element=Element,
    ElementId=types.SimpleNamespace(InvalidElementId=Eid(-1)),
    WallCrossSection=types.SimpleNamespace(Vertical="V", SingleSlanted="S", Tapered="T"))

SELECTION = []
doc = types.SimpleNamespace(GetElement=lambda eid: Elem.reg.get(eid.Value))
uidoc = types.SimpleNamespace(Selection=types.SimpleNamespace(GetElementIds=lambda: SELECTION))


@contextlib.contextmanager
def Transaction(name, doc=None):
    yield


# ---- fake pyRevit forms / config / WPF --------------------------------------
class Ev:
    def __init__(self): self.h = []
    def __iadd__(self, f): self.h.append(f); return self


class Ctl:
    def __init__(self): self.Text = ""; self.ItemsSource = None; self.Click = Ev()


class WPFWindow:
    last = None

    def __init__(self, xaml):
        assert os.path.exists(xaml), xaml
        self.ctl = {}
        WPFWindow.last = self

    def FindName(self, n): return self.ctl.setdefault(n, Ctl())
    def ShowDialog(self): pass


ALERTS = []


def alert(msg, **kw):
    ALERTS.append(msg)
    if kw.get("exitscript"):
        raise SystemExit(msg)
    return True


CFG = {}
SAVE = []        # paths the fake save dialog returns
PICK = ["net"]   # which pricing basis the fake choice dialog returns
IDS_PATH = [os.path.join(ROOT, "examples", "panel_requirements.ids")]   # what the fake file picker returns
cfg = types.SimpleNamespace(get_option=lambda k, d=None: CFG.get(k, d),
                            set_option=lambda k, v: CFG.__setitem__(k, v))
forms = types.SimpleNamespace(
    alert=alert, ask_for_string=lambda **kw: "10",
    save_file=lambda **kw: SAVE.pop(0) if SAVE else None, WPFWindow=WPFWindow,
    pick_file=lambda **kw: IDS_PATH[0],
    CommandSwitchWindow=types.SimpleNamespace(
        show=lambda options, message=None, **kw: options[1] if PICK[0] == "gross" else options[0]))
out = types.SimpleNamespace(print_md=print, print_table=lambda *a, **k: None, print_code=print)
script = types.SimpleNamespace(get_output=lambda: out, get_config=lambda section=None, reload=False: cfg,
                               save_config=lambda: None)
revit = types.SimpleNamespace(doc=doc, uidoc=uidoc, Transaction=Transaction)
pyrevit = types.ModuleType("pyrevit")
pyrevit.revit, pyrevit.DB, pyrevit.forms, pyrevit.script = revit, DB, forms, script
sys.modules["pyrevit"] = pyrevit


# fake .NET bits for bauser_ui
class _Rows(list):
    def Add(self, r): self.append(r)


class DataTable:
    def __init__(self, n):
        self.cols = []
        self.Columns = types.SimpleNamespace(Add=lambda c: self.cols.append(c))
        self.Rows, self.DefaultView = _Rows(), self

    def NewRow(self): return [None] * len(self.cols)


sys.modules["clr"] = types.SimpleNamespace(AddReference=lambda n: None)
sys.modules["System"] = types.SimpleNamespace(Data=None, Windows=None)
sys.modules["System.Data"] = types.SimpleNamespace(DataTable=DataTable)
sys.modules["System.Windows"] = types.SimpleNamespace(Visibility=types.SimpleNamespace(Visible="Visible"))


# ---- model: 2 levels, 2 wall types, 4 walls (feet / ft2, like Revit) ---------
Level(10, "Level 1", 0.0)
Level(11, "Level 2", 10.0)
TypeElem(20, "LSF 140")
TypeElem(21, "Drywall")
Wall(1, 20, 11, 0.0, 10.0, 100.0, 10.0, openings=1, fire=True)   # level 2
Wall(2, 20, 10, 8.0, 10.0, 80.0, 10.0, openings=2)    # level 1, x=8; net 80 = 100 - 20 ft2 of openings
Wall(3, 21, 10, 1.0, 5.0, 50.0, 10.0)                 # level 1, x=1
Wall(4, 20, 10, 4.0, 10.0, 100.0, 10.0, edited=True)  # level 1, x=4; has an edited profile
NET_FT2, GROSS_FT2 = 330.0, 350.0                     # sum of net areas / of length x bbox height


def button(name):
    return os.path.join(EXT, "Bauser.tab", "Panels.panel", name + ".pushbutton", "script.py")


def run(name):
    runpy.run_path(button(name))
    w = WPFWindow.last
    return {k: v.Text for k, v in w.ctl.items()}, w.FindName("grid").ItemsSource.Rows, w


def csv_lines(path):
    return open(path, encoding="utf-8-sig").read().splitlines()


# ---- English ----------------------------------------------------------------
CFG["lang"] = "en"

t, rows, w = run("Count")
assert t["v1"] == "4" and t["v2"] == "2" and t["subtitle"] == "Entire model", t
assert t["v3"] == "%.1f m²" % (NET_FT2 * 0.09290304), t
assert {r[0]: r[2] for r in rows} == {"Drywall": "0", "LSF 140": "3"}, rows   # openings per type

t, rows, w = run("Number")
marks = [(i, Elem.reg[i].p["ALL_MODEL_MARK"].text) for i in (3, 4, 2, 1)]
assert marks == [(3, "P-001"), (4, "P-002"), (2, "P-003"), (1, "P-004")], marks  # L1 by x, then L2
assert t["v1"] == "4" and t["v3"] == "P-001 - P-004", t

t, rows, w = run("Cost")
assert re.match(r"R\$ [\d,]+\.\d\d$", t["v1"]) and len(rows) == 4 and rows[0][0] == "P-001", (t, rows[0])
# default basis is net: 330 ft2 of net area, 10% waste
assert t["v1"] == core.money(NET_FT2 * 0.09290304 * core.DEFAULT_RATE * 1.10, "en"), t["v1"]
assert "Net area" in t["footnote"] and rows[0][3] == "0", (t["footnote"], rows[0])  # P-001 = wall 3, no openings

assert not any("upper bound" in m for m in ALERTS)                 # net basis: no irregular-wall warning

PICK[0] = "gross"                                                  # full panel size = length x height
ALERTS.clear()
t_g, rows_g, w_g = run("Cost")
warn = [m for m in ALERTS if "upper bound" in m]
assert len(warn) == 1 and warn[0].startswith("1 panel(s)"), ALERTS   # wall 4 has an edited profile
assert t_g["v1"] == core.money(GROSS_FT2 * 0.09290304 * core.DEFAULT_RATE * 1.10, "en"), t_g["v1"]
assert "Full panel size" in t_g["footnote"] and t_g["v1"] != t["v1"]
PICK[0] = "net"
assert t["v2"].startswith(u"€ ") and "5,6682" not in t["l2"] and "5.6682" in t["l2"] and "2026-10-19" in t["l2"], t
assert w.FindName("btn_budget").Visibility == "Visible"          # budget export only on the Cost window
assert rows[0][6] == "-"                                          # no SINAPI code configured -> dash

with tempfile.TemporaryDirectory() as d:
    SAVE.append(os.path.join(d, "b.csv"))
    w.ctl["btn_budget"].Click.h[0](None, None)
    lines = csv_lines(os.path.join(d, "b.csv"))
    assert lines[0] == "Code,Description,Unit,Qty,Unit price (R$),Total (R$)", lines[0]
    assert lines[1].startswith(",Drywall,m2,") and lines[2].startswith(",LSF 140,m2,"), lines[1:3]
    assert any("TOTAL (R$)" in line for line in lines) and any("TOTAL (EUR, approx.)" in line for line in lines), lines

SELECTION[:] = [Eid(1)]
t, rows, w = run("Count")
assert t["v1"] == "1" and t["subtitle"].startswith("Selection"), t
SELECTION[:] = []

# ---- Portuguese (default) -----------------------------------------------------
CFG["lang"] = "pt"

t, rows, w = run("Cost")
assert t["title"] == u"Estimativa de custo dos painéis", t
assert re.match(r"R\$ [\d.]+,\d\d$", t["v1"]), t["v1"]           # R$ 1.234,56
assert "Aprox. em EUR" in t["l2"] and w.FindName("btn_budget").Content == u"Exportar orçamento CSV"

with tempfile.TemporaryDirectory() as d:
    SAVE.append(os.path.join(d, "c.csv"))
    w.ctl["btn_export"].Click.h[0](None, None)
    first = csv_lines(os.path.join(d, "c.csv"))[0]
    assert first.count(";") == 7 and "Ref. SINAPI" in first, first   # pt-BR Excel delimiter

# ---- irregular-wall detection --------------------------------------------------
import bauser_revit as rv
assert not rv._is_irregular(Wall(90, 20, 10, 0.0, 1.0, 1.0, 1.0))
assert rv._is_irregular(Wall(91, 20, 10, 0.0, 1.0, 1.0, 1.0, edited=True))
assert rv._is_irregular(Wall(92, 20, 10, 0.0, 1.0, 1.0, 1.0, slanted=True))
assert not rv._is_irregular(types.SimpleNamespace(CrossSection="V"))   # Revit < 2022 has no SketchId
for k in (90, 91, 92):
    del Elem.reg[k]                                                    # keep the model walls only

# ---- Classify Panels and IDS Check ---------------------------------------------
import tempfile  # noqa: E402

CFG["lang"] = "en"
LSF_CODE = {"rates": {"LSF": {"rate": 500, "classification": {"system": "NBR 15965", "code": "3E.02"}}}}
core.apply_config(LSF_CODE)
code_param = Elem.reg[20].p["CLASSIFICATION_CODE"]

code_param.IsReadOnly = True                                    # a read-only parameter is reported, not forced
t, rows, w = run("Classify")
assert code_param.text == "" and (t["v1"], t["v2"], t["v3"]) == ("0", "1", "1"), t
assert rows == [["LSF 140", "NBR 15965", "3E.02", "3", "Read-only"]], rows
code_param.IsReadOnly = False

t, rows, w = run("Classify")                                    # wall types with a configured code get it
assert code_param.text == "3E.02" and Elem.reg[21].p["CLASSIFICATION_CODE"].text == "", "Drywall is left alone"
assert (t["v1"], t["v2"], t["v3"]) == ("1", "0", "1"), t        # written, not written, types without a code
assert rows == [["LSF 140", "NBR 15965", "3E.02", "3", "Written"]], rows

core.apply_config({})                                           # no codes configured: a message, no changes
try:
    run("Classify")
except SystemExit:
    pass
assert "No classification codes" in ALERTS[-1], ALERTS[-1]

core.apply_config(LSF_CODE)                                     # IDS Check against the shipped example file
ALERTS.clear()
t, rows, w = run("IdsCheck")
assert t["subtitle"].startswith("Wall panel information requirements (example)"), t["subtitle"]
assert (t["v1"], t["v2"], t["v3"]) == ("1", "4", "4"), t        # 1 specification, 4 panels, 4 failed requirements
verdict = {(r[0], r[2]): r[3] for r in rows}
assert len(rows) == 12 and verdict[("P-004", "property Pset_WallCommon.FireRating")] == "Pass", rows
assert verdict[("P-001", "classification NBR 15965 any")] == "Fail"   # the Drywall wall has no code
assert verdict[("P-003", "property Pset_WallCommon.FireRating")] == "Fail"

with tempfile.TemporaryDirectory() as d:                        # a file that is not IDS gives a message
    junk = os.path.join(d, "x.ids")
    open(junk, "w").write("not xml")
    IDS_PATH[0] = junk
    ALERTS.clear()
    try:
        run("IdsCheck")
    except SystemExit:
        pass
    assert any("Could not read the IDS file" in m for m in ALERTS), ALERTS
IDS_PATH[0] = os.path.join(ROOT, "examples", "panel_requirements.ids")

CFG["lang"] = "pt"
t, rows, w = run("IdsCheck")
assert t["title"] == u"Verificação IDS" and rows[0][3] == "Atende", (t["title"], rows[0])
core.load_config()                                              # back to the shipped file

# ---- Language button flips and persists --------------------------------------
CFG["lang"] = "pt"
runpy.run_path(button("Language"))
assert CFG["lang"] == "en"
runpy.run_path(button("Language"))
assert CFG["lang"] == "pt"

print("adapter + scripts OK")
