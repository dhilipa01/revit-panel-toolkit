# Standards and sources

Notes on the Brazilian standards, price references and trade context around this extension. Each item says what the repository does with it and how well the source is known. Facts were checked on 2026-10-20.

## ABNT NBR 16970:2022, light steel framing

Three parts, published 2022-05-23: Part 1 performance, Part 2 structural design, Part 3 interfaces between systems.

The standard is paywalled and was not read in full. What is known about Part 3 comes from:

- ABNT committee drafts of Part 3 (CE-002:125.004, 2020 and 2021), hosted by CAU/BR and marked as having no normative value
- the scope text published by the sellers (Target, DIN Media)
- the table of contents of a third-party copy

Interfaces covered, in the drafts: walls with openings (esquadrias), walls with services and foundation, mixed systems, wall to slab, fixings, floors, linings, roofs and building installations. For mixed systems, where light steel framing meets concrete, masonry, heavy steel or wood, the drafts ask for watertightness at the joint, compatible materials and movement joints.

Scope in the drafts and in ABCEM's summary: residential and non-residential buildings of up to two storeys. Whether the standard covers non-structural infill panels on tall concrete frames is an open question. Check the purchased text before claiming compliance.

In this repository: the Openings column and the roadmap item for an interface check follow the Part 3 topics. Nothing in the code claims conformity.

## SINAPI

Price and cost reference for building works, run by Caixa and IBGE, updated monthly, published per state with desonerado and não desonerado prices.

- It is the first reference for budgets of works paid with federal money: Lei 14.133/2021 art. 23 par. 2, and Decreto 7.983/2013. It is not required for private projects.
- Caixa publishes a technical notebook "Paredes em Drywall" with 25 active compositions. No light steel frame composition was found in the sources searched. That does not prove none exists.

In this repository: the rates table has an optional reference code column. The code is a label. No SINAPI data is imported, and the default price of R$ 490.00/m2 is a placeholder, not a SINAPI figure.

## BIM in Brazil

- Decreto 11.888 of 2024-01-22 sets the current national BIM strategy (Estratégia BIM BR) and revokes Decreto 9.983/2019.
- Decreto 10.306/2020, which phases BIM into federal works, is listed by Planalto as having no express revocation.

## EU-Mercosur and Mercosur-EFTA

- EU-Mercosur: signed 2026-01-17. The interim trade agreement has applied provisionally since 2026-05-01. It is not fully in force, because the European Parliament has not given its consent. The Parliament asked the EU Court of Justice for an opinion.
- Mercosur-EFTA: signed 2025-09-16. For Brazil it entered into force on 2026-10-01 with Iceland and on 2026-11-01 with Norway (gov.br, Siscomex).
- The public procurement chapter lets EU firms bid on Brazilian government works and engineering services (EEAS guide, 2026-06-19). Brazilian tenders run under Lei 14.133, whose art. 52 allows a preference margin for goods and services that follow Brazilian technical standards.

In this repository: only the EUR figure next to BRL follows from this. The trade agreements change nothing in the code.

## Exchange rates

The Banco Central do Brasil PTAX service is free and needs no key: `https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/`. It lists 10 currencies: AUD, CAD, CHF, DKK, EUR, GBP, JPY, NOK, SEK and USD. ARS, UYU and PYG are not included.

In this repository: `FX` holds one static EUR/BRL snapshot, the PTAX closing (sell) of 2026-10-19: 5.6682. Refresh it by hand when it matters.

## Revit API references

- `HostObject.FindInserts`, inherited by `Wall`: documented by Autodesk for the Revit 2026 API
- `Wall.SketchId`, `Wall.CrossSection`, `Element.BoundingBox`: documented by Autodesk
- Wall Area excludes hosted openings: described by The Building Coder, Autodesk's developer blog. Autodesk Support notes that opening areas cannot be read directly as a parameter
