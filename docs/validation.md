# Validation

The November 10 review compares human and GenAI coding through the **reported action selected from each article**. This makes the sequence explicit: establish which action was selected, then examine its extracted fields and political judgments. The results support an inspectable coding process and identify disagreements for further review. They do not establish representative human-reference accuracy for political alignment, reputational effect or framing.

Structural checks establish whether outputs conform to the schema and were stored correctly. They do not establish correct action selection, political interpretation or translation fidelity. Independent human validation of all three current judgments remains planned.

## GenAI validation (Astra-assisted)

All **266 historical validation articles** received a new action review. Two Astra reviewers divided the source-only work into disjoint sets of 133 articles; each article had one initial reference, not two independent initial codings. They read the supplied article and current prompt before seeing the original answers. The references were frozen, then the human and Luna choices were mapped as anonymized A/B candidates. A further names-hidden audit examined 56 cases, including a fixed sample of 20, uncertain references and flagged cases. Four action references changed. Initial decisions, revisions and hashes are preserved.

The final review is therefore model-assisted and partly adjudicated after seeing anonymized answers. It is not human ground truth. The [review protocol](event-review-protocol.md) specifies the selection hierarchy, action identity rules, audit process and treatment of uncertainty. [Aggregate results](../slides/figures/data/05_event_validation_20261110.json) and the [reducer](../scripts/build_event_validation.py) provide the exact counts and provenance; article texts and individual judgments remain private.

### Choosing the reported action

The common comparison contains **251 articles** with a unique reference choice and interpretable choices from both coders. All three pairs use exactly these articles:

| Comparison | Same action choice | Agreement |
|---|---:|---:|
| Human–Luna | 179 / 251 | 71.3% |
| Human–review reference | 184 / 251 | 73.3% |
| Luna–review reference | 221 / 251 | 88.0% |

An explicit no-action decision is a valid choice. An unreadable or ambiguous choice is not treated as no action. The remaining 15 articles comprise 12 with insufficient source text, one unresolved reference and two ambiguous action anchors. An interpretable but incorrect choice stays in the denominator. Neither coder's correctness nor the former Luna-specific acceptance flag determines inclusion.

The common population partitions as follows:

| Relationship among the three choices | Articles |
|---|---:|
| All three agree | 172 |
| Only the human agrees with the reference | 12 |
| Only Luna agrees with the reference | 49 |
| Human and Luna agree, but the reference differs | 7 |
| All three differ | 11 |

These counts reproduce the three pairs: human–Luna is 172 + 7; human–reference is 172 + 12; Luna–reference is 172 + 49. Shared choices that differ from the reference remain included.

For the broader observed human–Luna comparison, **184 of 264 interpretable pairs agree (69.7%)**: 173 select the same actual action and 11 both select no action. Among the 213 pairs where both choose an action, agreement is **173/213 (81.2%)**. The full comparison also retains 40 different-action pairs and 40 one-sided action/no-action decisions. Two action anchors cannot be assigned uniquely. Four structurally invalid full model records have readable action choices and enter these event-only comparisons; their full-record failures remain flagged.

### What the comparison can establish

Action identity concerns the selected occurrence, not exact wording. A shorter phrase or an actor-role extraction mistake may still identify the same occurrence. Distinct stages—an allegation versus alleged conduct, a proposal versus implementation—or actions by opposing participants remain different choices. This separation prevents a preference for a more complete extraction from being counted as a different event.

The human exercise and Luna run used different historical inputs and coding rules; seven source views changed. The sample spans January 2012–January 2025, with 193 of 266 articles from 2012–2013. It is not representative of the current 2019–2026 analytical corpus. The reference uses the current prompt, so the larger Luna–reference agreement does not establish superiority over human coders under equivalent conditions.

The earlier 187-case results mixed event identity with a Luna-specific selection check. They are preserved in the [historical review archive](validation-historical-2026-11-03.md), together with the earlier extraction preferences and political-label subsets. They are not constraints that the new review was designed to reproduce.

### Sensitivity to review decisions and inputs

| Construction | Common articles | Human–Luna | Human–reference | Luna–reference |
|---|---:|---:|---:|---:|
| Final reviewed comparison | 251 | 179 | 184 | 221 |
| Initial references and mappings, before audit | 251 | 180 | 186 | 220 |
| Exclude seven changed source views | 245 | 175 | 180 | 215 |
| Structurally valid full outputs only | 247 | 175 | 180 | 217 |
| Exclude both changed views and structural failures | 241 | 171 | 176 | 211 |

The first two rows happen to have the same size but differ in membership. Two previously insufficient references became identifiable, while two candidate anchors became unresolved. The audit also separated a closure from an evacuation order and revised a component action to the article's primary clash. These revisions were recorded before decoding coder identities.

