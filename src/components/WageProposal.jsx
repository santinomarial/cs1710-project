export default function WageProposal() {
  return <div className="wage-proposal">
    <div className="population-note"><span className="eyebrow accent">Proposed design / data unavailable</span><p>The matched DOL and BLS inputs are unavailable. No salary values, differences or wage findings are shown.</p></div>
    <div className="proposal-steps"><span><b>01</b> Match occupations</span><span><b>02</b> Align reporting periods</span><span><b>03</b> Match geography & wage basis</span></div>
    <div className="viz-split">
      <div className="plot-card wage-canvas"><span className="eyebrow accent">Planned comparison canvas</span><h3>One row per matched occupation.</h3><div className="wage-empty"><span className="empty-symbol" aria-hidden="true">—</span><h4>Waiting for comparable evidence.</h4><p>Once validated records are available, paired dots will place a DOL filing-level offered-wage median and a BLS occupational median on a common annual-USD scale.</p><span className="small">No quantitative marks or numeric wage ticks yet.</span></div><p className="small">Missing or incompatible occupations will receive an explicit status, never a zero.</p></div>
      <aside className="detail-card wage-legend"><span className="eyebrow accent">Legend / proposed encoding only</span><div><span className="match-symbol verbatim" aria-hidden="true" /><p><b>DOL offered wages</b>Median offered annual wage across eligible H-1B filings.</p></div><div><span className="match-symbol formatting" aria-hidden="true" /><p><b>BLS occupational median</b>Published annual median for the matched occupation, geography and reference period.</p></div><p className="small">Planned selection panel: occupation code, sample size, exclusions, wage units, periods and source definitions.</p></aside>
    </div>
    <div className="context-band"><p><b>Two distinct measurements.</b> Offered filing wages do not establish actual pay. The two medians have different weighting and coverage.</p><p><b>A question, not a finding.</b> No wage premium, underpayment or causal effect is established by this proposal.</p></div>
    <p className="source-note">Planned sources: DOL FY2025 Q4 LCA disclosure and record layout; BLS occupational wage estimates with compatible SOC definitions, annual units, geography and reference period. The BLS comparison vintage remains undecided.</p>
  </div>;
}
