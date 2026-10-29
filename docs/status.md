# Project status

Updated October 29, 2026. Counts below refer to the dated data snapshot, not live processing totals.

## Available work

| Component | Current state |
|---|---|
| Corpus | Articles collected across 71 countries and international/regional sources. Processing of the January 2012–June 2026 target period is incomplete. |
| Coding framework | One selected action, actor, target, and national incumbent government per article; separate alignment, reputation, and framing labels. |
| Prompt | Complete October 20 version, with coding rules and synthetic calibration examples. Earlier versions remain distinct. |
| Aggregate data | 542,981 valid complete-prompt records for January 2025–May 2026, with monthly coverage and missing-value counts. |
| Reproduction | A script that checks the frozen data and regenerates summary tables. |
| Preliminary review | Mechanical checks, independent storage verification, and two exploratory AI reviews of 30 and 40 records. |
| Documentation | Codebook, data description, validation plan, research design, and bibliography. |

The broader processing pipeline is maintained separately. The public code currently reproduces aggregate tables; it does not run collection, translation, model inference, or database storage.

## Remaining work

| Task | What is needed |
|---|---|
| Human validation | Independent coding of a documented sample, comparison before adjudication, and field-specific error estimates. |
| Translation review | Paired original-language and supplied-English checks for missing content, attribution, negation, and actor relationships. |
| Government and entity identification | Date-specific incumbent information and a versioned crosswalk for actor and institution names. |
| Joint label analysis | Article-level combinations of alignment, reputation, and framing, with nulls retained. |
| Comparable outlet analyses | Source/government/month tables, stable outlet panels, and sensitivity to different weighting choices. |
| Media institutions | Dated ownership and regulatory measures, with a defined comparison strategy. |
| Citizen attitudes | Exposure and survey or experimental data if the research is extended to audience effects. |
| Data releases | Documented versions as processing and validation advance. |

## Interpretation

Current percentages describe the processed article sample. They are not accuracy estimates or measures of societal polarization. A high zero share can reflect neutral reporting, mixed evidence, insufficient context, or conservative coding. A negative reputation label can reflect an unfavorable event without critical wording from the narrator.

The [validation documentation](validation.md) separates completed checks from proposed evaluation. The [research design](research-design.md) describes the evidence required for the substantive comparisons.
