"""Deterministic CSV extraction from the versioned originals. No network access."""
import csv
import hashlib
import json
import math
import re
import unicodedata
from pathlib import Path

import openpyxl
import pdfplumber

try:
    from . import uscis, ice
except ImportError:  # Direct `python scripts/pipeline.py` invocation.
    import uscis
    import ice

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
OUT = ROOT / 'data/processed'
NFAP = 'https://nfap.com/wp-content/uploads/2025/11/H-1B-Petitions-and-Denial-Rates-For-FY-2025.NFAP-Policy-Brief.2025.pdf'
IIE = 'https://opendoorsdata.org/data/international-students/'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def count(value):
    """Missing is None, never zero; tolerate only Excel floating-point noise."""
    if value is None or str(value).strip() in {'', '-', '—', 'N/A', 'no data'}:
        return None
    number = float(str(value).replace(',', ''))
    require(math.isfinite(number) and number >= 0, f'Invalid count: {value}')
    require(abs(number - round(number)) < 1e-6, f'Noninteger count: {value}')
    return round(number)


def year(value):
    match = re.fullmatch(r'(\d{4}/\d{2})\**', str(value).strip())
    return match[1] if match else None


def employer_key(name):
    """Conservative comparison key. No suffix stripping, fuzzy or parent-company merges."""
    text = unicodedata.normalize('NFKC', name).upper().replace('&', ' AND ')
    return ' '.join(re.sub(r'[^\w\s]', ' ', text).split())


def workbook(name):
    return openpyxl.load_workbook(RAW / name, data_only=True)


def enrollment():
    rows = []
    sheet = workbook('open_doors_enrollment.xlsx').worksheets[0]
    require('1948/49 - 2024/25' in sheet['A1'].value, 'Enrollment edition changed')
    for number, row in enumerate(sheet.values, 1):
        academic_year = year(row[0])
        if not academic_year:
            continue
        rows.append(dict(academic_year=academic_year, start_year=int(academic_year[:4]),
                         enrolled_students=count(row[1]), opt_students=count(row[2]),
                         total_international_students=count(row[3]),
                         us_higher_education_enrollment=count(row[5]),
                         source_year_label=str(row[0]).strip(),
                         source_file='open_doors_enrollment.xlsx', source_row=number,
                         source_url=IIE + 'enrollment-trends/'))
    return rows


def academic_levels():
    rows = []
    sheet = workbook('open_doors_academic_level.xlsx')['Broad Academic Levels']
    for number, row in enumerate(sheet.values, 1):
        academic_year = year(row[0])
        if not academic_year:
            continue
        for label, column in [('undergraduate', 1), ('graduate', 3), ('non_degree', 5), ('opt', 7)]:
            value = count(row[column])
            if value is not None:
                rows.append(dict(academic_year=academic_year, academic_level=label, students=value,
                                 source_file='open_doors_academic_level.xlsx',
                                 source_sheet=sheet.title, source_row=number,
                                 source_url=IIE + 'academic-level/'))
    return rows


def fields():
    """Broad, bold source categories only: never sum parents and children together."""
    sheet = workbook('open_doors_fields.xlsx').worksheets[0]
    columns = [(c.column, year(c.value)) for c in sheet[3] if year(c.value)]
    rows = []
    for number in range(5, 74):
        cell = sheet.cell(number, 1)
        if not cell.value or not cell.font.bold:
            continue
        for column, academic_year in columns:
            value = count(sheet.cell(number, column).value)
            if value is not None:
                rows.append(dict(academic_year=academic_year,
                                 field_of_study=re.sub(r'\d+$', '', cell.value).strip(),
                                 source_category=cell.value.strip(), students=value,
                                 classification='Open Doors 2025 broad categories',
                                 source_file='open_doors_fields.xlsx', source_row=number,
                                 source_column=column, source_url=IIE + 'fields-of-study/'))
    return rows


def table(page):
    candidates = [t for t in page.extract_tables() if len(t) > 3]
    require(len(candidates) == 1, f'Unexpected tables on PDF page {page.page_number}')
    return candidates[0]


