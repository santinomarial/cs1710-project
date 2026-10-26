import { useEffect, useRef, useState } from "react";

export function useChartWidth(initial = 700) {
  const ref = useRef(null);
  const [width, setWidth] = useState(initial);
  useEffect(() => {
    const observer = new ResizeObserver(([entry]) => {
      if (entry.contentRect.width > 0) setWidth(entry.contentRect.width);
    });
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);
  return [ref, width];
}

export function Tooltip({ children }) {
  return <div className="chart-tooltip" role="tooltip">{children}</div>;
}

export function EvidenceRow({ label, children }) {
  return <div className="evidence-row"><span>{label}</span><strong>{children}</strong></div>;
}
