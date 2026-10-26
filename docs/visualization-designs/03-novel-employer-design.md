# Draft 03 — Two datasets. One employer lens.

**Status:** first novel-view design, with real static coordinates and proposed interactions. See [mockup](03-employer-comparison-novel.png) and PDF pages 5–6. No additional website visualization was implemented.

## Purpose and project-specific novelty

Compare the scale of reported OPT/STEM OPT participation and initial H-1B approvals for the **47 accepted employer-name pairs**, while making the evidence and limits of each comparison inspectable. The design combines a linked scatterplot, a persistent employer evidence panel, name-format filters and a reporting-period strip. Selecting a point connects its values to the original names, source locations and period overlap.

The contribution is this coordinated treatment of comparison and provenance in the project's narrative. A linked scatterplot is an established technique, not a newly invented chart form. The design intentionally supports the question “What do these two employer-level records say?” without translating their vertical/horizontal position into a person-level flow.

## Visible reading rules

Keep this explanation immediately above the chart, including on small screens:

> Different populations and periods. ICE: calendar-2024 OPT/STEM OPT participation. USCIS: FY2025 initial petition approvals. These are not individual transitions, conversion rates, or verified legal-entity matches.

The period strip places January–December 2024 and October 2024–September 2025 on a shared monthly timeline, highlighting their October–December 2024 overlap. It uses no directional flow arrows. The cohorts are not sequential. The 47-name subset comes from ICE's published top-200 list and is not representative of all employers. Excluded or unmatched names do not imply an absence of H-1B sponsorship.

## Data and axes

Read `data/processed/opt_h1b_employer_overlap.csv` (47 accepted rows) and use `opt_h1b_match_audit.csv` (200 decisions) for coverage and exclusions. The [ICE extraction and matching report](../ice-2024-employers.md) defines the existing acceptance rule. This design does not re-run matching, introduce aliases, merge subsidiaries or sum alternate USCIS groups.

| Element | Exact meaning |
| --- | --- |
| One point | One accepted ICE employer name paired with its selected USCIS employer group. It is not a student, worker, petition or verified corporate identity. |
| X, default | `total_opt_or_stem_opt_participants`: the source's CY2024 combined count, preserved independently. Initial linear domain 0–2,000. |
| X, optional | `opt_participants` or `stem_opt_participants`, explicitly relabeling the axis and period. Proposed overview domains: OPT 0–2,000; STEM OPT 0–500. Announce the metric/domain change. |
| Y | `h1b_initial_approvals` for FY2025, equal to `h1b_new_employment_approvals + h1b_new_concurrent_approvals`. Initial linear domain 0–300. Continuing categories excluded. These are petition approvals, not unique workers. |
| Size | Constant; neither count is redundantly encoded by area. |
| Shape and color | Name-format category, defined below. No confidence gradient. |
| Selection | Outline ring, label and dashed guides to the axes; the underlying match shape remains visible. |
| Detail | Original names, all three ICE source columns separately, new/concurrent/initial counts separately, periods, match reason, USCIS group/suffix, ICE page/row and USCIS line references. |

Combined participation is **not OPT + STEM OPT**. Counts cannot be summed across employer rows into a national unique-student population. The source's multiple-program counting caveat belongs beside the figures and in expanded source detail. Missing cells remain missing.

Harvard is selected in the mockup: ICE **1,036 combined**, **799 OPT**, **407 STEM OPT**; USCIS **112 initial = 110 new + 2 concurrent**. The preserved names are `Harvard University` and `HARVARD UNIVERSITY`, with suffix `3580`, ICE page 1/table row 19 and USCIS line 24394. These are source values, not a calculated transition relationship.

## Exact names versus other accepted matches

The matching report already preserves both source strings and applies one conservative full-name rule. It does **not** assign exact/fuzzy confidence tiers. The draft derives three mutually exclusive display categories from those preserved strings, applied only to the 47 previously accepted rows:

1. **Verbatim exact — 15:** original extracted name strings are equal. Solid green circle. “Verbatim” refers to the preserved processed strings; extraction already normalized PDF line wrapping.
2. **Case/spacing only — 28:** strings are unequal but their uppercase, whitespace-collapsed forms are equal. Hollow blue circle. Harvard is an example.
3. **Formatting-normalized — 4:** the remaining already-accepted names require punctuation or ampersand normalization under the documented rule. Terra diamond.

