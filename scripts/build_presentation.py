#!/usr/bin/env python3
"""Build static figures and an offline HTML talk from the released aggregates."""
from pathlib import Path
from collections import Counter
import json
import html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'slides'
FIG = OUT / 'figures'
FIG.mkdir(parents=True, exist_ok=True)
D = json.loads((ROOT / 'data/monthly_complete_snapshot.json').read_text())
MONTHS = D['months']
N = sum(m['valid'] for m in MONTHS)
assert N == 542981 and len(MONTHS) == 17
TOTALS = {}
for axis in ['align', 'rep', 'frame']:
    count = Counter()
    for month in MONTHS:
        count.update(month['axes'][axis])
    assert sum(count.values()) == N
    TOTALS[axis] = count

BG, INK, RED, TEAL, GRAY, LIGHT = '#faf8f3', '#172a3a', '#b44b45', '#14786f', '#b6bdc3', '#e7e5df'
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':16, 'text.color':INK,
                     'axes.labelcolor':INK, 'xtick.color':INK, 'ytick.color':INK,
                     'axes.spines.top':False, 'axes.spines.right':False,
                     'axes.spines.left':False, 'axes.spines.bottom':False,
                     'figure.facecolor':BG, 'axes.facecolor':BG, 'svg.fonttype':'path'})

def save(fig, name):
    for ext in ['svg', 'png']:
        fig.savefig(FIG / f'{name}.{ext}', dpi=180, bbox_inches='tight', facecolor=BG,
                    metadata={'Creator':'Beyond Sentiment aggregate reproduction'})
    plt.close(fig)

names = ['Action alignment', 'Reputational implication', 'Article orientation']
fig, ax = plt.subplots(figsize=(13.7,4.4))
left = np.zeros(3)
for label, color, legend in [('-1',RED,'Negative'),('0',GRAY,'Zero'),('1',TEAL,'Positive'),('null',LIGHT,'Not codable')]:
    values=np.array([TOTALS[a][label]/N*100 for a in ['align','rep','frame']])
    ax.barh(np.arange(3), values, left=left, color=color, height=.50, label=legend)
    for i,v in enumerate(values):
        small = v < 5
        ax.text(left[i]+v/2, i-.30 if small else i, f'{v:.1f}%', ha='center',
                va='bottom' if small else 'center', fontsize=12,
                color=color if small else ('white' if label in ('-1','1') else INK), weight='bold')
    left += values
ax.set_yticks(range(3),names); ax.invert_yaxis(); ax.set_xlim(0,100)
ax.set_xlabel('Percent of all valid outcomes, including nulls')
ax.set_xticks([0,25,50,75,100]); ax.tick_params(length=0,pad=10)
ax.legend(ncol=4,loc='upper center',bbox_to_anchor=(.5,1.22),frameon=False)
fig.tight_layout(); save(fig,'label-distributions')

fig, ax = plt.subplots(figsize=(13.7,4.7))
y=np.arange(3)
for offset,label,color,name in [(-.16,'-1',RED,'Negative'),(.16,'1',TEAL,'Positive')]:
    values=[TOTALS[a][label]/N*100 for a in ['align','rep','frame']]
    ax.barh(y+offset,values,height=.27,color=color,label=name)
    for i,v in enumerate(values): ax.text(v+.16,i+offset,f'{v:.2f}%',va='center',fontsize=16)
ax.set_yticks(y,names); ax.invert_yaxis(); ax.set_xlim(0,11.4)
ax.set_xticks([0,2,4,6,8,10]); ax.set_xlabel('Percent of all 542,981 valid outcomes')
ax.tick_params(length=0,pad=10); ax.legend(ncol=2,loc='upper center',bbox_to_anchor=(.5,1.20),frameon=False)
fig.tight_layout(); save(fig,'directional-shares')

