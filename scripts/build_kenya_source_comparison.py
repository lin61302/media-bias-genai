"""Reproduce Kenya outlet comparisons from supplied frozen, verified caches.

Repeat --cache PATH for the three disjoint extraction files. Each must have its
neighboring EXTRACTION_VERIFIED.json. Supply --snapshot slides/analysis_snapshot.json,
--output FILE.json and optionally --scope explore-since2019.json and --private-subset
FILE.csv.gz. No database, model, provider, or network calls are made.
"""
from pathlib import Path
from collections import Counter
import argparse, csv, gzip, hashlib, json

SOURCES = ('citizen.digital', 'kbc.co.ke', 'nation.africa')
AXES = ('align', 'rep', 'frame')
ROLE_KEY = dict(zip('ABCDEFGHIJKLMNOPQRSTUVW', [
    'Executive/Cabinet', 'Legislature', 'Parties/Politicians', 'Administration/Regulators',
    'Electoral Bodies', 'Judiciary/Prosecutors', 'Security Forces', 'Local/Provincial Government',
    'International/Inter-Governmental Organizations', 'Non-Government Non-Profit Organizations',
    'Civic Movements/Unions', 'Armed Resistance Movements', 'Academia/Think-tanks',
    'Professional Associations', 'Media/Platforms', 'Business/Enterprises', 'State-Owned Enterprises',
    'Religious Groups/Organizations', 'Ethnic/Indigenous Groups/Organizations',
    'Criminal/Illicit Groups/Networks', 'Public Individuals/Influencers',
    'Government entity of a country other than gov', 'Other Actor']))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metrics(rows):
    n = len(rows)
    margins = {axis: {str(v): sum(r[axis] == str(v) for r in rows) for v in (-1, 0, 1)} for axis in AXES}
    cube = [0] * 27
    for r in rows:
        cube[(int(r['align']) + 1) * 9 + (int(r['rep']) + 1) * 3 + int(r['frame']) + 1] += 1
    return {'n': n, 'margins': margins,
            'negative_share': {axis: c['-1'] / n if n else None for axis, c in margins.items()},
            'positive_share': {axis: c['1'] / n if n else None for axis, c in margins.items()},
            'nonzero_share': {axis: (c['-1'] + c['1']) / n if n else None for axis, c in margins.items()},
            'net': {axis: (c['1'] - c['-1']) / n if n else None for axis, c in margins.items()},
            'P': {axis: 4 * c['-1'] * c['1'] / n**2 if n else None for axis, c in margins.items()},
            'joint_align_rep_frame_27': cube}


def rank(rows, field):
    return {key: n for key, n in sorted(Counter(r[field] for r in rows).items(), key=lambda item: (-item[1], item[0]))}


