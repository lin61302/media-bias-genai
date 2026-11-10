# Validation

Human validation is incomplete; a historical human-coded comparison is available, while a representative independent evaluation of all three current constructs remains planned. Structural checks and independent database verification establish that outputs conform to the schema and were stored correctly. They do not establish correct action selection, political interpretation, or translation fidelity.

## Preliminary reviews

Two reviews by an AI reviewer examined random samples of structurally valid, independently stored complete-prompt outputs. Each reviewer first coded the supplied input without seeing its stored labels.

| Review date | Sample size | Eligible pool | Exact agreement on all three labels |
|---|---:|---:|---:|
| October 21, 2026 | 30 | 35,412 | 24 |
| October 26, 2026 | 40 | 541,962 | 31 |

The later sample excluded the earlier 30 records. Both samples concern recent-period data and exclude failed or invalid requests. Agreement with one AI reviewer is not a human-reference accuracy estimate. The different sampling pools and review conditions do not support pooling the figures into a general performance estimate. Matching labels can coexist with incorrect actors, targets, or action spans.

The October 26 review identified five clear scope, extraction, or role errors. Across the reviews, observed problems included an event treated as an actor, a destination treated as an entity target, local conflict attributed to the national government without a supplied link, unrelated title/body content, and English text missing substantive original material. Other disagreements concerned interpretation. These small reviews diagnose error types; they do not estimate their population prevalence.

All 70 requests lacked incumbent-context metadata. Exact reconstruction of the supplied English confirmed what the model received, but did not establish fidelity to the original article. These limitations matter when the coding rules prohibit outside facts.

## November 2 historical comparison

A separate comparison processed 266 previously human-coded articles with the complete prompt and full supplied text; 262 outputs were structurally valid and four invalid. An AI-assisted qualitative review retained the original human annotations and recorded proposed corrections separately. It does not constitute an independent human adjudication panel.

The event-selection comparison gives the following **agreement rates**, based on AI-assisted review of whether the two codings describe the same event:

| Comparison denominator | Matches | Agreement |
|---|---:|---:|
| Both human and model identify an action | 167 / 211 | 79.1% |
| All valid outputs, including shared no-action decisions | 178 / 262 | 67.9% |

The latter includes 11 shared no-action decisions and counts all 40 action/no-action disagreements. Four invalid outputs are outside these valid-output denominators. Event matching and proposed corrections were reviewed with AI assistance; this is not an independent human adjudication panel. These percentages evaluate event selection, not the accuracy of the three political judgments.

Astra also reviewed action selection and extraction against the supplied source and current definitions. On the same 262 valid-output records:

| Astra's preference | Articles | Share |
|---|---:|---:|
| Luna preferred | 121 | 46.2% |
| Human preferred | 44 | 16.8% |
| Both defensible | 83 | 31.7% |
| Unresolved or neither supported | 14 | 5.3% |

The last category combines nine unresolved and five neither-supported judgments. When the human and Luna selected **different events** (44 records), Astra preferred Luna in 17, the human in 16, and had no single preferred answer in 11 (five both defensible, five unresolved, one neither). This near-even split applies only to that subgroup. A preferred extraction can still describe the same event as the other coding, so event agreement and reviewer preference are different results.

Astra saw both codings and project context; this is a dependent AI review, not independent human adjudication. Preferences concern action selection/extraction, not correctness of all fields. The full raw review also contains four invalid outputs; the table excludes them to match the valid-output denominator above. These judgments do not establish that Luna outperforms humans.

This is a historical, selected sample. Its legacy annotation used one sentiment field rather than the current three constructs. Historical inputs were truncated while the new comparison used full supplied text; some titles and bodies differed. Event equivalence, exact-span agreement and political-label agreement therefore answer different questions. Conditional agreement rates from this exercise must not be presented as overall classifier accuracy. No representative human-reference accuracy estimate is established by these checks. Private article texts and review workbooks are not part of this repository.

## Political-label review conditional on a shared event

