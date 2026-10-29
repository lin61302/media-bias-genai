# Data card: October 29, 2026 snapshot

## Scope and unit

The frozen extraction archive contained 7,373,816 unique eligible article IDs across 189 partitions and 178 months, including 71 countries plus international/regional sources. This historical extraction count is broader than the current presentation cohort and does not certify current input eligibility. The current production target is January 2012–June 2026 (174 months); those target months should not be described as fully processed.

The talk fixes a narrower **January 2025–May 2026 complete-prompt cohort** for consistent comparisons. Each observation is one processed article with one selected action. Repeated coverage of the same event can produce multiple observations. Source scraping, availability, civic relevance filtering, translated-field sufficiency, processing outcomes, and prompt version all determine inclusion.

## Denominators

| Quantity | Count | Interpretation |
|---|---:|---|
| Input-clear articles, 17-month window | 624,751 | Frozen source inventory minus input holds; neither a census of news nor live eligibility |
| Stored outcomes, either prompt | 614,204 | Includes older-prompt records and failures |
| Stored complete-prompt outcomes | 552,208 | Includes structural/API failures |
| Valid complete-prompt outcomes | 542,981 | Denominator for all label percentages in the talk |
| Stored older-prompt outcomes | 61,996 | Excluded from the talk's label tables |

Valid complete-prompt coverage is 86.91% of the input-clear denominator. This is coverage of the frozen input-clear source pool, not estimated population coverage or model accuracy. Input-clear includes protected claims and multiple prompt cohorts, and does not mean every article has been prepared for submission. The 9,227 difference between stored complete-prompt outcomes and valid outcomes remains outside label distributions. Within valid outcomes, null labels remain in each percentage denominator.

The broader production run has separate accepted, returned, structurally valid, and independently stored stages. These counts must not be conflated or added together. The presentation uses the fixed cohort above instead of a changing production total.

## Coverage and missingness

The fixed cohort has 370 source domains and 71 publication-country codes plus `ALL`. `ALL` contributes 29,512 observations and denotes international/regional provenance. The target-government variable reaches beyond publication countries: 187 distinct non-null codes plus 28,896 records with null government identity. These counts do not represent 187 independently sampled national media systems. Country codes identify the government country, not a standardized leader or regime entity.

Monthly coverage varies. June 2026 has stored older-prompt data but zero valid complete-prompt outcomes at this checkpoint, so it is excluded. Earlier years were filling unevenly and are not appended to this descriptive window. Source composition and language/translation differences can affect every marginal percentage. High-volume outlets and countries contribute more to pooled article-weighted estimates.

The released monthly tables support overall and month-specific marginal calculations. They do **not** contain joint `align × rep × frame`, country-by-label, source-by-label, or matched-event tables. Those analyses need a new documented aggregate extraction from appropriate record-level data.

## Provenance

The storage audit cutoff is **2026-10-29T05:20:31.624176+00:00**. It is different from the later aggregate-generation time and from the talk date. The source dashboard is [Processed data & outcomes](https://huggingface.co/spaces/zungru/media-bias-reported-polarization). This package freezes its relevant aggregate bytes with hashes and commit-pinned source links in [monthly_complete_snapshot.json](../data/monthly_complete_snapshot.json).

The dashboard name includes “polarization”; the present measurements do not establish societal polarization. No new paid inference, corpus-wide rescan, or database write is part of reproducing these materials.

## Access and disclosure

The repository releases aggregate counts, the coding prompt, and methods. It excludes news text, identifiers, URLs identifying individual observations, raw outputs, operational histories, and private correspondence. Access to article-level research data requires a separate discussion with the project team and consideration of source rights. No underlying news license is granted here.

## Known limits

Human semantic validation and entity standardization remain unfinished. Automatic English checks do not verify fidelity to original language sources. Translated summaries can omit context, and missing time-specific incumbent metadata makes strict responsibility attribution difficult. A frozen aggregate reproduction is auditable but cannot independently recreate the underlying LLM annotations without controlled source access and the complete run environment.
