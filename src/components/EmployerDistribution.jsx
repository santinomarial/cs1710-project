import { useState } from "react";
import { scaleBand } from "d3";
import { employerDistribution, number } from "../data";
import { distributionScale, percentage } from "../distribution";
import { ChartMeta, Tooltip, useChartWidth } from "./ChartPrimitives";
import "./EmployerDistribution.css";

export default function EmployerDistribution() {
  const { total, bins } = employerDistribution;
  const [selected, setSelected] = useState(1);
  const [measure, setMeasure] = useState("employer_share_percent");
  const [showTable, setShowTable] = useState(false);
  const [chartRef, width] = useChartWidth(640);
  const [hovered, setHovered] = useState(null);
  const preview = bins.find(row => row.bin_order === hovered);
  const single = bins[0];
  const active = bins.find(row => row.bin_order === selected);
  const byEmployers = measure === "employer_share_percent";
  const axisLabel = byEmployers ? "Share of employer groups (%)" : "Share of initial approvals (%)";
  const x = distributionScale(width);
  const y = scaleBand().domain(bins.map(row => row.bin_order)).range([62, 369]).paddingInner(0.34);
  return (
    <figure className="distribution-panel" aria-labelledby="distribution-heading">
      <div className="distribution-heading"><h3 id="distribution-heading">Most sponsors had one approval. Their share of approvals was smaller.</h3></div>
      <ChartMeta source="USCIS Employer Data Hub" href={total.source_url} period="FY2025 · Oct 2024–Sep 2025" unit="Approved initial petitions, not applications filed or unique workers" />
      <div className="distribution-callout" aria-label="One-approval employer groups: two denominators">
        <div><strong>{percentage(single.employer_share_percent)}</strong><span>of named employer groups had <b>one initial approval</b></span><small>{number(single.employer_count)} of {number(total.population_employers)} groups</small></div>
        <div><strong>{percentage(single.approval_share_percent)}</strong><span>of initial approvals went to <b>those same groups</b></span><small>{number(single.initial_approvals)} of {number(total.population_initial_approvals)} approvals</small></div>
      </div>
      <div className="distribution-controls" role="group" aria-label="Distribution measure">
        <button aria-pressed={byEmployers} onClick={() => setMeasure("employer_share_percent")}>% of employer groups</button>
        <button aria-pressed={!byEmployers} onClick={() => setMeasure("approval_share_percent")}>% of approvals</button>
      </div>
      <p className="distribution-denominator" role="status"><b>Each bar:</b> {byEmployers ? `groups in that bin ÷ ${number(total.population_employers)} named employer groups` : `initial approvals in that bin ÷ ${number(total.population_initial_approvals)} initial approvals`}.</p>
      <p className="distribution-instruction" id="distribution-instruction">
        Hover or focus to preview; click or Enter to pin a row. Both views use a 0–100% scale.
      </p>
      <div className="distribution-plot" ref={chartRef}>
      <svg viewBox={`0 0 ${width} 440`} className="distribution-chart" role="group"
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
            aria-controls="distribution-detail" onPointerEnter={() => setHovered(row.bin_order)} onPointerLeave={() => setHovered(null)}
            onFocus={() => setHovered(row.bin_order)} onBlur={() => setHovered(null)} onClick={() => { setSelected(row.bin_order); setHovered(null); }}
            onKeyDown={event => {
              if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setSelected(row.bin_order); setHovered(null); }
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
      {preview && <Tooltip><strong>{preview.bin_label} initial approvals per employer group</strong><span>{number(preview.employer_count)} / {number(total.population_employers)} groups · {percentage(preview.employer_share_percent)}</span><span>{number(preview.initial_approvals)} / {number(total.population_initial_approvals)} approvals · {percentage(preview.approval_share_percent)}</span></Tooltip>}
      </div>
      <div className="distribution-detail" id="distribution-detail" role="status" aria-live="polite" aria-atomic="true">
        <strong>Pinned: {active.bin_label} initial approvals per employer group</strong>
        <p>{number(active.employer_count)} groups ({percentage(active.employer_share_percent)} of {number(total.population_employers)})
          account for {number(active.initial_approvals)} approvals ({percentage(active.approval_share_percent)} of {number(total.population_initial_approvals)}).</p>
        <span>Initial = new employment + new concurrent employment. Continuing categories are excluded. Approved petitions are not unique workers.</span>
      </div>
      <figcaption id="distribution-limits" className="distribution-limits">Population: named employer groups with positive initial approvals. Excludes {number(total.excluded_unnamed_initial_approvals)} approvals in {number(total.excluded_unnamed_records)} unnamed records; these remain in the downloads.</figcaption>
      <details className="distribution-methods"><summary>Counting rules & national totals</summary>
        <p>Groups combine identical reported names and tax suffixes across locations. Name variants remain separate; partial tax IDs cannot establish unique legal employers. Each group appears in exactly one bin. Groups with zero initial approvals are excluded. Percentages use exact counts, rounded for display.</p>
        <p>The full export, including unnamed employers, totals {number(total.population_initial_approvals + total.excluded_unnamed_initial_approvals)} initial approvals. This is the industry chart’s denominator. NFAP reports 114,806; the two-approval difference remains unresolved.</p>
      </details>
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

    </figure>
  );
}
