"""Build public-safe aggregate evidence from separately supplied private caches.

Example (repeat --cache for each disjoint extraction):
python scripts/build_senegal_case.py --cache PATH/records.csv.gz \
  --cache PATH/additional_records.csv.gz --cache PATH/increment_records.csv.gz \
  --snapshot slides/analysis_snapshot.json \
  --slide-csv slides/figures/data/09_senegal_monthly_indices.csv \
  --output senegal_corpus_contributors.json

Each cache must have a neighboring EXTRACTION_VERIFIED.json. This script reads
existing files only and makes no database, provider, or network requests. It does
not export individual records, article identifiers, text, or private file paths.
"""
from pathlib import Path
from collections import Counter
import argparse
import csv
import gzip
import hashlib
import json

ROLES = dict(zip('ABCDEFGHIJKLMNOPQRSTUVW', [
    'Executive/Cabinet', 'Legislature', 'Parties/Politicians', 'Administration/Regulators',
    'Electoral Bodies', 'Judiciary/Prosecutors', 'Security Forces', 'Local/Provincial Government',
    'International/Inter-Governmental Organizations', 'Non-Government Non-Profit Organizations',
    'Civic Movements/Unions', 'Armed Resistance Movements', 'Academia/Think-tanks',
    'Professional Associations', 'Media/Platforms', 'Business/Enterprises', 'State-Owned Enterprises',
    'Religious Groups/Organizations', 'Ethnic/Indigenous Groups/Organizations',
    'Criminal/Illicit Groups/Networks', 'Public Individuals/Influencers',
    'Government entity of a country other than gov', 'Other Actor']))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance(row):
    pub = row['publication_country']
    return ('domestic' if pub == row['gov'] else
            'international_or_unknown' if pub in ('ALL', '', 'null') else 'foreign')


def rank(rows, fields, limit=None, named_only=False):
    c = Counter(tuple(row[k] for k in fields) for row in rows
                if not named_only or row['action'] != 'other_act')
    ordered = sorted(c.items(), key=lambda item: (-item[1], item[0]))
    return [{**dict(zip(fields, keys)), 'n': n} for keys, n in ordered[:limit]]


def metrics(rows):
    n = len(rows)
    margins = {key: {str(v): sum(row[key] == str(v) for row in rows) for v in (-1, 0, 1)}
               for key in ('align', 'rep', 'frame')}
    return {'n': n, 'margins': margins,
            'P': {key: 4 * c['-1'] * c['1'] / n**2 if n else None for key, c in margins.items()},
            'nonzero_share': {key: (c['-1'] + c['1']) / n if n else None for key, c in margins.items()}}


