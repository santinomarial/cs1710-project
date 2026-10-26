"""FY2025 Hub export: explicit record grain, conservative groups, no entity inference."""
import csv
import hashlib
import json
import re
from collections import defaultdict

FILE = 'Employer Information (1).csv'
URL = 'https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub'
METHOD = 'exact_name_and_tax_suffix; unnamed_records_separate'
CATEGORIES = {
    'New Employment': 'new_employment', 'New Concurrent': 'new_concurrent',
    'Continuation': 'continuation', 'Change with Same Employer': 'change_with_same_employer',
    'Change of Employer': 'change_of_employer', 'Amended': 'amended',
}
COUNTS = [f'{value}_{result}' for value in CATEGORIES.values() for result in ('approvals', 'denials')]
TOTALS = ['initial_approvals', 'initial_denials', 'continuing_approvals', 'continuing_denials']
BINS = [(1, 1, '1'), (2, 5, '2–5'), (6, 10, '6–10'), (11, 50, '11–50'),
        (51, 100, '51–100'), (101, 500, '101–500'), (501, None, '501+')]
PREFIX = 'uscis_fy2025_'
PROVENANCE = dict(fiscal_year=2025, source_file=FILE, source_url=URL, source_type='primary_USCIS_user_export')


def require(ok, message):
    if not ok:
        raise ValueError('USCIS: ' + message)


def integer(value):
    """Strict count parsing: blanks cannot silently become zero; reject malformed commas."""
    require(isinstance(value, str) and bool(re.fullmatch(r'(?:\d+|\d{1,3}(?:,\d{3})+)', value.strip())),
            f'Invalid integer count: {value!r}')
    return int(value.replace(',', '').strip())


