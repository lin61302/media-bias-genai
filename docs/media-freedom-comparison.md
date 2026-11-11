# Media freedom and domestic coverage

This comparison asks whether the patterns in negative coverage remain when a news source evaluates **its own country's national government**. Domestic means that the record's `publication_country` equals its evaluated-government code, `gov`. Publication country describes source origin; it does not establish ownership or editorial control.

## Figures and data

- [Domestic-only plot](../slides/figures/16_media_freedom_domestic.png) ([SVG](../slides/figures/16_media_freedom_domestic.svg))
- [All-origin and domestic plots on matching scales](../slides/figures/16_media_freedom_scope_comparison.png)
- [Positive domestic coverage](../slides/figures/17_media_freedom_positive.png), [negative and positive shares on matching scales](../slides/figures/17_media_freedom_sign_comparison.png), and [all nonzero coverage](../slides/figures/17_media_freedom_directional.png)
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

### Country composition matters

The framing contrast is **sensitive to Nicaragua's sampled coverage**. Nicaragua's mean monthly negative-framing share is **54.05%**, with 5,335 eligible domestic articles and all 48 months above the threshold. Each eligible country receives equal monthly weight, so a country with fewer articles can materially affect its group's mean.

Removing Nicaragua as a diagnostic reduces the low group's average from **7.23% to 5.16%**, below the high group's unchanged **6.13%**. The low group then has the highest framing mean in only **3 of 48 months**. This is not a reason to exclude Nicaragua or assume a coding error. It demonstrates that the displayed average does not describe a pattern shared by most low-freedom countries.

The [country summaries](../slides/figures/data/16_media_freedom_country_sensitivity.csv) and [leave-one-country-out checks](../slides/figures/data/16_media_freedom_leave_one_country_out.csv) reproduce this diagnostic across all 71 countries. Run `python scripts/check_media_freedom_country_sensitivity.py` to rebuild them. The groups remain fixed; removing a country never reallocates the others to different terciles.

### Nicaragua's outlets

The [outlet counts](../slides/figures/data/18_nicaragua_outlet_counts.csv) and [outlet-month counts](../slides/figures/data/18_nicaragua_outlet_month_counts.csv) use the same frozen caches, period and eligibility as the domestic figure. All 48 Nicaragua months exceed the 30-article threshold. The six largest outlets appear on the slide; the other two contribute 36 articles.

| Outlet | Eligible articles | Negative framing | Positive framing |
|---|---:|---:|---:|
| Artículo 66 | 1,832 | 71.4% | 0.2% |
| La Prensa | 1,445 | 54.3% | 0.3% |
| Confidencial | 988 | 65.1% | 0.0% |
| Onda Local | 233 | 70.8% | 0.0% |
| Nueva Radio Ya | 473 | 0.0% | 17.3% |
| Canal 2 | 328 | 0.0% | 8.5% |

These are pooled article percentages, including zero-coded labels in the denominator. The displayed group lines instead average countries within each month. The table is not a census of each outlet's published output. Artículo 66, La Prensa and Confidencial supply 79.94% of Nicaragua's eligible articles and 94.05% of its negative-framing labels. Nicaragua's national mean is 54.05% across months, or 54.53% pooling its articles. Including Nicaragua changes the low group's period-average line from 5.164% to 7.226%, a 2.062 percentage-point difference.

