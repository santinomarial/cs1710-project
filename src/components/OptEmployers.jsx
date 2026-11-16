import { useState } from "react";
import { optEmployers, number } from "../data";
import { ChartMeta } from "./ChartPrimitives";

export default function OptEmployers() {
  const [query, setQuery] = useState("");
  const fmt = n => n === null ? "Not reported" : number(n);
  const matches = optEmployers.filter(d => d.employer_name.toLowerCase().includes(query.toLowerCase()));
  return <div className="opt-employer-panel">
    <div className="opt-employer-lede"><h3>Leading employers,<br /><em>not the whole population.</em></h3><ChartMeta source="ICE / SEVIS" href={optEmployers[0].source_url} period="Calendar 2024 · Jan–Dec" unit="OPT / STEM OPT participation" /><p>This published top-200 list covers leading employers, not all OPT employment or unique students across employers.</p><p className="small">The source’s combined count is independent: OPT and STEM OPT must not be added to reconstruct it. A student can be counted multiple times across programs.</p><a href={optEmployers[0].source_url}>Read the original ICE table ↗</a></div>
    <div className="opt-ranking"><div className="list-heading"><span>FIRST SIX EMPLOYERS AS LISTED</span><span>COMBINED COUNT</span></div>{optEmployers.slice(0, 6).map(d => <div className="opt-rank-row" key={d.source_order}><span>{String(d.source_order).padStart(2, "0")}</span><div><b>{d.employer_name}</b><small>OPT {fmt(d.opt_participants)} · STEM OPT {fmt(d.stem_opt_participants)}</small></div><strong>{fmt(d.total_opt_or_stem_opt_participants)}</strong></div>)}<p className="small">Combined = total OPT or STEM OPT participation, as reported. Names retain the source’s corporate or campus scope.</p></div>
    <details className="viz-data"><summary>Explore all 200 source employers <span>+</span></summary><label className="control-label">Search the ICE employer table<input type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder="Employer name" /></label><p className="small" role="status">{matches.length} source records. Blank source cells display as “Not reported”.</p><div className="table-scroll"><table><caption>Calendar 2024 · ICE source counts · not unique people across employers</caption><thead><tr><th>Employer as reported</th><th>Combined</th><th>OPT</th><th>STEM OPT</th><th>PDF page</th></tr></thead><tbody>{matches.map(d => <tr key={d.source_order}><th scope="row">{d.employer_name}{d.name_note && <small className="source-cell-note">{d.name_note}</small>}</th><td>{fmt(d.total_opt_or_stem_opt_participants)}</td><td>{fmt(d.opt_participants)}</td><td>{fmt(d.stem_opt_participants)}</td><td><a href={`${d.source_url}#page=${d.source_page}`}>{d.source_page}</a></td></tr>)}</tbody></table></div></details>
  </div>;
}
