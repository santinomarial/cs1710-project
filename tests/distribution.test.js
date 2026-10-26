import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { csvParse, csvFormat } from "d3";
import { parseEmployerDistribution, distributionScale, percentage } from "../src/distribution.js";
const original = readFileSync(new URL("../data/processed/uscis_fy2025_distribution.csv", import.meta.url), "utf8");
const modified = change => { const rows = csvParse(original); change(rows); return csvFormat(rows); };

test("real processed bins conserve named groups and approvals while accounting for unnamed records", () => {
  const { total, bins } = parseEmployerDistribution(original);
  assert.equal(total.population_employers, 29350);
  assert.equal(total.population_initial_approvals + total.excluded_unnamed_initial_approvals, 114804);
  assert.equal(total.excluded_unnamed_records, 11);
  assert.deepEqual(bins.map(d => d.employer_count), [18343, 8090, 1561, 1113, 144, 87, 12]);
  assert.equal(bins.reduce((s, d) => s + d.initial_approvals, 0), 114798);
});
test("row order does not change meaning", () => {
  assert.deepEqual(parseEmployerDistribution(modified(rows => rows.reverse())), parseEmployerDistribution(original));
});
test("missing, duplicate and overlapping bins fail", () => {
  for (const change of [r => r.pop(), r => { r[6] = r[5]; }, r => { r[1].lower_bound = "1"; }])
    assert.throws(() => parseEmployerDistribution(modified(change)));
});
test("invalid and missing values fail; small positive shares never display as zero", () => {
  for (const value of ["", "NaN", "Infinity", "-1", "101"])
    assert.throws(() => parseEmployerDistribution(modified(r => { r[1].approval_share_percent = value; })));
  for (const value of ["", "1.5", "-1"])
    assert.throws(() => parseEmployerDistribution(modified(r => { r[1].employer_count = value; })));
  assert.equal(percentage(12 / 29350 * 100), "<0.1%");
  assert.equal(percentage(0), "0.0%");
});
test("rejects lost source, changed populations, periods, and totals", () => {
  for (const [key, value] of [["source_file", ""], ["source_url", ""], ["fiscal_year", "2024"],
    ["population", "unique workers"], ["identity_method", "tax_suffix_only"], ["source_type", "secondary"],
    ["population_employers", "29351"], ["excluded_unnamed_initial_approvals", "0"]])
    assert.throws(() => parseEmployerDistribution(modified(r => { r[2][key] = value; })));
});
test("rejects inconsistent counts, percentages and bin totals", () => {
  for (const [key, value] of [["employer_count", "100"], ["initial_approvals", "1"], ["employer_share_percent", "50"]])
    assert.throws(() => parseEmployerDistribution(modified(r => { r[2][key] = value; })));
  assert.throws(() => parseEmployerDistribution(modified(r => r.forEach(d => { d.population_initial_approvals = "114804"; }))));
});
test("both measures use a fixed zero-to-100 domain at mobile and desktop widths", () => {
  const { bins } = parseEmployerDistribution(original);
  for (const width of [240, 254, 324, 640, 1106]) {
    const x = distributionScale(width);
    assert.deepEqual(x.domain(), [0, 100]);
    for (const row of bins) for (const metric of ["employer_share_percent", "approval_share_percent"]) {
      assert.ok(Math.abs((x(row[metric]) - x(0)) / (x(100) - x(0)) - row[metric] / 100) < 1e-10);
      assert.ok(x(row[metric]) < width);
    }
  }
});
