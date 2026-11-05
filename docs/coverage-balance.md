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
