#!/usr/bin/env python3
"""Build separate coverage maps from existing, hash-pinned slide inputs.

Run from any directory with Python, numpy and matplotlib installed. This reads
local caches and existing coverage CSVs only. It does not fetch data, change the
original combined map, or rewrite any source CSV or slide.
"""
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from build_slide_figures import (
    ROOT, MANIFEST_PATH, GEOGRAPHY_URL, GEOGRAPHY_SHA,
    geography, geo_code, map_panel, NAVY, MUTED,
)

OUT = ROOT / "slides/figures"
DATA = OUT / "data"
MANIFEST_OUT = DATA / "06_split_maps_manifest.json"
MAP_CSV = DATA / "06_coverage_map.csv"
YEAR_CSV = DATA / "06_coverage_by_year.csv"
GEOGRAPHY_PATH = ROOT / "data/cache/ne_50m_admin_0_countries.geojson"
PALETTES = {
    "publication": ["#b7d7e8", "#73adc9", "#367caa", NAVY],
    "government": ["#d6e9df", "#91c6b1", "#469c80", "#00664c"],
}
GRAY = "#e7e9ed"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def pinned(name, snapshot):
    spec = snapshot["files"][name]
    path = ROOT / "data/cache/snapshots" / spec["sha256"] / name
    if not path.is_file():
        raise FileNotFoundError("Required local pinned cache is missing: " + name)
    assert digest(path) == spec["sha256"], "Pinned input hash mismatch: " + name
    return json.loads(path.read_text())


def verified_inputs(snapshot):
    scope = pinned("explore-since2019.json", snapshot)
    monthly = pinned("explore-monthly.json", snapshot)
    meta = pinned("explore-meta.json", snapshot)
    context = pinned("country_context.json", snapshot)
    start, end = snapshot["article_period"]
    government, domains = Counter(), Counter()
    for field, dest in (("gov", government), ("source", domains)):
        for row in monthly["groups"][field]:
            if start <= row["month"] <= end:
                dest[row["k"]] += sum(row["c"])
        assert sum(dest.values()) == sum(scope["overall"]["c"])
    publication, source_articles = Counter(), Counter()
    international = []
    for domain, n in domains.items():
        entry = meta["sources"][domain]
        code = entry["country"]
        if code is None:
            international.append({"source": domain, "eligible_articles": n,
                                  "reason": entry["country_status"]})
        else:
            assert entry["country_status"] == "single observed country"
            publication[code] += 1
            source_articles[code] += n
    # Reconcile every existing CSV row without rewriting it.
    csv_rows = read_csv(MAP_CSV)
    assert len({r["country_code"] for r in csv_rows}) == len(csv_rows)
    assert {r["country_code"] for r in csv_rows} == set(publication) | set(government)
    for row in csv_rows:
        code = row["country_code"]
        assert row["country_name"] == context["countries"][code]["name"]
        assert int(row["publication_source_domains"]) == publication.get(code, 0)
        assert int(row["articles_from_those_domains"]) == source_articles.get(code, 0)
        assert int(row["articles_evaluating_government"]) == government.get(code, 0)
    valid_year, eligible_year = Counter(), Counter()
    for month, n in scope["quality"]["months"].items():
        if start <= month <= end:
            valid_year[month[:4]] += n
    for row in monthly["groups"]["gov"]:
        if start <= row["month"] <= end:
            eligible_year[row["month"][:4]] += sum(row["c"])
    year_rows = read_csv(YEAR_CSV)
    assert {r["year"] for r in year_rows} == set(valid_year)
    for row in year_rows:
        assert int(row["valid_records"]) == valid_year[row["year"]]
        assert int(row["eligible_records"]) == eligible_year[row["year"]]
    assert sum(valid_year.values()) == scope["quality"]["valid"] == snapshot["valid_records"]
    assert sum(eligible_year.values()) == scope["quality"]["complete"] == snapshot["eligible_records"]
    assert (len(publication), sum(publication.values()), len(international), len(government)) == (71, 404, 26, 211)
    assert len(domains) == 430 and sum(government.values()) == 3181113
    # geography() is reused only after confirming its pinned local input exists.
    if not GEOGRAPHY_PATH.is_file():
        raise FileNotFoundError("Required local Natural Earth cache is missing")
    assert digest(GEOGRAPHY_PATH) == GEOGRAPHY_SHA
    features = geography()
    geometry_codes = {geo_code(feature) for feature in features}
    assert set(publication) <= geometry_codes and set(government) <= geometry_codes
    return publication, government, international, year_rows, features


def add_legend(fig, palette, labels, title, size, columns=5):
    handles = [Patch(facecolor=color, edgecolor="none", label=label)
               for color, label in zip(palette, labels)]
    handles.append(Patch(facecolor=GRAY, edgecolor="none", label="No observed value"))
    if columns == 3:
        # Matplotlib fills legend columns; keep numerical bins in row-reading order.
        handles = [handles[i] for i in (0, 3, 1, 4, 2)]
    legend = fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .018),
                        ncol=columns, frameon=False, fontsize=size, handlelength=1.2,
                        handleheight=1, columnspacing=1.15, title=title)
    legend.get_title().set_fontsize(size + 1)
    legend.get_title().set_fontweight("bold")


