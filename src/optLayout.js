import { extent, line, max, scaleLinear } from "d3";

// Geometry depends on the view and container, never on the inspected year.
export function optLayout(data, start, width) {
  const rows = data.filter(d => d.start_year >= start);
  const x = scaleLinear().domain(extent(rows, d => d.start_year)).range([48, width - 28]);
  const y = scaleLinear().domain([0, max(rows, d => d.opt_students)]).nice().range([286, 28]);
  const bands = rows.map((row, index) => ({
    row,
    left: index === 0 ? x.range()[0] : (x(rows[index - 1].start_year) + x(row.start_year)) / 2,
    right: index === rows.length - 1 ? x.range()[1] : (x(row.start_year) + x(rows[index + 1].start_year)) / 2,
  }));
  return { rows, x, y, bands, path: line().x(d => x(d.start_year)).y(d => y(d.opt_students))(rows) };
}
