"""ICE source controls, missingness, conservative matching and reproducibility."""
import copy
import csv
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pdfplumber
from scripts import ice, download
from scripts.pipeline import RAW, OUT


class ICETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.employers = ice.extract(RAW / ice.FILE)
        with (OUT / 'uscis_fy2025_employers.csv').open() as f:
            cls.groups = list(csv.DictReader(f))
        cls.datasets, cls.report = ice.build(RAW, cls.groups)
        cls.by_name = {r['employer_name']: r for r in cls.employers}

    def test_original_checksum_and_complete_four_page_coverage(self):
        self.assertEqual(hashlib.sha256((RAW / ice.FILE).read_bytes()).hexdigest(),
                         'e4e306a6ce75e347a2bc87b88403f5cb1eadc2707b6880c04faf259688860f3f')
        self.assertEqual(len(self.employers), 200)
        self.assertEqual([sum(r['source_page']==p for r in self.employers) for p in range(1,5)], [58,63,63,16])
        self.assertEqual([r['employer_name'] for r in self.employers if r['source_table_row']==1],
                         ['Amazon', 'HCL Technologies', "Brigham & Women's Hospital", 'Texas Instruments'])
        self.assertEqual(self.employers[-1]['employer_name'], 'Brown University')

    def test_each_output_cell_agrees_with_original_pdf_table(self):
        with pdfplumber.open(RAW / ice.FILE) as doc:
            for row in self.employers:
                page = doc.pages[row['source_page']-1]
                table = page.extract_tables()[0]
                offset = 0 if row['source_page']==1 else -1
                original = table[row['source_table_row']+offset]
                self.assertEqual(row['employer_name'], ' '.join(original[0].split()))
                for field, value in zip(ice.FIELDS, original[1:]):
                    self.assertEqual(row[field], int(value.replace(',','')) if value else None)

    def test_five_visually_verified_source_controls_and_no_sum_reconstruction(self):
        expected = {'Amazon': (10167,5379,6679), 'Google': (2454,1110,1778),
                    'Microsoft': (2143,1066,1496), 'Meta': (2032,1081,1302), 'Apple': (1621,1135,973)}
        for name, values in expected.items():
            row = self.by_name[name]
            self.assertEqual(tuple(row[f] for f in ice.FIELDS), values)
            self.assertNotEqual(row[ice.FIELDS[0]], row[ice.FIELDS[1]]+row[ice.FIELDS[2]])
            self.assertEqual(row['source_page'], 1)
        self.assertIn('counted multiple times', self.report['source_caveat_verbatim'])

    def test_missing_cells_zero_and_clipped_name_are_not_invented(self):
        blanks = [r for r in self.employers if r['stem_opt_participants'] is None]
        self.assertEqual(len(blanks),11)
        self.assertEqual(self.by_name['Carnegie Mellon University']['stem_opt_participants'],None)
        self.assertEqual(self.by_name['New York University']['stem_opt_participants'],1)
        self.assertEqual(ice.participant_count('0'),0)
        self.assertIsNone(ice.participant_count(''))
        self.assertIsNone(ice.participant_count(None))
        self.assertEqual(sum(r[f]==0 for r in self.employers for f in ice.FIELDS),0)
        self.assertTrue(self.by_name[ice.TRUNCATED]['name_note'])
        for value in ['1,23', '-1', '—', 'N/A', 'suppressed', '1.2']:
            with self.assertRaises(ValueError): ice.participant_count(value)

    def test_reject_truncation_missing_imputation_changed_controls_and_periods(self):
        for mutate in [lambda rows: rows.pop(), lambda rows: rows[0].update(calendar_year=2025),
                       lambda rows: rows[0].update(total_opt_or_stem_opt_participants=12058),
                       lambda rows: next(r for r in rows if r['stem_opt_participants'] is None).update(stem_opt_participants=0),
                       lambda rows: rows[0].update(counting_note=''),
                       lambda rows: rows[1].update(employer_name=rows[0]['employer_name'])]:
            rows=copy.deepcopy(self.employers); mutate(rows)
            with self.assertRaises(ValueError): ice.validate_employers(rows)

    def test_matching_outcomes_and_all_200_audit_decisions(self):
        self.assertEqual(self.report['matching_status_counts'], {
            'accepted_unique_name':47, 'ambiguous_multiple_name_matches':7, 'ambiguous_name_scope':7,
            'no_candidate':41, 'source_name_truncated':1, 'unresolved_name_variants':97})
        audit=self.datasets['opt_h1b_match_audit.csv']
        self.assertEqual(len(audit),200)
        statuses={r['ice_employer_name']:r['match_status'] for r in audit}
        for name in ['Amazon','Google','Microsoft','Meta','Apple','University of California']:
            self.assertEqual(statuses[name],'unresolved_name_variants')
        for name in ['University of Michigan','Columbia University','Texas A&M University','Fidelity Investments','ADOBE INC','Michigan State University','Ford Motor Company']:
            self.assertEqual(statuses[name],'ambiguous_multiple_name_matches')
        for name in ['Johns Hopkins University','University of Maryland','Indiana University','University of Minnesota','AECOM','Vanderbilt University','California Institute of Technology']:
            self.assertEqual(statuses[name],'ambiguous_name_scope')
        self.assertEqual(statuses[ice.TRUNCATED],'source_name_truncated')

    def test_overlap_uses_exact_source_values_periods_and_one_to_one_groups(self):
        overlap=self.datasets['opt_h1b_employer_overlap.csv']
        groups={g['employer_group_id']:g for g in self.groups}
        self.assertEqual(len({r['uscis_employer_group_id'] for r in overlap}),47)
        for r in overlap:
            original=self.by_name[r['employer_name']]; group=groups[r['uscis_employer_group_id']]
            self.assertEqual(ice.name_key(r['employer_name']),ice.name_key(group['employer_name']))
            self.assertEqual((r['calendar_year'],r['h1b_fiscal_year']),(2024,2025))
            self.assertEqual(r['h1b_initial_approvals'],int(group['initial_approvals']))
            self.assertEqual(r['h1b_initial_approvals'],r['h1b_new_employment_approvals']+r['h1b_new_concurrent_approvals'])
            for f in ice.FIELDS:self.assertEqual(r[f],original[f])
            self.assertIn('not individual transitions or conversion rates',r['comparison_label'])
            self.assertFalse(any('rate' in k or 'transition' in k for k in r))
        harvard=next(r for r in overlap if r['employer_name']=='Harvard University')
        self.assertEqual((harvard['total_opt_or_stem_opt_participants'],harvard['h1b_initial_approvals']),(1036,112))
        carnegie=next(r for r in overlap if r['employer_name']=='Carnegie Mellon University')
        self.assertIsNone(carnegie['stem_opt_participants'])

    def test_saved_outputs_and_report_reproduce_exactly(self):
        for name,rows in self.datasets.items():
            buffer=io.StringIO(newline='');writer=csv.DictWriter(buffer,fieldnames=rows[0].keys())
            writer.writeheader();writer.writerows(rows)
            self.assertEqual((OUT/name).read_bytes(),buffer.getvalue().encode(),name)
        # JSON page keys become strings on serialization.
        self.assertEqual(json.loads((OUT/'ice_2024_validation.json').read_text()),json.loads(json.dumps(self.report)))

    def test_refresh_preserves_manual_source_and_historical_alias_without_network(self):
        manual=next(r for r in json.loads((RAW/'manifest.json').read_text()) if r['file']==ice.FILE)
        old={'file':'opt_employers_2024.pdf','url':ice.URL,'status':'blocked','error':'HTTP 403 historical attempt'}
        for managed_name in ['opt_employers_2024.pdf',ice.FILE]:
            with tempfile.TemporaryDirectory() as temp:
                raw=Path(temp);(raw/ice.FILE).write_bytes((RAW/ice.FILE).read_bytes())
                initial=[manual,old] if managed_name!=ice.FILE else [manual]
                (raw/'manifest.json').write_text(json.dumps(initial))
                with patch.object(download,'RAW',raw),patch.object(download,'SOURCES',{managed_name:ice.URL}),patch('sys.argv',['download.py','--refresh']),patch.object(download,'fetch') as fetch,redirect_stdout(io.StringIO()):
                    download.main();fetch.assert_not_called()
                saved=json.loads((raw/'manifest.json').read_text())
                self.assertEqual(next(r for r in saved if r['file']==ice.FILE),manual)
                self.assertEqual((raw/ice.FILE).read_bytes(),(RAW/ice.FILE).read_bytes())


