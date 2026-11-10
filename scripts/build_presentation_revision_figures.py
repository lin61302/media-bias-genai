#!/usr/bin/env python3
"""Clear presentation figures from the unchanged November 8 public aggregates.

No model calls, private article records, source recoding, or external joins.
Run with the project's matplotlib environment. The manifest retains definitions,
input hashes and exact chart values; methodological detail stays in slide notes.
"""
from __future__ import annotations

import csv
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
from matplotlib.ticker import PercentFormatter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "slides/figures/data"
FIG = ROOT / "slides/figures"
INK = "#19334b"
POS = "#087f72"
NEG = "#bc4042"
FEB = "#68789a"
MAR = "#c28428"
GRID = "#e3e7eb"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--senegal-p-only", action="store_true",
                    help="Update only the Senegal P figure and its manifest entry.")
args = parser.parse_args()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(fig, stem: str) -> list[dict]:
    outputs = []
    if args.senegal_p_only and stem != "14_senegal_polarization_application":
        plt.close(fig)
        return [{"path": str((FIG / f"{stem}.{ext}").relative_to(ROOT)),
                 "sha256": digest(FIG / f"{stem}.{ext}")}
                for ext in ("png", "svg", "pdf")]
    for ext in ("png", "svg", "pdf"):
        path = FIG / f"{stem}.{ext}"
        metadata = {"Creator": "Frozen aggregate presentation figure"} if ext == "pdf" else None
        fig.savefig(path, dpi=180, facecolor="white", metadata=metadata)
        if ext == "svg":
            path.write_text(re.sub(r"[ \t]+(?=\n)", "", path.read_text()))
        outputs.append({"path": str(path.relative_to(ROOT)), "sha256": digest(path)})
    plt.close(fig)
    return outputs


def clean(ax, *, grid: str = "x") -> None:
    for key in ("top", "right", "left"):
        ax.spines[key].set_visible(False)
    ax.spines["bottom"].set_color("#aab5c0")
    ax.tick_params(axis="both", length=0, labelcolor=INK)
    ax.grid(axis=grid, color=GRID, linewidth=.8)
    ax.set_axisbelow(True)


plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 14,
    "text.color": INK, "axes.labelcolor": INK,
    "axes.titlecolor": INK, "svg.fonttype": "none",
    "svg.hashsalt": "presentation-revision-20261110-v1",
    "pdf.fonttype": 42,
})

contrib_file = DATA / "09_senegal_contributors.json"
monthly_file = DATA / "09_senegal_monthly_indices.csv"
foreign_file = DATA / "12_source_government_framing.csv"
assert digest(monthly_file) == "72fccdcdd7b4ffa1e73393c69edb6b2ceb2a6f17dbf196fbcaf374f9dee0e546"
contrib = json.loads(contrib_file.read_text())
monthly = list(csv.DictReader(monthly_file.open()))
foreign = list(csv.DictReader(foreign_file.open()))
assert contrib["snapshot"]["eligible_records"] == 3181113

# 1. Actor relationships and the changing mix of reported actions.
roles = ["A", "B", "G", "C", "K", "F"]
role_labels = ["Executive / cabinet", "Legislature", "Security forces",
               "Parties / politicians", "Civic movements / unions", "Courts / prosecutors"]
february = contrib["detail_months"]["2024-02"]["by_label"]
pos_roles = {x["actor_role"]: x["n"] for x in february["align_1"]["actor_roles"]}
neg_roles = {x["actor_role"]: x["n"] for x in february["align_-1"]["actor_roles"]}
pos_counts = [pos_roles.get(r, 0) for r in roles]
neg_counts = [neg_roles.get(r, 0) for r in roles]
assert pos_counts == [59, 18, 18, 17, 0, 3]
assert neg_counts == [0, 4, 0, 56, 37, 30]
action_codes = ["protest_march", "ban_disperse", "elect_vote"]
action_labels = ["Protest / march", "Ban / disperse", "Election / voting"]
month_n = {m: contrib["monthly"][m]["n"] for m in ("2024-02", "2024-03")}
action_counts = {m: [contrib["key_action_comparison"][a][m]["n"] for a in action_codes]
                 for m in month_n}
assert month_n == {"2024-02": 934, "2024-03": 874}
assert action_counts == {"2024-02": [51, 28, 14], "2024-03": [4, 1, 201]}
voting_zero = contrib["key_action_comparison"]["elect_vote"]["2024-03"]["margins"]["align"]["0"]
assert voting_zero == 168

