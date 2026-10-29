# Research design

## Research questions

The project studies how news reporting represents actions involving national governments. It distinguishes an action's political direction, its reputational implication for the incumbent, and the article's evaluative language. The aim is to examine how these dimensions vary across sources, political settings, and time.

| Dimension | Operational meaning | Interpretation limit |
|---|---|---|
| `align` | Direction of the selected actor's action toward the national incumbent: support, opposition, or no clear direction | Does not measure ideology or moral approval |
| `rep` | Implication of the same action and directly tied facts for the incumbent's performance or legitimacy | Does not measure public opinion or establish the truth of an allegation |
| `frame` | Observable incumbent-favoring or incumbent-critical evaluation in the title or narrator's voice | Does not capture all framing, selection, omission, or factual accuracy |

The reference is the national incumbent at publication time. Institutional role, incumbent membership, government responsibility, and political direction are separate judgments. A local conflict may have no supported direction toward the national government. An independent court can challenge an incumbent without belonging to it.

The codebook's `0` category includes no supported direction, mixed evidence, and insufficient directional evidence. `null` means the dimension cannot be coded. Neither is a confidence score. See the [codebook](codebook.md) for the action-selection and evidence rules.

## Political interpretation

An action that supports an incumbent can harm its legitimacy. An adverse event can also be reported without critical editorial language. Separating these judgments helps distinguish the events being reported from their treatment in the article.

A synthetic example in the prompt illustrates the distinction: cabinet-affiliated police disperse explicitly peaceful anti-government demonstrators. The action supports the incumbent (`align = +1`) and has an adverse reputational implication (`rep = -1`). A descriptive account can have `frame = 0`; narration endorsing the operation can have `frame = +1`. This is a constructed example, not an observation from the corpus.

Several mechanisms could explain differences in coverage:

- **Government influence and ownership.** Media-capture theory describes how government influence can affect news without formal censorship ([Besley and Prat, 2006](https://www.aeaweb.org/articles?id=10.1257/aer.96.3.720)). Government control and ownership can also create different editorial incentives ([Gehlbach and Sonin, 2014](https://doi.org/10.1016/j.jpubeco.2014.06.004)).
- **Audience demand.** Reader preferences can shape slant, alongside ownership and editorial decisions ([Gentzkow and Shapiro, 2010](https://doi.org/10.3982/ECTA7195)). Favorable incumbent coverage alone therefore does not identify government capture.
- **Audience selection and media effects.** Evidence from Italy links changes in public television news after a change in government to viewers switching programs ([Durante and Knight, 2012](https://doi.org/10.1111/j.1542-4774.2011.01060.x)). Studies of voting in the United States and Russia use variation in access to television, beyond article content, to estimate effects ([DellaVigna and Kaplan, 2007](https://doi.org/10.1162/qjec.122.3.1187); [Enikolopov, Petrova and Zhuravskaya, 2011](https://www.aeaweb.org/articles?id=10.1257/aer.101.7.3253)).

These studies motivate hypotheses and research designs; they are not findings about this corpus. The project has no current estimate of audience exposure, opinion change, electoral effects, or societal polarization. Research on polarization would need a defined outcome, such as ideological distance or hostility toward political opponents, and suitable audience measures.

The reasonable-observer standard for `rep` involves judgments about competence, accountability, legality, and rights. Cross-country validation must examine how consistently reviewers apply that standard and where political viewpoints produce disagreement.

## Units and descriptive targets

The coding unit is one supplied article record with one prioritized government-relevant action and one evaluated national government. The title and lead guide action selection. An article may contain other actions, and repeated coverage can give a real-world event multiple records. `align` and `rep` concern the selected action; `frame` concerns observable narration in the supplied text.

The current aggregate snapshot contains **542,981 structurally valid, independently verified stored outcomes** using the complete prompt, covering **January 2025–May 2026**. Its storage cutoff is **October 29, 2026, 05:20:31 UTC**. This is a processed subset of the broader project corpus, not a probability sample of all news or events. The [data card](data-card.md) records inclusion rules, coverage, and denominators.

Four distinct quantities guide the analysis:

1. **Observed-corpus label shares:** the proportion of records with each label, including `0` and `null`. The current marginal tables support this calculation.
2. **Within-source and within-government composition:** label shares by source, evaluated government, and publication month, with cell sizes and processing coverage. These tables remain to be extracted.
3. **Differences within matched events:** differences in `frame` among articles reporting the same event within a defined period, after checking that they select the same action. This comparison remains proposed.
4. **Coverage choice:** whether an outlet covers a defined event opportunity. This requires an external event frame or a bounded union of observed coverage. A missing scraped article cannot automatically be classified as editorial omission.

Every proportion needs an explicit denominator. Shares among all valid outputs, non-null records, and directional records answer different questions. Publication-country memberships can overlap and differ from the single evaluated-government country.

## Competing explanations

| Pattern | Possible explanations | Evidence needed |
|---|---|---|
| More adverse than favorable `rep` | Adverse events, watchdog reporting, selective coverage, source composition, coding or translation error | Event and topic mix, stable source panels, paired text review, representative validation |
| Favorable `frame` | Government pressure, ownership incentives, audience demand, editorial preferences, event mix | Dated ownership and control measures, audience data, matched events, validated labels |
| Many `0` labels | Routine reporting, national-government scope, mixed evidence, missing affiliations, partial translations, conservative coding | Input and government-identity checks, review of label decisions |
| Changes around an election | Changed events or officeholders, source entry and exit, editorial adaptation, processing composition | Tenure dates, stable outlets, consistent prompts, event matching, coverage checks |
| Differences across countries | Institutions, media systems, corpus selection, source volume, language error | Comparable source panels and periods, subgroup validation, alternative weighting |

## Analyses requiring additional work

The available marginal tables describe label distributions. Joint `align × rep` and `rep × frame` tables, government–source–month summaries, and action-type distributions require further aggregate extraction. Each analysis needs a dated cohort, explicit inclusion rules, and processing-coverage measures.

Comparisons across sources and governments also need human validation, stable-source panels, and sensitivity to article, source, and government weighting. Matched-event comparisons require manual checks that articles concern the same event and selected action.

Ownership or control studies would need dated external data and a separate identification strategy. Endogenous acquisition, simultaneous political changes, and source survival remain potential confounders. These studies are possible extensions, not completed project results.

## Interpreting media bias

The `frame` variable measures a narrow form of evaluation. Research on media bias distinguishes distortion from filtering or selection and requires a comparative benchmark ([Gentzkow, Shapiro and Stone, 2014](https://www.nber.org/papers/w19880)). An outlet can select adverse events while describing them without evaluative language, or omit adverse events without using favorable adjectives. `frame = 0` therefore does not establish that an article or outlet is unbiased.
