"""Render the Kenya source comparison from the frozen, audited aggregate export."""
from pathlib import Path
import csv, hashlib, json, re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'slides/figures/data/13_kenya_source_comparison.json'
FIG = ROOT / 'slides/figures/13_kenya_source_comparison'
SOURCE_LABELS = {'nation.africa': 'Nation', 'kbc.co.ke': 'KBC', 'citizen.digital': 'Citizen Digital'}
COLORS = {'nation.africa': '#0072B2', 'kbc.co.ke': '#D55E00', 'citizen.digital': '#009E73'}
MONTHS = ['2024-%02d' % m for m in range(1, 9)]
MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']


def main():
    data = json.loads(INPUT.read_text())
    snapshot = json.loads((ROOT / 'slides/analysis_snapshot.json').read_text())
    assert data['snapshot']['commit'] == snapshot['commit']
    assert data['snapshot']['prompt_sha256'] == snapshot['prompt_sha256']
    assert data['evaluated_government'] == data['publication_country'] == 'KEN'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 16,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.edgecolor': '#cbd0d9', 'text.color': '#20272f',
                         'axes.labelcolor': '#20272f', 'xtick.color': '#4f5965',
                         'ytick.color': '#4f5965', 'pdf.fonttype': 42, 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.5))
    fig.subplots_adjust(left=.065, right=.98, top=.82, bottom=.32, wspace=.19)
    handles = []
    for index, (ax, measure, title) in enumerate(zip(axes, ['frame', 'rep'], ['Negative framing', 'Negative reputational implication'])):
        ax.axvspan(4.7, 5.3, color='#e9edf3', zorder=0)
        for source, label in SOURCE_LABELS.items():
            series = [data['monthly'][source][m] for m in MONTHS]
            values = [100 * row['negative_share'][measure] if row['n'] else float('nan') for row in series]
            line, = ax.plot(range(8), values, marker='o', markersize=6, linewidth=2.6,
                            color=COLORS[source], label=label)
            if index == 0: handles.append(line)
            # Label the selected June observation explicitly; offset the two lower labels.
            offset = {'nation.africa': (10, 5), 'kbc.co.ke': (10, 8) if index else (-10, -21),
                      'citizen.digital': (-10, -20) if index else (10, 5)}[source]
            ax.annotate('%.1f%%' % values[5], (5, values[5]), xytext=offset,
                        textcoords='offset points', color=COLORS[source], fontsize=14, fontweight='bold',
                        ha='right' if offset[0] < 0 else 'left',
                        arrowprops={'arrowstyle': '-', 'color': COLORS[source], 'lw': .8, 'shrinkA': 2, 'shrinkB': 5} if offset[0] < 0 else None,
                        bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': .9, 'pad': 1.0})
        ax.set_title(title, loc='left', fontsize=19, fontweight='bold', pad=13)
        ax.set_xlim(-.2, 7.35); ax.set_ylim(0, 50)
        ax.set_xticks(range(8)); ax.set_xticklabels(MONTH_LABELS, fontsize=15)
        ax.set_yticks([0, 10, 20, 30, 40, 50]); ax.yaxis.set_major_formatter(PercentFormatter(100, decimals=0))
        ax.grid(axis='y', color='#e2e6eb', linewidth=.7); ax.set_axisbelow(True)
        ax.tick_params(axis='both', length=0, pad=7)
    fig.legend(handles, list(SOURCE_LABELS.values()), loc='upper left', bbox_to_anchor=(.06, .985),
               ncol=3, frameon=False, fontsize=17, handlelength=2.3, columnspacing=2.4)
    fig.text(.98, .925, 'June: protests and Finance Bill withdrawal', ha='right', fontsize=14, color='#566477')
    tax = fig.add_axes([.065, .085, .915, .15]); tax.axis('off')
    cells = [[label] + [str(data['monthly'][source][m]['n']) for m in MONTHS]
             for source, label in SOURCE_LABELS.items()]
    table = tax.table(cellText=cells, colLabels=['Eligible articles'] + MONTH_LABELS, cellLoc='center',
                      colWidths=[.20]+[.10]*8, bbox=[0,0,1,1])
    table.auto_set_font_size(False); table.set_fontsize(13)
    for (row, col), cell in table.get_celld().items():
        cell.set_linewidth(0); cell.set_edgecolor('white')
        cell.set_facecolor('#f3f5f8' if row == 0 else 'white')
        if row == 0: cell.get_text().set_weight('bold')
        if col == 0:
            cell.get_text().set_ha('left')
            if row: cell.get_text().set_color(COLORS[list(SOURCE_LABELS)[row-1]])
        if col == 6 and row: cell.set_facecolor('#e9edf3'); cell.get_text().set_weight('bold')
    fig.text(.065, .025, 'January–August 2024 · Same evaluated government: Kenya · All eligible records in each source-month, including zeros',
             fontsize=11.5, color='#606976')
    FIG.parent.mkdir(parents=True, exist_ok=True)
    for extension in ['png', 'pdf', 'svg']:
        fig.savefig(str(FIG)+'.'+extension, dpi=180, facecolor='white')
    svg = Path(str(FIG)+'.svg')
    svg.write_text(re.sub(r'[ \t]+(?=\n)', '', svg.read_text()))
    plt.close(fig)
    out_csv = FIG.parent / 'data/13_kenya_source_monthly.csv'
    rows = []
    for source, label in SOURCE_LABELS.items():
        for month, cell in sorted(data['monthly'][source].items()):
            out = {'source': source, 'source_label': label, 'month': month, 'eligible_articles': cell['n'],
                   'shown_in_main_figure': month in MONTHS}
            for axis in ['align', 'rep', 'frame']:
                for code, sign in [('-1', 'negative'), ('0', 'zero'), ('1', 'positive')]:
                    out[axis+'_'+sign+'_n'] = cell['margins'][axis][code]
                    out[axis+'_'+sign+'_share'] = cell['margins'][axis][code]/cell['n'] if cell['n'] else None
            rows.append(out)
    with out_csv.open('w', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    manifest = {'input': INPUT.name, 'input_sha256': hashlib.sha256(INPUT.read_bytes()).hexdigest(),
                'builder_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'snapshot_commit': snapshot['commit'], 'plot_months': MONTHS,
                'export_months': data['period'], 'count_filter': None,
                'june_denominators': {s: data['monthly'][s]['2024-06']['n'] for s in SOURCE_LABELS},
                'interpretation': 'Negative-label shares of the common eligible source-month sample; zero retained. Descriptive model labels, not a causal source effect.',
                'window_note': 'Selected episode window January–August; all36 January–December cells exported. December KBC has n3.',
                'files': {Path(str(FIG)+'.'+ext).name: hashlib.sha256(Path(str(FIG)+'.'+ext).read_bytes()).hexdigest() for ext in ['png','pdf','svg']}}
    (FIG.parent/'data/13_kenya_figure_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({'figure': str(FIG), 'plotted_cells':24, 'exported_cells':len(rows)}))


if __name__ == '__main__':
    main()
