#!/usr/bin/env python3
"""Account for a frozen, targeted review of previously uncertain labels.

This reducer makes no coding decisions and does not call a model or database.
Article text and individual review decisions remain outside the repository.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

DIMENSIONS = {"align": "Alignment", "rep": "Reputation", "frame": "Framing"}
STATUSES = ("Supported", "Defensible alternative", "Needs correction", "Unresolved")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path, fields=("case_id",)):
    rows = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        key = tuple(row[f] for f in fields)
        assert key not in rows, (path.name, "duplicate", key)
        rows[key] = row
    return rows


def counts(values):
    found = Counter(values)
    assert not set(found) - set(STATUSES)
    return {status: found[status] for status in STATUSES}


def check_decision(row, key, aux, sources):
    cid, full = key
    dim = next(k for k, v in DIMENSIONS.items() if v == full)
    label = aux[(cid,)]["luna_original_15_fields"][dim]
    assert row["original_label"] == label
    status, allowed = row["status"], row["admissible_labels"]
    assert status in STATUSES
    assert len(allowed) == len(set(allowed)) and all(x in (-1, 0, 1, None) for x in allowed)
    if status == "Supported":
        assert allowed == [label]
    elif status == "Defensible alternative":
        assert label in allowed and len(allowed) > 1
    elif status == "Needs correction":
        assert allowed and label not in allowed
    else:
        assert not allowed
    assert row["proposed_label"] == (allowed[0] if len(allowed) == 1 else None)
    assert row["rationale"].strip() and row["rule"].strip()
    source = sources[(cid,)]
    segments = {"T": source["title"], **source["segments"]}
    assert row["evidence"], key
    for quote in row["evidence"]:
        if isinstance(quote, dict):
            segment, text = quote["source"], quote["text"]
        else:
            segment, text = quote.split("|", 1)
        assert text and text in segments[segment], (key, "Evidence is not exact", quote)
    return len(row["evidence"])


def summarize(ids, aux, final):
    status_by_case = {}
    by_dimension = {}
    for dim, full in DIMENSIONS.items():
        current, original, moves, direction, labels = [], Counter(), Counter(), [], Counter()
        for cid in ids:
            row = aux[(cid,)]
            label = row["luna_original_15_fields"][dim]
            old = row["corrected_nov3_dimension_reviews"][full]["Astra assessment"]
            original[old] += 1
            labels[str(label)] += 1
            key = (cid, full)
            if old == "Ambiguous / boundary":
                new = final[key]["status"]
                moves[new] += 1
            else:
                new = {"Supported": "Supported", "Unsupported": "Needs correction"}[old]
            current.append(new)
            status_by_case.setdefault(cid, {})[dim] = new
            if label in (-1, 1):
                direction.append(new)
        c, dc = counts(current), counts(direction)
        by_dimension[dim] = {
            "denominator_n": len(ids), "status_counts": c,
            "strict_support_share": c["Supported"] / len(ids),
            "historical_status_counts": dict(sorted(original.items())),
            "uncertain_reassessment_status_counts": counts(moves.elements()),
            "original_luna_label_counts": dict(sorted(labels.items())),
            "directional_n": len(direction), "directional_status_counts": dc,
            "directional_strict_support_share": dc["Supported"] / len(direction) if direction else None,
        }
    all_supported = sum(all(s == "Supported" for s in row.values()) for row in status_by_case.values())
    return {"n": len(ids), "dimensions": by_dimension,
            "all_three_supported_n": all_supported,
            "all_three_supported_share": all_supported / len(ids)}


def build(base, historical_path):
    review = base / "uncertain_reassessment"
    aux_path = base / "analyst/FULL_CODER_FIELDS_AUX_V1.jsonl"
    source_path = base / "reviewer/references_only.jsonl"
    diag_path = base / "event_metrics_diagnostics.json"
    final_path = review / "final.jsonl"
    aux = read_jsonl(aux_path)
    sources = read_jsonl(source_path)
    diagnostics = json.loads(diag_path.read_text())["private_diagnostics"]
    ids = diagnostics["_cohort_case_ids"]["human_luna_same_actual_action"]
    assert len(ids) == len(set(ids)) == 173
    wanted = {(cid, full) for cid in ids for full in DIMENSIONS.values()
              if aux[(cid,)]["corrected_nov3_dimension_reviews"][full]["Astra assessment"] == "Ambiguous / boundary"}
    assert len(wanted) == 79 and len({key[0] for key in wanted}) == 55
    final = read_jsonl(final_path, ("case_id", "dimension"))
    assert set(final) == wanted, "Review must contain exactly the frozen 79 judgments"
    first, second = {}, {}
    review_paths = []
    for stage, collector in (("first", first), ("second", second)):
        for part in range(1, 4):
            path = review / f"{stage}_{part}.jsonl"
            rows = read_jsonl(path, ("case_id", "dimension"))
            assert not set(collector) & set(rows)
            collector.update(rows)
            review_paths.append(path)
        assert set(collector) == wanted, stage
    pass_evidence_n = 0
    for readings in (first, second):
        for key, row in readings.items():
            pass_evidence_n += check_decision(row, key, aux, sources)
    evidence_n = 0
    for key, row in final.items():
        evidence_n += check_decision(row, key, aux, sources)
        assert row["adjudication_reason"].strip()
        assert first[key]["reviewer_id"] != second[key]["reviewer_id"]
    historical = json.loads(historical_path.read_text())["historical_political_label_review"]["human_luna_same_actual_action"]
    result = summarize(ids, aux, final)
    for dim, vals in result["dimensions"].items():
        old = historical["dimensions"][dim]
        assert vals["historical_status_counts"] == old["saved_review_verdict_counts"]
        assert vals["original_luna_label_counts"] == old["original_luna_label_counts"]
        assert sum(vals["status_counts"].values()) == 173
    changed_path = base / "analyst/EARLIER_CHANGED_SOURCE_VIEWS_PRIVATE.jsonl"
    changed = {key[0] for key in read_jsonl(changed_path)}
    valid = set(diagnostics["_cohort_case_ids"]["same_actual_action_structurally_valid_only"])
    reference_match = set(diagnostics["_cohort_case_ids"]["human_luna_both_match_unique_reference_action"])
    unresolved_cases = {cid for (cid, _), row in final.items() if row["status"] == "Unresolved"}
    comparisons = Counter()
    for key in wanted:
        a, b = first[key], second[key]
        comparisons["same_status" if a["status"] == b["status"] else "different_status"] += 1
        comparisons["same_admissible_set" if set(a["admissible_labels"]) == set(b["admissible_labels"]) else "different_admissible_set"] += 1
    input_paths = [aux_path, source_path, diag_path, changed_path, historical_path,
                   review / "PROTOCOL.txt", review / "manifest.json", review / "adjudication_log.json", final_path, *review_paths]
    manifest = json.loads((review / "manifest.json").read_text())
    # Verify the source/prompt inputs have not changed since the review scope froze.
    for filename, expected in manifest["input_sha256"].items():
        assert sha(Path(filename)) == expected, filename
    return {
        "schema_version": "uncertain-label-reassessment-v1", "review_date": "2026-11-10",
        "title": "Targeted reassessment of previously uncertain political labels",
        "scope": {"cohort_articles": 173, "reassessed_articles": 55, "reassessed_judgments": 79,
                  "historical_judgments_carried_forward": 440,
                  "method": "Two assistant readings per uncertain judgment, followed by documented lead-assistant adjudication. Labels and selected action/government were visible. Other saved judgments were carried forward.",
                  "human_review_of_new_decisions": False,
                  "interpretation": "Conditional assistant review support, not independent human accuracy. Defensible alternatives and unresolved cases do not count as strict support.",
                  "unchanged": "Original producer labels, historical assessments, source text, action comparison, prompt and production data."},
        "definitions": {
            "Supported": "The recorded label clearly follows the supplied evidence and fixed rule.",
            "Defensible alternative": "The recorded label is one of multiple comparably rule-consistent interpretations.",
            "Needs correction": "The recorded label is excluded by the evidence/rule; a replacement is proposed, not applied to production.",
            "Unresolved": "A genuine input/reference/applicability limitation prevents a label assessment."},
        "current_cohort": result,
        "reassessment_outcomes": counts(row["status"] for row in final.values()),
        "first_second_review_comparison": dict(sorted(comparisons.items())),
        "sensitivities": {
            "valid_full_outputs_only": summarize([cid for cid in ids if cid in valid], aux, final),
            "exclude_unresolved_applicability_articles": summarize([cid for cid in ids if cid not in unresolved_cases], aux, final),
            "both_coders_match_action_reference": summarize([cid for cid in ids if cid in reference_match], aux, final),
            "exclude_changed_source_views": summarize([cid for cid in ids if cid not in changed], aux, final)},
        "verification": {"exact_final_evidence_excerpts_checked": evidence_n,
                         "exact_all_pass_evidence_excerpts_checked": evidence_n + pass_evidence_n,
                         "complete_frozen_membership": True},
        "provenance": {"input_sha256": {p.name: sha(p) for p in input_paths},
                       "prompt_sha256": next(v for k, v in manifest["input_sha256"].items() if k.endswith("civic_20261020_complete_v1.txt")),
                       "reducer_sha256": sha(Path(__file__))},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--historical", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.private_root, args.historical)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "outcomes": result["reassessment_outcomes"]}))


if __name__ == "__main__":
    main()
