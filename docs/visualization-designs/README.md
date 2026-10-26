# Prototype V1 visualization designs

Updated October 25, 2026 (America/New_York). **Three designs are currently proposed and unimplemented: wages, geography, and fields of study.** The industry and novel employer comparison have been implemented on the website; their original drafts remain design-history artifacts and are not counted toward the additional-unimplemented-design requirement. No website code was changed to create drafts 04 and 05.

## Process-book assets and implementation status

| Design | Current status | Image and specification |
| --- | --- | --- |
| 01. H-1B industry ranking | **Implemented** | [Industry mockup](01-industry-ranked-bars.png); [original specification](01-industry-design.md) |
| 02. Offered wages versus occupational medians | **Proposed / unimplemented; matched data unavailable** | [Wage mockup](02-wage-comparison-proposed.png); [detailed specification](02-wage-design.md) |
| 03. Novel employer comparison | **Implemented** | [Employer comparison mockup](03-employer-comparison-novel.png); [original specification](03-novel-employer-design.md) |
| 04. Geographic distribution of H-1B sponsorship | **Proposed / unimplemented; source-backed draft** | [04-h1b-geographic-map.png](04-h1b-geographic-map.png); specification below |
| 05. International students by field of study | **Proposed / unimplemented; source-backed draft** | [05-fields-of-study-stacked-area.png](05-fields-of-study-stacked-area.png); specification below |

New PNGs are **3240 × 2700 pixels**, exported at 216 dpi from vector layouts. Use a full landscape page for each; avoid squeezing source notes into a small illustration. The existing 01–03 PNGs remain 2400 × 1689. The [original six-page PDF insert](prototype-v1-design-drafts.pdf) contains **only designs 01–03**, including their rationale/interaction pages; it has not been rewritten to imply that 04–05 are inside it. For the current process book, include wage pages 3–4 plus the two new PNGs and their specifications, retaining earlier implemented-design history separately.

All control states in these PNGs are illustrations of intended behavior. They are not functional interfaces or evidence of usability testing. The cream background, forest-green typography and cards, serif headlines, terracotta selection accents, restrained borders and generous spacing follow `src/story.css` and the approved drafts. Read the [current website verification](../website-polish-verification.md) for live behavior.

## 04 — Geographic distribution of H-1B sponsorship

### Purpose, audience and insight

Help students, general readers and policy audiences understand where H-1B petitions are registered, complementing the existing question about whether sponsorship is confined to major technology companies. The employer distribution shows breadth across employer names; the industry chart shows sectors; this view adds the geographic dimension without treating location as another employer classification.

The pictured selected state is California: **21,552 initial approvals**, **18.8%** of the export-wide national total. A separate Texas hover preview shows **12,618**, **11.0%**. These describe concentration of filings, not local employment rates, residency, labor shortages or where beneficiaries actually work. The proposed position in the story is after industries and before employer comparison/policy discussion.

### Sources, period and aggregation

