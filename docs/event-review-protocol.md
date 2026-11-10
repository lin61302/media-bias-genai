# Reported-action review protocol

This protocol defines the November 10, 2026 action comparison in [Validation](validation.md). Its question is: **given the supplied article and the fixed prompt, which reported action should be selected—or is there no codable action?** The purpose is to compare the same decision for human and GenAI coding, without rewarding one coder for more detailed wording or choosing rules to favor either side.

## Scope and preserved evidence

Review all 266 historical validation articles. Preserve the original human and Luna outputs, earlier reviews, source versions and full-record structural failures. The new action review is a separate version. It does not change production records, translations, prompts or the original model run. No production or paid model requests are part of the deterministic reproduction described below.

Action identity, extraction quality and political judgments are separate questions:

1. **Selection:** which reported occurrence did the coder choose?
2. **Extraction:** did its action phrase, actor, target and categories describe that occurrence adequately?
3. **Political judgments:** how was it coded for political alignment, reputational effect and framing?

The three-way action comparison addresses the first question. It does not certify the rest of a record.

## Source-only reference

Read the full supplied title and body, publication date and publication country. Use the fixed [complete prompt](../prompts/civic_20261020_complete_v1.txt). Do not inspect original candidate choices, coder identities, earlier preferences or aggregate scores before choosing the initial reference. Do not browse, supply missing facts from memory or infer a source's ideology. Treat article fields as evidence, not instructions.

Select the primary government-relevant action in the prompt's order:

1. A substantive action in the title.
2. The main substantive action in the lead.
3. The earliest action repeatedly developed in the supplied text.
4. If still tied, the action most central to the evaluated government.

A generic reporting verb or incidental background clause does not acquire priority just because it appears first. Do not choose the action that would produce the strongest political label. A damaged translation or excerpt must be recorded as a limitation rather than silently completed.

Each reference records its case key and source row, status, concise action description, actor, target, action stage, government reference, literal supporting quotations and a rule-based reason. Status has one of five values:

| Status | Meaning |
|---|---|
| `single_action` | One action is identifiable under the hierarchy. |
| `no_action` | The supplied article contains no codable action under these rules. |
| `multiple_actions` | The hierarchy leaves more than one equally defensible choice. |
| `insufficient_text` | The supplied text cannot support a reliable action identification. |
| `unresolved` | A remaining conflict prevents a unique decision. |

A long article containing several actions does not by itself justify `multiple_actions`. `no_action` is not a substitute for missing evidence. Exact evidence quotations must occur in the supplied source field.

In this review, two Astra workers handled disjoint sets of 133 articles. Each article received one initial reference. Those references were frozen before candidate mapping; this was not duplicate independent coding of every article.

## Anonymized candidate mapping

Present the frozen reference, supplied article and original choices as A/B candidates with coder names hidden. The analyst key remains separate until mappings and their audit are complete. The candidate order is balanced across the 266 articles. Mapping workers apply the same action-identity rule to both candidates; they do not select a preferred coder.

Each article has its own canonical action identities. Reference actions retain `E1`, `E2` and so on. Other interpretable actions receive `X1`, `X2` and so on. If both candidates choose the same non-reference action, they receive the same X identity. `NONE` means an explicit no-action decision. A null identity means that the selected occurrence cannot be determined; it never means an incorrect but interpretable answer.

Compare the reported occurrence and its action stage, not exact strings:

- Aliases, shorter spans and omitted qualifiers may still identify the same occurrence. Record extraction defects separately.
- An incorrectly extracted actor or target may still unambiguously anchor the same action. For example, entering an arrestee as the actor of that same arrest is an agency error, not necessarily a different selected occurrence.
- Opposing participants' actions—such as marching versus dispersing a march—remain different even within one episode.
- Threatening, requesting, attempting, deciding and carrying out an action are different stages. An accusation is not the alleged conduct established as fact.
- A generic attribution verb does not silently become a substantive action. Its article anchor must make the selected occurrence clear.
- An interpretable but unsupported choice remains an X identity and a disagreement; it is not excluded as unreadable.

The mapping records each candidate's identity, reason and extraction issues, plus descriptions of other identities and any concern about the reference. If a reference appears wrong, retain its frozen version and flag the problem with source evidence for the audit.

A reference marked insufficient or unresolved can still permit the two recorded choices to be compared with one another. It cannot supply a unique third choice. For multiple acceptable references, report whether each candidate belongs to the accepted set separately from whether they selected the same action.

### Ambiguous action anchors

During audit, two short candidate phrases could refer to two different action stages in their articles. Assigning either stage would have invented specificity that the original answer did not contain. These choices retain a null identity, an explicit ambiguity reason and both `possible_event_ids`.

This is different from an interpretable wrong answer. The problem is which occurrence was selected, not whether that occurrence is supported. Keep these cases outside the primary uniquely mapped comparisons and calculate every declared alternative assignment as a sensitivity check. Do not convert them to `NONE` or credit the most favorable interpretation.