Action agreement does not establish label reliability. The corrected November 3 review identifies **167 articles in which the human and model codings describe the same event**. Of these, **155** also have model action selection judged compliant or defensible; two have unsupported selection and ten unresolved selection. The following diagnostic uses the 155 accepted selections. Shared-event identity does not certify matching action spans, actors, targets, modality, or evaluated government.

The reviewer assessed the producer's alignment, reputation, and framing labels against the supplied evidence and current definitions. It saw both codings and project context. These are **dependent AI evidence-review verdicts**, not independent labels or human-reference accuracy. They condition on the producer's selected government: 143 of the 155 records lack a human country reference. The historical human sentiment field cannot serve as three separate human labels.

| Dimension | Supported | Ambiguous or boundary | Correction proposed | Supported among directional labels only |
|---|---:|---:|---:|---:|
| Alignment | 126 / 155 (81.3%) | 20 | 9 | 24 / 37 (64.9%) |
| Reputation | 122 / 155 (78.7%) | 29 | 4 | 7 / 24 (29.2%) |
| Framing | 143 / 155 (92.3%) | 9 | 3 | 8 / 14 (57.1%) |

“Correction proposed” corresponds to the review's *Unsupported* verdict; it is not an independently established error. Ambiguous or boundary cases remain unresolved. All three labels were supported in 103 of 155 articles. Directional denominators include only the producer's −1 and +1 labels; the overall columns also include 118 alignment zeros, 131 reputation zeros, and 141 framing zeros. Their high frequency makes the directional breakdown essential. These small, selected subsets do not estimate population performance.

As a sensitivity check, retaining **all 167 shared-event articles** gives supported / ambiguous / correction-proposed counts of **133 / 25 / 9** for alignment, **128 / 34 / 5** for reputation, and **154 / 10 / 3** for framing. These totals retain the 12 records with action-selection problems; they should not replace the gated diagnostic without that qualification.

The review's numeric proposals are not a third set of independently assigned labels: supported values were copied from the producer, explicit corrections were recorded for unsupported values, and ambiguous cases were left unresolved. A confusion matrix based on those proposals would therefore overstate independence. The [aggregate review data](../slides/figures/data/05_same_event_label_review.json) preserve both denominators, directional counts, review limitations, and source hashes. No article text or individual review records are published.

## GenAI validation (Astra-assisted)

The November 10 reconstruction restores the comparisons from the November 3 review: human and Luna coding, followed by Astra's assessment of their selections and labels. Astra saw the existing answers and supplied text. It did not produce a complete independent third coding. The [three-way comparison aggregates](../slides/figures/data/05_threeway_validation.json) retain the counts, missing values, conditioning rules and source hashes.

### Three-way event comparison

These comparisons use the same **187 records with a determinate event judgment**:

| Comparison | Matching event choice | Share |
|---|---:|---:|
| Human–Luna | 155 / 187 | 82.9% |
| Luna–Astra | 170 / 187 | 90.9% |
| Human–Astra | 171 / 187 | 91.4% |

The broader 211 paired-action records comprise 155 accepted shared events, 15 accepted Luna-preferred events, 16 human-preferred events, one neither-supported case, five cases allowing different defensible events and 19 unresolved cases. The last two groups are excluded from the common 187-record denominator. The original human–Luna event comparison remains **167/211 = 79.1%** before this additional selection.

The 187-record rule is asymmetric: two Luna-preferred events were excluded because Luna's selection assessment remained unresolved, without a parallel human-selection assessment. The 171-versus-170 difference therefore does not establish a human performance advantage. These are overlaps with an informed AI review, not independent three-rater reliability.

### Astra's full action-selection and extraction review

Event identity and extraction preference answer different questions. Two codings can describe the same event while differing in specificity, agency, modality or completeness.

| Reviewed group | Luna preferred | Human preferred | Both defensible | Unresolved | Neither supported |
|---|---:|---:|---:|---:|---:|
| All 262 valid outputs | 121 | 44 | 83 | 9 | 5 |
| Same event: 167 | 75 | 20 | 67 | 2 | 3 |
| Different event: 44 | 17 | 16 | 5 | 5 | 1 |
| Action/no-action disagreement: 40 | 29 | 8 | 0 | 2 | 1 |
| Both select no action: 11 | 0 | 0 | 11 | 0 | 0 |

