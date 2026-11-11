#!/usr/bin/env python3
"""Two outlet-volume sensitivity plots, with equal countries at the outer stage.

Offline, frozen aggregate counts only. Square-root weights and saturating
n/(n+k) weights use the same eligible country-months as figure 16. The main k
is the median nonempty outlet-month count on that support, selected without
looking at labels. Neither method estimates audience reach or independence.
Existing figures and their inputs are never rewritten.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

import build_domestic_media_freedom as base
from build_media_freedom_signs import plot_panel, axis_limits

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "slides/figures/data"
FIGURES = ROOT / "slides/figures"
INPUTS = {
    "outlet_counts": ("19_media_freedom_outlet_month_counts.csv", "b9b93faf3879ae1a328b0ff20b753f0e0fe7c605921efd3710053aed1a6e2edd"),
    "extraction": ("19_media_freedom_outlet_extraction.json", "e089969e3ff7569bfa867b2d7bfd8a767bbbbc8a778243627b61c719b9ae3d65"),
    "country_counts": ("16_media_freedom_country_month.csv", base.INPUT_SHA),
    "groups": ("16_media_freedom_groups.csv", "050b0355857b2859383ac9596a5b2eb1a357f068417d46d96076ca3325d533a9"),
    "baseline": ("16_media_freedom_monthly_series.csv", "4058f61320afab8487dea2d08bab56ae62251ebda279ba14c118824ffab446ae"),
    "nicaragua": ("18_nicaragua_outlet_month_counts.csv", "905cc28235f2923430204a9ae8f14733f0ca2291e150620681d039f6891919f0"),
}
KEYS = ["country", "month"]
SHARES = [f"{a}_{s}_share" for a in base.AXES for s in base.SIGNS]


def calculate():
    for name, expected in INPUTS.values():
        base.check_hash(DATA / name, expected)
    groups = pd.read_csv(DATA / INPUTS["groups"][0])
    assert groups.country.nunique() == len(groups) == 71
    assert groups.groupby("group").size().to_dict() == {"low": 24, "middle": 23, "high": 24}
    counts = pd.read_csv(DATA / INPUTS["outlet_counts"][0])
    assert len(counts) == 16421 and counts.n.sum() == 1652040
    assert not counts.duplicated([*KEYS, "source_domain"]).any()
    assert counts[[*KEYS, "source_domain"]].notna().all().all()
    assert counts.country.isin(groups.country).all() and counts.month.isin(base.MONTHS).all()
    assert (counts.n > 0).all()
    assert (counts[base.COUNT_COLUMNS] >= 0).all().all()
    assert (counts[base.COUNT_COLUMNS] == np.floor(counts[base.COUNT_COLUMNS])).all().all()
    for axis in base.AXES:
        assert (counts[[f"{axis}_{s}" for s in base.SIGNS]].sum(axis=1) == counts.n).all()

    # Reconcile all ten counts, including country-months below the plot threshold.
    reference, _ = base.load_counts(DATA / INPUTS["country_counts"][0], sorted(groups.country))
    domestic = reference.loc[reference.scope == "domestic"].set_index(KEYS)
    reconstructed = counts.groupby(KEYS)[base.COUNT_COLUMNS].sum().reindex(domestic.index, fill_value=0)
    assert np.array_equal(reconstructed.values, domestic[base.COUNT_COLUMNS].values)
    nic = pd.read_csv(DATA / INPUTS["nicaragua"][0]).set_index(["source_domain", "month"])
    nic_new = counts.loc[counts.country == "NIC"].set_index(["source_domain", "month"])
    nic_new = nic_new[base.COUNT_COLUMNS].reindex(nic.index, fill_value=0)
    assert np.array_equal(nic_new.values, nic[base.COUNT_COLUMNS].values)

    cohort = domestic.loc[domestic.n >= base.MIN_N, ["n"]].reset_index()
    assert len(cohort) == 3282 and cohort.n.sum() == 1650617
    outlets = counts.merge(cohort[KEYS], on=KEYS, validate="many_to_one")
    assert outlets.n.sum() == cohort.n.sum() and len(outlets) == 16176
    k = float(outlets.n.median())
    assert k == 40.0
    # References and k sensitivity use the exact same sample as the two plots.
    scores = {
        "article_reference": outlets.n.astype(float),
        "equal_outlet_reference": np.ones(len(outlets)),
        "sqrt": np.sqrt(outlets.n),
        "saturating": outlets.n / (outlets.n + k),
        "saturating_k_half": outlets.n / (outlets.n + k / 2),
        "saturating_k_double": outlets.n / (outlets.n + k * 2),
    }
    effective_k = {"saturating": k, "saturating_k_half": k / 2, "saturating_k_double": 2 * k}
    weighted_tables, weight_tables = [], []
    for method, score in scores.items():
        work = outlets.copy()
        work["weight_score"] = score
        work["normalized_weight"] = work.weight_score / work.groupby(KEYS).weight_score.transform("sum")
        assert np.allclose(work.groupby(KEYS).normalized_weight.sum(), 1, atol=1e-12, rtol=0)
        for axis in base.AXES:
            for sign in base.SIGNS:
                work[f"{axis}_{sign}_share"] = work[f"{axis}_{sign}"] / work.n * work.normalized_weight
        result = work.groupby(KEYS, as_index=False)[SHARES].sum()
        result = result.merge(cohort, on=KEYS, validate="one_to_one")
        active = work.groupby(KEYS, as_index=False).agg(active_outlets=("source_domain", "size"))
        result = result.merge(active, on=KEYS, validate="one_to_one")
        result = result.merge(groups[["country", "group"]], on="country", validate="many_to_one")
        result.insert(0, "method", method)
        result["k"] = effective_k.get(method, np.nan)
        for axis in base.AXES:
            assert np.allclose(result[[f"{axis}_{s}_share" for s in base.SIGNS]].sum(axis=1), 1, atol=1e-12, rtol=0)
        weighted_tables.append(result)
        if method in ("sqrt", "saturating"):
            w = work[[*KEYS, "source_domain", "n", "weight_score", "normalized_weight"]].copy()
            w.insert(0, "method", method)
            weight_tables.append(w)
    country_month = pd.concat(weighted_tables, ignore_index=True)
    weights = pd.concat(weight_tables, ignore_index=True)
    monthly_rows = []
    for method in scores:
        for group in base.GROUPS:
            sub = country_month.loc[(country_month.method == method) & (country_month.group == group)]
            table = sub.groupby("month")[SHARES].mean().reindex(base.MONTHS)
            assert not table.isna().any().any()
            table["contributing_countries"] = sub.groupby("month").country.size().reindex(base.MONTHS)
            table["eligible_articles"] = sub.groupby("month").n.sum().reindex(base.MONTHS)
            table["contributing_country_codes"] = sub.groupby("month").country.agg(lambda s: "|".join(sorted(s))).reindex(base.MONTHS)
            table["fixed_group_countries"] = int((groups.group == group).sum())
            for col in SHARES:
                table[f"{col}_centered3"] = table[col].rolling(3, center=True, min_periods=3).mean()
            table.insert(0, "group", group)
            table.insert(0, "method", method)
            table["k"] = effective_k.get(method, np.nan)
            monthly_rows.append(table.reset_index(names="month"))
    monthly = pd.concat(monthly_rows, ignore_index=True)
    old = pd.read_csv(DATA / INPUTS["baseline"][0])
    old = old.loc[old.scope == "domestic"].set_index(["group", "month"])
    new = monthly.loc[monthly.method == "article_reference"].set_index(["group", "month"]).reindex(old.index)
    errors = {}
    for col in ("contributing_countries", "eligible_articles", "contributing_country_codes", "fixed_group_countries"):
        assert new[col].equals(old[col]), col
    for axis in base.AXES:
        for suffix in ("negative_share", "negative_share_centered3"):
            col = f"{axis}_{suffix}"
            assert np.allclose(new[col], old[col], atol=1e-11, rtol=0, equal_nan=True), col
            errors[col] = float((new[col] - old[col]).abs().max())
    # Every method uses identical country support, not just the same total n.
    for method in scores:
        check = monthly.loc[monthly.method == method].set_index(["group", "month"]).reindex(old.index)
        assert check.contributing_country_codes.equals(old.contributing_country_codes)
    summary = monthly.groupby(["method", "group"], sort=False)[SHARES].mean().reset_index()
    country_summary = country_month.groupby(["method", "country", "group"], sort=False)[SHARES].mean().reset_index()
    diagnostics = {}
    for method in scores:
        pivot = monthly.loc[monthly.method == method].pivot(index="month", columns="group", values="frame_negative_share")
        diagnostics[method] = {
            "low_framing_above_high_months": int((pivot.low > pivot.high).sum()),
            "low_framing_highest_months": int(((pivot.low > pivot.high) & (pivot.low > pivot.middle)).sum()),
            "nicaragua_mean_monthly_negative_framing": float(country_summary.loc[(country_summary.method == method) & (country_summary.country == "NIC"), "frame_negative_share"].iloc[0]),
        }
    checks = {
        "all_ten_counts_reconcile_to_every_baseline_domestic_country_month": True,
        "all_384_nicaragua_outlet_month_cells_reconcile": True,
        "eligible_country_months": len(cohort), "eligible_articles": int(cohort.n.sum()),
        "eligible_nonempty_outlet_months": len(outlets), "exact_domains": int(outlets.source_domain.nunique()),
        "median_eligible_outlet_month_count_k": k,
        "same_country_month_support_all_methods": True, "weights_normalized_within_country_month": True,
        "three_signs_sum_to_one": True, "article_reference_max_absolute_errors": errors,
    }
    return weights, country_month, monthly, summary, country_summary, checks, diagnostics


def figures(monthly, directory):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "text.color": "#202b36",
                         "axes.labelcolor": "#202b36", "xtick.color": "#49545f", "ytick.color": "#49545f",
                         "svg.fonttype": "none", "svg.hashsalt": "domestic-outlet-weights-nov4-v1"})
    comparison = monthly.loc[monthly.method.isin(["article_reference", "sqrt", "saturating"])]
    limits = axis_limits(comparison, ("negative_share",))
    handles = [Line2D([0], [0], color=base.COLORS[g], lw=3, label=base.NAMES[g]) for g in base.GROUPS]
    outputs = []
    specs = (
        ("sqrt", "Square-root outlet weights", "Outlet weight proportional to √n: larger collected samples count more, with reduced influence."),
        ("saturating", "Saturating outlet weights", "Outlet weight proportional to n / (n + 40): additional articles give diminishing weight; 40 is the sample median."),
    )
    for method, title, explanation in specs:
        fig, axs = plt.subplots(1, 3, figsize=(16, 6.1))
        fig.subplots_adjust(left=.06, right=.985, top=.70, bottom=.28, wspace=.25)
        fig.text(.06, .94, f"Negative coverage: {title.lower()}", fontsize=23, weight="bold")
        fig.text(.06, .895, "Publication country = evaluated-government country · January 2022–December 2025", fontsize=13)
        for ax, axis in zip(axs, base.AXES):
            plot_panel(ax, monthly.loc[monthly.method == method], axis, "negative_share", limits[axis])
            ax.set_title(base.TITLES[axis], loc="left", fontsize=17, weight="bold", pad=30)
            ax.text(0, 1.045, base.SUBTITLES[axis], transform=ax.transAxes, fontsize=10.5)
        axs[0].set_ylabel("Weighted negative share", fontsize=12)
        fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.52, .145), ncol=3,
                   frameon=False, fontsize=12, columnspacing=2.5)
        fig.text(.06, .115, explanation, fontsize=10.7)
        fig.text(.06, .078, "Normalize outlet weights within each country-month, then weight countries equally. Thin: monthly; thick: centered 3-month mean.", fontsize=10.3)
        fig.text(.06, .041, "Same sample and scales in both plots. Country-month n ≥ 30; zero labels retained. V-Dem v16 fixed groups; November 4 frozen data.", fontsize=10.3)
        fig.text(.06, .009, "Collected-volume sensitivity checks; weights do not measure audience reach. Monthly country and outlet participation can vary.", fontsize=10.3)
        outputs += base.save_figure(fig, directory, f"19_media_freedom_{method}_outlets")
    return outputs, limits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    weights, country, monthly, summary, country_summary, checks, diagnostics = calculate()
    if args.check_only:
        print(json.dumps({"checks": checks, "diagnostics": diagnostics, "summary": summary.to_dict("records")}, indent=2, allow_nan=False))
        return
    outputs = []
    for suffix, table in (("outlet_weights", weights), ("weighted_country_month", country),
                          ("weighted_monthly", monthly), ("weighted_summary", summary),
                          ("weighted_country_summary", country_summary)):
        path = DATA / f"19_media_freedom_{suffix}.csv"
        table.to_csv(path, index=False, na_rep="", float_format="%.12g", lineterminator="\n")
        outputs.append(path)
    figure_paths, limits = figures(monthly, FIGURES)
    outputs += figure_paths
    manifest = {
        "title": "Negative domestic coverage with alternative outlet-volume weights",
        "snapshot": "2026-11-04T13:38:01.213139+00:00", "period": [base.MONTHS[0], base.MONTHS[-1]],
        "inputs": {key: {"path": base.path_label(DATA / name), "sha256": expected} for key, (name, expected) in INPUTS.items()},
        "scripts": [{"path": base.path_label(p), "sha256": base.sha(p)} for p in (Path(__file__), Path(base.__file__), ROOT / "scripts/build_media_freedom_signs.py")],
        "checks": checks, "diagnostics": diagnostics, "plot_y_maxima": limits,
        "methods": {
            "outlet_share": "Sign count / all eligible articles from that exact source domain in that country-month; zero labels remain.",
            "sqrt": "Unnormalized outlet score sqrt(n). Normalize within each country-month, then average the outlet shares with these weights.",
            "saturating": "Unnormalized outlet score n/(n+k), k=40. Normalize within each country-month. k is the median of all 16,176 nonempty outlet-month counts on the common eligible support; one fixed k for all countries, months and labels.",
            "k_interpretation": "Reference tuning scale chosen from counts only. Half the limiting unnormalized score at n=k. No fitted correlation, audience reach or optimality claim. k/2=20 and 2k=80 are exported sensitivity settings.",
            "same_support": "3,282 country-months with n>=30, 1,650,617 articles. Every nonempty outlet-month included, even n=1. Absent outlets are missing, never zero-coded.",
            "country_group_stage": "Equal-country arithmetic means each month within unchanged 24/23/24 V-Dem groups. Countries do not receive square-root or saturating weights.",
            "centered3": "Full 48-month calendar, centered three-month arithmetic mean with all three required. No interpolation; first and last smoothed points missing.",
            "summary": "Arithmetic mean of 48 unsmoothed monthly group means, not pooled article shares or means of country-period means.",
            "references": "Article weighting and equal active outlet weighting are retained only in CSVs, not shown as either new alternative.",
            "extraction_receipt": "Immutable upstream receipt predates the user's correction. Its downstream_weighting field describes the initial request, not the final plotted methods. This manifest specifies the final methods.",
        },
        "limitations": ["Volume weights do not estimate audience exposure or repair omitted outlets, genres, domains or collection gaps.",
                        "Saturation bounds the raw score, not an outlet's normalized share. One observed outlet still has weight one.",
                        "Square-root scores grow without bound. Saturating weights are not uniformly more equal than square-root weights for every count pair.",
                        "No uncertainty intervals or causal effects are estimated. No model, provider or database calls were made for this analysis."],
        "outputs": [{"path": base.path_label(p), "sha256": base.sha(p), "bytes": p.stat().st_size} for p in outputs],
    }
    (DATA / "19_media_freedom_weighted_manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"checks": checks, "diagnostics": diagnostics, "summary": summary.to_dict("records")}, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
