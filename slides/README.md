# Shared slides

[MediaBias_Polarization.qmd](MediaBias_Polarization.qmd) is the shared Quarto source. [MediaBias_Polarization.html](MediaBias_Polarization.html) is the rendered Reveal.js deck. Edit the QMD, then render the HTML before committing. The HTML embeds its resources for local viewing.

```sh
cd slides
quarto render MediaBias_Polarization.qmd
```

Open the HTML in a browser. Click a slide, then use **F** for fullscreen, arrow keys or Space to move, **M** for the menu, and **S** for speaker view. Share the slide window with the audience and keep speaker notes on your own display. If speaker view is blocked for a local file, serve this folder with `python3 -m http.server 8883 --bind 127.0.0.1` and open `http://127.0.0.1:8883/MediaBias_Polarization.html`.

## Structure and timing

The deck has **18 slides**, including the title and references. Definitions appear once, one controlled example demonstrates them, and the classifier slide explains the process. The monthly formula and synthetic distributions share a single slide.

| Slides | Content | Suggested time |
|---|---|---:|
| 1–5 | Question, US and comparative literature, incumbent reference | 12–15 minutes |
| 6–7 | Three meanings of sentiment and one controlled example | 7 minutes |
| 8–10 | Sample, geographic coverage and coding pipeline | 7–8 minutes |
| 11–14 | Monthly measures and preliminary empirical comparisons | 9 minutes |
| 15 | Validation and limits | 2 minutes |
| 16 | Research agenda and links back to polarization theory | 5–7 minutes |
| 17 | Discussion | 10–12 minutes |
| 18 | References | Reference slide |

Slides **6–15** make a roughly **25-minute** section for Zung-Ru. These are suggested speaking roles and pacing, for agreement with the team. The [speaker guide](speaker_guide.md) contains a proposal to send the others, slide-by-slide talking points, transitions and wording cautions. Detailed notes are also embedded in the deck.

## Examples and figures

The police example is synthetic and comes from calibration examples 1–2 in the [complete prompt](../prompts/civic_20261020_complete_v1.txt). It explicitly supplies cabinet affiliation and peaceful anti-government demonstrators. It demonstrates alignment +1, reputation −1 and framing 0; adding narrator endorsement changes framing to +1. It is not a sampled event or model-accuracy result.

The classifier keeps Erik's six-box overview style. Translation and the two civic encoder classifiers have distinct stages. Its lower half explains prompt controls and sample rules rather than repeating the example or monthly formulas. Edit [includes/classifier.qmd](includes/classifier.qmd) and [classifier.css](classifier.css). `pipeline_schematic.png` retains the earlier static figure for reference.

The controlled example, sample counts and monthly distribution bars are editable HTML inside the main QMD. [concepts.css](concepts.css) styles those slides. Keep the `includes` folder and both CSS files with the QMD when sharing the source. The rendered HTML embeds its viewing resources.

The four current empirical figures use one fixed [November 4 release](../data/analysis_snapshot.json): January 2021–May 2026, **2,440,312 eligible articles** among 2,654,346 valid complete-prompt records. They do not mix in later processing totals.

| Figure | What it shows |
|---|---|
| [06_coverage_map.png](figures/06_coverage_map.png) | 71 publication countries and 205 evaluated-government codes. The maps have different quantities and scales. International/mixed source domains are separate. |
| [07_label_distributions.png](figures/07_label_distributions.png) | Three marginal distributions on the same eligible denominator. Zero combines neutral, mixed and insufficient directional evidence. |
| [08_alignment_reputation_joint.png](figures/08_alignment_reputation_joint.png) | Reputation conditional on alignment. Among pro-incumbent actions, 20.1% have negative reputational implications. |
| [09_senegal_monthly_indices.png](figures/09_senegal_monthly_indices.png) | Monthly two-sided index for each field, article volume and a sourced episode. Lines omit months below 100 articles; this is a display rule, not a reliability guarantee. |

PDF and SVG versions are alongside each PNG. [Plotted CSVs, notes and provenance](figures/data/) accompany the figures. Regenerate them from the repository root:

```sh
python -m pip install -r requirements-analysis.txt
python scripts/build_slide_figures.py
```

The builder verifies the public input hashes and pinned Natural Earth geometry. It uses no database, article text or model calls. The existing [notebook](../notebooks/01_dashboard_and_measures.ipynb) provides additional calculations and explanations.

## Updating coverage and counts

The current figures use the existing `explore-since2021.json` release, pinned in `data/analysis_snapshot.json` under `optional_since_2021`. Its audit cutoff is **November 4, 2026, 13:38:01 UTC**. The [figure manifest](figures/data/slide_figure_manifest.json) records the exact scope file and hash. January 2021 is included in released data, not only a future target.

When more data are ready, select a verified new release and update the manifest through the repository's normal data-release process. Then regenerate all four figures, plotted CSVs and this deck together. Change the counts and derived findings in the QMD, speaker guide and README as part of the same update. Leave historical snapshots and evidence intact. A larger production counter alone is insufficient for an analytical refresh.

## Interpretation and remaining work

- **Alignment** describes the political direction of the selected action, rather than moral approval or the actor's private views.
- **Reputation** describes a coded implication for government performance/legitimacy, rather than a measured change in public opinion.
- **Framing** describes observable narrator evaluation. Outlet bias requires evidence about coverage selection and comparable events.
- **Monthly P = 4p⁺p⁻** is a proposed two-sided coverage index, calculated separately for the three fields. Its relationship to societal polarization and to formal polarization indices remains to be justified.
- The country in the export is the **government evaluated**, which can differ from a source's publication country. Small country-month counts remain unsuitable for strong national claims.
- Action-based coding can miss adverse conditions without a substantive action. Representative human validation of the three current labels remains incomplete.

Literature and citation completion remain with the speakers developing those sections. Existing unresolved bibliography keys are `martin_yurukoglu_2017`, `mccoy_etal_2018`, `prior_2013` and `wagner_2021`; the literature slides also retain their original citation reminders. The research agenda contains proposed comparisons, not estimated effects.

Method details: [codebook](../docs/codebook.md), [data card](../docs/data-card.md), [validation](../docs/validation.md), [measure definition](../docs/coverage-balance.md), and [dashboard guide](../docs/dashboard-guide.md).
