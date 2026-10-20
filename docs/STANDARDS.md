# Standards and sources

Notes on the Brazilian standards, price references and trade context around this extension. Each section says what the repository does with the source and how well the source is known. Facts were checked on 2026-10-20. The numbered notes at the end of the page give the source and the reason for each citation.

## ABNT NBR 16970:2022, light steel framing

The standard has three parts, all published on 2022-05-23: Part 1 performance, Part 2 structural design and Part 3 interfaces between systems.[^din]

The standard is paywalled and was not read in full. What is known about Part 3 comes from three kinds of source:

- ABNT committee drafts of Part 3, from 2020 and 2021, hosted by the Brazilian architects' council (CAU/BR) and marked as having no normative value.[^draft21][^draft20]
- The scope text published by the sellers of the standard.[^target]
- The table of contents of a third-party copy. It lists walls and frames, walls with services and foundation, mixed systems, wall to slab, fixings, floors, linings, roofs and building installations.[^scribd]

In the drafts, the interface chapter on mixed systems covers light steel framing that meets concrete, masonry, heavy steel or wood. It asks for watertightness at the joint, compatible materials and movement joints.[^draft21] The chapter on walls with frames asks the design to guarantee the opening for fixing the frames.[^draft20]

The scope in the drafts and in the summary by the Brazilian steel construction association (ABCEM) is residential and non-residential buildings of up to two storeys.[^draft21][^abcem] Whether the standard covers non-structural infill panels on tall concrete frames is an open question. Check the purchased text before claiming compliance.

In this repository: the Openings column and the roadmap item for an interface check follow the Part 3 topics. Nothing in the code claims conformity.

## ABNT NBR 15965, classification of construction information

NBR 15965 is the Brazilian classification system for construction information. It has seven parts and thirteen tables: Part 1 (2011), Part 2 (2012), Part 3 (2014), Part 4 (2021), Part 5 (2022), Part 6 (2022) and Part 7 (2015).[^siurb] A full description of one element combines codes from several tables.[^dnit]

Public clients use it. A federal client specification names it as the classification system and asks the BIM Execution Plan to fix the coding.[^dnit] A state specification requires the contract to name at least one classification system, NBR 15965, SINAPI or DEINFRA, for the parameters of model entities.[^sc] The São Paulo city works department lists all seven parts as references.[^siurb]

In this repository: the Classify Panels button writes a code that the user supplies in `bauser_config.json`. The codes shown in the examples, such as `3E.02`, are placeholders. Take real codes from the standard.

## ISO 19650, level of information need and IDS

The first two parts of ISO 19650 are published in Portuguese as ABNT NBR ISO 19650-1 and -2, both 2022.[^dnit] Brazilian specifications built on them ask for a BIM Execution Plan, information requirements, a common data environment and the roles of BIM Manager, BIM Coordinator and BIM Modeller.[^dnit]

ISO 7817-1:2024 on level of information need was published in June 2024. Its parts 2 and 3 were still in development on 2026-09-19.[^iso7817] The BIMForum LOD specification of 2024 describes the level of information need as the quality, quantity and granularity of geometric, alphanumeric and documentation information, and treats LOD as the part that covers geometry.[^bimforum]

buildingSMART's Information Delivery Specification (IDS) is a machine-readable way to state those requirements. Version 1.0 has been approved as a final standard.[^idsfinal] buildingSMART describes it as the standard to use for defining level of information needs, and as a contract and a validation mechanism.[^idstech]

