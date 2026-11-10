#!/usr/bin/env python3
"""Build slide figures from the separate, hash-pinned presentation release.

Run from any directory with Python, numpy and matplotlib installed. No database,
article text or model access is used. Cached inputs are verified by SHA-256.
"""
from collections import Counter
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon, Patch
from matplotlib.ticker import PercentFormatter
import numpy as np

from analysis_utils import ROOT, AXES, load, cube, marginal, measures, correlation

OUT = ROOT / "slides/figures"
DATA = OUT / "data"
MANIFEST_PATH = ROOT / "slides/analysis_snapshot.json"
MANIFEST = json.loads(MANIFEST_PATH.read_text())
SCOPE_FILE = MANIFEST["scope_file"]
START, END = MANIFEST["article_period"]
PERIOD = f"{datetime.strptime(START, '%Y-%m'):%b %Y}–{datetime.strptime(END, '%Y-%m'):%b %Y}"
GEOGRAPHY_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_50m_admin_0_countries.geojson"
GEOGRAPHY_SHA = "3e458fc036ad0a66411f2c1e6cac49c5d7bfb81cb1123bc513b22511a2b7fdeb"
INK, NAVY, MUTED = "#1f2328", "#011F5B", "#6b7280"
NEG, ZERO, POS = "#D55E00", "#e1e5eb", "#009E73"
AXIS_COLORS = {"align": "#0072B2", "rep": "#D55E00", "frame": "#009E73"}
AXIS_NAMES = {"align": "Political alignment", "rep": "Reputational effect", "frame": "Framing"}

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "font.size": 16, "text.color": INK, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": INK, "axes.edgecolor": "#bdc3cc",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titleweight": "bold", "axes.titlecolor": NAVY,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "pdf.fonttype": 42, "svg.fonttype": "none",
})


def write_csv(name, rows):
    with (DATA / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def save(fig, name):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=180, facecolor="white")
    plt.close(fig)


def geography():
    path = ROOT / "data/cache/ne_50m_admin_0_countries.geojson"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(GEOGRAPHY_URL, timeout=120) as r:
            body = r.read()
        if hashlib.sha256(body).hexdigest() != GEOGRAPHY_SHA:
            raise ValueError("Natural Earth file differs from pinned v5.1.2")
        path.write_bytes(body)
    body = path.read_bytes()
    assert hashlib.sha256(body).hexdigest() == GEOGRAPHY_SHA
    return json.loads(body)["features"]


def geo_code(feature):
    p = feature["properties"]
    # ISO_A3_EH supplies France and Norway where ISO_A3 is -99.
    # Kosovo follows the explicit XKX convention in country_context.json.
    return "XKX" if p["ADM0_A3"] == "KOS" else p["ISO_A3_EH"]


def map_panel(ax, features, values, breaks, palette):
    patches, shades = [], []
    mapped = set()
    for f in features:
        code = geo_code(f)
        if code == "ATA":
            continue
        polygons = f["geometry"]["coordinates"]
        if f["geometry"]["type"] == "Polygon":
            polygons = [polygons]
        n = values.get(code, 0)
        shade = palette[int(np.searchsorted(breaks, n, side="right"))] if n else "#e7e9ed"
        if n:
            mapped.add(code)
        for poly in polygons:
            patches.append(Polygon(poly[0], closed=True))
            shades.append(shade)
    ax.add_collection(PatchCollection(patches, facecolor=shades, edgecolor="white", linewidth=.22))
    ax.set(xlim=(-180, 180), ylim=(-59, 84), aspect="equal")
    ax.axis("off")
    assert set(values) <= mapped, "Every observed code must have map geometry"


