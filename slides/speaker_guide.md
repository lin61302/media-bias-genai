# Speaking plan

## Proposal for the team

> Could we start with the US and comparative literature, then use the measurement limits to introduce the incumbent as a common political reference? I can take the next 25 minutes to explain the three meanings of sentiment, how we code them, and what the preliminary data show. We can then return to the theory together: what needs validation, how these measures relate to existing polarization measures, and what designs could distinguish political change from changing coverage.

| Part | Slides | Approximate time | Proposed lead |
|---|---|---:|---|
| Research question and literature | 1–5 | 12–15 minutes | Erik, Mina and/or Ezgi, as agreed |
| Concepts, data and preliminary findings | 6–15 | 25 minutes | Zung-Ru |
| Research agenda | 16 | 5–7 minutes | Team |
| Discussion | 17 | 10–12 minutes | Audience and team |
| References | 18 | As needed | Literature speakers |

The literature speakers can divide the US and comparative work or combine them into one introduction. The transitions below connect their discussion to your section. This is a proposed division, not a commitment made on anyone else's behalf.

## Your opening and conceptual distinction

### Slide 6: Sentiment about what? — 3 minutes

**Opening:** “We spent a long time discussing sentiment because we were asking different questions with the same word. The record we now collect makes those questions explicit.”

- Start with the purpose of a score. A product review evaluates a product or a feature, such as battery life. Political reporting can contain several objects of evaluation in one article.
- Explain the methods briefly: word counts and dictionaries use observable lexical features; learned representations such as embeddings encode patterns in context. Neither decides which political question the researcher wants to answer.
- Define the three fields once. Alignment concerns the action's direction toward the incumbent. Reputation concerns implications for the government's performance or legitimacy. Framing concerns evaluation added by the narration.
- Your point is a mismatch between a generic positive/negative score and a particular political question. Avoid claiming that the sentiment literature generally fails to define its purpose.

**Transition:** “The distinction is easier to see when we hold the event constant.”

### Slide 7: One event, different judgments — 4 minutes

Use the synthetic example on the slide. “Police forcibly dispersed peaceful anti-government demonstrators” is a natural spoken description.

1. Identify the actor, action and entity target. The police act on demonstrators, but the national incumbent is the government being evaluated. One article contributes one prioritized action, not an inventory of every event it mentions.
2. Explain the supplied affiliation assumption. Security forces are not automatically coded as incumbent-aligned from their institutional name alone.
3. Explain **alignment +1**: the reported conduct restricts explicit opponents. Positive means political direction, not moral approval or proof of the actor's private beliefs.
4. Explain **reputation −1**: coercion against peaceful demonstrators has a negative legitimacy implication under the project's coding standard. This is an inference about reported conduct. It does not establish that domestic or international opinion actually changed.
5. Explain **framing 0**: the descriptive account adds no independent approval or criticism. Add “a necessary operation that restored order” and framing becomes +1 while the action and its reputational implication stay fixed.

The three judgments have different inferential requirements. Describe alignment as more directly tied to the reported action, rather than completely objective. Describe framing as an observable evaluative cue, rather than access to the author's private intention.

**Transition:** “This is why a single sentiment field became a structured record. Now, what reporting do those records cover?”

## The data and pipeline

### Slide 8: The current analysis sample — 2 minutes

State the unit and the denominator together: one article, one prioritized action, in **January 2021–May 2026**. The fixed November 4 snapshot has **2,654,346 structurally valid records** and **2,440,312 records eligible for joint comparisons**.

- Joint eligibility requires an identified government and primary action and all three labels codable. The other 214,034 valid records are excluded from these comparisons, not assigned zero.
- The sample reflects source collection, civic filters, usable supplied English and processing completion. Repeated stories about one event remain multiple articles.
- The live pipeline is expanding. The figures use a named snapshot so changes in results can be traced to changes in the sample.

### Slide 9: Source countries and evaluated governments — 1.5 minutes

Point to the maps separately. The left concerns publication sources; the right concerns the government an article evaluates. International reporting allows a government to appear without domestic collection in that country.

The current sample includes **428 domains**, with **402 mapped to 71 publication countries** and **26 international or mixed-country domains** recorded separately. Evaluated governments span **205 country/territory codes**. The maps use different quantities and scales. Uneven counts prevent treating every country as equally well measured.

**Transition:** “The next slide shows how the original reporting becomes an inspectable coding record.”

### Slide 10: The classifier — 4 minutes

Walk across the six boxes once. Spend the most time on translation, civic selection and the controls underneath.

