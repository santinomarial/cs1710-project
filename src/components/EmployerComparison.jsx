import { useEffect, useMemo, useState } from "react";
import { max, scaleLinear, symbol, symbolCircle, symbolDiamond } from "d3";
import { overlap, matchAudit, number } from "../data";
import { comparisonRows, MATCH_TYPES } from "../chartData";
import { EvidenceRow, Tooltip, useChartWidth } from "./ChartPrimitives";

const metrics = {
  total_opt_or_stem_opt_participants: "Combined",
  opt_participants: "OPT",
  stem_opt_participants: "STEM OPT",
};
const fmt = v => v === null ? "Not reported" : number(v);
const symbolPath = type => symbol().type(type === "formatting" ? symbolDiamond : symbolCircle).size(65)();

export default function EmployerComparison() {
  const [metric, setMetric] = useState("total_opt_or_stem_opt_participants");
  const [query, setQuery] = useState("");
  const [types, setTypes] = useState(Object.keys(MATCH_TYPES));
  const [selected, setSelected] = useState(overlap.find(d => d.employer_name === "Harvard University").uscis_employer_group_id);
  const [hovered, setHovered] = useState(null);
  const [ref, width] = useChartWidth();
  const { filtered, plotted, missing } = useMemo(() => comparisonRows(overlap, { query, types, metric }), [query, types, metric]);
  useEffect(() => {
    setHovered(null);
    if (selected && !filtered.some(d => d.uscis_employer_group_id === selected)) setSelected(null);
  }, [filtered, selected]);
  const active = filtered.find(d => d.uscis_employer_group_id === selected);
  const preview = plotted.find(d => d.uscis_employer_group_id === hovered);
  const narrow = width < 500;
  const height = narrow ? 360 : 410;
  const bottom = height - 62;
  // Domains come from the full accepted population, so filters never rescale the evidence.
  const x = scaleLinear().domain([0, max(overlap, d => d[metric])]).nice(4).range([42, width - 24]);
  const y = scaleLinear().domain([0, max(overlap, d => d.h1b_initial_approvals)]).nice(6).range([bottom, 30]);
  const counts = Object.fromEntries(Object.keys(MATCH_TYPES).map(t => [t, overlap.filter(d => d.match_type === t).length]));
  const axisLabel = metric === "total_opt_or_stem_opt_participants" ? "Total OPT or STEM OPT participation" : `${metrics[metric]} participation`;
  const reset = () => { setTypes(Object.keys(MATCH_TYPES)); setQuery(""); setMetric("total_opt_or_stem_opt_participants"); };
  const choose = id => { setSelected(id || null); setHovered(null); };
  return <figure className="interactive-figure" aria-labelledby="comparison-title">
    <div className="population-note"><b>Different populations. Different reporting periods.</b><p>ICE: calendar-2024 OPT/STEM OPT participation. USCIS: FY2025 initial petition approvals. These are not individual transitions, conversion rates, or verified legal-entity matches.</p></div>
    <div className="viz-controls">
      <label className="control-label search-control">Find an accepted employer<input type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder="Search either source name" /></label>
      <div className="segmented" role="group" aria-label="Employer comparison horizontal axis">{Object.entries(metrics).map(([key, label]) => <button key={key} aria-pressed={metric === key} onClick={() => setMetric(key)}>{label}</button>)}</div>
      <p className="coverage-count" role="status">{plotted.length} / {overlap.length} plotted <span>{matchAudit.length - overlap.length} excluded from join</span></p>
    </div>
    <fieldset className="match-filters"><legend>Name formatting <span>Display categories, not identity confidence</span></legend>{Object.entries(MATCH_TYPES).map(([key, type]) => <label key={key}><input type="checkbox" checked={types.includes(key)} onChange={e => setTypes(e.target.checked ? [...types, key] : types.filter(t => t !== key))} /><span className={`match-symbol ${key}`} aria-hidden="true" />{type.label} ({counts[key]})</label>)}</fieldset>
    <div className="viz-split comparison-split">
      <div className="plot-card" ref={ref}>
        <div className="plot-heading"><h3 id="comparison-title">One point. Two source records.</h3><span>47 accepted name pairs</span></div>
        <p className="plot-unit">FY2025 initial H-1B approvals <span>(petitions)</span></p>
        {plotted.length ? <svg className="comparison-chart evidence-chart" viewBox={`0 0 ${width} ${height}`} role="group" aria-label={`Employer comparison: CY2024 ${axisLabel} versus FY2025 initial H-1B approvals`}>
          {y.ticks(narrow ? 3 : 6).map(t => <g key={t} aria-hidden="true"><line className="viz-grid" x1={x(0)} x2={x.range()[1]} y1={y(t)} y2={y(t)} /><text x="32" y={y(t) + 4} textAnchor="end">{t}</text></g>)}
          {x.ticks(narrow ? 3 : 4).map(t => <g key={t} aria-hidden="true"><line className="viz-grid" x1={x(t)} x2={x(t)} y1={y.range()[1]} y2={bottom} /><text x={x(t)} y={bottom + 22} textAnchor="middle">{number(t)}</text></g>)}
          {active && active[metric] !== null && <g aria-hidden="true" className="selected-guides"><line x1={x(0)} x2={x(active[metric])} y1={y(active.h1b_initial_approvals)} y2={y(active.h1b_initial_approvals)} /><line x1={x(active[metric])} x2={x(active[metric])} y1={y(active.h1b_initial_approvals)} y2={bottom} /></g>}
          {plotted.map(d => <g key={d.uscis_employer_group_id} transform={`translate(${x(d[metric])},${y(d.h1b_initial_approvals)})`} className={`comparison-point ${d.match_type} ${selected === d.uscis_employer_group_id ? "selected" : ""}`} role="button" tabIndex="0" aria-pressed={selected === d.uscis_employer_group_id} aria-controls="comparison-detail"
            aria-label={`${d.employer_name}: ${fmt(d[metric])} ${metrics[metric]} participation, calendar 2024; ${number(d.h1b_initial_approvals)} initial approvals, FY2025; ${MATCH_TYPES[d.match_type].label}`}
            onPointerEnter={() => setHovered(d.uscis_employer_group_id)} onPointerLeave={() => setHovered(null)} onFocus={() => setHovered(d.uscis_employer_group_id)} onBlur={() => setHovered(null)} onClick={() => choose(d.uscis_employer_group_id)}
            onKeyDown={e => { if (["Enter", " "].includes(e.key)) { e.preventDefault(); choose(d.uscis_employer_group_id); } if (e.key === "Escape") choose(null); }}>
            <circle r="11" className="point-hit" />
            <path d={symbolPath(d.match_type)} className="point-symbol" />
            <circle r="10" className="selection-ring" />
          </g>)}
          {active && active[metric] !== null && !narrow && <text className="point-label" x={Math.min(width - 10, x(active[metric]) + 13)} y={y(active.h1b_initial_approvals) - 15} textAnchor={x(active[metric]) > width * .62 ? "end" : "start"}>{active.employer_name}</text>}
          <text className="axis-caption" x={width / 2} y={height - 9} textAnchor="middle">CY2024 · {narrow ? `${metrics[metric]} participation` : axisLabel}</text>
        </svg> : <div className="empty-state"><h4>No plottable pairs in this view.</h4><p>Try another name, match type or participation measure.</p><button onClick={reset}>Reset comparison filters</button></div>}
        {preview && <Tooltip><strong>{preview.employer_name}</strong><span>CY2024 {metrics[metric]}: {fmt(preview[metric])}</span><span>FY2025 initial approvals: {number(preview.h1b_initial_approvals)}</span><span>{MATCH_TYPES[preview.match_type].label} · name comparison only</span></Tooltip>}
        <p className="interaction-hint">Hover or focus to preview; click or Enter to pin. Closely spaced points? Choose a name below.</p>
        <label className="control-label point-picker">Select an employer<select value={active?.uscis_employer_group_id ?? ""} onChange={e => choose(e.target.value)}><option value="">Choose an accepted name</option>{filtered.slice().sort((a, b) => a.employer_name.localeCompare(b.employer_name)).map(d => <option key={d.uscis_employer_group_id} value={d.uscis_employer_group_id}>{d.employer_name}{d[metric] === null ? " — value not reported" : ""}</option>)}</select></label>
        {missing.length > 0 && <p className="missing-note" role="status">{missing.length} missing {metrics[metric]} value: {missing.map(d => d.employer_name).join(", ")}. Not plotted; never treated as zero.</p>}
        <button className="quiet-button" onClick={reset}>Reset comparison filters</button>
      </div>
      <aside className="detail-card employer-evidence" id="comparison-detail" aria-live="polite" aria-atomic="true">
        <span className="eyebrow accent">Pinned employer</span>
        {active ? <><h3>{active.employer_name}</h3><span className="match-badge"><span className={`match-symbol ${active.match_type}`} aria-hidden="true" />{MATCH_TYPES[active.match_type].label}</span>
          <div className="detail-values"><EvidenceRow label="ICE / calendar 2024">{fmt(active.total_opt_or_stem_opt_participants)}</EvidenceRow><p className="small">Total OPT or STEM OPT participation</p><p className="small">OPT {fmt(active.opt_participants)} · STEM OPT {fmt(active.stem_opt_participants)}</p><p className="small accent">Combined is not OPT + STEM OPT.</p></div>
          <div className="detail-values"><EvidenceRow label="USCIS / FY2025 initial">{number(active.h1b_initial_approvals)}</EvidenceRow><p className="small">New employment {number(active.h1b_new_employment_approvals)} · Concurrent {number(active.h1b_new_concurrent_approvals)}</p><p className="small">Petition approvals, not unique workers.</p></div>
          {active[metric] === null && <p className="missing-note">Selected {metrics[metric]} value is not reported; this employer has no point in the current view.</p>}
          <details className="match-evidence" open><summary>Inspect the name evidence <span>+</span></summary><dl><dt>ICE name</dt><dd>{active.employer_name}</dd><dt>USCIS name</dt><dd>{active.uscis_employer_name}</dd><dt>USCIS tax suffix</dt><dd>{active.uscis_tax_id_suffix} · partial identifier</dd></dl><p className="small">Unique normalized full name under the conservative rule. Name agreement does not verify legal identity.</p></details>
          <div className="detail-sources"><a href={`${active.source_url}#page=${active.source_page}`}>ICE p. {active.source_page}, row {active.source_table_row} ↗</a><a href={active.uscis_source_url}>USCIS source line(s) {active.uscis_source_lines} ↗</a></div>
          <button className="quiet-button" onClick={() => choose(null)}>Clear employer selection</button>
        </> : <div className="empty-detail"><h3>Inspect a name.</h3><p>Choose a point or employer to see both source records, their periods and the matching evidence.</p></div>}
      </aside>
    </div>
    <div className="context-band comparison-context"><div className="period-strip"><b>Overlapping periods, not a student cohort</b><div className="period-row"><span>ICE · Jan–Dec 2024</span><div className="period-track"><i className="ice-period" /></div></div><div className="period-row"><span>USCIS · Oct 2024–Sep 2025</span><div className="period-track"><i className="uscis-period" /></div></div><small>Shared months: October–December 2024</small></div><p><b>One selected subset.</b> These {overlap.length} names come from ICE’s top {matchAudit.length} list. They do not represent all employers. Unmatched names do not establish an absence of sponsorship.</p></div>
    <figcaption className="source-note">Sources: <a href={overlap[0].source_url}>ICE / SEVIS, calendar 2024</a> and <a href={overlap[0].uscis_source_url}>USCIS, FY2025</a>. Combined participation is retained as reported; a student may be counted multiple times across programs. Shape categories describe name formatting, not confidence.</figcaption>
    <details className="viz-data"><summary>Comparison values & matching limits <span>{filtered.length} visible pairs +</span></summary><p className="small">15 preserved strings agree verbatim, 28 after case/spacing normalization, and 4 after punctuation/ampersand normalization. All 47 passed the same conservative full-name rule. No fuzzy aliases or parent-company merges. Of 200 ICE names, 153 are excluded: 14 ambiguous full-name cases, 97 unresolved variants, 41 without conservative candidates and one clipped name. These are lexical decisions, not verified affiliations.</p><div className="table-scroll"><table><caption>Accepted employer-name comparisons · current name filters · missing cells remain missing</caption><thead><tr><th>ICE employer name</th><th>CY2024 combined</th><th>OPT</th><th>STEM OPT</th><th>FY2025 initial approvals</th></tr></thead><tbody>{filtered.map(d => <tr key={d.uscis_employer_group_id}><th scope="row"><button className="table-select" onClick={() => choose(d.uscis_employer_group_id)}>{d.employer_name}</button></th><td>{fmt(d.total_opt_or_stem_opt_participants)}</td><td>{fmt(d.opt_participants)}</td><td>{fmt(d.stem_opt_participants)}</td><td>{number(d.h1b_initial_approvals)}</td></tr>)}</tbody></table></div></details>
  </figure>;
}
