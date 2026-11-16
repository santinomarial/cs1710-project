# Prototype 3: Week 12 think-aloud feedback and verification

Implemented locally on November 15, 2026 for **Prototype 3**, as confirmed by the team. Source: the three-page **Process Book CS1710 (11).pdf**, supplied by the team. This document records the website changes; it does not replace or edit the source PDF or the submission archive.

## Decisions implemented

| Feedback from the study | Website change | Implementation |
| --- | --- | --- |
| OPT interaction felt laggy. | Full-height year targets let users inspect the line without aiming at tiny circles. Tap/click selects a year; arrow keys and Home/End navigate observed years. Geometry is memoized separately from the readout, and the static plot is a memoized React component. Container resize updates are rounded and coalesced into animation frames. | `src/components/OptChart.jsx`, `src/optLayout.js`, `src/components/ChartPrimitives.jsx` |
| Employer percentages and units were unclear. | Buttons now say “% of employer groups” and “% of approvals.” A changing explanation names each numerator and denominator. Tooltips show both counts and shares; clicking or pressing Enter pins a row. Approved petitions are explicitly distinguished from applications filed and unique workers. | `src/components/EmployerDistribution.jsx` |
| Explain the one-approval pattern explicitly. | Paired callout: **62.5% of named groups** had one initial approval and accounted for **16.0% of initial approvals** in the chart population. Both percentages are read from the validated processed distribution, with their counts shown underneath. | `src/components/EmployerDistribution.jsx`, `tests/distribution.test.js` |
| Make titles takeaway-oriented and add short summaries. | Each story section leads with a concise finding or question and a short summary. Examples: “OPT participation rose 21.2% in a year,” “Sponsorship spans 20 industry sectors,” and “Shared names. Different measures.” The wage section clearly remains an unanswered proposal. | `src/App.jsx` and chart headings |
| Cut repetition and distracting controls. | Removed repeated industry context from the employer chart and duplicate section introductions. Industry bars remain ranked, with the alphabetical-order control removed. Comparison search/name filters and detailed name evidence are expandable; point-shape legend, axis controls, plotted counts and employer selector remain visible. Extended methods are expandable while essential population limitations stay visible. | `src/App.jsx`, `IndustryChart.jsx`, `EmployerComparison.jsx`, `WageProposal.jsx` |
| Put source, period and unit next to every chart. | Shared metadata rows accompany OPT, employer distribution, industry, employer comparison and the ICE employer list. The comparison lists both source periods separately. Wage metadata explicitly labels sources and annual-USD units as proposed, with the BLS vintage undecided. | `ChartMeta` in `src/components/ChartPrimitives.jsx` and all visualization components |

## Numerical checks and preserved definitions

- Exactly-one bin: **18,343 / 29,350 employer groups = 62.5%**, rounded; **18,343 / 114,798 initial approvals = 16.0%**, rounded. These are different denominators.
- The distribution excludes **6 initial approvals in 11 unnamed records**. The full export and industry chart still total **114,804**. The unresolved two-approval difference from NFAP’s 114,806 remains documented.
- Initial approvals remain new employment plus new concurrent employment; continuing categories remain excluded. Grouping still uses exact reported names and partial tax suffixes, without claiming unique legal employers.
- OPT ends at **294,253** in academic year **2024/25**, up **21.2%** from 242,782. Recent/full ranges retain **20/46** actual observations. No new observations or interpolated counts were introduced.
- Comparison remains **47 accepted name pairs**, excluding **153** ICE names. Disabling case/spacing matches leaves **19** points. STEM OPT has **46** plottable values: Carnegie Mellon’s missing value remains missing, not zero. Its detail panel retains 416 combined participants and 46 initial approvals.
- Different populations, calendar/academic/fiscal periods, source-specific combined participation, and the absence of individual transitions or verified entity matches remain explicit. No conversion rates were introduced.

## Verification

- `npm test`: **28 Python data tests and 19 frontend tests passed**. New regressions cover the two callout denominators and OPT hit-target coverage at phone/desktop widths, both date ranges, and sparse observed years.
- `npm run build`: passed. The existing nonblocking bundle-size warning remains (about 610 kB minified / 131 kB gzip).
- `npm run test:deployment -- http://127.0.0.1:4173/cs1710-project/`: passed. All **21 production files** served HTTP 200 and matched their build bytes; **17 CSV downloads** matched processed originals and used the production base path.
- Browser checks: pointer movement across the OPT plot updates the readout away from the line; tap/click and arrow/Home keyboard navigation work; date range and data table work. Employer measures change axis values and explicit denominators; preview tooltips, keyboard selection and pinned details work. Industry count/share, search, all-sector control and selection work. Comparison metric switching, missing values, match filters, search, reset, employer selector and expandable name evidence work.
- Responsive checks: no document-level horizontal overflow at **1440, 768, 390 or 320 px**. Desktop and phone screenshots were visually inspected, including chart labels, metadata, tooltips and callouts. Browser warning/error logs were empty during checks.
- SHA-256 comparison of **53 protected files** found **zero changes** across the data directory, pipeline/scripts, existing visualization drafts and root process-book PDF. The source PDF and existing submission archive were not edited.
- `git diff --check`: passed. No commit, push or deployment was performed.

The interaction changes address the mechanisms found during code inspection: small hit targets and repeated geometry work during year inspection. **No before/after latency benchmark or new participant study is claimed.** Re-run the think-aloud task to assess perceived smoothness, comprehension of the two percentages, and discoverability of the expandable filters.

## Screenshots

All screenshots are from the local production build, not mockups. Desktop viewport: 1440 px; phone viewport: 390 px. Captures include whole sections, so their heights vary.

| View | Desktop | Phone |
| --- | --- | --- |
| OPT growth | [Screenshot](screenshots/think-aloud/desktop-growth.png) | [Screenshot](screenshots/think-aloud/mobile-growth.png) |
| Employer distribution | [Screenshot](screenshots/think-aloud/desktop-employers.png) | [Screenshot](screenshots/think-aloud/mobile-employers.png) |
| Employer comparison | [Screenshot](screenshots/think-aloud/desktop-comparison.png) | [Screenshot](screenshots/think-aloud/mobile-comparison.png) |
| Wage proposal | [Screenshot](screenshots/think-aloud/desktop-wages.png) | [Screenshot](screenshots/think-aloud/mobile-wages.png) |

## Course-deliverable scope

This revision improves the existing four functional charts, storytelling and interaction design. It adds no implemented visualization and leaves the three unimplemented drafts (wages, geography and fields of study) intact. The supplied feedback PDF documents the earlier think-aloud study; incorporating the resulting website revisions into the final process book and repeating the evaluation are separate remaining steps. Earlier Prototype V1 packaging/status notes are historical and were not re-audited in this feedback task.
