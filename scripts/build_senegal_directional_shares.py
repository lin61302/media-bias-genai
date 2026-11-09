#!/usr/bin/env python3
"""Plot separate signs from the unchanged, audited Senegal aggregate export."""
import csv
import hashlib
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'slides/figures/data'
FIG = ROOT / 'slides/figures'
source = DATA / '09_senegal_monthly_indices.csv'
digest = hashlib.sha256(source.read_bytes()).hexdigest()
assert digest == '72fccdcdd7b4ffa1e73393c69edb6b2ceb2a6f17dbf196fbcaf374f9dee0e546'
all_rows = list(csv.DictReader(source.open()))
rows = [r for r in all_rows if '2023-10' <= r['month'] <= '2024-06']
assert len(rows) == 9
for r in all_rows:
    for field in ('align', 'rep', 'frame'):
        assert abs(sum(float(r[f'{field}_{sign}']) for sign in ('negative', 'zero', 'positive')) - 1) < 1e-12

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.spines.left': False, 'axes.edgecolor': '#b8c1cc',
                     'svg.fonttype': 'none', 'svg.hashsalt': 'senegal-shares-v1'})
fig, axes = plt.subplots(1, 3, figsize=(13.5, 5.55), sharey=True)
fig.subplots_adjust(left=.055, right=.985, bottom=.26, top=.78, wspace=.13)
x = list(range(len(rows)))
for ax, field, title in zip(axes, ('align', 'rep', 'frame'),
                            ('Political alignment', 'Reputational implication', 'Framing')):
    ax.axvspan(3.6, 4.4, color='#f1e7d8', zorder=0)
    ax.axvline(5.5, color='#7b8490', linestyle=':', linewidth=1.2)
    for sign, color, label in [('positive', '#087e68', 'Positive'), ('negative', '#ba3e3e', 'Negative')]:
        ax.plot(x, [float(r[f'{field}_{sign}']) for r in rows], marker='o', markersize=5,
                linewidth=2.3, color=color, label=label)
    ax.set_title(title, fontsize=14, fontweight='bold', loc='left', pad=15, color='#172f50')
    ax.set_xticks(x)
    ax.set_xticklabels(['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], fontsize=10)
    ax.set_ylim(0, .40)
    ax.set_yticks([0,.1,.2,.3,.4])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.grid(axis='y', color='#e3e7ec', linewidth=.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis='y', length=0)
    for i,r in enumerate(rows):
        ax.text(i, -.20, r['eligible_articles'], transform=ax.get_xaxis_transform(), ha='center', fontsize=9, color='#4f5e70')
    ax.text(0, -.12, '2023', transform=ax.get_xaxis_transform(), fontsize=9, color='#4f5e70')
    ax.text(3, -.12, '2024', transform=ax.get_xaxis_transform(), fontsize=9, color='#4f5e70')
fig.text(.055, .94, 'Shares of reporting that evaluate Senegal’s incumbent', fontsize=17, fontweight='bold', color='#172f50')
fig.text(.055, .875, 'Election delayed in February; held March 24. Faye takes office April 2 (dotted line).', fontsize=12, color='#4f5e70')
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='lower left', bbox_to_anchor=(.045,.035), frameon=False, ncol=2, fontsize=12)
fig.text(.985, .09, 'Numbers below each panel = eligible articles in that month', ha='right', fontsize=11, color='#4f5e70')
fig.text(.985, .045, 'Domestic and international sources · zeros included · no minimum-count mask', ha='right', fontsize=11, color='#4f5e70')
outputs=[]
for ext in ('png','pdf','svg'):
    p=FIG/f'09_senegal_directional_shares.{ext}'
    fig.savefig(p,dpi=180,facecolor='white',metadata={'Creator': 'MLP frozen aggregate figure'} if ext=='pdf' else None)
    if ext=='svg': p.write_text(re.sub(r'[ \t]+(?=\n)', '', p.read_text()))
    outputs.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
plt.close(fig)
manifest={'source':str(source.relative_to(ROOT)), 'source_sha256':digest,
          'snapshot':'November 8, 2026 frozen analytical release',
          'filter':{'government':'SEN','publication_origin':'all','display_start':'2023-10','display_end':'2024-06'},
          'denominator':'All eligible records per month, including zero; unknown/uncodable excluded upstream.',
          'measure':'Each sign count divided by the eligible monthly count; not P and not public opinion.',
          'full_export_months':len(all_rows),'display_months':len(rows),
          'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'outputs':outputs}
(DATA/'09_senegal_directional_shares_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'display_months':len(rows),'outputs':[o['path'] for o in outputs]}))