fig = plt.figure(figsize=(13.5, 6.0))
ax = fig.add_axes([.19, .18, .34, .63])
ax2 = fig.add_axes([.715, .18, .25, .63])
y = np.arange(len(roles))
for counts, shift, color, label in ((pos_counts, -.17, POS, "+1 alignment"),
                                    (neg_counts, .17, NEG, "−1 alignment")):
    bars = ax.barh(y + shift, counts, height=.28, color=color, label=label)
    for bar, n in zip(bars, counts):
        if n:
            ax.text(n + 1.1, bar.get_y() + bar.get_height()/2, str(n),
                    va="center", fontsize=13, fontweight="bold", color=color)
ax.set_yticks(y, role_labels, fontsize=13)
ax.set_xlim(0, 67)
ax.set_xticks([0, 20, 40, 60])
ax.invert_yaxis()
ax.set_xlabel("Article records", labelpad=9)
clean(ax)
ax.legend(loc="lower left", bbox_to_anchor=(-.02, 1.015), ncol=2,
          frameon=False, fontsize=12, handlelength=1.1, columnspacing=1.3)

y2 = np.arange(3)
for m, shift, color, label in (("2024-02", -.17, FEB, "February"),
                              ("2024-03", .17, MAR, "March")):
    shares = np.array(action_counts[m]) / month_n[m]
    bars = ax2.barh(y2 + shift, shares, height=.28, color=color, label=label)
    for bar, n, share in zip(bars, action_counts[m], shares):
        ax2.text(share + .006, bar.get_y() + bar.get_height()/2,
                 f"{share:.1%}", va="center", color=color,
                 fontsize=13, fontweight="bold")
ax2.set_yticks(y2, action_labels, fontsize=13)
ax2.set_xlim(0, .285)
ax2.set_xticks([0, .1, .2])
ax2.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
ax2.invert_yaxis()
ax2.set_xlabel("Share of all eligible articles", labelpad=9, fontsize=13)
clean(ax2)
ax2.legend(loc="lower left", bbox_to_anchor=(-.02, 1.015), ncol=2,
           frameon=False, fontsize=12, handlelength=1.1, columnspacing=1.3)
fig.text(.025, .955, "Political alignment by actor · February", fontsize=17, fontweight="bold")
fig.text(.615, .955, "The mix of reported actions changes", fontsize=17, fontweight="bold")
fig.text(.025, .04, "+1 = actor supports the incumbent   ·   −1 = actor opposes the incumbent", fontsize=13)
fig.text(.965, .04, "February n = 934  ·  March n = 874", fontsize=13, ha="right")
actor_outputs = save(fig, "14_senegal_actors_actions")

# 2. P across the three judgments, beside the separate-share slide in the deck.
rows = [r for r in monthly if "2023-10" <= r["month"] <= "2024-06"]
assert len(rows) == 9
for r in rows:
    for field in ("align", "rep", "frame"):
        assert abs(sum(float(r[f"{field}_{sign}"]) for sign in ("negative", "zero", "positive")) - 1) < 1e-12
        assert abs(4*float(r[f"{field}_positive"])*float(r[f"{field}_negative"])
                   - float(r[f"{field}_two_sided"])) < 1e-12
month_starts = [datetime.fromisoformat(r["month"] + "-01") for r in rows]
month_ends = [d.replace(year=d.year + 1, month=1) if d.month == 12
              else d.replace(month=d.month + 1) for d in month_starts]
month_midpoints = [start + (end - start) / 2
                   for start, end in zip(month_starts, month_ends)]
x = date2num(month_midpoints)


def calendar_x(date: str) -> float:
    return float(date2num(datetime.fromisoformat(date)))


event_annotations = [
    {"date": "2024-02-03", "label": "Election postponed",
     "text": "Feb 3\nElection postponed", "text_date": "2023-12-10", "height": .118},
    {"date": "2024-02-15", "label": "Court overturns delay",
     "text": "Feb 15\nCourt overturns delay", "text_date": "2023-12-10", "height": .091},
    {"date": "2024-03-24", "label": "Presidential election",
     "text": "March 24\nPresidential election", "text_date": "2024-05-15", "height": .064},
    {"date": "2024-04-02", "label": "Faye takes office",
     "text": "April 2\nFaye takes office", "text_date": "2024-05-15", "height": .111},
]
# Event dates use the same calendar scale as the monthly observations.
assert x[5] < calendar_x("2024-03-24") < calendar_x("2024-04-01")
assert calendar_x("2024-04-01") < calendar_x("2024-04-02") < x[6]
fig, ax = plt.subplots(figsize=(13.5, 5.2))
fig.subplots_adjust(left=.085, right=.975, top=.82, bottom=.13)
ax.axvspan(calendar_x("2024-02-01"), calendar_x("2024-03-01"), color="#f2e7d7", zorder=0)
for event in event_annotations:
    ax.axvline(calendar_x(event["date"]), color="#6d7782", linestyle=":", linewidth=1.25, zorder=1)
