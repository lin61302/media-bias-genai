/** Export the fixed public country-month counts. Requires Node 18+; no packages. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath, pathToFileURL} from 'node:url';

export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const outputDir = path.join(root, 'data/polarization');
export const filename = 'monthly_polarization_all_countries.csv';
const sha256 = b => crypto.createHash('sha256').update(b).digest('hex');
const axes = ['alignment', 'reputation', 'framing'];
const start = '2021-01', end = '2026-05';

export function encodeCSV(matrix) {
  const cell = value => {
    if (value === null || value === undefined) return '';
    const s = typeof value === 'number' ? String(value) : String(value);
    return /[",\r\n]/.test(s) ? '"' + s.replaceAll('"', '""') + '"' : s;
  };
  return matrix.map(row => row.map(cell).join(',')).join('\r\n') + '\r\n';
}

export async function buildExport() {
  const snapshot = JSON.parse(await fs.readFile(path.join(root, 'data/analysis_snapshot.json'), 'utf8'));
  const sources = {};
  async function load(name) {
    const spec = snapshot.files[name];
    if (!spec) throw Error('Unpinned source: ' + name);
    sources[name] = spec;
    const cache = path.join(root, 'data/cache', name);
    let bytes;
    try { bytes = await fs.readFile(cache); }
    catch (error) {
      if (error.code !== 'ENOENT') throw error;
      const response = await fetch(spec.url);
      if (!response.ok) throw Error('Source download failed: ' + response.status);
      bytes = Buffer.from(await response.arrayBuffer());
      if (sha256(bytes) !== spec.sha256) throw Error('Source hash mismatch: ' + name);
      await fs.mkdir(path.dirname(cache), {recursive:true});
      await fs.writeFile(cache, bytes);
    }
    if (sha256(bytes) !== spec.sha256) throw Error('Source hash mismatch: ' + name);
    return JSON.parse(bytes);
  }
  const [monthly, context, all, recent] = await Promise.all([
    load('explore-monthly.json'), load('country_context.json'),
    load('explore-since2021.json'), load('explore-post2021.json')
  ]);
  const records = monthly.groups.gov.filter(r => start <= r.month && r.month <= end);
  const lookup = new Map();
  const total = Array(27).fill(0), post2021 = Array(27).fill(0);
  for (const row of records) {
    const key = row.k + '/' + row.month;
    if (lookup.has(key)) throw Error('Duplicate country-month: ' + key);
    if (!context.countries[row.k]?.name) throw Error('Country name missing: ' + row.k);
    if (row.c.length !== 27 || row.c.some(n => !Number.isSafeInteger(n) || n < 0)) throw Error('Invalid joint counts: ' + key);
    if (!row.c.some(n => n > 0)) throw Error('Unexpected empty observed group: ' + key);
    lookup.set(key, row);
    row.c.forEach((n,i) => { total[i] += n; if (row.month >= '2022-01') post2021[i] += n; });
  }
  if (JSON.stringify(total) !== JSON.stringify(all.overall.c)) throw Error('Full-window joint counts do not reconcile');
  if (JSON.stringify(post2021) !== JSON.stringify(recent.overall.c)) throw Error('Default-window joint counts do not reconcile');
  const countries = [...new Set(records.map(r => r.k))].sort();
  const months = [];
  for (let year=2021; year<=2026; year++) for (let month=1; month<=12; month++) {
    const key = `${year}-${String(month).padStart(2,'0')}`;
    if (key <= end) months.push(key);
  }
  const columns = [
    'government_country_code', 'government_country_name', 'month', 'eligible_articles',
    ...axes.map(a => 'polarization_' + a),
    ...axes.map(a => a + '_nonzero_share'),
    ...axes.flatMap(a => [a+'_negative_share', a+'_zero_share', a+'_positive_share']),
    ...axes.map(a => a + '_net'), 'coverage_status'
  ];
  const data=[];
  const statusCounts={};
  for (const country of countries) for (const month of months) {
    const row = lookup.get(country + '/' + month);
    const n = row ? row.c.reduce((a,b) => a+b, 0) : 0;
    const marginals = Array.from({length:3}, () => [0,0,0]);
    if (row) row.c.forEach((count,i) => {
      [Math.floor(i/9), Math.floor(i/3)%3, i%3].forEach((category,axis) => marginals[axis][category] += count);
    });
    const shares = marginals.map(counts => counts.map(count => n ? count/n : null));
    const p = shares.map(([neg,zero,pos]) => n ? 4*pos*neg : null);
    const nonzero = shares.map(([neg,zero,pos]) => n ? neg+pos : null);
    const net = shares.map(([neg,zero,pos]) => n ? pos-neg : null);
    const status = n===0 ? 'no_eligible_articles' : n<100 ? 'under_100_articles' : 'at_least_100_articles';
    statusCounts[status] = (statusCounts[status] || 0) + 1;
    data.push([country,context.countries[country].name,month,n,...p,...nonzero,...shares.flat(),...net,status]);
  }
  const summary = {
    article_period_start:start,article_period_end:end,country_codes:countries.length,
    months:months.length,rows:data.length,observed_country_months:records.length,
    eligible_articles:total.reduce((a,b) => a+b,0),coverage_status_counts:statusCounts,
    default_dashboard_window_eligible_articles:post2021.reduce((a,b) => a+b,0),
    audit_cutoff:snapshot.audit_cutoff,prompt_sha256:snapshot.prompt_sha256,
    source_space:snapshot.space,source_commit:snapshot.commit,sources,
    formula:'4 * negative_share * positive_share',
    country_definition:'Country/territory code of the evaluated government, not publication country',
    missing_score_policy:'Blank scores/shares/net when eligible_articles=0; never impute a zero score',
    columns
  };
  return {matrix:[columns,...data],summary};
}

export async function writeExport(matrix, summary) {
  await fs.mkdir(outputDir, {recursive:true});
  const csv=encodeCSV(matrix);
  await fs.writeFile(path.join(outputDir,filename),csv);
  await fs.writeFile(path.join(outputDir,'export_manifest.json'),JSON.stringify({
    ...summary,output:{file:filename,bytes:Buffer.byteLength(csv),sha256:sha256(csv)}
  },null,2)+'\n');
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const {matrix,summary}=await buildExport();
  if (process.argv.includes('--check')) {
    const saved=await fs.readFile(path.join(outputDir,filename),'utf8');
    if (saved !== encodeCSV(matrix)) throw Error('Saved CSV differs from the pinned source calculation');
    console.log(`Verified ${summary.rows} country-month rows from pinned public aggregates.`);
  } else {
    await writeExport(matrix,summary);
    console.log(`Wrote ${filename}: ${summary.rows} rows, ${summary.country_codes} country/territory codes.`);
  }
}
