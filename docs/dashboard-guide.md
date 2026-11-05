# Reading the dashboard

[Open the dashboard](https://zungru-media-bias-reported-polarization.static.hf.space/index.html#cloud). The [executed notebook](../notebooks/01_dashboard_and_measures.ipynb) reproduces the calculations and exports figures from a fixed public snapshot. No model or database access is required.

## Two different time controls

**Article period** selects which news records enter every analysis tab. The default is January 2022–May 2026. An individual year or the January 2021–May 2026 window can be selected.

**External indicator year (V-Dem)** selects the country values used by a democracy or expression/information axis or color. It does not filter news articles. For example, articles from 2022–2026 colored by 2025 democracy compare a multi-year news profile with one institutional snapshot. This is useful for describing countries in a common reference year, but is not a contemporaneous country-year analysis.

For a same-year comparison, choose Article period = 2024 and External indicator year = 2024. Selecting an article period initially sets the indicator year to that period's final year, capped at 2025. Changing the indicator year afterward leaves the article period untouched. The indicator control is hidden when the current plot does not use it. Region and subregion are geographic categories and do not use an indicator year.

The release contains V-Dem v16 country observations for 2021–2025, using the last dated observation in each year. No observed 2026 score is supplied. A 2026 article comparison uses 2025 as an explicitly labeled reference, not as a measured 2026 value. Monthly democracy-band comparisons elsewhere in the dashboard use the article year, with 2025 carried forward for 2026; this differs from the fixed-year cloud control.

## What a point represents

| Plot element | Meaning |
|---|---|
| Government point | All eligible articles evaluating that government's country in the selected article period; not necessarily articles published there |
| Outlet point | All eligible articles from that source domain in the selected period, potentially evaluating several governments |
| Country color for a government | Attributes of the evaluated government's country |
| Country color for an outlet | Attributes of the outlet's publishing country; mixed, international or missing country assignments are not given an invented country score |
| Direct label axes | Mean/net label, negative share, or positive share, according to the statistic control |
| Label color | The **mean** label, even when the axes display shares |
| Institutional axes/color | The selected V-Dem indicator; not GPT-generated labels |
| Similarity axes | A two-dimensional projection of differences in five distributions: alignment, reputation, framing, actor role and action family |
| Similarity groups | Exploratory clusters fitted to the full five-field profiles, not political camps or validated regime types |

Zero remains in label denominators. Mean/net = positive share minus negative share, ranging from −1 to +1. Share axes range from 0 to 1. A mean near zero can result from many zero labels or offsetting directional labels; inspect the distribution.

## What point size means

The default size represents the **number of eligible articles in that point**, not population, audience, distinct events, effect size or confidence. Hover, click, or open the point list for the exact count. Minimum eligible articles removes small groups from view without changing other groups' statistics.

Size is deliberately compressed. In SVG coordinates, radius = `4 + min(12, sqrt(n)/30)`. It reaches its cap at **129,600 articles**. Circle area is **not proportional** to article count, and groups above the cap look equally large. The visible legend shows 500, 5,000, 50,000 and 129,600+ articles. Choose **Equal size** for a constant radius of 6 when comparing positions without visual emphasis on volume. Browser resizing can scale these SVG units on screen.

Direct comparison counts require an identified government and primary action and all three labels codable as −1, 0 or +1. Similarity plots additionally require identified actors and an action assigned to a substantive action family. Their point sizes can therefore be smaller. Similarity maps were fitted to groups with at least 200 eligible records; raising the visible threshold or filtering regions does not refit the projection or clusters. The displayed retained-variation percentage describes the two plotted components, not classification accuracy.

## Other tabs

| Tab | How to read it |
|---|---|
| Findings | Selected descriptive comparisons, with denominators and follow-up checks; not an exhaustive or pre-registered set of results |
| Relationships | Article-level 3×3 joint counts and Pearson correlations using numeric −1, 0, +1 labels; a correlation of group means in a cloud is a different statistic |
| Trends & spikes | Monthly shares or net scores; change compares the current month with the pooled previous three calendar months, within the selected article period |
| Contributors | Check specific action types or actor roles to plot their contribution to the overall monthly measure. Unknown, unclassified and “other” choices are excluded from rankings, but their article counts remain in the overall denominator and are disclosed separately |
| Actors & actions | Coded roles and action categories, not standardized named-person networks. A target role is the recipient of the action; the evaluated government is the reference for the political labels |
| Governments & outlets | Sources reporting on the same evaluated government. Common-source/year/action checks reduce some composition differences, but do not match identical events or articles |
| Coverage & missing | Valid and eligible counts, null labels, unidentified groups and processing coverage; missing cases are not substantive political categories |

For a negative share, an action's contribution is its negative-coded article count divided by **all** eligible articles in that group-month. Contributions add across a complete action partition. Actor contributions form a separate partition and must not be added to action contributions. The “change” ranking subtracts the corresponding pooled baseline contribution. It can change because the action is more common, more often negative, or both. It is not a causal attribution.

Same-outlet checks compare common outlets and use equal outlet weights. They answer a different question from pooled article-weighted changes. Missing months are not zero-filled. A selected spike is a lead for investigation and can reflect source composition, volume, government transitions, coding error or an event.

Story cards connect selected country-month patterns to sourced accounts of who did what. Those sources have not been matched article by article to the analysis corpus. Their dates and mechanisms supply context, not proof that the event caused the measured change. Action families are not inferred topics; corpus-wide topic extraction is not part of this release.

## Scope and interpretation

The fixed November 4, 2026 audit contains **2,157,912 valid records** and **1,984,402 eligible comparisons** for January 2022–May 2026. The optional 2021-start window contains 2,654,346 valid and 2,440,312 eligible records. All use one complete prompt. June uses an earlier prompt at this cutoff and is excluded. The processing dashboard can advance while this analysis remains frozen.

These are distributions of model-coded news records. They do not measure public approval, audience polarization, causal media effects or verified outlet ideology. A critical event can hurt a government's reputation without critical narrator wording; `frame = 0` does not establish unbiased reporting. Repeated event coverage, translation, source selection, missing data and incomplete semantic validation limit comparisons. See the [data card](data-card.md), [codebook](codebook.md) and [validation plan](validation.md).

Country-region mappings follow UN M49 with explicit project conventions for Kosovo and Taiwan. V-Dem data and adaptations are attributed and distributed under CC BY-SA 4.0; source URLs and hashes are retained in the pinned `country_context.json` in [the snapshot manifest](../data/analysis_snapshot.json).
