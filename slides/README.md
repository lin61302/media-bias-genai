# Slides

`MediaBias_Polarization.qmd` is Erik's Quarto source. `MediaBias_Polarization.html` is the rendered, self-contained Reveal.js deck. Both were pulled from commit `0631974` (November 4, 2026); this documentation update preserves those files unchanged.

Open the HTML directly in a browser. With Quarto installed, render the source from this directory:

```sh
quarto render MediaBias_Polarization.qmd
```

The deck contains 17 slides. Its research argument moves from polarization and regime change to incumbent-referenced article coding, monthly aggregation and future comparisons with democracy indicators.

## Evidence available for the draft

| Existing section | Available material | Remaining decision or evidence |
|---|---|---|
| From articles to a monthly measure | [Coverage-balance definition](../docs/coverage-balance.md), notebook synthetic examples and monthly calculations | Decide which of the three fields the index represents; justify its relationship to the polarization literature |
| The corpus | [Data card](../docs/data-card.md), dated snapshot manifest and coverage counts | Separate the broad MLP collection, historical 7.37m extraction inventory, current stored results and the 1.98m eligible analysis sample. The draft's “today 7m+” is not the verified denominator used in these figures |
| The classifier | [Codebook](../docs/codebook.md), [complete prompt](../prompts/civic_20261020_complete_v1.txt) and [validation](../docs/validation.md) | Show action selection, government reference and the three distinct labels; human-reference accuracy remains unresolved |
| Some descriptives / More descriptives | [Notebook and exported figures](../notebooks/01_dashboard_and_measures.ipynb): joint labels, government cloud and Senegal monthly example | Choose a small set of findings with scope, denominators and uncertainty clearly stated |
| Media polarization as lag or lead? | V-Dem country-year context and monthly label tables are available | A fitted, validated lag/lead design is not supplied by the dashboard |
| Limitations / Conclusion | Measurement limits in the codebook, data card and [dashboard guide](../docs/dashboard-guide.md) | Distinguish coverage patterns from public attitudes and causal effects |

The classifier and descriptive slides currently contain placeholders. Unresolved citation notes remain in the literature slides and measure proposal. Broad corpus figures in the draft (including the 130m+, 600+ sources and language counts) require a dated MLP source; this update does not certify them. The exported figures describe the fixed November 4 analysis snapshot, not completed processing of the full historical corpus.

Figure files are in [figures](../figures/); each caption and its reproduction code are in the notebook. The [dashboard guide](../docs/dashboard-guide.md) explains point size, the two time controls, clustering, exclusions and contributor denominators.
