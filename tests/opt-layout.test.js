import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { csvParse } from "d3";
import { optLayout } from "../src/optLayout.js";

const rows = csvParse(readFileSync(new URL("../data/processed/opt_growth.csv", import.meta.url), "utf8"), d => ({
  ...d, start_year: +d.start_year, opt_students: +d.opt_students,
}));

test("OPT layouts preserve every real observation in both time ranges", () => {
  for (const start of [1979, 2005]) {
    const layout = optLayout(rows, start, 1100);
    assert.deepEqual(layout.rows, rows.filter(d => d.start_year >= start));
    assert.equal(layout.rows.at(-1).opt_students, 294253);
    assert.equal(layout.bands.length, start === 1979 ? 46 : 20);
    assert.equal(layout.y.domain()[0], 0);
    assert.ok(!/NaN|Infinity/.test(layout.path));
  }
});

test("year targets cover the plot without gaps or overlap at phone and desktop widths", () => {
  for (const width of [254, 324, 700, 1180]) for (const start of [1979, 2005]) {
    const { bands, x } = optLayout(rows, start, width);
    assert.equal(bands[0].left, x.range()[0]);
    assert.equal(bands.at(-1).right, x.range()[1]);
    bands.forEach(({ row, left, right }, i) => {
      assert.ok(right > left);
      assert.ok(x(row.start_year) >= left && x(row.start_year) <= right);
      if (i) assert.equal(left, bands[i - 1].right);
      assert.equal(rows.find(d => d.start_year === row.start_year), row);
    });
  }
});

test("sparse observations create targets only for observed years, without inventing counts", () => {
  const sparse = rows.filter(d => [2005, 2008, 2024].includes(d.start_year));
  const { bands, x } = optLayout(sparse, 2005, 700);
  assert.deepEqual(bands.map(d => d.row.start_year), [2005, 2008, 2024]);
  assert.equal(bands[0].right, (x(2005) + x(2008)) / 2);
  assert.equal(bands[1].right, (x(2008) + x(2024)) / 2);
});
