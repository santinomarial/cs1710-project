import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { parseIndustries, parseOverlap, parseOptEmployers, industryRows, comparisonRows, nationalShare, nameFormat } from "../src/chartData.js";

const read = name => readFileSync(new URL(`../data/processed/${name}`, import.meta.url), "utf8");
const industries = parseIndustries(read("uscis_fy2025_industries.csv"));
const overlap = parseOverlap(read("opt_h1b_employer_overlap.csv"));

test("industry shares retain missing classifications in the national denominator", () => {
  assert.equal(industries.length, 21);
  assert.equal(industries.reduce((s, d) => s + d.initial_approvals, 0), 114804);
  const missing = industries.find(d => !d.naics_code);
  assert.equal(missing.initial_approvals, 2215);
  const education = industries.find(d => d.naics_code === "61");
  assert.equal(education.initial_approvals, 15966);
  assert.equal(nationalShare(education, industries), 100 * 15966 / 114804);
  assert.equal(education.new_employment_approvals + education.new_concurrent_approvals, 15966);
});

test("industry search reaches sectors outside the initial top ten", () => {
  assert.equal(industryRows(industries).length, 10);
  assert.equal(industryRows(industries, { all: true }).length, 20);
  assert.equal(industryRows(industries, { query: "92" })[0].industry, "Public Administration");
  assert.equal(industryRows(industries, { query: "nonsense industry" }).length, 0);
  assert.equal(industryRows(industries)[0].initial_approvals, 44180);
});

test("47 accepted comparisons preserve source counts, not combined sums or ratios", () => {
  assert.equal(overlap.length, 47);
  const h = overlap.find(d => d.employer_name === "Harvard University");
  assert.equal(h.total_opt_or_stem_opt_participants, 1036);
  assert.equal(h.opt_participants, 799);
  assert.equal(h.stem_opt_participants, 407);
  assert.notEqual(h.total_opt_or_stem_opt_participants, h.opt_participants + h.stem_opt_participants);
  assert.equal(h.h1b_initial_approvals, 112);
  assert.equal(h.uscis_source_lines, "24394");
  assert.equal(h.source_page, "1");
  assert.equal(new Set(overlap.map(d => d.uscis_employer_group_id)).size, 47);
});

test("name format categories describe preserved strings only", () => {
  const counts = overlap.reduce((acc, d) => ({ ...acc, [d.match_type]: (acc[d.match_type] ?? 0) + 1 }), {});
  assert.deepEqual(counts, { case_space: 28, verbatim: 15, formatting: 4 });
  assert.equal(nameFormat("HARVARD", "HARVARD"), "verbatim");
  assert.equal(nameFormat("Harvard  University", "HARVARD UNIVERSITY"), "case_space");
  const formatted = comparisonRows(overlap, { types: ["formatting"] });
  assert.equal(formatted.plotted.length, 4);
  assert.ok(formatted.plotted.some(d => d.employer_name === "Bain & Company, Inc."));
});

test("missing STEM is not plotted at zero, and remains available for inspection", () => {
  const { plotted, missing, filtered } = comparisonRows(overlap, { metric: "stem_opt_participants" });
  assert.equal(filtered.length, 47);
  assert.equal(plotted.length, 46);
  assert.equal(missing.length, 1);
  assert.equal(missing[0].employer_name, "Carnegie Mellon University");
  assert.equal(missing[0].stem_opt_participants, null);
  assert.ok(plotted.every(d => d.stem_opt_participants > 0));
});

test("search respects name filters and has honest empty states", () => {
  assert.equal(comparisonRows(overlap, { query: " HARVARD " }).plotted.length, 1);
  assert.equal(comparisonRows(overlap, { query: "harvard", types: ["verbatim"] }).plotted.length, 0);
  assert.equal(comparisonRows(overlap, { types: [] }).filtered.length, 0);
  assert.equal(comparisonRows(overlap, { query: "Amazon" }).filtered.length, 0);
});

test("ICE table preserves all records, missing cells and original combined observations", () => {
  const rows = parseOptEmployers(read("opt_employers.csv"));
  assert.equal(rows.length, 200);
  assert.equal(rows.filter(d => d.stem_opt_participants === null).length, 11);
  assert.equal(rows[0].employer_name, "Amazon");
  assert.equal(rows[0].total_opt_or_stem_opt_participants, 10167);
  assert.equal(rows.find(d => d.employer_name === "Apple").total_opt_or_stem_opt_participants, 1621);
});

test("unexpected populations, components and missing required counts fail visibly", () => {
  assert.throws(() => parseOverlap(read("opt_h1b_employer_overlap.csv").replace(",accepted_unique_name,", ",unresolved,")), /population/);
  assert.throws(() => parseIndustries(read("uscis_fy2025_industries.csv").replace(",44180,", ",44181,")), /components/);
  assert.throws(() => parseIndustries(read("uscis_fy2025_industries.csv").replace(",44180,", ",,")), /count/);
});
