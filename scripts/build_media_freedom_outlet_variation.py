#!/usr/bin/env python3
"""Outlet distributions and within-country outlet variation, frozen 2022–2025.

Uses only committed aggregate counts. The main figure gives every exact source
domain one point. The supplement gives every country with >=2 outlets one point
for its within-country sample SD. Neither figure measures temporal volatility.
"""
from __future__ import annotations

import argparse
import hashlib
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
    "outlet_counts": ("19_media_freedom_outlet_month_counts.csv", "b9b93faf3879ae1a328b0ff20b753f0e0fe7c605921efd3710053aed1a6e2edd"),
    "country_counts": ("16_media_freedom_country_month.csv", base.INPUT_SHA),
    "groups": ("16_media_freedom_groups.csv", "050b0355857b2859383ac9596a5b2eb1a357f068417d46d96076ca3325d533a9"),
}
METHODS = ("all_outlets", "outlet_total_n_ge_30")
SIGN_ORDER = ("negative", "positive")


def describe(values: pd.Series) -> dict:
    q1, q3 = values.quantile([.25, .75], interpolation="linear")
    return {"N": len(values), "mean": values.mean(), "median": values.median(),
            "sample_sd": values.std(ddof=1), "q1": q1, "q3": q3, "iqr": q3-q1,
            "minimum": values.min(), "maximum": values.max()}