class MatchingRuleTests(unittest.TestCase):
    def row(self,name):
        return dict(employer_name=name,calendar_year=2024,source_page=1,source_table_row=1,name_note='',
                    total_opt_or_stem_opt_participants=4,opt_participants=3,stem_opt_participants=None)

    def group(self,name,identifier='g1',suffix='0123',approvals=2):
        return dict(employer_name=name,name_status='reported',employer_group_id=identifier,tax_id_suffix=suffix,
                    initial_approvals=approvals,new_employment_approvals=approvals,new_concurrent_approvals=0,
                    source_lines='10',source_file='Employer Information (1).csv',source_url='https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub')

    def test_formatting_only_matches_preserve_legal_words_and_zeros(self):
        overlap,_,_=ice.match_employers([self.row('Example & Company, Inc.')],[self.group('EXAMPLE AND COMPANY INC',approvals=0)])
        self.assertEqual(len(overlap),1)
        self.assertEqual(overlap[0]['h1b_initial_approvals'],0)
        self.assertIsNone(overlap[0]['stem_opt_participants'])
        self.assertNotEqual(ice.name_key('Example Inc'),ice.name_key('Example LLC'))
        self.assertNotEqual(ice.name_key('University X'),ice.name_key('University X East Campus'))

    def test_zero_approval_competitors_missing_ids_and_duplicate_ice_names_block_join(self):
        a=self.group('Example Inc');zero=self.group('EXAMPLE INC','g2','4567',0)
        self.assertEqual(ice.match_employers([self.row('Example Inc')],[a,zero])[0],[])
        for suffix in ['', '0']:
            self.assertEqual(ice.match_employers([self.row('Example Inc')],[self.group('Example Inc',suffix=suffix)])[0],[])
        self.assertEqual(ice.match_employers([self.row('Example Inc'),self.row('EXAMPLE INC')],[a])[0],[])

    def test_prefix_candidates_are_never_proof_of_affiliation(self):
        broad=self.group('Apple');unrelated=self.group('APPLE TREE DENTAL','g2')
        overlap,audit,candidates=ice.match_employers([self.row('Apple')],[broad,unrelated])
        self.assertEqual(overlap,[])
        self.assertEqual(audit[0]['match_status'],'ambiguous_name_scope')
        self.assertTrue(all(r['accepted']=='false' for r in candidates))
        self.assertEqual(ice.match_employers([self.row('Apple')],[self.group('Apple Inc')])[0],[])


if __name__=='__main__':unittest.main()