The country code does not necessarily locate the newsroom: UNESCO documents La Prensa's mostly exiled staff, and RSF documents Confidencial director Carlos Chamorro's exile. Low national media freedom can coexist with independent journalism produced abroad. This supports investigating exile and outlet composition; it does not establish their causal contribution to these particular rates. [UNESCO, May 2025](https://www.unesco.org/en/articles/nicaraguan-newspaper-la-prensa-wins-unesco/guillermo-cano-world-press-freedom-prize-2025); [RSF, June 2025](https://rsf-es.org/nicaragua-el-exilio-es-la-unica-forma-de-supervivencia-para-el-periodismo-independiente/).

Nueva Radio Ya's own account of organizing Ortega's birthday celebration documents supportive positioning. It does not by itself establish state ownership. [Outlet account, November 2024](https://nuevaya.com.ni/destacadas/tu-nueva-radio-ya-y-el-pueblo-dedican-serenata-a-comandante-daniel-ortega-en-su-cumpleanos-79/).

### How unusual is Nicaragua?

The following distribution gives each country one value: its average monthly negative-framing share across qualifying months. It describes variation **between countries**, not changes over time or uncertainty intervals. Ten countries have fewer than 48 qualifying months; Timor-Leste has only one.

| Freedom group | Countries | Median country | Middle 50% of countries | Highest country rate |
|---|---:|---:|---:|---:|
| Low | 24 | 3.01% | 1.78–6.02% | Nicaragua: 54.05% |
| Low, excluding Nicaragua | 23 | 2.72% | 1.74–5.81% | Zimbabwe: 22.91% |
| Middle | 23 | 3.31% | 2.14–4.47% | Cameroon: 18.88% |
| High | 24 | 5.04% | 3.26–7.58% | Liberia: 14.00% |

Elevated rates occur in every group. Ethiopia (18.31%) and Uganda (16.47%) are further low-group cases; Malawi (13.96%) and Zambia (12.35%) are high-group cases. These examples have 48 qualifying months except Ethiopia (47). The groups' central ranges overlap; the middle group is narrower, while the low group has a much longer upper tail. Nicaragua is exceptional rather than representative of the typical low-freedom country. Group membership is relative to these 71 source countries, not a universal categorical judgment about regimes.

Run `python scripts/check_nicaragua_outlets.py` to verify the extraction hashes, reconcile all outlet-month counts with the original country-month export, and regenerate the [comparison summary](../slides/figures/data/18_nicaragua_comparison.json). The [extraction receipt](../slides/figures/data/18_nicaragua_provenance_and_summary.json) retains original filenames; delivered files use the `18_nicaragua_` prefix instead of `nic_`, with identical contents and hashes. No model or database calls are needed.

### Interpretation

Higher negative alignment means more articles about actions opposing the incumbent, not more criticism by journalists. Higher negative reputational implication means more selected actions coded as reflecting badly on the government, not worse measured government performance. Negative framing concerns critical language in the title or narration.

Consequently, a source can report an opposition action or damaging government conduct without adding its own critical evaluation. Another article can use critical language without selecting an action coded as opposing the government. These separate objects explain why the three shares need not move together. The graph does not hold the reported event or action constant.

One hypothesis is that sampled outlets in different settings differ in their mix of routine reporting and explicit criticism. Another is that the sources, article sections or stories collected differ. Both remain hypotheses. The country sensitivity points to inspecting particular countries and outlets before interpreting the pattern as a feature of their broader media environments. The middle group also has the lowest framing share, so the three-group pattern is not a monotonic relationship between freedom and criticism.

## Positive coverage and the amount of directional coverage

The positive figures use exactly the same domestic country-months, denominators, fixed freedom groups and averaging as the negative figures. A positive label means an actor's action supports the incumbent (`align`), has favorable reputational implications (`rep`), or the evaluated government is framed favorably in the title or narration (`frame`). Positive alignment is not the journalist's endorsement.

| Positive share | Low freedom | Middle freedom | High freedom |
|---|---:|---:|---:|
| Political alignment | 7.89% | 5.84% | 8.42% |
| Reputational implication | 4.52% | 3.45% | 4.04% |
| Framing | 3.73% | 2.72% | 3.34% |

These summarize the 48 monthly equal-country means. Relative to the low group, the high group has more positive **and** negative alignment. Its higher negative-reputation share is not accompanied by a higher positive-reputation share. For framing, both signs are somewhat more common in the low group. These are differences in observed coded coverage; they are not significance tests or population estimates of all national media.

To distinguish less directional coverage from a change in direction, use `S = positive share + negative share = 1 - zero share`:

| Either-sign share S | Low freedom | Middle freedom | High freedom |
|---|---:|---:|---:|
| Political alignment | 15.78% | 12.87% | 19.03% |
| Reputational implication | 15.23% | 11.21% | 17.13% |
| Framing | 10.95% | 7.09% | 9.46% |

The middle group has the lowest period-average S on all three dimensions. The high group has the most directional alignment and reputation coverage; the low group has the most directional framing in the full sample. Country composition still matters: removing Nicaragua changes low-group positive framing only from **3.73% to 3.78%**, while its negative framing falls to **5.16%** and its combined S falls from **10.95% to 8.94%**, below the high group's **9.46%**. The modest positive-framing difference is therefore not explained by the same Nicaragua sample that drives the negative-framing contrast.

S measures how often a direction is coded; it does not measure disagreement between outlets or citizens. The separate shares reveal whether both directions appear or one dominates. The supplemental tables also retain `P = 4 × positive share × negative share`, calculated **within each country-month before taking equal-country monthly means**. Multiplying the two group-average shares instead would create a different quantity and can imply two-sided coverage by combining countries with opposing, one-sided patterns. Neither quantity establishes polarization between outlets or among the public.

The [monthly values](../slides/figures/data/17_media_freedom_sign_monthly.csv), [period summaries](../slides/figures/data/17_media_freedom_sign_summary.csv) and [methods manifest](../slides/figures/data/17_media_freedom_sign_manifest.json) accompany the figures. Run `python scripts/build_media_freedom_signs.py` to rebuild them from the frozen local aggregates, without model or database calls.

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