def distributions(rows):
    return {'n': len(rows), 'other_act_n': sum(r['action'] == 'other_act' for r in rows),
            'actions': rank(rows, ['action']),
            'specified_actions_top10': rank(rows, ['action'], 10, True),
            'actor_roles': rank(rows, ['actor_role']),
            'target_roles': rank(rows, ['target_role']),
            'actor_action_target_top10': rank(rows, ['actor_role', 'action', 'target_role'], 10, True),
            'sources': rank(rows, ['source', 'publication_country'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, action='append', required=True)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--scope', type=Path, help='Optional explicit frozen explore-since2019.json path')
    parser.add_argument('--slide-csv', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text())
    spec = snapshot['files']['explore-since2019.json']
    scope_path = args.scope or args.snapshot.parent.parent / 'data/cache/snapshots' / spec['sha256'] / 'explore-since2019.json'
    assert digest(scope_path) == spec['sha256'], 'Frozen scope hash mismatch'
    scope = json.loads(scope_path.read_text())
    all_cube = [0] * 27
    rows, receipts = [], []
    valid = eligible = 0
    for path in args.cache:
        proof_path = path.parent / 'EXTRACTION_VERIFIED.json'
        proof = json.loads(proof_path.read_text())
        actual = digest(path)
        assert actual == proof['records_sha256'], 'Cache hash mismatch'
        assert proof['prompt_sha256'] == snapshot['prompt_sha256'], 'Prompt mismatch'
        assert proof['checkpoint'] <= snapshot['audit_cutoff'], 'Cache exceeds frozen cutoff'
        receipts.append({'filename': path.name, 'sha256': actual,
                         'proof_sha256': digest(proof_path), 'checkpoint': proof['checkpoint']})
        with gzip.open(path, 'rt') as handle:
            for row in csv.DictReader(handle):
                valid += 1
                if row['gov'] in ('', 'null') or row['action'] in ('', 'null') or any(row[k] not in ('-1', '0', '1') for k in ('align', 'rep', 'frame')):
                    continue
                eligible += 1
                index = (int(row['align']) + 1) * 9 + (int(row['rep']) + 1) * 3 + int(row['frame']) + 1
                all_cube[index] += 1
                if row['gov'] == 'SEN' and '2023-01' <= row['month'] <= '2024-12':
                    rows.append(row)
    assert valid == snapshot['valid_records'] == scope['quality']['valid']
    assert eligible == snapshot['eligible_records'] == scope['quality']['complete']
    assert all_cube == scope['overall']['c'], 'Full population joint-label mismatch'
    monthly = {}
    for month in sorted({r['month'] for r in rows}):
        sub = [r for r in rows if r['month'] == month]
        monthly[month] = {**metrics(sub), 'provenance': dict(Counter(provenance(r) for r in sub)),
                          'other_act_n': sum(r['action'] == 'other_act' for r in sub)}
    with args.slide_csv.open() as handle:
        for row in csv.DictReader(handle):
            m = monthly[row['month']]
            assert m['n'] == int(row['eligible_articles'])
            for key in ('align', 'rep', 'frame'):
                assert abs(m['P'][key] - float(row[key + '_two_sided'])) < 1e-12
                for code, name in [('-1', 'negative'), ('0', 'zero'), ('1', 'positive')]:
                    assert abs(m['margins'][key][code] / m['n'] - float(row[key + '_' + name])) < 1e-12
    details = {}
    for month in ('2024-01', '2024-02', '2024-03', '2024-04'):
        sub = [r for r in rows if r['month'] == month]
        both = [r for r in sub if r['align'] == '1' and r['rep'] == '-1']
        details[month] = {
            'all_records': distributions(sub),
            'by_label': {key + '_' + label: distributions([r for r in sub if r[key] == label])
                         for key in ('align', 'rep', 'frame') for label in ('-1', '0', '1')},
            'positive_alignment_negative_reputation': {
                'n': len(both), 'positive_alignment_denominator': monthly[month]['margins']['align']['1'],
                'framing_counts': {str(v): sum(r['frame'] == str(v) for r in both) for v in (-1, 0, 1)}},
            'provenance_sensitivity': {name: metrics([r for r in sub if (provenance(r) == 'domestic') == (name == 'domestic')])
                                       for name in ('domestic', 'non_domestic')},
        }
    same_source = {source: {month: metrics([r for r in rows if r['month'] == month and r['source'] == source])
                           for month in ('2024-01', '2024-02', '2024-03', '2024-04')}
                   for source in ('xalimasn.com', 'sudquotidien.sn', 'lasnews.sn', 'france24.com')}
    baseline = [r for r in rows if '2023-11' <= r['month'] <= '2024-01']
    key_comparison = {action: {month: metrics([r for r in rows if r['month'] == month and r['action'] == action])
                                for month in ('2024-01', '2024-02', '2024-03', '2024-04')}
                      for action in ('protest_march', 'elect_vote', 'ban_disperse', 'impose_restrict')}
    assert details['2024-02']['positive_alignment_negative_reputation']['n'] == 83
    assert details['2024-02']['positive_alignment_negative_reputation']['positive_alignment_denominator'] == 132
    assert [key_comparison['protest_march'][m]['n'] for m in ('2024-02', '2024-03')] == [51, 4]
    assert [key_comparison['elect_vote'][m]['n'] for m in ('2024-02', '2024-03')] == [14, 201]
    output = {
        'schema': 'senegal_contributor_summary_v1', 'evaluated_government': 'SEN',
        'months': ['2023-01', '2024-12'], 'selected_n': len(rows),
        'snapshot': {key: snapshot[key] for key in ('audit_cutoff', 'commit', 'prompt_sha256', 'valid_records', 'eligible_records')},
        'input_receipts': receipts, 'snapshot_sha256': digest(args.snapshot),
        'frozen_scope_sha256': spec['sha256'], 'slide_csv_sha256': digest(args.slide_csv),
        'script_sha256': digest(Path(__file__)),
        'role_key': ROLES,
        'reconciliation': {'full_valid_and_eligible_counts': True, 'full_27_joint_cells': True,
                           'all_24_slide_months_counts_margins_and_P': True},
        'definitions': {
            'unit': 'One article record and its primary selected action, not a count of unique real-world events.',
            'eligible': 'Government and action identified; align, rep and frame each -1, 0 or +1. Zeros retained.',
            'P': '4 × positive share × negative share, with all common-eligible articles as denominator.',
            'nonzero_share': '(positive + negative) / all common-eligible articles.',
            'domestic': 'Recorded publication_country equals evaluated government SEN.',
            'non_domestic': 'Recorded publication country differs from SEN, including ALL/unknown provenance.',
            'role': 'Institutional role, not evidence of direct affiliation with the incumbent.',
            'other_act': 'Residual primary-action category; retained in denominators but omitted from specified-action rankings.',
            'target_null': 'No coded entity target. This does not establish that an action is unrelated to the evaluated government.',
        },
        'limits': ['Descriptive model labels, not observed public opinion or causal effects.',
                   'Source, event, genre and available-record composition may vary by month.',
                   'Publication-country metadata is not proof of an outlet’s nationality, ownership or audience.',
                   'The compact caches contain no article text, actor names or identifiers.',
                   'Zero includes mixed or insufficient directional evidence; not all zeros imply neutral language.'],
        'monthly': monthly, 'detail_months': details, 'key_action_comparison': key_comparison,
        'same_source_comparison': same_source,
        'focused_relationships': {
            'february_security_to_civic_movements': {
                **metrics([row for row in rows if row['month'] == '2024-02' and row['actor_role'] == 'G' and row['target_role'] == 'K']),
                **distributions([row for row in rows if row['month'] == '2024-02' and row['actor_role'] == 'G' and row['target_role'] == 'K']),
            },
        },
        'prior_three_months_2023_11_to_2024_01': {**metrics(baseline), **distributions(baseline)},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'selected_n': len(rows), 'all_reconciliations_passed': True,
                      'output_filename': args.output.name}))


if __name__ == '__main__':
    main()
