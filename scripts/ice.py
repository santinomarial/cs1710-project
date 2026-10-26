"""Extract the pinned ICE 2024 table; compare names without inventing entity links."""
import re
import unicodedata
from collections import Counter, defaultdict

import pdfplumber

FILE = '2024_Top200_Employers_OPT_STEM_OPT_Students.pdf'
URL = 'https://www.ice.gov/doclib/sevis/btn/2024/' + FILE
CAVEAT = '**If a student is employed at the same Employer wile in a different program, he/she will be counted multiple times for the employer.'
COUNTING_NOTE = 'Source combined count retained independently; OPT and STEM OPT must not be added to reconstruct it. Students may be counted multiple times across programs.'
COMPARISON = 'Employer-level comparison: calendar-2024 OPT/STEM OPT participation versus FY2025 H-1B initial approvals; not individual transitions or conversion rates.'
IDENTITY_LIMIT = 'Name-based comparison only; ICE supplies no shared tax ID, address or corporate-scope crosswalk. Does not verify a legal-entity match.'
METHOD = 'unique_normalized_full_name_no_prefix_scope_conflict_v1'
FIELDS = ('total_opt_or_stem_opt_participants', 'opt_participants', 'stem_opt_participants')
PAGE_COUNTS = (58, 63, 63, 16)
HEADER = ['Top 200 Employer Names', 'Number of Students Participating in OPT or STEM-OPT in 2024',
          'Number of Students Participating in OPT in 2024', 'Number of Students Participating in STEM-OPT in 2024']
# Checked visually on original page 1. These are extraction controls, never replacement data.
CONTROLS = {'Amazon': (10167, 5379, 6679), 'Google': (2454, 1110, 1778),
            'Microsoft': (2143, 1066, 1496), 'Meta': (2032, 1081, 1302), 'Apple': (1621, 1135, 973)}
MISSING_STEM = {'Bright Mind Enrichment and Schooling', 'Changing The Present', 'THE KEELWORKS FOUNDATION',
                'OUTLIER', 'Carnegie Mellon University', 'Match4Action-CrowdDoing', 'REBECCA EVERLENE TRUST COMPANY',
                'ONE COMMUNITY', 'ABECEDARIAN', 'JERSEYSTEM', 'CROWDDOING'}
TRUNCATED = 'AMERICAN TECHNOLOGY CONSULTING L'


def require(condition, message):
    if not condition:
        raise ValueError('ICE: ' + message)


def participant_count(value):
    if value is None or not value.strip():
        return None
    require(bool(re.fullmatch(r'(?:\d+|\d{1,3}(?:,\d{3})+)', value.strip())), f'Invalid count: {value!r}')
    return int(value.strip().replace(',', ''))


def name_key(value):
    """Formatting normalization only: preserve every word, legal suffix and campus."""
    normalized = unicodedata.normalize('NFKC', value).upper().replace('&', ' AND ')
    return ' '.join(re.sub(r'[^\w\s]', ' ', normalized).split())


def extract(path):
    require(path.read_bytes().startswith(b'%PDF'), 'Expected original PDF')
    rows = []
    with pdfplumber.open(path) as doc:
        require(len(doc.pages) == 4, 'Pinned PDF page count changed')
        first_text = doc.pages[0].extract_text()
        require('2024 Top 200 Employers for OPT and STEM-OPT Students**' in first_text, 'Wrong title/period')
        require(CAVEAT in first_text, 'Source counting caveat changed')
        for page, expected in zip(doc.pages, PAGE_COUNTS):
            tables = page.extract_tables()
            require(len(tables) == 1, f'Expected one table on page {page.page_number}')
            cells = tables[0]
            if page.page_number == 1:
                require([' '.join(c.split()) for c in cells[0]] == HEADER, 'Column headers changed')
                cells = cells[1:]
            require(len(cells) == expected, f'Page {page.page_number} row coverage changed')
            # Independently check the grid extraction against text-line extraction.
            text_rows = []
            for line in page.extract_text().splitlines():
                match = re.fullmatch(r'(.+?)\s+([\d,]+)\s+([\d,]+)(?:\s+([\d,]+))?', line)
                if match:
                    text_rows.append((' '.join(match[1].split()), tuple(participant_count(x) for x in match.groups()[1:] if x)))
            grid_rows = []
            for page_row, cells_row in enumerate(cells, 1):
                require(len(cells_row) == 4, f'Unexpected column count on page {page.page_number}')
                raw_name, *values = cells_row
                require(bool(raw_name and raw_name.strip()), 'Missing employer name')
                name = ' '.join(raw_name.split())
                counts = tuple(participant_count(value) for value in values)
                grid_rows.append((name, tuple(value for value in counts if value is not None)))
                rows.append(dict(source_order=len(rows)+1, employer_name=name,
                                 **dict(zip(FIELDS, counts)), calendar_year=2024,
                                 source_type='primary_ICE_SEVIS', source_file=FILE, source_page=page.page_number,
                                 source_table_row=page_row, source_url=URL,
                                 name_note='Name visibly clipped at column edge; preserved as extracted, not expanded.' if name == TRUNCATED else '',
                                 counting_note=COUNTING_NOTE))
            require(grid_rows == text_rows, f'Grid/text extraction disagreement on page {page.page_number}')
    validate_employers(rows)
    return rows


