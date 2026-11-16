import { memo, useMemo, useState } from "react";
import { number, opt, optUrl } from "../data";
import { optLayout } from "../optLayout";
import { ChartMeta, useChartWidth } from "./ChartPrimitives";

// The path, ticks and pointer targets stay stable while the readout changes.
const Plot = memo(function Plot({ layout, width, inspect }) {
  const { x, y, path, bands } = layout;
  return <>
    {y.ticks(3).map(tick => <g key={tick} aria-hidden="true">
      <line x1="48" x2={width - 28} y1={y(tick)} y2={y(tick)} className="grid-line" />
      <text x="36" y={y(tick) + 4} textAnchor="end">{tick === 0 ? "0" : `${tick / 1000}k`}</text>
    </g>)}
    {x.ticks(width < 500 ? 2 : 4).filter(Number.isInteger).map(tick =>
      <text key={tick} x={x(tick)} y="319" textAnchor="middle" aria-hidden="true">{tick}/{String(tick + 1).slice(-2)}</text>)}
    <path d={path} className="data-line" aria-hidden="true" />
    {bands.map(({ row, left, right }, index) => <rect key={row.start_year}
      className="opt-year-target" x={left} y="28" width={right - left} height="258"
      role="button" tabIndex={index === bands.length - 1 ? 0 : -1}
      aria-label={`${row.academic_year}: ${number(row.opt_students)} students on OPT`}
      onPointerEnter={() => inspect(row.start_year)} onPointerMove={() => inspect(row.start_year)}
      onFocus={() => inspect(row.start_year)} onClick={event => { inspect(row.start_year); event.currentTarget.focus(); }}
      onKeyDown={event => {
        const keys = { ArrowLeft: Math.max(0, index - 1), ArrowRight: Math.min(bands.length - 1, index + 1), Home: 0, End: bands.length - 1 };
        if (event.key in keys) {
          event.preventDefault();
          event.currentTarget.parentElement.querySelectorAll(".opt-year-target")[keys[event.key]].focus();
        } else if (["Enter", " "].includes(event.key)) { event.preventDefault(); inspect(row.start_year); }
      }} />)}
  </>;
});

export default function OptChart() {
  const [start, setStart] = useState(2005);
  const [activeYear, setActiveYear] = useState(null);
  const [showTable, setShowTable] = useState(false);
  const [chartRef, width] = useChartWidth(840);
  const layout = useMemo(() => optLayout(opt, start, width), [start, width]);
  const { rows, x, y } = layout;
  const active = rows.find(d => d.start_year === activeYear) ?? rows.at(-1);
  return <div className="chart-panel">
    <h3 className="chart-takeaway">OPT participation reached {number(opt.at(-1).opt_students)} in {opt.at(-1).academic_year}.</h3>
    <ChartMeta source="IIE Open Doors 2025" href={optUrl} period={`Academic years ${rows[0].academic_year}–${rows.at(-1).academic_year}`} unit="Students on OPT" />
    <div className="chart-toolbar"><span><span className="legend-dot" /> Students on OPT</span>
      <label>View <select value={start} onChange={e => { setStart(+e.target.value); setActiveYear(null); }}><option value={2005}>2005/06–2024/25</option><option value={1979}>Full OPT history</option></select></label>
    </div>
    <div className="chart-readout" aria-live="polite" aria-atomic="true"><strong>{number(active.opt_students)}</strong><span>{active.academic_year} · students on OPT</span></div>
    <p className="interaction-hint" id="opt-interaction">Move across the chart or tap to inspect a year. Keyboard: Tab into the chart, then use ← / →.</p>
    <div ref={chartRef} className="opt-plot">
      <svg className="opt-chart" viewBox={`0 0 ${width} 335`} role="group" aria-labelledby="opt-chart-title" aria-describedby="opt-interaction">
        <title id="opt-chart-title">Students on OPT, {rows[0].academic_year} to {rows.at(-1).academic_year}</title>
        <Plot layout={layout} width={width} inspect={setActiveYear} />
        <g className="opt-inspection" aria-hidden="true">
          <line x1={x(active.start_year)} x2={x(active.start_year)} y1="28" y2="286" />
          <circle cx={x(active.start_year)} cy={y(active.opt_students)} r="5" className="data-dot selected" />
        </g>
      </svg>
    </div>
    <div className="chart-bottom"><a href={optUrl}>Source: IIE Open Doors 2025 ↗</a><button onClick={() => setShowTable(!showTable)} aria-expanded={showTable} aria-controls="opt-values">{showTable ? "Hide" : "View"} data table {showTable ? "−" : "+"}</button></div>
    {showTable && <div id="opt-values" className="table-scroll"><table><caption>OPT participation by academic year</caption><thead><tr><th scope="col">Academic year</th><th scope="col">Students on OPT</th></tr></thead><tbody>{rows.map(row => <tr key={row.academic_year}><th scope="row">{row.academic_year}</th><td>{number(row.opt_students)}</td></tr>)}</tbody></table></div>}
  </div>;
}