- Counts: [USCIS H-1B Employer Data Hub](https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub), the supplied FY2025 export, read through `data/processed/uscis_fy2025_records.csv`. FY2025 is **October 1, 2024–September 30, 2025**.
- One input row is one source record. Group its `initial_approvals` by the literal `petitioner_state`; initial is exactly `new_employment_approvals + new_concurrent_approvals`. Do not aggregate the already-grouped employer table across locations, deduplicate employers, add continuing categories, add denials or count one row once per category.
- All **62,415 distinct record IDs**, with source lines 1–62,415, contribute once. All rows, including unnamed employers and zero-initial-approval records, remain in the aggregation. Independently summing the unchanged UTF-16/tab-separated original reproduces every state/component/row-count group.
- Geometry: [U.S. Census Bureau 2024 cartographic boundaries](https://www.census.gov/geographies/mapping-files/2024/geo/carto-boundary-file.html), state and equivalent entities, **1:20,000,000 KML**. The [original geometry archive](assets/cb_2024_us_state_20m.zip) and [URL, retrieval timestamp and SHA-256](assets/cb_2024_us_state_20m.provenance.json) are documentation assets only. No source data or pipeline files were changed.
- Original polygon coordinates are projected with spherical Albers equal-area parameters (lower 48: central meridian −96°, standard parallels 29.5°/45.5°). Alaska and Hawaii use separate Albers projections and are independently scaled/repositioned in explicitly labeled insets. Labels and the DC callout derive from polygon centroids; no employer geocoding or invented coordinates are used. Boundary vintage is separate from the FY2025 approval period.

| Geographic coverage | Initial approvals | Treatment |
| --- | ---: | --- |
| 50 states + District of Columbia | 114,396 | Map fill; searchable selector and table |
| Guam | 312 | Separate territory row |
| Puerto Rico | 31 | Separate territory row |
| Northern Mariana Islands | 28 | Separate territory row |
| U.S. Virgin Islands | 14 | Separate territory row |
| American Samoa | 0 | Explicit source-backed zero, not a missing-value replacement |
| Blank petitioner state | 22 | Unlocated row; 49 source records |
| Literal code `XX` | 1 | Unmapped-code row; 4 source records |
| Literal code `AA` | 0 | Unmapped-code row; 1 source record |
| **All records / share denominator** | **114,804** | **113,458 new + 1,346 new concurrent** |

Territories total 385; blank/unmapped codes total 23. The **408 outside-map approvals are visible in the mockup**, not silently dropped. No geographic meaning is invented for `XX` or `AA`. The geometry archive contains Puerto Rico, but this design consistently places all territories in the accompanying table instead of mapping one territory and omitting the others.

### Encodings and proposed interactions

- **Fill:** continuous sequential pale-to-forest green, linear approval counts from 0 to the maximum state count, 21,552. The midpoint tick 10,776 is a scale reference, not another observed state. Higher counts are darker. A terracotta outline denotes selection without replacing the count-encoded fill.
- **Tooltip:** full state/location name, FY2025, initial approvals and share of **all 114,804** approvals, rounded to one decimal percent. Hover or keyboard focus previews; clicking/Enter pins a detail panel, while a different hover can preview another state. Leaving hover restores the selection; Escape clears it.
- **Detail:** state label, initial count, national share, new employment and new concurrent components, reporting period and source. California shows **21,350 + 202 = 21,552**. The selected state survives searching; searching does not recompute the scale or denominator.
- **Access:** a searchable state/territory selector and equivalent table reach small polygons, DC and unmapped rows. Proposed keyboard arrows navigate options, Enter selects, and an announced detail region reports changes. Touch selects directly without requiring hover. Missing location is a text status, never a guessed point; a future missing numeric count receives an explicit unavailable status rather than the zero color.
- **Mobile:** retain a full-width map with tap targets supported by the selector; put the detail panel immediately below it. Keep the color legend, outside-map count and location caveat visible. The accessible table is also the exact-value alternative for similar pale fills.

### Rationale and limitations

The geographic overview answers a different question from the existing ranked bars. A continuous linear scale preserves the meaning of count differences; no population denominator is available or assumed. Large states occupy more visual space, and skewed counts make smaller values difficult to distinguish, so exact values and the table are essential. No inference should be made from a state's physical size.

Petitions are **not unique workers**. New concurrent employment can concern someone already holding H-1B status. Petitioner addresses may represent headquarters or filing locations rather than actual employee worksites. A map cannot resolve employer identities, ownership or remote work. Zero is not missing; a missing address is not evidence of no sponsorship. The existing **two-approval difference from NFAP remains unresolved**; the map uses the supplied USCIS export and does not force its 114,804 total to match NFAP's 114,806.

## 05 — International students by field of study

### Purpose, audience and insight

Give students, educators and policy readers context about how the composition of international study has changed alongside participation growth. The existing OPT trend answers “how much?”; this design asks “across which academic fields?” It belongs alongside OPT growth, before employer-level comparisons. It does not connect fields to employers, petitions or individual visa transitions.

The selected 2024/25 example is **Math and Computer Science: 305,377 students**, **25.9%** of the **1,177,766 summed field counts**. Those figures describe the current mix, not a causal explanation for H-1B sponsorship. The title and subtitle avoid claiming that everyone counted is currently enrolled: Open Doors field data include OPT participants from 2008/09 onward.

### Sources, periods and coverage

- [IIE Open Doors, Fields of Study](https://opendoorsdata.org/data/international-students/fields-of-study/), 2025 edition; existing `data/processed/fields_of_study.csv`, original `data/raw/open_doors_fields.xlsx`, and preserved notes in `data/processed/source_notes.json`.
- **27 academic years, 1998/99–2024/25; 15 broad categories; 405 distinct field-year records.** Academic years are not calendar years or federal fiscal years. The 2025 edition date is not an extra observation year.
- The pipeline selected broad parent categories only. The design does not add detailed subcategories or the published total again. All 405 student counts were independently checked against the workbook cells identified by `source_row` and `source_column`.
- There are **no missing student-count cells** in the current broad-category extract and every field has one row per year. No values were interpolated, extrapolated or filled. The source's classification and population caveats still apply even when all cells contain numbers.

### Encodings and proposed interactions

- **X:** academic year, with equal spacing for adjacent observed years. **Y in count mode:** summed reported student counts on a common zero baseline, labeled 0–1.2 million. Each layer's vertical thickness is one field's observed count; the top is the sum of the 15 fields, not an independently substituted national-enrollment series.
- **Color:** a fixed 15-color categorical palette extending the website's forest, sage, blue, terracotta and neutral colors. Fixed stack order begins with Math and Computer Science, Engineering and Business and Management. Keep order stable across time and mode switches. The full legend is included; abbreviated display labels expand to exact source labels on focus/selection.
- **Composition switch:** use `100 × field students / sum(all 15 reported fields that academic year)` and a 0–100% axis. Counts remain in the tooltip. Do not divide by a possibly different published national total or by a filtered subset. The original published totals may differ from historical category sums, so the denominator is named visibly.
- **Legend and field selector:** focus/highlight a field with a boundary outline and deemphasize the rest, while retaining the full stack. The pictured Math/CS boundary is outlined in terracotta. “Reset all fields” restores the overview. A focused field is not moved to the baseline, removed from the total or silently restacked. This is focus filtering, not subset recomposition.
- **Hover:** snap to an actual year/field observation, never an interpolated value between observations. Tooltip shows academic year, full field label, integer student count and composition share. The pictured tooltip is **2024/25, Math and Computer Science, 305,377, 25.9%**. Click/Enter pins that field-year detail; arrow keys in a year selector support precise time navigation. The proposed detail panel announces updates.
- **Accessibility/mobile:** keep all 15 legend options available as labeled buttons, with keyboard focus and pressed state. Color is not the only cue: selection outline, names and exact values accompany it. On phones, stack detail below the chart, use a collapsible field selector and fewer visible year ticks without dropping observations. Offer an accessible year-by-field data table, especially for thin layers.

### Reporting changes, missingness and comparability

Two visible discontinuities **withhold connections across reporting breaks**, rather than implying smooth comparable growth: between 2007/08 and 2008/09, and between 2019/20 and 2020/21. Every year's values remain plotted. The gaps are explicitly labeled as reporting changes, not absent observations. Straight boundaries connect adjacent observed annual values only within each regime; hovering never manufactures intermediate student counts.

- **OPT coverage:** field-of-study data for OPT students were first reported in 2008/09; OPT was previously reported as a separate category. Thus the earlier broad-field totals do not represent the same coverage as later years. Do not interpret the jump as only a change in enrollment.
- **Classification:** the entire historical extract uses **Open Doors 2025 broad classifications**, which may not match historical publications. Starting with Open Doors 2021 (2020/21), CIP 2020 replaces CIP 2010. Professional Residency/Fellowship categories changed and figures from 2020/21 onward are not entirely comparable. Additional source notes describe earlier category renamings/new detailed categories in 2003/04–2004/05, 2010/11 and 2012/13; do not treat detailed-category histories as stable merely because broad fields are complete.
- **Missingness rule for future inputs:** an absent or blank field-year remains missing, never zero. If any component is unavailable, show a gap for the whole annual stack and withhold that year's full-composition percentages; the table can still show known values with an incomplete-total label. Do not bridge a missing year, carry values forward, add residual “Other” values or estimate shares.
- **Comparisons:** middle layers have moving baselines, so the area chart emphasizes the overall mix; exact field trends require focus/details and a table. Fifteen colors have practical distinguishability limits, especially for thin layers. Classification changes, coverage and aggregation prevent reading these marks as verified individual pathways, causal policy effects or future labor demand.

## Existing design evidence

The original [design-data-audit.json](design-data-audit.json) documents industry and employer-comparison input hashes and values. Industry totals reconcile to 114,804, including 2,215 missing-industry approvals. The employer mockup uses 47 accepted name comparisons, comprising 15 verbatim, 28 case/spacing-only and 4 formatting-normalized pairs; these are not verified legal-entity identities. The unchanged wage proposal contains **no invented salaries, numeric wage ticks, positioned salary observations or wage differences**. Its data gate remains closed until matched DOL/BLS inputs validate.

## Reproduction and verification

Run from the project root with Python, ReportLab, openpyxl and Poppler's `pdftoppm` installed:

```sh
python3 docs/visualization-designs/render_additional_drafts.py
```

The new renderer reads existing inputs and the archived Census geometry, validates aggregates and workbook cells, and exports only the two new PNGs plus [additional-design-data-audit.json](additional-design-data-audit.json) under this documentation directory. Its two-page vector intermediate is under `tmp/pdfs/`; it is not the updated process book. Rendering is offline once the geometry archive exists. No pipeline or frontend dependency is added. To reproduce only the earlier three drafts, use the separate, unchanged `render_drafts.py`.

The new audit includes input SHA-256 hashes, all state/component totals, the denominator and all 405 plotted field values, reporting breaks, geometry provenance and output hashes. The [verification record](additional-design-verification.md) records numeric checks, image dimensions, visual inspection and preservation of application/data/pipeline files. Proposed controls have been specified, not implemented or behavior-tested.

## Course requirement mapping

- **Requirement 4:** exactly **three currently unimplemented designs are ready**: wage comparison (02), geographic distribution (04), and fields of study (05). They have visual artifacts, rationale, data mappings, proposed interactions and limitations. **Incorporation into the actual process book is pending**, so the full requirement is not marked complete.
- **Requirement 7:** the novel employer comparison's first design is already complete and the linked view is implemented. The new designs are additions, not a replacement for that evidence.
- **Requirement 8:** these assets support new prototype documentation. The active-contributor roster, all previous milestones and the assembled, verified PDF process book remain outstanding, as does the single submission ZIP. These mockups do not finish unavailable-data acquisition or submission packaging.

Team review should check whether readers distinguish petitioner locations from worksites, understand why field-year percentages use category sums, and notice both reporting breaks before comparing periods. Record actual critique in the process book; no review outcomes are invented here.
