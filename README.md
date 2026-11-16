# International talent in America

A Harvard CS1710 team project investigating international students, Optional Practical Training (OPT), H-1B employers, and offered wages in the United States. The primary audience is policymakers; university administrators are the secondary audience.

**Current scope:** Prototype 3, including the Week 12 think-aloud revisions. Four interactive D3 charts are implemented using a validated real-data pipeline. Wage comparison remains a proposal awaiting matched DOL/BLS inputs; geography and fields-of-study views remain design drafts. See the [Prototype 3 tracker](docs/prototype-3.md) for current requirement status and [feedback report](docs/think-aloud-feedback.md) for tests and screenshots. Process-book PDFs and submission ZIPs are prepared separately from the website release. Pushes to `main` run the tests and GitHub Pages deployment workflow; check its result before treating a revision as published.

## Get started

Requires Node.js 22.12+ (Node 24 recommended), npm, and Python 3.11+. The checked-in processed data lets the website run without Python or network access to data providers.

```sh
npm ci
npm run dev
```

Open the local URL printed by Vite. To verify the production build:

```sh
npm run build
npm run preview
```

The build writes `dist/`. Vite uses the production base `/cs1710-project/`; open the full local preview URL, normally `http://localhost:4173/cs1710-project/`. Chart data and all seventeen CSV downloads are managed by Vite, including their hashed, base-prefixed asset URLs.

