# Shared slides

[MediaBias_Polarization.qmd](MediaBias_Polarization.qmd) is the shared Quarto source. [MediaBias_Polarization.html](MediaBias_Polarization.html) is the rendered Reveal.js deck. Edit the QMD, then render the HTML before committing. The HTML embeds its resources for local viewing.

```sh
cd slides
quarto render MediaBias_Polarization.qmd
```

Open the HTML in a browser. Click a slide, then use **F** for fullscreen, arrow keys or Space to move, **M** for the menu, and **S** for speaker view. Share the slide window with the audience and keep speaker notes on your own display. If speaker view is blocked for a local file, serve this folder with `python3 -m http.server 8883 --bind 127.0.0.1` and open `http://127.0.0.1:8883/MediaBias_Polarization.html`.

## Current deck

The current source renders **24 slides**. The concepts lead through classifier selection, prompting and GenAI review to coverage. One measurement slide opens the analysis by separating directional share and balance, then explaining their combination in P. Country cases precede the separate foreign-government comparison.

| Slides | Content |
|---|---|
| 1–5 | Question, literature and common political reference |
| 6–7 | Audience questions and three concepts |
| 8–10 | Classifier and processing, prompting, GenAI event agreement and Astra review |
| 11 | Coverage and analytical sample |
| 12 | Directional share, conditional balance and proposed P, on one slide |
| 13–14 | Label distributions and alignment–reputation relationship |
| 15–16 | Senegal monthly series, actor groups and article examples |
| 17–19 | Kenya source series, institutional context and paired article example |
| 20 | Same outlet evaluating domestic and foreign governments: Kyiv Independent |
| 21–23 | Validation, research agenda and discussion |
| 24 | References |

The shared files contain the presentation, method qualifications and source notes. Personal speaking manuscripts are maintained separately outside this repository.

## Examples and figures

Red X / green checks on slide 6 distinguish general event valence from the three government-related questions the project addresses; they do not mark the questions or their answers as true or false.

The rescue/title contrast in the opening questions comes from calibration example 6: cabinet-affiliated services rescue 20 miners, while the title calls the rescue a “cynical publicity stunt.” It can be discussed orally as a second example: political alignment 0, reputational implication +1 and framing −1.

The police example on slide 7 is synthetic and comes from calibration examples 1–2 in the [complete prompt](../prompts/civic_20261020_complete_v1.txt). It explicitly supplies cabinet affiliation and peaceful anti-government demonstrators. It demonstrates alignment +1, reputation −1 and framing 0; the narrator’s “Police rightly restored order by dispersing the rioters” changes framing to +1. “Rioters” alone is not a sufficient cue. The negative reputational implication uses the prompt's explicit rights and lawful-conduct norms, not a democracy index or observed public-opinion change. It is not a sampled event or model-accuracy result.

The evaluated government is selected once for all three fields. Publication country is the default for domestic government-relevant affairs; the foreign-government exception requires a foreign focus and no codable judgment about the publication country's incumbent. The article date identifies who is incumbent, not which country must be evaluated. The complete rule, including `ALL` and multiple governments, is in prompt section 1.

Framing uses only the supplied title and narration. Prompt sections Input and 5 prohibit external event knowledge, other articles and inferred omissions. The comparison holds reported facts constant and asks what evaluation the narrator adds; it does not use an external neutral-news baseline. Explicit minimization of acknowledged wrongdoing can count. Differences in coverage, omitted details or emphasis across accounts require a separate comparative analysis; the most common account is not automatically neutral or correct. Words such as “rioters” or an attributed claim about public safety are not automatic framing labels.

The classifier keeps Erik's six-box overview style. Translation and the two civic encoder classifiers have distinct stages. Its lower half reports civic-event and civic-relevance classifier performance. The conceptual definitions appear once on slide 7; monthly aggregation appears once on slide 12. Edit [includes/classifier.qmd](includes/classifier.qmd) and [classifier.css](classifier.css). `pipeline_schematic.png` retains the earlier static figure for reference.

The classifier and separate monthly illustration are editable HTML in the included QMD files. Sample counts and the framing comparison table remain editable in the main QMD. [concepts.css](concepts.css) styles those slides. Keep the `includes` folder and both CSS files with the QMD when sharing the source. The rendered HTML embeds its viewing resources.

The four current empirical figures use the fixed [November 8 release](analysis_snapshot.json): January 2019–May 2026, **3,181,113 eligible articles** among 3,464,596 valid, independently stored complete-prompt records. This adds 810,250 valid and 740,801 eligible records to the previous slide snapshot. Earlier-year coverage is uneven. Processing admissions and separately tracked reruns are outside this analytical denominator.

