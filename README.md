# Beyond Sentiment

## Actions, reputation, and political bias in civic news

Research materials for the **November 11, 2026 PDRI/DevLab presentation**. This project uses generative AI to distinguish an action's political direction, its implication for an incumbent government's reputation, and the article's own evaluative presentation. The aim is to study how news portrays governments without collapsing these different constructs into a single sentiment score.

**Status:** work in progress. The descriptive tables below use a frozen October 29 checkpoint. Structural checks and independent database readback establish processing integrity; representative human semantic validation remains unfinished. These results do not yet establish outlet bias, public opinion effects, or societal polarization.

### Start here

- [HTML presentation](https://lin61302.github.io/media-bias-genai/slides/) — the talk draft, with keyboard navigation and speaker notes. An [offline copy](slides/index.html) is included.
- [Research design and political implications](docs/research-design.md) — questions, competing explanations, and identification needs.
- [Codebook](docs/codebook.md) — the unit of analysis and the meaning of each output field.
- [Data card](docs/data-card.md) — coverage, denominators, provenance, and exclusions.
- [Validation plan](docs/validation.md) — what has been checked and what remains to establish scientific validity.
- [Presentation preparation](docs/presentation-plan.md) — proposed discussion sequence and next analyses.

### Why this distinction matters

A report of coercion against peaceful government opponents can describe an action that strengthens the incumbent's position while damaging its perceived legitimacy. The journalist can describe that event without endorsing it. Conversely, a narrator can praise the same conduct. Treating all three as “positive” or “negative sentiment” would obscure politically meaningful differences.

The current design therefore labels each article against **one national incumbent government at the publication date**:

| Construct | Field | Question |
|---|---|---|
| Action alignment | `align` | Does the selected action support or oppose the incumbent? |
| Reputational implication | `rep` | What do the action and directly tied facts imply about government performance or legitimacy? |
| Article orientation | `frame` | Does the title or narrator add an explicit government-favoring or government-critical presentation cue? |

All use `-1`, `0`, `+1`, or `null`. **Zero combines neutral, mixed, and insufficient directional evidence.** Null means the dimension is not codable under the rules. Reputation is an implication coded from the supplied report, not a measured change in anyone's attitudes. Article orientation is narrower than media bias: it does not by itself capture story selection, omitted sources, ownership influence, or ideology.

### A fixed descriptive cohort

The presentation uses **542,981 structurally valid, independently stored outcomes** from the **complete prompt** for **January 2025–May 2026**, a fixed 17-month window. Counts refer to selected articles, not unique real-world events or a representative sample of all news. June 2026 remains older-prompt data in this checkpoint and is excluded.

| Model-coded dimension | Negative | Zero: no clear direction / mixed | Positive | Not codable |
|---|---:|---:|---:|---:|
| Action alignment | 8.27% | 76.70% | 7.24% | 7.78% |
| Reputational implication | 9.68% | 78.56% | 3.97% | 7.78% |
| Article orientation | 4.96% | 86.70% | 3.01% | 5.33% |

Denominator for every row: all 542,981 valid outcomes, including null labels. Percentages are rounded independently. Exact counts and unrounded percentages are in [label_summary.csv](data/label_summary.csv). This cohort contains 370 source domains and 71 publication-country codes plus the international/regional `ALL` category; those are coverage descriptors, not equal country weights. See the [data card](docs/data-card.md) for how they differ from the target-government variable.

The observed negative reputational share exceeds the positive share. That is a **descriptive feature of model-coded coverage**. It could reflect events, selection, source composition, translation, or coding error. Separate marginal distributions do not reveal how labels combine within articles, so they cannot demonstrate reputationally harmful actions receiving favorable framing.

### Reproduce the tables

Python 3.10+ is sufficient for the aggregate calculations. No API key, database access, or paid model call is required.

```sh
python3 scripts/reproduce_summary.py
```

The script checks the frozen monthly counts and regenerates the CSV/JSON summaries. To regenerate the presentation figures and HTML after editing their source:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-figures.txt
.venv/bin/python scripts/build_presentation.py
```

Open `slides/index.html` in a browser. Use the arrow keys, Home/End, or the visible controls. Press **N** for speaker notes and **A** to show all slides. Browser printing produces one slide per page.

This is a reproduction package for the released aggregates and presentation. It is not a full corpus release or a runnable production extraction pipeline. The complete frozen prompt is included for methodological inspection.

### Repository structure

```text
README.md
docs/                  Research design, codebook, data card, validation, talk plan
data/                  Frozen monthly aggregates and regenerated summaries
prompts/               Exact complete prompt and public version metadata
references/            Primary-source bibliography
scripts/               Offline summary and presentation builders
slides/                HTML presentation and generated figures
```

### What this release contains

This repository contains aggregate counts, methods, a prompt with synthetic calibration examples, and the presentation. It excludes article text, article identifiers, raw model responses, private conversations, credentials, internal paths, financial ledgers, and operational state. The illustrative cases in the slides are **synthetic calibration examples**, not empirical evidence about the named countries.

The next research steps are blinded human validation, a versioned entity crosswalk, article-level joint tables, and composition-sensitive source/country analyses. Ownership and regulation measures, comparable events, and audience data would be needed for stronger political claims. See [research design](docs/research-design.md).

### Provenance and citation

The independent storage checkpoint is **2026-10-29 05:20:31 UTC**. [Snapshot metadata](data/monthly_complete_snapshot.json) records source hashes and immutable source URLs. The complete prompt release is `civic-complete-prompt-release-20261020-v1`; it must remain distinct from earlier minimal-prompt outcomes.

For discussion, cite this repository as *Beyond Sentiment: Actions, Reputation, and Political Bias in Civic News*, research-in-progress materials, October 29, 2026 snapshot, and include the Git commit used. Authorship order and a formal release citation remain to be agreed by the research team. No blanket redistribution license for the underlying news corpus is implied.