def nfap_data():
    employers, industries, selected = [], [], []
    with pdfplumber.open(RAW / 'nfap_fy2025.pdf') as doc:
        require(len(doc.pages) == 32, 'NFAP PDF edition changed')
        for index in [22, 23, 24]:
            for name, value in table(doc.pages[index]):
                if name == 'EMPLOYER':
                    continue
                name = ' '.join(name.split())
                employers.append(dict(fiscal_year=2025, employer_name=name,
                                      employer_key=employer_key(name), initial_approvals=count(value),
                                      coverage='NFAP Appendix Table 2: employers with 100+ initial approvals',
                                      source_type='secondary_analysis_of_USCIS', source_file='nfap_fy2025.pdf',
                                      source_page=index + 1, source_url=NFAP))
        for name, value in table(doc.pages[26])[1:]:
            industries.append(dict(fiscal_year=2025, industry=' '.join(name.split()),
                                   initial_approvals=count(value), source_type='secondary_analysis_of_USCIS',
                                   source_file='nfap_fy2025.pdf', source_page=27, source_url=NFAP))
        for index, approval_type in [(4, 'initial'), (11, 'continuing')]:
            for row in table(doc.pages[index])[1:]:
                require(len(row) == 7, 'Unexpected selected employer table columns')
                for column, fiscal_year in enumerate([2025, 2024, 2023], 1):
                    selected.append(dict(fiscal_year=fiscal_year, employer_name=' '.join(row[0].split()),
                                         approval_type=approval_type, approvals=count(row[column]),
                                         denial_rate_percent=float(row[column + 3].rstrip('%')),
                                         coverage='NFAP selected employers; affiliates consolidated by NFAP',
                                         source_file='nfap_fy2025.pdf', source_page=index + 1, source_url=NFAP))
        text = ' '.join(doc.pages[6].extract_text().split())
        total = re.search(r'([\d,]+) different employers in the United States', text)
        single = re.search(r'Sixty-one percent of employers were approved for a single H-1B petition', text)
        ten = re.search(r'(\d+)% were approved for ten or fewer new H-1B petitions', text)
        require(total and single and ten, 'NFAP distribution text changed; review manually')
        distribution = [
            dict(metric='employers_with_initial_approval', value=count(total[1]), unit='employers',
                 precision='reported_count', cumulative='true'),
            dict(metric='employer_share_exactly_1_initial_approval', value=61, unit='percent_of_employers',
                 precision='reported_rounded_percent', cumulative='false'),
            dict(metric='employer_share_1_to_10_initial_approvals', value=count(ten[1]), unit='percent_of_employers',
                 precision='reported_rounded_percent', cumulative='true'),
        ]
        for row in distribution:
            row.update(fiscal_year=2025, population='employers with at least one initial approval',
                       source_type='secondary_analysis_of_USCIS', source_file='nfap_fy2025.pdf',
                       source_page=7, source_url=NFAP)
    return employers, industries, selected, distribution


