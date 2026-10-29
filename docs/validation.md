# Validation plan and current limits

**Status: proposed human-validation design; not a completed accuracy evaluation.** Structural compliance and independent database verification establish useful engineering facts. They do not establish that the model selected the right action, interpreted politics correctly, or received a complete and faithful article translation.

## What has been checked

Two preliminary blind-first AI reviews on October 21 (30 cases) and October 26 (40 cases), 2026, examined randomly selected, structurally valid, independently stored complete-prompt outputs from their respective frozen eligible pools. The later draw excluded the earlier 30 cases. Both concern recent-period data, not the full historical corpus or failed requests. The October 26 review identified five clear scope/extraction/role issues, alongside interpretation disputes and upstream text problems; that count is diagnostic, not a population accuracy estimate.

First-pass label triples agreed with the stored outputs in 24/30 and 31/40 cases respectively. These figures are **single-AI-reviewer agreement**, not 80% or 77.5% accuracy estimates. Disagreements include defensible alternatives; matching label triples can coexist with incorrect actors, targets or action spans. The different sampling pools and review conditions also make a pooled percentage inappropriate as a general performance result.

The reviews found concrete scope/extraction errors and upstream source/translation defects. Observed examples included an event treated as an actor, a geographic destination treated as an entity target, local conflict attributed to the national government without a supplied link, unrelated title/body content, and English text missing substantive original material. Exact reconstruction of the supplied English requests did not establish fidelity to the original article. All 70 reviewed requests lacked incumbent-context metadata; this limits what can be inferred about affiliation under a prompt that forbids outside facts. These findings motivate targeted validation, not a population defect rate.

## Separate four validity questions

| Layer | Evaluation question | Suitable evidence |
|---|---|---|
| Source and translation | Does the supplied record preserve the relevant original meaning and adequate context? | Bilingual paired review of source and supplied English; title/body/date checks |
| Extraction and reference | Are `gov`, action, actor, target, roles and modality correct under the codebook? | Independent human annotations with exact spans and disagreement reasons |
| Political labels | Are alignment, reputational implication and explicit narrator orientation applied consistently? | Human reference labels on the exact supplied input; class-level evaluation |
| Research inference | Do substantive comparisons survive measurement error and sample composition? | Probability-based validation, subgroup diagnostics and analysis sensitivity |

Text-as-data research requires validation tailored to the intended inference, not simply a tool's general reputation ([Grimmer and Stewart, 2013](https://doi.org/10.1093/pan/mps028)). Published LLM annotation successes motivate this approach, but performance in other tasks is not evidence of performance on these constructs, countries and translations ([Gilardi, Alizadeh and Kubli, 2023](https://doi.org/10.1073/pnas.2305016120)).

## Proposed annotation design

1. **Fix the target population first.** Use a frozen complete-prompt analysis cohort with a stable identity and an explicit cutoff. A first human study could focus on the January 2025–May 2026 discussion cohort; claims must remain restricted to that population.
2. **Draw a probability sample with recorded inclusion probabilities.** Ensure positive selection probability for every eligible record. Allocate review across language, country, source, month and model-label categories, with oversampling of directional and null cases where useful. Plan the size around desired precision and available bilingual expertise; a few hundred annotations cannot establish every country-language subgroup's accuracy.
3. **Keep targeted diagnostics separate.** Add known difficult cases—allegations, peaceful coercion, local/national attribution, foreign governments, quoted criticism, conditions versus actions and partial translations—to a challenge set. Its success rate is not population accuracy. If diagnostic oversampling is part of the probability sample, retain the actual probabilities and use appropriate weights.
4. **Use at least two trained human coders for the evaluation set.** Provide the frozen codebook and exact supplied input. Keep stored model labels hidden during first-pass coding. Use a separate training/calibration set and preserve initial judgments before discussion. Adjudicate disagreements with a third reviewer or a documented consensus procedure. Keep unresolved alternatives rather than forcing false certainty.
5. **Separate codebook compliance from missing information.** First judge what is warranted by the exact supplied English. Then, in a distinct pass, compare the original-language text and metadata. Do not count a model as violating the codebook merely because a knowledgeable reviewer can supply a fact absent from its input. Do count missing context as a limitation of the research measurement when it changes the intended inference.
6. **Audit the causal chain within each record.** Check government/date, selected action and modality, entities/roles, and then each label. Report both end-to-end label performance and performance conditional on a correct government/action selection. The conditional metric must not replace the end-to-end one.

This is an analysis proposal. It does not authorize paid reruns or silently change production inputs, prompts, labels or no-repeat state.

## What to report

- Per-dimension confusion matrices including −1, 0, +1 and null; precision/recall for directional labels; class-specific sample sizes and uncertainty intervals.
- Human-human agreement before adjudication, human-model agreement, and adjudicated-reference performance as distinct quantities. Preserve unresolved cases and state the adopted reference standard.
- Action-selection and entity correctness separately from exact-span compliance. A verbatim span can still describe the wrong event or role.
- Weighted prevalence of clear contract errors, interpretation disputes, input defects and mechanical failures, using the appropriate sampling frame for each. Reviews sampled only from valid outputs cannot estimate the failure rate among all requests.
- Language, country/source and prompt-period diagnostics where sample sizes support them. A pooled average can hide systematic subgroup error.
- Missing-context and translation-completeness rates as separate measures. The current input policy has no sentence minimum and tolerates minor defects. A usable English record can still omit politically important original material.
- Sensitivity of substantive results to reasonable adjudication alternatives and source/country weighting. A census of model outputs has measurement uncertainty even when its arithmetic counts are exact.

Translation and preprocessing are part of the measurement design in comparative text analysis ([Lucas et al., 2015](https://doi.org/10.1093/pan/mpu019)). For political content, bilingual review should explicitly check actors, attribution, negation, modality, responsibility, accusations, outcomes and evaluative language. Length ratios alone cannot establish faithful coverage.

## Historical and cross-country reference checks

The evaluated government must be identified at publication time. Publication country is not always the evaluated government; institutional role is not proof of incumbent affiliation. Historical leadership metadata should be keyed to the resolved government and exact date, with transitions and uncertainty represented explicitly. An existing context dataset or lookup utility does not prove that production requests used it. Any future enrichment is a separately documented version and requires validation of its effect.

A useful sensitivity exercise would compare otherwise equivalent records with factual affiliation information supplied versus withheld, without inventing political facts. Synthetic party/name substitutions can probe whether irrelevant cues change coding, but those are stress tests rather than population accuracy estimates. Do not alter the factual relation to the incumbent and call the result a valid counterfactual.

## Downstream inference

High annotation accuracy alone does not guarantee unbiased regressions or correctly calibrated intervals. One available approach combines surrogate labels with a smaller probability sample of expert labels and known sampling probabilities ([Egami et al., 2023](https://proceedings.neurips.cc/paper_files/paper/2023/file/d862f7f5445255090de13b825b880d59-Paper-Conference.pdf)). Its assumptions and estimation procedure would need to be implemented for the specific target; this project has not done so.

The November 11 release should therefore label aggregate charts **descriptive model-coded patterns**, include a dated cohort and denominator, show 0 and null separately, and place the validation status next to the findings. No human-gold accuracy, causal media effect or complete-translation certification is claimed.
