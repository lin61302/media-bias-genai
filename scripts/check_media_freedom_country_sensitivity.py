#!/usr/bin/env python3
"""Check how individual countries affect the domestic negative-framing means.

Uses only the frozen aggregate CSVs already in this repository. No network,
database, model, outlet-level or article-text access. The reference plot gives
eligible countries equal weight each month; this script preserves that estimator
and its fixed freedom groups when removing one country at a time.

Run: python scripts/check_media_freedom_country_sensitivity.py
Use --check-only to calculate and verify without writing outputs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "slides/figures/data"
MONTHS = [f"{year}-{month:02d}" for year in range(2022, 2026)
          for month in range(1, 13)]
GROUPS = ("low", "middle", "high")
MIN_N = 30
INPUTS = {
    "country_month_counts": ("16_media_freedom_country_month.csv",
        "af6d0eda1df59818d8c150978ff84508ba4be0bd7d6e3909cfd4e0bd9a6b230d"),
    "fixed_country_groups": ("16_media_freedom_groups.csv",
        "050b0355857b2859383ac9596a5b2eb1a357f068417d46d96076ca3325d533a9"),
    "reference_monthly_series": ("16_media_freedom_monthly_series.csv",
        "4058f61320afab8487dea2d08bab56ae62251ebda279ba14c118824ffab446ae"),
    "extraction_provenance": ("16_media_freedom_extraction_provenance.json",
        "7550f1b3169e51920a3bedfc2b374d79d74bd52ed8de7b6e700d131cf8cd4589"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def csv_rows(name: str) -> list[dict]:
    with (DATA / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def load_inputs() -> tuple[dict, dict, dict]:
    provenance = {}
    for key, (name, expected) in INPUTS.items():
        path = DATA / name
        actual = sha(path)
        if actual != expected:
            raise ValueError(f"Frozen input changed: {path}; got {actual}")
        provenance[key] = {"path": relative(path), "sha256": actual}
    group_rows = csv_rows(INPUTS["fixed_country_groups"][0])
    countries = {row["country"]: row for row in group_rows}
    if len(countries) != len(group_rows) or len(countries) != 71:
        raise ValueError("Expected 71 unique countries in the fixed groups")
    if Counter(r["group"] for r in group_rows) != {"low": 24, "middle": 23, "high": 24}:
        raise ValueError("Fixed group sizes differ from 24/23/24")
    counts = {}
    for row in csv_rows(INPUTS["country_month_counts"][0]):
        if row["scope"] not in ("domestic", "domestic_only"):
            continue
        country, month = row["country"], row["month"]
        if country not in countries or month not in MONTHS:
            continue
        key = (country, month)
        if key in counts:
            raise ValueError(f"Duplicate domestic country-month: {key}")
        values = {name: int(row[name]) for name in ("n", "frame_negative", "frame_zero", "frame_positive")}
        if min(values.values()) < 0 or sum(values[k] for k in values if k != "n") != values["n"]:
            raise ValueError(f"Invalid framing counts: {key}")
        counts[key] = values
    if set(counts) != {(country, month) for country in countries for month in MONTHS}:
        raise ValueError("Expected complete 71-country, 48-month domestic count grid")
    return countries, counts, provenance


def calculate(countries: dict, counts: dict) -> tuple[list, list, dict]:
    members = {g: sorted(c for c, row in countries.items() if row["group"] == g)
               for g in GROUPS}
    eligible = {key: row for key, row in counts.items() if row["n"] >= MIN_N}
    shares = {key: row["frame_negative"] / row["n"] for key, row in eligible.items()}
    active = {(g, m): [c for c in members[g] if (c, m) in eligible]
              for g in GROUPS for m in MONTHS}

    def series(removed: str | None = None) -> dict:
        return {(g, m): mean(shares[c, m] for c in active[g, m] if c != removed)
                for g in GROUPS for m in MONTHS}

    def summarize(values: dict) -> dict:
        out = {f"{g}_mean_negative_framing_share": mean(values[g, m] for m in MONTHS)
               for g in GROUPS}
        out["low_minus_high_gap_pp"] = 100 * (
            out["low_mean_negative_framing_share"] - out["high_mean_negative_framing_share"])
        out["low_above_high_months"] = sum(values["low", m] > values["high", m] for m in MONTHS)
        out["low_highest_months"] = sum(values["low", m] > max(values["middle", m], values["high", m])
                                        for m in MONTHS)
        out["high_above_low_months"] = sum(values["high", m] > values["low", m] for m in MONTHS)
        out["months_compared"] = len(MONTHS)
        return out

    baseline_series = series()
    baseline = summarize(baseline_series)
    references = [r for r in csv_rows(INPUTS["reference_monthly_series"][0]) if r["scope"] == "domestic"]
    if len(references) != len(GROUPS) * len(MONTHS):
        raise ValueError("Expected 144 domestic group-month reference rows")
    errors = []
    for row in references:
        key = row["group"], row["month"]
        errors.append(abs(baseline_series[key] - float(row["frame_negative_share"])))
        if row["contributing_country_codes"] != "|".join(active[key]):
            raise ValueError(f"Country support differs from plot: {key}")
    if max(errors) > 1e-11:
        raise ValueError(f"Monthly means differ from the plot; maximum error {max(errors)}")

    country_rows = []
    for country, metadata in sorted(countries.items()):
        group = metadata["group"]
        months = [m for m in MONTHS if (country, m) in eligible]
        if not months:
            raise ValueError(f"Country never reaches the article threshold: {country}")
        n = sum(eligible[country, m]["n"] for m in months)
        negative = sum(eligible[country, m]["frame_negative"] for m in months)
        # Missing/below-threshold country-months have no contribution, not a zero share.
        weights = [1 / len(active[group, m]) if m in months else 0 for m in MONTHS]
        contribution = mean(shares[country, m] / len(active[group, m])
                            if m in months else 0 for m in MONTHS)
        country_rows.append({
            "country": country, "country_name": metadata["country_name"], "group": group,
            "eligible_months_at_least_30": len(months), "months_below_threshold": len(MONTHS) - len(months),
            "included_articles": n, "included_negative_framing_articles": negative,
            "all_months_eligible_articles": sum(counts[country, m]["n"] for m in MONTHS),
            "mean_monthly_negative_framing_share": mean(shares[country, m] for m in months),
            "pooled_negative_framing_share": negative / n,
            "minimum_included_month_articles": min(eligible[country, m]["n"] for m in months),
            "maximum_included_month_articles": max(eligible[country, m]["n"] for m in months),
            "mean_monthly_weight_across_48_months": mean(weights),
            "contribution_to_group_mean_pp": 100 * contribution,
            "fraction_of_group_mean": contribution / baseline[f"{group}_mean_negative_framing_share"],
        })
    by_country = {r["country"]: r for r in country_rows}
    for group in GROUPS:
        contribution_sum = sum(r["contribution_to_group_mean_pp"] for r in country_rows if r["group"] == group)
        if abs(contribution_sum - 100 * baseline[f"{group}_mean_negative_framing_share"]) > 1e-10:
            raise ValueError(f"Country contributions do not reconstruct the {group} mean")

    leave_out_rows = []
    for country, metadata in sorted(countries.items()):
        result = summarize(series(country))
        leave_out_rows.append({
            "removed_country": country, "country_name": metadata["country_name"], "group": metadata["group"],
            "removed_eligible_months": by_country[country]["eligible_months_at_least_30"],
            "removed_articles": by_country[country]["included_articles"], **result,
            "gap_change_from_full_sample_pp": result["low_minus_high_gap_pp"] - baseline["low_minus_high_gap_pp"],
        })
    diagnostics = {
        "baseline": baseline,
        "without_nicaragua": next(r for r in leave_out_rows if r["removed_country"] == "NIC"),
        "mean_of_monthly_country_medians": {
            g: mean(median(shares[c, m] for c in active[g, m]) for m in MONTHS) for g in GROUPS},
        "country_contributions_sum_to_group_means": True,
        "reference_monthly_means_checked": len(errors), "maximum_reference_absolute_error": max(errors),
        "countries_whose_removal_reverses_low_high_gap": [r["removed_country"] for r in leave_out_rows
            if r["low_minus_high_gap_pp"] * baseline["low_minus_high_gap_pp"] < 0],
        "minimum_leave_one_out_gap_pp": min(r["low_minus_high_gap_pp"] for r in leave_out_rows),
        "maximum_leave_one_out_gap_pp": max(r["low_minus_high_gap_pp"] for r in leave_out_rows),
    }
    return country_rows, leave_out_rows, diagnostics


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Verify and calculate without writing outputs")
    args = parser.parse_args()
    countries, counts, inputs = load_inputs()
    country_rows, leave_out_rows, diagnostics = calculate(countries, counts)
    if not args.check_only:
        outputs = []
        for name, rows in (("16_media_freedom_country_sensitivity.csv", country_rows),
                           ("16_media_freedom_leave_one_country_out.csv", leave_out_rows)):
            path = DATA / name
            write_csv(path, rows)
            outputs.append({"path": relative(path), "rows": len(rows), "sha256": sha(path)})
        manifest = {
            "title": "Country sensitivity of domestic negative framing by media freedom",
            "snapshot": "2026-11-04T13:38:01.213139+00:00",
            "period": [MONTHS[0], MONTHS[-1]], "scope": "publication_country == evaluated government",
            "inputs": inputs, "script": {"path": relative(Path(__file__)), "sha256": sha(Path(__file__))},
            "methods": {
                "eligibility": "Identified government/action and numeric -1/0/+1 labels; zeros retained. Domestic country-month n >= 30.",
                "country_mean": "Mean of that country's negative-framing shares over its eligible months. Pooled count share is separately labeled.",
                "group_mean": "Each month's equal-country mean, then arithmetic mean across all 48 months. No smoothing in sensitivity summaries.",
                "monthly_weight": "1 / number of eligible countries in the fixed group in that month; zero contribution when ineligible.",
                "country_contribution": "Mean across all 48 months of monthly country share times its monthly weight; reported in percentage points.",
                "leave_one_out": "Remove one country from all months; recompute its group's equal-country means. Remaining memberships, threshold and months stay fixed; no regrouping.",
                "comparison": "Low minus high group mean, in percentage points. Monthly rank counts use unsmoothed means and strict greater-than comparisons.",
                "share_units": "Fractions from 0 to 1 unless the column ends in _pp; multiply fractions by 100 for percentages.",
            },
            "diagnostics": diagnostics,
            "limits": [
                "A sensitivity diagnostic, not a preferred estimator or a reason to discard a country.",
                "These counts cannot identify which outlets, genres, events or coding decisions explain a country's rate.",
                "Equal-country weighting answers a different question from pooling all articles. Within country-months, included articles remain pooled across sources.",
                "Fixed media-freedom groups are descriptive; no causal effect or population-representative country coverage is established.",
            ],
            "outputs": outputs,
            "operations": {"network_calls": 0, "model_calls": 0, "database_calls": 0, "article_text_access": False},
        }
        (DATA / "16_media_freedom_country_sensitivity_manifest.json").write_text(
            json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    print(json.dumps(diagnostics, indent=2, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(f"Error: {error}") from error
