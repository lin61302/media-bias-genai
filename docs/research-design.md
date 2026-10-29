# Research design: from political reporting to measurable distinctions

**Status: preliminary research design for the November 11, 2026 discussion.** The current outputs describe model coding of supplied article text. They do not yet establish population semantic accuracy, outlet bias, government performance, or effects on public opinion.

## Research question and contribution

When news reports an action involving a national incumbent government, how does the action's political direction differ from its reputational implication and the article's evaluative presentation?

The proposed contribution is an auditable representation that separates these three judgments while retaining the selected action, actor, target, institutional roles and textual evidence. This makes distinctions available for comparative research that a single positive/negative sentiment score would obscure. It is a measurement contribution under evaluation; this release does not claim a first-of-its-kind method or a validated global bias index.

| Dimension | Current operational meaning | What it does not establish |
|---|---|---|
| `align` | Direction of the selected actor's action toward the identified national incumbent: support, opposition, or no clear direction | Actor ideology, moral approval, or a fixed left–right position |
| `rep` | Implication of the same action and directly tied facts for that incumbent's performance or legitimacy, under the codebook's reasonable-observer standard | An observed change in public reputation, approval or trust; whether an allegation is true |
| `frame` | Observable incumbent-favoring or incumbent-critical evaluation in the title or narrator's voice | All forms of framing, editorial intention, source-selection bias, omitted events, ownership effects or factual accuracy |

Use **“reputational implication”** in presentation prose even though the schema field retains its historical name `rep`. Use **“no clear direction”** for 0: the codebook combines neutral, mixed and insufficient-evidence cases. Null means not codable and remains a separate category. Neither is a confidence score.

The reference is the **national incumbent at publication time**. A local protest can be politically important without being directional toward that reference. An independent court can challenge the incumbent without belonging to it. Institutional role, incumbent membership, responsibility and political direction are separate judgments. This scope is a deliberate research choice.

## Why the distinction matters politically

An action that protects an incumbent can harm its legitimacy; an adverse event can be reported without critical editorial language. These are substantive possibilities, not coding contradictions.

The current prompt includes a useful **synthetic** illustration: cabinet-affiliated police disperse explicitly peaceful anti-government demonstrators. Under its definitions, the action favors the incumbent (`align = +1`) and has an adverse reputational implication (`rep = -1`). A descriptive account can have `frame = 0`; narration that calls the operation necessary can have `frame = +1`. These are constructed teaching examples, not observations about a real country.