def read_records(path):
    require(path.read_bytes()[:2] == b'\xff\xfe', 'Expected the original UTF-16 LE BOM')
    with path.open(encoding='utf-16', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        expected = {'Line by line', 'Fiscal Year', 'Employer (Petitioner) Name', 'Tax ID',
                    'Industry (NAICS) Code', 'Petitioner City', 'Petitioner State', 'Petitioner Zip Code'}
        expected |= {f'{category} {result}' for category in CATEGORIES for result in ('Approval', 'Denial')}
        headers = [h.strip() for h in reader.fieldnames]
        require(len(headers) == len(set(headers)) and set(headers) == expected, 'Export schema changed')
        records = []
        seen = set()
        for source_row, raw in enumerate(reader, 2):
            require(None not in raw and all(v is not None for v in raw.values()), f'Malformed row {source_row}')
            d = {k.strip(): v for k, v in raw.items()}
            line = integer(d['Line by line'])
            require(line > 0 and line not in seen, f'Duplicate/invalid export line {line}')
            seen.add(line)
            require(integer(d['Fiscal Year']) == 2025, 'Mixed fiscal years')
            name, tax = d['Employer (Petitioner) Name'], d['Tax ID']
            require(not tax or bool(re.fullmatch(r'\d{1,4}', tax)), 'Unexpected tax suffix format')
            # Names are exact source strings, not fuzzy aliases or legal identities.
            identity = ['named', name, tax] if name.strip() else ['unnamed_record', line]
            group_id = hashlib.sha256(json.dumps(identity, ensure_ascii=False).encode()).hexdigest()
            industry = d['Industry (NAICS) Code']
            code, label = industry.split(' - ', 1) if industry else ('', '')
            row = dict(record_id=f'FY2025-{line}', source_line=line, source_row=source_row,
                       employer_group_id=group_id, employer_name=name,
                       name_status='reported' if name.strip() else 'missing', tax_id_suffix=tax,
                       industry_source=industry, naics_code=code, industry=label,
                       petitioner_city=d['Petitioner City'], petitioner_state=d['Petitioner State'],
                       petitioner_zip_code=d['Petitioner Zip Code'])
            for category, key in CATEGORIES.items():
                for singular, plural in [('Approval', 'approvals'), ('Denial', 'denials')]:
                    row[f'{key}_{plural}'] = integer(d[f'{category} {singular}'])
            for result in ('approvals', 'denials'):
                row[f'initial_{result}'] = row[f'new_employment_{result}'] + row[f'new_concurrent_{result}']
                row[f'continuing_{result}'] = sum(row[f'{key}_{result}'] for key in list(CATEGORIES.values())[2:])
            row.update(PROVENANCE)
            records.append(row)
    require(len(records) == 62415 and seen == set(range(1, 62416)), 'Incomplete pinned export')
    return records


def aggregate(records):
    groups, industries = {}, {}
    for r in records:
        gid = r['employer_group_id']
        if gid not in groups:
            groups[gid] = dict(employer_group_id=gid, employer_name=r['employer_name'],
                               name_status=r['name_status'], tax_id_suffix=r['tax_id_suffix'],
                               identity_method=METHOD, source_record_count=0, source_lines=[],
                               naics_codes=set(), **dict.fromkeys(COUNTS + TOTALS, 0), **PROVENANCE)
        g = groups[gid]
        g['source_record_count'] += 1
        g['source_lines'].append(r['source_line'])
        g['naics_codes'].add(r['naics_code'] or 'missing')
        code = r['naics_code']
        if code not in industries:
            industries[code] = dict(naics_code=code, industry=r['industry'] or 'Industry not reported',
                                    industry_status='reported' if code else 'missing', source_record_count=0,
                                    **dict.fromkeys(COUNTS + TOTALS, 0), **PROVENANCE)
        i = industries[code]
        i['source_record_count'] += 1
        for key in COUNTS + TOTALS:
            g[key] += r[key]
            i[key] += r[key]
    for g in groups.values():
        g['source_lines'] = ';'.join(map(str, g['source_lines']))
        g['naics_codes'] = ';'.join(sorted(g['naics_codes']))
    employers = sorted(groups.values(), key=lambda g: (-g['initial_approvals'], g['employer_group_id']))
    return employers, sorted(industries.values(), key=lambda g: (-g['initial_approvals'], g['naics_code']))


def distribution(employers):
    named = [g for g in employers if g['name_status'] == 'reported' and g['initial_approvals'] > 0]
    unnamed = [g for g in employers if g['name_status'] == 'missing']
    total_approvals = sum(g['initial_approvals'] for g in named)
    rows = []
    for order, (lower, upper, label) in enumerate(BINS, 1):
        members = [g for g in named if g['initial_approvals'] >= lower and
                   (upper is None or g['initial_approvals'] <= upper)]
        approvals = sum(g['initial_approvals'] for g in members)
        rows.append(dict(bin_order=order, bin_label=label, lower_bound=lower, upper_bound=upper,
                         employer_count=len(members), initial_approvals=approvals,
                         employer_share_percent=100 * len(members) / len(named),
                         approval_share_percent=100 * approvals / total_approvals,
                         population_employers=len(named), population_initial_approvals=total_approvals,
                         excluded_unnamed_records=sum(g['source_record_count'] for g in unnamed),
                         excluded_unnamed_initial_approvals=sum(g['initial_approvals'] for g in unnamed),
                         population='named employer groups with positive initial approvals',
                         identity_method=METHOD, **PROVENANCE))
    return rows


def comparison(industries, nfap):
    # Explicit label bridge, no invented industry codes for the NFAP source itself.
    reported = {r['industry']: r for r in nfap}
    rows = []
    matched = set()
    for r in industries:
        name = 'Professional, Scientific, and Technical' if r['naics_code'] == '54' else r['industry']
        other = reported.get(name)
        if r['naics_code']:
            require(other is not None, f'Unmatched NFAP industry: {name}')
            matched.add(name)
        rows.append(dict(naics_code=r['naics_code'], industry=r['industry'],
                         uscis_initial_approvals=r['initial_approvals'],
                         nfap_initial_approvals=other['initial_approvals'] if other else None,
                         difference_uscis_minus_nfap=r['initial_approvals'] - other['initial_approvals'] if other else None,
                         comparison_status='matched_category' if other else 'not_reported_by_nfap',
                         nfap_source_file='nfap_fy2025.pdf', nfap_source_page=27,
                         nfap_source_url=nfap[0]['source_url'], **PROVENANCE))
    require(matched == set(reported), 'NFAP categories not fully compared')
    return rows


def build(raw, nfap):
    records = read_records(raw / FILE)
    employers, industries = aggregate(records)
    bins = distribution(employers)
    compared = comparison(industries, nfap)
    totals = {key: sum(r[key] for r in records) for key in COUNTS + TOTALS}
    require(totals['new_employment_approvals'] == 113458 and totals['new_concurrent_approvals'] == 1346,
            'Pinned approval controls changed')
    for key in COUNTS + TOTALS:
        require(sum(g[key] for g in employers) == totals[key] == sum(i[key] for i in industries),
                f'Aggregation lost {key}')
    require(sum(b['employer_count'] for b in bins) == bins[0]['population_employers'], 'Bins lost employers')
    require(sum(b['initial_approvals'] for b in bins) + bins[0]['excluded_unnamed_initial_approvals'] == totals['initial_approvals'],
            'Bins lost approvals')
    unnamed = [r for r in records if r['name_status'] == 'missing']
    named_positive = [g for g in employers if g['name_status'] == 'reported' and g['initial_approvals'] > 0]
    known_total = sum(i['initial_approvals'] for i in industries if i['naics_code'])
    missing = {key: sum(not r[key] for r in records) for key in
               ['employer_name', 'tax_id_suffix', 'naics_code', 'petitioner_city', 'petitioner_state', 'petitioner_zip_code']}
    report = dict(source_file=FILE, source_sha256=hashlib.sha256((raw / FILE).read_bytes()).hexdigest(),
                  fiscal_year=2025, source_records=len(records), missing=missing, category_totals=totals,
                  employer_groups=len(employers), named_groups=len(employers)-len(unnamed),
                  nonstandard_tax_suffix_records=sum(bool(r['tax_id_suffix']) and len(r['tax_id_suffix']) != 4 for r in records),
                  named_positive_groups=len(named_positive), identity_method=METHOD,
                  unnamed_records=len(unnamed), unnamed_positive_records=sum(r['initial_approvals'] > 0 for r in unnamed),
                  unnamed_initial_approvals=sum(r['initial_approvals'] for r in unnamed),
                  named_zero_initial_groups=sum(g['name_status'] == 'reported' and g['initial_approvals'] == 0 for g in employers),
                  nfap_initial_approvals=114806, initial_difference=totals['initial_approvals']-114806,
                  nfap_continuing_approvals=291542, continuing_difference=totals['continuing_approvals']-291542,
                  nfap_change_of_employer_approvals=68167, change_of_employer_difference=totals['change_of_employer_approvals']-68167,
                  known_industry_total=known_total, missing_industry_approvals=totals['initial_approvals']-known_total,
                  nfap_industry_total=sum(r['initial_approvals'] for r in nfap),
                  matched_industry_difference=known_total-sum(r['initial_approvals'] for r in nfap),
                  nfap_employer_count=28277,
                  identity_sensitivity=dict(positive_source_rows=sum(r['initial_approvals'] > 0 for r in records),
                                            positive_exact_names=len({r['employer_name'] for r in records if r['name_status']=='reported' and r['initial_approvals']>0}),
                                            positive_name_tax_groups=len(named_positive)),
                  difference_status='unresolved: no NFAP row-level snapshot or identity crosswalk supplied; no adjustment applied')
    datasets = {PREFIX + name + '.csv': rows for name, rows in [
        ('records', records), ('employers', employers), ('distribution', bins),
        ('industries', industries), ('industry_comparison', compared)]}
    return datasets, report
