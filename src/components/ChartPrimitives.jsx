import { useEffect, useRef, useState } from "react";

export function useChartWidth(initial = 700) {
  const ref = useRef(null);
  const [width, setWidth] = useState(initial);
  useEffect(() => {
    let frame;
    const observer = new ResizeObserver(([entry]) => {
      const next = Math.round(entry.contentRect.width);
      if (next > 0) {
        cancelAnimationFrame(frame);
        frame = requestAnimationFrame(() => setWidth(previous => previous === next ? previous : next));
      }
    });
    observer.observe(ref.current);
    return () => { observer.disconnect(); cancelAnimationFrame(frame); };
  }, []);
  return [ref, width];
}

export function ChartMeta({ source, href, period, unit }) {
  return <div className="chart-meta"><a href={href}>{source} ↗</a><span>{period}</span><span><b>Unit:</b> {unit}</span></div>;
}

export function Tooltip({ children }) {
  return <div className="chart-tooltip" role="tooltip">{children}</div>;
}

export function EvidenceRow({ label, children }) {
  return <div className="evidence-row"><span>{label}</span><strong>{children}</strong></div>;
}
