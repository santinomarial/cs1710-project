# Data provenance and reproduction

The latest [ICE extraction and conservative employer-match audit](../docs/ice-2024-employers.md) covers 200 employers, 47 accepted name comparisons and all exclusions.

The original Prototype V1 implementation audit is in [docs/data-audit.md](../docs/data-audit.md). It reports the complete columns, actual row counts, periods, original-file links, and limitations for every CSV. The H-1B chart now uses seven disjoint bins calculated from the complete supplied FY2025 USCIS export. The original eight CSVs remain unchanged as historical/source comparisons. See the [FY2025 reconciliation](../docs/uscis-fy2025-reconciliation.md) for the five new datasets and identity limitations.

Retrieval date: **October 25, 2026, America/New_York**. The manifest stores UTC timestamps (October 26 UTC), resolved URLs, response content types, byte lengths, and SHA-256 checksums. Retrieval date is distinct from publication date and reporting period.

## Source inventory

| Source and original URL | Local original | Coverage / result |
| --- | --- | --- |
| [IIE enrollment trends](https://opendoorsdata.org/data/international-students/enrollment-trends/) | `raw/open_doors_enrollment.xlsx` | Downloaded. Open Doors 2025 edition; 1948/49–2024/25. Separate OPT observations begin in 1979/80. |
| [IIE academic levels](https://opendoorsdata.org/data/international-students/academic-level/) | `raw/open_doors_academic_level.xlsx` | Downloaded. Broad levels for selected years 1954/55–2024/25; detailed worksheet also retained in original. |
| [IIE fields of study](https://opendoorsdata.org/data/international-students/fields-of-study/) | `raw/open_doors_fields.xlsx` | Downloaded. 1998/99–2024/25 under Open Doors 2025 broad classifications. |
| [ICE SEVIS 2024](https://www.ice.gov/doclib/sevis/btn/25_0605_2024-sevis-btn.pdf) | Not downloaded | HTTP 403. Calendar-year 2024 report requested. |
| [ICE top 200 employers](https://www.ice.gov/doclib/sevis/btn/2024/2024_Top200_Employers_OPT_STEM_OPT_Students.pdf) | `raw/2024_Top200_Employers_OPT_STEM_OPT_Students.pdf` | User-supplied official original integrated: 200 calendar-2024 employers on four pages. Prior automated 403 retained as history. |
| [USCIS Employer Data Hub](https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub) | `raw/Employer Information (1).csv` | Complete FY2025 export supplied by the user; 62,415 records. Original automated landing-page request returned 403 and remains recorded separately. |
| [NFAP FY2025 study](https://nfap.com/studies/h-1b-petitions-and-denial-rates-in-fy-2025/) | `raw/nfap_fy2025.pdf` | Downloaded. November 2025 report, 32 pages; secondary analysis of USCIS. Fiscal 2025 main extracts; selected tables also contain FY2023 and FY2024. |
| [BLS Occupational Outlook Handbook](https://www.bls.gov/ooh/) | Not downloaded | HTTP 403 for direct homepage and software-developer profile downloads. Search-tool page availability did not supply a downloaded occupational dataset. |
| [Fru / Salaries by Ibis](https://salaries.fru.dev/h1b) | `raw/fru_h1b.html` | Downloaded as reference only. Page describes selected data, AI, and engineering roles at selected employers, FY2025 Q4–FY2026 Q3; rounded employer medians are unsuitable for a matched occupation comparison. |
| [DOL OFLC performance data](https://www.dol.gov/agencies/eta/foreign-labor/performance) | Not downloaded | Additional primary-source route for wages. HTTP 403 for landing page and `LCA_Disclosure_Data_FY2025_Q4.xlsx`. |

Exact download URLs, including the three original IIE workbook filenames, are in `raw/manifest.json` and `scripts/download.py`. Only successful original responses are saved as data. HTTP error pages are not saved under dataset filenames. No authentication, proxies, mirrors, CAPTCHA workarounds, or access-control bypasses were used.

The NFAP extracts explicitly identify their secondary provenance. They remain separate from the new primary USCIS outputs and retain their original published values. Fru HTML is retained byte-for-byte and never executed by the website or used to generate wage records.

## Produced datasets

| CSV | Rows | Grain and coverage |
| --- | ---: | --- |
| `international_enrollment.csv` | 77 | One academic year, 1948/49–2024/25; missing historical OPT/enrolled values remain blank. |
| `opt_growth.csv` | 46 | One academic year with an observed OPT count, 1979/80–2024/25. |
| `academic_levels.csv` | 194 | One observed academic-year / broad-level count. Years before 1979 omit unreported non-degree and OPT counts. |
| `fields_of_study.csv` | 405 | 15 broad categories × 27 academic years. Detailed categories and total row are excluded. |
| `h1b_employers.csv` | 100 | NFAP Appendix Table 2, pages 23–25: listed employers with 100+ initial approvals, FY2025. **Not all employers.** |
| `h1b_employer_distribution.csv` | 3 | NFAP page 7: total approved employers; rounded share with exactly one approval; rounded cumulative share with 1–10 approvals. **Not reconstructed bins.** |
| `h1b_industries.csv` | 20 | NFAP Appendix Table 4, page 27; FY2025 initial approvals by reported industry. |
| `h1b_selected_petitions.csv` | 150 | NFAP Tables 1 and 4, pages 5 and 12: 25 selected employers × 3 fiscal years × 2 approval types. Selections can differ by approval type; preserve source names. |
| `uscis_fy2025_records.csv` | 62,415 | Every supplied export row; exact source names, tax suffixes, locations, NAICS and all six approval/denial categories. |
| `uscis_fy2025_employers.csv` | 55,142 | Exact reported name + tax-suffix groups across locations, including zero-initial groups; each unnamed record kept separately. |
| `uscis_fy2025_distribution.csv` | 7 | Seven disjoint bins of named groups with positive initial approvals; exact employer and approval counts and shares. |
| `uscis_fy2025_industries.csv` | 21 | 20 reported NAICS sectors plus an explicitly missing-industry group, calculated from every original row. |
| `uscis_fy2025_industry_comparison.csv` | 21 | Each USCIS industry compared with NFAP page 27. Missing NFAP values stay blank; signed differences are USCIS minus NFAP. |

**Not produced:** `wage_comparison.csv` (BLS/DOL inputs unavailable). There are no empty stand-in CSVs. The ICE annual summary report remains unavailable, but the distinct top-200 employer PDF is now integrated.

### New ICE outputs

| CSV | Rows | Grain and coverage |
| --- | ---: | --- |
| `opt_employers.csv` | 200 | All 200 ICE calendar-2024 source employers; combined total, OPT and STEM OPT retained independently. |
| `opt_h1b_employer_overlap.csv` | 47 | Only accepted one-to-one name-level comparisons of CY2024 participants with FY2025 initial approvals; not people or transition rates. |
| `opt_h1b_match_audit.csv` | 200 | One matching decision per ICE employer, including exclusion reason and candidate counts. |
| `opt_h1b_match_candidates.csv` | 455 | Lexical candidates with source identities and acceptance flags; excluded rows are not established links. |

## Column definitions

All processed CSVs use UTF-8, a header row, comma delimiters, and unformatted numeric values. Blank numeric cells mean unavailable, never zero. `validation.json` lists the complete ordered schema and row count for every CSV.

| Columns | Definition |
| --- | --- |
| `academic_year`, `start_year` | Original academic reporting period, normalized to `YYYY/YY`; integer starting year for plotting. Not a calendar-year or fiscal-year conversion. |
| `enrolled_students`, `opt_students`, `total_international_students` | IIE reported counts. Total includes enrolled plus OPT when those components are reported. OPT is not a count of approvals or necessarily new participants. |
| `us_higher_education_enrollment` | IIE's reported U.S. enrollment benchmark; source footnote describes NCES projections. Missing values remain blank. |
| `source_year_label` | Original year label, retaining asterisks that point to workbook footnotes. |
| `academic_level`, `students` | Broad level (`undergraduate`, `graduate`, `non_degree`, `opt`) and observed IIE student count. |
| `field_of_study`, `source_category`, `classification` | Broad field label without a trailing footnote digit, unchanged original label, and source classification edition. |
| `fiscal_year` | Federal fiscal year of the first decision in USCIS data, and fiscal year reported in NFAP tables. FY2025 = October 1, 2024–September 30, 2025. Not cap year or filing year. |
| `employer_name`, `employer_key` | Source display name and conservative comparison key. A key is not a verified corporate-entity identifier. |
| `initial_approvals` | Approved petitions for initial employment, which includes new and concurrent employment. Not distinct employees. |
| `approval_type`, `approvals` | Explicit `initial` or `continuing` category and petition count in selected-employer tables. Continuing includes extensions, amendments, and employer changes. |
| `denial_rate_percent` | NFAP reported percentage, in 0–100 units; retain its published rounding. No denied counts reconstructed. |
| `industry` | Industry label printed by NFAP; no inferred occupation or invented NAICS code. |
| `metric`, `value`, `unit`, `precision`, `cumulative`, `population` | Named distribution summary, observed value, units, published precision, whether cumulative, and its employer denominator. The exactly-one and 1–10 summaries overlap and must not be stacked. |
| `coverage`, `source_type` | Scope restrictions and secondary-source designation where applicable. |
| `source_file`, `source_row`, `source_column`, `source_sheet`, `source_page`, `source_url` | Provenance. Source coordinates are one-based; PDF pages count the cover as page 1. Fields vary by dataset. |

## Cleaning methodology

1. Download the explicitly identified public editions using Python's standard library. Preserve original bytes and hash them. Cached data are verified before reuse.
2. Read Excel cached values using `openpyxl`; no workbook is rewritten. Use actual year cells, not the enrollment worksheet's stale name (`Enrollment 1949-2023`). Strip year asterisks only in the normalized year column.
3. Treat `-`, `no data`, empty cells, and explicit missing markers as missing. Parse comma-separated counts; accept only nonnegative integer values, allowing less than 0.000001 of floating-point noise. Do not interpolate or estimate.
4. Use the broad academic-level worksheet. In fields of study, select bold parent-category rows from the pinned edition, excluding detailed subcategories and totals. Preserve the original category label and every numeric cell's coordinates. Shape checks prevent silently accepting a different edition.
5. Extract NFAP tables with `pdfplumber`. Collapse line breaks within employer and industry names. Inspect the relevant PDF page layout, including wrapped names. Extract the three distribution statements only when the expected surrounding text is present; the written “Sixty-one percent” is translated to 61 after checking the phrase.
6. Normalize employer keys with Unicode NFKC, uppercase, `&` → `AND`, punctuation removal, and whitespace collapse. Keep legal suffixes and subsidiaries distinct. No fuzzy matching, manual alias guesses, or automatic parent-company mergers. NFAP's source aggregation of related entities, where applied, is retained and cannot be undone from its PDF.
7. Reject duplicate analytical keys in the original eight extracts. The primary USCIS record grain and explicit aggregation rule are documented below; never treat a location row or four-digit tax suffix alone as a unique employer.
8. Validate all in-memory tables before writing output. Export CSVs plus `validation.json` and verbatim workbook footnotes in `source_notes.json`.

## Known limitations and source discrepancies

- **IIE disagreement:** 1994/95 OPT is 13,208 in the enrollment workbook and 13,209 in the academic-level workbook. Both are preserved; `opt_growth.csv` consistently uses the enrollment series. Validation explicitly checks this known one-student difference and rejects new unexplained discrepancies.
- **Industry reconciliation:** NFAP’s 20 rows sum to **112,599** versus its **114,806** national total (gap **2,207**). The supplied USCIS records yield **112,589** with reported industries plus **2,215** with missing industry = **114,804**. The matched-category difference is **−10**, and the national difference is **−2**. Missing industry explains most of the old gap, but is not an exact reconciliation of NFAP. No residual or category reassignment is invented.
- **IIE reporting changes:** institutional aggregate collection replaced individual reporting in 1974/75; refugees were included in 1975/76–1990/91; OPT was first reported separately in 1979/80; international students studying online outside the U.S. were counted in 2020/21–2022/23.
- Before 1979, non-degree and OPT were combined into an “Other” category. Broad academic categories in early years do not necessarily sum to the total. Do not calculate a residual as OPT.
- Broad field categories use the 2025 classification, which may differ from historical publications. The source warns historical category sums may not match totals. CIP 2020 replaced CIP 2010 starting with Open Doors 2021; some professional residency categories changed. OPT field-of-study reporting changed in 2008/09. Refer to `source_notes.json` and the original workbook before interpreting changes.
- OPT participation, initial approvals, continuing approvals, LCA filings, and BLS wage estimates measure different populations. An individual can be associated with multiple approved petitions. Do not combine initial and continuing counts into “workers.”
- NFAP's top-employer list cannot support a national histogram, prevalence estimate, or denominator for overlap. Its rounded 61% and 95% statements cannot recover exact bin counts.
- No OPT/H-1B linkage is claimed. Matching employer names would show common organizations only, not individual transitions. The available IIE academic years and NFAP fiscal years are labeled separately.
- No causal effect of immigration restrictions is identified by these aggregates. No wage-premium claim is made. Fru's limited employer/role sample and different reporting period are not substituted for representative worker wages or BLS occupational medians.

## Reproduction and validation

From the project root, with the virtual environment activated:

```sh
python scripts/download.py
python scripts/pipeline.py
python -m unittest discover -s tests -v
```

For an offline reproduction, omit `download.py`. For a deliberate upstream refresh, run `python scripts/download.py --refresh`, inspect the manifest and original source edition, then rerun cleaning and tests. The pinned parsers intentionally stop if expected coverage changes; review and update them instead of weakening checks to accept unknown records.

Twenty-eight Python tests cover original-source validation plus UTF-16 parsing, category totals, record preservation, exact grouping, missing identities, every industry comparison, bin conservation, malformed-input rejection, byte-identical regeneration, and manual-manifest preservation. Seven Node tests check the actual distribution CSV, failure cases, and both chart scales. Deterministic reruns must produce identical hashes for all processed files.

The pipeline currently depends on the six available structured originals. If one is unavailable on a new machine, restore its checked-in original and matching manifest or obtain the same edition through authorized access. It will not claim a complete clean run from a missing required original. The broader research pipeline remains incomplete while the ICE annual summary and BLS/DOL inputs remain unavailable. The separate ICE top-200 employer PDF and FY2025 USCIS extraction are implemented and verified.

## Manual-download handoff

These are the exact records needed through normal authorized access. Do not bypass a restriction. Simply placing a newly obtained file in `raw/` does **not** implement its parser: record provenance, inspect the schema, extend cleaning and validation, and only then enable the corresponding output.

| Needed original | Save / acquisition instruction | Work it unlocks |
| --- | --- | --- |
| `25_0605_2024-sevis-btn.pdf` | Download the [requested ICE report](https://www.ice.gov/doclib/sevis/btn/25_0605_2024-sevis-btn.pdf); preserve as `raw/sevis_2024.pdf`. | Inspect calendar-2024 definitions and totals; do not substitute IIE counts. |
| ICE top-200 employer PDF | **Integrated** under its original filename `raw/2024_Top200_Employers_OPT_STEM_OPT_Students.pdf`. | 200 records and a conservative employer-level overlap are produced; UI changes remain deferred. |
| FY2024 USCIS export for a calendar-2024 comparison (FY2025 now integrated) | In the [Hub](https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub), export **all employers**, with employer identity/name, fiscal year, initial approvals/denials, continuing approvals/denials, location, and industry/NAICS if supplied. Save the untouched export under its original filename and record filters. The service-generated filename and schema could not be verified because access was blocked; no filename is invented. | FY2025 distribution and industry reconciliation are implemented. FY2024 would support a separately qualified period-aware comparison; federal fiscal and ICE calendar years still differ. Retain identifier/location grain; do not merge solely on names. |
| `LCA_Disclosure_Data_FY2025_Q4.xlsx` and its record layout | Download [the original XLSX](https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/LCA_Disclosure_Data_FY2025_Q4.xlsx) and `LCA_Record_Layout_FY2025_Q4.pdf` via the [DOL performance page](https://www.dol.gov/agencies/eta/foreign-labor/performance). Preserve filenames. | Build a documented H-1B-only certified-filing sample, deduplicated by case identifiers; retain SOC, worksite, period, wage range, unit, and covered positions. Do not silently use the midpoint or annualize without assumptions. |
| BLS occupational wage table/profile for each selected SOC and explicit reference year | Start with the [software developers profile](https://www.bls.gov/ooh/computer-and-information-technology/software-developers.htm), save its original HTML, and retain the wage reference year and separate occupations. Additional occupations and exact reference files must be chosen after inspecting the LCA SOC coverage. | Match occupation codes and wage reference periods; disclose national versus location-specific scope and sample weighting. A profile title alone is not an SOC match. |

For any manual file, record its source URL, UTC retrieval time, untouched filename, reporting period, filters, byte length, SHA-256, and acquisition method in the manifest before ingestion. Check hashes with `shasum -a 256 <file>` (macOS) or `sha256sum <file>` (Linux). Preserve the prior blocked attempt in the project history or a separate acquisition log.


## Supplied FY2025 USCIS original

The file was found in the user’s Downloads directory and copied byte-for-byte to `raw/Employer Information (1).csv`. It is **UTF-16 LE with a BOM, tab-separated**, despite the `.csv` extension. It contains 62,415 records, all FY2025 (October 1, 2024–September 30, 2025), and 20 original columns. The user identifies it as the complete Hub export; the original retrieval timestamp, query receipt, and USCIS snapshot revision were not supplied. The manifest records this provenance honestly as `provided_local`, with an ingestion timestamp and a null retrieval timestamp. The earlier 403 request is retained.

- Original bytes: **15,342,594**.
- SHA-256: `49299055b254ab1f950c9f86e43c548becacfba6f151bb9e345f61d6ddd6ec37`.
- The downloader preserves this manifest entry even with `--refresh`; it never fetches over the manual original and fails on a checksum mismatch.
- Offline reproduction runs `scripts/pipeline.py`, which verifies the manifest checksum before parsing and delegates to `scripts/uscis.py`. No network access or local Downloads dependency is needed after import.

The parser trims header whitespace only (the fiscal-year header has trailing spaces), preserves employer spellings, leading-zero tax suffixes and ZIP codes, and converts properly comma-formatted nonnegative integer counts. Missing or malformed counts cause failure; they are never filled with zero. Line IDs and one-based source rows are retained. All six petition categories and their approval/denial fields remain separate. Initial totals are new employment + new concurrent employment. Continuing totals are continuation + change with same employer + change of employer + amended petitions. The Hub counts petition decisions, **not unique workers**, cap selections, or newly arrived people. See the [USCIS FY2024 methodology, footnote 3](https://www.uscis.gov/sites/default/files/document/reports/ola_signed_h1b_characteristics_congressional_report_FY24.pdf).

Employer grouping uses **exact reported name and exact tax suffix**, combining locations only within that pair. It deliberately does not reuse NFAP’s punctuation-normalized comparison key. There are 55,131 named groups and 11 unnamed source records, for 55,142 output rows. The opaque group ID is a hash of the grouping tuple, not a fabricated employer identity. Source line lists allow every aggregation to be traced back. The tax field contains only a partial identifier: 198 records have blank suffixes and one contains the nonstandard string `0`, retained exactly rather than padded or guessed. An identical name with a blank suffix is grouped only with the same exact name and blank suffix. Names with different suffixes remain separate. Name variants can split one legal employer; coincident names/suffixes can conflate employers. These are analytical employer groups, not a verified count of unique companies.

All 11 missing names remain blank and separate. Five have positive initial approvals, totaling **6**. The named-employer chart excludes them and the 25,781 named groups with zero initial approvals. Its denominator is **29,350 named groups / 114,798 initial approvals**. The seven bins are 1, 2–5, 6–10, 11–50, 51–100, 101–500 and 501+. Both employer shares and approval shares are computed from exact counts; bins do not overlap. No corporate “big tech” classification is inferred. Education and health-care examples use supplied NAICS labels.

Missing industry codes occur in **3,211 original records**, totaling **2,215 initial approvals**. The primary industry output labels this observed missingness as “Industry not reported” and leaves its NAICS code blank. It is not a residual created to match NFAP. The 49 missing states and 53 missing ZIP codes also remain blank; petitioner addresses are not asserted to be worker locations.

The original NFAP employer/industry tables remain explicitly attributed comparison views on the website. The interactive distribution and its headline statistics use `uscis_fy2025_distribution.csv`; its industry context uses `uscis_fy2025_industries.csv`. The complete record and employer CSVs are downloadable assets, not loaded into the chart’s JavaScript bundle. See `processed/validation.json` for the full schemas and `processed/uscis_fy2025_reconciliation.json` for machine-readable checks.


## Supplied ICE calendar-2024 employer PDF

Original URL: <https://www.ice.gov/doclib/sevis/btn/2024/2024_Top200_Employers_OPT_STEM_OPT_Students.pdf>. Preserved file: `raw/2024_Top200_Employers_OPT_STEM_OPT_Students.pdf`, **483,377 bytes**. SHA-256: `e4e306a6ce75e347a2bc87b88403f5cb1eadc2707b6880c04faf259688860f3f`. The user’s official download was located in Downloads and copied unchanged. Source URL is confirmed by file download metadata. The actual retrieval date is pending user confirmation; null retrieval fields and a separate ingestion timestamp avoid confusing import time or PDF metadata dates with download time. The earlier 403 under the old alias remains in the manifest; manual originals survive downloader refreshes.

`scripts/ice.py` extracts 200 rows from four table pages (58, 63, 63, 16). Header/schema, calendar year, footnote, page coverage and table/text agreement are validated before output. Each row retains page and per-page data-row provenance. The five major-company controls are verified in [the audit](../docs/ice-2024-employers.md), alongside complete schemas for all four new CSVs.

**Combined participation is not OPT + STEM OPT.** The PDF warns that a student at the same employer in a different program can be counted multiple times. We retain the independently reported combined total; no counts or person-level intersections are reconstructed. All **11 blank STEM OPT cells remain missing**; no printed cell explicitly contains zero. `AMERICAN TECHNOLOGY CONSULTING L` is visibly clipped on page 4 and is preserved with a note, not expanded.

The overlap contains **47 accepted name-level matches**, using unique normalized full names, a standard USCIS tax suffix and no competing token-prefix scope alternatives. Normalization changes only case/spacing/punctuation/ampersands, never legal words, suffixes or campus qualifiers. All 200 decisions and 455 lexical candidates are retained. Exclusions comprise **14 ambiguous full-name cases, 97 unresolved variants, 41 with no candidate, and one clipped name**. Prefix candidates are not evidence of affiliation. ICE does not supply shared identifiers, so accepted comparisons are not independently verified legal identities.

The comparison is **CY2024 employer participation versus FY2025 H-1B initial approvals**. It includes new employment and concurrent approvals, not continuing approvals or unique workers. These periods overlap in October–December 2024; they do not define sequential cohorts. There are no conversion rates or student transitions. The top-200 list and conservative matched subset are not representative national employer samples. Existing chart code/data remain unchanged; placeholder/source-card updates are deferred to a later UI phase at the user’s request.
