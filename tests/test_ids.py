"""Run: python tests/test_ids.py. Covers the IDS reader and the Revit-side check."""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src", "Bauser.extension", "lib"))
import bauser_ids as ids  # noqa: E402

EXAMPLE = os.path.join(HERE, "..", "examples", "panel_requirements.ids")
WRAP = ('<ids xmlns="http://standards.buildingsmart.org/IDS" xmlns:xs="http://www.w3.org/2001/XMLSchema">'
        '<info><title>T</title></info><specifications><specification name="S" ifcVersion="IFC4">'
        '<applicability>%s</applicability><requirements>%s</requirements></specification>'
        '</specifications></ids>')
WALL = "<entity><name><simpleValue>IFCWALL</simpleValue></name></entity>"
DOOR = "<entity><name><simpleValue>IFCDOOR</simpleValue></name></entity>"


def prop(name, value="", card="required"):
    v = "<value><simpleValue>%s</simpleValue></value>" % value if value else ""
    return ('<property cardinality="%s"><propertySet><simpleValue>Pset_X</simpleValue></propertySet>'
            "<baseName><simpleValue>%s</simpleValue></baseName>%s</property>" % (card, name, v))


def restriction(kind, *values):
    items = "".join('<xs:%s value="%s"/>' % (kind, v) for v in values)
    return '<xs:restriction base="xs:string">%s</xs:restriction>' % items


def run(panels, applicability, requirements):
    parsed = ids.parse_ids(io.BytesIO((WRAP % (applicability, requirements)).encode("utf-8")))
    return ids.check(panels, parsed)


def panel(i, **kw):
    p = {"id": i, "mark": "P-%03d" % i, "type": "Facade", "properties": {}, "classification": "",
         "classification_system": ""}
    p.update(kw)
    return p


def states(rows):
    return [r[3] for r in rows]


# the shipped example file reads and checks
spec = ids.parse_ids(EXAMPLE)
assert spec["title"].startswith("Wall panel information requirements")
assert [(s["name"], len(s["requirements"])) for s in spec["specs"]] == [
    ("Wall panels are numbered, classified and rated", 3)]
good = panel(1, properties={"Fire Rating": "EI60"}, classification="3E.02", classification_system="NBR 15965")
bad = panel(2, mark="")
rows = ids.check([good, bad], spec)
assert [(r[0], r[3]) for r in rows] == [("P-001", "Pass")] * 3 + [("id 2", "Fail")] * 3
assert ids.summarise(rows) == {"Pass": 3, "Fail": 3, "Not checked": 0, "panels": 2}
assert rows[1][2] == "classification NBR 15965 any" and rows[2][2] == "property Pset_WallCommon.FireRating"

# a classification with the wrong system does not count
assert states(ids.check([panel(1, classification="3E.02", classification_system="OmniClass")], spec))[1] == "Fail"

# property names ignore case, spaces and underscores; values must be non-empty
assert states(run([panel(1, properties={"fire_rating": "EI60"})], WALL, prop("FireRating"))) == ["Pass"]
assert states(run([panel(1, properties={"FireRating": ""})], WALL, prop("FireRating"))) == ["Fail"]

# value checks: plain value, enumeration, pattern
vals = {"Mat": "Steel"}
assert states(run([panel(1, properties=vals)], WALL, prop("Mat", "Steel"))) == ["Pass"]
assert states(run([panel(1, properties=vals)], WALL, prop("Mat", "Wood"))) == ["Fail"]
enum = ('<property><propertySet><simpleValue>P</simpleValue></propertySet><baseName><simpleValue>Mat</simpleValue>'
        "</baseName><value>%s</value></property>")
assert states(run([panel(1, properties=vals)], WALL, enum % restriction("enumeration", "Steel", "Wood"))) == ["Pass"]
assert states(run([panel(1, properties=vals)], WALL, enum % restriction("enumeration", "Wood"))) == ["Fail"]
assert states(run([panel(1, properties=vals)], WALL, enum % restriction("pattern", "St.*"))) == ["Pass"]
assert states(run([panel(1, properties=vals)], WALL, enum % restriction("pattern", "St"))) == ["Fail"]   # anchored
assert states(run([panel(1, properties=vals)], WALL, enum % restriction("minLength", "2"))) == ["Not checked"]

# cardinality
absent, present = panel(1), panel(2, properties={"Mat": "Steel"})
assert states(run([absent, present], WALL, prop("Mat", card="prohibited"))) == ["Pass", "Fail"]
assert states(run([absent, present], WALL, prop("Mat", "Wood", card="optional"))) == ["Pass", "Fail"]
assert states(run([absent, present], WALL, prop("Mat", card="required"))) == ["Fail", "Pass"]

# applicability: other entities do not apply; a property can filter
assert run([panel(1)], DOOR, prop("Mat")) == []
filtered = WALL + prop("Mat", "Steel")
assert [r[0] for r in run([absent, present], filtered, prop("X"))] == ["P-002"]

# attributes: Name is the type name, Tag is the Mark
attr = '<attribute><name><simpleValue>%s</simpleValue></name><value><simpleValue>%s</simpleValue></value></attribute>'
assert states(run([panel(1)], WALL, attr % ("Name", "Facade"))) == ["Pass"]
assert states(run([panel(1)], WALL, attr % ("Tag", "P-009"))) == ["Fail"]
assert states(run([panel(1)], WALL, attr % ("ObjectType", "x"))) == ["Not checked"]

# facets that are not read give a Not checked row, not a silent pass
material = "<material><value><simpleValue>Steel</simpleValue></value></material>"
assert states(run([panel(1)], WALL, material)) == ["Not checked"]
part_of = "<partOf><entity><name><simpleValue>IFCBUILDING</simpleValue></name></entity></partOf>"
rows = run([panel(1), panel(2)], part_of, prop("Mat"))
assert [(r[0], r[3]) for r in rows] == [("-", "Not checked")]   # one row for the specification

# bad input
for source in (b"not xml", b'<ids xmlns="urn:other"/>'):
    try:
        ids.parse_ids(io.BytesIO(source))
    except ValueError:
        pass
    else:
        raise AssertionError("accepted %r" % source)

print("ids OK")