def validate_employers(rows):
    require(len(rows) == 200, 'Expected all 200 employers')
    require([r['source_order'] for r in rows] == list(range(1, 201)), 'Source order changed')
    require(len({name_key(r['employer_name']) for r in rows}) == 200, 'Duplicate employer names')
    require(Counter(r['source_page'] for r in rows) == dict(enumerate(PAGE_COUNTS, 1)), 'Page provenance changed')
    for row in rows:
        require(row['calendar_year'] == 2024, 'Wrong calendar year')
        require(row['source_file'] == FILE and row['source_url'] == URL and row['counting_note'] == COUNTING_NOTE, 'Lost provenance/caveat')
        for field in FIELDS:
            value = row[field]
            require(value is None or (type(value) is int and value >= 0), f'Invalid {field}')
        require(row[FIELDS[0]] is not None and row[FIELDS[1]] is not None, 'Unexpected missing total/OPT count')
    require({r['employer_name'] for r in rows if r[FIELDS[2]] is None} == MISSING_STEM, 'Missing cells changed or were imputed')
    totals = [r[FIELDS[0]] for r in rows]
    require(totals == sorted(totals, reverse=True), 'Source ordering changed')
    indexed = {r['employer_name']: r for r in rows}
    for name, expected in CONTROLS.items():
        require(tuple(indexed[name][k] for k in FIELDS) == expected, f'Visually verified source control changed: {name}')
    require(bool(indexed[TRUNCATED]['name_note']), 'Lost clipped-name limitation')


