# Verification — additional unimplemented designs

Verified October 25, 2026 (America/New_York). This is a documentation-only phase. The two new visualizations remain **proposed and unimplemented**.

## Export and visual review

- `04-h1b-geographic-map.png` and `05-fields-of-study-stacked-area.png` are valid **3240 × 2700 PNGs**, rendered at 216 dpi from vector page layouts.
- Both exported images were visually inspected for typography, spacing, clipping, chart/legend readability, source notes, selections and proposed-control labels. The fields tooltip was moved into unused chart space to expose the historical area profile; the revised export was inspected again.
- The map has a count legend, selected California outline/detail, Texas hover preview, Alaska/Hawaii inset labels, DC callout and visible outside-map accounting. The area chart includes all 15 categories, year/count axes, field legend, mode controls, observed-value tooltip and reporting-break annotations.
- Footer notes and caveats remain within page bounds. Original PNGs 01–03 and the original six-page PDF were not regenerated or edited.
- Static mockups document proposed interactions; no claim is made that the illustrated controls work or have been user-tested. The intermediate PDF in `tmp/pdfs/` is not a submitted or assembled process book.

## Geographic numeric checks

The renderer verifies 62,415 unique `record_id` values, complete source-line coverage 1–62,415, and FY2025 on every row. On **every record**, initial approvals equal new employment plus new concurrent employment. Every input record contributes once to exactly one literal petitioner-state group.

The same grouping was independently recomputed from the unchanged UTF-16/tab-separated original export. **Every location group's initial, new, concurrent and source-record counts match the processed CSV.** No continuing category, denial, employer-level replication or inferred employer identity enters the sum.

| Check | Verified result |
| --- | ---: |
| New employment approvals | 113,458 |
| New concurrent approvals | 1,346 |
| Combined initial approvals | 114,804 |
| 50 states + DC mapped | 114,396 |
| Territories shown separately | 385 |
| Blank/unmapped codes shown separately | 23 |
| Reconciliation | 114,396 + 385 + 23 = 114,804 |
| California selection | 21,552 = 21,350 + 202; 18.8% |
| Texas tooltip | 12,618; 11.0% |

All displayed territory/unlocated counts were separately checked: GU 312, PR 31, MP 28, VI 14, AS 0, blank 22, XX 1, AA 0. The national-share denominator always includes them. The legend midpoint, 10,776, is half the maximum state count, 21,552; it is not a claimed observation. Source-backed zero and missing geography remain distinct.

The archived Census geometry SHA-256 is checked on every render. All 50 state/DC codes join to the original boundary attributes. Shape coordinates are projected original vertices; labels are derived polygon centroids. No geographic coordinates or petitioner worksites were fabricated. The exact map geometry provenance is in `assets/cb_2024_us_state_20m.provenance.json`.

## Fields-of-study numeric checks

- **405 unique field-year pairs = 15 fields × 27 consecutive academic years**, 1998/99–2024/25.
- **All 405 counts** match the original workbook cells referenced by each processed row. All years have the same 15 broad-category labels. There are **zero missing count cells** in this extract.
- Every stack boundary is computed from actual CSV counts in a fixed order; the stack top equals that year's 15-category sum. The 1.2-million axis ceiling contains every annual sum.
- The selected 2024/25 observation is **305,377 Math and Computer Science students**, with a **1,177,766** summed-field denominator. Its rounded share is **25.9%**. No published national total is substituted for the field sum.
- Proposed composition values sum to 100% in each of the 27 years (within floating-point precision). Selection is specified to keep this denominator stable.
- Separate area segments retain every observed year but do not connect across the 2008/09 OPT reporting change or the 2020/21 CIP change. These breaks are named visibly. No missing observations are interpolated or assigned zero.
- The full published note set remains unchanged in `data/processed/source_notes.json`; the design documentation also discusses earlier classification changes, differing historical totals and future missing-cell behavior.

## Preservation and reproducibility

Executed successfully:

```sh
python3 docs/visualization-designs/render_additional_drafts.py
```

The renderer includes the record, component, source-cell, geometry-checksum and stack assertions described above. A separate verification pass checked the pictured state values and shares, all annual composition totals, PNG decoding/dimensions/output hashes, and the vector pages' pictured values and proposed-status text.

Pre/post SHA-256 comparisons confirmed **69 pre-existing protected files unchanged**, covering the website sources, public files, raw/processed data, pipeline scripts, tests and root configuration files present in the baseline. The only changed root documentation file is `README.md`, whose obsolete “only wage remains unimplemented” sentence now points to the current three-design set. Other saved changes are under `docs/`; temporary render/check artifacts are under `tmp/`. No application, dataset, cleaning-script or dependency changes were made.

The prior website/data test and production-build results are recorded in `../website-polish-verification.md`. They were **not rerun for these static documentation-only changes**; the checks above validate this phase. No commit, push, publication or new React/D3 implementation occurred.

## Requirement status

Requirement 4 now has **three verified unimplemented design deliverables**: wages (02), geography (04), fields of study (05). The full requirement still awaits inclusion in the actual process book. Requirement 7 remains satisfied by the designed and implemented novel employer view. Contributor documentation, previous-milestone integration, the assembled/verified PDF book and one submission ZIP remain outstanding. Proposed wage inputs remain unavailable. See `../prototype-v1.md` for the exact eight-requirement tracker.
