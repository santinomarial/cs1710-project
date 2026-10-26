# Processed-data audit — Prototype V1

**FY2025 update:** the eight CSVs audited below remain byte-identical. Five new primary USCIS datasets now supply the employer chart. See [the reconciliation and full new schemas](uscis-fy2025-reconciliation.md). Earlier statements below about absent USCIS records describe the pre-import audit.

Inspected October 25, 2026 (America/New_York). This report reads all eight actual CSVs, source manifest, preserved source notes, data guide, extraction code, and visualization code. Counts exclude headers. Original downloads occurred October 25 local time (October 26 UTC).

## Sufficiency decision before implementation

An exact national employer histogram is **not supported**. The 100-employer appendix omits employers with fewer than 100 initial approvals. The three summary records cannot reconstruct those observations. Missing: complete FY2025 USCIS employer records, stable identity/location grain, initial approvals separately from continuing approvals, and reliable employer industry codes if a technology-versus-other comparison is desired.

The supported second visualization is an explicitly limited **reported-threshold employer distribution**: independent horizontal bars for the published shares with exactly one initial approval and with one through ten. It does not invent bins, interpolate a CDF, infer omitted employer counts, or imply unique workers. The national employer total is contextual only. No formal technology/nontechnology classification is available.

## File-by-file inspection

### academic_levels.csv

- **Rows:** 194.
- **Reporting period:** 1954/55–2024/25; 51 distinct academic years.

- **Columns:** `academic_year`, `academic_level`, `students`, `source_file`, `source_sheet`, `source_row`, `source_url`.

- **Original source:** IIE Open Doors 2025, Broad Academic Levels worksheet.

