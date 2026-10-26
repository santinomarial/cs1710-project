# Prototype V1 website implementation and visual verification

Verified October 25, 2026. This phase follows the three approved mockups in `docs/visualization-designs/`. It improves the local React/Vite website and implements two designs without changing the validated data pipeline. No deployment, commit or push was performed.

## Result

The website now has four functional D3 visualizations. The original OPT trend and H-1B employer distribution retain their component code and calculations. New industry bars and the employer scatterplot use D3 CSV parsing and scales with React rendering and interaction state. The ICE employer section now displays real source records; the wage section remains an explicitly unavailable-data proposal.

The shared visual system uses the approved cream, forest-green, sage and terracotta palette; Georgia headlines; readable sans-serif labels; white chart/evidence cards; consistent controls; persistent annotations; and a chapter navigation strip. Wide screens place charts and evidence side by side. Phones place industry names above their bars and stack detail panels below charts.

The story sequence is: main sponsorship question → academic-year OPT growth → calendar-2024 OPT employers → FY2025 employer breadth → FY2025 industries → cross-period employer comparison → proposed wages → policy implications → source methods. Calendar, academic and fiscal periods remain explicit.

## Data bindings

| Live view | Processed input | Verified behavior and meaning |
| --- | --- | --- |
| OPT line | `opt_growth.csv` | Original 20-year default and full 46-year OPT history; final source value 294,253 in 2024/25; source note and reporting caveat retained. Enrollment totals in narrative remain from the same validated Open Doors inputs. |
| H-1B distribution | `uscis_fy2025_distribution.csv` | Original seven disjoint bins, 29,350 named positive-approval groups, 114,798 approvals, fixed 0–100% scales and six unnamed approvals excluded from this chart. All exclusions and identity notes retained. |
| Industry ranking | `uscis_fy2025_industries.csv` | 20 sectors plus 2,215 approvals with missing industry. National denominator stays 114,804, including during search. Initial = new + concurrent. These are petition approvals, not unique workers. |
| Employer comparison | `opt_h1b_employer_overlap.csv`; coverage from `opt_h1b_match_audit.csv` | 47 accepted name pairs; source combined participation stays independent from OPT and STEM columns. No conversion rates or person-level transitions. Shapes are derived from preserved strings: 15 verbatim, 28 case/spacing only, 4 formatting-normalized. All passed the same existing conservative acceptance rule. |
| ICE employer overview/table | `opt_employers.csv` | Six leading source rows plus searchable full 200-row table. All 11 missing STEM cells display as “Not reported”; the clipped source-name note is retained. Apple source control is 1,621 combined, 1,135 OPT and 973 STEM. |
| Wage proposal | None | No salary records, wage scale, numeric ticks or comparison findings. Legend symbols describe the planned encoding only. DOL/BLS acquisition and defensible matching remain future work. |

CSV imports use Vite's raw-file support and D3 parsing; downloads resolve to those same pipeline files. There are no synthetic chart records or duplicate public data copies. `src/chartData.js` validates periods, accepted-match status, nonnegative integer counts and initial-approval components. These checks do not alter pipeline calculations.

## Checks run

| Check | Result |
| --- | --- |
| Python: `python3 -m unittest discover -s tests -v` in the bundled environment with required libraries | **28 passed**. Includes original PDF cells, raw USCIS sums, matching ambiguities, missingness and deterministic output reproduction. |
| Frontend: `npm run test:charts` | **15 passed**: original seven distribution tests plus eight new source/filter/missingness tests. The command now discovers every `tests/*.test.js` file. |
| Production: `npm run build` | **Passed**, 622 modules transformed. Non-failing Vite advisory: main JS is approximately 614 kB uncompressed / 132 kB gzip. No new runtime dependencies added; code splitting is deferred for this prototype. |
| Production HTTP | `http://127.0.0.1:4173/` returned **200**. Built app showed 20 default OPT points, seven distribution bins, 10 initial industry bars and all 47 comparison points. Count/share and four-name filtering also checked in the built app. Temporary preview server stopped after verification; existing dev server retained. |
| Browser logs | No captured warning/error entries during reviewed browser checks. The build advisory above is separate from browser runtime logs. |
| Responsive sizes | 1440 × 1000 desktop, 390 × 844 phone; additional 320 × 800 phone and 768 × 1024 tablet overflow checks. Document width equaled viewport at all four sizes. Scrollable tables and the chapter navigation contain their own overflow. |
| Preservation | SHA-256 baseline for **37 files**: all raw/processed data, pipeline source, original OPT/distribution component files and distribution calculation module remained byte-identical. Python cache files excluded. |