For each of the two ambiguous anchors, two action stages fit the recorded phrase. Assigning all four combinations gives a common denominator of 253: human–Luna matches range from 179 to 181, human–reference from 184 to 186, and Luna–reference remains 223. Across all 266 pairs, human–Luna matches range from 184 to 186. These are sensitivity bounds, not adjudicated corrections. The primary comparison leaves the two anchors unresolved.

## Political judgments after selecting the same action

The new review identifies **173 articles where human and Luna selected the same actual action**. This cohort includes shared actions that differ from the review reference; it does not use the former 155-case acceptance gate.

The following counts apply the **saved, corrected November 3 political-label assessments** to that new cohort. They are not a new coding pass. The reviewer had seen Luna's labels and assessed them conditional on Luna's selected action and government. The original human sheet has one legacy sentiment field, not separate political alignment, reputational effect and framing labels.

| Judgment | Review agrees | Uncertain | Change proposed | Review agrees when Luna coded +1 or −1 |
|---|---:|---:|---:|---:|
| Political alignment | 135 / 173 (78.0%) | 28 | 10 | 27 / 41 (65.9%) |
| Reputational effect | 131 / 173 (75.7%) | 37 | 5 | 11 / 31 (35.5%) |
| Framing | 155 / 173 (89.6%) | 14 | 4 | 9 / 21 (42.9%) |

“Review agrees” means the saved assessment supports the producer label. “Uncertain” means ambiguous or boundary; “change proposed” is the saved unsupported verdict, not an independently established error. All three judgments are supported together in **108/173 (62.4%)**. Every article remains in each row's denominator, including unresolved assessments; all 173 have traceable assessments for all three labels.

Zeros are common: 132 political-alignment labels, 142 reputational-effect labels and 152 framing labels. The positive/negative-only columns show why high overall support does not establish reliable detection of directional content. These small selected subsets are diagnostic, not population accuracy estimates. Four invalid full outputs are included because their actions and political values are readable; other field errors remain flagged. The aggregate file also reports valid-output-only cohorts and the 166 actual actions where both coders match the review reference.

The saved review's numeric proposals often copy accepted Luna labels; ambiguous cases have no point proposal. Treating those proposals as independently assigned labels would exaggerate agreement. A valid human three-way comparison of the three political judgments requires new, separate human labels on the same action and government.

## Other fields after selecting the same action

Within the same 173 actions, each field is compared only where both recorded values are substantive and interpretable:

| Human–Luna field comparison | Matches / comparable values |
|---|---:|
| Main action category | 109 / 173 (63.0%) |
| Complete action-category set | 100 / 173 (57.8%) |
| Actor category | 108 / 157 (68.8%) |
| Literal actor wording | 48 / 154 (31.2%) |
| Actor wording after case/spacing normalization | 57 / 154 (37.0%) |
| Prior action triggering the selected action | 9 / 20 (45.0%) |
| One named evaluated government | 5 / 13 (38.5%) |

Wording equality is stricter than identifying the same entity. Actor-category comparison uses the recorded A–W code; action categories are compared as a first tag and as an exact set, without semantic recoding. Missing fields are not matches. The human government reference is missing in 157 cases, multiple or uninterpretable in three, matching in five and different in eight. The 13 comparable references are too few and too selective for a general government-selection accuracy claim.

No complete third set of actor, action-category, reaction and government fields was independently recorded. The historical review's preferences and proposed changes cannot supply that missing third coding.

## Reproduction and historical results

