# FY2025 USCIS integration and reconciliation

Verified against the preserved user-supplied export. This document supersedes the earlier “full USCIS export unavailable” limitation; the original eight-file audit remains valid for its unchanged CSVs.

## Provenance and source grain

`data/raw/Employer Information (1).csv`: UTF-16 LE BOM, tab-separated, 15,342,594 bytes, 62,415 records, all FY2025. SHA-256: `49299055b254ab1f950c9f86e43c548becacfba6f151bb9e345f61d6ddd6ec37`. User-supplied as the complete [USCIS Hub export](https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub), found in Downloads and copied unchanged. Acquisition method, import time, filters as reported, missing retrieval time and checksum are recorded in the manifest. The raw file is never rewritten.

A source row combines petitioner name, partial tax ID, industry and address with petition-decision counts. It is neither a person nor necessarily an entire employer. No duplicate full source records were found after excluding the line-number column. All line numbers 1–62,415 are present. Numeric fields accept thousands separators; leading zeros in identifier strings survive extraction.

## Category totals

| Petition category | Approvals | Denials |
| --- | ---: | ---: |
| New employment | 113,458 | 3,270 |
| New concurrent employment | 1,346 | 84 |
| Continuation | 118,194 | 1,963 |
| Change with same employer | 39,967 | 688 |
| Change of employer | 68,168 | 1,385 |
| Amended | 65,214 | 1,535 |
| Combined initial | 114,804 | 3,354 |
| Combined continuing | 291,543 | 5,571 |

