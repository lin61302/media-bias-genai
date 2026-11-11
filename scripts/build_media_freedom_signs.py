#!/usr/bin/env python3
"""Positive, negative and directional domestic coverage from frozen counts.

Uses committed, hash-pinned aggregate CSVs; no network, model, database, private
text or PDF operations. Preserves the existing 71 fixed freedom groups, January
2022–December 2025 period, domestic equality filter and n >= 30 threshold.
The existing figure-16 files are read only and never rewritten.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MaxNLocator
import numpy as np
import pandas as pd

import build_domestic_media_freedom as base

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "slides/figures/data"
FIGURES = ROOT / "slides/figures"
INPUTS = {
    "counts": ("16_media_freedom_country_month.csv",
               "af6d0eda1df59818d8c150978ff84508ba4be0bd7d6e3909cfd4e0bd9a6b230d"),
    "groups": ("16_media_freedom_groups.csv",
               "050b0355857b2859383ac9596a5b2eb1a357f068417d46d96076ca3325d533a9"),
    "negative_reference": ("16_media_freedom_monthly_series.csv",
                           "4058f61320afab8487dea2d08bab56ae62251ebda279ba14c118824ffab446ae"),
    "extraction": ("16_media_freedom_extraction_provenance.json",
                   "7550f1b3169e51920a3bedfc2b374d79d74bd52ed8de7b6e700d131cf8cd4589"),
}
METRICS = ("negative_share", "zero_share", "positive_share", "directional_share", "P_country_mean")
SUBTITLES = {
    "positive": {
        "align": "Reported actions supporting the incumbent",
        "rep": "Favorable implications for the government",
        "frame": "Favorable evaluation in title or narration",
    },
    "directional": {
        "align": "Reported support or opposition",
        "rep": "Favorable or unfavorable implications",
        "frame": "Favorable or critical narrator evaluation",
    },
}


def load_and_calculate() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    for name, expected in INPUTS.values():
        base.check_hash(DATA / name, expected)
    groups = pd.read_csv(DATA / INPUTS["groups"][0])
    if groups.country.duplicated().any() or len(groups) != 71:
        raise ValueError("Expected 71 unique countries")
    if groups.groupby("group").size().to_dict() != {"low": 24, "middle": 23, "high": 24}:
        raise ValueError("Fixed groups must contain 24/23/24 countries")
    frame, selection = base.load_counts(DATA / INPUTS["counts"][0], sorted(groups.country))
    domestic = frame.loc[(frame.scope == "domestic") & (frame.n >= base.MIN_N)].copy()
    if len(domestic) != 3282 or int(domestic.n.sum()) != 1650617:
        raise ValueError("Domestic eligible cohort differs from 3,282 country-months / 1,650,617 articles")
    domestic = domestic.merge(groups[["country", "group"]], on="country", validate="many_to_one")
    for axis in base.AXES:
        for sign in base.SIGNS:
            domestic[f"{axis}_{sign}_share"] = domestic[f"{axis}_{sign}"] / domestic.n
        domestic[f"{axis}_directional_share"] = domestic[f"{axis}_negative_share"] + domestic[f"{axis}_positive_share"]
        # Calculate P within each country-month BEFORE any group averaging.
        domestic[f"{axis}_P_country_mean"] = 4 * domestic[f"{axis}_negative_share"] * domestic[f"{axis}_positive_share"]
        if not np.allclose(domestic[[f"{axis}_{s}_share" for s in base.SIGNS]].sum(axis=1), 1, atol=1e-12, rtol=0):
            raise ValueError(f"Country-month sign shares do not sum to one: {axis}")
        if not np.allclose(domestic[f"{axis}_directional_share"], 1 - domestic[f"{axis}_zero_share"], atol=1e-12, rtol=0):
            raise ValueError(f"Country-month S != 1 - zero: {axis}")
    rows = []
    for group in base.GROUPS:
        fixed_n = int((groups.group == group).sum())
        for month in base.MONTHS:
            sub = domestic.loc[(domestic.group == group) & (domestic.month == month)]
            if sub.empty:
                raise ValueError(f"No eligible country-months in frozen group {group}, {month}")
            row = {"group": group, "month": month, "contributing_countries": len(sub),
                   "fixed_group_countries": fixed_n, "eligible_articles": int(sub.n.sum()),
                   "contributing_country_codes": "|".join(sorted(sub.country))}
            for axis in base.AXES:
                for metric in METRICS:
                    row[f"{axis}_{metric}"] = sub[f"{axis}_{metric}"].mean()
            rows.append(row)
    monthly = pd.DataFrame(rows)
    for axis in base.AXES:
        if not np.allclose(monthly[[f"{axis}_{s}_share" for s in base.SIGNS]].sum(axis=1), 1, atol=1e-12, rtol=0):
            raise ValueError(f"Group-month sign shares do not sum to one: {axis}")
        if not np.allclose(monthly[f"{axis}_directional_share"], 1 - monthly[f"{axis}_zero_share"], atol=1e-12, rtol=0):
            raise ValueError(f"Group-month S != 1 - zero: {axis}")
        for metric in METRICS:
            col = f"{axis}_{metric}"
            monthly[f"{col}_centered3"] = monthly.groupby("group", sort=False)[col].transform(
                lambda s: s.rolling(3, center=True, min_periods=3).mean())
    reference = pd.read_csv(DATA / INPUTS["negative_reference"][0])
    reference = reference.loc[reference.scope == "domestic"].set_index(["group", "month"])
    current = monthly.set_index(["group", "month"])
    if set(reference.index) != set(current.index):
        raise ValueError("Reference group-month membership differs")
    reference = reference.reindex(current.index)
    for col in ("contributing_countries", "fixed_group_countries", "eligible_articles", "contributing_country_codes"):
        if not current[col].equals(reference[col]):
            raise ValueError(f"Negative reference cohort differs: {col}")
    negative_errors = {}
    for axis in base.AXES:
        for suffix in ("negative_share", "negative_share_centered3"):
            col = f"{axis}_{suffix}"
            if not np.allclose(current[col], reference[col], atol=1e-11, rtol=0, equal_nan=True):
                raise ValueError(f"Existing negative series changed: {col}")
            negative_errors[col] = float((current[col] - reference[col]).abs().max())
    summaries = []
    for group in base.GROUPS:
        sub = monthly.loc[monthly.group == group]
        row = {"group": group, "months": len(sub), "fixed_group_countries": int(sub.fixed_group_countries.iloc[0]),
               "contributing_country_months": int(sub.contributing_countries.sum()),
               "included_articles": int(sub.eligible_articles.sum()),
               "min_contributing_countries": int(sub.contributing_countries.min()),
               "max_contributing_countries": int(sub.contributing_countries.max())}
        for axis in base.AXES:
            for metric in METRICS:
                row[f"{axis}_{metric}"] = sub[f"{axis}_{metric}"].mean()
        summaries.append(row)
    checks = {"eligible_country_months": len(domestic), "eligible_articles": int(domestic.n.sum()),
              "group_months": len(monthly), "three_sign_shares_sum_to_one": True,
              "directional_equals_one_minus_zero": True,
              "negative_reference_max_absolute_errors": negative_errors,
              "threshold_and_country_support_match_existing_negative_plot": True,
              "input_selection": selection}
    return groups, monthly, pd.DataFrame(summaries), checks


def percent_tick(value: float, _position: float) -> str:
    # 0.025 must display as 2.5%, not a rounded 2% or 3%.
    return f"{value * 100:.1f}".rstrip("0").rstrip(".") + "%"


def plot_panel(ax, monthly: pd.DataFrame, axis: str, metric: str, upper: float) -> None:
    x = np.arange(len(base.MONTHS))
    for group in base.GROUPS:
        sub = monthly.loc[monthly.group == group].set_index("month").loc[base.MONTHS]
        ax.plot(x, sub[f"{axis}_{metric}"], color=base.COLORS[group], linewidth=1.05, alpha=.30)
        ax.plot(x, sub[f"{axis}_{metric}_centered3"], color=base.COLORS[group], linewidth=2.8)
    ax.set_xlim(-.5, 47.5)
    ax.set_ylim(0, upper)
    ax.set_xticks([0, 12, 24, 36], ["2022", "2023", "2024", "2025"])
    ax.yaxis.set_major_locator(MaxNLocator(nbins=4, steps=[1, 2, 2.5, 5, 10]))
    ax.yaxis.set_major_formatter(FuncFormatter(percent_tick))
    ax.grid(axis="y", color="#e1e5e9", linewidth=.75)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, pad=7)
    for side in ("left", "right", "top"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#b7bec7")


def axis_limits(monthly: pd.DataFrame, metrics: tuple[str, ...]) -> dict:
    return {axis: min(1., max(.05, np.ceil(max(float(monthly[f"{axis}_{m}"].max()) for m in metrics) * 1.04 / .025) * .025))
            for axis in base.AXES}


def build_figures(monthly: pd.DataFrame, directory: Path) -> tuple[list[Path], dict]:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12,
                         "text.color": "#202b36", "axes.labelcolor": "#202b36",
                         "xtick.color": "#49545f", "ytick.color": "#49545f",
                         "svg.fonttype": "none", "svg.hashsalt": "domestic-media-freedom-signs-nov4-v1"})
    sizes = {"low": 24, "middle": 23, "high": 24}
    handles = [Line2D([0], [0], color=base.COLORS[g], lw=3,
                      label=f"{base.NAMES[g]} · {sizes[g]} countries") for g in base.GROUPS]
    shared_limits = axis_limits(monthly, ("negative_share", "positive_share"))
    positive_limits = axis_limits(monthly, ("positive_share",))
    directional_limits = axis_limits(monthly, ("directional_share",))
    outputs = []
    for kind, metric, title, ylabel, limits in (
        ("positive", "positive_share", "Positive domestic coverage by media freedom", "Positive share · mean across countries", positive_limits),
        ("directional", "directional_share", "Directional domestic coverage by media freedom", "Positive + negative share", directional_limits),
    ):
        fig, axs = plt.subplots(1, 3, figsize=(16, 5.95))
        fig.subplots_adjust(left=.06, right=.985, top=.71, bottom=.27, wspace=.25)
        fig.text(.06, .94, title, fontsize=23, weight="bold")
        fig.text(.06, .895, "Publication country = evaluated-government country · January 2022–December 2025", fontsize=13)
        for ax, axis in zip(axs, base.AXES):
            plot_panel(ax, monthly, axis, metric, limits[axis])
            ax.set_title(base.TITLES[axis], loc="left", fontsize=17, weight="bold", pad=30)
            ax.text(0, 1.045, SUBTITLES[kind][axis], transform=ax.transAxes, fontsize=10.5)
        axs[0].set_ylabel(ylabel, fontsize=12)
        fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.52, .13), ncol=3,
                   frameon=False, fontsize=12, columnspacing=2.2)
        fig.text(.06, .095, "Equal-country monthly means. Thin: monthly; thick: centered 3-month mean. At least 30 eligible articles per country-month.", fontsize=10.3)
        if kind == "directional":
            fig.text(.06, .058, "Directional = positive + negative. Zero-coded articles remain in the denominator. This is not the P index.", fontsize=10.3)
        else:
            fig.text(.06, .058, "Positive, zero and negative shares use the same denominator. Panel scales differ; use the paired figure to compare signs.", fontsize=10.3)
        fig.text(.06, .021, "Groups are fixed; monthly participation varies. V-Dem v16, mean 2022–2025. Frozen November 4, 2026 counts.", fontsize=10.3)
        outputs += base.save_figure(fig, directory, f"17_media_freedom_{kind}")

    fig, axs = plt.subplots(2, 3, figsize=(16, 9.2))
    fig.subplots_adjust(left=.075, right=.985, top=.78, bottom=.16, hspace=.50, wspace=.25)
    fig.text(.075, .96, "Domestic coverage: negative and positive shares", fontsize=22, weight="bold")
    fig.text(.075, .915, "Same countries and months in both rows · Identical vertical scales within each column · January 2022–December 2025", fontsize=12)
    for i, sign in enumerate(("negative", "positive")):
        for ax, axis in zip(axs[i], base.AXES):
            plot_panel(ax, monthly, axis, f"{sign}_share", shared_limits[axis])
            if i == 0:
                ax.set_title(base.TITLES[axis], loc="left", fontsize=17, weight="bold", pad=16)
        axs[i, 0].set_ylabel(f"{sign.capitalize()} share", fontsize=12)
    fig.text(.075, .855, "Negative coverage", fontsize=14, weight="bold")
    fig.text(.075, .452, "Positive coverage", fontsize=14, weight="bold")
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.52, .073), ncol=3,
               frameon=False, fontsize=12, columnspacing=2.2)
    fig.text(.075, .048, "Domestic: publication country = evaluated government. Equal-country monthly means; thin = monthly, thick = centered 3-month mean.", fontsize=10)
    fig.text(.075, .022, "At least 30 eligible articles per country-month. Zeros stay in the denominator. Fixed groups, varying monthly participation. November 4, 2026 snapshot.", fontsize=10)
    outputs += base.save_figure(fig, directory, "17_media_freedom_sign_comparison")
    return outputs, {"positive_and_negative_shared_y_maxima": shared_limits,
                     "positive_standalone_y_maxima": positive_limits,
                     "directional_y_maxima": directional_limits}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Calculate and validate without writing files")
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--figure-dir", type=Path, default=FIGURES)
    args = parser.parse_args()
    groups, monthly, summary, checks = load_and_calculate()
    if args.check_only:
        print(json.dumps({"checks": checks, "summary": summary.to_dict(orient="records")}, indent=2, allow_nan=False))
        return
    args.data_dir.mkdir(parents=True, exist_ok=True)
    args.figure_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for name, table in (("17_media_freedom_sign_monthly.csv", monthly),
                        ("17_media_freedom_sign_summary.csv", summary)):
        path = args.data_dir / name
        table.to_csv(path, index=False, na_rep="", float_format="%.12g", lineterminator="\n")
        outputs.append(path)
    figure_outputs, limits = build_figures(monthly, args.figure_dir)
    outputs += figure_outputs
    manifest = {
        "title": "Signs of domestic coverage by media freedom",
        "snapshot": "2026-11-04T13:38:01.213139+00:00", "period": [base.MONTHS[0], base.MONTHS[-1]],
        "inputs": {key: {"path": base.path_label(DATA / name), "sha256": expected} for key, (name, expected) in INPUTS.items()},
        "scripts": [{"path": base.path_label(p), "sha256": base.sha(p)} for p in (Path(__file__), Path(base.__file__))],
        "checks": checks, "summary": summary.to_dict(orient="records"), "plot_limits": limits,
        "methods": {
            "domestic": "Publication country equals evaluated-government country; same frozen extraction as figure16.",
            "groups": "Same 71 countries and fixed 2022-2025 V-Dem v16 v2x_freexp_altinf mean terciles: low24, middle23, high24. Read from hash-pinned membership CSV.",
            "eligibility": "Government/action identified, all three codes numeric -1/0/+1. Country-month n >= 30 after domestic restriction. Zeros retained.",
            "country_month_sign_share": "Count of that sign / eligible n, separately for alignment, reputation and framing.",
            "directional_S": "Country-month positive share + negative share = 1 - zero share.",
            "P_country_mean": "First compute country-month P=4*p_positive*p_negative; then average those P values equally over eligible countries. NEVER multiply group-mean shares.",
            "monthly_group_mean": "Equal-country arithmetic mean of each country-month statistic. The same country-month support is used for every sign and dimension.",
            "within_country": "Articles pooled across included outlets; high-volume outlets contribute more within country-month.",
            "centered3": "Three-calendar-month centered arithmetic mean of the monthly group statistic; require all three months. First and last thick-line values missing; no interpolation.",
            "summary": "Arithmetic mean of 48 unsmoothed monthly group statistics; not pooled article shares and not means of country-period means.",
            "units": "Shares and P stored as fractions; plots show percentages. P is provided in CSV only, not plotted.",
            "membership": "24/23/24 are fixed membership counts; monthly contributor counts and identities are in the monthly CSV.",
            "zero": "Zero includes neutral, mixed or insufficient directional evidence; zero is distinct from uncodable/excluded.",
        },
        "limits": ["Descriptive coverage statistics, not causal effects of freedom, representative national media samples or measured public polarization.",
                   "Fixed groups conceal within-period institutional changes. Event, source, genre, translation and classification differences remain uncontrolled.",
                   "A higher directional share may reflect one-sided coverage. Positive and negative series should be examined separately.",
                   "Country sensitivity identified in the negative-framing comparison remains relevant; adding positive shares does not resolve it."],
        "outputs": [{"path": base.path_label(p), "sha256": base.sha(p), "bytes": p.stat().st_size} for p in outputs],
        "operations": {"network_calls": 0, "database_calls": 0, "model_calls": 0, "pdf_outputs": 0,
                       "existing_figure16_outputs_modified": False},
        "software": {"pandas": pd.__version__, "numpy": np.__version__, "matplotlib": matplotlib.__version__},
    }
    manifest_path = args.data_dir / "17_media_freedom_sign_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"manifest": base.path_label(manifest_path), "checks": checks,
                      "summary": summary.to_dict(orient="records")}, indent=2, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(f"Error: {error}") from error