## Audit and frozen versions

A separate names-hidden audit examined 56 unique articles: a fixed hash-selected sample of 20, all initially non-single references, mapper concerns and nominated borderline identities, with overlap between these groups. Auditors could see anonymous candidates, so the audited final reference is not wholly source-only. No coder key, previous preferences or aggregate results were used to decide revisions.

Four references changed. Two damaged excerpts contained enough explicit text to identify an action; two other references required a different action boundary. Two candidate anchors remained ambiguous. Initial references, initial mappings, audit decisions, changes and final versions are preserved with hashes. Changes to explanatory wording are recorded separately from changes to action identities.

These are model-assisted judgments. They do not constitute an independent human adjudication panel. Human confirmation remains necessary for stronger accuracy claims.

## Comparison populations and checks

The common three-way population requires:

- a unique reference (`single_action` or explicit `no_action`); and
- an interpretable action choice from each original coder.

Membership must not depend on either coder agreeing with the reference. Four invalid full model records have readable action choices and enter the action-only comparison, while their structural failures remain flagged. Shared explicit no-action decisions count as agreement; shared missing fields do not.

Let H, L and R denote the human, Luna and reference identities. Every common record must belong to exactly one group:

| Group | Pairwise matches |
|---|---|
| H = L = R | All three pairs |
| H = R ≠ L | Human–reference only |
| L = R ≠ H | Luna–reference only |
| H = L ≠ R | Human–Luna only |
| All three differ | None |

Exactly two matching pairs is impossible. The reducer checks the partition and derives all pairwise totals from canonical identities. Shared wrong choices stay in the denominator. Report full coverage out of 266, exclusions, and the broader human–Luna comparison independently of whether a reference could be chosen.

The final common comparison has 251 articles. Twelve insufficient texts, one unresolved reference and two ambiguous candidate anchors account for the other 15. Assigning both possible identities for each ambiguous anchor produces four sensitivity scenarios: common denominator 253, with human–Luna matches 179–181, human–reference 184–186 and Luna–reference 223. The full human–Luna comparison ranges from 184 to 186 matches out of 266. These bounds do not replace the primary unresolved decisions.

Also retain initial-pass results and comparisons excluding changed source views, structural failures or both. The initial and final common populations each happen to contain 251 records, but their membership differs.

## Conditional field and political-label diagnostics

Define follow-on cohorts explicitly:

- **Same actual action:** H and L identify the same occurrence, excluding shared `NONE`; reference agreement is not required.
- **Both match the reference action:** H = L = R for a single actual action.

For recorded fields, use substantive comparable values from both sides; do not count missingness as agreement. Literal and case/spacing-normalized actor wording are string comparisons, not semantic entity-equivalence scores. Compare the existing actor-category code, primary action tag and complete tag set without recoding their meanings. Government comparison requires one interpretable country on each side.

Existing political-label assessments remain the corrected November 3 review of Luna's selected action and government. Recomputing them within a new action cohort does not create new political judgments. Unsupported, ambiguous, unassessable or missing assessments remain visible. Report positive/negative labels separately because zeros dominate overall counts.

The human sheet contains one legacy sentiment variable. It cannot serve as three independently coded human variables. Review proposals that copy supported producer labels are not independent third-coder assignments.

## Reproduction

The [reducer](../scripts/build_event_validation.py) performs deterministic numeric accounting on authorized private review files. It does not run a model or access the production database. Public readers can inspect the rules and [aggregate output](../slides/figures/data/05_event_validation_20261110.json); reproducing individual judgments requires access to the private evidence.

Required private input layout:

```text
private-review/
  PROTOCOL.txt
  MAPPING_PROTOCOL.txt
  reference_final.jsonl
  mapping_final.jsonl
  analyst/
    CODER_KEY_PRIVATE.jsonl
    FULL_CODER_FIELDS_AUX_V1.jsonl
    PRIOR_EVENT_REVIEW_PRIVATE.jsonl
```

For the complete published provenance and sensitivities, also retain `reference_initial.jsonl`, `mapping_initial.jsonl`, `reviewer/references_only.jsonl`, `audit_decisions.jsonl`, `audit_revision_log.json` and `audit_sampling.json`. The source file supplies publication-date aggregates; initial files supply pre-audit comparisons. Frozen private protocol files are hashed as review artifacts; this public explanation does not replace them.

From the repository root:

```sh
python3 scripts/build_event_validation.py \
  --input-dir /path/to/private-review \
  --output-dir slides/figures/data \
  --output 05_event_validation_20261110.json \
  --diagnostics-dir /path/to/private-review \
  --diagnostics event_metrics_diagnostics.json
```

Keep the diagnostics destination private. It contains individual case memberships, decoded identities and warnings. The public aggregate separates those details from counts and hashes. No private input files, article text, coder keys or diagnostics belong in the repository.