def save(fig, stem):
    outputs = {}
    for extension in ("png", "pdf", "svg"):
        path = OUT / (stem + "." + extension)
        kwargs = {"dpi": 180, "facecolor": "white"}
        if extension == "pdf":
            kwargs["metadata"] = {"Creator": "build_coverage_maps.py", "CreationDate": None, "ModDate": None}
        elif extension == "svg":
            kwargs["metadata"] = {"Date": None, "Creator": "build_coverage_maps.py"}
        fig.savefig(path, **kwargs)
        if extension == "svg":
            path.write_text(re.sub(r"[ \t]+(?=\n)", "", path.read_text()))
        outputs[str(path.relative_to(ROOT))] = {"sha256": digest(path), "bytes": path.stat().st_size}
    plt.close(fig)
    return outputs


def main():
    snapshot = json.loads(MANIFEST_PATH.read_text())
    original_hashes = {"06_coverage_map.csv": digest(MAP_CSV), "06_coverage_by_year.csv": digest(YEAR_CSV)}
    publication, government, international, year_rows, features = verified_inputs(snapshot)
    start, end = snapshot["article_period"]
    period = "{} - {}".format(datetime.strptime(start, "%Y-%m").strftime("%b %Y"),
                              datetime.strptime(end, "%Y-%m").strftime("%b %Y"))
    plt.rcParams["svg.hashsalt"] = snapshot["commit"] + "-separate-coverage-maps"
    outputs = {}

    fig = plt.figure(figsize=(14, 5.4))
    ax = fig.add_axes([.012, .225, .976, .765])
    map_panel(ax, features, publication, [3, 6, 9], PALETTES["publication"])
    add_legend(fig, PALETTES["publication"], ["1-2", "3-5", "6-8", "9+"],
               "Number of source domains", 20)
    outputs.update(save(fig, "06a_publication_coverage"))

    fig = plt.figure(figsize=(9, 5))
    ax = fig.add_axes([.012, .335, .976, .655])
    map_panel(ax, features, government, [100, 1000, 10000], PALETTES["government"])
    add_legend(fig, PALETTES["government"], ["1-99", "100-999", "1,000-9,999", "10,000+"],
               "Eligible articles", 20, columns=3)
    outputs.update(save(fig, "06b_evaluated_governments"))

    assert digest(MAP_CSV) == original_hashes["06_coverage_map.csv"]
    assert digest(YEAR_CSV) == original_hashes["06_coverage_by_year.csv"]
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "builder": "scripts/build_coverage_maps.py", "builder_sha256": digest(Path(__file__)),
        "helper": "scripts/build_slide_figures.py", "helper_sha256": digest(ROOT / "scripts/build_slide_figures.py"),
        "snapshot": {"path": "slides/analysis_snapshot.json", "sha256": digest(MANIFEST_PATH),
                     "commit": snapshot["commit"], "audit_cutoff": snapshot["audit_cutoff"],
                     "prompt_sha256": snapshot["prompt_sha256"], "article_period": snapshot["article_period"]},
        "pinned_inputs": {name: {"sha256": spec["sha256"]} for name, spec in snapshot["files"].items()},
        "existing_csv_inputs": original_hashes,
        "geography": {"url": GEOGRAPHY_URL, "sha256": GEOGRAPHY_SHA, "version": "Natural Earth v5.1.2",
                      "license": "Public domain", "kosovo_code": "XKX"},
        "statistics": {"publication_countries": len(publication), "mapped_source_domains": sum(publication.values()),
                       "international_or_mixed_source_domains": len(international), "total_source_domains": 430,
                       "international_or_mixed_eligible_articles": sum(r["eligible_articles"] for r in international),
                       "evaluated_government_codes": len(government), "eligible_articles": sum(government.values()),
                       "valid_records": snapshot["valid_records"]},
        "annual_coverage": [{"year": row["year"], "valid_records": int(row["valid_records"]),
                             "eligible_records": int(row["eligible_records"])} for row in year_rows],
        "definitions": {
            "publication": "Unique observed source domains assigned to one publication country in frozen source metadata; not restricted to domestic-government evaluations.",
            "international_or_mixed": "Domains without a single observed publication country are counted separately and not assigned to a country on the publication map.",
            "government": "Eligible article records evaluating each government, regardless of the source's publication country; this is not local news collection coverage.",
            "eligible": "Government and action identified, with align, rep and frame each coded -1, 0 or +1; zero labels retained.",
            "gray": "No observed positive value in this frozen plotted measure; not a claim of no news collection.",
            "coverage": "Observed records are not distinct real-world events and do not imply complete coverage of every source/year.",
        },
        "figure_specs": {
            "06a_publication_coverage": {"inches": [14, 5.4], "unit": "source domains", "breaks": [3, 6, 9]},
            "06b_evaluated_governments": {"inches": [9, 5], "unit": "eligible article records", "breaks": [100, 1000, 10000]},
        },
        "verification": {"all_four_pinned_inputs_hash_verified": True, "all_map_csv_values_reconciled": True,
                         "all_annual_csv_values_reconciled": True, "every_observed_code_has_geometry": True,
                         "original_source_csvs_unchanged": True},
        "outputs": outputs,
        "operations": {"database_calls": 0, "network_calls": 0, "model_calls": 0},
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"statistics": manifest["statistics"], "manifest": str(MANIFEST_OUT.relative_to(ROOT)),
                      "outputs": list(outputs)}, indent=2))


if __name__ == "__main__":
    main()
