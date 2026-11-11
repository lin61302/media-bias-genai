"""Reconcile frozen Nicaragua outlet counts and compare country distributions.

Uses saved aggregates only. No database, provider or production calls.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "slides/figures/data"


def main():
    receipt = json.loads((DATA / "18_nicaragua_provenance_and_summary.json").read_text())
    for item in receipt["files"]:
        path = DATA / item["filename"].replace("nic_", "18_nicaragua_", 1)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
    outlets = pd.read_csv(DATA / "18_nicaragua_outlet_counts.csv")
    months = pd.read_csv(DATA / "18_nicaragua_outlet_month_counts.csv")
    count_cols = ["n"] + [f"{axis}_{sign}" for axis in ("align", "rep", "frame")
                           for sign in ("negative", "zero", "positive")]
    baseline = pd.read_csv(DATA / "16_media_freedom_country_month.csv")
    nic = baseline[(baseline.scope == "domestic_only") & (baseline.country == "NIC")]
    pd.testing.assert_frame_equal(months.groupby("month")[count_cols].sum(),
                                  nic.set_index("month")[count_cols].sort_index())
    assert (nic.n >= 30).all() and len(nic) == 48
    pd.testing.assert_frame_equal(months.groupby("source_domain")[count_cols].sum(),
                                  outlets.set_index("source_domain")[count_cols].sort_index())
    assert outlets.n.sum() == 5335 and outlets.frame_negative.sum() == 2909
    for axis in ("align", "rep", "frame"):
        assert (outlets[[f"{axis}_{s}" for s in ("negative", "zero", "positive")]].sum(axis=1) == outlets.n).all()

    countries = pd.read_csv(DATA / "16_media_freedom_country_sensitivity.csv")
    groups = pd.read_csv(DATA / "16_media_freedom_groups.csv")
    domestic = baseline[(baseline.scope == "domestic_only") & (baseline.n >= 30)].copy()
    domestic["share"] = domestic.frame_negative / domestic.n
    observed = domestic.groupby("country").share.mean().sort_index()
    assert np.allclose(observed, countries.set_index("country").loc[observed.index, "mean_monthly_negative_framing_share"], atol=1e-12)
    domestic = domestic.merge(groups[["country", "group"]], on="country", validate="many_to_one")
    full = domestic.groupby(["group", "month"]).share.mean().groupby("group").mean()
    without = domestic[domestic.country != "NIC"].groupby(["group", "month"]).share.mean().groupby("group").mean()
    distributions = {}
    for group in ("low", "middle", "high", "low_without_NIC"):
        rows = countries[countries.group == group.replace("_without_NIC", "")]
        if group.endswith("_without_NIC"):
            rows = rows[rows.country != "NIC"]
        values = rows.mean_monthly_negative_framing_share * 100
        distributions[group] = {
            "countries": len(rows), "median_pct": values.median(),
            "q1_pct": values.quantile(.25), "q3_pct": values.quantile(.75),
            "min_pct": values.min(), "max_pct": values.max(),
            "sd_pp": values.std(ddof=1),
            "top_countries": [{"country": r.country, "name": r.country_name,
                                "negative_framing_pct": r.mean_monthly_negative_framing_share * 100,
                                "months": int(r.eligible_months_at_least_30),
                                "articles": int(r.included_articles)}
                               for r in rows.nlargest(4, "mean_monthly_negative_framing_share").itertuples()],
        }
    top3 = outlets.nlargest(3, "n")
    result = {
        "scope": "January 2022–December 2025; November 4 snapshot; publication country equals evaluated government.",
        "definitions": "Country distributions describe country mean-monthly negative-framing rates on qualifying months, not temporal variance or population uncertainty. Group-line summaries first average eligible countries each month, then the 48 months. Quantiles use linear interpolation. Zeros remain in denominators.",
        "nicaragua": {
            "articles": int(outlets.n.sum()), "negative_articles": int(outlets.frame_negative.sum()),
            "monthly_negative_pct": float((nic.frame_negative / nic.n).mean() * 100),
            "pooled_negative_pct": float(outlets.frame_negative.sum() / outlets.n.sum() * 100),
            "top_three_article_share_pct": float(top3.n.sum() / outlets.n.sum() * 100),
            "top_three_negative_share_pct": float(top3.frame_negative.sum() / outlets.frame_negative.sum() * 100),
            "low_group_with_pct": float(full["low"] * 100),
            "low_group_without_pct": float(without["low"] * 100),
            "difference_pp": float((full["low"] - without["low"]) * 100),
        },
        "country_distributions": distributions,
        "input_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [
            DATA / "18_nicaragua_provenance_and_summary.json", DATA / "18_nicaragua_outlet_counts.csv",
            DATA / "18_nicaragua_outlet_month_counts.csv", DATA / "18_nicaragua_action_actor_role_counts.csv",
            DATA / "16_media_freedom_country_month.csv", DATA / "16_media_freedom_country_sensitivity.csv",
            DATA / "16_media_freedom_groups.csv"]},
    }
    output = DATA / "18_nicaragua_comparison.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result["nicaragua"], indent=2))


if __name__ == "__main__":
    main()
