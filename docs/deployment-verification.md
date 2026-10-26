# GitHub Pages deployment verification

Prepared October 25, 2026 (America/New_York).

Repository: https://github.com/santinomarial/cs1710-project

Publishing destination: https://santinomarial.github.io/cs1710-project/

## Configuration

- Vite base: `/cs1710-project/`.
- All 17 existing CSV downloads are emitted as hashed files (`assetsInlineLimit: 0`); their bytes remain identical to `data/processed/`.
- The existing root favicon and entrypoint references in `index.html` are rewritten correctly by Vite; no chart/source component required changes.
- `.github/workflows/deploy-pages.yml` tests and builds on `main` pushes or manual dispatch, then uploads **only `dist/`** and deploys using the `github-pages` environment. Deployment depends on the successful build job.
- Official action commits are pinned. Node 24 and Python 3.12 are selected. Permissions are scoped: content read for build; Pages write and OIDC for deploy. No personal access token is stored in the workflow.
- The remote repository was empty and the local folder had no Git history. The initial publication therefore includes the reviewed existing project as well as deployment configuration. A repository-local GitHub noreply author address avoids exposing the configured personal email in commit metadata.

## Checks completed before publication

| Check | Result |
| --- | --- |
| `npm ci` | Passed; npm reported zero known vulnerabilities |
| Full Python suite | 28 tests passed, including original-source and reproducibility checks |
| Full frontend suite | 15 tests passed |
| Production build | Passed |
| `actionlint .github/workflows/deploy-pages.yml` | Passed |
| `npm run test:deployment` | Passed: 21 expected build files, 17 byte-identical CSVs, base-prefixed runtime/download and HTML paths |
| HTTP production preview verification | All 21 files returned 200 with byte-identical contents at `http://127.0.0.1:4173/cs1710-project/`; JS/CSS MIME types checked |
| Browser production preview | All four charts rendered; full-history OPT range, approval-share toggle, national industry-share toggle and STEM comparison mode worked |
| Missing-value browser check | STEM mode showed 46/47 plotted and explicitly retained Carnegie Mellon's missing value as missing |
| Browser logs and download paths | No captured errors/warnings; all 17 download links used `/cs1710-project/assets/` |
| Preservation | 51 website/source-data/public/cleaning files matched their pre-deployment SHA-256 hashes |

The existing main-bundle size warning remains nonfatal (about 610 kB uncompressed, 131 kB gzip). No code splitting, visual design, chart calculations or source datasets were changed for deployment.

## Publication review

Reviewed the candidate file inventory and scanned text files (including the UTF-16 source) for recognizable GitHub/OpenAI/AWS credentials and private-key headers; no matches were detected. `.env` files, common private-key formats, local npm/netrc configuration, dependencies, caches, build output and temporary work are ignored by Git. This targeted scan does not claim to detect every possible secret format.

The Pages artifact contains only HTML, JavaScript, CSS, the favicon and the 17 intentional processed CSV downloads. No raw archives, cleaning scripts, documentation, screenshots, source maps or private configuration are uploaded to Pages. Website provenance metadata used by the existing source-status cards remains bundled intentionally.

The public repository retains the original public reference sources needed for checksum validation, reproducibility and the full Python test suite. Those reference files are not credentials or individual beneficiary records. USCIS petitioner names, addresses and partial tax-ID suffixes are already public source fields; their existing processed downloads are intentionally preserved. Unnecessary local work (`tmp/`, environments, dependencies and generated `dist/`) is excluded from Git.

## Publication status

Local configuration, tests, build, preview and artifact review are complete. At the time this pre-push record was written, no GitHub deployment or public-URL success was asserted. Consult the repository's Actions run and environment for the current remote status; the conversation reports the actual push result. To independently verify a deployed release against its matching local build:

```sh
npm run test:deployment -- https://santinomarial.github.io/cs1710-project/
```

The [README deployment section](../README.md#github-pages-deployment) documents repository settings, authentication recovery and deployment commands. GitHub Pages must use **GitHub Actions** as its source. Deployment configuration follows the [Vite project-site guidance](https://vite.dev/guide/static-deploy.html#github-pages) and [GitHub custom-workflow requirements](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
