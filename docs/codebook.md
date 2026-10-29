# Codebook

## Unit and input

One article yields one prioritized government-relevant action and one national incumbent government (`gov`) evaluated at publication time. The action-selection hierarchy is substantive headline action, then lead action, then the earliest repeatedly developed action, then centrality to the government. Each record represents an article and its selected action, not an exhaustive event inventory.

The input uses `title_translated` and `maintext_translated` exactly, including English originals stored in those fields. Other text fields are not substituted. The **October 17, 2026 input policy** excludes empty or invalid bodies and wholly non-English input, while tolerating minor translation defects. It imposes no sentence or article-length minimum and no blanket exclusion by source language or country. This policy supersedes the earlier two-complete-sentence rule. Passing the input check does not establish translation fidelity or adequate political context.

Deterministic S1/S2 segment labels are evidence anchors rather than linguistic sentence counts. Synthetic examples in the prompt illustrate coding rules; they are not sampled observations.

Publication country records provenance and can differ from the government being evaluated. `gov` permits recognized ISO-3 codes and the project code `XKX`; `ALL` is reserved for publication provenance. Foreign government entities are classified relative to `gov`. Courts, legislatures, local officials, and security institutions are not automatically national incumbent members. Affiliation must be supported by supplied text or time-appropriate context.

## Output fields

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Exact input identifier; article identifiers are not published in this repository |
| `act` | string/null | Shortest adequate contiguous action span from one supplied field |
| `tags` | array | One or two action tags, primary first; empty if no action |
| `react` | string/null | Tag for an explicitly motivating prior or ongoing action |
| `actor`, `target` | string/null | Exact entity spans; an abstract policy is not an entity target |
| `ac`, `tc` | string/null | Institutional role categories A–W, separate from incumbent affiliation |
| `gov` | string/null | Country of the national incumbent evaluated |
| `align` | -1/0/1/null | Political direction of the selected action relative to `gov` |
| `rep` | -1/0/1/null | Substantive reputational implication for `gov` |
| `frame` | -1/0/1/null | Observable evaluative cue in the title or narrator's voice toward `gov` |
| `rep_ev`, `frame_ev` | string/null | Source label and exact 1–8-word evidence span for nonzero labels |
| `q` | array | Up to two structural flags: `multi_action`, `no_action`, `gov_unclear`, `claim` |

## Label interpretation

**Alignment (`align`).** A positive label can describe restricting explicitly identified government opponents; it does not imply moral approval. Actor identity alone does not establish alignment. Routine official business can receive `0`.

**Reputational implication (`rep`).** A negative label can follow a clearly attributed corruption allegation against cabinet members, with `claim` retained. The label records the allegation's implication, not wrongdoing as established fact. The reasonable-observer standard involves judgments about performance and legitimacy, whose consistency across contexts requires human evaluation.

**Evaluative framing (`frame`).** A directional label requires an observable cue in the title or narration beyond the underlying event. Quoted criticism or an attributed headline alone is insufficient. An unfavorable event can receive `0`. Subtle wording that may be a translation artifact normally receives `0`; this conservative rule can miss indirect bias.

**Zero and null.** `0` means the dimension is applicable but has no supported direction, mixed evidence, or insufficient directional evidence. It is not a pure neutrality class. `null` means not codable. Missing government identity forces all three dimensions to null. No codable action forces alignment and reputational implication to null, while framing can still be coded when government identity and a textual cue are available. Null counts can therefore differ across dimensions.

## Taxonomy and versions

The [complete prompt](../prompts/civic_20261020_complete_v1.txt) contains all 44 action tags, 23 actor/target categories, selection rules, null rules, and seven synthetic calibration examples. `other_act` is a residual category containing different action types. Published action-type aggregates use the primary tag only.

The recorded production configuration uses `gpt-6-luna`. [Version metadata](../prompts/version.json) records settings, input policy, and prompt hash. Earlier minimal-prompt results form a separate cohort; comparisons across versions require explicit analysis of the version change.

Neither `q=[]` nor a valid JSON response is a confidence score. An exact copied span can still receive an incorrect role or political label.
