# Media Bias in Civic News

This project studies how news outlets cover national governments. It uses language models to identify reported actions and distinguish their political alignment, reputational implications, and treatment in the article's own wording.

The research examines how these measures vary across outlets and political settings, and how they relate to media ownership, regulation, and government accountability.

## Measures

Each record refers to one selected action and one national incumbent government at the article's publication date.

| Measure | Field | Definition |
|---|---|---|
| Action alignment | `align` | Whether the action supports or opposes the incumbent government |
| Reputational implication | `rep` | What the action and directly related facts imply about government performance or legitimacy |
| Article framing | `frame` | Whether the title or narrator adds explicit favorable or critical evaluation of the government |

The measures use `-1`, `0`, `+1`, and `null`. Zero includes neutral, mixed, and insufficient directional evidence. Null means the dimension cannot be coded. A negative reputational implication does not necessarily indicate critical framing, and neither measure directly estimates changes in public opinion.

The [codebook](docs/codebook.md) describes action selection, government identification, evidence requirements, and the full output structure.

## Project materials

| Location | Contents |
|---|---|
| [Project status](docs/status.md) | Available work and remaining tasks |
| [Dashboard guide](docs/dashboard-guide.md) | Time controls, point size, denominators, clustering and interpretation |
| [Monthly polarization CSV](data/polarization/) | All available government country-months, three separate scores, shares and article counts |
| [Analysis notebook](notebooks/01_dashboard_and_measures.ipynb) | Executed examples, figures and reproducible calculations |
| [Research design](docs/research-design.md) | Research questions, comparisons, and political interpretation |
| [Media freedom and domestic coverage](docs/media-freedom-comparison.md) | Country-month comparisons with publication country matched to the evaluated government |
| [Codebook](docs/codebook.md) | Coding definitions and field descriptions |
| [Data documentation](docs/data-card.md) | Corpus scope, inclusion rules, coverage, and limitations |
| [Validation](docs/validation.md) | Completed checks and planned human evaluation |
| [Data](data/) | Monthly aggregates and summary tables |
| [Prompts](prompts/) | Current coding prompt and version metadata |
| [Scripts](scripts/) | Reproduction of the aggregate tables |
| [References](references/references.bib) | Research bibliography |

## Available data

The [analysis dashboard](https://zungru-media-bias-reported-polarization.static.hf.space/index.html) uses a fixed **January 2022–May 2026** cohort: **2,157,912 structurally valid records**, of which **1,984,402** have an identified government and primary action and all three labels codable. The storage audit is November 4, 2026. An optional 2021-start view includes 2,440,312 eligible records. All comparisons use one complete prompt.

The [snapshot manifest](data/analysis_snapshot.json) pins the public aggregate downloads by commit and SHA-256. The [notebook](notebooks/01_dashboard_and_measures.ipynb) reproduces distributions, joint-label correlations, a country cloud, monthly changes and the proposed [two-sided coverage index](docs/coverage-balance.md). Figures and calculated tables are included. See [notebook instructions](notebooks/README.md) to rerun it.

The original October 29 snapshot of 542,981 valid January 2025–May 2026 records remains in `data/` for historical reproduction. Its marginal tables retain null in their denominators; the newer comparison sample excludes uncodable cases. These are different denominators.

The broader processing target is January 2012–June 2026. [Corpus processing](https://huggingface.co/spaces/zungru/civic-actor-action-sentiment) is tracked separately and can advance without changing the frozen analysis. The [data card](docs/data-card.md) records scope, prompt versions and limitations. Article text and record-level outputs are not included.

## Reproduce the summaries

Use Python 3.9 or later. The script uses only the standard library.

```sh
python3 scripts/reproduce_summary.py
```

To check the existing summaries without changing them:

```sh
python3 scripts/reproduce_summary.py --check
```

Add `--verify-upstream` to compare the snapshot with its archived public source files. This option requires internet access. The script does not run model inference or connect to the project database.

## Current work

Corpus processing, human validation, and entity standardization are in progress. The available results describe model-coded articles. Source composition, translation quality, and coding error still need to be evaluated before interpreting differences as outlet bias or political effects.

Joint label tables, monthly government/outlet comparisons and selected same-outlet checks are available. Matched-event comparisons, stable source panels and independent semantic validation remain needed. Ownership and regulatory data would support research on media institutions; audience data would be needed to study effects on political attitudes. See [project status](docs/status.md) for the current priorities.

Data snapshots and prompt versions are documented separately. Analyses should identify the snapshot and Git commit used, and keep older prompt versions distinct.
