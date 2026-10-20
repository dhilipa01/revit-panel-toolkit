# Roadmap

Open work, in the order it is likely to be done. Finished items stay listed so the direction is visible.

## Done

- [x] Count, number and price wall panels from the ribbon
- [x] Net area and full panel size pricing
- [x] Openings per panel from `FindInserts`
- [x] Warning for walls with an edited profile or a slanted or tapered section
- [x] Portuguese and English labels
- [x] BRL with an approximate EUR figure
- [x] Per-panel CSV and budget CSV
- [x] Tests that run outside Revit, and CI

## Next

- [ ] Run the extension in a live Revit session and record the results ([checklist](VERIFY_IN_REVIT.md))
- [ ] Add screenshots with one frame style: same aspect ratio, padding, corner radius and window frame
- [ ] Detect walls with an attached top or base
- [ ] Read prices from a JSON file instead of editing `bauser_core.py`

## Later

- [ ] Split a wall into panels
- [ ] Automatic panel detailing for factory production
- [ ] Create a panel assembly with its assembly views and sheet, for factory shop drawings
- [ ] Export a cutting list for factory production
- [ ] Interface check for the NBR 16970-3 topics: wall to slab, wall to opening, mixed systems
- [ ] Live exchange rate with a date, and currencies PTAX does not cover (ARS, UYU, PYG)
- [ ] Documentation in Portuguese

Ideas and bugs go in [Issues](https://github.com/dhilipa01/revit-panel-toolkit/issues).
