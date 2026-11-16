# Prototype 3 progress

The team confirmed that the Week 12 think-aloud revisions belong to **Prototype 3**. This tracker uses the four requirements supplied on November 15, 2026; the earlier eight-item V1 rubric is historical.

| Requirement | Current status | Evidence and remaining work |
| --- | --- | --- |
| Complete data pipeline: scraping and cleaning finished using real datasets | Complete for the four implemented charts; incomplete for the full proposed source scope | Seventeen processed CSVs, reproducible Python extraction/cleaning, provenance, checksums and 28 passing data tests. IIE, USCIS and ICE employer data are integrated. Matched DOL/BLS wage inputs remain unavailable. Some files were supplied manually, not successfully scraped. Do not claim all planned acquisition is finished. |
| Functional D3 visualizations: all implemented and interactive, ready for an unfamiliar tester | Four current charts implemented and browser-tested; all proposed views not complete | OPT trend, H-1B employer distribution, industry ranking and employer comparison support interactive exploration. Nineteen frontend tests pass; desktop/mobile interactions were checked. Wages remains a placeholder, while geography and fields of study remain unimplemented drafts. Implement any retained proposals or explicitly establish a reduced final visualization scope before marking the broad requirement complete. Repeat think-aloud testing after the revisions. |
| Website structure: fully implemented layout with clear design vision | Complete for the current website | React/Vite page, coherent typography/palette, chapter navigation, chart cards, details, source metadata and responsive layouts. No document-level overflow at 1440, 768, 390 or 320 px in the latest review. The wage section intentionally remains a proposed visualization. |
| Clear storytelling: evident narrative and message | Implemented; earlier study supports comprehension | The question about sponsorship beyond major technology firms leads through OPT, employers, industries and the linked comparison to policy implications. The supplied study reports that testers understood the core message. Prototype 3 adds takeaway headlines, short summaries and the 62.5%/16.0% comparison. The revised version has not undergone a new participant study. |

## Process-book documentation

The existing 50-page `Process Book CS1710 (10).pdf` documents data collection/cleaning on pages 40–41, four functional charts on page 41, layout/storytelling on pages 40–42, and remaining limitations on page 43. These are explicitly Prototype V1 entries, not a current Prototype 3 completion statement.

The separately supplied three-page `Process Book CS1710 (11).pdf` contains Week 12 think-aloud findings and six planned changes. The changes have now been implemented in code, but neither PDF has been edited to record their completion.

The [feedback implementation report](think-aloud-feedback.md) provides the changes, rationale, numerical checks, test results and desktop/mobile screenshots to incorporate into the next complete process-book revision. The six decisions, implementation evidence, current limitations, and post-revision evaluation status should appear under a **Prototype 3** milestone.

## Submission limits

- Do not describe the wage comparison as functional or the missing wage pipeline as complete.
- Keep geography/fields drafts identified as unimplemented until scope or implementation changes.
- Update the complete process-book PDF with this milestone; repository Markdown is supporting documentation, not the PDF deliverable.
- Local changes are not a new published deployment or updated submission ZIP.