def validate(datasets):
    keys = {
        'international_enrollment.csv': ['academic_year'], 'opt_growth.csv': ['academic_year'],
        'academic_levels.csv': ['academic_year', 'academic_level'],
        'fields_of_study.csv': ['academic_year', 'field_of_study'],
        'h1b_employers.csv': ['fiscal_year', 'employer_key'],
        'h1b_industries.csv': ['fiscal_year', 'industry'],
        'h1b_selected_petitions.csv': ['fiscal_year', 'employer_name', 'approval_type'],
        'h1b_employer_distribution.csv': ['fiscal_year', 'metric'],
        'opt_employers.csv': ['calendar_year', 'employer_name'],
        'opt_h1b_employer_overlap.csv': ['calendar_year', 'h1b_fiscal_year', 'employer_name'],
        'opt_h1b_match_audit.csv': ['calendar_year', 'h1b_fiscal_year', 'ice_employer_name'],
        'opt_h1b_match_candidates.csv': ['ice_employer_name', 'uscis_employer_group_id'],
    }
    checks = []
    for name, rows in datasets.items():
        if name.startswith(uscis.PREFIX):
            continue  # The primary-source module validates these before export.
        require(rows, f'Empty dataset: {name}')
        identifiers = [tuple(r[k] for k in keys[name]) for r in rows]
        require(len(identifiers) == len(set(identifiers)), f'Duplicate keys: {name}')
        for row in rows:
            require(row.keys() == rows[0].keys(), f'Inconsistent columns: {name}')
            require((RAW / row['source_file']).is_file(), f'Missing original: {name}')
            for key, value in row.items():
                if key in {'students', 'enrolled_students', 'opt_students', 'total_international_students',
                           'us_higher_education_enrollment', 'initial_approvals', 'approvals',
                           *ice.FIELDS, 'h1b_initial_approvals', 'h1b_new_employment_approvals',
                           'h1b_new_concurrent_approvals', 'candidate_initial_approvals'} and value is not None:
                    require(isinstance(value, int) and value >= 0, f'Invalid {key}: {value}')
        checks.append(f'{name}: nonempty, unique keys, consistent schema, provenance, valid counts')
    enrolled = {r['academic_year']: r for r in datasets['international_enrollment.csv']}
    for row in datasets['opt_growth.csv']:
        require(row['enrolled_students'] + row['opt_students'] == row['total_international_students'],
                f'Enrollment identity fails: {row["academic_year"]}')
    for row in datasets['academic_levels.csv']:
        if row['academic_level'] == 'opt':
            expected_difference = 1 if row['academic_year'] == '1994/95' else 0
            require(row['students'] - enrolled[row['academic_year']]['opt_students'] == expected_difference,
                    'New cross-source OPT discrepancy; inspect the original workbooks')
    require(len(enrolled) == 77 and len(datasets['opt_growth.csv']) == 46, 'Enrollment coverage changed')
    require(len(datasets['h1b_employers.csv']) == 100, 'NFAP employer table truncated')
    require(all(r['initial_approvals'] >= 100 for r in datasets['h1b_employers.csv']), 'Employer coverage violation')
    require(len(datasets['h1b_industries.csv']) == 20, 'NFAP industries truncated')
    require(len(datasets['h1b_selected_petitions.csv']) == 150, 'Selected employer tables truncated')
    require(enrolled['2024/25']['opt_students'] == 294253, 'Latest OPT source control changed')
    require(next(r for r in datasets['h1b_employers.csv'] if r['employer_name'] == 'HARVARD UNIVERSITY')['initial_approvals'] == 112,
            'NFAP employer source control changed')
    if 'opt_employers.csv' in datasets:
        ice.validate_employers(datasets['opt_employers.csv'])
    checks.extend(['Enrolled + OPT = total in every available OPT year',
                   'OPT counts agree across workbooks except the documented one-student 1994/95 discrepancy',
                   'Pinned edition row counts and independently inspected source values match'])
    return checks


