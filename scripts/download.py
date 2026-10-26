"""Download public originals without evading access controls; retain an audit manifest."""
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
SOURCES = {
    'open_doors_enrollment.xlsx': 'https://opendoorsdata.org/wp-content/uploads/2025/11/Census_Overall-Enrollment-1949-2025_OD25_Website.xlsx',
    'open_doors_academic_level.xlsx': 'https://opendoorsdata.org/wp-content/uploads/2025/11/Census_Academic-Level_OD25_Website.xlsx',
    'open_doors_fields.xlsx': 'https://opendoorsdata.org/wp-content/uploads/2025/11/Census_Field-of-Study_OD25_Website.xlsx',
    'sevis_2024.pdf': 'https://www.ice.gov/doclib/sevis/btn/25_0605_2024-sevis-btn.pdf',
    'opt_employers_2024.pdf': 'https://www.ice.gov/doclib/sevis/btn/2024/2024_Top200_Employers_OPT_STEM_OPT_Students.pdf',
    'uscis_hub.html': 'https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub',
    'nfap_fy2025.pdf': 'https://nfap.com/wp-content/uploads/2025/11/H-1B-Petitions-and-Denial-Rates-For-FY-2025.NFAP-Policy-Brief.2025.pdf',
    'bls_ooh.html': 'https://www.bls.gov/ooh/',
    'fru_h1b.html': 'https://salaries.fru.dev/h1b',
    'dol_performance.html': 'https://www.dol.gov/agencies/eta/foreign-labor/performance',
    'LCA_Disclosure_Data_FY2025_Q4.xlsx': 'https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/LCA_Disclosure_Data_FY2025_Q4.xlsx',
    'bls_software_developers.html': 'https://www.bls.gov/ooh/computer-and-information-technology/software-developers.htm',
}


def fetch(item):
    name, url = item
    record = {'file': name, 'url': url, 'attempted_at_utc': datetime.now(timezone.utc).isoformat()}
    try:
        with urlopen(Request(url, headers={'User-Agent': 'CS1710-Research-Pipeline/1.0'}), timeout=90) as response:
            content = response.read()
            record['resolved_url'] = response.url
            record['content_type'] = response.headers.get('Content-Type', '')
        if name.endswith('.pdf') and not content.startswith(b'%PDF'):
            raise ValueError('Expected PDF; received a different response')
        if name.endswith('.xlsx') and not content.startswith(b'PK'):
            raise ValueError('Expected XLSX archive; received a different response')
        (RAW / name).write_bytes(content)
        record.update(status='downloaded', bytes=len(content), sha256=hashlib.sha256(content).hexdigest())
    except Exception as error:
        record.update(status='blocked', error=str(error))
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Re-download existing sources (may change upstream data)')
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    manifest_path = RAW / 'manifest.json'
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    cached = {r['file']: r for r in previous if r['status'] == 'downloaded'}
    todo = []
    # A refresh applies only to managed URLs. Never overwrite a supplied original
    # or drop its provenance when rebuilding the retrieval manifest.
    records = preserved_manual_records(previous)
    manual_urls = {r['url'] for r in records if r['status'] == 'provided_local'}
    manual_names = {r['file'] for r in records if r['status'] == 'provided_local'}
    for name, url in SOURCES.items():
        if name in manual_names:
            continue
        if url in manual_urls:
            # Preserve historical attempts under a former filename, but do not
            # download a duplicate or overwrite an imported source on refresh.
            records.extend(r for r in previous if r['file'] == name)
            continue
        path = RAW / name
        if not args.refresh and name in cached and path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest() != cached[name]['sha256']:
                raise ValueError(f'Raw file changed: {name}. Restore it or use --refresh.')
            records.append(cached[name])
        else:
            todo.append((name, url))
    with ThreadPoolExecutor(max_workers=4) as pool:
        records.extend(pool.map(fetch, todo))
    records.sort(key=lambda r: r['file'])
    manifest_path.write_text(json.dumps(records, indent=2) + '\n')
    for record in records:
        print(record['status'], record['file'], record.get('error', record.get('bytes')))


def preserved_manual_records(previous):
    records = [r for r in previous if r['file'] not in SOURCES or r['status'] == 'provided_local']
    for record in records:
        if record['status'] == 'provided_local':
            if hashlib.sha256((RAW / record['file']).read_bytes()).hexdigest() != record['sha256']:
                raise ValueError(f'Manually supplied original changed: {record["file"]}')
    return records


if __name__ == '__main__':
    main()
