# Data card

## Project corpus and historical October 29 snapshot

The project covers news reporting on civic actions involving national governments. The frozen extraction archive contains **7,373,816 unique eligible article IDs**, across **189 partitions and 178 months**, from **71 countries plus international or regional sources**. These are historical extraction counts, not a count of currently qualified inputs. The production target is **January 2012–June 2026**, or 174 months; processing is incomplete.

The original October 29 aggregate tables included in this repository cover a narrower **January 2025–May 2026** cohort using the complete prompt. This dated subset supports comparisons under one prompt version and does not define the project's full scope.

Each observation is one processed article with one selected action. Repeated coverage of an event can produce multiple observations. Scraping, source availability, civic relevance filters, translated-field checks, processing outcomes, and prompt version all affect inclusion. The cohort is not a probability sample of news or events.

## November 4 analysis snapshot

The [analysis manifest](../data/analysis_snapshot.json) records a separate fixed aggregate release, independently audited at **2026-11-04T13:38:01.213139+00:00**. The complete prompt SHA-256 is `452ac4b66439acfb34c9e1016d037433df05b24fc24241e384fe58afc74b71fc`.

| Article period | Valid records | Eligible joint comparisons |
|---|---:|---:|
| January 2022–May 2026 (default) | 2,157,912 | 1,984,402 |
| January 2021–May 2026 (optional) | 2,654,346 | 2,440,312 |

Eligible comparisons require an identified government and primary action and numeric −1, 0, +1 values for all three measures. Zero stays in the denominator; null does not. Missing/unidentified categories are separately reported, not compared with substantive groups. Missingness counts overlap. Similarity maps additionally exclude unknown actors and unclassified actions. A grouping field can introduce further exclusions. June has older-prompt data at this cutoff and is excluded.

This release supplies 27-cell joint label counts by group and month, actor/action/target interactions, government/outlet comparisons, country context, contributor counts and sourced story accounts. It contains no article-level text or event matching. See the [dashboard guide](dashboard-guide.md) for the exact controls and denominators. Country-year context comes from V-Dem v16; geographic mappings follow UN M49 with disclosed conventions. Source hashes and attribution are retained in `country_context.json`. V-Dem values and adaptations are CC BY-SA 4.0.

The processing target, historical extraction inventory and this analysis cohort are different quantities. Current processing totals must not replace these fixed denominators. The original tables below remain reproducible through `scripts/reproduce_summary.py`; the new notebook uses the new manifest.

## October 29 counts and denominators

| Quantity | Count | Definition |
|---|---:|---|
| Input-clear articles, January 2025–May 2026 | 624,751 | Frozen source inventory minus input holds |
| Stored outcomes, either prompt | 614,204 | Includes older-prompt records and failed outcomes |
| Stored complete-prompt outcomes | 552,208 | Includes structural and API failures |
| Valid complete-prompt outcomes | 542,981 | Denominator for the October 29 marginal label distributions |
| Stored older-prompt outcomes | 61,996 | Excluded from complete-prompt label tables |

Valid complete-prompt coverage is **86.91%** of the input-clear pool. This measures processing coverage within the frozen source pool, not population coverage or model accuracy. Input-clear records include multiple prompt cohorts and records with prior submission claims; the term does not mean each record is available for a new request.

The **9,227** stored complete-prompt outcomes that fail structural or API checks are excluded from label distributions. Within valid outcomes, null labels remain in the percentage denominator for each dimension. Accepted, returned, structurally valid, and independently verified stored outcomes are different processing stages and are not additive counts.

## Composition and missingness

The October 29 cohort contains **370 source domains**, **71 publication-country codes plus `ALL`**, and **29,512 observations with `ALL` provenance**. `ALL` denotes international or regional sources. Publication-country memberships can overlap and must not be summed as unique articles.

The evaluated-government field contains **187 distinct non-null codes** and **28,896 records with null government identity**. These codes describe the government selected for evaluation, not 187 independently sampled national media systems or standardized leader and regime entities.

Monthly coverage varies. June 2026 contains stored older-prompt data but no valid complete-prompt outcomes at this checkpoint, so it is excluded. Earlier years were still being processed unevenly. High-volume sources and countries receive more weight in pooled article-level percentages; language, translation, and source composition can also affect the distributions.

The October 29 monthly tables support overall and month-specific marginal counts. They do not contain joint `align × rep × frame`, country-by-label, source-by-label, or matched-event tables. The separate November 4 extraction described above supplies joint and grouped aggregates; matched-event tables remain unavailable.

## Provenance

The independent storage audit cutoff is **2026-10-29T05:20:31.624176+00:00**. Aggregate generation and public-source publication occurred separately. The [snapshot metadata](../data/monthly_complete_snapshot.json) record hashes and commit-pinned links to the aggregate files from [Processed data & outcomes](https://huggingface.co/spaces/zungru/media-bias-reported-polarization).

The source dashboard's name includes “polarization,” but the current variables do not measure societal polarization. The [research design](research-design.md) explains the proposed political comparisons and their evidence requirements.

## Access

This repository includes aggregate counts, the coding prompt, methods, and reproduction code. Article text, identifiers, observation-level URLs, raw model outputs, and private correspondence are not included. Article-level access requires coordination with the project team and consideration of source rights. The repository does not grant a license to underlying news content.

## Limitations

Human semantic validation and entity standardization remain incomplete. English-input checks do not establish fidelity to original-language sources. Translated summaries can omit context, and missing historical incumbent metadata can limit affiliation and responsibility judgments.

The published files allow reproduction of aggregate calculations. Recreating the underlying annotations requires controlled access to the source data and the recorded run configuration. See [validation.md](validation.md) for planned human review and measurement checks.
