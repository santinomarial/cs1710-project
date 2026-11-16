import OptChart from "./components/OptChart";
import EmployerTable from "./components/EmployerTable";
import EmployerDistribution from "./components/EmployerDistribution";
import IndustryChart from "./components/IndustryChart";
import EmployerComparison from "./components/EmployerComparison";
import WageProposal from "./components/WageProposal";
import OptEmployers from "./components/OptEmployers";
import {
  distribution,
  downloads,
  growth,
  primaryIndustries,
  latest,
  manifest,
  nfapUrl,
  number,
  optUrl,
  validation,
} from "./data";

function Chapter({ n, children, light = false }) {
  return (
    <div className={`chapter ${light ? "light" : ""}`}>
      <span>{n}</span>
      {children}
    </div>
  );
}

const sourceLinks = [
  ["IIE Open Doors", "Enrollment trends", optUrl, "open_doors_enrollment.xlsx"],
  [
    "IIE Open Doors",
    "Academic levels",
    "https://opendoorsdata.org/data/international-students/academic-level/",
    "open_doors_academic_level.xlsx",
  ],
  [
    "IIE Open Doors",
    "Fields of study",
    "https://opendoorsdata.org/data/international-students/fields-of-study/",
    "open_doors_fields.xlsx",
  ],
  [
    "ICE / SEVIS",
    "2024 annual report",
    "https://www.ice.gov/doclib/sevis/btn/25_0605_2024-sevis-btn.pdf",
    "sevis_2024.pdf",
  ],
  [
    "ICE / SEVIS",
    "2024 top 200 OPT / STEM OPT employers",
    "https://www.ice.gov/doclib/sevis/btn/2024/2024_Top200_Employers_OPT_STEM_OPT_Students.pdf",
    "2024_Top200_Employers_OPT_STEM_OPT_Students.pdf",
  ],
  [
    "USCIS",
    "H-1B Employer Data Hub",
    "https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub",
    "Employer Information (1).csv",
  ],
  ["NFAP", "FY2025 H-1B petitions report", nfapUrl, "nfap_fy2025.pdf"],
  [
    "BLS",
    "Occupational Outlook Handbook",
    "https://www.bls.gov/ooh/",
    "bls_ooh.html",
  ],
  [
    "Salaries by Ibis",
    "Selected H-1B wage summaries",
    "https://salaries.fru.dev/h1b",
    "fru_h1b.html",
  ],
  [
    "U.S. Department of Labor",
    "FY2025 Q4 LCA disclosure",
    "https://www.dol.gov/agencies/eta/foreign-labor/performance",
    "LCA_Disclosure_Data_FY2025_Q4.xlsx",
  ],
];

