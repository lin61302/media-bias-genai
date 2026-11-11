# Media freedom and domestic coverage

This comparison asks whether the patterns in negative coverage remain when a news source evaluates **its own country's national government**. Domestic means that the record's `publication_country` equals its evaluated-government code, `gov`. Publication country describes source origin; it does not establish ownership or editorial control.

## Figures and data

- [Domestic-only plot](../slides/figures/16_media_freedom_domestic.png) ([SVG](../slides/figures/16_media_freedom_domestic.svg))
- [All-origin and domestic plots on matching scales](../slides/figures/16_media_freedom_scope_comparison.png)
- [Country-month counts, all signs](../slides/figures/data/16_media_freedom_country_month.csv)
- [Monthly plotted values](../slides/figures/data/16_media_freedom_monthly_series.csv), [country participation](../slides/figures/data/16_media_freedom_contributing_countries.csv), and [fixed groups](../slides/figures/data/16_media_freedom_groups.csv)
- [Comparison using identical country-months](../slides/figures/data/16_media_freedom_same_support.csv)
- [Extraction verification](../slides/figures/data/16_media_freedom_extraction_provenance.json) and [calculation manifest](../slides/figures/data/16_media_freedom_manifest.json)

The three panels report negative political alignment, negative reputational implication, and negative framing separately. Zero and positive labels remain in each denominator.

The comparison uses **January 2022–December 2025**, with the **November 4, 2026** frozen data release. It does not include subsequently processed articles.

## Findings

The main ordering remains after restricting coverage to domestic sources evaluating their own government. The high-freedom group has the largest average negative alignment and reputational-implication shares; the low-freedom group has the largest negative-framing share.

| Fixed freedom group | Negative alignment | Negative reputational implication | Negative framing |
|---|---:|---:|---:|
| Low | 7.89% | 10.71% | 7.23% |
| Middle | 7.03% | 7.76% | 4.37% |
| High | 10.61% | 13.09% | 6.13% |

These summarize the **48 monthly equal-country means**, not pooled article shares. The low-freedom group's negative-framing mean is highest in **42 of 48 months**, compared with 46 months in the all-origin reconstruction. Domestic coverage contributes **1,650,617 articles across 3,282 country-months** after the threshold; the all-origin reconstruction contributes 1,742,969 articles across 3,299 country-months.

On the same 3,282 country-months, restricting to domestic sources lowers average negative framing by **0.76 percentage points for the low group, 0.68 for the middle group, and 0.44 for the high group**. The ordering persists. Foreign and international reporting therefore do not fully account for the low group's higher framing share in this corpus. This does not identify which remaining political, editorial or collection differences explain it.

## Reproduction

With Python, pandas, NumPy and matplotlib installed, run from the repository root:

```sh
python scripts/build_domestic_media_freedom.py --fetch-inputs
```

The optional flag obtains missing, hash-pinned public country context and source metadata. With those files cached, omit it to run fully offline. `--check-only` validates the counts without writing figures. No model or database calls are made.

The input is a new aggregation of two verified, non-overlapping November 4 caches. All 27 joint-label counts match every one of the 9,449 nonempty country-month profiles in the original January 2021–May 2026 export. The plotting script additionally checks all 71 × 48 plotted-universe cells against the existing public CSV. The count export includes 205 evaluated-government codes; the figures select the fixed 71-country universe below. Original article records remain private.

## Calculation

1. Require an identified government and selected action, and numeric `-1`, `0`, or `+1` labels on all three dimensions. Keep valid `other_act` records.
2. Produce counts by evaluated government and publication month for all source origins, then separately for records where publication country equals evaluated government. Unidentified and international (`ALL`) publication origins cannot enter the domestic sample.
3. Require at least **30 eligible articles per country-month**, recalculated after the domestic filter. For each dimension, divide its negative count by the eligible article count.
4. Fix the country universe to the **71 publication countries** in the November 4 source metadata. Average each country's 2022–2025 V-Dem v16 `v2x_freexp_altinf` values and divide these means into terciles. The groups contain **24 low, 23 middle, and 24 high** freedom countries. Keep those assignments fixed when restricting the articles.
5. Within each group and month, average the available country shares equally. A country with more articles does not receive more weight. The number of contributing countries can change each month.
6. Show the monthly means as thin lines and a centered three-calendar-month mean as thick lines. Smoothing requires all three months; it is absent at the first and last month and across gaps.

The V-Dem variable measures *Freedom of Expression and Alternative Sources of Information*. The cached country-year entries use the last dated observation in each year; the grouping averages the four annual entries.

## Comparability

The reconstructed country groups exactly match the sizes and rounded score ranges in Erik Wibbels's supplied figure. His original plotting code was not available, so this is a documented reconstruction rather than an assertion that every plotting choice matches his code. The original image is preserved separately.

Restricting to domestic coverage can both change a country's article mix and push its monthly count below 30. The supporting comparison therefore also holds the set of country-months fixed to those that meet the domestic threshold. This separates changes in country-month inclusion from changes in article composition. It still does not hold source, event or article genre constant.

These are descriptive patterns in the collected and model-coded corpus. They do not establish that press freedom causes the differences, that negative framing represents an outlet's overall bias, or that an unobserved article was censored. Comparing similar actions and matched events, checking news versus opinion coverage, and validating the labels remain separate tasks.