def match_employers(ice_rows, uscis_groups):
    """Accept only one-to-one normalized full names; weaker candidates are audit-only.

    Retain zero-approval groups in the search. Dropping them can hide identity
    ambiguity. Prefix alternatives block even an otherwise unique exact name:
    the ICE label may aggregate campuses or affiliates. Prefixes do NOT prove
    affiliation and are never joined or summed into the accepted comparison.
    """
    exact = defaultdict(list)
    longer = defaultdict(list)
    for group in uscis_groups:
        if group['name_status'] != 'reported':
            continue
        key = name_key(group['employer_name'])
        if not key:
            continue
        exact[key].append(group)
        tokens = key.split()
        for i in range(1, len(tokens)):
            longer[' '.join(tokens[:i])].append(group)
    ice_counts = Counter(name_key(row['employer_name']) for row in ice_rows)
    accepted, audit, candidates = [], [], []
    for row in ice_rows:
        key = name_key(row['employer_name'])
        matches = sorted(exact.get(key, []), key=lambda g: g['employer_group_id'])
        alternatives = {g['employer_group_id']: g for g in longer.get(key, [])}
        tokens = key.split()
        for i in range(1, len(tokens)):
            alternatives.update((g['employer_group_id'], g) for g in exact.get(' '.join(tokens[:i]), []))
        alternatives = sorted(alternatives.values(), key=lambda g: g['employer_group_id'])
        if row.get('name_note'):
            status, reason = 'source_name_truncated', 'Source label is visibly clipped; do not infer its missing legal suffix.'
        elif len(matches) > 1 or ice_counts[key] > 1:
            status, reason = 'ambiguous_multiple_name_matches', 'Full normalized name maps to multiple USCIS groups or ICE rows; no group is selected or summed.'
        elif len(matches) == 1 and alternatives:
            status, reason = 'ambiguous_name_scope', 'An exact name exists alongside longer/shorter petitioner names; ICE corporate/campus scope is unverified.'
        elif len(matches) == 1 and not re.fullmatch(r'\d{4}', matches[0]['tax_id_suffix']):
            status, reason = 'ambiguous_incomplete_identifier', 'The only USCIS name candidate lacks a standard four-digit tax suffix.'
        elif len(matches) == 1:
            status, reason = 'accepted_unique_name', 'Unique full normalized name on both sides, standard USCIS suffix, no prefix-scope alternative.'
        elif alternatives:
            status, reason = 'unresolved_name_variants', 'Only prefix-related names exist; legal suffixes, subsidiaries or campus differences require external identity evidence.'
        else:
            status, reason = 'no_candidate', 'No full-name or token-prefix candidate; this does not imply no H-1B sponsorship.'
        audit.append(dict(ice_employer_name=row['employer_name'], normalized_name=key, match_status=status,
                          full_name_candidate_count=len(matches), prefix_candidate_count=len(alternatives),
                          reason=reason, calendar_year=2024, h1b_fiscal_year=2025,
                          source_file=FILE, source_page=row['source_page'], source_url=URL,
                          identity_limitation=IDENTITY_LIMIT))
        for relationship, groups in [('normalized_full_name', matches), ('token_prefix_only', alternatives)]:
            for group in groups:
                candidates.append(dict(ice_employer_name=row['employer_name'], uscis_employer_name=group['employer_name'],
                                       uscis_employer_group_id=group['employer_group_id'], tax_id_suffix=group['tax_id_suffix'],
                                       candidate_relationship=relationship, match_status=status,
                                       accepted='true' if status=='accepted_unique_name' else 'false',
                                       candidate_initial_approvals=int(group['initial_approvals']),
                                       candidate_source_lines=group['source_lines'], calendar_year=2024, h1b_fiscal_year=2025,
                                       source_file=FILE, source_page=row['source_page'], source_url=URL,
                                       uscis_source_file=group['source_file'], uscis_source_url=group['source_url'],
                                       interpretation='Lexical review candidate only unless accepted=true; not evidence of affiliation.'))
        if status == 'accepted_unique_name':
            group = matches[0]
            accepted.append(dict(employer_name=row['employer_name'], uscis_employer_name=group['employer_name'],
                                 uscis_employer_group_id=group['employer_group_id'], uscis_tax_id_suffix=group['tax_id_suffix'],
                                 **{k: row[k] for k in FIELDS}, calendar_year=2024, h1b_fiscal_year=2025,
                                 h1b_new_employment_approvals=int(group['new_employment_approvals']),
                                 h1b_new_concurrent_approvals=int(group['new_concurrent_approvals']),
                                 h1b_initial_approvals=int(group['initial_approvals']),
                                 match_method=METHOD, match_status=status, comparison_label=COMPARISON,
                                 identity_limitation=IDENTITY_LIMIT, counting_note=COUNTING_NOTE,
                                 source_file=FILE, source_page=row['source_page'], source_table_row=row['source_table_row'], source_url=URL,
                                 uscis_source_file=group['source_file'], uscis_source_lines=group['source_lines'], uscis_source_url=group['source_url']))
    require(len({r['uscis_employer_group_id'] for r in accepted}) == len(accepted), 'Many-to-one accepted join')
    return accepted, audit, candidates


def build(raw, uscis_groups):
    employers = extract(raw / FILE)
    overlap, audit, candidates = match_employers(employers, uscis_groups)
    report = dict(source_file=FILE, calendar_year=2024, employers=len(employers),
                  pages=dict(enumerate(PAGE_COUNTS, 1)), source_caveat_verbatim=CAVEAT,
                  counting_note=COUNTING_NOTE, missing_cells={field:sum(r[field] is None for r in employers) for field in FIELDS},
                  explicit_zero_cells={field:sum(r[field] == 0 for r in employers) for field in FIELDS},
                  extraction_checks=['Four source pages visually reviewed', 'All 200 grid rows agree with text-line extraction',
                                     'Amazon, Google, Microsoft, Meta and Apple values checked against original page 1',
                                     'Eleven blank STEM OPT cells retained; no combined counts reconstructed'],
                  extraction_limitations=[f'Page 4: {TRUNCATED} is visibly clipped in the source; retained and excluded from matching.'],
                  overlap_matches=len(overlap), matching_status_counts=dict(sorted(Counter(r['match_status'] for r in audit).items())),
                  candidate_rows=len(candidates), match_method=METHOD, comparison_label=COMPARISON,
                  identity_limitation=IDENTITY_LIMIT)
    return {'opt_employers.csv': employers, 'opt_h1b_employer_overlap.csv': overlap,
            'opt_h1b_match_audit.csv': audit, 'opt_h1b_match_candidates.csv': candidates}, report