export default function App() {
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="site-header">
        <a className="brand" href="#top">
          <span className="brand-mark" aria-hidden="true">
            i.
          </span>
          <span>
            INTERNATIONAL
            <br />
            <b>TALENT IN AMERICA</b>
          </span>
        </a>
        <nav aria-label="Main navigation">
          <a href="#growth">The story</a>
          <a href="#employers">Employers</a>
          <a href="#comparison">Compare the evidence</a>
          <a href="#sources">Sources & method</a>
        </nav>
        <span className="edition">
          CS1710 <span> / </span> PROTOTYPE 3
        </span>
      </header>
      <main id="main">
        <section className="hero wrap" id="top">
          <div className="hero-copy">
            <div className="eyebrow">
              <span className="tiny-dot" /> A DATA STORY ABOUT WORK &
              OPPORTUNITY
            </div>
            <h1>
              Beyond the
              <br />
              <em>usual names.</em>
            </h1>
            <p className="hero-question">
              Is H-1B sponsorship limited to a few major technology companies?
            </p>
            <p className="hero-description">
              Follow the evidence from international education to the employers
              seeking global talent. A broader picture of America’s workforce
              comes into view.
            </p>
            <a className="button primary" href="#growth">
              Explore the story <span>↓</span>
            </a>
            <div className="hero-meta">
              HARVARD CS1710 <span>·</span> DATA VISUALIZATION <span>·</span>{" "}
              FALL 2026
            </div>
          </div>
          <aside className="hero-index" aria-label="Evidence at a glance">
            <div className="index-heading">
              <span>THE EVIDENCE</span>
              <span>01—03</span>
            </div>
            <a href="#growth" className="evidence-item">
              <span className="evidence-number">01 / EDUCATION</span>
              <strong>{number(latest.opt_students)}</strong>
              <p>students on Optional Practical Training</p>
              <div>
                Open Doors · {latest.academic_year} <span>↗</span>
              </div>
            </a>
            <a href="#employers" className="evidence-item">
              <span className="evidence-number">02 / EMPLOYERS</span>
              <strong>
                {number(distribution.employers_with_initial_approval)}
              </strong>
              <p>named employer groups with initial H-1B approvals</p>
              <div>
                USCIS export · FY2025 <span>↗</span>
              </div>
            </a>
            <a href="#industries" className="evidence-item">
              <span className="evidence-number">03 / INDUSTRIES</span>
              <strong>
                {primaryIndustries.filter(d => d.naics_code).length}
                <span className="number-qualifier">categories</span>
              </strong>
              <p>reported industry sectors with initial approvals</p>
              <div>
                USCIS export · FY2025 <span>↗</span>
              </div>
            </a>
            <p className="index-note">
              Different populations. Different reporting periods.
              <br />
              Read together, with care.
            </p>
          </aside>
        </section>
        <div className="story-strip">
          <div className="wrap">
            <span>THE QUESTION</span>
            <p>
              Who participates, where do they work, and what can the data
              actually tell us?
            </p>
            <span aria-hidden="true">↓</span>
          </div>
        </div>

        <nav className="chapter-nav wrap" aria-label="Story chapters">
          <a href="#growth"><span>01</span> OPT growth</a><a href="#opt-employers"><span>02</span> OPT employers</a><a href="#employers"><span>03</span> Sponsorship</a><a href="#industries"><span>04</span> Industries</a><a href="#comparison"><span>05</span> Compare</a><a href="#wages"><span>06</span> Wages</a><a href="#implications"><span>07</span> Implications</a>
        </nav>

        <section className="wrap section" id="growth">
          <Chapter n="01">FROM CAMPUS TO THE WORKFORCE</Chapter>
          <div className="section-intro">
            <h2>OPT participation<br /><em>rose {growth.toFixed(1)}% in a year.</em></h2>
            <p>In {latest.academic_year}, Open Doors counted {number(latest.opt_students)} students on OPT within its total of {number(latest.total_international_students)} international students.</p>
          </div>
          <OptChart />
          <details className="section-methods"><summary>What OPT measures & coverage limits</summary><p>OPT is work authorization for eligible F-1 students. Open Doors reports OPT participants separately from enrolled students; these are not H-1B approvals. Its international-student totals included students studying online outside the U.S. in 2020/21–2022/23. Long-run comparisons span reporting changes. <a href="#sources">See methodology.</a></p></details>
        </section>

        <section className="section soft-section" id="opt-employers">
          <div className="wrap">
            <Chapter n="02">WHERE OPT PARTICIPANTS WORK</Chapter>
            <div className="section-intro">
              <h2>Companies and campuses.<br /><em>Both employ OPT participants.</em></h2>
              <p>Amazon leads ICE’s calendar-2024 top-200 employer list, which also includes universities and other organizations.</p>
            </div>
            <OptEmployers />
          </div>
        </section>

        <section className="dark-section section" id="employers">
          <div className="wrap">
            <Chapter n="03" light>
              THE PICTURE GETS BIGGER
            </Chapter>
            <div className="section-intro">
              <h2>Small sponsors.<br /><em>Broad reach.</em></h2>
              <p>{distribution.employer_share_1_to_10_initial_approvals}% of the {number(distribution.employers_with_initial_approval)} named employer groups with initial approvals in FY2025 had ten or fewer.</p>
            </div>
            <EmployerDistribution />
            <EmployerTable />
          </div>
        </section>

        <section className="wrap section" id="industries">
          <Chapter n="04">ACROSS THE ECONOMY</Chapter>
          <div className="section-intro">
            <h2>Sponsorship spans<br /><em>20 industry sectors.</em></h2>
            <p>Professional, scientific and technical services lead FY2025 initial approvals; education, manufacturing and health care also have a substantial presence.</p>
          </div>
          <IndustryChart />
        </section>

        <section className="soft-section section" id="comparison">
          <div className="wrap">
            <Chapter n="05">TWO DATASETS, ONE EMPLOYER LENS</Chapter>
            <div className="section-intro">
              <h2>Shared names.<br /><em>Different measures.</em></h2>
              <p>For 47 conservatively matched names, compare calendar-2024 OPT/STEM OPT participation with FY2025 initial H-1B approvals.</p>
            </div>
            <EmployerComparison />
          </div>
        </section>

        <section className="wrap section" id="wages">
          <Chapter n="06">WHAT THE WAGE DATA COULD SAY</Chapter>
          <div className="section-intro">
            <h2>The wage question<br /><em>remains open.</em></h2>
            <p>Comparing offered H-1B wages with occupational medians requires matched DOL/BLS data that are not yet available.</p>
          </div>
          <WageProposal />
        </section>

        <section className="wrap section conclusion" id="implications">
          <Chapter n="07">IMPLICATIONS FOR POLICY</Chapter>
          <div className="section-intro">
            <h2>
              See the breadth.
              <br />
              <em>Respect the limits.</em>
            </h2>
            <div>
              <p>OPT and H-1B policy discussions should account for employers across sectors, including universities, hospitals and manufacturers.</p>
              <p className="small">These aggregate data do not track individual OPT-to-H-1B transitions or establish the effects of policy changes.</p>
              <a className="button outline" href="#sources">
                Inspect the evidence <span>↓</span>
              </a>
            </div>
          </div>
        </section>

        <section className="sources-section section" id="sources">
          <div className="wrap">
            <Chapter n="08">DATA SOURCES & METHODOLOGY</Chapter>
            <div className="sources-heading">
              <h2>Open to inspection.</h2>
              <p>
                Prototype 3 · Source retrieval attempted October 25, 2026.
                <br />
                Every displayed statistic traces to a downloaded source.
              </p>
            </div>
            <div className="sources-grid">
              {sourceLinks.map(([publisher, title, url, file]) => {
                const record = manifest.find((d) => d.file === file);
                const available = ["downloaded", "provided_local"].includes(record?.status);
                return (
                  <a className="source-card" key={file} href={url}>
                    <div>
                      <span className="eyebrow">{publisher}</span>
                      <span aria-hidden="true">↗</span>
                    </div>
                    <h3>{title}</h3>
                    <span
                      className={`source-status ${available ? "available" : ""}`}
                    >
                      {available
                        ? record.status === "provided_local"
                          ? "User-provided original · verified checksum"
                          : file === "fru_h1b.html"
                          ? "Archived reference only"
                          : "Original downloaded"
                        : "Download blocked · HTTP 403"}
                    </span>
                  </a>
                );
              })}
            </div>
            <details className="method-detail">
              <summary>
                Definitions, coverage & limitations <span>+</span>
              </summary>
              <ul>
                <li>
                  Open Doors uses academic years. USCIS and NFAP use federal fiscal
                  years; FY2025 runs October 2024–September 2025. ICE employer records
                  cover calendar 2024. These periods are not interchangeable.
                </li>
                <li>
                  Initial H-1B approvals include new and concurrent employment.
                  Continuing approvals include extensions, amendments, and
                  changes of employer. Approval counts do not equal unique
                  workers.
                </li>
                <li>
                  Names retain the source spelling. Comparison keys normalize
                  case, spacing, punctuation, and ampersands; no fuzzy matching
                  or parent-company mergers have been applied. NFAP’s own entity
                  aggregation remains part of its source methodology.
                </li>
                <li>
                  Missing observations stay missing. Blank values are not zero.
                  The fields-of-study extract uses only broad categories,
                  avoiding double-counting their detailed subcategories.
                </li>
                {validation.warnings.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            </details>
            <details className="method-detail">
              <summary>
                Download the cleaned datasets{" "}
                <span>{downloads.length} CSVs</span>
              </summary>
              <div className="download-list">
                {downloads.map((d) => (
                  <a key={d.name} href={d.url} download={d.name}>
                    <span>{d.name}</span>
                    <span>{validation.datasets[d.name].rows} rows ↓</span>
                  </a>
                ))}
              </div>
              <p className="small">
                Unavailable datasets are omitted, not populated with
                placeholders. The repository includes original downloads,
                checksums, cleaning scripts, and validation tests.
              </p>
            </details>
            <div className="prototype-note">
              <span className="tiny-dot" />
              <p>
                <b>A foundation for further exploration.</b> The OPT trend and
                FY2025 H-1B employer distribution chart are implemented using
                processed source data, alongside the industry ranking and employer comparison.
                The wage comparison remains a proposed design awaiting matched DOL/BLS inputs.
              </p>
            </div>
          </div>
        </section>
      </main>
      <footer className="wrap">
        <a className="footer-brand" href="#top">
          International talent in America <span>↑</span>
        </a>
        <p>A team project for Harvard CS1710 · Fall 2026</p>
      </footer>
    </>
  );
}