Initial is new employment + new concurrent; continuing is the other four categories. Initial and continuing are not added into a worker count. This follows [USCIS’s methodology](https://www.uscis.gov/sites/default/files/document/reports/ola_signed_h1b_characteristics_congressional_report_FY24.pdf), footnote 3. The tax suffix is only the last four digits, as documented in the [USCIS FY2023 report, transparency section](https://www.uscis.gov/sites/default/files/document/reports/OLA_Signed_H-1B_Characteristics_Congressional_Report_FY2023.pdf).

## Investigation of NFAP differences

The retained [NFAP report](https://nfap.com/wp-content/uploads/2025/11/H-1B-Petitions-and-Denial-Rates-For-FY-2025.NFAP-Policy-Brief.2025.pdf), page 7, reports 114,806 initial, 291,542 continuing and 68,167 change-of-employer approvals. The supplied export has **114,804 (−2)**, **291,543 (+1)** and **68,168 (+1)**, respectively.

Checks performed: all supplied records are FY2025; all six categories are parsed without blanks or suppressed counts; all line IDs are present; no exact full-row duplicates; counts conserve through every grouping; concurrent approvals are included exactly once; change-of-employer approvals are continuing; unnamed and missing-industry records remain in national totals. Omitting blank names would yield 114,798, not NFAP’s total. Employer grouping changes counts of groups but cannot change summed approvals. No rounding applies to approval counts.

The report supplies no row-level snapshot or identity crosswalk to isolate the differing petitions. A later source revision or NFAP processing could explain the differences, but neither is established. **The two-approval difference remains unresolved.** No two records or approvals are invented, deleted, or reassigned to force agreement. To resolve it, obtain the exact USCIS snapshot used by NFAP and its cleaning/grouping rules.

NFAP’s 20 industries total 112,599, leaving 2,207 against its national total. Our 20 reported sectors total 112,589 (−10 vs NFAP), and actual blank-industry records contribute 2,215. Thus **112,589 + 2,215 = 114,804**, and **−10 + 2,215 − 2,207 = −2**. Missing industry explains most of the original gap, but calling it an exact explanation of NFAP’s residual would be incorrect.

| Industry / NAICS | Supplied USCIS initial approvals | NFAP page 27 | USCIS − NFAP |
| --- | ---: | ---: | ---: |
| Professional, Scientific, and Technical Services (54) | 44,180 | 44,184 | -4 |
| Educational Services (61) | 15,966 | 15,941 | +25 |
| Manufacturing (31-33) | 11,496 | 11,521 | -25 |
| Information (51) | 10,058 | 10,062 | -4 |
| Health Care and Social Assistance (62) | 8,970 | 8,963 | +7 |
| Finance and Insurance (52) | 8,031 | 8,034 | -3 |
| Retail Trade (44-45) | 4,906 | 4,908 | -2 |
| Industry not reported (missing) | 2,215 | Not reported | Not comparable |
| Administrative and Support and Waste Management and Remediation Services (56) | 1,839 | 1,838 | +1 |
| Construction (23) | 1,393 | 1,391 | +2 |
| Wholesale Trade (42) | 1,367 | 1,373 | -6 |
| Management of Companies and Enterprises (55) | 776 | 786 | -10 |
| Other Services (except Public Administration) (81) | 764 | 766 | -2 |
| Transportation and Warehousing (48-49) | 653 | 647 | +6 |
| Real Estate and Rental and Leasing (53) | 489 | 490 | -1 |
| Utilities (22) | 467 | 463 | +4 |
| Accommodation and Food Services (72) | 353 | 352 | +1 |
| Public Administration (92) | 342 | 342 | +0 |
| Arts, Entertainment, and Recreation (71) | 251 | 251 | +0 |
| Mining, Quarrying, and Oil and Gas Extraction (21) | 226 | 226 | +0 |
| Agriculture, Forestry, Fishing and Hunting (11) | 62 | 61 | +1 |

“Professional, Scientific, and Technical” in NFAP is explicitly matched to export sector 54. All other labels match directly. No values or categories are relabeled to reduce differences. Missing NFAP values are blank, never zero.

## Employer identity and distribution

Exact name + exact tax suffix produces **55,131 named groups**, plus **11 separate unnamed records**. Source names, suffixes and line references are retained. No case/punctuation/suffix cleanup, fuzzy entity resolution, or parent-company consolidation is applied. The output includes all supplied records, even if initial approvals are zero.

**29,350 named groups** have positive initial approvals, totaling **114,798**. The five positive unnamed records account for the remaining **6** approvals. All 11 unnamed rows stay in the outputs with blank names; record IDs only identify source rows. There are **25,781 named groups with zero initial approvals** outside the chart population. No zero-only group is portrayed as having initial approvals.

Identity sensitivity is material: there are 31,769 positive source rows (including unnamed), 29,210 distinct nonblank exact names with positive approvals, and 29,350 positive exact name/tax groups. None reproduces NFAP’s 28,277. No claim is made that any of these is a unique legal-employer count. Partial-ID collisions, 198 blank tax suffixes, one literal `0` suffix, and unmerged spelling variants remain limitations. The chart’s calculated **62.5%** with exactly one and **95.4%** with 1–10 approvals use our stated denominator, not NFAP’s rounded 61% and 95%.

| Initial approvals per group | Named groups | Initial approvals | Share of groups | Share of approvals |
| --- | ---: | ---: | ---: | ---: |
| 1 | 18,343 | 18,343 | 62.4974% | 15.9785% |
| 2–5 | 8,090 | 22,520 | 27.5639% | 19.6171% |
| 6–10 | 1,561 | 11,627 | 5.3186% | 10.1282% |
| 11–50 | 1,113 | 22,312 | 3.7922% | 19.4359% |
| 51–100 | 144 | 10,259 | 0.4906% | 8.9366% |
| 101–500 | 87 | 17,227 | 0.2964% | 15.0064% |
| 501+ | 12 | 12,510 | 0.0409% | 10.8974% |

Each group is in one bin only. Small shares display as “<0.1%” instead of incorrectly showing zero. The chart offers employer-share and approval-share views with a common 0–100% axis, mouse/touch selection, keyboard focus, exact-count detail, and an alternate data table. Industry context includes all records: education 15,966 and health care/social assistance 8,970 initial approvals. These are employer industries, not worker occupations or a technology/nontechnology classification.

## New output inventory

All five new CSVs use UTF-8, comma delimiters, and unformatted numbers. Their period is FY2025; original source is the preserved USCIS export. The comparison CSV additionally cites NFAP page 27. Existing eight CSVs and the OPT component remain byte-identical.

### `uscis_fy2025_records.csv` — 62,415 rows

Columns: `record_id`, `source_line`, `source_row`, `employer_group_id`, `employer_name`, `name_status`, `tax_id_suffix`, `industry_source`, `naics_code`, `industry`, `petitioner_city`, `petitioner_state`, `petitioner_zip_code`, `new_employment_approvals`, `new_employment_denials`, `new_concurrent_approvals`, `new_concurrent_denials`, `continuation_approvals`, `continuation_denials`, `change_with_same_employer_approvals`, `change_with_same_employer_denials`, `change_of_employer_approvals`, `change_of_employer_denials`, `amended_approvals`, `amended_denials`, `initial_approvals`, `continuing_approvals`, `initial_denials`, `continuing_denials`, `fiscal_year`, `source_file`, `source_url`, `source_type`.

### `uscis_fy2025_employers.csv` — 55,142 rows

Columns: `employer_group_id`, `employer_name`, `name_status`, `tax_id_suffix`, `identity_method`, `source_record_count`, `source_lines`, `naics_codes`, `new_employment_approvals`, `new_employment_denials`, `new_concurrent_approvals`, `new_concurrent_denials`, `continuation_approvals`, `continuation_denials`, `change_with_same_employer_approvals`, `change_with_same_employer_denials`, `change_of_employer_approvals`, `change_of_employer_denials`, `amended_approvals`, `amended_denials`, `initial_approvals`, `initial_denials`, `continuing_approvals`, `continuing_denials`, `fiscal_year`, `source_file`, `source_url`, `source_type`.

### `uscis_fy2025_distribution.csv` — 7 rows

Columns: `bin_order`, `bin_label`, `lower_bound`, `upper_bound`, `employer_count`, `initial_approvals`, `employer_share_percent`, `approval_share_percent`, `population_employers`, `population_initial_approvals`, `excluded_unnamed_records`, `excluded_unnamed_initial_approvals`, `population`, `identity_method`, `fiscal_year`, `source_file`, `source_url`, `source_type`.

### `uscis_fy2025_industries.csv` — 21 rows

Columns: `naics_code`, `industry`, `industry_status`, `source_record_count`, `new_employment_approvals`, `new_employment_denials`, `new_concurrent_approvals`, `new_concurrent_denials`, `continuation_approvals`, `continuation_denials`, `change_with_same_employer_approvals`, `change_with_same_employer_denials`, `change_of_employer_approvals`, `change_of_employer_denials`, `amended_approvals`, `amended_denials`, `initial_approvals`, `initial_denials`, `continuing_approvals`, `continuing_denials`, `fiscal_year`, `source_file`, `source_url`, `source_type`.

### `uscis_fy2025_industry_comparison.csv` — 21 rows

Columns: `naics_code`, `industry`, `uscis_initial_approvals`, `nfap_initial_approvals`, `difference_uscis_minus_nfap`, `comparison_status`, `nfap_source_file`, `nfap_source_page`, `nfap_source_url`, `fiscal_year`, `source_file`, `source_url`, `source_type`.

`records` retains every original line; `employers` retains all groups and semicolon-delimited source lines/NAICS coverage; `distribution` excludes unnamed and zero-initial groups with denominators explicit; `industries` includes observed missing industry; `industry_comparison` reports signed differences and unmatched missingness. `source_row` is one-based including the header; `source_line` is the export’s own line ID. SHA-derived `employer_group_id` is an analytical join key, not a source-issued corporate identifier. Full ordered schemas are also in `validation.json`.

Reproduce with `python scripts/pipeline.py`, then `python -m unittest discover -s tests -v`, `npm run test:charts`, and `npm run build`. No Downloads path is required on subsequent runs. The complete record/employer downloads total about 43 MB; the chart reads only the compact distribution and industry CSVs. Automatic retrieval of the original export remains unsupported, but the archived input and deterministic transformation are reproducible offline.
