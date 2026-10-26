# Draft 01 — H-1B initial approvals by industry

**Status:** source-backed static design; interactions proposed. See [mockup](01-industry-ranked-bars.png) and PDF pages 1–2. No D3 implementation was added.

## Question and rationale

How are FY2025 initial H-1B approvals distributed across employer industries? A ranked horizontal bar chart gives all sectors a common zero baseline and leaves room for long industry names. Education, health care, manufacturing and finance are visible alongside information and professional services. Industry does not identify an employer's occupation or prove that it is or is not a technology company; the title and annotation avoid making that inference.

## Source and visual mapping

Input: `data/processed/uscis_fy2025_industries.csv`, derived from the preserved official USCIS FY2025 Employer Data Hub export `data/raw/Employer Information (1).csv`. FY2025 runs October 1, 2024–September 30, 2025. See [USCIS reconciliation](../uscis-fy2025-reconciliation.md) and [data guide](../../data/README.md) for provenance, category definitions and limitations.

| Element | Mapping |
| --- | --- |
| One row | A reported NAICS industry sector; use `naics_code` as the stable key |
| Y position | Descending `initial_approvals`, with a stable NAICS tie break; optional alphabetical order |
| X position / bar length | `initial_approvals`, linear scale starting at zero; axis says “Initial approvals (petitions)” |
| Alternative X measure | `100 × initial_approvals / 114804`; national-share denominator includes missing industry and does not change with search |
| Labels | Industry name and exact formatted count; shortened labels in the desktop draft reveal the complete source label on focus/hover and in the table |
| Selection | Terra bar and tinted full-row background, reinforced by a “Selected industry” label |
| Detail panel | Full label, NAICS, initial total, national share, `new_employment_approvals`, `new_concurrent_approvals`, fiscal period and source |
| Missing industry | Separate persistent card/row for 2,215 approvals, outside the 20-sector ranking |

Initial approvals are **new employment + new concurrent employment**, not continuing categories and not unique workers. The supplied export totals **114,804**, comprising 112,589 in reported sectors and 2,215 without industry. Do not substitute NFAP's 114,806; the two-approval discrepancy remains unresolved. Do not classify missing industry by guessing from employer names.

The main mockup shows the largest 10 of 20 reported sectors. Educational Services is pinned: **15,966 initial approvals**, **13.9%** of the national total, comprising **15,763 new employment + 203 concurrent**. These are actual processed values. PDF page 2 illustrates the percentage encoding on three real sectors with an explicitly unchanged denominator; it is an interaction-state excerpt, not a second full chart.

## Planned interactions and states

| Action | Result |
| --- | --- |
| Hover or keyboard focus a row | Preview the complete sector name, NAICS, count, share and two initial components. A pinned selection is restored when preview ends. |
| Click, tap or Enter | Pin the sector in the detail panel. Escape or “Clear selection” clears it. Sorting retains selection by NAICS. |
| Switch count / national share | Relabel axis and data labels. Keep the zero baseline, exact source counts in detail and fixed national denominator. |
| Search | Match full sector name or NAICS. Search applies to all 20 sectors, overriding the Top 10 visibility limit so small sectors are discoverable. Show visible count; no match produces a message and Reset. |
| Top 10 / All 20 | Expand chart height for all sectors, with scroll where needed. Never turn the unshown sectors into an unlabeled residual. |
| Sort | Largest first or alphabetical; preserve stable keys and any pinned selection. Respect reduced-motion settings. |
| View data / source | Expose all 20 sectors and the missing category in an accessible table, with original CSV and source references. |

No pie chart, broken axis or logarithmic bar lengths: small sectors keep honest proportions and remain inspectable through exact labels. Filters alter visible rows, not the national meaning of the percentages. The persistent missing-industry card remains visible even when search finds no known sector.

## Responsive and accessible behavior

On wide screens, use the chart and detail side by side. On narrow screens, wrap each industry label above its bar, keep an explicit zero and readable ticks, and stack detail below the chart. Full rows provide touch targets at least 44 CSS px high. Focus and hover expose equivalent content; use native controls, a named chart region, visible focus, a textual table and an announced selection status. Do not rely on color alone or require scrolling a tooltip to find caveats.

## Acceptance before future implementation

- Verify all 20 sector rows plus the missing category, with exact sum 114,804 and no continuing approvals.
- Verify bars and displayed shares against the CSV, including the Education example and rounding.
- Confirm that search reaches a sector outside the initial Top 10 and that selection survives sorting.
- Confirm missing industry remains in the denominator and never appears as zero or a fabricated classification.
- Check full names, keyboard selection, empty search, touch layout and the source-value table.

This design contributes one of the three additional drafts for requirement 4. Its visual and interaction specification is ready for the process book; it does not increase the number of functional D3 views.
