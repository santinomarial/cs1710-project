# ICE calendar-2024 employer extraction and USCIS comparison

## Provenance

The original [ICE PDF](https://www.ice.gov/doclib/sevis/btn/2024/2024_Top200_Employers_OPT_STEM_OPT_Students.pdf) is preserved as `data/raw/2024_Top200_Employers_OPT_STEM_OPT_Students.pdf`. It was located in the user’s Downloads directory and copied byte-for-byte. macOS `kMDItemWhereFroms` confirms the official ICE URL (with a tracking query); the canonical URL is recorded without that query. The manifest retains the earlier blocked automated request under `opt_employers_2024.pdf` as historical evidence. The downloader recognizes the supplied URL and does not fetch a duplicate or overwrite the manual original, even with `--refresh`.

- Bytes: **483,377**.
- SHA-256: `e4e306a6ce75e347a2bc87b88403f5cb1eadc2707b6880c04faf259688860f3f`.
- Reporting period: **calendar year 2024**, January 1–December 31.
- Coverage: **200 listed employers** across four PDF pages, with **58 / 63 / 63 / 16** data rows.
- Retrieval date: **not yet confirmed**; requested from the user. Download-date metadata is absent. The manifest uses null for retrieval date/time and records the actual import timestamp separately. PDF creation/modification dates are not used as download dates.

## Extraction and counting rules

`scripts/ice.py` uses `pdfplumber` to extract the four-column grid on each page. It verifies the exact edition title, column headers, page counts and counting caveat, removes only the page-1 header, and preserves every employer in printed order. `source_order` is the one-based printed order, not an invented rank for ties. `source_page` counts physical PDF pages 1–4; `source_table_row` counts data rows within each page, excluding the header. Source names retain spelling/case and normalize only line wrapping/whitespace. Numeric commas are removed; missing cells remain empty in CSV and `None` in Python. Unexpected numeric markers stop extraction rather than silently becoming zero.

All **200 grid rows** also agree with the independently extracted text lines from the PDF. All four pages were visually reviewed, including page boundaries, blank cells and the final row (Brown University). Automated tests compare **all 600 numeric cells** and 200 names back to their original page/table positions. No OCR, row interpolation, inferred totals or fabricated employer names were needed.

The source caveat is preserved verbatim, including its spelling:

> **If a student is employed at the same Employer wile in a different program, he/she will be counted multiple times for the employer.

The combined column is an independent source observation. **Do not add OPT and STEM OPT to reconstruct it**, infer a unique-person population from the rows, or aggregate employer counts into a national unique-student total. The table is only the published top-200 list, not all OPT employers. It does not document corporate aggregation rules or supply tax IDs or addresses for joining.

### Verified page-1 controls

| Employer | Total OPT or STEM OPT | OPT | STEM OPT |
| --- | ---: | ---: | ---: |
| Amazon | 10,167 | 5,379 | 6,679 |
| Google | 2,454 | 1,110 | 1,778 |
| Microsoft | 2,143 | 1,066 | 1,496 |
| Meta | 2,032 | 1,081 | 1,302 |
| Apple | 1,621 | 1,135 | 973 |

For example, Amazon’s source combined count is 10,167, while 5,379 + 6,679 = 12,058. We retain 10,167; neither the sum nor a reconstructed overlap replaces a source value.

### Missing and clipped source cells

There are **11 blank STEM OPT cells**, no blank total/OPT cells, and **no explicit zero cells** in the PDF. Blank values are not inferred as zero even where total equals OPT. The missing STEM OPT values are:

- Bright Mind Enrichment and Schooling — page 1, data row 16.
- Changing The Present — page 1, data row 46.
- THE KEELWORKS FOUNDATION — page 2, data row 4.
- OUTLIER — page 2, data row 8.
- Carnegie Mellon University — page 2, data row 20.
- Match4Action-CrowdDoing — page 2, data row 33.
- REBECCA EVERLENE TRUST COMPANY — page 2, data row 44.
- ONE COMMUNITY — page 3, data row 15.
- ABECEDARIAN — page 3, data row 35.
- JERSEYSTEM — page 3, data row 50.
- CROWDDOING — page 4, data row 15.

On page 4, data row 11 (source order 195), **AMERICAN TECHNOLOGY CONSULTING L** is visibly clipped at the employer-column edge. We preserve exactly the extracted name, attach a `name_note`, and exclude it from matching. We do not expand it to a guessed legal suffix. This is a source-layout limitation, not a missing table row. There were no grid/text disagreements or lost rows.

## Conservative employer matching

The comparison is explicitly **employer-level: CY2024 OPT/STEM OPT participation versus FY2025 H-1B initial approvals**. FY2025 covers October 1, 2024–September 30, 2025. These reporting periods overlap during October–December 2024; they are not sequential student cohorts. No individual transitions, conversion rates, causal effects, or share of OPT students receiving H-1B status can be calculated from this join.

The matcher starts with every named USCIS group, including groups with zero initial approvals. It normalizes Unicode, case, whitespace, punctuation and `&` → `AND`, preserving every word, legal suffix and campus term. It does **not** strip legal suffixes, equate abbreviations, fuzzy-match spelling, merge campuses/subsidiaries or choose whichever candidate has the most approvals.

An accepted match must have one unique normalized full name on each side, exactly one USCIS group with a standard four-digit suffix, and no competing longer/shorter token-prefix name that would make the ICE label’s scope uncertain. A prefix alternative is only a lexical warning, **not proof of affiliation** (for example, Apple Tree Dental is not assumed to be Apple Inc.). The presence of such an alternative blocks an otherwise exact match. This intentionally favors excluding uncertain comparisons over maximizing match coverage.

USCIS group IDs, original name, suffix and source line references are retained. Only the selected group’s reported initial approvals are used: new employment + new concurrent employment, with continuing categories excluded. The existing USCIS grouping is not changed. Missing OPT cells remain missing in the overlap output.

These are **47 defensible, reproducible name-level matches under the stated rule**, not 47 independently verified legal-entity identities. ICE provides no shared tax ID, address or corporate-scope crosswalk. Undetected spelling variants or corporate aggregation can still affect scope; a stricter identity verification would require additional source documentation. The selected subset is not representative of all employers and unmatched names do not establish absence of H-1B sponsorship.

### Audit outcomes

| Status | ICE employers | Treatment |
| --- | ---: | --- |
| Accepted unique full name | 47 | Included in overlap CSV |
| Multiple USCIS full-name matches | 7 | Ambiguous; excluded |
| Full-name match plus scope alternatives | 7 | Ambiguous; excluded |
| Prefix/name variants only | 97 | Unresolved; excluded |
| No conservative candidate | 41 | Excluded; no negative sponsorship inference |
| Clipped source name | 1 | Excluded; not completed by guesswork |

Thus **153 entries are excluded**: 14 ambiguous full-name cases, 97 unresolved variants, 41 without candidates, and one clipped name. All decisions appear in the 200-row audit; the 455-row candidate file includes accepted and excluded lexical candidates without asserting affiliations or summing them into employer totals.

### The 14 ambiguous full-name cases

| ICE name | Full-name groups | Additional prefix candidates | Reason |
| --- | ---: | ---: | --- |
| Johns Hopkins University | 1 | 1 | An exact name exists alongside longer/shorter petitioner names; ICE corporate/campus scope is unverified. |
| University of Michigan | 3 | 0 | Full normalized name maps to multiple USCIS groups or ICE rows; no group is selected or summed. |
| Columbia University | 2 | 0 | Full normalized name maps to multiple USCIS groups or ICE rows; no group is selected or summed. |
| University of Maryland | 1 | 9 | An exact name exists alongside longer/shorter petitioner names; ICE corporate/campus scope is unverified. |
| Indiana University | 1 | 4 | An exact name exists alongside longer/shorter petitioner names; ICE corporate/campus scope is unverified. |
| Texas A&M University | 2 | 8 | Full normalized name maps to multiple USCIS groups or ICE rows; no group is selected or summed. |
| Fidelity Investments | 7 | 1 | Full normalized name maps to multiple USCIS groups or ICE rows; no group is selected or summed. |
| University of Minnesota | 1 | 1 | An exact name exists alongside longer/shorter petitioner names; ICE corporate/campus scope is unverified. |
| ADOBE INC | 3 | 0 | Full normalized name maps to multiple USCIS groups or ICE rows; no group is selected or summed. |
| AECOM | 1 | 1 | An exact name exists alongside longer/shorter petitioner names; ICE corporate/campus scope is unverified. |
| Vanderbilt University | 1 | 2 | An exact name exists alongside longer/shorter petitioner names; ICE corporate/campus scope is unverified. |
| Michigan State University | 2 | 0 | Full normalized name maps to multiple USCIS groups or ICE rows; no group is selected or summed. |
| California Institute of Technology | 1 | 1 | An exact name exists alongside longer/shorter petitioner names; ICE corporate/campus scope is unverified. |
| Ford Motor Company | 2 | 0 | Full normalized name maps to multiple USCIS groups or ICE rows; no group is selected or summed. |

For example, University of Michigan has three exact-name tax groups (including a zero-initial group); Adobe and Ford also have zero-initial alternatives. Removing zero-initial groups before matching would hide the ambiguity. Indiana University has additional campus/health-system names, including a same-suffix campus record; AECOM has a separate technical-services petitioner. Neither label is joined to a convenient subset or consolidated without evidence.

### Requested major employers

The five source-control employers all have reliable extracted PDF values, but **none is accepted into the cross-source overlap** under the conservative rule:

| ICE label | Lexical prefix candidates | Why no automatic join |
| --- | ---: | --- |
| Amazon | 28 | Multiple differently named petitioners and tax suffixes; no documented ICE corporate roll-up. |
| Google | 4 | Google LLC, alternate/missing suffixes and a public-sector petitioner. |
| Microsoft | 2 | The source uses a short label; USCIS has Corporation records with reported and missing suffixes. |
| Meta | 12 | Platforms/Payments and unrelated similarly prefixed businesses; lexical similarity does not establish affiliation. |
| Apple | 11 | Apple Inc./Payments and unrelated similarly prefixed businesses; lexical similarity does not establish affiliation. |

University of California and University of Texas also have campus-specific petitioner candidates. A corporate/campus crosswalk from authoritative documentation would be needed to decide whether and how they align with ICE’s broader labels. Prefix searches are intentionally incomplete and are not evidence of all subsidiaries.

## Outputs and schemas

All CSVs are UTF-8 with comma delimiters and unformatted numeric counts. Blank numeric cells mean missing. The two source periods and both sources’ provenance are explicit in every accepted comparison. The original 13 processed CSVs remain byte-identical.

### `opt_employers.csv` — 200 rows

Columns: `source_order`, `employer_name`, `total_opt_or_stem_opt_participants`, `opt_participants`, `stem_opt_participants`, `calendar_year`, `source_type`, `source_file`, `source_page`, `source_table_row`, `source_url`, `name_note`, `counting_note`.

### `opt_h1b_employer_overlap.csv` — 47 rows

Columns: `employer_name`, `uscis_employer_name`, `uscis_employer_group_id`, `uscis_tax_id_suffix`, `total_opt_or_stem_opt_participants`, `opt_participants`, `stem_opt_participants`, `calendar_year`, `h1b_fiscal_year`, `h1b_new_employment_approvals`, `h1b_new_concurrent_approvals`, `h1b_initial_approvals`, `match_method`, `match_status`, `comparison_label`, `identity_limitation`, `counting_note`, `source_file`, `source_page`, `source_table_row`, `source_url`, `uscis_source_file`, `uscis_source_lines`, `uscis_source_url`.

### `opt_h1b_match_audit.csv` — 200 rows

Columns: `ice_employer_name`, `normalized_name`, `match_status`, `full_name_candidate_count`, `prefix_candidate_count`, `reason`, `calendar_year`, `h1b_fiscal_year`, `source_file`, `source_page`, `source_url`, `identity_limitation`.

### `opt_h1b_match_candidates.csv` — 455 rows

Columns: `ice_employer_name`, `uscis_employer_name`, `uscis_employer_group_id`, `tax_id_suffix`, `candidate_relationship`, `match_status`, `accepted`, `candidate_initial_approvals`, `candidate_source_lines`, `calendar_year`, `h1b_fiscal_year`, `source_file`, `source_page`, `source_url`, `uscis_source_file`, `uscis_source_url`, `interpretation`.

`opt_employers.csv` includes all 200 printed employers and source values. `opt_h1b_employer_overlap.csv` contains only accepted one-to-one name comparisons. `opt_h1b_match_audit.csv` records one decision per ICE employer, including exclusions. `opt_h1b_match_candidates.csv` is a review artifact; `accepted=false` rows must never be used as established links. It includes zero-approval and missing-suffix candidates so uncertainty is visible. `ice_2024_validation.json` records page counts, source caveat, missing cells, extraction checks and match-status totals.

## Reproduction and website scope

```sh
python scripts/pipeline.py
python -m unittest discover -s tests -v
npm run test:charts
npm run build
```

Run Python from an environment with the pinned `requirements.txt` dependencies. The pipeline verifies all required original checksums and uses no network access. The raw ICE PDF is required; Downloads is not needed after import. `download.py --refresh` preserves manual sources and historical failed attempts for the same URL.

No visualization or website source file was edited. Existing charts still use byte-identical input CSVs. The existing downloads glob naturally exposes the new CSVs, and validation metadata updates dynamically; the old OPT placeholder and historical source-card copy are deliberately left for the next UI phase. No new visualization, person-level linkage or conversion-rate view is claimed. No commit or push was made.
