import { useState } from "react";
import { max, scaleBand, scaleLinear } from "d3";
import { primaryIndustries as data, number } from "../data";
import { industryRows, nationalShare } from "../chartData";
import { ChartMeta, EvidenceRow, Tooltip, useChartWidth } from "./ChartPrimitives";

const short = {
  "54": "Professional, scientific & technical", "61": "Educational services", "31-33": "Manufacturing",
  "51": "Information", "62": "Health care & social assistance", "52": "Finance & insurance",
  "44-45": "Retail trade", "56": "Admin., support & waste services", "23": "Construction", "42": "Wholesale trade",
  "71": "Arts, entertainment & recreation", "48-49": "Transportation & warehousing", "53": "Real estate & rental",
  "72": "Accommodation & food services", "81": "Other services", "55": "Management of companies",
  "21": "Mining, quarrying, oil & gas", "11": "Agriculture, forestry & fishing", "22": "Utilities", "92": "Public administration",
};

export default function IndustryChart() {
  const [mode, setMode] = useState("count");
  const [query, setQuery] = useState("");
  const [all, setAll] = useState(false);
  const [selected, setSelected] = useState("61");
  const [hovered, setHovered] = useState(null);
  const [ref, width] = useChartWidth();
  const rows = industryRows(data, { query, all, sort: "count" });
  const active = data.find(d => d.naics_code === (hovered ?? selected));
  const missing = data.find(d => !d.naics_code);
  const total = data.reduce((sum, d) => sum + d.initial_approvals, 0);
  const mobile = width < 580;
  const measure = d => mode === "count" ? d.initial_approvals : nationalShare(d, data);
  const x = scaleLinear().domain([0, max(data, measure)]).nice().range([mobile ? 12 : 255, width - 58]);
  const rowHeight = mobile ? 72 : 44;
  const plotBottom = 24 + rows.length * rowHeight;
  const y = scaleBand().domain(rows.map(d => d.naics_code)).range([24, plotBottom]).paddingInner(.12);
  const label = mode === "count" ? "Initial approvals (petitions)" : "Share of all initial approvals (%)";
  const display = d => mode === "count" ? number(d.initial_approvals) : `${measure(d).toFixed(1)}%`;
  const reset = () => { setQuery(""); setAll(false); setHovered(null); };
  return <figure className="interactive-figure" aria-labelledby="industry-title">
    <ChartMeta source="USCIS Employer Data Hub" href={data[0].source_url} period="FY2025 · Oct 2024–Sep 2025" unit="Initial approved petitions (new + new concurrent employment)" />
    <div className="stat-ribbon">
      <div><strong>{number(total)}</strong><span>initial approvals · FY2025</span></div>
      <div><strong>{data.filter(d => d.naics_code).length}</strong><span>reported industry sectors</span></div>
      <div><strong>{number(missing.initial_approvals)}</strong><span>industry not reported</span></div>
    </div>
    <div className="viz-controls">
      <div className="segmented" role="group" aria-label="Industry measure">
        <button aria-pressed={mode === "count"} onClick={() => setMode("count")}>Approvals</button>
        <button aria-pressed={mode === "share"} onClick={() => setMode("share")}>National share (%)</button>
      </div>
      <label className="control-label search-control">Find an industry<input type="search" placeholder="Name or NAICS code" value={query} onChange={e => { setQuery(e.target.value); setHovered(null); }} /></label>
    </div>
    <div className="viz-split">
      <div className="plot-card" ref={ref}>
        <div className="plot-heading"><h3 id="industry-title">Professional services lead; education follows.</h3><span>{rows.length} of 20 sectors</span></div>
        <p className="interaction-hint">Hover or focus to preview. Click or Enter to pin a sector.</p>
        {rows.length ? <svg className="industry-chart evidence-chart" viewBox={`0 0 ${width} ${plotBottom + 70}`} role="group" aria-label={`Industry ranked bars: ${label}`}>
          {x.ticks(mobile ? 3 : 4).map(t => <g key={t} aria-hidden="true"><line className="viz-grid" x1={x(t)} x2={x(t)} y1="20" y2={plotBottom} /><text x={x(t)} y={plotBottom + 24} textAnchor="middle">{mode === "count" ? (t ? `${t / 1000}k` : "0") : `${t}%`}</text></g>)}
          {rows.map(d => {
            const yy = y(d.naics_code); const barY = yy + (mobile ? 28 : 9);
            return <g key={d.naics_code} role="button" tabIndex="0" aria-pressed={selected === d.naics_code} aria-controls="industry-detail"
              aria-label={`${d.industry}, NAICS ${d.naics_code}: ${number(d.initial_approvals)} initial approvals, ${nationalShare(d, data).toFixed(1)} percent nationally`}
              className={`industry-mark ${selected === d.naics_code ? "selected" : ""}`} onPointerEnter={() => setHovered(d.naics_code)} onPointerLeave={() => setHovered(null)} onFocus={() => setHovered(d.naics_code)} onBlur={() => setHovered(null)}
              onClick={() => { setSelected(d.naics_code); setHovered(null); }} onKeyDown={e => { if (["Enter", " "].includes(e.key)) { e.preventDefault(); setSelected(d.naics_code); setHovered(null); } if (e.key === "Escape") { setSelected(null); setHovered(null); } }}>
              <rect className="industry-hit" x="2" y={yy} width={width - 4} height={y.bandwidth()} rx="4" />
              <text className="industry-label" x="12" y={yy + (mobile ? 16 : 24)}>{short[d.naics_code] ?? d.industry}</text>
              <rect className="industry-bar" x={x(0)} y={barY} width={x(measure(d)) - x(0)} height="18" />
              <text className="value-label" x={x(measure(d)) + 7} y={barY + 13}>{display(d)}</text>
            </g>;
          })}
          <text x={width / 2} y={plotBottom + 55} textAnchor="middle" className="axis-caption">{label}</text>
        </svg> : <div className="empty-state"><h4>No industry matches “{query}”.</h4><button onClick={reset}>Reset industry filters</button></div>}
        {hovered !== null && active && <Tooltip><strong>{active.industry}</strong><span>{number(active.initial_approvals)} initial approvals · {nationalShare(active, data).toFixed(1)}% nationally</span><span>NAICS {active.naics_code} · FY2025 · petitions, not unique workers</span></Tooltip>}
        <button className="quiet-button" onClick={() => setAll(!all)} aria-pressed={all}>{all ? "Show top 10" : "View all 20 sectors"} {all ? "−" : "+"}</button>
      </div>
      <aside className="detail-card" id="industry-detail" aria-live="polite" aria-atomic="true">
        <span className="eyebrow accent">{hovered !== null ? "Preview industry" : "Selected industry"}{active ? ` / NAICS ${active.naics_code}` : ""}</span>
        {active ? <><h3>{active.industry}</h3><div className="detail-total">{number(active.initial_approvals)}</div><p className="accent">{nationalShare(active, data).toFixed(1)}% of all initial approvals</p>
          <div className="detail-values"><EvidenceRow label="New employment">{number(active.new_employment_approvals)}</EvidenceRow><EvidenceRow label="New concurrent employment">{number(active.new_concurrent_approvals)}</EvidenceRow></div>
          <p className="small">FY2025 · October 2024–September 2025. Initial approvals count petitions, not unique workers.</p>
          <button className="quiet-button" onClick={() => { setSelected(null); setHovered(null); }}>Clear industry selection</button></> : <p>Select a sector to inspect its components and national share.</p>}
        <a className="card-source" href={data[0].source_url}>USCIS Employer Data Hub ↗</a>
      </aside>
    </div>
    <figcaption className="context-band"><p><b>Keep missing industry visible.</b> {number(missing.initial_approvals)} approvals have no reported industry. They remain in the national denominator, including when filtering.</p><p><b>Read the categories carefully.</b> Industry describes the employer, not the occupation. It does not define a technology/nontechnology split.</p></figcaption>
    <details className="viz-data"><summary>Source values & reconciliation <span>21 rows +</span></summary><p className="small">20 reported sectors plus missing industry. USCIS totals 114,804; NFAP reports 114,806. The two-approval difference remains unresolved. The chart uses USCIS throughout.</p><div className="table-scroll"><table><caption>FY2025 USCIS · all source sectors, including missing industry</caption><thead><tr><th>Industry / NAICS</th><th>Initial approvals</th><th>National share</th></tr></thead><tbody>{data.map(d => <tr key={d.naics_code || "missing"}><th scope="row">{d.industry} {d.naics_code && `(${d.naics_code})`}</th><td>{number(d.initial_approvals)}</td><td>{nationalShare(d, data).toFixed(2)}%</td></tr>)}</tbody></table></div></details>
  </figure>;
}