## Reproduce the data

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/download.py
python scripts/pipeline.py
python -m unittest discover -s tests -v
```

`download.py` downloads public original files, records failures without bypassing restrictions, and preserves checksummed cached downloads. It retries blocked sources on subsequent runs. `--refresh` explicitly re-downloads managed URL sources while preserving user-provided originals; upstream revisions may require parser review. The scripts are pinned to the identified source editions, not to an automatically changing “latest” year.

For an offline rerun, omit the download step. The six consumed original files are included in `data/raw/`. Cleaning verifies the manifest checksums, extracts tables, validates them, and writes seventeen CSVs plus four JSON reports. Processing does not fetch data from the web. Missing required originals or unexpected table formats fail visibly; blocked, unsupported datasets are not fabricated. See [the data guide](data/README.md) for exact manual downloads and remaining ingestion work.

The `data:download`, `data:clean`, and `test:data` npm scripts are shortcuts using `python3`; activate the Python virtual environment first.

## Website structure

| Section | Current implementation |
| --- | --- |
| Hero | Main question, source-derived evidence, navigation |
| International students and OPT growth | Working D3 line chart; academic-year range selector, point inspection, accessible table |
| OPT / STEM OPT employers | Source-backed leading-employer overview and searchable 200-row ICE table, with independent combined/OPT/STEM counts |
| H-1B employer distribution | Interactive D3 chart from the supplied USCIS FY2025 export; employer/approval share toggle, seven disjoint bins, hover/focus/tap details, data table and explicit identity limits; separate historical NFAP employer table |
| Industry breakdown | Interactive D3 ranked bars from USCIS: count/share toggle, search, all 20 sectors, selection detail and missing-industry category |
| Employer comparison | Interactive D3 scatterplot for 47 accepted name pairs; source evidence panel, name-format filters, metric switching, missingness and period caveats |
| Wage comparison | Approved proposal styling, explicitly awaiting matched DOL/BLS data; no salary marks or invented values |
| Policy implications | Audience-specific questions and limits on causal / transition claims |
| Sources and methodology | Source status, limitations, and seventeen CSV download links |

The story asks whether H-1B employment is concentrated among a handful of major technology companies, then broadens the view through education, employers, and industries. It distinguishes OPT participation from H-1B approvals. The wage argument is withheld until comparable records are available.

`src/data.js` parses the processed CSVs with D3 and exposes typed records. Vite bundles these same files for download; there is no duplicated public data directory to synchronize. D3 owns the chart scales, category layout, and line-path calculation; React owns rendering and interaction state. The ICE overview remains an HTML table, and the wage proposal remains clearly unavailable. Name-format categories describe the preserved strings of already accepted pairs; they are not a new matching algorithm.

## Files

```text
data/raw/                 Original XLSX/PDF/HTML/UTF-16 TSV files and retrieval manifest
data/processed/           Seventeen CSVs, source notes and validation/reconciliation JSON
data/README.md            Provenance, definitions, schemas, blockers, reproduction
scripts/download.py      Public-source downloader, cache, SHA-256 audit
scripts/pipeline.py      Deterministic extraction and validation
scripts/uscis.py         Primary USCIS parsing, grouping, distribution and reconciliation
scripts/ice.py           ICE PDF extraction and conservative employer comparison
tests/test_ice.py        Source-cell, missingness, ambiguity and reproduction tests
docs/ice-2024-employers.md  Complete ICE extraction and match audit
tests/test_uscis.py      Raw-source, aggregation, reproduction and failure-case tests
docs/uscis-fy2025-reconciliation.md  Full reconciliation and new dataset schemas
tests/test_pipeline.py   Cleaning regressions and failure-case tests
src/App.jsx              Eight-part narrative plus sources
src/data.js              CSV parsing and derived display values
src/components/          Four D3 charts, ICE and NFAP tables, wage proposal
src/distribution.js      Source-aware distribution parsing and chart scale
src/chartData.js         Validated new chart parsing, filtering and missingness
tests/*.test.js          Fifteen frontend data and scale tests
docs/data-audit.md       Eight-file schema, provenance, period, and limitation audit
src/styles.css           Existing layout, print and reduced-motion rules
src/story.css            Approved palette, shared chart styling and responsive design
docs/website-polish-verification.md  Latest tests, browser checks and screenshots
docs/prototype-v1.md      Exact course rubric and outstanding deliverables
docs/verification.md     Verification record and known limits
docs/screenshots/        Desktop and mobile review images
```

## Quality and next phase

The pipeline checks nonempty outputs, unique keys, nonnegative integer counts, source checksums, cross-workbook OPT values, source coverage, and selected independently inspected records. Tests also reject duplicate keys and corrupted records. See [verification](docs/verification.md) for the checks actually run.

Run `npm run test:charts` for all nineteen frontend tests, including industry denominators, conservative name categories, search and missing STEM behavior. The H-1B chart uses exact counts from the processed USCIS distribution CSV: 29,350 named groups and 114,798 initial approvals. Eleven unnamed source records remain separate, with their six initial approvals excluded from the chart but retained in national totals. The supplied 114,804 total differs from NFAP by two; see the [reconciliation report](docs/uscis-fy2025-reconciliation.md).

Before submission, review the unavailable proposed inputs and assemble previous milestones and contributor names into a reviewed PDF process book. Three currently unimplemented designs are ready: wage comparison, geographic H-1B sponsorship, and fields of study. Include their PNGs and specifications in the actual process book to finish requirement 4; the industry and novel employer-comparison drafts are now implemented and are retained as design history. Then package code and the process book into a single ZIP. The [Prototype V1 tracker](docs/prototype-v1.md) records exact statuses without claiming those deliverables exist.

The ICE employer source is now integrated with its original PDF, checksum, page references, missing cells and counting caveat preserved. See the [ICE audit](docs/ice-2024-employers.md) for match exclusions, source limitations and the pending retrieval-date confirmation. No visualization source files were changed for this data-only phase.

The subsequent website phase implements two approved designs while leaving validated data and original chart calculations unchanged. See [website verification and screenshots](docs/website-polish-verification.md). The production build passes; the compressed main JavaScript bundle is about 132 kB, with a non-failing Vite warning about its uncompressed size. Those results predate the GitHub Pages deployment phase; see the deployment instructions and verification record below.


## GitHub Pages deployment

**Public website URL:** [https://santinomarial.github.io/cs1710-project/](https://santinomarial.github.io/cs1710-project/)

**Repository:** [santinomarial/cs1710-project](https://github.com/santinomarial/cs1710-project) · **Deployment branch:** `main`.

The URL above is the configured publishing destination, not proof that the latest deployment is live. Check the [Actions runs](https://github.com/santinomarial/cs1710-project/actions/workflows/deploy-pages.yml), the `github-pages` environment and the public URL. The local verification record is [docs/deployment-verification.md](docs/deployment-verification.md).

### One-time repository settings

1. In [Settings → Pages](https://github.com/santinomarial/cs1710-project/settings/pages), set **Build and deployment → Source → GitHub Actions**. Do not select a branch-based Jekyll build or a `docs/` publishing folder.
2. In **Settings → Actions → General**, enable Actions and permit the official `actions/*` actions used by the workflow. Keep the repository public for GitHub Free Pages hosting. No custom domain is configured.
3. If the `github-pages` environment has deployment restrictions, permit `main`. If required reviewers are configured, an authorized reviewer must approve the deployment. The workflow supplies `pages: write` and `id-token: write` only to its deployment job; repository-wide write-token defaults are unnecessary.
4. No personal token or API key is needed in repository secrets. GitHub provides the workflow token and Pages deployment identity automatically. A local OAuth credential used to push a new workflow needs the `workflow` scope; if GitHub rejects the push for that reason, run `gh auth refresh -h github.com -s workflow`, finish the browser authorization, then retry `git push -u origin main`.

### Automatic deployments

`.github/workflows/deploy-pages.yml` runs on pushes to `main` and can also be started with **Actions → Test and deploy GitHub Pages → Run workflow**. It uses pinned official action commits, Node 24 and Python 3.12, installs locked dependencies, runs all Python and frontend tests, builds Vite, and verifies the output before publishing. A failing test or build prevents the deployment job.

Only **`dist/`** is uploaded to Pages. Do not change the upload path to the repository root. Raw XLSX/PDF/HTML/USCIS originals are public reference sources retained in Git for provenance and the source-backed Python tests; they are not copied to the website artifact. Existing processed CSV download links remain public, including USCIS petitioner-level data and publicly released partial tax-ID suffixes. These are official employer/petition records, not individual beneficiary records. Documentation and local temporary files are not deployed.

The site uses section anchors, so no SPA history fallback or generated `404.html` is needed. Do not remove the project base or replace Vite-managed imports with root-relative `/assets/` or `/data/` paths. If renaming the GitHub repository, update both `vite.config.js` and the deployment verifier's base path.

### Verify a release locally

Use the Python environment from “Reproduce the data” above, then run:

```sh
npm ci
npm test
npm run build
npm run test:deployment
npm run preview
```

In a second terminal, verify every built file over HTTP:

```sh
npm run test:deployment -- http://localhost:4173/cs1710-project/
```

After a successful deployment, the same command can verify the public URL against the matching local build:

```sh
npm run test:deployment -- https://santinomarial.github.io/cs1710-project/
```

The verifier checks the base-prefixed HTML/runtime asset paths, all seventeen CSV download files against their original processed bytes, expected artifact types, common credential signatures, and (when a URL is supplied) HTTP status, file contents and JavaScript/CSS MIME types. It rejects raw archives, source maps and unexpected file types. The Pages artifact intentionally contains no `.env`, private keys, dependency directories, raw archives, process-book assets or cleaning scripts. The verifier is a focused deployment check, not a guarantee against every possible form of sensitive content.