The broader political motivation concerns accountability and access to information. Media-capture theory gives a mechanism through which government influence can shape news, including without formal censorship ([Besley and Prat, 2006](https://www.aeaweb.org/articles?id=10.1257/aer.96.3.720)). Formal work also distinguishes the incentives associated with government control and ownership ([Gehlbach and Sonin, 2014](https://doi.org/10.1016/j.jpubeco.2014.06.004)). These mechanisms motivate hypotheses; neither is identified by the present coding marginals.

Audience demand is another explanation: research on U.S. newspapers examines how reader preferences and owner identity relate to slant ([Gentzkow and Shapiro, 2010](https://doi.org/10.3982/ECTA7195)). A cross-country project must allow several mechanisms rather than treating favorable incumbent coverage as sufficient evidence of capture.

Effects on citizens require a further research design. Studies of media exposure and voting use evidence beyond article content, such as the introduction of a channel across markets ([DellaVigna and Kaplan, 2007](https://doi.org/10.1162/qjec.122.3.1187)). This project presently has no audience exposure, opinion-change or electoral-effect estimate.

Empirical work outside the United States makes institutions and audience responses central. In Italy, [Durante and Knight (2012)](https://doi.org/10.1111/j.1542-4774.2011.01060.x) document a shift in public television news after the 2001 change in government and viewers switching preferred programs in ways that partly offset that shift in exposure. In Russia, [Enikolopov, Petrova and Zhuravskaya (2011)](https://www.aeaweb.org/articles?id=10.1257/aer.101.7.3253) use geographical differences in access to independent television to study voting in the 1999 parliamentary election. These historically specific studies motivate examining political control, available alternatives and audience selection together. They provide comparative research precedents, not findings about this corpus. A future polarization analysis must separately define its outcome—such as ideological distance or hostility toward political opponents—and obtain suitable audience measures; changes in news labels, viewing choices or votes alone do not establish either form of polarization.

## Unit, population and estimands

The coding unit is **one supplied article record with one prioritized government-relevant action and one evaluated national government**. The title and lead guide action selection. The resulting record is neither a census of actions in that article nor a unique real-world event. Reprints and repeated coverage can give one event multiple article records. `frame` uses observable narration in the supplied text; `align` and `rep` share the selected action.

The fixed descriptive discussion cohort is **542,981 structurally valid, independently stored, complete-prompt outcomes from January 2025 through May 2026**, at the October 29, 2026 storage checkpoint, **05:20:31 UTC**. It excludes mechanical/API failures and older-prompt outcomes. It is an observed processed subset, not a probability sample of all news or all events. Retaining one prompt and period improves comparability but does not remove incomplete coverage or selection.

Define the first estimands explicitly:

1. **Observed-corpus prevalence:** the share of records in that frozen cohort with each label, including 0 and null. This is the appropriate interpretation of the current marginal charts.
2. **Within-source and within-government composition:** label shares by outlet, evaluated government and publication month, with cell sizes and processing coverage. These tables are proposed next work; current marginals do not supply them.
3. **Matched-event presentation difference:** differences in `frame` among articles reporting the same event within a bounded time window, after checking which action each article selects. This is a proposed relative comparison, not an existing estimate of bias.
4. **Coverage choice:** whether outlets cover a common, independently defined event opportunity at all. This requires an external event frame or a clearly bounded union of observed coverage. Missing scraped articles cannot automatically be coded as editorial silence.

For any conditional proportion, state the changed denominator. A positive share among all valid outputs differs from a positive share among non-null records or among directional records. Publish counts alongside percentages. Publication-country memberships and the single evaluated-government country are different variables; overlapping memberships must not be summed as unique articles.

## Competing explanations to test

| Observed pattern | Plausible explanations | Evidence needed to distinguish them |
|---|---|---|
| More adverse `rep` than favorable `rep` | More adverse events; watchdog reporting; selective coverage; source mix; coding or translation error | Event/topic mix, stable source panels, paired text review, representative validation |
| Favorable `frame` toward an incumbent | Government pressure; ownership incentives; audience demand; editorial preference; differential event mix | Dated ownership/control measures, audience information, same-event comparisons, validated framing |
| Many 0 labels | Routine reporting; narrow national scope; mixed evidence; missing affiliations; partial translations; conservative coding | Separate audits of input completeness, government identity and label decisions |
| Change around an election or transfer of power | Changed events; changed officeholders/reference; source entry/exit; political adaptation; processing composition | Exact tenure dates, stable outlets, consistent prompt, event matching and coverage checks |
| Differences across countries | Institutions and media systems; corpus selection; unequal country/source volume; language error; varying political context | Comparable outlet panels and periods, subgroup validation, alternative weighting |

The codebook's reasonable-observer standard for `rep` encodes judgments about competence, accountability, legality and rights. It is explicit and reviewable, but it is not evidence that every political audience would interpret an event identically. Cross-country validation should examine disagreement about that standard.

## Concrete next analysis

1. Freeze a dated analysis manifest defining article identity, prompt/model cohort, inclusion rules, processing coverage and exclusions. Preserve every original outcome; corrections belong in versioned annotations.
2. Build unique-record joint tables for `align × rep`, `rep × frame`, government × source × month, and action type × labels. The fact that marginal distributions differ does not reveal the article-level association between dimensions.
3. Compare article-weighted results with equal-outlet and equal-government summaries, restricted to explicitly defined comparable cells. These are different descriptive targets; none automatically represents the world population or readership.
4. Add a stable-outlet panel and distinguish domestic coverage (`publication country = gov`) from foreign/international coverage. Report uncodable records and mechanical failures separately. Examine the effect of incomplete source-month cells.
5. Validate the main labels and input pipeline using the design in [validation.md](validation.md). Report error and adjudication patterns before turning prevalence into political claims.
6. Select a small, predeclared set of events with multiple outlets and manually verify event matches. Compare the same underlying action, not merely similar keywords. Inspect when outlets choose different focal actions; that choice is itself a separate representation question.
7. Only after dated ownership/control data and a defensible treatment design exist, evaluate an ownership or control change. A panel or event-study specification alone does not solve endogenous acquisition, simultaneous political changes or differential source survival. A causal interpretation needs its own assumptions, diagnostic tests and uncertainty analysis.

## What “media bias” can mean here

The current `frame` variable is intentionally narrow. Theoretical work distinguishes distortion from filtering or selection of information, and emphasizes the role of a comparative benchmark ([Gentzkow, Shapiro and Stone, 2014 working paper](https://www.nber.org/papers/w19880)). Thus `frame = 0` cannot certify an unbiased article or outlet. A source can report selected adverse events in descriptive language, or omit adverse events while never using favorable adjectives.

For November 11, a defensible headline is: **“Separating political action, reputational implication and evaluative presentation in news.”** The political ambition is to use these distinctions to study accountability and information environments after validation and design work. An outlet ranking or a claim that the data demonstrate polarization would exceed the present evidence.
