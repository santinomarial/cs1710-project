// Deployment contract: only reviewed website assets, project-relative URLs,
// and byte-identical processed CSV downloads. Run after `npm run build`.
import assert from 'node:assert/strict';
import { readdir, readFile, lstat } from 'node:fs/promises';
import { join, extname, basename } from 'node:path';
import { createHash } from 'node:crypto';

const base = '/cs1710-project/';
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
async function walk(dir) {
  const paths = [];
  for (const name of await readdir(dir)) {
    const path = join(dir, name);
    const stat = await lstat(path);
    assert(!stat.isSymbolicLink(), `No symlinks in Pages artifact: ${path}`);
    if (stat.isDirectory()) paths.push(...await walk(path));
    else paths.push(path);
  }
  return paths;
}
const paths = await walk('dist');
const allowed = new Set(['.html', '.js', '.css', '.svg', '.csv']);
for (const path of paths) {
  assert(allowed.has(extname(path)), `Unexpected deployed file: ${path}`);
  assert(!/(?:^|\/)(?:raw|docs|src|scripts|tests|\.git)(?:\/|$)/.test(path), path);
}
const html = await readFile('dist/index.html', 'utf8');
const urls = [...html.matchAll(/(?:src|href)="([^"]+)"/g)].map(m => m[1]);
assert(urls.length >= 3, 'Expected JavaScript, stylesheet and favicon links');
for (const url of urls) {
  assert(url.startsWith(base), `HTML URL outside project base: ${url}`);
  assert(paths.includes('dist/' + url.slice(base.length)), `Missing asset: ${url}`);
}
const scripts = (await Promise.all(paths.filter(p => p.endsWith('.js')).map(p => readFile(p, 'utf8')))).join('\n');
const csvUrls = new Set([...scripts.matchAll(/\/cs1710-project\/assets\/[A-Za-z0-9_.-]+\.csv/g)].map(m => m[0]));
const expected = (await readdir('data/processed')).filter(p => p.endsWith('.csv'));
assert.equal(expected.length, 17, 'Review intentional changes to downloadable data');
assert.equal(csvUrls.size, expected.length, 'Each CSV needs a base-prefixed download URL');
assert.equal(paths.filter(p => p.endsWith('.csv')).length, expected.length);
for (const name of expected) {
  const matches = [...csvUrls].filter(url => basename(url).startsWith(name.slice(0, -4) + '-'));
  assert.equal(matches.length, 1, `Expected one download for ${name}`);
  const output = 'dist/' + matches[0].slice(base.length);
  assert.equal(hash(await readFile(output)), hash(await readFile('data/processed/' + name)), `Changed CSV: ${name}`);
}
assert(!/["'`]\/(?:assets|data|src)\//.test(scripts), 'Found an unprefixed runtime asset URL');
// Narrow, recognizable credential formats; do not mistake public source metadata for secrets.
const credentials = /(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)/;
for (const path of paths) assert(!credentials.test(await readFile(path, 'utf8')), `Potential credential in ${path}`);

// Optional HTTP check, useful for both the production preview and published Pages URL.
if (process.argv[2]) {
  const site = new URL(process.argv[2]);
  assert.equal(site.pathname, base, 'Pass the full project URL ending with /');
  for (const path of paths) {
    const url = new URL(path.slice(5), site);
    const response = await fetch(url, { signal: AbortSignal.timeout(30000) });
    assert.equal(response.status, 200, `${url}: HTTP ${response.status}`);
    const body = Buffer.from(await response.arrayBuffer());
    assert.equal(hash(body), hash(await readFile(path)), `HTTP content differs for ${url}`);
    if (path.endsWith('.js')) assert(/javascript/.test(response.headers.get('content-type') || ''), `Invalid JavaScript MIME: ${url}`);
    if (path.endsWith('.css')) assert(/text\/css/.test(response.headers.get('content-type') || ''), `Invalid CSS MIME: ${url}`);
  }
  console.log(`HTTP verification passed for all ${paths.length} files at ${site}`);
}
console.log(`Pages artifact verified: ${paths.length} files, 17 unchanged CSVs, all asset URLs under ${base}; no raw archives or source maps.`);
