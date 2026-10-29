#!/usr/bin/env python3
"""Reproduce civic news aggregates using Python 3.9+ standard library only.

Default: validate the included snapshot and regenerate three summary files.
--check: verify those files without writing. --verify-upstream: also download
the two commit-pinned public aggregate files and verify their hashes and rows.
No article-level data, database connection, API credentials or model calls.
"""

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SNAPSHOT = DATA / "monthly_complete_snapshot.json"
SNAPSHOT_SHA256 = "75688202b63d8c28786a030193570e23efe9673caaba87e5fe58f7e25e50902e"
AXES = ("align", "rep", "frame")
LABELS = ("-1", "0", "1", "null")
MEANINGS = {
    "-1": "negative direction",
    "0": "neutral, mixed, or insufficient directional evidence",
    "1": "positive direction",
    "null": "not codable",
}
MONTH_KEYS = {"month", "saved", "valid", "mechanical_failures", "api_failures", "axes", "input_clear"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(snapshot):
    require(snapshot["schema_version"] == "civic-monthly-complete-v1", "Unexpected schema")
    version = json.loads((ROOT / "prompts" / "version.json").read_text(encoding="utf-8"))
    prompt = (ROOT / "prompts" / version["prompt_file"]).read_bytes()
    require(version["release"] == snapshot["cohort"]["prompt_version"], "Prompt version mismatch")
    require(hashlib.sha256(prompt).hexdigest() == version["prompt_text_sha256"] == snapshot["cohort"]["prompt_text_sha256"], "Prompt byte hash mismatch")
    rows = snapshot["months"]
    expected = [f"2025-{month:02d}" for month in range(1, 13)] + [f"2026-{month:02d}" for month in range(1, 6)]
    require([row["month"] for row in rows] == expected, "Expected exactly 17 ordered months")
    require(snapshot["cohort"]["months"] == len(rows), "Wrong month denominator")
    require(snapshot["cohort"]["prompt_version"] == "civic_20261020_complete_v1", "Mixed prompt cohort")
    for row in rows:
        month = row["month"]
        require(set(row) == MONTH_KEYS, f"Unexpected fields in {month}")
        for field in ("saved", "valid", "mechanical_failures", "api_failures", "input_clear"):
            require(type(row[field]) is int and row[field] >= 0, f"Invalid count: {month}/{field}")
        require(row["saved"] == row["valid"] + row["mechanical_failures"] + row["api_failures"], f"Outcome sum mismatch: {month}")
        require(row["valid"] <= row["saved"] <= row["input_clear"], f"Invalid coverage: {month}")
        require(set(row["axes"]) == set(AXES), f"Unexpected axes: {month}")
        for axis in AXES:
            counts = row["axes"][axis]
            require(set(counts) == set(LABELS), f"Missing null or label: {month}/{axis}")
            require(all(type(value) is int and value >= 0 for value in counts.values()), "Invalid label count")
            require(sum(counts.values()) == row["valid"], f"Label denominator mismatch: {month}/{axis}")
    require(sum(row["valid"] for row in rows) == 542981, "Frozen cohort total changed")
    composition = snapshot["cohort_composition"]
    require(composition["denominator_valid"] == 542981, "Composition denominator mismatch")
    for key in ("source_domains_distinct", "publication_countries_distinct_excluding_ALL", "publication_ALL_outcomes", "government_country_codes_distinct_excluding_null", "government_null_outcomes"):
        require(type(composition[key]) is int and 0 <= composition[key] <= composition["denominator_valid"], f"Invalid composition count: {key}")


def verify_upstream(snapshot):
    documents = {}
    for name, provenance in snapshot["upstream_provenance"]["files"].items():
        with urlopen(provenance["url"], timeout=30) as response:
            raw = response.read()
        require(hashlib.sha256(raw).hexdigest() == provenance["sha256"], f"Upstream hash mismatch: {name}")
        documents[name] = json.loads(raw)
    analytics = documents["monthly_analytics.json"]
    progress = documents["monthly_progress.json"]
    require(analytics["outcomes_verified_at_utc"] == snapshot["independently_verified_at_utc"], "Upstream audit time mismatch")
    require(progress["independent_db_verified_at_utc"] == snapshot["independently_verified_at_utc"], "Progress audit time mismatch")
    pmap = {row["month"]: row for row in progress["months"]}
    selected = []
    composition_counts = {key: Counter() for key in ("sources", "publication_countries", "government_countries")}
    for row in analytics["groups"]:
        if row["prompt"] == "complete" and "2025-01" <= row["month"] <= "2026-05":
            for key in composition_counts:
                composition_counts[key].update(row[key])
            require(row["valid"] == pmap[row["month"]]["complete_valid"], "Progress/analytics mismatch")
            item = {key: row[key] for key in ("month", "saved", "valid", "mechanical_failures", "api_failures", "axes")}
            item["input_clear"] = pmap[row["month"]]["input_clear"]
            selected.append(item)
    require(sorted(selected, key=lambda row: row["month"]) == snapshot["months"], "Curated snapshot differs from upstream")
    require(all(sum(counts.values()) == snapshot["cohort_composition"]["denominator_valid"] for counts in composition_counts.values()), "Upstream composition sums differ")
    expected_composition = {
        "source_domains_distinct": len(composition_counts["sources"]),
        "publication_countries_distinct_excluding_ALL": len(set(composition_counts["publication_countries"]) - {"ALL"}),
        "publication_ALL_outcomes": composition_counts["publication_countries"]["ALL"],
        "government_country_codes_distinct_excluding_null": len(set(composition_counts["government_countries"]) - {"null"}),
        "government_null_outcomes": composition_counts["government_countries"]["null"],
    }
    for key, value in expected_composition.items():
        require(snapshot["cohort_composition"][key] == value, f"Upstream composition mismatch: {key}")


def csv_text(fields, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def summaries(snapshot):
    rows = snapshot["months"]
    totals = {key: sum(row[key] for row in rows) for key in ("saved", "valid", "mechanical_failures", "api_failures", "input_clear")}
    labels = []
    for axis in AXES:
        for label in LABELS:
            count = sum(row["axes"][axis][label] for row in rows)
            labels.append({"axis": axis, "label": label, "meaning": MEANINGS[label], "count": count, "denominator_valid": totals["valid"], "percent_of_valid": f"{100 * count / totals['valid']:.6f}"})
    coverage = [{key: row[key] for key in ("month", "input_clear", "saved", "valid", "mechanical_failures", "api_failures")} | {"valid_percent_of_input_clear": f"{100 * row['valid'] / row['input_clear']:.6f}"} for row in rows]
    summary = {
        "cohort": snapshot["cohort"],
        "independently_verified_at_utc": snapshot["independently_verified_at_utc"],
        "snapshot_sha256": SNAPSHOT_SHA256,
        "cohort_composition": snapshot["cohort_composition"],
        "totals": totals,
        "valid_percent_of_input_clear": round(100 * totals["valid"] / totals["input_clear"], 6),
        "failure_percent_of_saved": round(100 * (totals["mechanical_failures"] + totals["api_failures"]) / totals["saved"], 6),
        "interpretation": "Descriptive marginals among structurally valid stored complete-prompt outputs; neither accuracy nor population estimates.",
    }
    return {
        "label_summary.csv": csv_text(list(labels[0]), labels),
        "monthly_coverage.csv": csv_text(list(coverage[0]), coverage),
        "cohort_summary.json": json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare existing summaries without writing")
    parser.add_argument("--verify-upstream", action="store_true", help="Verify the exact public source release over HTTPS")
    args = parser.parse_args()
    raw = SNAPSHOT.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SNAPSHOT_SHA256, "Snapshot hash mismatch")
    snapshot = json.loads(raw)
    validate(snapshot)
    if args.verify_upstream:
        verify_upstream(snapshot)
    for name, contents in summaries(snapshot).items():
        target = DATA / name
        if args.check:
            require(target.read_text(encoding="utf-8") == contents, f"Summary mismatch: {name}")
        else:
            target.write_text(contents, encoding="utf-8")
    print("Verified 17 complete-prompt months; 542,981 valid outcomes; each label axis reconciles.")
    print("Summaries match." if args.check else "Wrote label_summary.csv, monthly_coverage.csv, and cohort_summary.json.")


if __name__ == "__main__":
    main()