clean(ax, grid="y")
for field, color, label in [("align", "#0072b2", "Political alignment"),
                            ("rep", "#d55e00", "Reputational effect"),
                            ("frame", "#009e73", "Framing")]:
    ax.plot(x, [float(r[f"{field}_two_sided"]) for r in rows], marker="o",
            linewidth=2.7, markersize=6, color=color, label=label)
ax.set_ylim(0, .13)
ax.set_yticks([0, .04, .08, .12])
ax.set_ylabel("Monthly P index", fontsize=16)
ax.set_xlim(date2num(month_starts[0]), date2num(month_ends[-1]))
ax.set_xticks(x)
ax.set_xticklabels(["Oct 2023", "Nov", "Dec", "Jan 2024", "Feb", "Mar", "Apr", "May", "Jun"], fontsize=12)
ax.set_xticks(date2num(month_starts + [month_ends[-1]]), minor=True)
ax.tick_params(axis="x", which="minor", length=5, color="#aab5c0")
ax.legend(loc="lower center", bbox_to_anchor=(.5, 1.06), ncol=3, frameon=False, fontsize=15)
# Point positions center each whole-month aggregate; they are not daily
# observations. Leaders identify event lines, never inferred daily data values.
event_arrow = {"arrowstyle": "-", "color": "#6d7782", "linewidth": 1.1}
for event in event_annotations:
    ax.annotate(event["text"],
                xy=(calendar_x(event["date"]), event["height"]),
                xytext=(calendar_x(event["text_date"]), event["height"]),
                ha="center", va="center", fontsize=14, linespacing=1.3,
                arrowprops=event_arrow)
polar_outputs = save(fig, "14_senegal_polarization_application")

# 3. Same source, different governments: keep positive and negative separately.
ki = [r for r in foreign if r["source_domain"] == "kyivindependent.com"]
ki.sort(key=lambda r: (r["evaluated_government"] != "RUS"))
assert [r["evaluated_government"] for r in ki] == ["RUS", "UKR"]
for r in ki:
    n = int(r["eligible_articles"])
    assert sum(int(r[f"{s}_count"]) for s in ("negative", "zero", "positive")) == n
    for sign in ("negative", "positive"):
        assert abs(int(r[f"{sign}_count"])/n - float(r[f"{sign}_share"])) < 1e-12
fig, ax = plt.subplots(figsize=(13.5, 4.9))
fig.subplots_adjust(left=.245, right=.94, top=.78, bottom=.2)
y = np.array([0, 1.15])
for sign, shift, color, label in (("negative", -.17, NEG, "Negative framing (−1)"),
                                ("positive", .17, POS, "Positive framing (+1)")):
    vals = [float(r[f"{sign}_share"]) for r in ki]
    bars = ax.barh(y + shift, vals, height=.27, color=color, label=label)
    for bar, value in zip(bars, vals):
        ax.text(value + .008, bar.get_y() + bar.get_height()/2, f"{value:.1%}",
                va="center", color=color, fontsize=17, fontweight="bold")
ax.set_yticks(y, ["Russia · foreign\n1,242 article records", "Ukraine · domestic\n9,568 article records"],
              fontsize=16)
ax.invert_yaxis()
ax.set_xlim(0, .43)
ax.set_xticks([0, .1, .2, .3, .4])
ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
ax.set_xlabel("Share of eligible articles evaluating that government", labelpad=12, fontsize=15)
clean(ax)
ax.legend(loc="lower left", bbox_to_anchor=(-.02, 1.04), ncol=2,
          frameon=False, fontsize=14, handlelength=1.5)
fig.text(.04, .93, "The Kyiv Independent: framing toward the evaluated government", fontsize=19,
         fontweight="bold")
fig.text(.04, .035, "Available reporting in January 2019–May 2026", fontsize=14)
foreign_outputs = save(fig, "14_kyiv_government_framing")

