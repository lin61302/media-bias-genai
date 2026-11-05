# Shared slides

[MediaBias_Polarization.qmd](MediaBias_Polarization.qmd) is the shared Quarto source. [MediaBias_Polarization.html](MediaBias_Polarization.html) is the rendered Reveal.js deck. Edit the QMD, then render the HTML before committing. The HTML embeds its resources for local viewing.

```sh
cd slides
quarto render MediaBias_Polarization.qmd
```

Open the HTML in a browser. Click a slide, then use **F** for fullscreen, arrow keys or Space to move, **M** for the menu, and **S** for speaker view. Share the slide window with the audience and keep speaker notes on your own display. If speaker view is blocked for a local file, serve this folder with `python3 -m http.server 8883 --bind 127.0.0.1` and open `http://127.0.0.1:8883/MediaBias_Polarization.html`.

## Structure and timing

The deck has 26 slides including the title and references. It keeps the existing design and literature sections. Detailed explanations and qualifications are in the speaker notes.

| Slides | Content | Suggested time |
|---|---|---:|
| 1–5 | Question, literature and analytical challenges | 12–15 minutes |
| 6–9 | Sentiment target, action/government reference, three-label example | 7–9 minutes |
| 10–15 | Approach, corpus, coverage map, pipeline, coding and analytical views | 8–10 minutes |
| 16–20 | Monthly measure, distributions, joint labels and Senegal example | 7–9 minutes |
| 21–25 | Validation, research design, limitations and next comparisons | 8–10 minutes |
| 26 | References | Reference slide |

Slides 6–20 make a roughly 25-minute concepts-and-data section. The full sequence leaves time for discussion within an hour. These are pacing suggestions, not assigned speaking roles.

## Examples and figures

The police example is synthetic and comes from calibration examples 1–2 in the [complete prompt](../prompts/civic_20261020_complete_v1.txt). It explicitly supplies cabinet affiliation and peaceful anti-government demonstrators. It demonstrates alignment +1, reputation −1 and framing 0; adding narrator endorsement changes framing to +1. It is not a sampled event or model-accuracy result.

The classifier slide restores Erik's overview layout with six numbered boxes, a coded-record example and illustrative monthly distributions. Translation and the two civic encoder classifiers have distinct stages. The editable diagram is in [includes/classifier.qmd](includes/classifier.qmd), styled by [classifier.css](classifier.css). `pipeline_schematic.png` retains Erik's original static figure for reference.

The actor/action/target diagram, framing comparison and larger monthly distribution bars are editable HTML inside the main QMD. [concepts.css](concepts.css) styles only those slides. Positive, zero and negative labels use the same green, gray and orange palette in the examples and label-distribution figure. Keep the `includes` folder and both CSS files with the QMD when editing or sharing the source; the rendered HTML embeds everything needed for viewing.

The four current empirical figures use one fixed [November 4 release](../data/analysis_snapshot.json): January 2022–May 2026, **1,984,402 eligible articles** among 2,157,912 valid complete-prompt records. They do not mix in later processing totals.

| Figure | What it shows |
|---|---|
| [06_coverage_map.png](figures/06_coverage_map.png) | 71 publication countries and 203 evaluated-government codes. The maps have different quantities and scales. International/mixed source domains are separate. |
| [07_label_distributions.png](figures/07_label_distributions.png) | Three marginal distributions on the same eligible denominator. Zero combines neutral, mixed and insufficient directional evidence. |
| [08_alignment_reputation_joint.png](figures/08_alignment_reputation_joint.png) | Reputation conditional on alignment. Among pro-incumbent actions, 19.5% have negative reputational implications. |
| [09_senegal_monthly_indices.png](figures/09_senegal_monthly_indices.png) | Monthly two-sided index for each field, article volume and a sourced episode. Lines omit months below 100 articles; this is a display rule, not a reliability guarantee. |

PDF and SVG versions are alongside each PNG. [Plotted CSVs, notes and provenance](figures/data/) accompany the figures. Regenerate them from the repository root:

```sh
python -m pip install -r requirements-analysis.txt
python scripts/build_slide_figures.py
```

The builder verifies the public input hashes and pinned Natural Earth geometry. It uses no database, article text or model calls. The existing [notebook](../notebooks/01_dashboard_and_measures.ipynb) provides additional calculations and explanations.

## Interpretation and remaining work

- **Alignment** describes the political direction of the selected action, rather than moral approval or the actor's private views.
- **Reputation** describes a coded implication for government performance/legitimacy, rather than a measured change in public opinion.
- **Framing** describes observable narrator evaluation. Outlet bias requires evidence about coverage selection and comparable events.
- **Monthly P = 4p⁺p⁻** is a proposed two-sided coverage index, calculated separately for the three fields. Its relationship to societal polarization and to formal polarization indices remains to be justified.
- The country in the export is the **government evaluated**, which can differ from a source's publication country. Small country-month counts remain unsuitable for strong national claims.
- Action-based coding can miss adverse conditions without a substantive action. Representative human validation of the three current labels remains incomplete.

Literature and citation completion remain with the speakers developing those sections. Existing unresolved bibliography keys are `martin_yurukoglu_2017`, `mccoy_etal_2018`, `prior_2013` and `wagner_2021`; the literature slides also retain their original citation reminders. The lead/lag slide is a research proposal, not an estimated result.

Method details: [codebook](../docs/codebook.md), [data card](../docs/data-card.md), [validation](../docs/validation.md), [measure definition](../docs/coverage-balance.md), and [dashboard guide](../docs/dashboard-guide.md).