| Figure | What it shows |
|---|---|
| [06_coverage_map.png](figures/06_coverage_map.png) | 71 publication countries and 211 evaluated-government codes. The maps have different quantities and scales. International/mixed source domains are separate. |
| [07_label_distributions.png](figures/07_label_distributions.png) | Three marginal distributions on the same eligible denominator. Zero combines neutral, mixed and insufficient directional evidence. |
| [08_alignment_reputation_joint.png](figures/08_alignment_reputation_joint.png) | Reputation conditional on alignment. Among pro-incumbent actions, 20.8% have negative reputational implications. |
| [09_senegal_monthly_indices.png](figures/09_senegal_monthly_indices.png) | Monthly two-sided index for each field, article volume and a sourced episode. All nonempty months are shown with exact article counts. Counts describe coverage volume, not independent events or a guarantee of precision. |

PDF and SVG versions are alongside each PNG. [Plotted CSVs, notes and provenance](figures/data/) accompany the figures. Regenerate them from the repository root:

```sh
python -m pip install -r requirements-analysis.txt
python scripts/build_slide_figures.py
```

The builder verifies the public input hashes and pinned Natural Earth geometry. It uses no database, article text or model calls. The existing [notebook](../notebooks/01_dashboard_and_measures.ipynb) provides additional calculations and explanations.

## Senegal case evidence

Slides 15–16 connect the monthly series to actors, primary actions and selected article records. February has 132 positive-alignment and 182 negative-alignment articles; 83 of the positive-alignment records also have negative reputation. From February to March, protest/march actions fall from 51 to 4 and voting/election actions rise from 14 to 201. These are coded article counts, not independent events or a causal decomposition of P.

[Aggregate evidence](figures/data/09_senegal_contributors.json) contains all 24 monthly denominators, actor/action distributions, joint labels and within-source comparisons. [Nine article examples](figures/data/09_senegal_article_examples.json) contain source links, saved model codes, short evidence spans and input lengths. Each example's saved-attempt membership, source plan and input were verified against the frozen extraction evidence. Examples were deliberately selected and are not an accuracy sample. Several translated inputs are short excerpts. In the police example, the negative reputation span concerns the election postponement, so the slide reports only the police–protester link and alignment.

Reproduce the aggregates with [build_senegal_case.py](../scripts/build_senegal_case.py), supplying the three disjoint private extraction caches using repeated `--cache` arguments, plus `--snapshot slides/analysis_snapshot.json`, `--slide-csv slides/figures/data/09_senegal_monthly_indices.csv` and `--output slides/figures/data/09_senegal_contributors.json`. Each cache needs its neighboring `EXTRACTION_VERIFIED.json`; the frozen public scope JSON must be cached or supplied with `--scope`. The script verifies cache hashes, full sample counts and the 27-cell joint distribution, then reconciles every displayed month. It reads existing files and makes no database, network or model calls. Private caches and article texts are not published.

## Kenya source comparison

Slides 17–19 compare Nation, KBC and Citizen Digital articles evaluating Kenya's incumbent government. The chart shows January–August 2024 around the Finance Bill protests. [All 36 source-month cells for January–December](figures/data/13_kenya_source_monthly.csv) remain available; December KBC has only three records. The source gap predates June, and all three outlets' negative-framing shares rise in June. Zero labels remain in each denominator.

[Aggregate evidence](figures/data/13_kenya_source_comparison.json) includes all three signs, June actor/action distributions and the March–May baseline. [The paired reports](figures/data/13_source_article_pairs.json) cover the same Blinken–Ruto call in original English, but the stored model records select different actions. This supports a close comparison of narration, quotation and action selection; it does not isolate an outlet effect. A secondary Nicaragua pair is documented with its smaller sample and shorter translated inputs.

Use [build_kenya_source_comparison.py](../scripts/build_kenya_source_comparison.py) with the three private caches and frozen slide snapshot to reproduce the aggregate export. [build_source_comparison_figure.py](../scripts/build_source_comparison_figure.py) renders PNG/PDF/SVG and the CSV from that public export. Both use existing data without database or model calls. The [figure manifest](figures/data/13_kenya_figure_manifest.json) records hashes and the selected display window.

Slide 18 distinguishes the outlets' institutional settings in 2024. NMG was a listed private-sector group with AKFED as majority shareholder; KBC was the state public broadcaster; Citizen was part of commercial Royal Media Services. NMG's stated support for accountability and interpretive journalism is policy context, not evidence that ownership caused its measured framing. Citizen's June negative-framing share (8.5%) is close to KBC's (7.2%), compared with Nation's 33.5%, so a state/private split does not account for the pattern. Period-specific sources and qualifications are linked in the slide notes. Later ownership changes are not projected back onto 2024.