manifest = {
    "schema_version": 1,
    "snapshot": "November 8, 2026 frozen analytical release",
    "input_files": [{"path": str(p.relative_to(ROOT)), "sha256": digest(p)}
                    for p in (contrib_file, monthly_file, foreign_file)],
    "script_sha256": digest(Path(__file__)),
    "global_definitions": {
        "unit": "Article records with one primary selected action, not unique real-world events.",
        "eligible": "Evaluated government and primary action identified; all three political labels numeric. Unknown/uncodable excluded upstream.",
        "sign_share": "Each sign count divided by all eligible records in the same grouping, including zeros.",
        "zero": "May represent neutral, mixed or insufficient directional evidence.",
        "political_alignment": "Actor's support/opposition relative to the evaluated incumbent manifested through the selected action.",
        "P": "4 * positive share * negative share, on a theoretical 0–1 scale; measures coexistence of coded directions in this reporting corpus, not public-opinion polarization.",
    },
    "figures": {
        "senegal_actors_actions": {
            "outputs": actor_outputs,
            "evaluated_government": "SEN", "publication_origin": "all",
            "actor_month": "2024-02", "month_denominators": month_n,
            "selected_actor_groups": [dict(code=r, label=l, positive=p, negative=n)
                                      for r,l,p,n in zip(roles,role_labels,pos_counts,neg_counts)],
            "actor_totals": {"positive_all_roles": 132, "negative_all_roles": 182,
                             "positive_displayed_roles": sum(pos_counts), "negative_displayed_roles": sum(neg_counts)},
            "action_counts": {m: dict(zip(action_codes, values)) for m, values in action_counts.items()},
            "march_election_voting_zero_alignment_n": voting_zero,
            "limits": ["Displayed actor groups and action categories are selected, not exhaustive.",
                       "Role describes an institution, not permanent political allegiance.",
                       "Action shares divide by all eligible articles, not just displayed actions.",
                       "The changing mix is descriptive; it is not a causal decomposition of the sign-share change."],
        },
        "senegal_polarization_application": {
            "outputs": polar_outputs, "evaluated_government": "SEN", "publication_origin": "all",
            "display_months": [r["month"] for r in rows],
            "values": [{"month": r["month"], "n": int(r["eligible_articles"]),
                        "positive_alignment_share": float(r["align_positive"]),
                        "negative_alignment_share": float(r["align_negative"]),
                        "P_alignment": float(r["align_two_sided"]),
                        "P_reputation": float(r["rep_two_sided"]),
                        "P_framing": float(r["frame_two_sided"])} for r in rows],
            "P_axis_display_range": [0, .13], "P_theoretical_range": [0, 1],
            "time_axis": {
                "scale": "Continuous calendar dates; month-start boundary ticks and centered month labels.",
                "monthly_point_positions": [d.isoformat() for d in month_midpoints],
                "aggregation": "One unchanged aggregate per calendar month; midpoint placement does not create daily observations.",
            },
            "incumbent_boundary": "Faye inaugurated April 2, 2024; same external chronology as the existing Senegal slide notes.",
            "event_annotations": {
                "source": "https://documents.un.org/doc/undoc/gen/n24/173/40/pdf/n2417340.pdf",
                "source_locator": "UN Secretary-General report S/2024/521, paragraph 18 (page 5)",
                "events": [{"date": e["date"], "label": e["label"], "display_position": "Exact calendar date"}
                           for e in event_annotations],
                "interpretation": "External chronology provides context for monthly aggregates; it neither recodes articles nor identifies within-month or causal effects.",
            },
            "limits": ["Shares and P measure model-coded news content, not attitudes or behavior among citizens.",
                       "Changing source mix, reported actions, genre, repeated reporting and model sensitivity remain possible contributors.",
                       "No minimum-count filter; counts remain in the values table and separate-share figure. Zeros stay in all sign-share denominators.",
                       "A low P can reflect rare directional coverage or predominantly one-sided coverage; inspect separate sign shares."],
        },
        "kyiv_government_framing": {
            "outputs": foreign_outputs, "source_domain": "kyivindependent.com",
            "scope": "Available eligible reporting within January 2019–May 2026 frozen release.",
            "values": [{"government": r["evaluated_government"], "n": int(r["eligible_articles"]),
                        "negative_n": int(r["negative_count"]), "positive_n": int(r["positive_count"]),
                        "negative_share": float(r["negative_share"]), "positive_share": float(r["positive_share"])} for r in ki],
            "limits": ["Government labels refer to the evaluated government, not the publication origin.",
                       "Pooled comparisons do not match events, conduct, genre, time or supplied-text quality.",
                       "Different framing shares do not by themselves establish bias, double standards or a causal outlet effect."],
        },
    },
}
(DATA / "14_presentation_revision_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
updated = (["senegal_polarization_application"] if args.senegal_p_only
           else list(manifest["figures"]))
print(json.dumps({"figures": updated,
                  "outputs": [x["path"] for key in updated
                              for x in manifest["figures"][key]["outputs"]]}, indent=2))
