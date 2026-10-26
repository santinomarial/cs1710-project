import { useEffect, useRef, useState } from "react";
import { scaleBand } from "d3";
import { employerDistribution, primaryIndustries, number } from "../data";
import { distributionScale, percentage } from "../distribution";
import "./EmployerDistribution.css";

export default function EmployerDistribution() {
  const { total, bins } = employerDistribution;
  const [selected, setSelected] = useState(1);
  const [measure, setMeasure] = useState("employer_share_percent");
  const [showTable, setShowTable] = useState(false);
  const [width, setWidth] = useState(640);
  const svgRef = useRef(null);
  const active = bins.find(row => row.bin_order === selected);
  const byEmployers = measure === "employer_share_percent";
  const axisLabel = byEmployers ? "Share of employer groups (%)" : "Share of initial approvals (%)";
  useEffect(() => {
    const observer = new ResizeObserver(([entry]) => {
      if (entry.contentRect.width > 0) setWidth(entry.contentRect.width);
    });
    observer.observe(svgRef.current);
    return () => observer.disconnect();
  }, []);
  const x = distributionScale(width);
  const y = scaleBand().domain(bins.map(row => row.bin_order)).range([62, 369]).paddingInner(0.34);
  return (
    <figure className="distribution-panel" aria-labelledby="distribution-heading">
      <div className="distribution-heading">
        <div>
          <span className="eyebrow">FY2025 · complete supplied USCIS export</span>
          <h3 id="distribution-heading">Many employers, different scales of sponsorship.</h3>
        </div>
        <p>{number(total.population_employers)} named employer groups · {number(total.population_initial_approvals)} initial approvals</p>
      </div>
      <p className="distribution-context">
        The distribution reaches well beyond the largest sponsors. Switch views to see
        how the share of employers differs from the share of approved petitions.
        Each employer group appears in exactly one bin.
      </p>
      <div className="distribution-controls" role="group" aria-label="Distribution measure">
        <button aria-pressed={byEmployers} onClick={() => setMeasure("employer_share_percent")}>Employer share</button>
        <button aria-pressed={!byEmployers} onClick={() => setMeasure("approval_share_percent")}>Approval share</button>
      </div>
      <p className="distribution-instruction" id="distribution-instruction">
        Hover, tap, or Tab to a row for counts and both shares. The scale stays at 0–100% in both views.
      </p>
      <svg ref={svgRef} viewBox={`0 0 ${width} 440`} className="distribution-chart" role="group"
        aria-labelledby="distribution-svg-title" aria-describedby="distribution-instruction distribution-limits">
        <title id="distribution-svg-title">FY2025 initial H-1B distribution: {axisLabel}</title>
        <text x="8" y="17" className="distribution-axis-title">Initial approvals per employer group</text>
        {x.ticks(width < 400 ? 2 : 4).map(tick => (
          <g key={tick} aria-hidden="true">
            <line x1={x(tick)} x2={x(tick)} y1="40" y2="388" className="distribution-grid" />
            <text x={x(tick)} y="407" textAnchor="middle">{tick}%</text>
          </g>
        ))}
        {bins.map(row => (
          <g key={row.bin_order} className={`distribution-mark ${selected === row.bin_order ? "active" : ""}`}
            role="button" tabIndex="0" aria-pressed={selected === row.bin_order}
            aria-label={`${row.bin_label} initial approvals: ${number(row.employer_count)} employer groups, ${number(row.initial_approvals)} approvals. ${percentage(row[measure])} in this view.`}
            aria-controls="distribution-detail" onPointerEnter={() => setSelected(row.bin_order)}
            onFocus={() => setSelected(row.bin_order)} onClick={() => setSelected(row.bin_order)}
            onKeyDown={event => {
              if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setSelected(row.bin_order); }
            }}>
            <rect x="3" y={y(row.bin_order) - 6} width={width - 6} height={y.bandwidth() + 12} rx="3" className="distribution-hit" />
            <text x="8" y={y(row.bin_order) + y.bandwidth() / 2 + 4} className="distribution-category">{row.bin_label}</text>
            <rect x={x(0)} y={y(row.bin_order)} width={x(row[measure]) - x(0)} height={y.bandwidth()} className="distribution-bar" />
            <text x={x(row[measure]) + 6} y={y(row.bin_order) + y.bandwidth() / 2 + 4} className="distribution-value">{percentage(row[measure])}</text>
          </g>
        ))}
        <line x1={x(0)} x2={x(100)} y1="388" y2="388" className="distribution-baseline" />
        <text x={width / 2} y="434" textAnchor="middle" className="distribution-axis-title">{axisLabel}</text>
      </svg>
      <div className="distribution-detail" id="distribution-detail" role="status" aria-live="polite" aria-atomic="true">
        <strong>{active.bin_label} initial approvals per employer group</strong>
        <p>{number(active.employer_count)} groups ({percentage(active.employer_share_percent)} of {number(total.population_employers)})
          account for {number(active.initial_approvals)} approvals ({percentage(active.approval_share_percent)} of {number(total.population_initial_approvals)}).</p>
        <span>Initial = new employment + new concurrent employment. Continuing categories are excluded. Approved petitions are not unique workers.</span>
      </div>
      <figcaption id="distribution-limits">
        <b>Counting rule:</b> Groups combine identical reported names and tax suffixes across locations.
        Name variants remain separate; the partial tax ID cannot establish unique legal employers.
        {" "}{number(total.excluded_unnamed_records)} unnamed records are retained in the downloads;
        their {number(total.excluded_unnamed_initial_approvals)} initial approvals are excluded here.
        Groups with zero initial approvals are also excluded. Percentages are calculated from exact counts and rounded for display.
      </figcaption>
      <div className="distribution-footer">
        <a href={total.source_url}>Source: USCIS Employer Data Hub · FY2025 ↗</a>
        <button onClick={() => setShowTable(!showTable)} aria-expanded={showTable} aria-controls="distribution-values">
          {showTable ? "Hide" : "View"} data table {showTable ? "−" : "+"}
        </button>
      </div>
      {showTable && <div id="distribution-values" className="table-scroll"><table>
        <caption>Named employer groups with positive initial approvals · mutually exclusive bins</caption>
        <thead><tr><th scope="col">Initial approvals per group</th><th scope="col">Groups</th><th scope="col">Group share</th><th scope="col">Approvals</th><th scope="col">Approval share</th></tr></thead>
        <tbody>{bins.map(row => <tr key={row.bin_order}><th scope="row">{row.bin_label}</th><td>{number(row.employer_count)}</td><td>{percentage(row.employer_share_percent)}</td><td>{number(row.initial_approvals)}</td><td>{percentage(row.approval_share_percent)}</td></tr>)}</tbody>
      </table></div>}
      <aside className="distribution-examples" aria-label="Industry context from the full export">
        <p><b>Sponsorship also reaches education and health care.</b> Across all export records, including unnamed employers:</p>
        <ul>{primaryIndustries.filter(row => ["61", "62"].includes(row.naics_code)).map(row => <li key={row.naics_code}>
          <a href={row.source_url}>{row.industry}</a><span>{number(row.initial_approvals)} initial approvals · NAICS {row.naics_code}</span>
        </li>)}</ul>
        <p>Industry describes the employer, not the occupation. These categories do not define a technology/nontechnology split.
          The export totals {number(total.population_initial_approvals + total.excluded_unnamed_initial_approvals)} initial approvals, two fewer than NFAP’s 114,806; the difference remains unresolved.</p>
      </aside>
    </figure>
  );
}
