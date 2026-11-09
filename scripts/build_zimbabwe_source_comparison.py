#!/usr/bin/env python3
"""Build directional framing figures from the frozen available article cohort.

Default: verify the bundled aggregate hash, then rebuild CSV/PNG/PDF/SVG/manifest.
Optional: repeat --cache PATH for all three private extraction caches to also
recompute the full release and selected source-month cells before plotting.
No database, model, provider or network calls are made.
"""
from pathlib import Path
from collections import defaultdict
import argparse, csv, gzip, hashlib, json
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "slides/figures/data"
OUT = ROOT / "slides/figures"
INPUT = DATA / "13_zimbabwe_source_summary.json"
INPUT_SHA = "08fc0f05567ab28f64dca950b1af15dcaab2a61c2473c70cfb5e85268a5a3194"
EXAMPLES = DATA / "13_zimbabwe_article_examples.json"
CACHE_PROOF = DATA / "13_zimbabwe_cache_verification.json"
SOURCES = ("chronicle.co.zw", "zimlive.com")
LABELS = {"chronicle.co.zw": "Chronicle", "zimlive.com": "ZimLive"}
COLORS = {"chronicle.co.zw": "#011F5B", "zimlive.com": "#D55E00"}
MONTHS = ["2023-08", "2023-09", "2023-10", "2023-11", "2023-12"]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_raw(paths, summary):
    """Optional reproduction from supplied private caches; all zeros retained."""
    expected = {r["filename"]: r for r in summary["source_receipts"]}
    assert len(paths) == len(expected) and {p.name for p in paths} == set(expected)
    cells = defaultdict(lambda: [0] * 27)
    full_cube = [0] * 27
    valid = eligible = 0
    for path in paths:
        proof_path = path.parent / "EXTRACTION_VERIFIED.json"
        proof = json.loads(proof_path.read_text())
        assert sha(path) == proof["records_sha256"] == expected[path.name]["sha256"]
        assert sha(proof_path) == expected[path.name]["proof_sha256"]
        with gzip.open(path, "rt") as handle:
            for row in csv.DictReader(handle):
                valid += 1
                if row["gov"] in ("", "null") or row["action"] in ("", "null") or any(row[a] not in ("-1", "0", "1") for a in ("align", "rep", "frame")):
                    continue
                eligible += 1
                index = (int(row["align"]) + 1) * 9 + (int(row["rep"]) + 1) * 3 + int(row["frame"]) + 1
                full_cube[index] += 1
                if row["gov"] == row["publication_country"] == "ZWE" and row["source"] in SOURCES and "2023-01" <= row["month"] <= "2023-12":
                    cells[row["source"], row["month"]][index] += 1
    assert (valid, eligible) == (summary["full_release_valid"], summary["full_release_eligible"])
    scope_path = ROOT / "data/cache/snapshots" / summary["frozen_scope_sha256"] / "explore-since2019.json"
    assert scope_path.is_file(), "Full verification needs the existing pinned explore-since2019.json cache"
    assert sha(scope_path) == summary["frozen_scope_sha256"]
    assert full_cube == json.loads(scope_path.read_text())["overall"]["c"]
    for row in summary["monthly"]:
        cube = cells[row["source"], row["month"]]
        assert sum(cube) == row["n"]
        for i, axis in enumerate(("align", "rep", "frame")):
            for code in (-1, 0, 1):
                count = sum(n for k, n in enumerate(cube) if (k // (9, 3, 1)[i]) % 3 == code + 1)
                assert count == row["margins"][axis][str(code)]
    return {"three_cache_hashes": True, "full_population_counts": True,
            "full_population_27_joint_cells": True, "all_2023_source_month_margins": True}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", type=Path, action="append")
    args = ap.parse_args()
    assert sha(INPUT) == INPUT_SHA
    summary = json.loads(INPUT.read_text())
    raw_verification = verify_raw(args.cache, summary) if args.cache else {"performed_this_run": False}
    if args.cache:
        CACHE_PROOF.write_text(json.dumps({"input": {"path": str(INPUT.relative_to(ROOT)), "sha256": INPUT_SHA},
            "checks": raw_verification, "source_receipts": summary["source_receipts"],
            "frozen_scope_sha256": summary["frozen_scope_sha256"],
            "verified_at": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
    cached_verification = None
    if CACHE_PROOF.exists():
        proof = json.loads(CACHE_PROOF.read_text())
        assert proof["input"]["sha256"] == INPUT_SHA
        assert proof["source_receipts"] == summary["source_receipts"]
        assert all(proof["checks"].values())
        cached_verification = {"path": str(CACHE_PROOF.relative_to(ROOT)), "sha256": sha(CACHE_PROOF),
                               "checks": proof["checks"], "verified_at": proof["verified_at"]}
    by_key = {(r["source"], r["month"]): r for r in summary["monthly"]}
    rows = []
    for source in SOURCES:
        for month in MONTHS:
            r = by_key[source, month]
            out = {"evaluated_government": "ZWE", "publication_country": "ZWE", "source": source,
                   "month": month, "eligible_articles": r["n"]}
            for axis in ("align", "rep", "frame"):
                for code, label in (("-1", "negative"), ("0", "zero"), ("1", "positive")):
                    out[axis + "_" + label + "_count"] = r["margins"][axis][code]
                    out[axis + "_" + label + "_share"] = r["margins"][axis][code] / r["n"] if r["n"] else None
            rows.append(out)
    csv_path = DATA / "13_zimbabwe_monthly_framing.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)

    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
                         "font.size": 16, "text.color": "#1f2328", "axes.labelcolor": "#1f2328",
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "figure.facecolor": "white",
                         "axes.facecolor": "white", "pdf.fonttype": 42, "svg.fonttype": "none",
                         "svg.hashsalt": "zimbabwe-directional-framing-2023-v1"})
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.2), sharey=True)
    fig.subplots_adjust(left=.09, right=.98, bottom=.37, top=.83, wspace=.12)
    for ax, sign, title in zip(axes, ("1", "-1"), ("Positive framing", "Negative framing")):
        for source, marker in zip(SOURCES, ("o", "s")):
            values = [by_key[source, month]["margins"]["frame"][sign] / by_key[source, month]["n"] for month in MONTHS]
            ax.plot(range(5), values, color=COLORS[source], marker=marker, linewidth=2.8, markersize=7,
                    label=LABELS[source], clip_on=False)
        ax.set_title(title, fontsize=21, pad=15)
        ax.set_ylim(0, .65); ax.set_xlim(-.12, 4.12)
        ax.set_yticks([0, .2, .4, .6]); ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        ax.set_xticks(range(5)); ax.set_xticklabels(["Aug", "Sep", "Oct", "Nov", "Dec"], fontsize=17)
        ax.grid(axis="y", color="#dce1e7", linewidth=.7)
        ax.set_axisbelow(True); ax.tick_params(axis="both", length=0, pad=9)
        ax.spines["left"].set_visible(False); ax.spines["bottom"].set_color("#b8bec7")
    axes[0].set_ylabel("Share of eligible articles", fontsize=17, labelpad=11)
    axes[1].tick_params(axis="y", labelleft=True)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="upper center", bbox_to_anchor=(.52, .995),
               ncol=2, frameon=False, fontsize=19, columnspacing=2.5)

    # Pooled counts are descriptive summaries of the displayed months, not mean monthly rates.
    for x, sign in ((.28, "1"), (.77, "-1")):
        for y, source in ((.285, SOURCES[0]), (.245, SOURCES[1])):
            r = summary["focus_pooled"][source]; n = r["n"]; k = r["margins"]["frame"][sign]
            fig.text(x, y, "{}: {:.1%} ({}/{})".format(LABELS[source], k/n, k, n),
                     ha="center", va="center", color=COLORS[source], fontsize=15)
    # A separate figure-level axes keeps the count table aligned under both panels.
    table_ax = fig.add_axes([.17, .075, .72, .125]); table_ax.axis("off")
    table = table_ax.table(cellText=[[str(by_key[s,m]["n"]) for m in MONTHS] for s in SOURCES],
                           rowLabels=[LABELS[s] for s in SOURCES], colLabels=["Aug", "Sep", "Oct", "Nov", "Dec"],
                           loc="center", cellLoc="center", rowLoc="right", bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False); table.set_fontsize(14)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("white"); cell.set_facecolor("#f1f3f6" if row == 0 else "white")
        if col == -1 and row > 0: cell.get_text().set_color(COLORS[SOURCES[row-1]])
    fig.text(.055, .15, "Articles", fontsize=14, color="#6b7280", ha="left")
    fig.text(.52, .024, "Zimbabwe, Aug-Dec 2023 | Zero-coded articles remain in the denominator. Observed coverage, not independent events.",
             fontsize=12, color="#6b7280", ha="center")

    outputs = {}
    for extension in ("png", "pdf", "svg"):
        path = OUT / ("13_zimbabwe_framing_shares." + extension)
        kwargs = {"dpi": 180, "facecolor": "white"}
        if extension == "pdf": kwargs["metadata"] = {"Creator": "build_zimbabwe_source_comparison.py", "CreationDate": None, "ModDate": None}
        if extension == "svg": kwargs["metadata"] = {"Creator": "build_zimbabwe_source_comparison.py", "Date": None}
        fig.savefig(path, **kwargs)
        if extension == "svg":
            # Normalize trailing whitespace before calculating the published output hash.
            text = "\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n"
            path.write_text(text)
        outputs[str(path.relative_to(ROOT))] = {"sha256": sha(path), "bytes": path.stat().st_size}
    plt.close(fig)
    outputs[str(csv_path.relative_to(ROOT))] = {"sha256": sha(csv_path), "bytes": csv_path.stat().st_size}
    if EXAMPLES.exists(): outputs[str(EXAMPLES.relative_to(ROOT))] = {"sha256": sha(EXAMPLES), "bytes": EXAMPLES.stat().st_size}
    manifest = {"created_at_utc": datetime.now(timezone.utc).isoformat(),
                "builder": "scripts/build_zimbabwe_source_comparison.py", "builder_sha256": sha(Path(__file__)),
                "input": {"path": str(INPUT.relative_to(ROOT)), "sha256": INPUT_SHA},
                "source_receipts": summary["source_receipts"], "frozen_scope_sha256": summary["frozen_scope_sha256"],
                "scope": {"gov": "ZWE", "publication_country": "ZWE", "sources": list(SOURCES), "months": MONTHS},
                "definition": "Separate positive and negative framing shares; each sign count divided by all common-eligible articles. Neither panel is P.",
                "pooled_counts": {s: {"n": summary["focus_pooled"][s]["n"], "frame": summary["focus_pooled"][s]["margins"]["frame"]} for s in SOURCES},
                "limits": summary["cautions"], "raw_cache_verification_this_run": raw_verification,
                "verification_receipt_for_unchanged_aggregate": cached_verification,
                "outputs": outputs, "operations": {"database_calls": 0, "model_calls": 0, "network_calls": 0}}
    path = DATA / "13_zimbabwe_manifest.json"; path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"manifest": str(path.relative_to(ROOT)), "outputs": list(outputs), "raw_verification": raw_verification}))


if __name__ == "__main__": main()
