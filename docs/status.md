# Project status

Updated November 4, 2026. Analysis counts are fixed at the dated storage audit; processing continues separately.

| Component | Available evidence |
|---|---|
| Coding | Complete prompt, codebook and separate action alignment, reputational implication and article framing labels |
| Fixed analysis | January 2022–May 2026: 2,157,912 valid records and 1,984,402 eligible comparisons; optional 2021-start window |
| Relationships | Joint three-label counts, correlations, actor/action/target comparisons and government/outlet groups |
| Time | Monthly series, prior-three-month changes, common-outlet comparisons and action/actor contribution toggles |
| Context | Region/subregion and V-Dem country-year indicators; five sourced event accounts, without article-level event matching |
| Reproduction | Commit/hash-pinned aggregate manifest; executed notebook, exported figures and calculated tables; historical October 29 summaries retained |
| Review | Structural/storage checks, earlier small AI reviews and a November 2 comparison on 266 previously human-coded articles (262 structurally valid); no representative human-reference accuracy estimate |

The [dashboard guide](dashboard-guide.md) explains every view and its denominators. The [notebook](../notebooks/01_dashboard_and_measures.ipynb) reproduces selected findings and the exploratory [coverage-balance index](coverage-balance.md).

## Remaining research work

- Independent human validation of the three separate constructs on the exact supplied input, with a documented sampling design.
- Bilingual source/translation review and error analysis by country, source and label.
- Date-specific incumbent references and standardized named entities; coded actor roles are not resolved individuals.
- Stable source panels, matched-event comparisons and sensitivity to article versus outlet weighting.
- A justified and validated interpretation of the proposed two-sided index before treating it as polarization.
- Country-year research designs for institutional comparisons; fixed-year cloud colors do not supply lag/lead or causal evidence.
- Dated ownership/regulation data for media-institution questions, and audience data for attitude effects.

The public code reproduces aggregate calculations. It does not run collection, translation, model inference or database storage. Processing status is maintained separately; the historical inventory, current stored totals and eligible analysis sample must remain distinct.