The four subgroup rows partition the 262 valid outputs. The 17/16 result concerns only the 44 different-event records; it does not summarize Astra's full review. Review preferences do not certify that every field in a preferred record is correct.

### Agreement on other fields after selecting the same event

The 155 accepted shared-event records are the same records used in the political-label review above. The larger 167-record column also retains 12 unsupported or unresolved model selections.

| Human–Luna comparison | All 167 shared events | Accepted 155 shared events |
|---|---:|---:|
| Exact action-tag set | 99 / 167 | 92 / 155 |
| Primary action tag | 108 / 167 | 101 / 155 |
| Actor category code | 106 / 149 | 101 / 140 |
| Literal actor wording | 46 / 146 | 43 / 137 |
| Actor wording after case/spacing normalization | 53 / 146 | 49 / 137 |
| Reaction tag, both substantive | 9 / 20 | 9 / 19 |

Missing or uncodable values are excluded from each comparison, not counted as matches. Wording equality is not a semantic entity-equivalence judgment. Actor-category normalization extracts the existing A–W code without recoding its meaning.

Astra assessed each side's action tags separately:

| Reviewed group | Human tags supported | Luna tags supported |
|---|---:|---:|
| All 211 paired actions | 142 / 211 (67.3%) | 150 / 211 (71.1%) |
| All 167 shared events | 118 / 167 (70.7%) | 127 / 167 (76.0%) |
| Accepted 155 shared events | 114 / 155 (73.5%) | 121 / 155 (78.1%) |

These are support assessments of the recorded tags. There is no complete independently coded Astra tag set for an exact three-way tag-agreement comparison.

### Numeric sign correspondence with the legacy human sentiment

Humans recorded one field, `sent_gov_final`, rather than separate alignment, reputation and framing judgments. The following table compares that **legacy sentiment's numeric sign** with each Luna dimension and Astra's corresponding proposal. It is a descriptive correspondence check across different constructs, not three-way agreement on the same sentiment definition.

Within the 155 accepted shared events, each row uses only records with all three numeric values available, so the three pairs have an identical denominator within that row:

| Dimension compared with human legacy sentiment | Common records | Human–Luna | Human–Astra proposal | Luna–Astra proposal |
|---|---:|---:|---:|---:|
| Alignment | 132 | 75 / 132 (56.8%) | 74 / 132 (56.1%) | 123 / 132 (93.2%) |
| Reputation | 123 | 63 / 123 (51.2%) | 63 / 123 (51.2%) | 119 / 123 (96.7%) |
| Framing | 141 | 61 / 141 (43.3%) | 64 / 141 (45.4%) | 138 / 141 (97.9%) |

Five human sentiments in the accepted-event cohort are nonnumeric. Astra leaves 20 alignment, 29 reputation and nine framing proposals unresolved. Unresolved values remain missing, not zero or agreement. When Astra supports a Luna label, its retained proposal copies that label; otherwise it may propose a correction. This construction partly accounts for the high Luna–Astra correspondence and cannot establish independent reliability. The support rates **126/155, 122/155 and 143/155** above retain unresolved assessments in their denominators and must not be replaced with these complete-case rates.

The evaluated government is another limitation. Among the 167 shared events, the human reference is missing in 153, different in seven, multiple in two and explicitly matching in only five. All five matching references are within the accepted 155. This is too little evidence for a general comparison with action and government both held fixed. No record combines literal action-wording equality with an explicitly matching human–Luna government.

Human actor, category, action-tag and reaction fields can be compared with Luna where recorded. Exact comparisons against independently coded Astra equivalents are **not available**: Astra supplied assessments, preferences and proposals, not a full third set of those fields. Historical `*_GPT` fields are an older model baseline, not Astra. The November 3 correction leaving the disputed reputation assessment unresolved is retained, and original human and model values remain unchanged.

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
