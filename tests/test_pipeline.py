"""Source-backed regressions plus failure cases for the data cleaning rules."""
import copy
import csv
import hashlib
import json
import unittest

from scripts.pipeline import ROOT, OUT, count, employer_key, year, validate
from scripts.ice import FIELDS


class CleaningTests(unittest.TestCase):
    def test_missing_is_not_zero(self):
        for value in [None, '', '-', 'no data']:
            self.assertIsNone(count(value))
        self.assertEqual(count(0), 0)

    def test_reject_bad_counts(self):
        for value in [-1, '12.2', 'NaN', 'inf', 'suppressed']:
            with self.assertRaises(ValueError):
                count(value)
        self.assertEqual(count(780055.0000000005), 780055)
        self.assertEqual(count('294,253'), 294253)

    def test_source_footnotes_and_names(self):
        self.assertEqual(year('2020/21*****'), '2020/21')
        self.assertIsNone(year('FY2025'))
        self.assertEqual(employer_key(' Cummins Inc. '), 'CUMMINS INC')
        self.assertEqual(employer_key('Ernst & Young'), 'ERNST AND YOUNG')
        self.assertNotEqual(employer_key('Amazon'), employer_key('Amazon Web Services Inc'))


class OutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((OUT / 'validation.json').read_text())
        cls.tables = {}
        numeric = {'start_year', 'enrolled_students', 'opt_students', 'total_international_students',
                   'us_higher_education_enrollment', 'students', 'initial_approvals', 'approvals', 'fiscal_year',
                   *FIELDS, 'calendar_year', 'h1b_fiscal_year', 'source_order', 'source_page', 'source_table_row',
                   'h1b_initial_approvals', 'h1b_new_employment_approvals', 'h1b_new_concurrent_approvals', 'candidate_initial_approvals'}
        for name in cls.report['datasets']:
            with (OUT / name).open() as file:
                cls.tables[name] = [dict((k, (int(v) if v else None) if k in numeric else v)
                                         for k, v in r.items()) for r in csv.DictReader(file)]

    def test_all_outputs_and_manifest(self):
        validate(self.tables)
        self.assertEqual(set(p.name for p in OUT.glob('*.csv')), set(self.report['datasets']))
        for name, metadata in self.report['datasets'].items():
            self.assertEqual(len(self.tables[name]), metadata['rows'])
            self.assertEqual(list(self.tables[name][0]), metadata['columns'])
        for record in json.loads((ROOT / 'data/raw/manifest.json').read_text()):
            if record['status'] in {'downloaded', 'provided_local'}:
                self.assertEqual(hashlib.sha256((ROOT / 'data/raw' / record['file']).read_bytes()).hexdigest(), record['sha256'])

    def test_duplicate_and_corrupted_data_fail(self):
        for name, mutate in [
            ('opt_growth.csv', lambda rows: rows.append(rows[0].copy())),
            ('opt_growth.csv', lambda rows: rows[0].update(opt_students=-1)),
            ('h1b_employers.csv', lambda rows: rows.pop()),
            ('academic_levels.csv', lambda rows: next(r for r in rows if r['academic_level'] == 'opt').update(students=0)),
        ]:
            tables = copy.deepcopy(self.tables)
            mutate(tables[name])
            with self.assertRaises(ValueError):
                validate(tables)

    def test_wrapped_names_and_source_discrepancies(self):
        names = {r['employer_name'] for r in self.tables['h1b_employers.csv']}
        self.assertIn('NEW YORK CITY HEALTH AND HOSPITALS CORPORATION', names)
        self.assertIn('MANAGEMENT HEALTH SYSTEMS LLC DBA MEDPRO INTERNATIONAL', names)
        self.assertEqual(sum(r['initial_approvals'] for r in self.tables['h1b_industries.csv']), 112599)
        self.assertEqual(len(self.tables['fields_of_study.csv']), 405)

    def test_unavailable_is_not_fabricated(self):
        for name in self.report['unavailable']:
            self.assertFalse((OUT / name).exists())
        distribution = self.tables['h1b_employer_distribution.csv']
        self.assertEqual([float(r['value']) for r in distribution], [28277, 61, 95])
        self.assertNotIn('employer_count', distribution[1])


if __name__ == '__main__':
    unittest.main()
