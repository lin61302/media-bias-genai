# Shared slides

[MediaBias_Polarization.qmd](MediaBias_Polarization.qmd) is the shared Quarto source. [MediaBias_Polarization.html](MediaBias_Polarization.html) is the rendered Reveal.js deck. Edit the QMD, then render the HTML before committing. The HTML embeds its resources for local viewing.

```sh
cd slides
quarto render MediaBias_Polarization.qmd
```

Open the HTML in a browser. Click a slide, then use **F** for fullscreen, arrow keys or Space to move, **M** for the menu, and **S** for speaker view. Share the slide window with the audience and keep speaker notes on your own display. If speaker view is blocked for a local file, serve this folder with `python3 -m http.server 8883 --bind 127.0.0.1` and open `http://127.0.0.1:8883/MediaBias_Polarization.html`.

## Current deck

The current source renders **20 slides**. Slides 6–7 move from audience questions directly to three judgments about the same government. The classifier and processing have their own page, followed by a separate monthly-score illustration, prompting fields/rules, and the historical GenAI comparison.

| Slides | Content |
|---|---|
| 1–5 | Question, literature and common political reference |
| 6–7 | Audience questions and three concepts |
| 8 | Full-page classifier and processing; civic-event and relevance performance |
| 9 | Illustrative monthly distributions, net score and proposed P |
| 10 | Prompting fields and decision rules |
| 11 | GenAI event-selection agreement with earlier human coding |
| 12 | Coverage and analytical sample |
| 13–16 | Label distributions, joint labels, source–government framing and monthly context |
| 17–19 | Validation, research agenda and discussion |
| 20 | References |

The shared files contain the presentation, method qualifications and source notes. Personal speaking manuscripts are maintained separately outside this repository.

## Examples and figures

The rescue/title contrast in the opening questions comes from calibration example 6: cabinet-affiliated services rescue 20 miners, while the title calls the rescue a “cynical publicity stunt.” It can be discussed orally as a second example: political alignment 0, reputational implication +1 and framing −1.

The police example on slide 7 is synthetic and comes from calibration examples 1–2 in the [complete prompt](../prompts/civic_20261020_complete_v1.txt). It explicitly supplies cabinet affiliation and peaceful anti-government demonstrators. It demonstrates alignment +1, reputation −1 and framing 0; the narrator’s “Police rightly restored order by dispersing the rioters” changes framing to +1. “Rioters” alone is not a sufficient cue. The negative reputational implication uses the prompt's explicit rights and lawful-conduct norms, not a democracy index or observed public-opinion change. It is not a sampled event or model-accuracy result.

The evaluated government is selected once for all three fields. Publication country is the default for domestic government-relevant affairs; the foreign-government exception requires a foreign focus and no codable judgment about the publication country's incumbent. The article date identifies who is incumbent, not which country must be evaluated. The complete rule, including `ALL` and multiple governments, is in prompt section 1.

Framing uses only the supplied title and narration. Prompt sections Input and 5 prohibit external event knowledge, other articles and inferred omissions. The comparison holds reported facts constant and asks what evaluation the narrator adds; it does not use an external neutral-news baseline. Explicit minimization of acknowledged wrongdoing can count. Differences in coverage, omitted details or emphasis across accounts require a separate comparative analysis; the most common account is not automatically neutral or correct. Words such as “rioters” or an attributed claim about public safety are not automatic framing labels.

The classifier keeps Erik's six-box overview style. Translation and the two civic encoder classifiers have distinct stages. Its lower half contains the record, three judgment questions and illustrative monthly distributions. Definitions stay in this integrated figure. Edit [includes/classifier.qmd](includes/classifier.qmd) and [classifier.css](classifier.css). `pipeline_schematic.png` retains the earlier static figure for reference.

The classifier and separate monthly illustration are editable HTML in the included QMD files. Sample counts and the framing comparison table remain editable in the main QMD. [concepts.css](concepts.css) styles those slides. Keep the `includes` folder and both CSS files with the QMD when sharing the source. The rendered HTML embeds its viewing resources.

The four current empirical figures use the fixed [November 8 release](analysis_snapshot.json): January 2019–May 2026, **3,181,113 eligible articles** among 3,464,596 valid, independently stored complete-prompt records. This adds 810,250 valid and 740,801 eligible records to the previous slide snapshot. Earlier-year coverage is uneven. Processing admissions and separately tracked reruns are outside this analytical denominator.

| Figure | What it shows |
|---|---|
| [06_coverage_map.png](figures/06_coverage_map.png) | 71 publication countries and 211 evaluated-government codes. The maps have different quantities and scales. International/mixed source domains are separate. |
| [07_label_distributions.png](figures/07_label_distributions.png) | Three marginal distributions on the same eligible denominator. Zero combines neutral, mixed and insufficient directional evidence. |
| [08_alignment_reputation_joint.png](figures/08_alignment_reputation_joint.png) | Reputation conditional on alignment. Among pro-incumbent actions, 20.8% have negative reputational implications. |
| [09_senegal_monthly_indices.png](figures/09_senegal_monthly_indices.png) | Monthly two-sided index for each field, article volume and a sourced episode. Lines omit months below 100 articles; this is a display rule, not a reliability guarantee. |

PDF and SVG versions are alongside each PNG. [Plotted CSVs, notes and provenance](figures/data/) accompany the figures. Regenerate them from the repository root:

```sh
python -m pip install -r requirements-analysis.txt
python scripts/build_slide_figures.py
```

The builder verifies the public input hashes and pinned Natural Earth geometry. It uses no database, article text or model calls. The existing [notebook](../notebooks/01_dashboard_and_measures.ipynb) provides additional calculations and explanations.

## Performance figures

The upstream civic-event classifier’s **82%** average out-of-sample accuracy and civic relevance classifier’s **87%** overall accuracy are reported in [Moratz et al. (2025), Tracking Civic Space](https://zungru.com/assets/papers/civic-space-transformers.pdf), pp. 11–13. These are separate from GenAI evaluation.

The GenAI slide reports **79.1% same-event agreement (167/211)** when both model and human identify an action, and **67.9% (178/262)** including shared no-action decisions and action/no-action disagreements. These come from a selected historical sample and AI-assisted event matching. They are not accuracy estimates for the three current political judgments. See [validation](../docs/validation.md).

## Analytical scope

The current analytical figures retain the fixed full eligible sample, including domestic, cross-border and international reporting. A domestic-only analysis additionally requires publication country to equal the evaluated government. “National incumbent” identifies the government reference, not a domestic-only sampling rule. The two maps distinguish where sources publish from which governments their articles evaluate; the pooled correlation describes article labels in that broader sample. Foreign evaluations support comparisons of multiple outlets covering the same government. Those comparisons need common periods and events.

## Updating coverage and counts

The figures use `explore-since2019.json`, pinned in [analysis_snapshot.json](analysis_snapshot.json). The independent storage cutoff is **November 8, 2026, 13:57:13 UTC**. The [figure manifest](figures/data/slide_figure_manifest.json) records the input hashes and calculated results. [Annual counts](figures/data/06_coverage_by_year.csv) describe the uneven observed coverage. The Senegal case remains a 2023–2024 subwindow. [Source–government counts and framing scores](figures/data/12_source_government_framing.csv) reproduce the editable table on slide 15.

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