The four formatting cases are:

| ICE name | Preserved USCIS name |
| --- | --- |
| BEACONFIRE SOLUTION INC. | BEACONFIRE SOLUTION INC |
| Antra, Inc | ANTRA INC |
| Washington University in St. Louis | WASHINGTON UNIVERSITY IN ST LOUIS |
| Bain & Company, Inc. | BAIN AND COMPANY INC |

PDF page 6 shows these four points at their true coordinates with the same overview domains. Categories describe the string differences, not identity confidence or match reliability. Even a verbatim name is not legal-entity verification. The USCIS tax suffix is partial and ICE has no shared tax ID/address crosswalk.

## Interaction contract

| Action / state | Behavior |
| --- | --- |
| Hover or keyboard focus | Preview employer name, X/Y values with units and periods, name-format type and the scope caveat. Hover does not overwrite a pinned panel. Focus has the same information and visible outline. |
| Click, tap or Enter | Pin a point and populate the evidence panel. Selection uses the accepted pair's stable source/group key, not screen coordinates. Escape/Clear removes the pin. |
| Dense cluster | Brush to zoom; keep a domain label and Reset zoom visible. The zero-based overview returns on reset. Zoom can exclude zero and must say so; it changes viewport only, never values. Provide numeric range inputs and a sortable employer list as keyboard alternatives. No jitter or displacement of data coordinates. |
| Overlapping points | List all candidates in the hit area and let the reader select a named row; never silently pick whichever point was drawn last. |
| Search | Search either preserved name within the 47 accepted pairs. Show match count and Reset for no results. It does not search excluded candidates as established matches. |
| Match-format controls | Independent labeled checkbox-style filters for the three shapes; default all on. Show “visible / 47 accepted” plus 153 excluded from the original join. Filter counts are display coverage, not acceptance changes. |
| Change X metric | Relabel units, update the declared overview domain and reset zoom. Preserve selected employer if plottable. For missing X, show its evidence panel and an “unplottable for this metric” notice with no point. |
| Missing STEM | Carnegie Mellon University has no STEM value. With all name filters on, STEM mode shows **46 plotted, 1 missing**. Its row remains in the missing-data list; never put it at zero. |
| Filter hides a pinned employer | Clear the selection with an announcement explaining why; do not leave an apparently linked panel for an invisible point. |
| Inspect evidence | Expand both original source names, the existing acceptance reason, source URLs/files, USCIS group and suffix, ICE page/row and USCIS source lines. Link to the full matching audit. |
| Inspect exclusions | Separate coverage drawer: 14 ambiguous full-name cases, 97 unresolved variants, 41 without conservative candidates, 1 clipped name. Excluded candidates are never drawn as accepted points. |

Do not compute `H-1B / OPT` or label quadrants as conversion success/failure. No equality diagonal, fitted trend line, confidence score, flow arrows, causal labels or “students retained” annotation is proposed. The two axes have different measurement units despite both using counts.

## Responsive layout and accessibility

Wide view: plot at left, evidence panel at right, period strip below. Narrow view: population warning first, wrapped controls, plot, then selected detail. A sticky selection summary may be used only if it leaves adequate plot area and does not cover axis labels. Give touch targets at least 44 CSS px, visible keyboard focus, native filter controls, a chart description and an announced selected-name/status region. A source-value table must offer every action needed to inspect a point without hover or brushing. Use shape and text in addition to color.

## Verification and future evaluation

The draft generator reads all 47 coordinates directly, checks acceptance status and 15/28/4 category counts, and records input hashes and pictured values in `design-data-audit.json`. Overview maxima fit the labeled axes. The selected Harvard figures and four filtered values were checked against the source CSV; Carnegie Mellon's missing cell is preserved.

Before implementing: test selection restoration, overlapping-point choice, search, filter-hidden selection, STEM missingness, metric/domain announcements, reset zoom and equivalent table/keyboard actions. Ask readers to explain the two periods and why a point cannot reveal individual transitions; record their answers before claiming the warning is effective. The mockup has been visually checked, but interaction usability has not been tested.

This supplies the first novel-view design for requirement 7 and a third additional design for requirement 4. The full process-book incorporation remains pending.
