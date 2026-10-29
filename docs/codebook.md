# Codebook

## Unit and input

One article yields one prioritized government-relevant action and one common national incumbent government (`gov`) at publication time. The action selection hierarchy is substantive headline action, then lead action, then the earliest repeatedly developed action, then centrality to the government. This is an article-action record, not an exhaustive event inventory.

The production input uses the supplied `title_translated` and `maintext_translated` exactly, including English originals stored in those fields. There is no silent fallback to other text fields. The October 17 input policy excludes empty or wholly non-English API input while tolerating minor translation defects. It supersedes the earlier two-complete-sentence screening rule; do not describe that historical rule as a property of the current corpus. Passing the current gate does not establish translation fidelity or sufficient political context. The deterministic S1/S2 segment labels are evidence anchors, not reliable linguistic sentence counts. The synthetic prompt calibration examples are pedagogical illustrations, not sampled production observations.

Publication country is provenance. It is not necessarily the government being evaluated. `gov` permits recognized ISO-3 codes and the project code `XKX`; `ALL` is reserved for publication provenance. Government entities abroad are classified relative to `gov`. Courts, legislatures, local officials, and security institutions are not automatically national incumbent members. Direct affiliation must be supported by the supplied text or time-appropriate context.

## Output fields

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Exact input identifier; excluded from this public release |
| `act` | string/null | Shortest adequate contiguous action span from one supplied field |
| `tags` | array | One or two action tags, primary first; empty if no action |
| `react` | string/null | Tag for an explicitly motivating prior/ongoing action; not an aftermath measure |
| `actor`, `target` | string/null | Exact entity spans; an abstract policy is not an entity target |
| `ac`, `tc` | string/null | Institutional role categories A–W, separate from incumbent affiliation |
| `gov` | string/null | Country of the national incumbent evaluated |
| `align` | -1/0/1/null | Political direction of the selected action relative to `gov` |
| `rep` | -1/0/1/null | Substantive reputational implication for `gov` |
| `frame` | -1/0/1/null | Observable evaluative cue in the title/narrator's voice toward `gov` |
| `rep_ev`, `frame_ev` | string/null | Source label and exact 1–8-word evidence span for nonzero labels |
| `q` | array | Up to two structural flags: `multi_action`, `no_action`, `gov_unclear`, `claim` |

## Label interpretation

`align=+1` can describe restricting explicitly identified government opponents. It is not moral approval. Actor identity alone cannot establish alignment. Routine official business can have `align=0`.

`rep=-1` can follow a clearly attributed corruption allegation against cabinet members, with `claim` retained. That records the allegation's implication, not the alleged wrongdoing as established fact. The reasonable-observer standard embeds judgments about performance and legitimacy. Human review should evaluate whether those judgments travel across contexts and political viewpoints.

`frame` requires a narrator/title presentation cue beyond the underlying event. A quoted criticism or an attributed headline alone is insufficient. An unfavorable event can have `frame=0`. Subtle wording that may be a translation artifact normally warrants zero. This conservative rule can miss indirect bias.

**`0` means applicable but no supported direction, genuinely mixed, or insufficient directional evidence. It is not a pure neutrality class.** `null` means not codable. For example, missing government identity forces all three dimensions to null. No codable action forces alignment and reputation to null, while framing can still be coded if government identity and a textual cue are available. Nulls therefore differ across dimensions.

## Taxonomy and version

The [exact complete prompt](../prompts/civic_20261020_complete_v1.txt) contains all 44 action tags, 23 actor/target categories, selection rules, null rules, and seven explicitly synthetic calibration examples. `other_act` remains a heterogeneous residual category. Current published action-type aggregates, if consulted outside this package, count the primary tag only.

The model is `gpt-6-luna` in the pinned production configuration. The [version metadata](../prompts/version.json) records the verified settings and prompt hash. Earlier minimal-prompt results are a distinct cohort. Pooling versions or interpreting prompt changes as political change would invalidate the comparison.

Neither `q=[]` nor a valid JSON response is a confidence score. Exact spans help auditing, but a model can copy a correct span and assign the wrong political relationship.