The [protocol](event-review-protocol.md#reproduction) documents the private input layout and aggregate-only output command. The reducer checks fixed membership, canonical action identities, the five-way partition, missingness, source versions and review provenance. Initial/final and ambiguous-anchor sensitivities are included in the public JSON. Private diagnostics contain case membership and reasons and must stay outside the repository.

The [November 2–3 archive](validation-historical-2026-11-03.md) retains the former 167/211, 178/262, 187-case and 155-case constructions. Its figures are historical and should not be combined with the new action comparison. The preliminary October reviews below concern different samples and remain separate.

## Preliminary reviews

Two reviews by an AI reviewer examined random samples of structurally valid, independently stored complete-prompt outputs. Each reviewer first coded the supplied input without seeing its stored labels.

| Review date | Sample size | Eligible pool | Exact agreement on all three labels |
|---|---:|---:|---:|
| October 21, 2026 | 30 | 35,412 | 24 |
| October 26, 2026 | 40 | 541,962 | 31 |

The later sample excluded the earlier 30 records. Both samples concern recent-period data and exclude failed or invalid requests. Agreement with one AI reviewer is not a human-reference accuracy estimate. The different sampling pools and review conditions do not support pooling the figures into a general performance estimate. Matching labels can coexist with incorrect actors, targets, or action spans.

The October 26 review identified five clear scope, extraction, or role errors. Across the reviews, observed problems included an event treated as an actor, a destination treated as an entity target, local conflict attributed to the national government without a supplied link, unrelated title/body content, and English text missing substantive original material. Other disagreements concerned interpretation. These small reviews diagnose error types; they do not estimate their population prevalence.

All 70 requests lacked incumbent-context metadata. Exact reconstruction of the supplied English confirmed what the model received, but did not establish fidelity to the original article. These limitations matter when the coding rules prohibit outside facts.

## Evaluation layers

| Layer | Question | Evidence |
|---|---|---|
| Source and translation | Does the supplied record preserve relevant meaning and context? | Bilingual comparison of original and supplied text; title/body/date checks |
| Extraction and reference | Are government, action, modality, entities, and roles correct? | Independent human annotations with exact spans and disagreement reasons |
| Political labels | Are alignment, reputational implication, and narrator evaluation applied consistently? | Human labels on the exact supplied input; class-level evaluation |
| Research inference | Do comparisons survive measurement error and sample composition? | Probability-based validation, subgroup diagnostics, sensitivity analysis |

Validation must match the intended inference ([Grimmer and Stewart, 2013](https://doi.org/10.1093/pan/mps028)). Published evidence of LLM annotation performance in other tasks does not establish performance for these constructs, countries, and translations ([Gilardi, Alizadeh and Kubli, 2023](https://doi.org/10.1073/pnas.2305016120)).

## Human annotation design

1. **Define the population.** Freeze an analysis cohort, its identities, and its cutoff. An initial study could use the January 2025–May 2026 cohort documented in the [data card](data-card.md).
2. **Use probability sampling.** Record inclusion probabilities and allocate review across languages, countries, sources, months, and model labels. Oversampling directional or null cases can improve their evaluation if estimates retain the sampling weights. Sample size should reflect desired precision and available bilingual expertise.
3. **Maintain a separate challenge set.** Include allegations, peaceful coercion, local/national attribution, foreign governments, quoted criticism, conditions versus actions, and partial translations. Its error rate does not estimate population accuracy.
4. **Use at least two trained human coders.** Provide the fixed codebook and exact supplied input, hide model labels during first-pass coding, and use a separate calibration set. Preserve initial judgments before adjudication by a third reviewer or documented consensus. Retain unresolved alternatives.
5. **Separate coding from missing information.** First assess what the supplied English supports. Then compare the original-language source and metadata in a separate pass. Missing context is a measurement limitation even when the model followed the input-only rule.
6. **Evaluate each stage.** Check government and date, action and modality, entities and roles, then labels. Report both end-to-end performance and label performance conditional on correct government/action selection.

## Reporting

- Confusion matrices for each dimension, retaining −1, 0, +1, and null; class-specific sample sizes, precision/recall, and uncertainty intervals.
- Human–human agreement before adjudication, human–model agreement, and performance against the adjudicated reference as separate measures.
- Action-selection and entity correctness separately from exact-span compliance.
- Weighted prevalence of coding errors, interpretation disputes, input defects, and mechanical failures. Each requires an appropriate sampling frame; valid-output samples cannot estimate failure rates among all requests.
- Language, country, source, and prompt-period diagnostics where sample sizes permit them.
- Missing-context and translation-completeness rates, and sensitivity of substantive findings to adjudication alternatives and source/country weighting.

Translation and preprocessing are part of comparative measurement ([Lucas et al., 2015](https://doi.org/10.1093/pan/mpu019)). Bilingual review should check actors, attribution, negation, modality, responsibility, accusations, outcomes, and evaluative language. Length ratios cannot establish faithful coverage. The October 17 input policy has no sentence minimum and tolerates minor defects; a usable English record may still omit politically relevant content.

## Historical and cross-country checks

Government identity must correspond to publication time. Publication country does not necessarily identify the evaluated government, and institutional role does not prove incumbent affiliation. Historical leadership metadata should use the resolved government and exact date, including transitions and uncertainty. The existence of a context dataset does not establish that production requests used it. Any future enrichment needs a documented version and evaluation.

A sensitivity study could compare otherwise equivalent inputs with factual affiliation information supplied or withheld. Synthetic party or name substitutions can probe sensitivity to irrelevant cues, but are diagnostic tests rather than population accuracy estimates. They must preserve the factual relationship to the incumbent.

## Downstream inference

High annotation accuracy does not by itself guarantee unbiased regression estimates or calibrated intervals. Methods combining model labels with a probability sample of expert labels offer one possible approach ([Egami et al., 2023](https://proceedings.neurips.cc/paper_files/paper/2023/file/d862f7f5445255090de13b825b880d59-Paper-Conference.pdf)). The project has not yet implemented this approach; its assumptions and sampling design would need to match the intended analysis.

Current aggregate results are descriptive distributions of model labels. They retain dated cohorts and denominators, distinguish `0` from `null`, and do not establish human-reference accuracy or causal media effects.
