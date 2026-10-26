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
          CS1710 <span> / </span> PROTOTYPE V1
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
            <h2>
              A growing role for
              <br />
              <em>post-graduation work.</em>
            </h2>
            <div>
              <p>
                In {latest.academic_year}, Open Doors counted{" "}
                {number(latest.total_international_students)} international
                students, including {number(latest.opt_students)} on OPT. OPT
                participation rose {growth.toFixed(1)}% from the previous
                academic year.
              </p>
              <p className="small">
                OPT is a form of work authorization for eligible F-1 students.
                Open Doors reports participants separately from enrolled
                students; these are not counts of H-1B approvals.
              </p>
            </div>
          </div>
          <OptChart />
          <p className="source-note">
            Coverage note: Open Doors counted international students studying
            online from outside the U.S. in 2020/21–2022/23. Long-run
            comparisons also span changes in reporting methods.{" "}
            <a href="#sources">See methodology.</a>
          </p>
        </section>

        <section className="section soft-section" id="opt-employers">
          <div className="wrap">
            <Chapter n="02">WHERE OPT PARTICIPANTS WORK</Chapter>
            <div className="section-intro">
              <h2>The first employers<br /><em>in the story.</em></h2>
              <div><p>ICE’s calendar-2024 employer table brings names into view. Amazon leads the published list, alongside universities and other organizations.</p><p className="small">This is a different source and reporting period from the academic-year trend above. The employer counts are participation records, not a national count of unique students.</p></div>
            </div>
            <OptEmployers />
          </div>
        </section>

        <section className="dark-section section" id="employers">
          <div className="wrap">
            <Chapter n="03" light>
              THE PICTURE GETS BIGGER
            </Chapter>
            <div className="reveal">
              <div>
                <h2>
                  Thousands of employers.
                  <br />
                  <em>A wider story.</em>
                </h2>
                <p>
                  The supplied USCIS export contains{" "}
                  {number(distribution.employers_with_initial_approval)}{" "}
                  named employer groups with at least one initial H-1B approval in FY2025.
                  That reach extends beyond the familiar technology companies.
                </p>
                <a className="text-link" href="https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub">
                  Explore the primary source ↗
                </a>
              </div>
              <div className="reveal-stat">
                <strong>
                  {distribution.employer_share_exactly_1_initial_approval}
                  <span>%</span>
                </strong>
                <p>
                  of those employer groups had
                  <br />
                  just one initial approval.
                </p>
                <span className="small">
                  USCIS · calculated share, rounded · FY2025
                </span>
              </div>
            </div>
            <div className="reveal-note">
              <b>
                {distribution.employer_share_1_to_10_initial_approvals}% had ten
                or fewer.
              </b>
              <p>
                This cumulative share includes groups with one approval. Groups
                use exact reported names and tax suffixes; they are not verified
                unique legal employers. See the counting rule below.
              </p>
            </div>
            <EmployerDistribution />
            <EmployerTable />
          </div>
        </section>

        <section className="wrap section" id="industries">
          <Chapter n="04">ACROSS THE ECONOMY</Chapter>
          <div className="section-intro">
            <h2>More than<br /><em>one industry.</em></h2>
            <div><p>Education, manufacturing and health care appear alongside professional services and information. Initial H-1B approvals reach across the economy.</p><p className="small">Explore the complete FY2025 USCIS export by employer industry. Industry describes organizations, not individual occupations or a technology/nontechnology split.</p></div>
          </div>
          <IndustryChart />
        </section>

        <section className="soft-section section" id="comparison">
          <div className="wrap">
            <Chapter n="05">TWO DATASETS, ONE EMPLOYER LENS</Chapter>
            <div className="section-intro">
              <h2>Compare the pattern.<br /><em>Inspect the match.</em></h2>
              <div><p>What happens when we put two employer-level records side by side? For 47 conservatively matched names, we can compare reported OPT/STEM OPT participation with initial H-1B approvals.</p><p className="small">The connection is a name-level comparison. It cannot tell us which students later received H-1B status.</p></div>
            </div>
            <EmployerComparison />
          </div>
        </section>

        <section className="wrap section" id="wages">
          <Chapter n="06">WHAT THE WAGE DATA COULD SAY</Chapter>
          <div className="section-intro">
            <h2>Offered wages,<br /><em>in context.</em></h2>
            <div><p>How do wages offered in H-1B filings compare with occupational medians? A fair comparison requires a matched occupation, a defined reporting period and the same geographic scope.</p><p className="small">This next question remains a proposal. Matched DOL/BLS data are not yet available.</p></div>
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
              <p>
                The evidence invites policymakers to consider employers across
                sectors, alongside the universities that educate international
                students. University administrators can use this foundation to
                ask better questions about work opportunities after graduation.
              </p>
              <p>
                These aggregate records do not track individual OPT-to-H-1B
                transitions or establish the effects of immigration
                restrictions. The employer comparison identifies accepted name
                pairs, not verified shared legal entities or student transitions.
              </p>
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
                Prototype V1 · Source retrieval attempted October 25, 2026.
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
