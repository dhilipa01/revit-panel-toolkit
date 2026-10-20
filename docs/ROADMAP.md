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
- [x] Configuration in a JSON file
- [x] Classification code per wall type
- [x] IDS check against the Revit parameters
- [x] Tests that run outside Revit, linting and CI
- [x] Release workflow and extension metadata

## Next

- [ ] Run the extension in a live Revit session and record the results ([checklist](VERIFY_IN_REVIT.md))
- [ ] Add screenshots with one frame style: same aspect ratio, padding, corner radius and window frame
- [ ] Confirm that Revit accepts the classification code written through the API, and on which Revit versions
- [ ] Detect walls with an attached top or base
- [ ] Check an exported IFC file against an IDS file, not only the Revit parameters

## Later

- [ ] Split a wall into panels
- [ ] Automatic panel detailing for factory production
- [ ] Create a panel assembly with its assembly views and sheet, for factory shop drawings
- [ ] Export a cutting list for factory production
- [ ] Panel labels with a QR code or barcode, and a status for each panel, which existing framing products offer[^onyx]
- [ ] Machine output for roll formers and panel machines, once a target machine and its format are known
- [ ] Interface check for the NBR 16970-3 topics: wall to slab, wall to opening, mixed systems
- [ ] A signed release and an installer, which Autodesk's publisher guidelines ask for[^publisher]
- [ ] Live exchange rate with a date, and currencies PTAX does not cover (ARS, UYU, PYG)
- [ ] Documentation in Portuguese

Ideas and bugs go in [Issues](https://github.com/dhilipa01/revit-panel-toolkit/issues).

[^onyx]: Graitec Strucsoft, "Production management software". https://strucsoftsolutions.com/solutions/production-management-software. Accessed 2026-10-20. Cited because it shows QR and barcode tracking of individual panels through manufacturing, stacking and shipping in an existing product, which is the model for the label item. It is the vendor's own description.
[^publisher]: Autodesk Platform Services, "Revit publisher guidelines". https://aps.autodesk.com/marketplace/publisher-center/revit-publisher-guidelines. Accessed 2026-10-20. Cited for the marketplace requirements on a ribbon button, an add-in manifest and an installer with no manual steps. Revit also prompts for add-ins without a trusted signature: https://help.autodesk.com/cloudhelp/2022/ENU/Revit-Troubleshooting/files/GUID-36D29367-A540-4CFD-9773-4995BF1DF08A.htm.
