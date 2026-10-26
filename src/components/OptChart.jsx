import { useEffect, useRef, useState } from "react";
import { extent, line, max, scaleLinear } from "d3";
import { number, opt, optUrl } from "../data";

export default function OptChart() {
  const [start, setStart] = useState(2005);
  const [activeYear, setActiveYear] = useState(null);
  const [showTable, setShowTable] = useState(false);
  const [width, setWidth] = useState(840);
  const chartRef = useRef(null);
  useEffect(() => {
    const observer = new ResizeObserver(([entry]) => {
      if (entry.contentRect.width > 0) setWidth(entry.contentRect.width);
    });
    observer.observe(chartRef.current);
    return () => observer.disconnect();
  }, []);
  const rows = opt.filter((d) => d.start_year >= start);
  const active = rows.find((d) => d.start_year === activeYear) ?? rows.at(-1);
  const x = scaleLinear()
    .domain(extent(rows, (d) => d.start_year))
    .range([48, width - 28]);
  const y = scaleLinear()
    .domain([0, max(rows, (d) => d.opt_students)])
    .nice()
    .range([286, 28]);
  const path = line()
    .x((d) => x(d.start_year))
    .y((d) => y(d.opt_students))(rows);
  return (
    <div className="chart-panel">
      <div className="chart-toolbar">
        <div>
          <span className="legend-dot" /> Students on OPT{" "}
          <span className="muted">· academic year</span>
        </div>
        <label>
          View{" "}
          <select
            value={start}
            onChange={(e) => {
              setStart(+e.target.value);
              setActiveYear(null);
            }}
          >
            <option value={2005}>2005/06–2024/25</option>
            <option value={1979}>Full OPT history</option>
          </select>
        </label>
      </div>
      <div className="chart-readout" aria-live="polite">
        <strong>{number(active.opt_students)}</strong>
        <span>{active.academic_year}</span>
      </div>
      <svg
        ref={chartRef}
        className="opt-chart"
        viewBox={`0 0 ${width} 335`}
        role="img"
        aria-labelledby="opt-chart-title opt-chart-description"
      >
        <title id="opt-chart-title">
          Students on Optional Practical Training, {rows[0].academic_year} to{" "}
          {rows.at(-1).academic_year}
        </title>
        <desc id="opt-chart-description">
          Annual Open Doors counts. Values fluctuate, including a decline
          through 2021/22. Use the data table below for every value.
        </desc>
        {y.ticks(3).map((tick) => (
          <g key={tick}>
            <line
              x1="48"
              x2={width - 28}
              y1={y(tick)}
              y2={y(tick)}
              className="grid-line"
            />
            <text x="36" y={y(tick) + 4} textAnchor="end">
              {tick === 0 ? "0" : `${tick / 1000}k`}
            </text>
          </g>
        ))}
        {x
          .ticks(width < 500 ? 2 : 4)
          .filter(Number.isInteger)
          .map((tick) => (
            <text key={tick} x={x(tick)} y="319" textAnchor="middle">
              {tick}/{String(tick + 1).slice(-2)}
            </text>
          ))}
        <path d={path} className="data-line" />
        {rows.map((row) => (
          <circle
            key={row.start_year}
            cx={x(row.start_year)}
            cy={y(row.opt_students)}
            r="7"
            className={row === active ? "data-dot selected" : "data-dot"}
            onMouseEnter={() => setActiveYear(row.start_year)}
            onClick={() => setActiveYear(row.start_year)}
          >
            <title>
              {row.academic_year}: {number(row.opt_students)} students
            </title>
          </circle>
        ))}
      </svg>
      <div className="chart-bottom">
        <a href={optUrl}>Source: IIE Open Doors 2025 ↗</a>
        <button
          onClick={() => setShowTable(!showTable)}
          aria-expanded={showTable}
          aria-controls="opt-values"
        >
          {showTable ? "Hide" : "View"} data table {showTable ? "−" : "+"}
        </button>
      </div>
      {showTable && (
        <div id="opt-values" className="table-scroll">
          <table>
            <caption>OPT participation by academic year</caption>
            <thead>
              <tr>
                <th scope="col">Academic year</th>
                <th scope="col">Students on OPT</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.academic_year}>
                  <th scope="row">{row.academic_year}</th>
                  <td>{number(row.opt_students)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