def coverage(scope, monthly, meta, context, features):
    govt, domains = Counter(), Counter()
    for field, dest in (("gov", govt), ("source", domains)):
        for row in monthly["groups"][field]:
            if START <= row["month"] <= END:
                dest[row["k"]] += sum(row["c"])
        assert sum(dest.values()) == sum(scope["overall"]["c"])
    source_country = Counter()
    source_articles = Counter()
    international = []
    for domain, n in domains.items():
        entry = meta["sources"][domain]
        code = entry["country"]
        if code is None:
            international.append({"source": domain, "eligible_articles": n,
                                  "reason": entry["country_status"]})
        else:
            assert entry["country_status"] == "single observed country"
            source_country[code] += 1
            source_articles[code] += n
    rows = []
    for code in sorted(set(source_country) | set(govt)):
        rows.append({"country_code": code, "country_name": context["countries"][code]["name"],
                     "publication_source_domains": source_country.get(code, 0),
                     "articles_from_those_domains": source_articles.get(code, 0),
                     "articles_evaluating_government": govt.get(code, 0)})
    write_csv("06_coverage_map.csv", rows)
    write_csv("06_international_or_mixed_sources.csv", sorted(international, key=lambda x: -x["eligible_articles"]))
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.9))
    fig.subplots_adjust(left=.015, right=.985, top=.88, bottom=.23, wspace=.035)
    palettes = [["#b7d7e8", "#73adc9", "#367caa", NAVY], ["#d6e9df", "#91c6b1", "#469c80", "#00664c"]]
    map_panel(axes[0], features, source_country, [3, 6, 9], palettes[0])
    map_panel(axes[1], features, govt, [100, 1000, 10000], palettes[1])
    axes[0].set_title(f"Where coverage is published\n{len(source_country)} countries · {sum(source_country.values())} source domains", fontsize=18, pad=14)
    axes[1].set_title(f"Which government is evaluated\n{len(govt)} country / territory codes", fontsize=18, pad=14)
    for ax, pal, labels in zip(axes, palettes, [["1–2", "3–5", "6–8", "9+"], ["1–99", "100–999", "1,000–9,999", "10,000+"]]):
        handles = [Patch(color=c, label=l) for c, l in zip(pal, labels)]
        ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, -.28), ncol=4,
                  frameon=False, fontsize=13, handlelength=1.2, columnspacing=1)
    fig.text(.255, .188, "Number of source domains", ha="center", fontsize=14, color=MUTED)
    fig.text(.75, .188, "Number of eligible articles", ha="center", fontsize=14, color=MUTED)
    fig.text(.5, .105, f"{len(international)} international / mixed-country domains are separate from the publication-country map.", ha="center", fontsize=14)
    fig.text(.5, .052, f"{PERIOD} · {sum(govt.values()):,} eligible articles · gray = no observed value · Natural Earth v5.1.2", ha="center", fontsize=12, color=MUTED)
    save(fig, "06_coverage_map")
    return {"eligible_articles": sum(govt.values()), "source_domains": len(domains),
            "source_countries": len(source_country), "mapped_source_domains": sum(source_country.values()),
            "international_or_mixed_domains": len(international),
            "international_or_mixed_articles": sum(x["eligible_articles"] for x in international),
            "evaluated_government_codes": len(govt),
            "examples": {k: govt[k] for k in ("AFG", "ARE", "AND")}}


