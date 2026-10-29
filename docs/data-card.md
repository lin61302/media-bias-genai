# Data card

## Project corpus and current snapshot

The project covers news reporting on civic actions involving national governments. The frozen extraction archive contains **7,373,816 unique eligible article IDs**, across **189 partitions and 178 months**, from **71 countries plus international or regional sources**. These are historical extraction counts, not a count of currently qualified inputs. The production target is **January 2012–June 2026**, or 174 months; processing is incomplete.

The aggregate data currently included in this repository cover a narrower **January 2025–May 2026** cohort using the complete prompt. This dated subset supports comparisons under one prompt version and does not define the project's full scope.

Each observation is one processed article with one selected action. Repeated coverage of an event can produce multiple observations. Scraping, source availability, civic relevance filters, translated-field checks, processing outcomes, and prompt version all affect inclusion. The cohort is not a probability sample of news or events.

## Counts and denominators

| Quantity | Count | Definition |
|---|---:|---|
| Input-clear articles, January 2025–May 2026 | 624,751 | Frozen source inventory minus input holds |
| Stored outcomes, either prompt | 614,204 | Includes older-prompt records and failed outcomes |
| Stored complete-prompt outcomes | 552,208 | Includes structural and API failures |
| Valid complete-prompt outcomes | 542,981 | Denominator for the current label distributions |
| Stored older-prompt outcomes | 61,996 | Excluded from complete-prompt label tables |

Valid complete-prompt coverage is **86.91%** of the input-clear pool. This measures processing coverage within the frozen source pool, not population coverage or model accuracy. Input-clear records include multiple prompt cohorts and records with prior submission claims; the term does not mean each record is available for a new request.

The **9,227** stored complete-prompt outcomes that fail structural or API checks are excluded from label distributions. Within valid outcomes, null labels remain in the percentage denominator for each dimension. Accepted, returned, structurally valid, and independently verified stored outcomes are different processing stages and are not additive counts.

## Composition and missingness

The fixed cohort contains **370 source domains**, **71 publication-country codes plus `ALL`**, and **29,512 observations with `ALL` provenance**. `ALL` denotes international or regional sources. Publication-country memberships can overlap and must not be summed as unique articles.

The evaluated-government field contains **187 distinct non-null codes** and **28,896 records with null government identity**. These codes describe the government selected for evaluation, not 187 independently sampled national media systems or standardized leader and regime entities.

Monthly coverage varies. June 2026 contains stored older-prompt data but no valid complete-prompt outcomes at this checkpoint, so it is excluded. Earlier years were still being processed unevenly. High-volume sources and countries receive more weight in pooled article-level percentages; language, translation, and source composition can also affect the distributions.

The monthly tables support overall and month-specific marginal counts. They do not contain joint `align × rep × frame`, country-by-label, source-by-label, or matched-event tables. Those analyses require documented aggregate extraction from article-level records.

## Provenance

The independent storage audit cutoff is **2026-10-29T05:20:31.624176+00:00**. Aggregate generation and public-source publication occurred separately. The [snapshot metadata](../data/monthly_complete_snapshot.json) record hashes and commit-pinned links to the aggregate files from [Processed data & outcomes](https://huggingface.co/spaces/zungru/media-bias-reported-polarization).

The source dashboard's name includes “polarization,” but the current variables do not measure societal polarization. The [research design](research-design.md) explains the proposed political comparisons and their evidence requirements.

## Access

This repository includes aggregate counts, the coding prompt, methods, and reproduction code. Article text, identifiers, observation-level URLs, raw model outputs, and private correspondence are not included. Article-level access requires coordination with the project team and consideration of source rights. The repository does not grant a license to underlying news content.

## Limitations

Human semantic validation and entity standardization remain incomplete. English-input checks do not establish fidelity to original-language sources. Translated summaries can omit context, and missing historical incumbent metadata can limit affiliation and responsibility judgments.

The published files allow reproduction of aggregate calculations. Recreating the underlying annotations requires controlled access to the source data and the recorded run configuration. See [validation.md](validation.md) for planned human review and measurement checks.
