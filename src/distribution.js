import { csvParse, scaleLinear } from "d3";

const bins = [
  [1, 1, "1"], [2, 5, "2–5"], [6, 10, "6–10"], [11, 50, "11–50"],
  [51, 100, "51–100"], [101, 500, "101–500"], [501, null, "501+"],
];
function require(ok, message) {
  if (!ok) throw new Error(`H-1B distribution: ${message}`);
}
function numeric(value, integer = false) {
  require(typeof value === "string" && value.trim() !== "", "missing numeric value");
  const number = Number(value);
  require(Number.isFinite(number) && number >= 0 && (!integer || Number.isInteger(number)), "invalid numeric value");
  return number;
}
export function parseEmployerDistribution(text) {
  const rows = csvParse(text);
  require(rows.length === bins.length, "expected seven disjoint bins");
  const integers = ["bin_order", "lower_bound", "employer_count", "initial_approvals",
    "population_employers", "population_initial_approvals", "excluded_unnamed_records", "excluded_unnamed_initial_approvals"];
  const data = rows.map(row => {
    const d = { ...row };
    integers.forEach(key => { d[key] = numeric(row[key], true); });
    d.upper_bound = row.upper_bound === "" ? null : numeric(row.upper_bound, true);
    for (const key of ["employer_share_percent", "approval_share_percent"]) {
      d[key] = numeric(row[key]);
      require(d[key] <= 100, "share exceeds 100 percent");
    }
    require(row.fiscal_year === "2025" && row.source_type === "primary_USCIS_user_export", "unexpected period or source");
    require(row.source_file === "Employer Information (1).csv" && row.source_url === "https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub", "missing source attribution");
    require(row.identity_method === "exact_name_and_tax_suffix; unnamed_records_separate" &&
      row.population === "named employer groups with positive initial approvals", "unexpected population or identity method");
    return d;
  }).sort((a, b) => a.bin_order - b.bin_order);
  const total = data[0];
  require(total.population_employers > 0 && total.population_initial_approvals > 0, "empty population");
  for (const [index, d] of data.entries()) {
    const [lower, upper, label] = bins[index];
    require(d.bin_order === index + 1 && d.lower_bound === lower && d.upper_bound === upper && d.bin_label === label, "duplicate, missing, or overlapping bins");
    for (const key of ["population_employers", "population_initial_approvals", "excluded_unnamed_records", "excluded_unnamed_initial_approvals"]) {
      require(d[key] === total[key], `inconsistent ${key}`);
    }
    require(d.initial_approvals >= lower * d.employer_count && (upper === null || d.initial_approvals <= upper * d.employer_count), "approvals outside bin bounds");
    require(Math.abs(d.employer_share_percent - 100 * d.employer_count / total.population_employers) < 1e-8 &&
      Math.abs(d.approval_share_percent - 100 * d.initial_approvals / total.population_initial_approvals) < 1e-8, "shares disagree with counts");
  }
  require(data.reduce((sum, d) => sum + d.employer_count, 0) === total.population_employers &&
    data.reduce((sum, d) => sum + d.initial_approvals, 0) === total.population_initial_approvals, "bins do not conserve totals");
  return { total, bins: data };
}
export function distributionScale(width) {
  require(Number.isFinite(width) && width > 160, "invalid chart width");
  return scaleLinear().domain([0, 100]).range([72, width - 48]);
}
export function percentage(value) {
  return value > 0 && value < 0.1 ? "<0.1%" : `${value.toFixed(1)}%`;
}