def calculate():
    for name, expected in INPUTS.values():
        base.check_hash(DATA / name, expected)
    groups = pd.read_csv(DATA / INPUTS["groups"][0])
    raw = pd.read_csv(DATA / INPUTS["outlet_counts"][0])
    assert len(groups) == groups.country.nunique() == 71
    assert groups.groupby("group").size().to_dict() == {"low": 24, "middle": 23, "high": 24}
    assert not raw.duplicated(["country", "source_domain", "month"]).any()
    assert raw.month.isin(base.MONTHS).all() and raw.country.isin(groups.country).all()
    assert (raw.n > 0).all()
    assert (raw[base.COUNT_COLUMNS] >= 0).all().all()
    assert (raw[base.COUNT_COLUMNS] == np.floor(raw[base.COUNT_COLUMNS])).all().all()
    for axis in base.AXES:
        assert (raw[[f"{axis}_{s}" for s in base.SIGNS]].sum(axis=1) == raw.n).all()
    reference, _ = base.load_counts(DATA / INPUTS["country_counts"][0], sorted(groups.country))
    domestic = reference.loc[reference.scope == "domestic"].set_index(["country", "month"])
    reconstructed = raw.groupby(["country", "month"])[base.COUNT_COLUMNS].sum().reindex(domestic.index, fill_value=0)
    assert np.array_equal(reconstructed.values, domestic[base.COUNT_COLUMNS].values)
    eligible = domestic.loc[domestic.n >= 30].reset_index()
    rows = raw.merge(eligible[["country", "month"]], on=["country", "month"], validate="many_to_one")
    assert len(eligible) == 3282 and len(rows) == 16176 and rows.n.sum() == 1650617
    assert rows.groupby("source_domain").country.nunique().max() == 1
    outlets = rows.groupby(["country", "source_domain"], as_index=False)[base.COUNT_COLUMNS].sum()
    support = rows.groupby(["country", "source_domain"], as_index=False).agg(
        observed_months=("month", "nunique"), first_month=("month", "min"), last_month=("month", "max"))
    outlets = outlets.merge(support, on=["country", "source_domain"], validate="one_to_one")
    outlets = outlets.merge(groups[["country", "country_name", "group"]], on="country", validate="many_to_one")
    outlets["small_sample"] = outlets.n < 30
    assert len(outlets) == outlets.source_domain.nunique() == 401
    assert outlets.small_sample.sum() == 14
    for axis in base.AXES:
        for sign in base.SIGNS:
            outlets[f"{axis}_{sign}_share"] = outlets[f"{axis}_{sign}"] / outlets.n
        assert np.allclose(outlets[[f"{axis}_{s}_share" for s in base.SIGNS]].sum(axis=1), 1, atol=1e-12, rtol=0)
    outlet_stats, country_rows, country_stats = [], [], []
    for population in METHODS:
        subset = outlets if population == "all_outlets" else outlets.loc[~outlets.small_sample]
        for axis in base.AXES:
            for sign in base.SIGNS:
                col = f"{axis}_{sign}_share"
                for group in base.GROUPS:
                    group_rows = subset.loc[subset.group == group]
                    outlet_stats.append({"population": population, "dimension": axis, "sign": sign,
                                         "group": group, "articles": int(group_rows.n.sum()),
                                         "countries": group_rows.country.nunique(), **describe(group_rows[col])})
                for country, country_data in subset.groupby("country", sort=True):
                    country_rows.append({"population": population, "country": country,
                                         "country_name": country_data.country_name.iloc[0],
                                         "group": country_data.group.iloc[0], "dimension": axis, "sign": sign,
                                         "outlets": len(country_data), "articles": int(country_data.n.sum()),
                                         "contains_small_outlet": bool(country_data.small_sample.any()),
                                         **{k: v for k, v in describe(country_data[col]).items() if k != "N"}})
    country = pd.DataFrame(country_rows)
    for (population, group, axis, sign), sub in country.loc[country.outlets >= 2].groupby(
            ["population", "group", "dimension", "sign"], sort=False):
        country_stats.append({"population": population, "group": group, "dimension": axis, "sign": sign,
                              **describe(sub.sample_sd)})
    checks = {"eligible_country_months": len(eligible), "eligible_articles": int(rows.n.sum()),
              "eligible_nonempty_outlet_months": len(rows), "exact_domains": len(outlets),
              "domains_assigned_to_multiple_countries": 0, "outlets_total_n_below_30": int(outlets.small_sample.sum()),
              "outlets_by_group": outlets.groupby("group").size().to_dict(),
              "small_outlets_by_group": outlets.loc[outlets.small_sample].groupby("group").size().to_dict(),
              "outlet_article_totals_reconcile": bool(outlets.n.sum() == rows.n.sum()),
              "country_counts_reconcile_all_nine_labels_and_n": True,
              "country_supplement_N": country.loc[(country.population == "all_outlets") &
                                                  (country.dimension == "frame") & (country.sign == "negative") &
                                                  (country.outlets >= 2)].groupby("group").size().to_dict()}
    tail = []
    stable = outlets.loc[outlets.n >= 30]
    for group in base.GROUPS:
        sub = stable.loc[stable.group == group]
        above = int((sub.frame_negative_share > .20).sum())
        tail.append({"group": group, "outlets": len(sub), "above_20_percent": above,
                     "fraction_above": above / len(sub)})
    without_nic = stable.loc[(stable.group == "low") & (stable.country != "NIC")]
    low_country = country.loc[(country.population == "outlet_total_n_ge_30") &
                             (country.group == "low") & (country.country != "NIC") &
                             (country.dimension == "frame") & (country.sign == "negative") &
                             (country.outlets >= 2)]
    checks["negative_framing_tail_n_ge_30"] = tail
    checks["low_without_nicaragua_n_ge_30"] = {
        "outlets": len(without_nic), "above_20_percent": int((without_nic.frame_negative_share > .20).sum()),
        "fraction_above": float((without_nic.frame_negative_share > .20).mean()),
        "countries_with_two_outlets": len(low_country),
        "median_within_country_outlet_sd": float(low_country.sample_sd.median()),
    }
    assert [(r["above_20_percent"], r["outlets"]) for r in tail] == [(26, 146), (5, 125), (5, 116)]
    assert len(without_nic) == 139 and (without_nic.frame_negative_share > .20).sum() == 21
    return outlets, pd.DataFrame(outlet_stats), country, pd.DataFrame(country_stats), checks


def jitter(identity):
    return (int(hashlib.sha256(identity.encode()).hexdigest()[:8], 16) / (2**32-1) - .5) * .46


def tick(value, _):
    return f"{value*100:.1f}".rstrip("0").rstrip(".") + "%"