def distributions(scope):
    rows, data = [], []
    n = sum(scope["overall"]["c"])
    for a in AXES:
        counts = marginal(scope["overall"], a)
        data.append(counts / n)
        for label, count in zip([-1, 0, 1], counts):
            rows.append({"measure": a, "label": label, "count": int(count), "eligible_denominator": n, "share": float(count / n)})
    write_csv("07_label_distributions.csv", rows)
    fig, ax = plt.subplots(figsize=(14, 5.8))
    fig.subplots_adjust(left=.27, right=.965, top=.81, bottom=.29)
    data = np.array(data)
    left = np.zeros(3)
    for j, (color, label) in enumerate(zip([NEG, ZERO, POS], ["Negative (−1)", "Zero", "Positive (+1)"])):
        ax.barh(range(3), data[:, j], left=left, color=color, height=.55, label=label)
        for i, value in enumerate(data[:, j]):
            if value >= .07 or j == 1:
                ax.text(left[i] + value / 2, i, f"{value:.1%}", ha="center", va="center", fontsize=18,
                        color=INK if j == 1 else "white", fontweight="bold")
            else:
                ax.annotate(f"{value:.1%}", xy=(left[i] + value/2, i-.22), xytext=(left[i]+value/2, i-.45),
                            ha="center", va="bottom", fontsize=16, color=color,
                            arrowprops={"arrowstyle": "-", "color": color, "lw": .7})
        left += data[:, j]
    ax.set_yticks(range(3), [AXIS_NAMES[a] for a in AXES], fontsize=19)
    ax.set_xlim(0, 1)
    ax.set_ylim(2.6, -.65)
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xlabel("Share of eligible articles", labelpad=10)
    ax.spines[["left", "bottom"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=15)
    ax.tick_params(axis="x", length=0)
    ax.legend(loc="lower center", bbox_to_anchor=(.45, 1.07), ncol=3, frameon=False, fontsize=17)
    fig.text(.5, .09, "Zero includes neutral, mixed or insufficient directional evidence; not-codable labels are excluded.", ha="center", fontsize=14)
    save(fig, "07_label_distributions")
    return {axis: {"negative": int(marginal(scope["overall"], axis)[0]),
                   "zero": int(marginal(scope["overall"], axis)[1]),
                   "positive": int(marginal(scope["overall"], axis)[2])}
            for axis in AXES}


def framing_comparisons(scope):
    """Reproduce the selected source–government rows on slide 14."""
    selected = [("Kyiv Independent", "kyivindependent.com", "RUS"),
                ("Kyiv Independent", "kyivindependent.com", "UKR"),
                ("BBC", "bbc.com", "RUS"), ("Reuters", "reuters.com", "RUS"),
                ("The Guardian", "theguardian.com", "RUS")]
    available = {(row["source"], row["gov"]): row
                 for row in scope["interactions"]["government_outlet"]}
    assert len(available) == len(scope["interactions"]["government_outlet"]), "Duplicate source–government pair"
    rows = []
    for label, domain, government in selected:
        row = available[(domain, government)]
        counts = marginal(row, "frame")
        metric = measures(row, "frame")
        rows.append({"source_label": label, "source_domain": domain,
                     "evaluated_government": government, "eligible_articles": metric["n"],
                     "negative_count": int(counts[0]), "zero_count": int(counts[1]),
                     "positive_count": int(counts[2]), "negative_share": metric["negative"],
                     "positive_share": metric["positive"],
                     "nonzero_share": metric["negative"] + metric["positive"],
                     "two_sided_P": metric["two_sided"]})
    write_csv("12_source_government_framing.csv", rows)
    return rows


def yearly_coverage(scope, monthly):
    """Expose uneven coverage without treating observed years as complete."""
    valid, eligible = Counter(), Counter()
    for month, n in scope["quality"]["months"].items():
        if START <= month <= END:
            valid[month[:4]] += n
    for row in monthly["groups"]["gov"]:
        if START <= row["month"] <= END:
            eligible[row["month"][:4]] += sum(row["c"])
    assert sum(valid.values()) == scope["quality"]["valid"]
    assert sum(eligible.values()) == scope["quality"]["complete"]
    rows = [{"year": y, "valid_records": valid[y], "eligible_records": eligible[y]}
            for y in sorted(valid)]
    write_csv("06_coverage_by_year.csv", rows)
    return rows


def joint(scope):
    ar = cube(scope["overall"]).sum(axis=2)
    shares = ar / ar.sum(axis=1)[:, None]
    joint_correlation = float(correlation(scope["overall"]))
    rows = [{"alignment": i-1, "reputation": j-1, "count": int(ar[i,j]),
             "alignment_group_denominator": int(ar[i].sum()), "share_within_alignment_group": float(shares[i,j])}
            for i in range(3) for j in range(3)]
    write_csv("08_alignment_reputation_joint.csv", rows)
    fig, ax = plt.subplots(figsize=(12.2, 6.5))
    fig.subplots_adjust(left=.28, right=.96, bottom=.23, top=.82)
    cmap = colors.LinearSegmentedColormap.from_list("navy", ["#f2f5fa", NAVY])
    ax.imshow(shares, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{shares[i,j]:.1%}", ha="center", va="center", fontsize=25,
                    color="white" if shares[i,j] > .5 else NAVY, fontweight="bold")
    ax.set_xticks(range(3), ["Negative (−1)", "Zero", "Positive (+1)"], fontsize=18)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.set_xlabel("Reputational effect", labelpad=20, fontsize=19)
    ax.set_yticks(range(3), [f"Opposes (−1)\nn = {ar[0].sum():,}", f"Zero\nn = {ar[1].sum():,}", f"Supports (+1)\nn = {ar[2].sum():,}"], fontsize=17)
    ax.set_ylabel("Political alignment", fontsize=19, labelpad=18)
    ax.tick_params(length=0, pad=12)
    ax.set_xticks(np.arange(-.5, 3, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 3, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=3)
    ax.tick_params(which="minor", length=0)
    ax.spines[:].set_visible(False)
    fig.text(.5, .13, f"{shares[2,0]:.1%} of articles with positive alignment have a negative reputational effect.", ha="center", fontsize=19, fontweight="bold", color=NAVY)
    fig.text(.5, .074, "Each row sums to 100%", ha="center", fontsize=14)
    save(fig, "08_alignment_reputation_joint")
    return {"correlation_alignment_reputation": joint_correlation,
            "positive_alignment_n": int(ar[2].sum()), "positive_alignment_negative_reputation_n": int(ar[2,0]),
            "negative_reputation_share_among_positive_alignment": float(shares[2,0])}


def timeseries(monthly):
    # Selected for a documented political episode, not as a random country case.
    months = [f"{year}-{month:02d}" for year in (2023, 2024) for month in range(1,13)]
    source = {x["month"]: x for x in monthly["groups"]["gov"] if x["k"] == "SEN"}
    rows = []
    for month in months:
        row = source.get(month)
        n = sum(row["c"]) if row else 0
        out = {"evaluated_government": "SEN", "month": month, "eligible_articles": n}
        for axis in AXES:
            metric = measures(row, axis) if row else {"two_sided": np.nan, "negative": np.nan, "zero": np.nan, "positive": np.nan}
            for field in ("two_sided", "negative", "zero", "positive"):
                out[f"{axis}_{field}"] = metric[field]
        out["displayed_in_line"] = n > 0
        rows.append(out)
    write_csv("09_senegal_monthly_indices.csv", rows)
    fig, (ax, count_ax) = plt.subplots(2, 1, figsize=(14, 6.8), sharex=True,
                                      gridspec_kw={"height_ratios": [3.8, 1.1], "hspace": .13})
    fig.subplots_adjust(left=.085, right=.97, top=.84, bottom=.19)
    x = np.arange(24)
    n = np.array([r["eligible_articles"] for r in rows])
    for axis in AXES:
        y = np.array([r[f"{axis}_two_sided"] for r in rows])
        y[n == 0] = np.nan
        ax.plot(x, y, marker="o", markersize=5, linewidth=2.5, color=AXIS_COLORS[axis], label=AXIS_NAMES[axis])
    ax.set_ylabel("Two-sided index P")
    ax.set_ylim(0, .13)
    ax.set_yticks([0, .04, .08, .12])
    ax.grid(axis="y", color="#e5e7eb")
    ax.legend(loc="lower center", bbox_to_anchor=(.5, 1.11), ncol=3, frameon=False, fontsize=16)
    ax.axvspan(12.6, 13.4, facecolor=NAVY, alpha=.07)
    ax.annotate("Election postponement\nand court reversal", xy=(13, rows[13]["align_two_sided"]), xytext=(9.5,.126),
                ha="center", va="top", fontsize=14, color=NAVY,
                arrowprops={"arrowstyle": "-", "color": NAVY, "lw": 1})
    ax.annotate("Election held", xy=(14, rows[14]["align_two_sided"]), xytext=(15.0,.062), fontsize=14, color=NAVY,
                arrowprops={"arrowstyle": "-", "color": NAVY, "lw": 1})
    bars = count_ax.bar(x, n, width=.7, color="#c3c9d2", edgecolor="none")
    count_ax.bar_label(bars, labels=[str(int(v)) for v in n], padding=3, fontsize=13, color=MUTED)
    count_ax.set_ylim(0, 1150)
    count_ax.set_ylabel("Eligible\narticles", fontsize=13)
    count_ax.set_yticks([0, 500, 1000])
    count_ax.set_yticklabels(["0", "500", "1,000"], fontsize=12)
    count_ax.set_xticks([0, 3, 6, 9, 12, 15, 18, 21])
    count_ax.set_xticklabels(["Jan 2023", "Apr", "Jul", "Oct", "Jan 2024", "Apr", "Jul", "Oct"], fontsize=14)
    count_ax.set_xlim(-.5,23.5)
    ax.tick_params(axis="x", length=0)
    count_ax.spines["left"].set_visible(False)
    fig.text(.5, .09, "Senegal government · P = 4 × positive share × negative share · all months with data shown", ha="center", fontsize=14)
    fig.text(.5, .04, "Counts show coverage volume, not independent events · selected episode: UN S/2024/521, §18", ha="center", fontsize=12, color=MUTED)
    save(fig, "09_senegal_monthly_indices")
    return next(r for r in rows if r["month"] == "2024-02")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    scope, monthly, meta, context = [load(n, MANIFEST_PATH) for n in (SCOPE_FILE, "explore-monthly.json", "explore-meta.json", "country_context.json")]
    assert scope["start"] == START and scope["end"] == END
    eligible = sum(scope["overall"]["c"])
    valid = scope["quality"]["valid"]
    assert eligible == scope["quality"]["complete"]
    manifest = MANIFEST
    assert valid == manifest["valid_records"] and eligible == manifest["eligible_records"]
    results = {
        "audit_cutoff": manifest["audit_cutoff"], "source_commit": manifest["commit"],
        "article_period": [START, END],
        "valid_records": valid, "eligible_records": eligible,
        "scope_file": SCOPE_FILE,
        "scope_sha256": manifest["files"][SCOPE_FILE]["sha256"],
        "source_files": {name: manifest["files"][name] for name in
                         (SCOPE_FILE, "explore-monthly.json", "explore-meta.json", "country_context.json")},
        "scope_note": manifest["scope_note"],
        "source_manifest": "slides/analysis_snapshot.json",
        "coverage": coverage(scope, monthly, meta, context, geography()),
        "coverage_by_year": yearly_coverage(scope, monthly),
        "label_counts": distributions(scope),
        "joint": joint(scope), "senegal_february_2024": timeseries(monthly),
        "timeseries_display": {"policy": "all nonempty months", "hide_below_n": None,
                               "no_data": "gap, not zero", "count_unit": "eligible article records, not unique events"},
        "framing_comparisons": framing_comparisons(scope),
        "geography": {"url": GEOGRAPHY_URL, "sha256": GEOGRAPHY_SHA, "license": "Public domain",
                      "terms": "https://www.naturalearthdata.com/about/terms-of-use/",
                      "code_rule": "ISO_A3_EH; Natural Earth KOS explicitly mapped to project XKX; no other substitutions",
                      "note": "Natural Earth boundaries and code matching are cartographic conventions, not a statement of recognition."},
        "event_source": "https://documents.un.org/doc/undoc/gen/n24/173/40/pdf/n2417340.pdf",
        "figures": ["06_coverage_map", "07_label_distributions", "08_alignment_reputation_joint", "09_senegal_monthly_indices"],
    }
    (DATA / "slide_figure_manifest.json").write_text(json.dumps(results, indent=2) + "\n")
    (DATA / "figure_notes.txt").write_text(
        "FIGURE SCOPE\nAll four figures use the hash-pinned release in slides/analysis_snapshot.json. "
        f"No current-production totals are substituted. Main period: {PERIOD}; "
        f"{eligible:,} eligible joint records among {valid:,} structurally valid records. "
        f"Audit cutoff: {manifest['audit_cutoff']}. Aggregate: {SCOPE_FILE}; SHA-256 "
        f"{manifest['files'][SCOPE_FILE]['sha256']}. {manifest['scope_note']} "
        "New production outcomes must enter a separately pinned, verified analysis release before these figures are updated. An eligible record has "
        "an identified evaluated government and primary action and numeric labels on all three axes. "
        "Zero remains; null/not codable does not. Structural checks are not semantic validation.\n\n"
        "MAP\nPublication countries are metadata of observed source domains, not the governments evaluated. "
        "Use complete monthly groups: display-level aggregate groups omit low-count categories. There are "
        f"{results['coverage']['source_domains']} domains, with {results['coverage']['mapped_source_domains']} assigned to "
        f"{results['coverage']['source_countries']} single observed countries and {results['coverage']['international_or_mixed_domains']} international/mixed domains "
        "shown separately in the CSV. Do not infer a domain's scraped country from its brand or headquarters. "
        f"Evaluated-government records span {results['coverage']['evaluated_government_codes']} country/territory codes; Afghanistan, UAE and Andorra "
        "need not be scraped locally to appear. Each map has its own scale. Gray means no observed value. "
        "All observed codes map to Natural Earth geometry; tiny territories may not be visually distinguishable.\n\n"
        "DISTRIBUTIONS AND JOINT TABLE\nSame eligible article denominator across all measures. Zero includes "
        "neutral, mixed and insufficient directional evidence. The joint table conditions reputation on "
        "alignment; rows sum to 100%, and this is not a confusion matrix or an accuracy test. The correlation "
        "treats -1/0/+1 as equally spaced scores and is descriptive; article and source dependence remain. "
        f"{results['joint']['negative_reputation_share_among_positive_alignment']:.1%} of supporting actions are reputation-negative; these are coding implications, not measured "
        "changes in public reputation.\n\n"
        "SENEGAL\nSelected documented episode, not a representative or randomly selected case. Monthly "
        "P is calculated separately for all three measures. Source/month composition can change and repeated "
        "coverage is not independent events. All nonempty months are shown, with the exact eligible article "
        "count labeled below. There is no arbitrary minimum-count display cutoff. Low-count months can "
        "be more sensitive to individual records; volume is not a guarantee of precision. Months with "
        "no data remain gaps, not zero scores. The count panel is raw coverage volume, not normalized salience. The February 2024 episode and March election dates come from UN S/2024/521 paragraph 18. "
        "An incumbent transition changes the government reference point. No causal/event attribution or "
        "societal polarization estimate is established.\n\n"
        "SOURCE–GOVERNMENT FRAMING\nThe five selected rows in 12_source_government_framing.csv "
        "use the same common eligible cohort. P is computed from exact counts before display rounding. "
        "These are pooled descriptive comparisons, not matched events or estimates of editorial-policy effects.\n\n"
        "REPRODUCTION\nRun python scripts/build_slide_figures.py with numpy and matplotlib. Public input "
        "hashes are checked by scripts/analysis_utils.py; Natural Earth geometry is version- and hash-pinned. "
        "PNG, PDF, SVG, plotted CSVs and this manifest are regenerated. No paid/model/database access occurs.\n"
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
