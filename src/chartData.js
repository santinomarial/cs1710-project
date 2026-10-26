import { csvParse } from "d3";

function count(value, nullable = false) {
  if (nullable && value === "") return null;
  if (!/^\d+$/.test(value)) throw new Error(`Invalid source count: ${value}`);
  return Number(value);
}

export const MATCH_TYPES = {
  verbatim: { label: "Verbatim exact", shape: "circle" },
  case_space: { label: "Case / spacing only", shape: "ring" },
  formatting: { label: "Formatting-normalized", shape: "diamond" },
};

// Display categories for already-accepted pairs only. This is not an entity matcher.
export function nameFormat(a, b) {
  if (a === b) return "verbatim";
  const caseSpace = s => s.toUpperCase().trim().replace(/\s+/g, " ");
  return caseSpace(a) === caseSpace(b) ? "case_space" : "formatting";
}

export function parseIndustries(text) {
  return csvParse(text, row => {
    if (row.fiscal_year !== "2025") throw new Error("Unexpected industry period");
    const d = { ...row };
    for (const k of ["initial_approvals", "new_employment_approvals", "new_concurrent_approvals"]) d[k] = count(row[k]);
    if (d.initial_approvals !== d.new_employment_approvals + d.new_concurrent_approvals) throw new Error("Industry components disagree");
    return d;
  });
}

export function parseOverlap(text) {
  return csvParse(text, row => {
    if (row.calendar_year !== "2024" || row.h1b_fiscal_year !== "2025" || row.match_status !== "accepted_unique_name") throw new Error("Unexpected comparison population");
    const d = { ...row, match_type: nameFormat(row.employer_name, row.uscis_employer_name) };
    for (const k of ["total_opt_or_stem_opt_participants", "opt_participants", "stem_opt_participants"]) d[k] = count(row[k], true);
    for (const k of ["h1b_initial_approvals", "h1b_new_employment_approvals", "h1b_new_concurrent_approvals"]) d[k] = count(row[k]);
    if (d.h1b_initial_approvals !== d.h1b_new_employment_approvals + d.h1b_new_concurrent_approvals) throw new Error("Employer components disagree");
    return d;
  });
}

export function parseOptEmployers(text) {
  return csvParse(text, row => {
    if (row.calendar_year !== "2024") throw new Error("Unexpected ICE period");
    const d = { ...row };
    for (const k of ["total_opt_or_stem_opt_participants", "opt_participants", "stem_opt_participants"]) d[k] = count(row[k], true);
    return d;
  });
}

export const nationalShare = (row, all) => 100 * row.initial_approvals / all.reduce((sum, d) => sum + d.initial_approvals, 0);

export function industryRows(rows, { query = "", all = false, sort = "count" } = {}) {
  const q = query.trim().toLowerCase();
  const ranked = rows.filter(d => d.naics_code).slice().sort((a, b) => sort === "name"
    ? a.industry.localeCompare(b.industry)
    : b.initial_approvals - a.initial_approvals || a.naics_code.localeCompare(b.naics_code));
  return q ? ranked.filter(d => `${d.industry} ${d.naics_code}`.toLowerCase().includes(q)) : all ? ranked : ranked.slice(0, 10);
}

export function comparisonRows(rows, { query = "", types = Object.keys(MATCH_TYPES), metric = "total_opt_or_stem_opt_participants" } = {}) {
  const q = query.trim().toLowerCase();
  const filtered = rows.filter(d => types.includes(d.match_type) && `${d.employer_name} ${d.uscis_employer_name}`.toLowerCase().includes(q));
  return { filtered, plotted: filtered.filter(d => d[metric] !== null), missing: filtered.filter(d => d[metric] === null) };
}
