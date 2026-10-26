"""Independent raw-source reconciliation, derivation regressions and import failure cases."""
import csv
import hashlib
import io
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from scripts import uscis, download
from scripts.pipeline import RAW, OUT


class USCISTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_bytes = (RAW / uscis.FILE).read_bytes()
        cls.raw = list(csv.DictReader(io.StringIO(cls.raw_bytes.decode('utf-16')), delimiter='\t'))
        cls.records = uscis.read_records(RAW / uscis.FILE)
        with (OUT / 'h1b_industries.csv').open() as f:
            cls.nfap = [{**r, 'initial_approvals': int(r['initial_approvals'])} for r in csv.DictReader(f)]
        cls.datasets, cls.report = uscis.build(RAW, cls.nfap)

    def test_original_checksum_encoding_period_and_line_coverage(self):
        self.assertEqual(hashlib.sha256(self.raw_bytes).hexdigest(), '49299055b254ab1f950c9f86e43c548becacfba6f151bb9e345f61d6ddd6ec37')
        self.assertEqual(self.raw_bytes[:2], b'\xff\xfe')
        self.assertEqual(len(self.raw), 62415)
        self.assertEqual({r['Fiscal Year   '] for r in self.raw}, {'2025'})
        self.assertEqual([r['source_line'] for r in self.records], list(range(1, 62416)))
        self.assertEqual(self.records[1]['tax_id_suffix'], '0274')
        self.assertEqual(self.records[1]['petitioner_zip_code'], '06437')

    def test_numeric_fields_are_strict_and_never_imputed(self):
        self.assertEqual(uscis.integer('113,458'), 113458)
        self.assertEqual(uscis.integer('0'), 0)
        for value in ['', '1,23', '1.0', '-1', 'NaN', '—', '1e3', None]:
            with self.assertRaises(ValueError): uscis.integer(value)

    def test_all_category_totals_match_independent_raw_sums(self):
        for source, key in uscis.CATEGORIES.items():
            for singular, plural in [('Approval', 'approvals'), ('Denial', 'denials')]:
                expected = sum(int(r[f'{source} {singular}'].replace(',', '')) for r in self.raw)
                self.assertEqual(self.report['category_totals'][f'{key}_{plural}'], expected)
        t = self.report['category_totals']
        self.assertEqual((t['new_employment_approvals'], t['new_concurrent_approvals'], t['initial_approvals'], t['continuing_approvals']), (113458, 1346, 114804, 291543))
        for r in self.records:
            for result in ['approvals', 'denials']:
                self.assertEqual(r[f'initial_{result}'], r[f'new_employment_{result}'] + r[f'new_concurrent_{result}'])
                self.assertEqual(r[f'continuing_{result}'], sum(r[f'{k}_{result}'] for k in ['continuation', 'change_with_same_employer', 'change_of_employer', 'amended']))

    def test_every_employer_group_matches_exact_raw_identity_without_name_merging(self):
        expected = Counter()
        for r in self.raw:
            key = (r['Employer (Petitioner) Name'], r['Tax ID']) if r['Employer (Petitioner) Name'].strip() else ('unnamed', r['Line by line'])
            expected[key] += int(r['New Employment Approval'].replace(',', '')) + int(r['New Concurrent Approval'].replace(',', ''))
        employers = self.datasets['uscis_fy2025_employers.csv']
        self.assertEqual(len(employers), len(expected))
        for g in employers:
            key = (g['employer_name'], g['tax_id_suffix']) if g['name_status']=='reported' else ('unnamed', g['source_lines'])
            self.assertEqual(g['initial_approvals'], expected[key])
        unnamed = [g for g in employers if g['name_status'] == 'missing']
        self.assertEqual(len(unnamed), 11)
        self.assertTrue(all(g['employer_name'] == '' and g['source_record_count'] == 1 for g in unnamed))
        self.assertEqual(sum(g['initial_approvals'] for g in unnamed), 6)
        self.assertEqual(self.report['missing']['tax_id_suffix'], 198)
        self.assertEqual(self.report['nonstandard_tax_suffix_records'], 1)

    def test_every_industry_matches_raw_and_nfap_is_separate(self):
        expected = Counter()
        for r in self.raw:
            expected[r['Industry (NAICS) Code']] += int(r['New Employment Approval'].replace(',', '')) + int(r['New Concurrent Approval'].replace(',', ''))
        for d in self.datasets['uscis_fy2025_industries.csv']:
            label = f'{d["naics_code"]} - {d["industry"]}' if d['naics_code'] else ''
            self.assertEqual(d['initial_approvals'], expected[label])
        comparison = self.datasets['uscis_fy2025_industry_comparison.csv']
        self.assertEqual(sum(d['difference_uscis_minus_nfap'] or 0 for d in comparison), -10)
        unknown = next(d for d in comparison if d['naics_code'] == '')
        self.assertEqual(unknown['uscis_initial_approvals'], 2215)
        self.assertIsNone(unknown['nfap_initial_approvals'])
        self.assertEqual(self.report['initial_difference'], -2)
        self.assertEqual(self.report['continuing_difference'], 1)

    def test_bins_assign_each_named_positive_group_once_and_conserve_counts(self):
        groups = self.datasets['uscis_fy2025_employers.csv']
        bins = self.datasets['uscis_fy2025_distribution.csv']
        actual = Counter()
        approvals = Counter()
        for g in groups:
            if g['name_status'] == 'missing' or g['initial_approvals'] == 0: continue
            matched = [b for b in bins if g['initial_approvals'] >= b['lower_bound'] and (b['upper_bound'] is None or g['initial_approvals'] <= b['upper_bound'])]
            self.assertEqual(len(matched), 1)
            actual[matched[0]['bin_order']] += 1
            approvals[matched[0]['bin_order']] += g['initial_approvals']
        for b in bins:
            self.assertEqual(b['employer_count'], actual[b['bin_order']])
            self.assertEqual(b['initial_approvals'], approvals[b['bin_order']])
        self.assertEqual(sum(actual.values()), 29350)
        self.assertEqual(sum(approvals.values()), 114798)

    def test_all_saved_primary_csvs_reproduce_exactly(self):
        for name, rows in self.datasets.items():
            output = io.StringIO(newline='')
            writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader(); writer.writerows(rows)
            self.assertEqual((OUT / name).read_bytes(), output.getvalue().encode('utf-8'), name)
        self.assertEqual(json.loads((OUT / 'uscis_fy2025_reconciliation.json').read_text()), self.report)

    def test_reject_wrong_encoding_headers_year_duplicate_lines_and_missing_counts(self):
        text = self.raw_bytes.decode('utf-16')
        samples = [b'not UTF16', text.replace('Fiscal Year', 'Unknown Year', 1).encode('utf-16'),
                   text.replace('\t2025\t', '\t2024\t', 1).encode('utf-16'),
                   text.replace('2\t2025\t', '1\t2025\t', 1).encode('utf-16'),
                   text.replace('\t0\t0\t', '\t\t0\t', 1).encode('utf-16')]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'export.csv'
            for content in samples:
                path.write_bytes(content)
                with self.assertRaises(ValueError): uscis.read_records(path)

    def test_downloader_preserves_manual_provenance_and_rejects_modified_original(self):
        manifest = json.loads((RAW / 'manifest.json').read_text())
        preserved = download.preserved_manual_records(manifest)
        source = next(r for r in preserved if r['file'] == uscis.FILE)
        self.assertIsNone(source['retrieved_at_utc'])
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / uscis.FILE).write_bytes(b'changed')
            with patch.object(download, 'RAW', Path(temp)):
                with self.assertRaises(ValueError): download.preserved_manual_records([source])


if __name__ == '__main__': unittest.main()