def make_figure(outlets, country, within=False):
    fig, axes = plt.subplots(2, 3, figsize=(16, 10.1))
    fig.subplots_adjust(left=.065, right=.985, top=.80, bottom=.22, hspace=.38, wspace=.24)
    fig.text(.065, .95, "Variation between outlets within countries" if within else "Variation in coverage across media outlets",
             fontsize=24, weight="bold")
    fig.text(.065, .91, "Domestic coverage of the incumbent · January 2022–December 2025", fontsize=14)
    fig.text(.065, .875, "One point per country: spread of its outlets’ coverage rates" if within else
             "One point per outlet: sign count divided by its total articles in the eligible sample", fontsize=12.5)
    for row, sign in enumerate(SIGN_ORDER):
        for col, axis in enumerate(base.AXES):
            ax = axes[row, col]
            if row == 0:
                ax.set_title(base.TITLES[axis], loc="left", fontsize=17, weight="bold", pad=17)
            panel_values = []
            for position, group in enumerate(base.GROUPS, start=1):
                if within:
                    sub = country.loc[(country.population == "all_outlets") & (country.group == group) &
                                      (country.dimension == axis) & (country.sign == sign) & (country.outlets >= 2)]
                    values = sub.sample_sd
                    small = sub.contains_small_outlet
                    ids = sub.country
                else:
                    sub = outlets.loc[outlets.group == group]
                    values = sub[f"{axis}_{sign}_share"]
                    small = sub.small_sample
                    ids = sub.source_domain
                panel_values.extend(values)
                color = base.COLORS[group]
                box = ax.boxplot([values], positions=[position], widths=.52, showfliers=False,
                                 patch_artist=True, medianprops={"color": "#182d40", "linewidth": 1.6},
                                 whiskerprops={"color": color, "linewidth": 1.1},
                                 capprops={"color": color, "linewidth": 1.1}, zorder=2)
                box["boxes"][0].set(facecolor=color, edgecolor=color, alpha=.19)
                x = np.array([position+jitter(s) for s in ids])
                ax.scatter(x[~small], values[~small], s=22 if not within else 31,
                           color=color, edgecolor="white", linewidth=.35, alpha=.80, zorder=3)
                ax.scatter(x[small], values[small], s=32 if not within else 38, facecolors="none",
                           edgecolors="#7d8389", linewidth=1.1, zorder=4)
                ax.scatter([position], [values.mean()], marker="D", s=37, color="#172c3c",
                           edgecolor="white", linewidth=.65, zorder=5)
            group_counts = ([len(country.loc[(country.population == "all_outlets") & (country.group == g) &
                                           (country.dimension == axis) & (country.sign == sign) & (country.outlets >= 2)])
                             for g in base.GROUPS] if within else [int((outlets.group == g).sum()) for g in base.GROUPS])
            ax.set_xticks([1, 2, 3], [f"{g.capitalize()}\n(n={n})" for g, n in zip(base.GROUPS, group_counts)])
            ax.set_xlim(.52, 3.48)
            ax.set_ylim(0, max(panel_values)*1.10 if max(panel_values) else .01)
            ax.yaxis.set_major_formatter(FuncFormatter(
                (lambda value, _: f"{value*100:.1f}".rstrip("0").rstrip(".")) if within else tick))
            ax.yaxis.set_major_locator(MaxNLocator(nbins=5, steps=[1, 2, 2.5, 5, 10]))
            ax.grid(axis="y", alpha=.18, zorder=0)
            for edge in ("top", "right"):
                ax.spines[edge].set_visible(False)
            ax.spines["left"].set_color("#cbd1d7")
            ax.spines["bottom"].set_color("#cbd1d7")
            ax.tick_params(axis="both", labelsize=11)
            if col == 0:
                ax.set_ylabel(f"{sign.capitalize()}: outlet SD (pp)" if within else f"{sign.capitalize()} share", fontsize=12)
    fig.text(.065, .125, "Boxes: middle 50%; line: median; diamond: mean. Every point is shown. Vertical scales differ across panels.", fontsize=11)
    fig.text(.065, .090, "Gray open points: countries containing an outlet with fewer than 30 articles." if within else
             "Gray open points: 14 outlets with fewer than 30 articles; these remain in the boxes and statistics.", fontsize=11)
    fig.text(.065, .055, "Low/Middle/High: relative V-Dem media-freedom groups. Country-month n ≥ 30; all nonempty outlet-months retained, including zero labels.", fontsize=10.6)
    fig.text(.065, .020, "Rates pool each outlet’s observed months. The spread includes differences in events covered, collection and editorial choices.", fontsize=10.6)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    outlets, stats, country, spread_stats, checks = calculate()
    if args.check_only:
        print(json.dumps(checks, indent=2))
        return
    outputs = []
    for suffix, frame in (("outlet_rates", outlets), ("outlet_distribution_stats", stats),
                          ("within_country_outlet_spread", country), ("within_country_spread_stats", spread_stats)):
        path = DATA / f"20_media_freedom_{suffix}.csv"
        frame.to_csv(path, index=False, na_rep="", float_format="%.12g", lineterminator="\n")
        outputs.append(path)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "text.color": "#202b36",
                         "axes.labelcolor": "#202b36", "xtick.color": "#49545f", "ytick.color": "#49545f",
                         "svg.fonttype": "none", "svg.hashsalt": "outlet-variation-nov4-v1"})
    outputs += base.save_figure(make_figure(outlets, country), FIGURES, "20_media_freedom_outlet_variation")
    outputs += base.save_figure(make_figure(outlets, country, within=True), FIGURES, "20_media_freedom_within_country_variation")
    manifest = {
        "title": "Variation in negative and positive domestic coverage across media outlets",
        "snapshot": "2026-11-04T13:38:01.213139+00:00", "period": ["2022-01", "2025-12"],
        "inputs": {key: {"path": base.path_label(DATA/name), "sha256": expected} for key, (name, expected) in INPUTS.items()},
        "scripts": [{"path": base.path_label(p), "sha256": base.sha(p)} for p in (Path(__file__), Path(base.__file__))],
        "checks": checks,
        "methods": {
            "selection": "Publication country equals evaluated-government country. Fixed 71-country groups. Retain country-months with n>=30, then all their nonempty outlet-months without a further monthly threshold.",
            "point": "One exact source domain, not a corporate parent or ownership family. Each domain belongs to one publication country in this extract.",
            "outlet_rate": "Sum of sign counts across the outlet's eligible observed months / sum of all its articles over those same months. A pooled period share, not a mean of monthly rates. Zero labels remain in the denominator.",
            "main_distribution": "Equal weight per outlet. Boxplot and summary mean/SD describe the outlet distribution; they do not reproduce equal-country monthly group means in figures16/19.",
            "within_country": "Calculate sample SD (ddof=1) of the pooled outlet rates within each country; countries with fewer than two outlets have undefined SD and are excluded from this plot. Each retained country has equal weight in the supplement.",
            "small_samples": "Retain all outlets in both figures. Gray open dots identify outlet total n<30, or countries containing such an outlet. CSVs separately report calculations after removing outlets with total n<30; this is a sensitivity check, not a change to the main sample.",
            "statistics": "Sample SD uses ddof=1; quartiles use linear interpolation; IQR=Q3-Q1. All numerical CSV rates and SDs use 0-to-1 units; multiply by100 for percentages or percentage points.",
            "boxplot": "Box=Q1 toQ3; line=median; whiskers=endmost observations within1.5IQR; diamond=mean; all observations shown as country/domain-stable jittered dots.",
            "labels": "Low/Middle/High are relative groups based on each country's mean2022–2025 V-Dem v2x_freexp_altinf, with fixed24/23/24countries. They are not absolute classifications of media freedom.",
        },
        "limitations": [
            "Between-outlet dispersion pooled within a freedom group combines within-country and between-country differences; the supplement isolates variation among the observed outlets within each country.",
            "Outlets do not necessarily cover the same months or events; pooled rates reflect their observed time and story mix.",
            "Small samples can create extreme rates. Source domains, genre inclusion and collection gaps are not audited here.",
            "Higher dispersion does not mechanically cause a higher mean; a few high-rate outlets can raise both. Negative coverage alone does not establish media bias.",
            "No population inference, uncertainty intervals, audience weights, temporal-volatility estimates or causal effects are claimed.",
        ],
        "outputs": [{"path": base.path_label(p), "sha256": base.sha(p), "bytes": p.stat().st_size} for p in outputs],
    }
    (DATA / "20_media_freedom_variation_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
