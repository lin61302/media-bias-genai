# Monthly polarization scores

[Download the CSV](https://raw.githubusercontent.com/lin61302/media-bias-genai/main/data/polarization/monthly_polarization_all_countries.csv).

One row per **evaluated-government country/territory and month**, sorted by country code and then month. The file covers **January 2021–May 2026**, with 65 months for each of 205 codes (13,325 rows). It uses the fixed November 4, 2026 analysis snapshot: 2,440,312 eligible articles and 9,449 country-months with at least one eligible article. Months without eligible records remain present with zero eligible articles and **blank scores**, not zero polarization.

Country refers to the government being evaluated, regardless of where the article was published. These are coded country/territory identities, not 205 independently sampled national media systems. Some codes have very sparse coverage or need entity review. The same country series may span a change of incumbent.

## Which score to use

The three score columns apply Erik's proposed formula separately:

`P = 4 × negative_share × positive_share`

| Column | What the two directions mean |
|---|---|
| `polarization_alignment` | Actions opposing versus supporting the incumbent government |
| `polarization_reputation` | Unfavorable versus favorable implications for the government's reputation |
| `polarization_framing` | Critical versus favorable evaluation in the title or narrator's wording |

For a question about **pro- and anti-incumbent actions**, start with `polarization_alignment`. Reputation and framing answer different questions; the file does not combine them into one score.

Each score ranges from 0 to 1. It reaches 1 for equal positive and negative shares without zero-coded articles. It is 0 when either directional side is absent, including an all-zero or entirely one-sided sample. Zero-coded articles remain in the denominator, so the score accounts for both the nonzero share and directional balance. Zero includes neutral, mixed and insufficient directional evidence. This is a proposed coverage statistic, not a validated measure of public polarization.

## Columns and denominators

| Columns | Definition |
|---|---|
| `government_country_code`, `government_country_name` | Evaluated government country/territory; project three-letter codes include conventions such as XKX |
| `month` | Publication month, `YYYY-MM` |
| `eligible_articles` | Number of articles with an identified government and primary action and all three labels codable as −1, 0, +1 |
| `polarization_*` | Proposed score using the formula above |
| `*_nonzero_share` | `(negative count + positive count) / eligible_articles` |
| `*_negative_share`, `*_zero_share`, `*_positive_share` | Fractions on the same eligible denominator; sum to 1 when articles are present |
| `*_net` | Positive share minus negative share, ranging from −1 to +1 |
| `coverage_status` | `no_eligible_articles`, `under_100_articles`, or `at_least_100_articles` |

Shares are fractions (0–1), not percentages. All numerical precision is retained. The 100-article flag is a convenient filter, not a validated precision threshold. No small groups are silently dropped. Absence of eligible records does not establish absence of news in the underlying corpus.

Each country-month pools its eligible articles across sources. It is **not** an average of outlet-specific polarization scores, and sources with more articles receive more weight. Do not sum monthly scores or average them to obtain an annual score; pool the underlying counts/shares weighted by `eligible_articles` and recalculate the formula. Repeated event coverage, source composition, translation and coding errors limit interpretation. Missing/unidentified governments and uncodable labels are excluded, not treated as political categories.

## Use

Filter to `month >= "2022-01"` to match the dashboard's default period. Retain 2021 to use the full available frozen window. The later production pipeline may have additional records; this file does not silently update to them. June 2026 uses an earlier prompt at this snapshot and is excluded.

```r
d <- read.csv("monthly_polarization_all_countries.csv", na.strings = "")
senegal <- subset(d, government_country_code == "SEN")
senegal$polarization_alignment[senegal$eligible_articles < 100] <- NA
plot(as.Date(paste0(senegal$month, "-01")), senegal$polarization_alignment,
     type = "b", xlab = "Month", ylab = "Alignment polarization (0–1)", ylim = c(0, 1))
```

To reproduce using Node.js 18 or later, from the repository root:

```sh
node scripts/export_monthly_polarization.mjs
node scripts/export_monthly_polarization.mjs --check
```

Only public, commit-pinned aggregate files are downloaded and their SHA-256 hashes checked. No model calls, credentials, article texts or database access are required. [export_manifest.json](export_manifest.json) records the source hashes, prompt, audit cutoff, counts and output hash. The [analysis snapshot](../analysis_snapshot.json), [measure definition](../../docs/coverage-balance.md), [notebook](../../notebooks/01_dashboard_and_measures.ipynb) and [data card](../../docs/data-card.md) provide further detail. The older notebook country-month table remains unchanged and uses the narrower 2022-start window and one row per measure.