def main():
    manifest = json.loads((RAW / 'manifest.json').read_text())
    downloaded = {r['file'] for r in manifest if r['status'] in {'downloaded', 'provided_local'}}
    required = {'open_doors_enrollment.xlsx', 'open_doors_academic_level.xlsx', 'open_doors_fields.xlsx', 'nfap_fy2025.pdf', uscis.FILE, ice.FILE}
    require(required <= downloaded, f'Required originals unavailable: {sorted(required - downloaded)}; see manifest.json')
    for record in manifest:
        if record['status'] in {'downloaded', 'provided_local'}:
            require(hashlib.sha256((RAW / record['file']).read_bytes()).hexdigest() == record['sha256'],
                    f'Original checksum mismatch: {record["file"]}')
    enrolled = enrollment()
    employers, industries, selected, distribution = nfap_data()
    datasets = {
        'international_enrollment.csv': enrolled,
        'opt_growth.csv': [r for r in enrolled if r['opt_students'] is not None],
        'academic_levels.csv': academic_levels(), 'fields_of_study.csv': fields(),
        'h1b_employers.csv': employers, 'h1b_employer_distribution.csv': distribution,
        'h1b_industries.csv': industries, 'h1b_selected_petitions.csv': selected,
    }
    primary, reconciliation = uscis.build(RAW, industries)
    datasets.update(primary)
    ice_datasets, ice_report = ice.build(RAW, primary['uscis_fy2025_employers.csv'])
    datasets.update(ice_datasets)
    checks = validate(datasets)
    checks.extend(['ICE: all 200 employers across four pages agree between table and text extraction; five major-employer controls verified',
                   'ICE: eleven blank STEM OPT cells preserved; combined values never reconstructed',
                   'ICE/USCIS: only unique normalized full-name matches without prefix-scope conflicts accepted; all other candidates documented'])
    checks.extend(['USCIS: UTF-16 tab schema, all 62,415 sequential records, FY2025 and strict integer counts verified',
                   'USCIS: every approval/denial category conserved through employer and industry aggregation',
                   'USCIS: disjoint employer bins conserve named positive groups and initial approvals; unnamed approvals separately accounted for'])
    industry_total = sum(r['initial_approvals'] for r in industries)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows in datasets.items():
        with (OUT / name).open('w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    report = dict(status='passed_with_source_limitations', checks=checks,
                  datasets={name: {'rows': len(rows), 'columns': list(rows[0])} for name, rows in datasets.items()},
                  unavailable={
                      'wage_comparison.csv': 'BLS and DOL downloads returned HTTP 403. Fru employer-level summaries do not supply a matched occupational sample.'},
                  warnings=[
                      'IIE 1994/95 OPT counts differ: enrollment workbook 13,208; academic-level workbook 13,209. Both original values retained; opt_growth uses enrollment.',
                      'The historical NFAP extracts remain separate. The D3 distribution uses the complete supplied USCIS FY2025 export.',
                      'Employer groups use exact name plus four-digit tax suffix, not verified legal identities. Name variants remain separate; suffix collisions and missing suffixes limit identification.',
                      '11 unnamed records remain in the primary datasets; their 6 initial approvals are excluded from the named-employer histogram, not discarded from totals.',
                      'USCIS initial approvals total 114,804 versus NFAP 114,806: difference -2, unresolved. No adjustment applied.',
                      f'USCIS named industries total 112,589 versus NFAP {industry_total:,} (-10); 2,215 approvals have missing industry codes. Missing-industry records explain most but not exactly all of NFAP’s 2,207 gap.',
                      'Fru HTML is archived as a reference, not ingested into wage comparisons.',
                      'Source reporting periods differ: IIE academic years, ICE calendar 2024, USCIS/NFAP fiscal 2025. Calendar 2024 and FY2025 overlap in Oct–Dec 2024; these are not sequential student cohorts.',
                      ice.COUNTING_NOTE, ice.IDENTITY_LIMIT, ice.COMPARISON,
                      'ICE covers only its top-200 list. Eleven STEM OPT cells are blank, not zero. One employer name on page 4 is visibly clipped and retained without expansion.',
                      'The ICE pipeline is integrated; existing website placeholders and visualization code remain unchanged for the next UI phase.'])
    (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    (OUT / 'uscis_fy2025_reconciliation.json').write_text(json.dumps(reconciliation, indent=2) + '\n')
    (OUT / 'ice_2024_validation.json').write_text(json.dumps(ice_report, indent=2) + '\n')
    notes = {}
    for name in ['open_doors_enrollment.xlsx', 'open_doors_academic_level.xlsx', 'open_doors_fields.xlsx']:
        notes[name] = [str(cell.value) for sheet in workbook(name) for row in sheet for cell in row
                       if isinstance(cell.value, str) and cell.value.startswith(('*', 'Note:', '(', 'Suggested citation:'))]
    (OUT / 'source_notes.json').write_text(json.dumps(notes, indent=2) + '\n')
    for name, rows in datasets.items():
        print(f'{name}: {len(rows)} rows')
    print(report['status'])
    for warning in report['warnings']:
        print('NOTE:', warning)


if __name__ == '__main__':
    main()