## Interaction verification

- **Industry:** approval/share switching; Education 15,966 / 13.9%; Manufacturing selection and 11,496 components; search for NAICS 92 beyond the initial top ten; empty search/reset; all 20 sectors; alphabetical sort retaining selected NAICS; keyboard focus tooltip with full name, exact count, period and units; pointer/tap selection; mobile labels above bars. The missing-industry card and denominator remain visible.
- **Comparison:** 47 default points; unchecking verbatim and case/spacing leaves four formatting-normalized points with unchanged axes. Selecting Bain displays both original names, 346 combined participation, 33 approvals and source references. Filtering out the selected employer clears its detail panel.
- **Missingness:** STEM mode shows 46 plotted pairs and the explicit Carnegie Mellon missing-value notice. The employer remains selectable and its evidence panel reports “Not reported” without placing a point at zero. This was also checked on the phone layout.
- **Search/keyboard:** “Harvard” yields one point; “Amazon” yields an honest empty state, not an inferred zero. Enter pins, Escape clears, and keyboard focus displays the same tooltip values used by hover. The source-name selector and value table provide access to closely spaced/overlapping points without jitter or brush zoom.
- **Preserved views:** full OPT history still contains 46 table rows and its latest source value; range switching/table controls work. H-1B approval-share mode and the 501+ group still show 12 groups / 12,510 approvals / 10.9% of approval volume, with seven source-table rows.
- **Sources:** the ICE source card now recognizes the preserved supplied PDF instead of its historical failed-download alias. The wage area visibly states that matched data are unavailable. Source links and caveats were inspected in rendered content.

These are functional checks and visual reviews, not a formal usability study or exhaustive accessibility certification. No brush zoom was added: the prototype uses fixed zero-based overview scales, search, shape filters, a native selector and a table. This keeps the requested interactions simple and makes every accepted name inspectable even in dense clusters.

## Screenshots

Images are direct browser captures, not recreated mockups. Desktop captures use the production build. Phone captures show the same source implementation in the Vite preview. Full section captures include nearby explanation and source context; the smaller phone chart image shows the viewport at normal reading size.

| View | Screenshot |
| --- | --- |
| Desktop introduction | [desktop-home.jpg](screenshots/prototype-v1-polish/desktop-home.jpg) |
| Desktop industry | [desktop-industry.jpg](screenshots/prototype-v1-polish/desktop-industry.jpg) |
| Desktop novel comparison | [desktop-comparison.jpg](screenshots/prototype-v1-polish/desktop-comparison.jpg) |
| Four-name filter state | [desktop-comparison-filtered.jpg](screenshots/prototype-v1-polish/desktop-comparison-filtered.jpg) |
| Desktop wage proposal | [desktop-wage-proposal.jpg](screenshots/prototype-v1-polish/desktop-wage-proposal.jpg) |
| Desktop original OPT view | [desktop-opt-growth.jpg](screenshots/prototype-v1-polish/desktop-opt-growth.jpg) |
| Mobile introduction | [mobile-home.jpg](screenshots/prototype-v1-polish/mobile-home.jpg) |
| Mobile industry | [mobile-industry.jpg](screenshots/prototype-v1-polish/mobile-industry.jpg) |
| Mobile novel comparison | [mobile-comparison.jpg](screenshots/prototype-v1-polish/mobile-comparison.jpg) |
| Mobile scatterplot viewport | [mobile-comparison-chart.jpg](screenshots/prototype-v1-polish/mobile-comparison-chart.jpg) |
| Mobile original sponsorship view | [mobile-sponsorship.jpg](screenshots/prototype-v1-polish/mobile-sponsorship.jpg) |
| Mobile wage proposal | [mobile-wage-proposal.jpg](screenshots/prototype-v1-polish/mobile-wage-proposal.jpg) |

## Remaining Prototype V1 work

The [exact-rubric tracker](prototype-v1.md) remains the submission checklist. Active contributor names, previous milestones, the assembled/verified process-book PDF and submission ZIP are still outstanding. Two formerly unimplemented drafts are now live; only the wage proposal remains unimplemented. Under the literal requirement for 2–3 unimplemented designs, at least one additional unimplemented design is needed unless the course accepts the earlier design-milestone artifacts. No new draft is invented solely to mark the checkbox complete.

Matched DOL/BLS data remain unavailable, as does the planned ICE annual summary. The implemented views use validated real data; unavailable proposed analyses remain withheld. The two-approval NFAP discrepancy, partial-ID/name-only identity limitations and unconfirmed ICE retrieval date remain documented in the data reports.
