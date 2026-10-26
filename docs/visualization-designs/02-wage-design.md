# Draft 02 — Offered wages versus occupational medians

**Status: PROPOSED / DATA UNAVAILABLE.** See [mockup](02-wage-comparison-proposed.png) and PDF pages 3–4. No matched DOL/BLS dataset, salary marks or wage findings were created.

## Question and planned encoding

For comparable occupations, how would the median offered wage in an eligible H-1B LCA filing sample compare with BLS's published occupational median? A horizontal paired-dot chart would put both measurements on the same annual-USD axis, one row per matched occupation. This allows comparison while keeping the two statistical definitions visible.

The main draft shows an intentionally empty comparison canvas, a disabled filter strip, an explanatory legend and a visible unavailable-data banner. The legend's circle and diamond are categorical symbols, not wage observations. No numeric salary ticks, occupation examples, rank order, sample counts, differences or quantitative positions are invented. This remains a detailed design through its layout, encodings, source contract and interaction specification.

## Proposed data contract — inspect before finalizing

Planned inputs are the DOL FY2025 Q4 LCA disclosure and its record layout, plus BLS occupational wage estimates with documented SOC edition, geography, units and reference period. These are intended sources, not records already analyzed. The BLS vintage and final occupation scope remain undecided until source inspection. Consult the existing [data guide](../../data/README.md) for availability.

| Field needed in a future occupation-level output | Use / constraint |
| --- | --- |
| SOC code, SOC version, source occupation labels | Establish compatible occupation definitions. Do not silently mix editions or join by approximate title. |
| DOL observation period, BLS reference period, geography | Explicit labels and comparability checks. A fiscal filing period and a BLS point-in-time estimate are not automatically equivalent. |
| DOL filing-level median offered annual wage | Proposed equal-case median after a documented eligible H-1B certified-filing selection and revision/case-ID audit. It is not an estimate of actual pay or a worker-weighted median. |
| BLS annual occupational median | Published estimate for the matched occupation and geography; do not replace a median with a mean. Preserve suppression or unavailability. |
| Included DOL cases and exclusion counts/reasons | Expose selection, missingness, range wages, unit exclusions and duplicate/revision treatment. |
| Match status, limitations and source references | Prevent unsupported comparisons from entering the plot; retain source file and record provenance. |

Proposed primary sample: directly reported annual, single-valued offered wages. Investigate how equal lower/upper bounds, missing upper bounds and source markers are defined before coding that rule. Do not use guessed range midpoints or invented hours-per-year to annualize hourly wages. Document and count excluded ranges and nonannual units; consider separate sensitivity views only if defensible. DOL requested-worker counts do not silently become statistical weights.

A national BLS comparison requires an eligible national DOL aggregation with comparable scope. Selecting a state or local area is enabled only if both sides support that geography. Document period differences and either justify the descriptive comparison or withhold it. Profile sample sizes and predeclare an adequate-sample rule before interpreting wage differences; no threshold is asserted without inspection.

## Planned chart and interactions

| Element / action | Proposed behavior after validation |
| --- | --- |
| Row and Y ordering | One valid occupation, full SOC label; alphabetical by default. Optional signed-difference sorting only once comparable real values exist. |
| X axis | Shared linear annual-USD scale with explicit units and readable numeric ticks derived from data. A zero-based overview is the starting design; any future zoom must visibly label its domain. |
| Two marks | Green circle: DOL eligible-filing median offered annual wage. Terra diamond: BLS published annual occupational median. Shapes and adjacent text distinguish them without color. |
| Connector | Thin neutral line only when both estimates are available and comparable. It denotes a descriptive separation; it does not establish a wage premium, underpayment or causation. |
| Hover / focus | Show both definitions, actual values, source periods, geography and SOC. Missing values remain text statuses. |
| Click / Enter / tap | Pin an occupation evidence panel with included cases, exclusions, wage-basis treatment, BLS estimate and provenance. Escape clears selection. |
| Filters | Occupation search plus only supported period/geography combinations. Show resulting sample/coverage changes; do not present an unsupported geography as selectable. |
| Absent or suppressed side | Display an explicit unavailable-status row. No zero substitution, connector or computed difference. No-data search offers Reset. |

On mobile, stack labeled values and their evidence panel beneath the selected occupation; keep the two definitions and year labels visible. Supply an accessible data table, keyboard equivalents, visible focus and selection announcements. Controls in this draft stay disabled while the source gate is closed.

## Interpretation and release gate

An offered wage in a filing is not observed earnings. The two medians have different sampling, weighting, coverage and time definitions. A comparison cannot isolate skill, location, experience, hours, employer selection or other causes. The narrative asks a question rather than promising a conclusion.

Future implementation requires acquisition and provenance, schema review, SOC/geographic/period alignment, a documented wage-range rule, missingness and sample-size checks, independently verified medians and visible definitions. Incompatible rows stay disabled. This draft supports requirement 4 while truthfully leaving the complete-data-pipeline requirement unresolved.
