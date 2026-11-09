# A proposed two-sided coverage index

Erik's draft defines `P = 4 p⁺ p⁻`, where the shares refer to positive and negative labels for one measure, in a specified group and period. The [notebook](../notebooks/01_dashboard_and_measures.ipynb) calculates this candidate separately for alignment, reputational implication and framing. It is not yet a validated measure of societal polarization.

Because `p⁺ + p⁻ + p⁰ = 1`, the same expression is `(1 − p⁰)² − (p⁺ − p⁻)²`. It combines how much coverage is directional with how evenly the two directions are represented. For a fixed zero share, it is largest when positive and negative shares are equal. It ranges from 0 to 1. It is zero whenever either directional share is zero.

| Negative | Zero | Positive | Net | P | Interpretation |
|---:|---:|---:|---:|---:|---|
| 0% | 100% | 0% | 0 | 0 | All zero-coded |
| 0% | 0% | 100% | 1 | 0 | Entirely positive |
| 50% | 0% | 50% | 0 | 1 | Balanced directional coverage |
| 10% | 80% | 10% | 0 | 0.04 | Balanced but mostly zero-coded |

Always show the three shares, net score, P and article count together. The first and second rows have identical P but very different coverage. A high zero share suppresses P, and zero includes neutral, mixed and insufficient directional evidence. Excluding zeros instead would define a different, conditional statistic and could make a handful of directional records look highly polarized.

The proposal in the draft still needs comparison with the cited polarization literature. This repository does not assert that the formula is a validated implementation of Esteban–Ray polarization. Label order, equal spacing and the meaning of zero require substantive justification.

Pooled country-level P can be high because individual outlets disagree, because each outlet contains opposing coverage, or because events change within the period. These mechanisms require separate comparisons. Article volume is not the number of independent events; simple article-level standard errors would not capture repeated coverage and source dependence.

Government identity is date-dependent. For example, a country series spanning a change of incumbent uses a changing political reference. Lag/lead comparisons with annual democracy indicators also require a country-year design, consistent source coverage, temporal ordering and validation. A fixed-year cloud color cannot establish that relationship.


## Directional share, balance and source disagreement

We can separate three descriptive questions. For each measure, government and period, let `n` be the eligible article count and retain all three sign counts.

| Question | Summary | What it describes |
|---|---|---|
| How often is the code directional? | `S = p⁺ + p⁻` | Prevalence within eligible coverage. Show `nS`, the directional count. |
| Which direction predominates? | `N = p⁺ − p⁻`, plus both sign shares | Net direction. Opposing signs can cancel. |
| How balanced are the directional labels? | `B = 4q(1−q)`, `q = p⁺/S`, for `S > 0` | Balance conditional on having a directional label. |
| Are both directions common in the full sample? | `P = 4p⁺p⁻ = S²B` for `S > 0` | A combination of prevalence and conditional balance. |

`B` is undefined when `S = 0`; `P` is still zero. B ranges from zero for one sign only to one for equal positive and negative shares. A high B can rest on very few articles, so always show its directional count. A high correlation of P with S can reflect limited variation in B; it does not by itself establish poor classifier sensitivity. S describes directional prevalence in this selected civic corpus, not issue prominence or national-news salience. Article volume answers a separate coverage question.

The optional synthetic illustration retained in `slides/includes/polarization.qmd` uses 100 articles in each case. It is not displayed in the current condensed deck:

| Negative | Zero | Positive | S | N | B | P |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 100 | 0 | 0 | 0 | undefined | 0 |
| 60 | 40 | 0 | .60 | −.60 | 0 | 0 |
| 5 | 90 | 5 | .10 | 0 | 1 | .01 |
| 30 | 40 | 30 | .60 | 0 | 1 | .36 |

For **between-source disagreement**, compare each outlet's sign distribution toward the same government over common periods and, where possible, the same events and genres. Report within-source balance separately. A pooled index can hide that every outlet is individually one-sided. Distances between outlet distributions or between their net scores can be explored, but event composition, source weights, repeated stories and coding error need sensitivity checks. These comparisons are a proposed analysis, not an additional validated index already calculated here.

Actor/action patterns can show which groups are reported supporting or opposing the incumbent and whether actions target government institutions or third parties. They do not establish reciprocal alliances, ideological distance, the size of political camps, or how citizens feel about one another. External survey, party-position or conflict evidence is needed to validate a societal-polarization interpretation. Generic entropy or dispersion over all three labels would also depend on treating the heterogeneous zero category as a comparable substantive position.
