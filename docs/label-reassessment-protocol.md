# Reassessing uncertain political labels

This November 10, 2026 follow-up examines all **79 previously uncertain dimension judgments across 55 articles** in the existing 173-article shared-action cohort. Membership was frozen before review. The original articles, model outputs, saved assessments and action comparison remain unchanged.

The question is whether each recorded label follows the supplied article and the fixed [coding prompt](../prompts/civic_20261020_complete_v1.txt), conditional on the recorded action and evaluated government. This is a targeted assistant review, not an independent human accuracy test. The other 440 dimension assessments are carried forward from the saved review; they have not received this new review.

## Decision rules

| Review outcome | Meaning |
|---|---|
| Supported | The recorded label clearly follows the evidence and rule, without a comparably supported competing label. |
| Defensible alternative | The recorded label is one of two or more comparably rule-consistent interpretations. |
| Needs correction | The evidence and rule exclude the recorded label; the review specifies a replacement or replacement set. |
| Unresolved | An input, reference or applicability problem prevents an assessment. |

Only **Supported** enters the strict support numerator. Defensible alternatives and unresolved judgments remain in the denominator and are reported separately. A proposed correction is a review judgment, not an independently established error or a production-data edit.

The prompt already uses zero for several kinds of insufficient directional evidence. Those cases do not automatically remain unresolved. Reviewers distinguish:

- the actor's political relationship to the incumbent, including relationships established through the action's target;
- the selected action's substantive reputational implication, which does not require observed opinion change;
- evaluation in the narrator's voice, as distinct from an attributed source's position;
- a competing interpretation from a missing government link, an input defect or a different preferred action.

The review holds the recorded action and government fixed. An earlier action-selection exclusion does not determine a political-label verdict. Reviewers flag action, reference and extraction limitations separately. They do not substitute another event to obtain a different label, infer affiliation from an institution alone, or use external political knowledge. Structural errors in other fields do not automatically invalidate readable political values. Evidence-span compliance is recorded separately from the semantic label assessment.

Fixing the recorded government does not establish that government coding applies. The final audit retained six judgments in two articles as **Unresolved** because meaningful government relevance was not established. A conditional zero reading and the full prompt's inapplicability/null rule conflict here; these zeros do not count as supported. A separate sensitivity excludes the two affected articles. This differs from an applicable government-related action whose political direction or reputational implication is simply not established.

## Review and adjudication

The 55 articles are divided into three disjoint packets. Each assigned reviewer reads the full supplied article and frozen prompt, derives the warranted label or admissible labels, and explains the comparison with the recorded value. The original label is visible; this is not blind independent coding. Earlier uncertainty rationales are withheld from the review packets, although some illustrative cases were discussed before the full review.

A second assistant reads each packet without seeing the first decisions. No assistant reviews its own first-pass packet. The lead assistant examines the two readings and records a final decision with an adjudication reason. Agreement is not a substitute for applying the rule: final decisions may retain ambiguity or differ from both initial assessments when the source warrants it. No target support percentage governs adjudication.

The private audit retains the frozen packet membership, input hashes, both readings, exact source excerpts, prompt rules, limitations, final decisions and reasons. The new decisions have not been individually approved by a human researcher. They remain distinguishable from the original Astra-assisted review.

## Reporting and reproduction

The [reducer](../scripts/build_label_reassessment.py) checks the complete 79-judgment membership, recorded labels, both review passes, admissible-label sets, exact excerpts in their named source segments and unchanged input hashes. It replaces only the old uncertain assessments when computing the revised 173-article totals. It also reports directional-label results and sensitivities excluding invalid full records, changed source views or unresolved-applicability articles, and restricting to actions shared with the action-review reference.

The original [aggregate results](../slides/figures/data/05_event_validation_20261110.json) are preserved. Updated aggregate results are written separately to `slides/figures/data/05_label_reassessment_20261110.json`. Neither individual article text nor private decisions are published.

With access to the authorized private review directory:

```sh
python3 scripts/build_label_reassessment.py \
  --private-root '/path/to/GenAI event review 2026-11-10' \
  --historical slides/figures/data/05_event_validation_20261110.json \
  --output slides/figures/data/05_label_reassessment_20261110.json
```

The updated rate combines carried-forward assessments with a targeted follow-up of uncertain cases. It does not estimate a fresh review of all 519 judgments, independent human agreement, or population accuracy. The historical sample and its source/input limitations remain unchanged; see [Validation](validation.md).