## Measurement and foreign-government comparisons

Slide 12 replaces the earlier N/P-only illustration with directional share `S`, conditional balance `B`, and their combination `P = S²B`. B is undefined when no directional articles exist. The four synthetic examples distinguish prevalence from balance. [Measure definitions](../docs/coverage-balance.md) retain N and explain comparisons within and between sources. These describe coded coverage, with societal polarization still to validate.

Slide 20 holds the outlet fixed on The Kyiv Independent and compares Russia with Ukraine. Directional framing appears in 470/1,242 Russia-evaluating records (37.8%) and 605/9,568 Ukraine-evaluating records (6.3%). Russia's framing is almost all negative, so its P is lower despite its much larger directional share. These pooled data do not hold event, time or political conduct constant. They illustrate the value of recording foreign evaluated governments, without establishing double standards. The existing five-row source-government CSV remains available.

## Performance figures

The upstream civic-event classifier’s **82%** average out-of-sample accuracy and civic relevance classifier’s **87%** overall accuracy are reported in [Moratz et al. (2025), Tracking Civic Space](https://zungru.com/assets/papers/civic-space-transformers.pdf), pp. 11–13. These are separate from GenAI evaluation.

The GenAI slide reports **79.1% same-event agreement (167/211)** when both model and human identify an action, and **67.9% (178/262)** including shared no-action decisions and action/no-action disagreements. Astra’s action-coding preferences among those 262 valid outputs are Luna 121, human 44, both defensible 83, unresolved/neither 14. The near-even 17-versus-16 preference occurs only in 44 different-event cases. These come from a selected historical sample and dependent AI review. They are not accuracy estimates for the three current political judgments. See [validation](../docs/validation.md).

## Analytical scope

The current analytical figures retain the fixed full eligible sample, including domestic, cross-border and international reporting. A domestic-only analysis additionally requires publication country to equal the evaluated government. “National incumbent” identifies the government reference, not a domestic-only sampling rule. The two maps distinguish where sources publish from which governments their articles evaluate; the pooled correlation describes article labels in that broader sample. Foreign evaluations support comparisons of multiple outlets covering the same government. Those comparisons need common periods and events.

## Updating coverage and counts

The figures use `explore-since2019.json`, pinned in [analysis_snapshot.json](analysis_snapshot.json). The independent storage cutoff is **November 8, 2026, 13:57:13 UTC**. The [figure manifest](figures/data/slide_figure_manifest.json) records the input hashes and calculated results. [Annual counts](figures/data/06_coverage_by_year.csv) describe the uneven observed coverage. The Senegal case remains a 2023–2024 subwindow. [Source–government counts and framing scores](figures/data/12_source_government_framing.csv) reproduce the editable comparison on slide 20, with additional source rows retained in the CSV.

The repository-wide `data/analysis_snapshot.json`, notebook and earlier exports retain their November 4 release. Slide inputs use a separate hash-addressed cache. The previous deck and figure files remain available at Git revision `118684b0ccd37bbcf4b9ff9c73004f2ca4fe5f48`; their dates have not been relabeled.

When more data are ready, select a verified new release and update the manifest through the repository's normal data-release process. Then regenerate all four figures, plotted CSVs and this deck together. Change the counts and derived findings in the QMD and README as part of the same update. Leave historical snapshots and evidence intact. A larger production counter alone is insufficient for an analytical refresh.

## Interpretation and remaining work

- **Political alignment** describes the actor's directional relationship to the evaluated government as expressed through the selected action. It can be evidenced directly or through conduct toward explicitly identified government opponents. It does not establish a reciprocal or permanent relationship, moral approval or private views.
- **Reputational implication** describes a coded implication for government performance/legitimacy, rather than a measured change in public opinion.
- **Framing** describes observable narrator evaluation. Outlet bias requires evidence about coverage selection and comparable events.
- **Monthly P = 4p⁺p⁻** is a proposed two-sided coverage index, calculated separately for the three fields. Its relationship to societal polarization and to formal polarization indices remains to be justified.
- The country in the export is the **government evaluated**, which can differ from a source's publication country. Small country-month counts remain unsuitable for strong national claims.
- Action-based coding can miss adverse conditions without a substantive action. Representative human validation of the three current labels remains incomplete.

The latest shared citation and bibliography updates are included. Literature slides retain citation reminders for the speakers developing those sections. The research agenda contains proposed comparisons, not estimated effects.

Method details: [codebook](../docs/codebook.md), [data card](../docs/data-card.md), [validation](../docs/validation.md), [measure definition](../docs/coverage-balance.md), and [dashboard guide](../docs/dashboard-guide.md).