- Scraping and preprocessing retain article text, date and source. The coding input uses the supplied English title and full supplied English body, including English originals in the same fields.
- **Two encoder classifiers** provide civic-event type and civic relevance. Both eligibility conditions must pass before GenAI coding. This is two classification tasks, not a claim that the system uses a “dual-encoder” architecture.
- Each article is an independent request within a batch. The complete prompt first selects the government and action, then applies the label rules. Boundary examples and exact evidence help reveal where a judgment came from. Allegations remain allegations.
- Fixed prompt versions, input structure and recorded settings constrain variation across batches. They do not eliminate bias or guarantee deterministic answers. Prompt caching mainly affects reuse and cost.
- Parsing and storage checks establish valid structure and persistence. Political interpretation still needs human validation.

Keep failed, missing and uncodable outcomes separate. Zero means neutral, mixed or insufficient directional evidence. Null means not codable. This distinction is essential to interpreting the denominators.

**Transition:** “Once the record is defined, we can aggregate it without collapsing the three political questions into one.”

## Monthly measures and preliminary findings

### Slide 11: Monthly shares, direction and balance — 3 minutes

Begin with positive, zero and negative article shares within a government-month. Explain that all three fields use the common eligible sample.

- **Net direction, N = p⁺ − p⁻**, summarizes direction. It is zero for both all-zero coverage and equal positive and negative shares.
- **Proposed two-sided index, P = 4p⁺p⁻**, responds to the prevalence of both directions and their balance. In the synthetic 45/10/45 month, P = .81; in the one-sided month, P = 0.
- The equivalent expression **P = (1 − p⁰)² − N²** makes the nonzero share explicit. This addresses Erik's concern that net sentiment alone ignores important distributional differences.
- P is not a measure of overall negativity. A wholly negative month has P = 0. Nor is it yet a validated measure of societal polarization. Keep the shares and article count alongside the score.

### Slide 12: Most eligible articles have zero-coded labels — 1.5 minutes

Give the audience one result: zero shares are **82.4% for alignment, 85.9% for reputation and 92.2% for framing**. Explain that the conservative framing rule requires evaluation beyond the event itself.

Do not interpret 92.2% as the share of unbiased articles. The label combines several reasons for no supported direction, and translation, selection and model errors can also affect it.

### Slide 13: Supporting the incumbent can still reflect badly on it — 2 minutes

Explain how to read one row before stating the finding. Rows condition reputation on an alignment category and sum to 100%.

Among **190,409 supporting actions**, **38,322 (20.1%)** have a negative reputational implication. The article-level numeric correlation is **0.338**. The relationship is positive overall, but the fields do not coincide. This is the empirical reason for keeping both, rather than only a conceptual preference.

These are model classifications. The table is not an accuracy test, and the coefficient does not establish causation or independence. Large zero categories and source dependence affect its interpretation.

### Slide 14: Monthly comparisons: Senegal — 2.5 minutes

Explain the lines and article-volume panel before discussing the election episode. Ask: “Do the three kinds of reporting move together, and how much reporting supports that comparison?”

The February 2024 postponement and court reversal provide context for examining the series. The March election follows. This is a selected, documented case, not a representative case or evidence that the episode caused the change in an index.

Check directional shares as well as P: rising negativity need not raise the two-sided index if coverage becomes more one-sided. Changing source composition, repeated reporting and incumbent turnover can alter interpretation. Gaps below 100 eligible articles are a display rule, not zero scores or a guarantee of reliability above the threshold.

## Your closing and handoff

### Slide 15: What needs validation — 2 minutes

Separate five questions: correct government/action/entities; consistent label interpretation; translation; omitted conditions without codable actions; stability under source and prompt changes.

The structured record lets reviewers locate a disagreement instead of debating an unexplained single score. Representative human-reference accuracy of the three current labels remains unmeasured. Old generic sentiment labels and dependent AI adjudication cannot substitute for three independently reviewed reference labels.

**Handoff:** “We now have a way to distinguish the action, its implications and the narration. The next question is when these patterns in reporting tell us something about polarization outside the reporting.”

Let the team lead slide 16: actor/action contributions, matched events across outlets, comparable countries and regions, and the original question about polarization and democratic change. The discussion slide asks which patterns should count as evidence and which comparisons could separate politics from coverage changes.

## Data release and later revisions

All current descriptive counts use the hash-pinned **November 4, 2026, 13:38:01 UTC** release, filtered from **January 2021 through May 2026**. January 2021 data are already released. Later pipeline totals are not included automatically.

When a new verified release is ready, update the figure inputs, regenerate all four figures and CSVs, then update counts and derived findings in the deck and this guide together. The [figure manifest](figures/data/slide_figure_manifest.json) records the scope and provenance. See the [slide README](README.md) for reproduction and the remaining literature citations.