fig, ax = plt.subplots(figsize=(13.7,4.8))
x=np.arange(17); cov=[m['valid']/m['input_clear']*100 for m in MONTHS]
ax.bar(x,cov,color=TEAL,width=.69)
ax.set_ylim(0,100); ax.set_ylabel('Valid complete-prompt coverage (%)')
ax.set_xticks(x,[m['month'][2:] for m in MONTHS],rotation=45,ha='right',fontsize=12)
ax.set_yticks([0,25,50,75,100]); ax.tick_params(length=0,pad=8)
ax.axhline(N/sum(m['input_clear'] for m in MONTHS)*100,color=INK,ls='--',lw=1.2)
ax.text(16.5,95,'Overall 86.91%',ha='right',fontsize=15)
fig.tight_layout(); save(fig,'monthly-coverage')

slides=[]
def slide(title, body, note, source='', kind=''):
    slides.append({'title':title,'body':body,'note':note,'source':source,'kind':kind})
def table(headers, rows):
    return '<table><thead><tr>'+''.join(f'<th>{x}</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{x}</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'
def figure(name, alt):
    return f'<img class="chart" src="figures/{name}.svg" alt="{html.escape(alt)}">'

slide('Beyond Sentiment',
      '<p class="subtitle">Actions, Reputation, and Political Bias<br>in Civic News</p><p class="event">PDRI/DevLab<br>November 11, 2026</p><p class="covernote">Research in progress<br>Descriptive evidence frozen October 29, 2026</p>',
      'The central contribution is a measurement design. We distinguish an action’s political direction, its implication for a government’s performance or legitimacy, and the article’s own evaluative voice. Present this as ongoing research, with a transparent descriptive checkpoint and a validation agenda. Confirm the final team author list before the talk.',kind='cover')

slide('The political meaning of a negative report',
      '<p class="lead">A report can describe government abuse without adding hostile editorial language.</p><p>Coercion against peaceful opponents may strengthen an incumbent’s political position while damaging its legitimacy.</p><p>The same event can receive descriptive coverage, endorsement, or condemnation.</p><p class="takeaway">These distinctions matter for studying accountability, media control, and the information citizens receive.</p>',
      'This is a conceptual motivation, not an empirical claim that any particular outlet or country behaves this way. A single positive/negative sentiment label can combine fundamentally different relationships. Our question is what is reported and how it is presented. Effects on audiences need additional evidence.',
      'Conceptual illustration. Definitions: complete prompt, October 20 release.')

slide('Three dimensions, one incumbent government',
      table(['Dimension','Object of judgment','Directional labels'],[
          ['Action alignment','The selected action relative to the incumbent','Supports / opposes'],
          ['Reputational implication','Performance or legitimacy implied by the action and tied facts','Favorable / unfavorable'],
          ['Article orientation','Explicit evaluation in the title or narrator’s voice','Favors / criticizes']])+
      '<p class="small">Zero = neutral, mixed, or insufficient directional evidence. Null = not codable.</p>',
      'Each dimension refers to the same national incumbent government at the publication date. Alignment is not moral approval. Reputation is a reasonable-observer implication rather than a measured opinion change. Frame is narrower than selection bias or outlet ideology. The broad zero category is intentional and must stay separate from null.',
      'Codebook and prompts/civic_20261020_complete_v1.txt')

slide('A synthetic contrast in narrator evaluation',
      '<p class="example">“Police dispersed peaceful anti-government demonstrators.”</p><p class="small">Synthetic context explicitly links the police to the national cabinet.</p>'+
      table(['Narration','Align','Rep','Frame'],[
          ['Descriptive account of that action','+1','−1','0'],
          ['Adds “a necessary operation that restored order”','+1','−1','+1']])+
      '<p class="takeaway">The action and reputational implication stay fixed. The presentation cue changes.</p>',
      'These are synthetic calibration examples 1 and 2 from the prompt, not observed country cases. The anti-government target supports alignment +1. Peaceful demonstrators and explicit cabinet affiliation support reputation -1. The added necessary-operation wording legitimates the action and supports frame +1. This illustrates the intended distinction; measured within-article divergence still needs joint tables and human validation.',
      'Synthetic calibration examples 1–2, complete prompt. No empirical country claim.')

slide('How news becomes a coded observation',
      '<ol class="process"><li><strong>Source selection</strong><span>Available news enters the civic corpus through collection and relevance rules.</span></li><li><strong>Supplied English</strong><span>The exact stored translated title and body enter the request.</span></li><li><strong>Action and government</strong><span>One prioritized action, actor, entity target, and national incumbent.</span></li><li><strong>Labels and evidence</strong><span>Three separate judgments, exact evidence spans, explicit nulls and flags.</span></li></ol>',
      'The source pool is not all news or all political events. The current tolerant input policy excludes empty or wholly non-English API inputs but permits minor defects. It supersedes the historical two-sentence quality rule. Exact use of stored translated text does not guarantee fidelity to the original. One selected action means this is not an exhaustive event census.',
      'Codebook; October 17 input policy; October 20 complete prompt.')

slide('A fixed window for the first descriptive results',
      '<p class="big">542,981</p><p class="lead">Valid complete-prompt outcomes<br>January 2025–May 2026</p>'+
      table(['Frozen input-clear pool','Stored complete-prompt outcomes','Valid outcomes'],[['624,751','552,208','542,981']])+
      '<p class="small">370 source domains. 71 publication-country codes plus international/regional sources. Article counts are not unique event counts.</p>',
      'The independent database audit is 2026-10-29 05:20:31 UTC. Stored outcomes include failures; 9,227 complete-prompt outcomes are outside valid label tables. There are 61,996 stored older-prompt records in the same time window, also excluded. June 2026 remains older-prompt data at this checkpoint. We fix the window so filling older years does not silently change the analysis population.',
      'Frozen monthly snapshot and data card. Storage checkpoint: October 29, 2026, 05:20 UTC.')

slide('Complete-prompt coverage varies by month',
      figure('monthly-coverage','Monthly valid complete-prompt outcomes divided by the frozen input-clear pool. Overall 86.91 percent.')+
      '<p class="small">Denominator: each month’s input-clear source pool. Coverage does not measure model accuracy or coverage of all news.</p>',
      'The dashed line shows overall valid complete-prompt coverage, 86.91 percent. Month-to-month differences can change the composition of the coded sample. We retain the monthly denominators, and we need source-level sensitivity analyses before treating a changing label rate as political change. June is excluded rather than shown as substantive absence.',
      'data/monthly_coverage.csv. January 2025–May 2026.')

slide('Most outputs have no clear directional label',
      figure('label-distributions','Full distributions of negative, zero, positive and null labels for all three dimensions.')+
      '<p class="small">Zero includes neutral, mixed, and insufficient evidence. An 86.70% zero framing share does not establish unbiased media.</p>',
      'All three rows use the same denominator of 542,981 valid outputs, including nulls. The zero class combines several different reasons not to assign direction. In particular, the frame rule requires an explicit narrator cue and is conservative about translated wording. It does not evaluate story selection or omitted perspectives.',
      'data/label_summary.csv. Every dimension sums to 542,981.')

slide('Negative reputational implications are more frequent',
      figure('directional-shares','Negative versus positive shares: alignment 8.27 vs 7.24; reputation 9.68 vs 3.97; framing 4.96 vs 3.01 percent.')+
      '<p class="small">Shares retain all valid outputs in the denominator. This view displays only the directional categories.</p>',
      'This is a descriptive fact about the model-coded cohort. It does not show that media are biased against government. Adverse events may be more newsworthy or more common in the selected civic corpus. Outlet/country mix and annotation errors can also affect this pattern. Different marginals alone do not show how the dimensions combine within individual articles.',
      'data/label_summary.csv. Model-coded marginals, not validated population estimates.')

slide('Competing explanations for the pattern',
      table(['Explanation','Evidence needed to assess it'],[
          ['Events and civic-news selection','Comparable events, topic/action mix, collection denominators'],
          ['Outlet and country composition','Stable source panels and alternative weighting'],
          ['Editorial presentation','Matched coverage of the same action with narrator cues'],
          ['Measurement error','Blinded human coding and original-language review']])+
      '<p class="takeaway">The pooled distribution motivates a research design. It does not choose among these explanations.</p>',
      'The count of negative articles is a mixture of event occurrence, coverage, source selection, translation, and measurement. A balanced source panel can address one compositional problem, but does not eliminate shared event shocks or capture all outlets. Avoid inferring bias from the sign of the pooled reputation distribution.',
      'Proposed analyses. See docs/research-design.md.')

slide('Two comparisons for studying media control',
      '<div class="columns"><div><h3>Which events receive coverage?</h3><p>Compare the selection and prominence of government-relevant actions across outlets.</p><p class="small">Needs a common event or exposure denominator.</p></div><div><h3>How is the same event presented?</h3><p>Compare narrator evaluation within matched events, government targets, and time periods.</p><p class="small">Needs joint article-level measures and credible event matching.</p></div></div><p class="takeaway">Ownership and regulatory variation become explanatory variables after measurement and comparability checks.</p>',
      'Frame does not itself recover gatekeeping or source-selection bias. Event matching separates variation in what happened from variation in presentation, but matching quality and article completeness still matter. Ownership or regulation associations remain observational without an identification strategy. An ownership change can be studied within outlets if the timing and counterfactual are defensible.',
      'Research-design proposal; literature in references/references.bib.')

slide('Political implications and testable hypotheses',
      table(['Question','Proposed test','Remaining requirement'],[
          ['Does media control alter government portrayal?','Within-outlet change around ownership or regulatory shifts','Credible timing and comparison group'],
          ['Do articles legitimize reputationally harmful conduct?','Joint reputation × frame table within matched actions','Semantic validation and joint data'],
          ['Does portrayal affect citizen attitudes?','Link exposure to survey or experimental outcomes','Audience data and identification']]),
      'These are hypotheses, not results from the current marginals. The second question directly uses the distinction between rep and frame. A joint distribution must be calculated before claiming such a relationship exists in this corpus. A reputational implication label does not measure actual audience persuasion, and societal polarization needs its own definition and data.',
      'Proposed research agenda, not completed tests.')

slide('Current validation evidence',
      table(['Check','What it establishes','What remains open'],[
          ['Schema and exact spans','Output conforms to mechanical rules','Correct political meaning'],
          ['Independent storage readback','Records were stored as checked','Accuracy or representativeness'],
          ['Exploratory AI reviews','Concrete failure modes for follow-up','Held-out human accuracy']])+
      '<p class="small">A recent 40-case review identified five clear scope/extraction issues and upstream text problems. It is a diagnostic review, not an accuracy estimate.</p>',
      'The smaller reviews were useful for discovering failure mechanisms, including scope, action selection, entity targets, and translation defects. Agreement among AI reviews is not independent human gold. Historical human work on an earlier sentiment design cannot be carried over as accuracy for the complete three-dimension prompt. Keep failed outputs and disputed cases visible.',
      'Dated diagnostic reviews summarized in docs/validation.md.')

slide('A validation design for academic claims',
      '<ol class="process"><li><strong>Freeze the task</strong><span>Prompt, translation policy, incumbent scope, and evaluation rubric.</span></li><li><strong>Sample the difficult and common cases</strong><span>Countries, languages, source types, action categories, nulls and all label directions.</span></li><li><strong>Code independently before reconciliation</strong><span>Blinded human judgments, original-language checks, and recorded disagreements.</span></li><li><strong>Report field-specific performance</strong><span>Confusion matrices, classwise recall/precision, uncertainty and subgroup failures.</span></li></ol>',
      'Separate a development set from held-out evaluation, and report original coder agreement before adjudication. Oversample rare labels and uncertain reference cases for diagnosis, but reweight or separately report prevalence-sensitive metrics. Evaluate gov identity and actor/target extraction in addition to label signs. Prompt revisions require new versioned evaluations. See the validation document for the complete proposed protocol.',
      'Proposed protocol: docs/validation.md.')

slide('The research package and next analyses',
      '<div class="columns"><div><h3>Available with this talk</h3><ul><li>Codebook and exact prompt</li><li>Frozen monthly aggregates</li><li>Reproducible tables and figures</li><li>Research design and validation plan</li></ul></div><div><h3>Next empirical work</h3><ul><li>Joint label distributions</li><li>Source/country composition checks</li><li>Blinded semantic evaluation</li><li>Historical entity standardization</li></ul></div></div><p class="small"><a href="https://github.com/lin61302/media-bias-genai">github.com/lin61302/media-bias-genai</a></p>',
      'This repository is the shared research package. It contains no raw news articles or private correspondence. Literature on institutions/polarization and incumbent coverage/attitudes will help sharpen the next designs. Later data refreshes should be frozen and versioned rather than silently replacing the evidence shown today. November 2 is a working synthesis checkpoint, not a guarantee of corpus completion.',
      'Repository README and presentation plan.')

slide('Questions for discussion',
      '<p class="discussion">Which disagreements belong inside a useful reputational measure?</p><p class="discussion">What comparison best separates event selection from evaluative presentation?</p><p class="discussion">Which institutional setting offers a credible test of media control?</p><p class="discussion">What evidence would connect portrayal to political attitudes?</p>',
      'Invite criticism of the measurement construct as well as suggestions for design. In particular, the reasonable-observer criterion can conceal disagreement about rights, performance and legitimacy. Consider whether those disagreements should be coded separately, rather than forcing agreement. The purpose of the project is to make relationships inspectable enough to support stronger political science.',
      'Research in progress. October 29, 2026 descriptive snapshot.')

slide('Appendix: scope and attribution',
      table(['Boundary','Coding consequence'],[
          ['National incumbent at publication date','A court, province, agency, or former leader is not automatically the incumbent'],
          ['One prioritized action','The record does not inventory every event in the article'],
          ['Attributed allegation','Code the accusation and retain claim status, not wrongdoing as proven fact'],
          ['Exact supplied English','Complete use of supplied text does not guarantee a faithful original translation'],
          ['Missing action or government','Apply dimension-specific null rules; framing can remain codable without an action']]),
      'The current government-country code does not standardize leaders, offices, or regimes. The membership/role distinction is essential: a domestic institution can be relevant without being directly affiliated with the incumbent. Future entity resolution must preserve the raw spans and temporal provenance.',
      'Exact complete prompt, October 20 release.')

slide('Appendix: research foundations',
      table(['Research foundation','Selected primary studies'],[
          ['Media capture and control','<a href="https://doi.org/10.1257/aer.96.3.720">Besley &amp; Prat (2006)</a><br><a href="https://doi.org/10.1016/j.jpubeco.2014.06.004">Gehlbach &amp; Sonin (2014)</a>'],
          ['Audience demand and consequences','<a href="https://doi.org/10.3982/ECTA7195">Gentzkow &amp; Shapiro (2010)</a><br><a href="https://doi.org/10.1162/qjec.122.3.1187">DellaVigna &amp; Kaplan (2007)</a>'],
          ['Text measurement and comparative validity','<a href="https://doi.org/10.1093/pan/mps028">Grimmer &amp; Stewart (2013)</a><br><a href="https://doi.org/10.1093/pan/mpu019">Lucas et al. (2015)</a>']])+
      '<p class="small">Full citations and additional LLM/inference references are in the repository bibliography. These studies motivate the design; they do not validate this project’s outputs.</p>',
      'Use the linked primary sources and research-design document for citations and the precise scope of earlier results. The selected bibliography is a starting point for the team literature synthesis, not a claim that the ongoing literature review is complete. Existing causal media findings do not establish effects for this dataset.',
      'docs/research-design.md, docs/validation.md, references/references.bib')

CSS='''
:root{--paper:#faf8f3;--ink:#172a3a;--accent:#14786f;--muted:#536574}
*{box-sizing:border-box}html,body{margin:0;background:#deded9;color:var(--ink);font-family:Arial,Helvetica,sans-serif}
main{padding:24px 16px 82px}.slide{position:relative;width:min(1280px,calc(100vw - 32px));aspect-ratio:16/9;margin:0 auto;background:var(--paper);padding:48px 62px 60px;display:none;overflow:hidden}.slide.active{display:block}
h1,h2{font-family:Georgia,'Times New Roman',serif;font-weight:normal;margin:0 0 24px;line-height:1.12;letter-spacing:-.8px}h1{font-size:76px}h2{font-size:46px}h3{font-size:26px;margin:0 0 20px;font-weight:600}p,li{font-size:27px;line-height:1.45}p{margin:16px 0}.lead{font-size:32px;line-height:1.3}.small{font-size:20px;line-height:1.4;color:var(--muted)}.takeaway{font-size:26px;color:var(--accent);margin-top:28px}.subtitle{font-size:39px;line-height:1.25;margin-top:30px}.event{margin-top:42px;font-size:24px}.covernote{font-size:20px;color:var(--muted);margin-top:32px}.cover{padding-top:74px}.big{font-size:76px;margin:5px 0 0;line-height:1;font-family:Georgia,serif;color:var(--accent)}.example{font-family:Georgia,serif;font-size:35px;line-height:1.35;padding:12px 0}.chart{display:block;width:100%;height:405px;object-fit:contain}.columns{display:grid;grid-template-columns:1fr 1fr;gap:58px;margin-top:34px}.columns p,.columns li{font-size:25px}.columns .small{font-size:20px}.columns ul{padding-left:24px}.process{list-style:none;padding:0;margin:12px 0}.process li{display:grid;grid-template-columns:280px 1fr;gap:30px;border-top:1px solid #cdd2d3;padding:20px 0;font-size:24px}.process span{color:var(--muted)}table{border-collapse:collapse;width:100%;margin:24px 0;font-size:23px;line-height:1.35}th{text-align:left;font-size:20px;letter-spacing:.2px;color:var(--muted);font-weight:600;border-bottom:2px solid #9ba8ae;padding:12px 15px 12px 0}td{vertical-align:top;padding:17px 20px 17px 0;border-bottom:1px solid #d9dcda}td:first-child{font-weight:600}.discussion{font-size:31px;line-height:1.3;margin:27px 0;padding-left:20px;border-left:3px solid var(--accent)}a{color:var(--accent)}footer{position:absolute;bottom:22px;left:62px;right:62px;font-size:15px;color:var(--muted);display:flex;justify-content:space-between;gap:30px}footer .source{max-width:92%}.notes{display:none;width:min(1280px,calc(100vw - 32px));margin:0 auto;padding:22px 40px;background:#fff;font-size:19px;line-height:1.55}.notes-on .notes.active{display:block}.all .slide{display:block;margin-bottom:24px}.all.notes-on .notes{display:block;margin-top:-24px;margin-bottom:24px}.controls{position:fixed;bottom:0;left:0;right:0;background:#172a3a;color:#fff;padding:12px 20px;display:flex;align-items:center;justify-content:center;gap:14px;font-size:14px;z-index:4}.controls button{border:1px solid #647780;color:white;background:transparent;padding:8px 13px;border-radius:3px;cursor:pointer}.controls button:focus-visible{outline:3px solid #66d2bc}.hint{opacity:.8}.controls a{color:#a4e0d4}
@media(max-width:1050px){.slide{aspect-ratio:auto;min-height:620px;padding:32px 34px 64px}h1{font-size:60px}h2{font-size:37px}p,li{font-size:23px}.lead{font-size:27px}table{font-size:20px}th{font-size:17px}td{padding:13px 12px 13px 0}.process li{grid-template-columns:230px 1fr;font-size:21px}.chart{height:340px}footer{left:34px;right:34px}.hint{display:none}}
@media(max-width:650px){main{padding:0 0 100px}.slide{width:100%;padding:28px 24px 82px;min-height:100vh}h1{font-size:51px}h2{font-size:34px}.subtitle{font-size:29px}p,li{font-size:21px}.lead{font-size:25px}.big{font-size:62px}.columns{grid-template-columns:1fr;gap:22px}.columns p,.columns li{font-size:21px}.process li{display:block;font-size:21px}.process span{display:block;margin-top:6px}.small{font-size:17px}.chart{height:280px}table{font-size:16px}th{font-size:15px}td{padding:10px 9px 10px 0}.example{font-size:27px}.discussion{font-size:25px}footer{font-size:12px;left:24px;right:24px;bottom:20px}.controls{gap:6px;flex-wrap:wrap}.controls button{padding:6px 9px}.takeaway{font-size:22px}}
@page{size:13.333in 7.5in;margin:0}
@media print{body,html{background:var(--paper)}main{padding:0}.slide,.slide.active,.all .slide{display:block;width:13.333in;height:7.5in;min-height:0;aspect-ratio:auto;margin:0;padding:48px 62px 60px;break-after:page;page-break-after:always}.controls,.notes,.notes-on .notes.active,.all.notes-on .notes{display:none!important}.cover{padding-top:74px}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
'''
JS='''
const slides=[...document.querySelectorAll('.slide')];let index=0;
function show(n){index=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,i)=>{s.classList.toggle('active',i===index);s.nextElementSibling.classList.toggle('active',i===index)});document.querySelector('#count').textContent=`${index+1} / ${slides.length}`;history.replaceState(null,'',`#${index+1}`);document.title=slides[index].querySelector('h1,h2').textContent+' — Beyond Sentiment';if(document.body.classList.contains('all'))slides[index].scrollIntoView({behavior:'smooth'});}
document.querySelector('#prev').onclick=()=>show(index-1);document.querySelector('#next').onclick=()=>show(index+1);
function notes(){document.body.classList.toggle('notes-on');document.querySelector('#notes').setAttribute('aria-pressed',document.body.classList.contains('notes-on'));}
function all(){document.body.classList.toggle('all');document.querySelector('#all').setAttribute('aria-pressed',document.body.classList.contains('all'));show(index);}
document.querySelector('#notes').onclick=notes;document.querySelector('#all').onclick=all;
document.addEventListener('keydown',e=>{if(e.target.closest('button,a,input,textarea'))return;if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(index+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(index-1)}if(e.key==='Home')show(0);if(e.key==='End')show(slides.length-1);if(e.key.toLowerCase()==='n')notes();if(e.key.toLowerCase()==='a')all();});
const initial=Number(location.hash.slice(1));show(Number.isFinite(initial)&&initial>0?initial-1:0);
'''
parts=['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Beyond Sentiment</title><meta name="description" content="Research in progress: actions, reputation, and political bias in civic news. November 11, 2026 presentation."><style>'+CSS+'</style></head><body><main>']
for i,s in enumerate(slides,1):
    h='h1' if i==1 else 'h2'
    parts.append(f'<section class="slide {s["kind"]}" id="slide-{i}" aria-label="Slide {i}: {html.escape(s["title"])}"><{h}>{html.escape(s["title"])}</{h}>{s["body"]}<footer><span class="source">{html.escape(s["source"])}</span><span>{i}</span></footer></section><aside class="notes"><strong>Speaker notes</strong><br>{html.escape(s["note"])}</aside>')
parts.append('</main><nav class="controls" aria-label="Presentation controls"><button id="prev" aria-label="Previous slide">Previous</button><span id="count" aria-live="polite"></span><button id="next" aria-label="Next slide">Next</button><button id="notes" aria-pressed="false">Notes (N)</button><button id="all" aria-pressed="false">All slides (A)</button><span class="hint">Arrow keys navigate</span><a href="https://github.com/lin61302/media-bias-genai">Repository</a></nav><script>'+JS+'</script></body></html>')
(OUT/'index.html').write_text('\n'.join(parts))
(OUT/'.nojekyll').touch()
print(f'Built {len(slides)} slides and 3 figures from {N:,} outcomes.')
