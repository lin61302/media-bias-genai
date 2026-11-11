#!/usr/bin/env python3
"""Rebuild domestic media-freedom figures from frozen, aggregate article counts.

No model, database or private-text access. Default execution is offline; the
optional --fetch-inputs flag downloads only missing, hash-pinned public context
and source-country JSON files. The November 4 context, source-country metadata
and all-origins reference CSV are hash-pinned. The input
CSV supplies both all-origins and domestic counts; domestic means publication
country equals evaluated-government country. This script cannot independently
recover that article-level filter from aggregates: retain the extraction receipt.

Run: python scripts/build_domestic_media_freedom.py
Only PNG/SVG figures are authored; no PDF is generated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter, MultipleLocator
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "slides/figures/data"
FIGURES = ROOT / "slides/figures"
INPUT = DATA / "16_media_freedom_country_month.csv"
INPUT_SHA = "af6d0eda1df59818d8c150978ff84508ba4be0bd7d6e3909cfd4e0bd9a6b230d"
EXTRACTION = DATA / "16_media_freedom_extraction_provenance.json"
EXTRACTION_SHA = "7550f1b3169e51920a3bedfc2b374d79d74bd52ed8de7b6e700d131cf8cd4589"
CONTEXT = ROOT / "data/cache/country_context.json"
SOURCE_META = ROOT / "data/cache/explore-meta.json"
REFERENCE = ROOT / "data/polarization/monthly_polarization_all_countries.csv"
CONTEXT_SHA = "20a7c94a6e4fe998c89ef2be2ff9472468c38409b1cab36ca52947e45e8e7cda"
SOURCE_META_SHA = "e28aa6b9cf6d3b0267b7417cd4d82ae11de84f64120da7ce011082a644669cdc"
REFERENCE_SHA = "9e70e773c22fab5f9d9d365d5344e3669a78afee5a3ac2f7df0f9a6b7775f965"
PUBLIC_BASE = "https://huggingface.co/spaces/zungru/media-bias-reported-polarization/resolve/8ce2764cffe71c66222fb46a98d2f8d18f9d0135/"
MONTHS = pd.period_range("2022-01", "2025-12", freq="M").astype(str).tolist()
MIN_N = 30
AXES = ("align", "rep", "frame")
SIGNS = ("negative", "zero", "positive")
COUNT_COLUMNS = ["n"] + [f"{a}_{s}" for a in AXES for s in SIGNS]
GROUPS = ("low", "middle", "high")
SCOPES = ("all_origins", "domestic")
SCOPE_ALIASES = {
    "all_origins": "all_origins", "allorigins": "all_origins",
    "all": "all_origins", "all_sources": "all_origins",
    "domestic": "domestic", "domestic_only": "domestic",
    "same_country": "domestic", "publication_equals_government": "domestic",
}
COLORS = {"low": "#80b3f5", "middle": "#2f7fdf", "high": "#1c4f88"}
NAMES = {"low": "Low media freedom", "middle": "Middle media freedom",
         "high": "High media freedom"}
TITLES = {"align": "Political alignment", "rep": "Reputational implication",
          "frame": "Framing"}
SUBTITLES = {"align": "Reported actions opposing the incumbent",
             "rep": "Unfavorable implications for the government",
             "frame": "Critical evaluation in title or narration"}
LONG_AXES = {"align": "alignment", "rep": "reputation", "frame": "framing"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def path_label(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def check_hash(path: Path, expected: str) -> None:
    if not path.is_file():
        raise ValueError(f"Missing frozen input: {path}")
    actual = sha(path)
    if actual != expected:
        raise ValueError(f"Hash mismatch for {path}: expected {expected}, got {actual}")


def fetch_missing_context(enabled: bool) -> list[dict]:
    downloaded = []
    for path, expected in ((CONTEXT, CONTEXT_SHA), (SOURCE_META, SOURCE_META_SHA)):
        if path.is_file():
            check_hash(path, expected)
            continue
        if not enabled:
            raise ValueError(f"Missing cached input: {path}. Use --fetch-inputs to obtain the pinned public file.")
        from urllib.request import urlopen
        url = PUBLIC_BASE + path.name
        with urlopen(url, timeout=60) as response:
            content = response.read()
        actual = hashlib.sha256(content).hexdigest()
        if actual != expected:
            raise ValueError(f"Downloaded hash mismatch for {url}: {actual}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        downloaded.append({"path": path_label(path), "url": url, "sha256": actual})
    return downloaded


def country_groups() -> tuple[pd.DataFrame, dict]:
    check_hash(CONTEXT, CONTEXT_SHA)
    check_hash(SOURCE_META, SOURCE_META_SHA)
    context = json.loads(CONTEXT.read_text())
    meta = json.loads(SOURCE_META.read_text())
    countries = sorted({v["country"] for v in meta["sources"].values()
                        if v.get("country") and v["country"] != "ALL"})
    if len(countries) != 71:
        raise ValueError(f"Expected 71 source countries, got {len(countries)}")
    rows = []
    for country in countries:
        r = {"country": country, "country_name": context["countries"][country]["name"]}
        for year in range(2022, 2026):
            value = context["country_year"].get(f"{country}_{year}", {}).get("v2x_freexp_altinf")
            if value is None or not np.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"Missing or invalid media freedom: {country}, {year}")
            r[f"freedom_{year}"] = value
        r["mean_freedom_2022_2025"] = np.mean([r[f"freedom_{y}"] for y in range(2022, 2026)])
        rows.append(r)
    groups = pd.DataFrame(rows).sort_values(["mean_freedom_2022_2025", "country"])
    groups["group"], cutpoints = pd.qcut(groups["mean_freedom_2022_2025"],
                                         q=3, labels=GROUPS, retbins=True)
    groups["group"] = groups["group"].astype(str)
    sizes = groups.groupby("group").size().to_dict()
    if sizes != {"low": 24, "middle": 23, "high": 24}:
        raise ValueError(f"Unexpected fixed group sizes: {sizes}")
    groups["fixed_group_countries"] = groups["group"].map(sizes)
    details = {g: {"fixed_countries": sizes[g],
                   "score_min": float(groups.loc[groups.group == g, "mean_freedom_2022_2025"].min()),
                   "score_max": float(groups.loc[groups.group == g, "mean_freedom_2022_2025"].max()),
                   "countries": sorted(groups.loc[groups.group == g, "country"].tolist())}
               for g in GROUPS}
    return groups.reset_index(drop=True), {
        "groups": details, "quantile_edges": cutpoints.tolist(),
        "context_provenance": context["provenance"],
    }


def normalize_scope(value: str) -> str:
    key = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    if key not in SCOPE_ALIASES:
        raise ValueError(f"Unknown scope {value!r}; expected all_origins or domestic")
    return SCOPE_ALIASES[key]


def load_counts(path: Path, countries: list[str]) -> tuple[pd.DataFrame, dict]:
    if not path.is_file():
        raise ValueError(f"Missing count CSV: {path}. Obtain the frozen aggregate export first.")
    df = pd.read_csv(path, dtype={"scope": str, "country": str, "month": str})
    required = {"scope", "country", "month", *COUNT_COLUMNS}
    if required - set(df.columns):
        raise ValueError(f"Missing CSV columns: {sorted(required - set(df.columns))}")
    if df[["scope", "country", "month"]].isna().any().any():
        raise ValueError("Scope, country and month must be populated")
    df["scope"] = df.scope.map(normalize_scope)
    df["country"] = df.country.str.strip().str.upper()
    df["month"] = df.month.str.strip()
    if not df.month.str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])").all():
        raise ValueError("Months must use valid YYYY-MM strings")
    if df.duplicated(["scope", "country", "month"]).any():
        raise ValueError("Duplicate scope/country/month rows after scope normalization")
    for col in COUNT_COLUMNS:
        values = pd.to_numeric(df[col], errors="raise")
        if not (np.isfinite(values).all() and (values >= 0).all() and (values == np.floor(values)).all()):
            raise ValueError(f"{col} must contain nonnegative integer counts")
        df[col] = values.astype("int64")
    for axis in AXES:
        if not (df[[f"{axis}_{s}" for s in SIGNS]].sum(axis=1) == df.n).all():
            raise ValueError(f"{axis} counts do not sum to n on every input row")
    if set(df.scope) != set(SCOPES):
        raise ValueError("Both all_origins and domestic scopes are required")
    selected = df.country.isin(countries) & df.month.isin(MONTHS)
    selection = {
        "input_rows": len(df), "selected_input_rows": int(selected.sum()),
        "out_of_period_rows": int((~df.month.isin(MONTHS)).sum()),
        "outside_71_country_scope_rows_in_period": int((df.month.isin(MONTHS) & ~df.country.isin(countries)).sum()),
        "outside_71_country_codes_in_period": sorted(df.loc[df.month.isin(MONTHS) & ~df.country.isin(countries), "country"].unique().tolist()),
    }
    df = df.loc[selected, ["scope", "country", "month", *COUNT_COLUMNS]].copy()
    df["input_row_present"] = True
    index = pd.MultiIndex.from_product([SCOPES, countries, MONTHS], names=["scope", "country", "month"])
    df = df.set_index(["scope", "country", "month"]).reindex(index)
    df["input_row_present"] = df.input_row_present.notna()
    # Omitted cells have no contributing observations; they never become zero shares.
    df[COUNT_COLUMNS] = df[COUNT_COLUMNS].fillna(0).astype("int64")
    domestic = df.xs("domestic").loc[:, COUNT_COLUMNS]
    all_origins = df.xs("all_origins").loc[:, COUNT_COLUMNS]
    if (domestic > all_origins).any().any():
        raise ValueError("Domestic counts exceed all-origins counts in at least one cell/label")
    selection["missing_input_cells_by_scope"] = {
        scope: int((~df.xs(scope).input_row_present).sum()) for scope in SCOPES}
    return df.reset_index(), selection


def verify_reference(df: pd.DataFrame) -> dict:
    """Validate all selected all-origin cells against the independently saved Nov4 export."""
    check_hash(REFERENCE, REFERENCE_SHA)
    ref = pd.read_csv(REFERENCE, dtype={"government_country_code": str, "month": str})
    ref = ref.set_index(["government_country_code", "month"])
    all_rows = df.loc[df.scope == "all_origins"]
    checked = 0
    for row in all_rows.itertuples(index=False):
        key = (row.country, row.month)
        if key not in ref.index:
            raise ValueError(f"Missing reference country-month {key}")
        other = ref.loc[key]
        if int(other.eligible_articles) != row.n:
            raise ValueError(f"All-origins denominator differs from Nov4 export at {key}")
        for axis in AXES:
            for sign in SIGNS:
                expected = 0 if row.n == 0 else float(other[f"{LONG_AXES[axis]}_{sign}_share"]) * row.n
                if not np.isfinite(expected) or abs(expected - getattr(row, f"{axis}_{sign}")) > 1e-6:
                    raise ValueError(f"All-origins {axis}/{sign} differs from Nov4 export at {key}")
        checked += 1
    return {"path": path_label(REFERENCE), "sha256": sha(REFERENCE),
            "country_months_checked": checked, "counts_and_all_nine_margins_match": True}


def monthly_series(df: pd.DataFrame, groups: pd.DataFrame, *, shared: bool) -> pd.DataFrame:
    frame = df.merge(groups[["country", "group"]], on="country", validate="many_to_one")
    support = frame.pivot(index=["country", "month"], columns="scope", values="n")
    common = support.ge(MIN_N).all(axis=1)
    frame["passes_threshold"] = frame.n >= MIN_N
    frame["common_support"] = [bool(common.loc[c, m]) for c, m in zip(frame.country, frame.month)]
    rows = []
    for scope in SCOPES:
        for group in GROUPS:
            n_fixed = int((groups.group == group).sum())
            for month in MONTHS:
                cells = frame.loc[(frame.scope == scope) & (frame.group == group) & (frame.month == month)]
                contributing = cells.loc[cells.common_support if shared else cells.passes_threshold]
                row = {"scope": scope, "group": group, "month": month,
                       "contributing_countries": len(contributing), "fixed_group_countries": n_fixed,
                       "eligible_articles": int(contributing.n.sum()),
                       "contributing_country_codes": "|".join(sorted(contributing.country)),
                       "observed_country_cells": int(cells.input_row_present.sum()),
                       "countries_below_threshold": int((cells.n < MIN_N).sum())}
                for axis in AXES:
                    row[f"{axis}_negative_share"] = ((contributing[f"{axis}_negative"] / contributing.n).mean()
                                                       if len(contributing) else np.nan)
                rows.append(row)
    result = pd.DataFrame(rows)
    for axis in AXES:
        result[f"{axis}_negative_share_centered3"] = result.groupby(["scope", "group"], sort=False)[
            f"{axis}_negative_share"].transform(lambda s: s.rolling(3, center=True, min_periods=3).mean())
    return result


def shared_comparison(series: pd.DataFrame) -> pd.DataFrame:
    left = series.loc[series.scope == "all_origins"].set_index(["group", "month"])
    right = series.loc[series.scope == "domestic"].set_index(["group", "month"])
    if not left.contributing_country_codes.equals(right.contributing_country_codes):
        raise ValueError("Common-support country sets differ unexpectedly")
    out = left[["contributing_countries", "fixed_group_countries", "contributing_country_codes"]].copy()
    for scope, sub in (("all_origins", left), ("domestic", right)):
        out[f"{scope}_eligible_articles"] = sub.eligible_articles
        for axis in AXES:
            for ending in ("negative_share", "negative_share_centered3"):
                out[f"{scope}_{axis}_{ending}"] = sub[f"{axis}_{ending}"]
    for axis in AXES:
        for ending in ("negative_share", "negative_share_centered3"):
            out[f"domestic_minus_all_origins_{axis}_{ending}"] = right[f"{axis}_{ending}"] - left[f"{axis}_{ending}"]
    return out.reset_index()


def panel(ax, series: pd.DataFrame, scope: str, axis: str, upper: float) -> None:
    x = np.arange(len(MONTHS))
    for group in GROUPS:
        s = series.loc[(series.scope == scope) & (series.group == group)].set_index("month").loc[MONTHS]
        ax.plot(x, s[f"{axis}_negative_share"], color=COLORS[group], linewidth=1.05, alpha=.30)
        ax.plot(x, s[f"{axis}_negative_share_centered3"], color=COLORS[group], linewidth=2.8)
    ax.set_ylim(0, upper)
    ax.set_xlim(-.5, 47.5)
    ax.set_xticks([0, 12, 24, 36], ["2022", "2023", "2024", "2025"])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.yaxis.set_major_locator(MultipleLocator(.02 if upper <= .15 else .04))
    ax.grid(axis="y", color="#e1e5e9", linewidth=.75)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, pad=7)
    for side in ("left", "right", "top"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#b7bec7")


def save_figure(fig, directory: Path, stem: str) -> list[Path]:
    outputs = []
    for ext in ("png", "svg"):
        path = directory / f"{stem}.{ext}"
        metadata = {"Date": None} if ext == "svg" else {"Software": "Frozen aggregate comparison"}
        fig.savefig(path, dpi=190, facecolor="white", metadata=metadata)
        if ext == "svg":
            path.write_text(re.sub(r"[ \t]+(?=\n)", "", path.read_text()))
        outputs.append(path)
    plt.close(fig)
    return outputs


def figures(series: pd.DataFrame, group_details: dict, directory: Path) -> tuple[list[Path], dict]:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12,
                         "text.color": "#202b36", "axes.labelcolor": "#202b36",
                         "xtick.color": "#49545f", "ytick.color": "#49545f",
                         "svg.fonttype": "none", "svg.hashsalt": "domestic-media-freedom-nov4-v1"})
    upper = {}
    for axis in AXES:
        maximum = series[f"{axis}_negative_share"].max()
        if not np.isfinite(maximum):
            raise ValueError(f"No eligible country-months for {axis}")
        upper[axis] = min(1., max(.05, np.ceil(maximum * 1.04 / .025) * .025))
    handles = [Line2D([0], [0], color=COLORS[g], lw=3,
                      label=f"{NAMES[g]} · {group_details[g]['fixed_countries']} countries") for g in GROUPS]
    outputs = []
    fig, axs = plt.subplots(1, 3, figsize=(16, 5.75))
    fig.subplots_adjust(left=.06, right=.985, top=.71, bottom=.25, wspace=.25)
    fig.text(.06, .94, "Domestic coverage of the incumbent by media freedom", fontsize=23, weight="bold")
    fig.text(.06, .895, "Publication country = evaluated-government country · January 2022–December 2025", fontsize=13)
    for ax, axis in zip(axs, AXES):
        panel(ax, series, "domestic", axis, upper[axis])
        ax.set_title(TITLES[axis], loc="left", fontsize=17, fontweight="bold", pad=30)
        ax.text(0, 1.045, SUBTITLES[axis], transform=ax.transAxes, fontsize=10.5)
    axs[0].set_ylabel("Negative share · mean across countries", fontsize=12)
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.52, .105), ncol=3,
               frameon=False, fontsize=12, columnspacing=2.2)
    fig.text(.06, .065, "Thin: monthly mean. Thick: centered 3-month mean. At least 30 eligible articles per country-month.", fontsize=10.3)
    fig.text(.06, .028, "Groups are fixed; monthly participation varies. V-Dem v16, mean 2022–2025. Frozen November 4, 2026 counts.", fontsize=10.3)
    outputs += save_figure(fig, directory, "16_media_freedom_domestic")

    fig, axs = plt.subplots(2, 3, figsize=(16, 9.2))
    fig.subplots_adjust(left=.075, right=.985, top=.78, bottom=.16, hspace=.50, wspace=.25)
    fig.text(.075, .96, "Coverage by media freedom: changing the source restriction", fontsize=22, weight="bold")
    fig.text(.075, .915, "Same 71 country groups and time window · Identical vertical scales within each column", fontsize=13)
    for i, scope in enumerate(SCOPES):
        for ax, axis in zip(axs[i], AXES):
            panel(ax, series, scope, axis, upper[axis])
            if i == 0:
                ax.set_title(TITLES[axis], loc="left", fontsize=17, weight="bold", pad=16)
        axs[i, 0].set_ylabel("Negative share", fontsize=12)
    fig.text(.075, .855, "All source origins", fontsize=14, weight="bold")
    fig.text(.075, .452, "Domestic only: publication country = evaluated government", fontsize=14, weight="bold")
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.52, .073), ncol=3,
               frameon=False, fontsize=12, columnspacing=2.2)
    fig.text(.075, .048, "Monthly equal-country means; thin = monthly, thick = centered 3-month mean. Threshold ≥30 is applied separately in each scope.", fontsize=10)
    fig.text(.075, .022, "Country participation can change between rows. The accompanying same-support CSV compares identical country-month sets. November 4, 2026 snapshot.", fontsize=10)
    outputs += save_figure(fig, directory, "16_media_freedom_scope_comparison")
    return outputs, upper


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--input-sha256", help="Optional required SHA-256 for the pipeline count export")
    parser.add_argument("--fetch-inputs", action="store_true",
                        help="Download missing pinned public context/source JSONs; default is offline")
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--figure-dir", type=Path, default=FIGURES)
    parser.add_argument("--check-only", action="store_true", help="Validate and calculate without writing files")
    args = parser.parse_args()
    check_hash(args.input, args.input_sha256 or INPUT_SHA)
    check_hash(EXTRACTION, EXTRACTION_SHA)
    extraction = json.loads(EXTRACTION.read_text())
    if sha(args.input) != extraction["csv"]["sha256"]:
        raise ValueError("Count CSV does not match the verified extraction receipt")
    downloaded = fetch_missing_context(args.fetch_inputs)
    groups, group_info = country_groups()
    frame, selection = load_counts(args.input, sorted(groups.country))
    reference_check = verify_reference(frame)
    series = monthly_series(frame, groups, shared=False)
    common_series = monthly_series(frame, groups, shared=True)
    common = shared_comparison(common_series)
    checks = {"all_count_margins_sum_to_n": True, "domestic_is_countwise_subset_of_all_origins": True,
              "full_calendar_months": len(MONTHS), "country_groups": group_info["groups"],
              "all_origins_reference": reference_check}
    summary = {scope: {"selected_articles": int(frame.loc[frame.scope == scope, "n"].sum()),
                       "plotted_articles": int(frame.loc[(frame.scope == scope) & (frame.n >= MIN_N), "n"].sum()),
                       "country_months_at_least_30": int(((frame.scope == scope) & (frame.n >= MIN_N)).sum())}
               for scope in SCOPES}
    if args.check_only:
        print(json.dumps({"checks": checks, "selection": selection, "summary": summary,
                          "downloaded_context_files": downloaded}, indent=2))
        return
    args.data_dir.mkdir(parents=True, exist_ok=True)
    args.figure_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    coverage_cols = ["scope", "group", "month", "contributing_countries", "fixed_group_countries",
                     "eligible_articles", "contributing_country_codes", "observed_country_cells", "countries_below_threshold"]
    for name, table in (("16_media_freedom_groups.csv", groups),
                        ("16_media_freedom_monthly_series.csv", series),
                        ("16_media_freedom_contributing_countries.csv", series[coverage_cols]),
                        ("16_media_freedom_same_support.csv", common)):
        path = args.data_dir / name
        table.to_csv(path, index=False, na_rep="", float_format="%.12g", lineterminator="\n")
        outputs.append(path)
    figure_paths, limits = figures(series, group_info["groups"], args.figure_dir)
    outputs.extend(figure_paths)
    manifest = {
        "title": "Domestic coverage of the incumbent by media freedom",
        "snapshot": {"audit_cutoff": "2026-11-04T13:38:01.213139+00:00",
                     "public_release_commit": "8ce2764cffe71c66222fb46a98d2f8d18f9d0135"},
        "inputs": {"country_month_counts": {"path": path_label(args.input), "sha256": sha(args.input)},
                   "extraction_provenance": {"path": path_label(EXTRACTION), "sha256": sha(EXTRACTION)},
                   "country_context": {"path": path_label(CONTEXT), "sha256": sha(CONTEXT)},
                   "source_metadata": {"path": path_label(SOURCE_META), "sha256": sha(SOURCE_META)},
                   "all_origins_reference": reference_check},
        "script": {"path": path_label(Path(__file__)), "sha256": sha(Path(__file__))},
        "selection": selection, "summary": summary, "checks": checks,
        "grouping": group_info,
        "methods": {
            "period": [MONTHS[0], MONTHS[-1]], "eligible_denominator": "Identified government and action; all three labels numeric -1/0/+1. Zeros retained; uncodable excluded.",
            "domestic_filter": "publication_country == evaluated government; supplied by upstream count export",
            "country_identity": "Evaluated-government country, equal to publication country in domestic scope",
            "source_scope": "71 distinct non-null source countries in pinned Nov4 source metadata; ALL origins excluded by domestic equality filter upstream",
            "country_year_values": "Last dated V-Dem Country-Date v16 observation in each year, as recorded in country_context.json",
            "group_rule": "Fixed terciles of arithmetic mean v2x_freexp_altinf across four years 2022-2025; pandas qcut; 24/23/24 countries",
            "country_month_share": "negative label count / n for each of three dimensions",
            "threshold": "n >= 30 applied after each scope restriction; the identical rule is applied to all three dimensions",
            "monthly_mean": "Arithmetic mean of eligible country-month shares within each fixed freedom group; no article-volume weighting across countries",
            "within_country": "Articles pooled across included sources; sources with more included articles receive more weight within country-month",
            "smoothing": "After monthly group means, centered 3-calendar-month arithmetic mean requiring all three values; first and last month omitted from thick line",
            "missing_months": "Complete 48-month calendar. Omitted input cells are noncontributing, not zero shares; no interpolation or bridging of missing group means",
            "common_support": "Both scopes have n >= 30 in the same country-month; both group means use those identical country sets; difference = domestic minus all origins",
            "common_support_difference_unit": "Fraction, multiply by 100 for percentage points",
            "group_sizes": "24/23/24 are fixed group membership, not monthly contributing country counts",
            "plot_units": "Negative shares formatted as percentages; no polarization index",
            "panel_y_maxima_shared_across_scopes": limits,
        },
        "limits": [
            "Reconstructed counterpart following the supplied caption; not a numerical replication of Erik's image without his code and monthly values.",
            "All-origins counts independently reconcile to the frozen public CSV; article-level domestic filtering requires the upstream extraction receipt.",
            "Source, event, genre, translation and model-label composition remain uncontrolled. This is not a causal estimate of media freedom.",
            "Fixed 2022-2025 mean groups conceal within-period institutional changes. Media freedom is not a categorical regime label.",
            "Country participation may vary by month. The common-support comparison addresses this scope difference, not selection of outlets or stories.",
        ],
        "outputs": [{"path": path_label(p), "bytes": p.stat().st_size, "sha256": sha(p)} for p in outputs],
        "operations": {"network_calls": len(downloaded), "downloaded_context_files": downloaded,
                       "model_calls": 0, "database_calls": 0, "pdf_outputs": 0},
        "software": {"pandas": pd.__version__, "numpy": np.__version__, "matplotlib": matplotlib.__version__},
    }
    manifest_path = args.data_dir / "16_media_freedom_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"manifest": path_label(manifest_path), "outputs": len(outputs), "summary": summary}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(f"Error: {error}") from error
