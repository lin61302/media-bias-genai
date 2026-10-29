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
| [Research design](docs/research-design.md) | Research questions, comparisons, and political interpretation |
| [Codebook](docs/codebook.md) | Coding definitions and field descriptions |
| [Data documentation](docs/data-card.md) | Corpus scope, inclusion rules, coverage, and limitations |
| [Validation](docs/validation.md) | Completed checks and planned human evaluation |
| [Data](data/) | Monthly aggregates and summary tables |
| [Prompts](prompts/) | Current coding prompt and version metadata |
| [Scripts](scripts/) | Reproduction of the aggregate tables |
| [References](references/references.bib) | Research bibliography |

## Available data

The current aggregate snapshot covers **542,981 structurally valid records from January 2025 through May 2026**, using the same complete prompt. It was verified on **October 29, 2026**. It is a processed subset of the broader project corpus, whose current target period is January 2012 through June 2026.

The [data documentation](docs/data-card.md) records the sampling boundaries, prompt versions, missing values, and processing coverage. The repository contains aggregate data; article text and record-level outputs are not included.

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

The next analyses require joint label tables and comparable outlet, government, and time groups. Ownership and regulatory data would support research on media institutions; audience data would be needed to study effects on political attitudes. See [project status](docs/status.md) for the current priorities.

Data snapshots and prompt versions are documented separately. Analyses should identify the snapshot and Git commit used, and keep older prompt versions distinct.