def grouped(rows, fields):
    keys = sorted({tuple(r[f] for f in fields) for r in rows})
    result = []
    for key in keys:
        sub = [r for r in rows if tuple(r[f] for f in fields) == key]
        result.append({**dict(zip(fields, key)), **metrics(sub)})
    return sorted(result, key=lambda r: (-r['n'], tuple(r[f] for f in fields)))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cache', type=Path, action='append', required=True)
    ap.add_argument('--snapshot', type=Path, required=True)
    ap.add_argument('--scope', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--private-subset', type=Path)
    args = ap.parse_args()
    snapshot = json.loads(args.snapshot.read_text())
    spec = snapshot['files']['explore-since2019.json']
    sp = args.scope or args.snapshot.parent.parent / 'data/cache/snapshots' / spec['sha256'] / 'explore-since2019.json'
    assert sha(sp) == spec['sha256']
    scope = json.loads(sp.read_text())
    rows, receipts = [], []
    valid = eligible = 0
    full_cube = [0] * 27
    exclusions = Counter()
    for path in args.cache:
        proof_path = path.parent / 'EXTRACTION_VERIFIED.json'
        proof = json.loads(proof_path.read_text())
        actual = sha(path)
        assert actual == proof['records_sha256']
        assert proof['prompt_sha256'] == snapshot['prompt_sha256']
        assert proof['checkpoint'] <= snapshot['audit_cutoff']
        receipts.append({'filename': path.name, 'sha256': actual, 'proof_sha256': sha(proof_path),
                         'checkpoint': proof['checkpoint'], 'hash_verified': True})
        with gzip.open(path, 'rt') as handle:
            for row in csv.DictReader(handle):
                valid += 1
                if row['gov'] in ('', 'null') or row['action'] in ('', 'null') or any(row[a] not in ('-1', '0', '1') for a in AXES):
                    continue
                eligible += 1
                full_cube[(int(row['align']) + 1) * 9 + (int(row['rep']) + 1) * 3 + int(row['frame']) + 1] += 1
                if row['source'] not in SOURCES or not '2024-01' <= row['month'] <= '2024-12':
                    continue
                if row['gov'] != 'KEN':
                    exclusions['other_evaluated_government'] += 1
                elif row['publication_country'] != 'KEN':
                    exclusions['KEN_evaluated_but_other_publication_country'] += 1
                else:
                    rows.append(row)
    assert valid == snapshot['valid_records'] == scope['quality']['valid'] == 3464596
    assert eligible == snapshot['eligible_records'] == scope['quality']['complete'] == 3181113
    assert full_cube == scope['overall']['c']
    series = {source: {f'2024-{m:02d}': metrics([r for r in rows if r['source'] == source and r['month'] == f'2024-{m:02d}'])
                       for m in range(1, 13)} for source in SOURCES}
    june = {}
    for source in SOURCES:
        sub = [r for r in rows if r['source'] == source and r['month'] == '2024-06']
        june[source] = {
            **metrics(sub), 'action_counts': rank(sub, 'action'),
            'actor_role_counts': rank(sub, 'actor_role'), 'target_role_counts': rank(sub, 'target_role'),
            'action_cells': grouped(sub, ['action']), 'actor_cells': grouped(sub, ['actor_role']),
            'action_actor_cells': grouped(sub, ['action', 'actor_role']),
            'actor_target_cells': grouped(sub, ['actor_role', 'target_role']),
        }
    assert [june[s]['n'] for s in SOURCES] == [236, 138, 224]
    assert [june[s]['margins']['frame']['-1'] for s in SOURCES] == [20, 10, 75]
    assert [june[s]['margins']['rep']['-1'] for s in SOURCES] == [34, 25, 91]
    # Same categorical labels do not imply same events, stories or factual evidence.
    shared = []
    for action, actor in sorted({(r['action'], r['actor_role']) for r in rows if r['month'] == '2024-06'}):
        cells = {source: metrics([r for r in rows if r['month'] == '2024-06' and r['source'] == source and r['action'] == action and r['actor_role'] == actor]) for source in SOURCES}
        if sum(c['n'] > 0 for c in cells.values()) >= 2:
            shared.append({'action': action, 'actor_role': actor, 'by_source': cells})
    prior = {source: metrics([r for r in rows if r['source'] == source and '2024-03' <= r['month'] <= '2024-05']) for source in SOURCES}
    out = {
        'schema': 'kenya_source_comparison_v1', 'evaluated_government': 'KEN',
        'publication_country': 'KEN', 'period': ['2024-01', '2024-12'], 'focus_month': '2024-06',
        'sources': list(SOURCES), 'selected_n': len(rows), 'eligible_other_scope_exclusions': dict(exclusions),
        'snapshot': {k: snapshot[k] for k in ('audit_cutoff', 'commit', 'prompt_sha256', 'valid_records', 'eligible_records')},
        'input_receipts': receipts, 'snapshot_sha256': sha(args.snapshot),
        'frozen_scope_sha256': spec['sha256'], 'script_sha256': sha(Path(__file__)),
        'reconciliation': {'all_three_cache_hashes': True, 'full_population_counts': True, 'full_population_27_joint_cells': True},
        'role_key': ROLE_KEY,
        'definitions': {
            'unit': 'One cached article record and its prioritized primary action; not distinct real-world events.',
            'eligibility': 'Gov and action identified, align/rep/frame each -1/0/+1. Zeros retained.',
            'source_scope': 'Source domain matches, evaluated government KEN, publication country KEN.',
            'negative_share': 'Negative records / all common-eligible records in this cell.',
            'net': '(Positive records - negative records) / all common-eligible records.',
            'P': '4 × positive share × negative share.',
            'cube_order': '27 cells: align, rep, frame nested in that order, each -1,0,+1.',
            'role': 'Institutional role, not automatically incumbent affiliation.',
            'other_act': 'Residual category retained in all denominators; not interpreted as a substantive action type.',
        },
        'limits': ['Same source-month and action/role categories are not matched-event comparisons.',
                   'Article genres, story selection, source completeness and repeated coverage may differ.',
                   'Descriptive model labels do not establish outlet bias, accuracy or public opinion.',
                   'No sampling-independence assumption, confidence interval or significance claim is made.',
                   'Zero includes mixed or insufficient directional evidence, not just neutral wording.'],
        'monthly': series, 'june_details': june, 'shared_june_action_actor_cells': shared,
        'march_to_may_baseline': prior,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + '\n')
    if args.private_subset:
        with gzip.open(args.private_subset, 'wt') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        args.private_subset.chmod(0o600)
    print(json.dumps({'selected_n': len(rows), 'june_n': {s: june[s]['n'] for s in SOURCES},
                      'all_reconciliations_passed': True, 'output_filename': args.output.name}))


if __name__ == '__main__':
    main()