- **Original file:** [open_doors_academic_level.xlsx](https://opendoorsdata.org/wp-content/uploads/2025/11/Census_Academic-Level_OD25_Website.xlsx); local `data/raw/open_doors_academic_level.xlsx`. Original SHA-256 verified against manifest.

- **Limitations:** 51 selected academic years; missing categories are omitted, not zero. Pre-1979 OPT/non-degree were combined. The 1994/95 OPT count is 13,209 versus 13,208 in enrollment.

- **Website use:** Supporting data; not currently plotted.

- **Processed SHA-256:** `f8df875fe005918de62cdfeacbf04a632f8ad4b12cb8bf2f051e34bbc9904991`.

### fields_of_study.csv

- **Rows:** 405.
- **Reporting period:** 1998/99–2024/25; 27 distinct academic years.

- **Columns:** `academic_year`, `field_of_study`, `source_category`, `students`, `classification`, `source_file`, `source_row`, `source_column`, `source_url`.

- **Original source:** IIE Open Doors 2025, Fields of Study worksheet.

- **Original file:** [open_doors_fields.xlsx](https://opendoorsdata.org/wp-content/uploads/2025/11/Census_Field-of-Study_OD25_Website.xlsx); local `data/raw/open_doors_fields.xlsx`. Original SHA-256 verified against manifest.

- **Limitations:** 15 broad categories × 27 years; detailed categories and totals excluded. Historical sums may differ from totals; CIP and OPT field reporting changed.

- **Website use:** Supporting data; not currently plotted.

- **Processed SHA-256:** `001f55dcc24a537e06f0a5fec931bbf782e5a6ddd6e5844ab5c4ce140bcec82f`.

### international_enrollment.csv

- **Rows:** 77.
- **Reporting period:** 1948/49–2024/25; 77 distinct academic years.

- **Columns:** `academic_year`, `start_year`, `enrolled_students`, `opt_students`, `total_international_students`, `us_higher_education_enrollment`, `source_year_label`, `source_file`, `source_row`, `source_url`.

- **Original source:** IIE Open Doors 2025, International Student and U.S. Higher Education Enrollment workbook.

- **Original file:** [open_doors_enrollment.xlsx](https://opendoorsdata.org/wp-content/uploads/2025/11/Census_Overall-Enrollment-1949-2025_OD25_Website.xlsx); local `data/raw/open_doors_enrollment.xlsx`. Original SHA-256 verified against manifest.

- **Limitations:** 31 early enrolled/OPT counts are blank; three U.S. enrollment values are blank. Institutional reporting, refugee inclusion, and online/outside-U.S. coverage changed.

- **Website use:** Supporting series; the OPT chart uses its observed-OPT subset.

- **Processed SHA-256:** `c2b0c041ea268ffa99e7b5781abf7a39262c09812942d2aecc0891a93871366e`.

### opt_growth.csv

- **Rows:** 46.
- **Reporting period:** 1979/80–2024/25; 46 distinct academic years.

- **Columns:** `academic_year`, `start_year`, `enrolled_students`, `opt_students`, `total_international_students`, `us_higher_education_enrollment`, `source_year_label`, `source_file`, `source_row`, `source_url`.

- **Original source:** IIE Open Doors 2025, same original enrollment workbook.

- **Original file:** [open_doors_enrollment.xlsx](https://opendoorsdata.org/wp-content/uploads/2025/11/Census_Overall-Enrollment-1949-2025_OD25_Website.xlsx); local `data/raw/open_doors_enrollment.xlsx`. Original SHA-256 verified against manifest.

- **Limitations:** Observed OPT only, not authorizations issued or H-1B transitions. Historical coverage changes apply; 1994/95 differs by one from academic levels.

- **Website use:** Existing D3 OPT chart: csvParse → numeric start_year/opt_students → D3 scales and line → SVG. Range selector filters actual rows; no synthetic points.

- **Processed SHA-256:** `f20709543c5dfc6cfa185258b0d3c5ce3545ccf295881e2a8b04c8433904f2d4`.

### h1b_employers.csv

- **Rows:** 100.
- **Reporting period:** 2025; 1 distinct fiscal years. FY2025 covers October 1, 2024–September 30, 2025.

- **Columns:** `fiscal_year`, `employer_name`, `employer_key`, `initial_approvals`, `coverage`, `source_type`, `source_file`, `source_page`, `source_url`.

- **Original source:** USCIS data as reproduced/analyzed in NFAP November 2025 report, Appendix Table 2, pp. 23–25.

- **Original file:** [nfap_fy2025.pdf](https://nfap.com/wp-content/uploads/2025/11/H-1B-Petitions-and-Denial-Rates-For-FY-2025.NFAP-Policy-Brief.2025.pdf); local `data/raw/nfap_fy2025.pdf`. Original SHA-256 verified against manifest.

- **Limitations:** 100 selected employers with at least 100 initial approvals, not the complete registry. NFAP entity aggregation retained. No worker counts or employer-level industry field.

- **Website use:** Searchable HTML employer table; context only, not the national distribution denominator.

- **Processed SHA-256:** `79ee13b14556c1ef4deb046cd90d7ccd9fdd1daa65bb45c156847874f0d0afe4`.

### h1b_employer_distribution.csv

- **Rows:** 3.
- **Reporting period:** 2025; 1 distinct fiscal years. FY2025 covers October 1, 2024–September 30, 2025.

- **Columns:** `metric`, `value`, `unit`, `precision`, `cumulative`, `fiscal_year`, `population`, `source_type`, `source_file`, `source_page`, `source_url`.

- **Original source:** USCIS data as summarized by NFAP November 2025 report, p. 7.

- **Original file:** [nfap_fy2025.pdf](https://nfap.com/wp-content/uploads/2025/11/H-1B-Petitions-and-Denial-Rates-For-FY-2025.NFAP-Policy-Brief.2025.pdf); local `data/raw/nfap_fy2025.pdf`. Original SHA-256 verified against manifest.

- **Limitations:** Three summaries, not individual employers or histogram bins. 61% exactly one and 95% at most ten are rounded and overlapping. Never derive exact counts by multiplication/subtraction.

- **Website use:** Existing headline values read this CSV. Second D3 chart plots only the two published percentage records on a 0–100% axis.

- **Processed SHA-256:** `ef24b4a3341d6b70530e3ab4d3674d50e9200426813b76a6ad832d639cfd2fab`.

### h1b_industries.csv

- **Rows:** 20.
- **Reporting period:** 2025; 1 distinct fiscal years. FY2025 covers October 1, 2024–September 30, 2025.

- **Columns:** `fiscal_year`, `industry`, `initial_approvals`, `source_type`, `source_file`, `source_page`, `source_url`.

- **Original source:** USCIS data as reproduced/analyzed in NFAP November 2025 report, Appendix Table 4, p. 27.

- **Original file:** [nfap_fy2025.pdf](https://nfap.com/wp-content/uploads/2025/11/H-1B-Petitions-and-Denial-Rates-For-FY-2025.NFAP-Policy-Brief.2025.pdf); local `data/raw/nfap_fy2025.pdf`. Original SHA-256 verified against manifest.

- **Limitations:** Counts sum to 112,599 versus 114,806 reported nationally, an unresolved 2,207 gap. Employer industry is not worker occupation.

- **Website use:** Expandable HTML industry table, not a D3 chart.

- **Processed SHA-256:** `f8a28fdb21c1a406229b643b62e4c5b41d498af43e5d144b5a9697a508da800e`.

### h1b_selected_petitions.csv

- **Rows:** 150.
- **Reporting period:** 2023–2025; 3 distinct fiscal years. FY2025 covers October 1, 2024–September 30, 2025.

- **Columns:** `fiscal_year`, `employer_name`, `approval_type`, `approvals`, `denial_rate_percent`, `coverage`, `source_file`, `source_page`, `source_url`.

- **Original source:** USCIS data as reproduced/analyzed in NFAP November 2025 report, Tables 1 and 4, pp. 5 and 12.

- **Original file:** [nfap_fy2025.pdf](https://nfap.com/wp-content/uploads/2025/11/H-1B-Petitions-and-Denial-Rates-For-FY-2025.NFAP-Policy-Brief.2025.pdf); local `data/raw/nfap_fy2025.pdf`. Original SHA-256 verified against manifest.

- **Limitations:** Selected employer lists, 25 per approval type across three years. Selections differ by type. Initial and continuing approvals are separate; published denial rates are rounded; petitions are not unique workers.

- **Website use:** Supporting data; not currently plotted.

- **Processed SHA-256:** `be3ad058e0f08defd10bffd1d5184b5345886ff5cb97dae51a1dd37c4dcb35d9`.

## Data-to-visual verification

`src/data.js` imports processed CSVs with Vite `?raw` and parses them with D3. The OPT chart uses `opt_growth.csv`; employer and industry tables use their corresponding CSVs; summary headlines use `h1b_employer_distribution.csv`. No chart reads the archived Fru HTML. Download links bundle the same processed files.

The second chart retains row-level provenance (year, population, precision, page, and URL) when loading its two percentage records. Passing plotting tests reject missing, duplicated, mixed-year, wrong-unit, or incompatible summary records rather than fill them in. Hover, focus, and touch selection expose the original population and rounded precision.

All eight source CSVs remain unchanged in this implementation. The broader OPT-employer, overlap, and wage datasets are still unavailable. See `data/README.md` for acquisition requirements and `docs/verification.md` for execution results.

## Verification outcome

All eight CSVs were independently regenerated **in memory** from the original XLSX/PDF files using the extraction functions. Every resulting byte matched the existing CSV, including headers and all records. No raw or processed files were rewritten. Seven Python tests and seven chart-data tests passed; production build passed. Browser checks verified the new bars against their source percentages and preserved all 46 OPT observations in the full-history view.
