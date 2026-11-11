#!/usr/bin/env python3
"""Reproduce the country overview from frozen monthly sign counts.

Offline only. All source origins, evaluated-government country, Jan 2022–May
2026. Pool integer sign counts before calculating P; do not average monthly P.
The ranked figure contains all 70 countries in Erik's Ukraine-excluded roster.
His original regime scatter is preserved unchanged: the underlying categorical
regime assignments were not supplied and are not reconstructed here.

Run: python scripts/build_polarization_overview.py
Only PNG/SVG figures and CSV/JSON audit artifacts are authored.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "slides/figures"
DATA = FIGURES / "data"
INPUT = ROOT / "data/polarization/monthly_polarization_all_countries.csv"
INPUT_SHA = "9e70e773c22fab5f9d9d365d5344e3669a78afee5a3ac2f7df0f9a6b7775f965"
ROSTER = DATA / "06_coverage_map.csv"
CHECK_ROSTER = DATA / "16_media_freedom_groups.csv"
DIMS = ("alignment", "reputation", "framing")
SIGNS = ("negative", "zero", "positive")
COLORS = {"alignment": "#2878ad", "reputation": "#d88720", "framing": "#389556"}
MARKERS = {"alignment": "o", "reputation": "s", "framing": "D"}
NAMES = {"alignment": "Political alignment", "reputation": "Reputational implication", "framing": "Framing"}
SHORT_NAMES = {
    "BOL": "Bolivia", "COD": "DR Congo", "MDA": "Moldova", "TZA": "Tanzania",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pool_countries() -> tuple[pd.DataFrame, pd.DataFrame]:
    assert sha(INPUT) == INPUT_SHA, "Frozen monthly export changed; inspect before rebuilding."
    coverage = pd.read_csv(ROSTER)
    roster = set(coverage.loc[coverage.publication_source_domains.gt(0), "country_code"])
    assert len(roster) == 71
    assert roster == set(pd.read_csv(CHECK_ROSTER).country)
    monthly = pd.read_csv(INPUT)
    monthly = monthly.loc[monthly.month.between("2022-01", "2026-05") &
                          monthly.government_country_code.isin(roster)].copy()
    assert not monthly.duplicated(["government_country_code", "month"]).any()
    assert len(monthly) == 71 * 53
    assert monthly.eligible_articles.notna().all() and monthly.eligible_articles.ge(0).all()
    count_cols = []
    for dimension in DIMS:
        for sign in SIGNS:
            share = f"{dimension}_{sign}_share"
            count = f"{dimension}_{sign}_count"
            assert monthly.loc[monthly.eligible_articles.gt(0), share].notna().all()
            raw = monthly.eligible_articles * monthly[share].fillna(0)
            assert np.allclose(raw, np.rint(raw), rtol=0, atol=1e-7)
            monthly[count] = np.rint(raw).astype("int64")
            count_cols.append(count)
        assert (monthly[[f"{dimension}_{s}_count" for s in SIGNS]].sum(axis=1)
                == monthly.eligible_articles).all()
    pooled = monthly.groupby(["government_country_code", "government_country_name"],
                             as_index=False)[["eligible_articles"] + count_cols].sum()
    for dimension in DIMS:
        for sign in SIGNS:
            pooled[f"{dimension}_{sign}_share"] = (pooled[f"{dimension}_{sign}_count"] /
                                                     pooled.eligible_articles)
        pooled[f"polarization_{dimension}"] = (
            4 * pooled[f"{dimension}_negative_share"] * pooled[f"{dimension}_positive_share"])
    all_71 = pooled.copy()
    ranked = pooled.loc[pooled.government_country_code.ne("UKR")].sort_values(
        ["polarization_alignment", "government_country_code"], ascending=[False, True]).reset_index(drop=True)
    ranked.insert(0, "alignment_rank", np.arange(1, len(ranked) + 1))
    ranked.insert(3, "display_name", [SHORT_NAMES.get(c, n) for c, n in zip(
        ranked.government_country_code, ranked.government_country_name)])
    assert len(ranked) == 70 and ranked.eligible_articles.sum() == 1781972
    assert all_71.eligible_articles.sum() == 1873774
    return ranked, all_71


def correlation(frame: pd.DataFrame) -> dict[str, float]:
    x, y = frame.polarization_alignment, frame.polarization_reputation
    return {"pearson": float(x.corr(y)), "spearman": float(x.rank().corr(y.rank()))}


def render_rank(ranked: pd.DataFrame) -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 15, "svg.fonttype": "none",
        "axes.edgecolor": "#b9c1ca", "axes.labelcolor": "#344454",
        "xtick.color": "#475767", "ytick.color": "#344454", "savefig.facecolor": "white",
    })
    fig, axes = plt.subplots(1, 3, figsize=(19, 8), dpi=200)
    # Each panel has its own label gutter; all three use exactly the same scale.
    fig.subplots_adjust(left=0.15, right=0.992, top=0.945, bottom=0.15, wspace=1.06)
    chunks = (ranked.iloc[:24], ranked.iloc[24:47], ranked.iloc[47:])
    for ax, chunk in zip(axes, chunks):
        y = np.arange(len(chunk))
        for i in range(len(chunk)):
            if i % 2 == 0:
                ax.axhspan(i - .5, i + .5, color="#f5f7f9", lw=0, zorder=0)
        senegal = np.flatnonzero(chunk.government_country_code.eq("SEN"))
        for i in senegal:
            ax.axhspan(i - .5, i + .5, color="#e5edf5", lw=0, zorder=1)
        for dimension in DIMS:
            ax.scatter(chunk[f"polarization_{dimension}"], y, color=COLORS[dimension],
                       marker=MARKERS[dimension], s=35 if dimension == "framing" else 40,
                       edgecolor="white", linewidth=.45, zorder=4)
        ax.set_yticks(y)
        ax.set_yticklabels([f"{int(r):2d}  {n}" for r, n in zip(chunk.alignment_rank, chunk.display_name)], fontsize=18)
        for tick, code in zip(ax.get_yticklabels(), chunk.government_country_code):
            if code == "SEN":
                tick.set_fontweight("bold")
                tick.set_color("#012b50")
        ax.set_ylim(23.65, -.7)  # Fixed row spacing, including the two 23-row panels.
        ax.set_xlim(0, .13)
        ax.set_xticks([0, .04, .08, .12], ["0", ".04", ".08", ".12"], fontsize=16)
        ax.tick_params(axis="y", length=0, pad=7)
        ax.tick_params(axis="x", length=3, pad=6)
        ax.grid(axis="x", color="#dce2e8", linewidth=.65, zorder=0)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.set_title(f"Ranks {chunk.alignment_rank.min()}–{chunk.alignment_rank.max()}",
                     loc="left", fontsize=18, fontweight="bold", color="#344454", pad=12)
        # The slide defines P below the figure; repeated axis labels crowd the legend.
    handles = [Line2D([0], [0], marker=MARKERS[d], color="none", markerfacecolor=COLORS[d],
                      markeredgecolor="white", markersize=8, label=NAMES[d]) for d in DIMS]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .027), ncol=3,
               frameon=False, fontsize=18, columnspacing=2.2, handletextpad=.5)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"21_polarization_country_ranking.{suffix}", dpi=200)
    svg_path = FIGURES / "21_polarization_country_ranking.svg"
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text().splitlines()) + "\n")
    plt.close(fig)


def main() -> None:
    ranked, all_71 = pool_countries()
    corr = correlation(ranked)
    assert np.isclose(corr["pearson"], .7789785079335438, rtol=0, atol=1e-12)
    assert np.isclose(corr["spearman"], .8514565654798355, rtol=0, atol=1e-12)
    DATA.mkdir(parents=True, exist_ok=True)
    csv_path = DATA / "21_country_polarization.csv"
    ranked.to_csv(csv_path, index=False, float_format="%.15g")
    render_rank(ranked)
    originals = [FIGURES / "21_erik_rank_original.png", FIGURES / "21_erik_scatter_original.png"]
    assert all(p.exists() for p in originals), "Retain the two unmodified Erik source images."
    manifest = {
        "title": "Country polarization overview for Erik's broad introduction",
        "input": {"path": str(INPUT.relative_to(ROOT)), "sha256": sha(INPUT)},
        "country_roster": {"path": str(ROSTER.relative_to(ROOT)), "sha256": sha(ROSTER),
                           "filter": "publication_source_domains > 0", "countries_before_exclusion": 71,
                           "crosscheck": str(CHECK_ROSTER.relative_to(ROOT))},
        "period": {"first_month": "2022-01", "last_month": "2026-05", "months": 53},
        "unit": "Evaluated-government country; all countries of publication are included.",
        "country_month_minimum": None,
        "method": "Recover integer sign counts as eligible_articles × share; pool counts across months; P = 4 × negative_count × positive_count / eligible_articles². Neutral records remain in the denominator.",
        "rank_order": "Descending political-alignment P; all 70 countries shown in three consecutive panels.",
        "excluded_countries": {"UKR": "Inherited from Erik's supplied figures; substantive exclusion rationale was not supplied."},
        "countries": len(ranked), "eligible_articles": int(ranked.eligible_articles.sum()),
        "alignment_reputation_correlation": corr,
        "including_ukraine_sensitivity": {"countries": len(all_71), "eligible_articles": int(all_71.eligible_articles.sum()), **correlation(all_71)},
        "regime_scatter": {
            "status": "Erik's supplied PNG is preserved unchanged, not regenerated.",
            "caption_reports": "Modal V-Dem Regimes of the World category, 2022–25; 8 closed autocracies, 32 electoral autocracies, 30 democracies (including one liberal democracy).",
            "limitation": "Underlying country regime assignments, modal tie rule and generation code were not supplied. Local continuous V-Dem press-freedom data do not identify these regime categories. Regime membership and subgroup correlations are therefore caption-reported, not independently verified here.",
        },
        "original_images": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in originals],
        "outputs": {"csv": str(csv_path.relative_to(ROOT)), "csv_sha256": sha(csv_path),
                    "figure_png": "slides/figures/21_polarization_country_ranking.png",
                    "figure_svg": "slides/figures/21_polarization_country_ranking.svg", "png_dimensions": [3800, 1600]},
        "interpretation": "Descriptive corpus scores, not population estimates or evidence of causal regime effects. P depends on both directional shares and the neutral share; pooling can combine different actors, events and periods.",
    }
    (DATA / "21_polarization_overview_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"countries": len(ranked), "eligible_articles": int(ranked.eligible_articles.sum()),
                      "correlations": corr, "including_ukraine": correlation(all_71)}, indent=2))
    print(ranked.loc[ranked.government_country_code.isin(["ETH", "NIC", "SEN"]),
                     ["alignment_rank", "display_name", "eligible_articles"] + [f"polarization_{d}" for d in DIMS]].to_string(index=False))


if __name__ == "__main__":
    main()