In this repository: the IDS Check button reads an IDS 1.0 file. The mapping from IDS terms to Revit parameters and its limits are in [Reference](REFERENCE.md#ids-check).

## SINAPI

SINAPI is the price and cost reference for building works. Caixa and IBGE run it jointly, and it is published monthly with desonerado and não desonerado prices.[^ibge][^caixa]

- It is the first reference for budgets of works paid with federal money. Lei 14.133/2021 art. 23 paragraph 2 sets SINAPI first for works other than transport infrastructure,[^lei14133] and Decreto 7.983/2013 sets the same rule for the federal budget.[^dec7983] The decree was amended again in March 2026 by Decreto 12.867.[^dec7983] The rule does not bind private projects.
- Caixa publishes a technical notebook "Paredes em Drywall".[^drywall] A third-party transcription counts 25 active compositions in it.[^buscador] No light steel frame composition was found in the sources searched. That does not prove none exists.

In this repository: the rates table has an optional reference column. The value is a label. No SINAPI data is imported, and the default price of R$ 490.00/m2 is a placeholder, not a SINAPI figure.

## BIM in Brazil

- Decreto 11.888 of 2024-01-22 sets the current national BIM strategy, Estratégia BIM BR, and revokes Decreto 9.983/2019.[^d11888]
- Decreto 10.306/2020, which phases BIM into federal works, is listed by the Presidency's legislation database as having no express revocation.[^d10306]

## EU-Mercosur and Mercosur-EFTA

- EU-Mercosur: signed on 2026-01-17. The interim trade agreement has applied provisionally since 2026-05-01. It is not fully in force, because the European Parliament has not given its consent.[^eutrade][^eucom] The Parliament asked the EU Court of Justice for an opinion on whether the agreements fit the EU treaties.[^europarl]
- Mercosur-EFTA: signed on 2025-09-16. For Brazil it entered into force on 2026-10-01 with Iceland and enters into force on 2026-11-01 with Norway, after Decreto 13.126 of 2026-09-23.[^efta]
- The public procurement chapter lets EU firms bid on Brazilian government works and engineering services. Brazil's offer lists works under CPC Division 51 and engineering services separately.[^eeas]

In this repository: only the EUR figure next to BRL follows from this. The trade agreements change nothing in the code.

## Exchange rates

The Banco Central do Brasil PTAX service is free and needs no key. It lists ten currencies: AUD, CAD, CHF, DKK, EUR, GBP, JPY, NOK, SEK and USD. ARS, UYU and PYG are not included.[^ptax]

In this repository: `fx` in the configuration holds one static EUR/BRL snapshot, the PTAX closing (sell) of 2026-10-19: 5.6682. Refresh it by hand when it matters.

## Tools in the same space

Two commercial products show what users of panel software expect beyond a quantity and a price.

- Strucsoft MWF, from Graitec, frames light gauge steel and wood panels in Revit and writes shop drawings, cut lists and machine output for several roll formers and panel machines.[^strucsoft] Its ONYX tool carries production data to the factory floor with a QR code for each panel.[^onyx]
- AltoQi's Eberick and Builder are Brazilian structural and building services software that export IFC.[^altoqi]

This extension stops at a CSV, a classification code and an IDS check. Machine output and labelling are on the [Roadmap](ROADMAP.md).

## Documentation in Portuguese

No ABNT standard sets the layout of a README or of a software user guide. The closest ones are written for other kinds of document, and the sources say so.

- ABNT NBR 14724:2024, fourth edition of 2024-12-16, covers academic works and similar documents. It names the supporting standards for references (NBR 6023), section numbering (NBR 6024), contents (NBR 6027) and abstracts (NBR 6028). It also says that ABNT documents are voluntary and do not replace laws.[^nbr14724]
- ABNT NBR 6023:2025, third edition of 2025-05-21, cancels the 2018 edition. It sets the elements and the order of a reference, and allows a reference in a footnote, at the end of a text or in a list.[^nbr6023]
- ABNT NBR 10520:2023 covers citations in the text. The source used here is a university guide.[^nbr10520]
- ISO/IEC/IEEE 26514:2022, published in January 2022, covers the design and development of information for users of software. It replaced the 2008 edition. It is paywalled and was not read.[^iso26514]
- The Portuguese Language Orthographic Agreement of 1990 was promulgated in Brazil by Decreto 6.583/2008.[^acordo] It took effect on 2009-01-01, with a transition that a later decree extended to 2015-12-31.[^acordotrans]
- The consumer code, art. 31, requires information on products and services in Portuguese.[^cdc] It is written for the offer of products and services to consumers. Whether it reaches software sold to companies was not researched, so it is not treated as a requirement for this repository.

What the Portuguese documentation does: it follows the current orthography, numbers its notes in the order of first appearance, gives each note the elements that NBR 6023 asks for (the issuing body, the title, "Disponível em", "Acesso em" and the date with an abbreviated month), and writes numbers and dates the Brazilian way. It uses Autodesk's own Portuguese wording for Revit terms where Autodesk's help gives it,[^ptbhelp] and says where it does not. It does not follow the layout of NBR 14724 or the section numbering of NBR 6024, which are written for academic works, and it does not claim to follow ISO/IEC/IEEE 26514 as a whole.

The Portuguese pages are in [docs/pt-BR](pt-BR/NORMAS_E_FONTES.md).

## Distribution notes

Autodesk's publisher guidelines for Revit apps ask for a ribbon button, an add-in manifest as the loading mechanism and an installer that works with no manual steps.[^publisher] Revit shows a security prompt when an add-in is not digitally signed by a trusted authority.[^signing] This extension is a pyRevit extension and is neither signed nor packaged for the Autodesk marketplace.

## Revit API references

See the notes in [Reference](REFERENCE.md#revit-data-used).

[^din]: DIN Media, "ABNT NBR 16970-3, 2022-05-23". https://www.dinmedia.de/en/standard/abnt-nbr-16970-3/355816863. Accessed 2026-10-20. Cited for the title of Part 3 and its publication date. The same seller lists Parts 1 and 2 with the same date.
[^draft21]: ABNT/CB-002, "Projeto ABNT NBR 16970-3", draft of 2021-08-27, hosted by CAU/BR. https://transparencia.caubr.gov.br/arquivos/ABNT-CB-002-CE002125004_N0_Minuta-LSF-NBR-16970-Parte-III-27082021.pdf. Accessed 2026-10-20. Cited because it is the closest freely available text to the published Part 3. It is a draft marked "no normative value", so the published wording may differ.
[^draft20]: ABNT/CB-002/CE 125.004, working draft of Part 3, 2020-12-15, hosted by CAU/BR. https://transparencia.caubr.gov.br/arquivos/Minuta-_GT_LSF_para-Zacarias.pdf. Accessed 2026-10-20. Cited for the earlier wording on walls with frames, foundations and mixed systems. It is an earlier draft than the 2021 one and is marked "no normative value".
[^target]: Target Normas, "ABNT NBR 16970-3". https://www.normas.com.br/visualizar/abnt-nbr-nm/13382/abnt-nbr16970-3-light-steel-framing-sistemas-construtivos-estruturados-em-perfis-leves-de-aco-formados-a-frio-com-fechamentos-em-chapas-delgadas-parte-3-interfaces-entre-sistemas. Accessed 2026-10-20. Cited for the scope sentence of the published standard: requirements and construction details for interfaces between systems, such as wall and floor, wall and frame, and wall or floor and services.
[^scribd]: Scribd copy of ABNT NBR 16970-3:2022, table of contents only. https://www.scribd.com/document/956286152/NBR-16970-3-2022-Light-Steel-Framing-Structural-construction-systems-made-of-cold-formed-light-steel-profiles-with-thin-sheet-closures-Part-3. Accessed 2026-10-20. Cited only for the list of chapter headings. It is an uncontrolled third-party copy and the clauses were not relied on.
[^abcem]: ABCEM, "Light Steel Frame: Aplicação das Normas Brasileiras". https://www.abcem.org.br/site/blog/light-steel-frame-aplicacao-das-normas-brasileiras. Accessed 2026-10-20. Cited as an industry association's summary of the three parts, including the limit of two storeys for Part 1.
[^siurb]: Prefeitura de São Paulo, SIURB, "Coleção BIM SIURB, Caderno 1: Diretrizes para a contratação de projetos com uso de BIM", 2025-10-07. https://participemais.prefeitura.sp.gov.br/system/documents/attachments/000/004/156/original/6f4036de81ce4187bfa997464eac68f2b2e38a45.pdf. Accessed 2026-10-20. Cited for the list of the seven parts of NBR 15965 with their years, and the other ABNT references used in Brazilian BIM contracts.
[^dnit]: DNIT, "Caderno de Requisitos Técnicos BIM", 2023. https://www.gov.br/dnit/pt-br/assuntos/planejamento-e-pesquisa/bim-no-dnit/mosaico-de-servicos/documentos-tecnicos-bim/CRTBIM__2023_v2.pdf. Accessed 2026-10-20. Cited as a federal client document. It states that the NBR ISO 19650 parts 1 and 2 were published in Portuguese in 2022, defines the BIM Execution Plan and the three BIM roles, and names NBR 15965 as the classification system.
[^sc]: Governo de Santa Catarina, Secretaria de Estado do Planejamento, "Caderno de Especificações de Projetos em BIM", 2018. https://www.sie.sc.gov.br/webdocs/sie/doc-tecnicos/labim/Caderno%20de%20Especifica%C3%A7%C3%B5es%20de%20Projetos%20em%20BIM_102018.pdf. Accessed 2026-10-20. Cited because it is a state client document that requires at least one classification system in the model parameters. It is dated 2018, before several parts of NBR 15965 existed.
[^iso7817]: ISO, "ISO 7817-1:2024 Building information modelling, Level of information need, Part 1". https://www.iso.org/standard/82914.html. Accessed 2026-10-20. Cited for the publication date and price. The status of parts 2 and 3 comes from the ISO/TC 59/SC 13 catalogue, https://www.iso.org/committee/49180/x/catalogue/p/1/u/1/w/0/d/0, listed on 2026-09-19.
[^bimforum]: BIMForum, "Level of Development Specification 2024, Part I". https://bimforum.org/wp-content/uploads/2024/11/LOD-Spec-2024-Part-I-official-English.pdf. Accessed 2026-10-20. Cited for the relation between level of information need and LOD.
[^idsfinal]: buildingSMART International, "Information Delivery Specification (IDS) v1.0 is approved as a final standard". https://www.buildingsmart.org/information-delivery-specification-ids-v1-0-is-approved-as-a-final-standard. Accessed 2026-10-20. Cited for the status of version 1.0. The page was not dated in the extract that was read.
[^idstech]: buildingSMART Technical, "Information Delivery Specification IDS". https://technical.buildingsmart.org/projects/information-delivery-specification-ids/. Accessed 2026-10-20. Cited for the description of IDS as the standard to use for level of information needs and as a contract and validation mechanism.
[^ibge]: IBGE, "Sistema Nacional de Pesquisa de Custos e Índices da Construção Civil". https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9270-sistema-nacional-de-pesquisa-de-custos-e-indices-da-construcao-civil.html. Accessed 2026-10-20. Cited for the division of work between IBGE (collection and calculation) and Caixa (engineering definitions and compositions) and for the monthly publication.
[^caixa]: Caixa Econômica Federal, SINAPI. https://www.caixa.gov.br/poder-publico/modernizacao-gestao/sinapi/Paginas/default.aspx. Accessed 2026-10-20. Cited as the publisher of the monthly price reports and the technical notebooks.
[^lei14133]: Lei 14.133/2021, art. 23, in the Senate's legislation database. https://normas.leg.br/?urn=urn%3Alex%3Abr%3Afederal%3Alei%3A2021-04-01%3B14133!art23. Accessed 2026-10-20. Cited for paragraph 2, which orders the reference sources for the estimated value of works and engineering services and puts SINAPI first for works other than transport infrastructure.
[^dec7983]: Decreto 7.983/2013, Planalto. https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/decreto/d7983.htm. Accessed 2026-10-20. Cited for the rule that reference budgets for works paid with federal money use SINAPI. The list of later amendments, including Decreto 12.867 of 2026-03-05, is on https://legislacao.presidencia.gov.br/atos/?tipo=DEC&numero=7983&ano=2013&ato=1c3gXVE5ENVpWT3d6.
[^drywall]: Caixa, "Caderno Técnico de Composições SINAPI: Paredes em Drywall". https://www.caixa.gov.br/Downloads/sinapi-cadernos-tecnicos/SINAPI-CT-PAREDES-EM-DRYWALL.pdf. Accessed 2026-10-20. Cited because it is the closest SINAPI group to a light steel frame wall: compositions for plasterboard walls on a galvanised steel frame.
[^buscador]: Buscador SINAPI, "Caderno Técnico Paredes em drywall". https://buscadorsinapi.com.br/caderno-tecnico/paredes-em-drywall. Accessed 2026-10-20. Cited only for the count of 25 active compositions, which is a third-party transcription of Caixa's document and not an official figure.
[^d11888]: Decreto 11.888/2024, Planalto. http://planalto.gov.br/ccivil_03/_ato2023-2026/2024/decreto/d11888.htm. Accessed 2026-10-20. Cited for the national BIM strategy and the revocation of Decreto 9.983/2019 in its article 14.
[^d10306]: Decreto 10.306/2020, status page of the Presidency's legislation database. https://legislacao.presidencia.gov.br/atos/?tipo=DEC&numero=10306&ano=2020&ato=260MTTU1EMZpWTc7e. Accessed 2026-10-20. Cited for the entry "Não consta revogação expressa". The text is at http://presidencia.gov.br/ccivil_03/_ato2019-2022/2020/decreto/d10306.htm.
[^eutrade]: European Commission, DG Trade, "EU-Mercosur agreement". https://policy.trade.ec.europa.eu/eu-trade-relationships-country-and-region/countries-and-regions/mercosur/eu-mercosur-agreement_en. Accessed 2026-10-20. Cited for the signing date of 2026-01-17 and the start of provisional application on 2026-05-01.
[^eucom]: European Commission, "The EU-Mercosur trade agreement", updated 2026-04-30. https://commission.europa.eu/topics/trade/eu-mercosur-trade-agreement_en. Accessed 2026-10-20. Cited for the statement that the agreement comes into force formally only when the European Parliament has given its consent.
[^europarl]: European Parliament, press release of 2026-02-05. https://www.europarl.europa.eu/news/en/press-room/20260205IPR33618/mercosur-parliament-approves-safeguard-clauses-to-protect-eu-agriculture. Accessed 2026-10-20. Cited for the Parliament's request for an opinion of the Court of Justice.
[^efta]: Siscomex, "Mercosul-EFTA". https://www.gov.br/siscomex/pt-br/acordos-comerciais/mercosul-efta. Accessed 2026-10-20. Cited for the signing date, Decreto 13.126 and the dates of entry into force for Brazil with Iceland and Norway.
[^eeas]: European External Action Service, "Public Procurement in the EU-Mercosur Agreement: Access of EU Companies to the BR Market", 2026-06-19. https://www.eeas.europa.eu/sites/default/files/2026/documents/Public%20Procurement%20in%20the%20EU-Mercosur%20Agreement%20-%20Access%20of%20EU%20Companies%20to%20the%20BR%20Market_0.pdf. Accessed 2026-10-20. Cited for how Brazil's offer treats works and engineering services. The thresholds in reais were not retrieved.
[^ptax]: Banco Central do Brasil, PTAX exchange rate service. https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/. Queried 2026-10-20. Cited for the list of ten currencies and the EUR/BRL closing rate of 2026-10-19. The service is described at https://dadosabertos.bcb.gov.br/pt_BR/dataset/taxas-de-cambio-todos-os-boletins-diarios.
[^strucsoft]: Graitec Strucsoft, "MWF Pro". http://strucsoftsolutions.com/mwf-pro. Accessed 2026-10-20. Cited for what an existing Revit framing product offers: template-based panels, shop drawings, cut lists and machine output for named roll formers. It is the vendor's own description, not an independent review.
[^onyx]: Graitec Strucsoft, "Production management software". https://strucsoftsolutions.com/solutions/production-management-software. Accessed 2026-10-20. Cited for the QR and barcode tracking of individual panels and for production use without a Revit licence. It is the vendor's own description.
[^altoqi]: AltoQi, "Eberick". https://altoqi.com.br/produtos/eberick. Accessed 2026-10-20. Cited as a Brazilian vendor of BIM structural software that exports IFC. It is the vendor's own description.
[^publisher]: Autodesk Platform Services, "Revit publisher guidelines". https://aps.autodesk.com/marketplace/publisher-center/revit-publisher-guidelines. Accessed 2026-10-20. Cited for the requirements on a ribbon button, an add-in manifest and an installer with no manual steps.
[^signing]: Autodesk, "Digitally Signing Your Revit Add-in", Revit API developer's guide. https://help.autodesk.com/cloudhelp/2025/DEU/Revit-API/files/Revit_API_Developers_Guide/Introduction/Add_In_Integration/Revit_API_Revit_API_Developers_Guide_Introduction_Add_In_Integration_Digitally_Signing_Your_Revit_Add_in_html.html. Accessed 2026-10-20. Cited for the security prompt shown for an add-in without a trusted signature.
[^nbr14724]: ABNT, "ABNT NBR 14724:2024, Informação e documentação, Trabalhos acadêmicos, Apresentação", fourth edition, 2024-12-16, as hosted at https://cdn.prod.website-files.com/65b125bdd0407a7ed7dd8897/67c0be30b39362b0975d21f1_NBR%2014724_2024_Trabalhos%20acade%CC%82micos.pdf. Accessed 2026-10-20. Cited for its scope (academic works and similar), its list of supporting standards, and the statement that ABNT technical documents are voluntary. It is a copy on a third-party site, so the purchased text should be checked before anything depends on it.
[^nbr6023]: ABNT, "ABNT NBR 6023:2025, Informação e documentação, Referências, Elaboração", third edition, 2025-05-21, as hosted by a regional electoral court at https://estatico.tre-rn.jus.br/ABNT_NBR_6023_2025.pdf. Accessed 2026-10-20. Cited for the statement that it cancels and replaces the 2018 edition and for the places where a reference may appear. It is a licensed copy shared by a public body, and the text extracted for this note was partly garbled, so only those two points were relied on.
[^nbr10520]: Universidade Federal de Juiz de Fora, "Guia para citação em trabalhos acadêmicos, NBR 10520:2023". https://www2.ufjf.br/turismo/wp-content/uploads/sites/550/2025/02/Guia-para-cita%C3%A7%C3%A3o-em-trabalhos-acad%C3%AAmicos-NBR10520-USP-1.pdf. Accessed 2026-10-20. Cited as a university guide that gives 2023 as the year of the citation standard that goes with the references standard. The standard itself was not read.
[^iso26514]: ISO, "ISO/IEC/IEEE 26514:2022, Systems and software engineering, Design and development of information for users". https://www.iso.org/cms/%20render/live/en/sites/isoorg/contents/data/standard/07/74/77451.html. Accessed 2026-10-20. Cited for its title, its date and the fact that it replaced ISO/IEC 26514:2008. The price on the page is CHF 204.
[^acordo]: Presidência da República, "Decreto nº 6.583, de 29 de setembro de 2008". http://presidencia.gov.br/ccivil_03/_ato2007-2010/2008/decreto/d6583.htm. Accessed 2026-10-20. Cited because it promulgates the 1990 orthographic agreement and sets 2009-01-01 as the start of its effects. The text on this page states a transition that ends on 2012-12-31.
[^acordotrans]: Jusbrasil, transcription of "Decreto nº 6.583, de 29 de setembro de 2008". https://www.jusbrasil.com.br/legislacao/93111/lei-do-acordo-ortografico-decreto-6583-08. Accessed 2026-10-20. Cited for the amended text, which gives a transition ending on 2015-12-31 and marks it as changed by Decreto 7.875 of 2012. It is a third-party transcription, and the official page above shows the earlier wording.
[^cdc]: Jusbrasil, "Art. 31 do Código de Defesa do Consumidor, Lei 8078/90". https://www.jusbrasil.com.br/topicos/10603657/artigo-31-da-lei-n-8078-de-11-de-setembro-de-1990. Accessed 2026-10-20. Cited for the wording of art. 31. It is a third-party transcription of the law.
[^ptbhelp]: Autodesk, Revit 2026 help in Brazilian Portuguese: "Paleta Propriedades", https://help.autodesk.com/view/RVT/2026/PTB/?guid=GUID-A764EA7A-FE26-469B-857C-F3A70812FC34, and "Partes da interface do usuário", https://help.autodesk.com/view/RVT/2026/PTB/?guid=GUID-7793667D-5657-4382-9BEC-F7CB6AC8F53E. Accessed 2026-10-20. Cited as Autodesk's own wording for the Properties palette, instance and type properties, Unconnected Height (Altura desconectada), the ribbon (faixa de opções) and the Project Browser (Navegador de projeto).
