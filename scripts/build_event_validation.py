#!/usr/bin/env python3
"""Reduce the frozen source-first review without making coding judgments.

This file reads private, versioned observations. It never changes a coding,
launches a model request, accesses the database, or chooses a comparison mask
based on either coder's correctness. Output is private aggregate accounting.
"""

from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import sys
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
STATUSES = {"single_action", "no_action", "multiple_actions", "insufficient_text", "unresolved"}
VERDICTS = {"Supported", "Unsupported", "Ambiguous / boundary", "Not assessable"}
MISSING = {"", "na", "n/a", "none", "null", "nan", "-999", "not codable", "uncodable"}
DIMENSIONS = {"align": "Alignment", "rep": "Reputation", "frame": "Framing"}
PARTITIONS = (
    "all_three_same", "human_reference_only", "luna_reference_only",
    "human_luna_same_but_not_reference", "all_three_different",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    result = {}
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        cid = row.get("case_id")
        if not isinstance(cid, str) or not cid:
            raise ValueError(f"{path.name}:{line_no}: missing case_id")
        if cid in result:
            raise ValueError(f"{path.name}:{line_no}: duplicate case_id {cid}")
        result[cid] = row
    return result


def scalar(value: Any) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    value = str(value).strip()
    return None if value.casefold() in MISSING else value


def number(value: Any) -> int | None:
    value = scalar(value)
    if value is None:
        return None
    try:
        val = float(value)
    except ValueError:
        return None
    return int(val) if val in (-1, 0, 1) else None


def normalized_actor(value: Any) -> str | None:
    value = scalar(value)
    return re.sub(r"\s+", " ", value).casefold() if value is not None else None


def literal_actor(value: Any) -> str | None:
    # Match the retained historical literal audit: preserve surrounding spaces.
    return str(value) if scalar(value) is not None else None


def category(value: Any) -> str | None:
    value = scalar(value)
    if value is None:
        return None
    match = re.match(r"^([A-W])(?:\b|\s|/)", value)
    return match.group(1) if match else None


def tag_list(value: Any) -> list[str] | None:
    if isinstance(value, list):
        vals = [scalar(v) for v in value]
        return [v for v in vals if v is not None] or None
    text = scalar(value)
    if text is None:
        return None
    if text.startswith("["):
        try:
            return tag_list(json.loads(text))
        except (ValueError, TypeError):
            return None
    # Historical human action_type_final contains a single taxonomy label.
    # Preserve unfamiliar substantive labels; do not make semantic recodings.
    return [text]


def tag_set(value: Any) -> tuple[str, ...] | None:
    tags = tag_list(value)
    return tuple(sorted(set(tags))) if tags else None


def primary_tag(value: Any) -> str | None:
    tags = tag_list(value)
    return tags[0] if tags else None


def country(value: Any) -> str | None:
    value = scalar(value)
    if value is None:
        return None
    value = value.upper()
    # Exact aliases observed in the retained human country cells.
    value = {"US": "USA", "SD": "SDN", "SS": "SSD"}.get(value, value)
    return value if re.fullmatch(r"[A-Z]{3}", value) and value != "ALL" else None


def fraction(a: int, b: int) -> float | None:
    return a / b if b else None


def ratio(a: int, b: int) -> dict[str, Any]:
    return {"matches": a, "compared": b, "share": fraction(a, b)}


def human_fields(row: dict[str, Any]) -> dict[str, Any]:
    return row["aux"]["human_november_full_original_fields"]


def luna_fields(row: dict[str, Any]) -> dict[str, Any]:
    return row["aux"].get("luna_original_15_fields") or {}


def mapping_state(event_id: str | None) -> str:
    return "uninterpretable" if event_id is None else "no_action" if event_id == "NONE" else "action"


def compare_field(rows: list[dict[str, Any]], human_key: str, luna_key: str,
                  normalize: Callable[[Any], Any]) -> dict[str, Any]:
    states = Counter({k: 0 for k in (
        "both_present_same", "both_present_different", "human_missing_or_not_comparable",
        "luna_missing_or_not_comparable", "both_missing_or_not_comparable",
    )})
    matches = []
    mismatches = []
    for row in rows:
        h = normalize(human_fields(row).get(human_key))
        l = normalize(luna_fields(row).get(luna_key))
        if h is None and l is None:
            states["both_missing_or_not_comparable"] += 1
        elif h is None:
            states["human_missing_or_not_comparable"] += 1
        elif l is None:
            states["luna_missing_or_not_comparable"] += 1
        elif h == l:
            states["both_present_same"] += 1
            matches.append(row["case_id"])
        else:
            states["both_present_different"] += 1
            mismatches.append(row["case_id"])
    n = states["both_present_same"] + states["both_present_different"]
    assert sum(states.values()) == len(rows)
    return {
        "cohort_n": len(rows),
        **ratio(states["both_present_same"], n),
        "excluded_n": len(rows) - n,
        "availability": dict(states),
        "human_missing_or_not_comparable_n": states["human_missing_or_not_comparable"] + states["both_missing_or_not_comparable"],
        "luna_missing_or_not_comparable_n": states["luna_missing_or_not_comparable"] + states["both_missing_or_not_comparable"],
        "both_missing_or_not_comparable_n": states["both_missing_or_not_comparable"],
        "_matching_case_ids": matches,
        "_differing_case_ids": mismatches,
    }


FIELD_SPECS = {
    "actor_literal": ("actor_final", "actor", literal_actor),
    "actor_case_spacing_normalized": ("actor_final", "actor", normalized_actor),
    "actor_category_code": ("actor_cat_final", "ac", category),
    "action_tag_exact_set": ("action_type_final", "tags", tag_set),
    "action_primary_tag": ("action_type_final", "tags", primary_tag),
    "reaction_tag": ("event_reacted_to_final", "react", scalar),
    "government_single_country": ("sentiment_target_country", "gov", country),
}


def government_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    result = Counter({s: 0 for s in (
        "missing_human_reference", "multiple_or_uninterpretable_human_reference",
        "missing_or_uninterpretable_luna_reference", "same_single_country",
        "different_single_country",
    )})
    for row in rows:
        raw = human_fields(row).get("sentiment_target_country")
        h, l = country(raw), country(luna_fields(row).get("gov"))
        if scalar(raw) is None:
            result["missing_human_reference"] += 1
        elif h is None:
            result["multiple_or_uninterpretable_human_reference"] += 1
        elif l is None:
            result["missing_or_uninterpretable_luna_reference"] += 1
        elif h == l:
            result["same_single_country"] += 1
        else:
            result["different_single_country"] += 1
    assert sum(result.values()) == len(rows)
    return dict(result)


def field_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "n": len(rows),
        "luna_structural_status": dict(Counter(r["luna_status"] for r in rows)),
        "fields": {name: compare_field(rows, *spec) for name, spec in FIELD_SPECS.items()},
        "government_reference": government_counts(rows),
    }


def historical_label_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Recondition saved assessments; never derive new dimension judgments."""
    result = {
        "n": len(rows),
        "assessment_origin": "Corrected November 3 saved review, reconditioned on fresh action identities; not newly coded political labels.",
        "reference": "Each saved assessment concerns the original Luna action and stored Luna government, not a new independent government or label reference.",
        "denominator": "All members of the named fresh cohort; unsupported, ambiguous, not-assessable and unreviewed judgments remain in the denominator.",
        "dimensions": {},
        "government_reference": government_counts(rows),
    }
    all_supported: dict[str, bool] = {r["case_id"]: True for r in rows}
    any_proposal = set()
    for dim, name in DIMENSIONS.items():
        raw_verdicts = Counter()
        effective = Counter({s: 0 for s in (
            "Supported", "Unsupported", "Ambiguous / boundary", "Not assessable",
            "Unreviewed", "Review provenance mismatch", "No numeric producer label",
            "Unknown saved review verdict",
        )})
        labels = Counter()
        directional = Counter()
        old_eligibility = Counter()
        proposal_counts = Counter()
        mismatches = []
        for row in rows:
            cid = row["case_id"]
            model = luna_fields(row)
            label = number(model.get(dim))
            labels[str(label) if label is not None else "missing_or_not_numeric"] += 1
            rev = (row["aux"].get("corrected_nov3_dimension_reviews") or {}).get(name)
            verdict = rev.get("Astra assessment", "Unreviewed") if rev else "Unreviewed"
            raw_verdicts[verdict] += 1
            old_eligibility[str(rev.get("Eligible")) if rev else "unreviewed"] += 1
            provenance_ok = bool(rev) and (
                scalar(rev.get("Luna action being assessed")) == scalar(model.get("act"))
                and country(rev.get("Luna government")) == country(model.get("gov"))
                and number(rev.get("Luna numeric label")) == label
            )
            if not rev:
                status = "Unreviewed"
            elif not provenance_ok:
                status = "Review provenance mismatch"
                mismatches.append(cid)
            elif label is None:
                status = "No numeric producer label"
            elif verdict in VERDICTS:
                status = verdict
            else:
                status = "Unknown saved review verdict"
            effective[status] += 1
            if label in (-1, 1):
                directional[status] += 1
            supported = status == "Supported"
            all_supported[cid] &= supported
            proposed = number(rev.get("Astra point proposal")) if rev else None
            if status == "Unsupported" and proposed is not None:
                proposal_counts[f"{label}->{proposed}"] += 1
                any_proposal.add(cid)
        assert sum(effective.values()) == len(rows)
        dir_n = sum(directional.values())
        result["dimensions"][dim] = {
            "denominator_n": len(rows),
            "retained_in_historical_review_n": effective["Supported"],
            "retained_share": fraction(effective["Supported"], len(rows)),
            "effective_status_counts": dict(effective),
            "saved_review_verdict_counts": dict(raw_verdicts),
            "original_luna_label_counts": dict(labels),
            "directional_n": dir_n,
            "directional_status_counts": dict(directional),
            "directional_retained_share": fraction(directional["Supported"], dir_n),
            "saved_old_eligibility_flag_counts_not_used_as_filter": dict(old_eligibility),
            "explicit_saved_numeric_changes": dict(proposal_counts),
            "_review_provenance_mismatch_case_ids": mismatches,
        }
    result["all_three_retained_n"] = sum(all_supported.values())
    result["all_three_retained_share"] = fraction(result["all_three_retained_n"], len(rows))
    result["any_explicit_saved_numeric_change_n"] = len(any_proposal)
    return result


def event_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ref_states = Counter({s: 0 for s in sorted(STATUSES)})
    ref_states.update(r["reference"]["status"] for r in rows)
    choice_states = {c: Counter({s: 0 for s in ("action", "no_action", "uninterpretable")}) for c in ("human", "luna")}
    for coder in choice_states:
        choice_states[coder].update(mapping_state(r[coder]) for r in rows)
    pair_rows = [r for r in rows if r["human"] is not None and r["luna"] is not None]
    common = [r for r in pair_rows if r["reference_id"] is not None]
    partition = Counter({p: 0 for p in PARTITIONS})
    classification = {}
    for row in common:
        h, l, ref = row["human"], row["luna"], row["reference_id"]
        hl, hr, lr = h == l, h == ref, l == ref
        assert sum((hl, hr, lr)) != 2, row["case_id"]
        part = ("all_three_same" if hl and hr else "human_reference_only" if hr
                else "luna_reference_only" if lr else "human_luna_same_but_not_reference" if hl
                else "all_three_different")
        partition[part] += 1
        classification[row["case_id"]] = part
    assert sum(partition.values()) == len(common)
    pair_categories = Counter({s: 0 for s in (
        "both_explicit_no_action", "human_no_action_luna_action", "human_action_luna_no_action",
        "same_actual_action", "different_actual_actions",
    )})
    for row in pair_rows:
        h, l = row["human"], row["luna"]
        if h == l == "NONE":
            pair_categories["both_explicit_no_action"] += 1
        elif h == "NONE":
            pair_categories["human_no_action_luna_action"] += 1
        elif l == "NONE":
            pair_categories["human_action_luna_no_action"] += 1
        elif h == l:
            pair_categories["same_actual_action"] += 1
        else:
            pair_categories["different_actual_actions"] += 1
    assert sum(pair_categories.values()) == len(pair_rows)
    both_actual = [r for r in pair_rows if r["human"] != "NONE" and r["luna"] != "NONE"]
    any_none = [r for r in pair_rows if "NONE" in (r["human"], r["luna"])]
    coverage_cells = Counter((r["reference"]["status"], mapping_state(r["human"]), mapping_state(r["luna"])) for r in rows)
    common_ids = {r["case_id"] for r in common}
    common_exclusions = [r for r in rows if r["case_id"] not in common_ids]
    a, b, c, d, e = (partition[p] for p in PARTITIONS)
    multiple = [r for r in rows if r["reference"]["status"] == "multiple_actions"]
    multi_counts = Counter({s: 0 for s in (
        "at_least_one_uninterpretable", "both_acceptable_same_action",
        "both_acceptable_different_actions", "only_human_acceptable",
        "only_luna_acceptable", "neither_acceptable",
    )})
    multi_by_coder = {c: Counter({s: 0 for s in ("acceptable", "not_in_acceptable_set", "uninterpretable")}) for c in ("human", "luna")}
    for row in multiple:
        accepted = set(row["reference_event_ids"])
        for coder in ("human", "luna"):
            key = "uninterpretable" if row[coder] is None else "acceptable" if row[coder] in accepted else "not_in_acceptable_set"
            multi_by_coder[coder][key] += 1
        if row["human"] is None or row["luna"] is None:
            multi_counts["at_least_one_uninterpretable"] += 1
        elif row["human"] in accepted and row["luna"] in accepted:
            multi_counts["both_acceptable_same_action" if row["human"] == row["luna"] else "both_acceptable_different_actions"] += 1
        elif row["human"] in accepted:
            multi_counts["only_human_acceptable"] += 1
        elif row["luna"] in accepted:
            multi_counts["only_luna_acceptable"] += 1
        else:
            multi_counts["neither_acceptable"] += 1
    return {
        "eligible_records": len(rows),
        "reference_status_counts": dict(ref_states),
        "choice_interpretability": {c: dict(v) for c, v in choice_states.items()},
        "ambiguous_action_anchor_counts": {
            c: sum(r[c] is None and bool(r.get("possible_event_ids", {}).get(c)) for r in rows)
            for c in ("human", "luna")
        },
        "coverage_cells": [
            {"reference_status": k[0], "human_choice_status": k[1], "luna_choice_status": k[2], "n": n}
            for k, n in sorted(coverage_cells.items())
        ],
        "full_observed_human_luna": {
            **ratio(sum(r["human"] == r["luna"] for r in pair_rows), len(pair_rows)),
            "coverage_of_eligible": fraction(len(pair_rows), len(rows)),
            "uninterpretable_pair_n": len(rows) - len(pair_rows),
            "pair_categories": dict(pair_categories),
            "both_select_actual_actions": ratio(sum(r["human"] == r["luna"] for r in both_actual), len(both_actual)),
            "at_least_one_explicit_no_action": ratio(sum(r["human"] == r["luna"] for r in any_none), len(any_none)),
        },
        "common_unique_reference_threeway": {
            "n": len(common),
            "coverage_of_eligible": fraction(len(common), len(rows)),
            "five_way_partition": dict(partition),
            "human_luna": ratio(a + d, len(common)),
            "human_reference": ratio(a + b, len(common)),
            "luna_reference": ratio(a + c, len(common)),
            "paired_luna_minus_human_matches": c - b,
            "paired_luna_minus_human_share": fraction(c - b, len(common)),
            "reference_no_action_n": sum(r["reference_id"] == "NONE" for r in common),
            "reference_actual_action_n": sum(r["reference_id"] != "NONE" for r in common),
            "_case_ids": [r["case_id"] for r in common],
            "_case_partition": classification,
            "_excluded_case_ids": [r["case_id"] for r in common_exclusions],
        },
        "unique_reference_subgroups": {
            label: {
                "n": len(group),
                "human_luna": ratio(sum(r["human"] == r["luna"] for r in group), len(group)),
                "human_reference": ratio(sum(r["human"] == r["reference_id"] for r in group), len(group)),
                "luna_reference": ratio(sum(r["luna"] == r["reference_id"] for r in group), len(group)),
            }
            for label, group in (
                ("actual_action", [r for r in common if r["reference_id"] != "NONE"]),
                ("explicit_no_action", [r for r in common if r["reference_id"] == "NONE"]),
            )
        },
        "multiple_reference_acceptability": {
            "n": len(multiple),
            "per_coder": {c: dict(v) for c, v in multi_by_coder.items()},
            "joint": dict(multi_counts),
            "_case_ids": [r["case_id"] for r in multiple],
        },
    }


def split_private(value: Any, trail: str = "") -> tuple[Any, dict[str, Any]]:
    """Keep case memberships and review issues in a separate private diagnostic."""
    diagnostics = {}
    if isinstance(value, dict):
        clean = {}
        for key, val in value.items():
            child = f"{trail}.{key}" if trail else key
            if key.startswith("_"):
                diagnostics[child] = val
            else:
                clean[key], more = split_private(val, child)
                diagnostics.update(more)
        return clean, diagnostics
    if isinstance(value, list):
        clean = []
        for i, val in enumerate(value):
            item, more = split_private(val, f"{trail}[{i}]")
            clean.append(item)
            diagnostics.update(more)
        return clean, diagnostics
    return value, diagnostics


def sensitivity_groups(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return {
        "all_266": records,
        "exclude_7_changed_text_views": [r for r in records if not r["source_changed"]],
        "only_262_structurally_valid_outputs": [r for r in records if r["luna_status"] == "valid"],
        "exclude_changed_text_and_structural_failures": [r for r in records if not r["source_changed"] and r["luna_status"] == "valid"],
    }


def ambiguous_anchor_sensitivity(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Enumerate declared anchor interpretations without choosing one as truth."""
    anchors = [(r["case_id"], coder, r["possible_event_ids"][coder])
               for r in records for coder in ("human", "luna")
               if r[coder] is None and r.get("possible_event_ids", {}).get(coder)]
    if not anchors:
        return {"ambiguous_anchor_n": 0, "scenarios": []}
    combinations = math.prod(len(a[2]) for a in anchors)
    assert combinations <= 256, "Too many anchor combinations for exhaustive sensitivity"
    by_id = {r["case_id"]: r for r in records}
    scenarios = []
    for index, selected in enumerate(itertools.product(*(a[2] for a in anchors)), 1):
        substitutions = {(a[0], a[1]): eid for a, eid in zip(anchors, selected)}
        modified = [dict(r, **{c: substitutions.get((r["case_id"], c), r[c])
                              for c in ("human", "luna")}) for r in records]
        scenarios.append({
            "scenario": index,
            "assigned_unique_reference_n": sum(eid == by_id[a[0]]["reference_id"] for a, eid in zip(anchors, selected)),
            "event_comparisons": {name: event_summary(rows) for name, rows in sensitivity_groups(modified).items()},
            "_assignments": [{"case_id": a[0], "coder": a[1], "event_id": eid}
                             for a, eid in zip(anchors, selected)],
        })
    bounds = {}
    for sensitivity in sensitivity_groups(records):
        bounds[sensitivity] = {}
        for metric in ("full_observed_human_luna", "human_luna", "human_reference", "luna_reference"):
            values = [s["event_comparisons"][sensitivity] for s in scenarios]
            pairs = [v[metric] if metric == "full_observed_human_luna" else v["common_unique_reference_threeway"][metric] for v in values]
            bounds[sensitivity][metric] = {
                k + "_min": min(v[k] for v in pairs) for k in ("matches", "compared", "share")
            } | {k + "_max": max(v[k] for v in pairs) for k in ("matches", "compared", "share")}
    return {
        "ambiguous_anchor_n": len(anchors),
        "ambiguous_case_n": len({a[0] for a in anchors}),
        "interpretation": "Each scenario assigns every declared ambiguous anchor to one of its possible event identities. These are sensitivity cases, not adjudicated corrections; the primary comparison keeps these anchors unresolved.",
        "bounds": bounds,
        "scenarios": scenarios,
    }


def assemble_records(inputs: dict[str, dict[str, dict[str, Any]]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ids = set(inputs["coder_key"])
    assert len(ids) == 266, f"Expected 266 frozen cases, found {len(ids)}"
    for name, rows in inputs.items():
        assert set(rows) == ids, f"Membership mismatch in {name}"
    records = []
    warnings = []
    for cid in sorted(ids):
        ref, mapped, key, aux, prior = (inputs[k][cid] for k in ("references", "mapping", "coder_key", "original_fields", "prior_provenance"))
        source_rows = {r["source_row"] for r in (ref, mapped, key, aux, prior)}
        assert len(source_rows) == 1, (cid, "source_row mismatch")
        status = ref.get("status")
        assert status in STATUSES, (cid, "invalid reference status", status)
        events = ref.get("events")
        assert isinstance(events, list), (cid, "events must be a list")
        event_ids = [ev["event_id"] for ev in events]
        assert len(event_ids) == len(set(event_ids)), (cid, "duplicate reference IDs")
        assert all(re.fullmatch(r"E[1-9]\d*", eid) for eid in event_ids), (cid, event_ids)
        if status == "single_action":
            assert len(event_ids) == 1, cid
            ref_id = event_ids[0]
        elif status == "no_action":
            assert not event_ids, cid
            ref_id = "NONE"
        elif status == "multiple_actions":
            assert len(event_ids) >= 2, cid
            ref_id = None
        else:
            assert not event_ids, cid
            ref_id = None
        extras = mapped.get("other_events", [])
        extra_ids = [ev["event_id"] for ev in extras]
        assert len(extra_ids) == len(set(extra_ids)), (cid, "duplicate alternate IDs")
        assert all(re.fullmatch(r"X[1-9]\d*", eid) for eid in extra_ids), (cid, extra_ids)
        choices = {}
        possible_choices = {}
        for candidate in ("candidate_A", "candidate_B"):
            coder = key[candidate]
            assert coder in ("human", "luna"), (cid, coder)
            choice = mapped[candidate]
            eid = choice.get("event_id")
            assert eid is None or eid == "NONE" or eid in set(event_ids + extra_ids), (cid, candidate, eid)
            assert scalar(choice.get("reason")), (cid, candidate, "missing mapping rationale")
            assert isinstance(choice.get("extraction_issues", []), list), (cid, candidate)
            possible = choice.get("possible_event_ids", [])
            assert isinstance(possible, list), (cid, candidate, "possible IDs must be a list")
            assert not possible or eid is None, (cid, candidate, "possibilities only for unresolved anchor")
            assert len(possible) == len(set(possible)), (cid, candidate, "duplicate possible IDs")
            assert all(p == "NONE" or p in set(event_ids + extra_ids) for p in possible), (cid, candidate, possible)
            choices[coder] = eid
            possible_choices[coder] = possible
        assert set(choices) == {"human", "luna"}, (cid, "coder key not a permutation")
        luna_status = prior["luna_status"]
        assert luna_status in ("valid", "invalid"), (cid, luna_status)
        assert luna_status == aux["luna_original_status"], (cid, "structural status mismatch")
        if mapped.get("reference_concern") is not None:
            warnings.append({"case_id": cid, "type": "recorded_reference_concern", "detail": mapped["reference_concern"]})
        for coder, original in (("human", aux["human_november_full_original_fields"].get("action_final")),
                                ("luna", (aux.get("luna_original_15_fields") or {}).get("act"))):
            if choices[coder] == "NONE" and scalar(original) is not None:
                warnings.append({"case_id": cid, "type": "no_action_mapping_with_nonempty_recorded_action", "coder": coder})
        records.append({
            "case_id": cid, "source_row": ref["source_row"], "reference": ref,
            "reference_event_ids": event_ids, "reference_id": ref_id, **choices,
            "possible_event_ids": possible_choices,
            "luna_status": luna_status,
            "source_changed": bool(prior.get("source_version_changed_fields")),
            "aux": aux, "prior": prior,
        })
    assert len({r["source_row"] for r in records}) == 266
    assert sum(r["luna_status"] == "invalid" for r in records) == 4
    assert sum(r["source_changed"] for r in records) == 7
    return records, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT,
                        help="Private directory containing the frozen JSONL inputs and protocols.")
    parser.add_argument("--output-dir", type=Path,
                        help="Aggregate-only output directory; defaults to --input-dir.")
    parser.add_argument("--diagnostics-dir", type=Path,
                        help="PRIVATE diagnostics destination; defaults to --input-dir, never --output-dir.")
    parser.add_argument("--references", default="reference_final.jsonl")
    parser.add_argument("--mapping", default="mapping_final.jsonl")
    parser.add_argument("--output", default="event_metrics.json")
    parser.add_argument("--diagnostics", default="event_metrics_diagnostics.json")
    args = parser.parse_args()
    root = args.input_dir.resolve()
    output_dir = args.output_dir.resolve() if args.output_dir else root
    diagnostics_dir = args.diagnostics_dir.resolve() if args.diagnostics_dir else root
    paths = {
        "references": root / args.references,
        "mapping": root / args.mapping,
        "coder_key": root / "analyst/CODER_KEY_PRIVATE.jsonl",
        "original_fields": root / "analyst/FULL_CODER_FIELDS_AUX_V1.jsonl",
        "prior_provenance": root / "analyst/PRIOR_EVENT_REVIEW_PRIVATE.jsonl",
    }
    missing = [str(p) for p in paths.values() if not p.is_file()]
    if missing:
        print(json.dumps({"status": "waiting_for_final_inputs", "missing": missing}, indent=2))
        return 2
    inputs = {k: load_jsonl(p) for k, p in paths.items()}
    records, warnings = assemble_records(inputs)
    ids = set(inputs["coder_key"])
    revisions = {}
    for kind, initial_name, current in (
        ("reference", "reference_initial.jsonl", inputs["references"]),
        ("mapping", "mapping_initial.jsonl", inputs["mapping"]),
    ):
        initial_path = root / initial_name
        if initial_path.is_file():
            initial = load_jsonl(initial_path)
            assert set(initial) == ids, f"Initial {kind} membership mismatch"
            changed_ids = [cid for cid in sorted(ids) if initial[cid] != current[cid]]
            revisions[kind] = {
                "initial_file": initial_name,
                "initial_sha256": digest(initial_path),
                "final_sha256": digest(paths["references" if kind == "reference" else "mapping"]),
                "revised_records_n": len(changed_ids),
                "_revised_case_ids": changed_ids,
            }
            if kind == "reference":
                def identity_fields(row: dict[str, Any]) -> Any:
                    return row["status"], [tuple(e.get(k) for k in ("event_id", "actor", "action", "target", "stage", "gov_reference")) for e in row["events"]]
                identity_changed = [cid for cid in sorted(ids) if identity_fields(initial[cid]) != identity_fields(current[cid])]
                structure_changed = [cid for cid in sorted(ids) if
                    (initial[cid]["status"], [e["event_id"] for e in initial[cid]["events"]]) !=
                    (current[cid]["status"], [e["event_id"] for e in current[cid]["events"]])]
                revisions[kind].update({
                    "identity_field_changes_n": len(identity_changed),
                    "status_or_event_id_structure_changes_n": len(structure_changed),
                    "rationale_evidence_or_other_only_changes_n": len(set(changed_ids) - set(identity_changed)),
                    "_identity_field_changed_case_ids": identity_changed,
                })
            else:
                event_id_changed = [cid for cid in sorted(ids) if any(
                    initial[cid][c].get("event_id") != current[cid][c].get("event_id")
                    for c in ("candidate_A", "candidate_B"))]
                possibilities_changed = [cid for cid in sorted(ids) if any(
                    initial[cid][c].get("possible_event_ids", []) != current[cid][c].get("possible_event_ids", [])
                    for c in ("candidate_A", "candidate_B"))]
                revisions[kind].update({
                    "candidate_event_id_changes_n": len(event_id_changed),
                    "candidate_possibilities_changes_n": len(possibilities_changed),
                    "rationale_metadata_or_other_only_changes_n": len(set(changed_ids) - set(event_id_changed) - set(possibilities_changed)),
                    "_candidate_event_id_changed_case_ids": event_id_changed,
                })
    audit_provenance = {}
    for name in ("audit_revision_log.json", "audit_sampling.json", "audit_decisions.jsonl"):
        audit_path = root / name
        if audit_path.is_file():
            audit_provenance[name] = {"sha256": digest(audit_path)}
            if name == "audit_revision_log.json":
                audit_log = json.loads(audit_path.read_text())
                audit_provenance[name].update({k: audit_log[k] for k in ("audited_n", "reference_revisions") if k in audit_log})
                audit_provenance[name]["logged_change_entries_n"] = len(audit_log.get("changes", []))
    source_path = root / "reviewer/references_only.jsonl"
    sample_dates = {"available": False}
    if source_path.is_file():
        sources = load_jsonl(source_path)
        assert set(sources) == ids, "Source-date membership mismatch"
        valid_dates = []
        for source in sources.values():
            try:
                valid_dates.append(dt.date.fromisoformat(str(source.get("publication_date"))[:10]))
            except (ValueError, TypeError):
                pass
        sample_dates = {
            "available": True,
            "source_sha256": digest(source_path),
            "dated_n": len(valid_dates),
            "missing_or_invalid_date_n": len(records) - len(valid_dates),
            "publication_date_min": min(valid_dates).isoformat() if valid_dates else None,
            "publication_date_max": max(valid_dates).isoformat() if valid_dates else None,
            "year_counts": dict(sorted(Counter(str(d.year) for d in valid_dates).items())),
            "scope_note": "Dates describe this historical validation sample, not the current analytical corpus.",
        }
    sensitivities = sensitivity_groups(records)
    initial_event_comparisons = None
    initial_warnings = []
    if (root / "reference_initial.jsonl").is_file() and (root / "mapping_initial.jsonl").is_file():
        initial_inputs = dict(inputs)
        initial_inputs["references"] = load_jsonl(root / "reference_initial.jsonl")
        initial_inputs["mapping"] = load_jsonl(root / "mapping_initial.jsonl")
        initial_records, initial_warnings = assemble_records(initial_inputs)
        initial_event_comparisons = {
            "pass_description": "Initial source-first reference and initial anonymized mapping before subsequent audited revisions.",
            "reference_sha256": digest(root / "reference_initial.jsonl"),
            "mapping_sha256": digest(root / "mapping_initial.jsonl"),
            "event_comparisons": {name: event_summary(rows) for name, rows in sensitivity_groups(initial_records).items()},
        }
    same_action = [r for r in records if r["human"] is not None and r["human"] != "NONE" and r["human"] == r["luna"]]
    both_reference = [r for r in records if r["reference"]["status"] == "single_action" and r["human"] == r["luna"] == r["reference_id"]]
    cohorts = {
        "human_luna_same_actual_action": same_action,
        "human_luna_both_match_unique_reference_action": both_reference,
        "same_actual_action_structurally_valid_only": [r for r in same_action if r["luna_status"] == "valid"],
        "both_match_reference_action_structurally_valid_only": [r for r in both_reference if r["luna_status"] == "valid"],
    }
    result = {
        "schema_version": 1,
        "title": "Symmetric reported-action comparison from frozen source-first references",
        "review_date": "2026-11-10",
        "rules": {
            "unit": "One historical validation case; membership fixed at 266.",
            "review_provenance": "Model-assisted reference first selected unseen candidate answers, followed by anonymized mapping and a logged subset audit using anonymous answers. Initial and final passes are separately reported; not independent human ground truth.",
            "unique_reference_mask": "single_action or explicit no_action reference, and interpretable choices from both coders. No correctness or old coder-specific selection flag controls inclusion.",
            "no_action": "Explicit NONE is a substantive choice. Missing/uninterpretable choices are not NONE. Shared explicit NONE counts as event-choice agreement.",
            "unsupported_choices": "Interpretable unsupported actions remain in the comparison as distinct X identities; they are not excluded as unmappable.",
            "structural_failures": "All four readable action choices can enter event-only metrics; invalid full-record status remains separately recorded.",
            "field_missingness": "Pairwise field denominators require comparable values on both sides. Missing/uncodable fields are excluded, never silently counted as matching.",
            "actor_wording": "Literal comparison preserves recorded wording including surrounding whitespace. Normalized comparison strips/collapses whitespace and casefolds. Neither is a semantic entity-equivalence score.",
            "category_and_tag_normalization": "Extract existing A–W category code; compare action tag lists as exact sets and first tags separately. No semantic retagging.",
            "government_normalization": "Only single interpretable country codes; explicit US→USA, SD→SDN, SS→SSD aliases. Multiple-country and prose cells remain incomparable.",
            "human_sentiment": "The original human coding has one legacy sentiment field. No human three-dimension agreement is manufactured.",
            "historical_review": "Saved November 3 assessments remain dependent on the original Luna action and government; recomputing their subgroup counts is not new political-label coding.",
            "legacy_rates": "Prior 178/262 and 187-case rates are historical comparisons, not constraints on this fresh semantic mapping.",
        },
        "input_status": {
            "records": len(records),
            "luna_structural_status": dict(Counter(r["luna_status"] for r in records)),
            "changed_text_view_n": sum(r["source_changed"] for r in records),
            "reference_concern_count": sum(w["type"] == "recorded_reference_concern" for w in warnings),
        },
        "historical_sample_dates": sample_dates,
        "event_comparisons": {name: event_summary(rows) for name, rows in sensitivities.items()},
        "initial_pass_sensitivity": initial_event_comparisons,
        "ambiguous_action_anchor_sensitivity": ambiguous_anchor_sensitivity(records),
        "field_comparison_cohorts": {name: field_metrics(rows) for name, rows in cohorts.items()},
        "historical_political_label_review": {name: historical_label_metrics(rows) for name, rows in cohorts.items()},
        "_cohort_case_ids": {name: [r["case_id"] for r in rows] for name, rows in cohorts.items()},
        "_warnings": warnings,
        "_initial_pass_warnings": initial_warnings,
        "_case_decoded_identities": [
            {"case_id": r["case_id"], "source_row": r["source_row"], "reference_status": r["reference"]["status"],
             "reference_id": r["reference_id"], "human": r["human"], "luna": r["luna"],
             "luna_structural_status": r["luna_status"], "changed_text": r["source_changed"]}
            for r in records
        ],
        "provenance": {
            "inputs": {name: {"file": str(path.relative_to(root)), "sha256": digest(path)} for name, path in paths.items()},
            "protocol_sha256": digest(root / "PROTOCOL.txt"),
            "mapping_protocol_sha256": digest(root / "MAPPING_PROTOCOL.txt"),
            "reducer_sha256": digest(Path(__file__)),
            "review_revisions": revisions,
            "audit_files": audit_provenance,
        },
    }
    clean, diagnostic = split_private(result)
    diagnostic = {"schema_version": 1, "aggregate_input_provenance": clean["provenance"], "private_diagnostics": diagnostic}
    output_dir.mkdir(parents=True, exist_ok=True)
    diagnostics_dir.mkdir(parents=True, exist_ok=True)
    for target, value in ((output_dir / args.output, clean), (diagnostics_dir / args.diagnostics, diagnostic)):
        target.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n")
        target.chmod(0o600)
    print(json.dumps({"status": "complete", "output": args.output, "diagnostics": args.diagnostics,
                      "event_summary": clean["event_comparisons"]["all_266"],
                      "field_cohort_sizes": {k: v["n"] for k, v in clean["field_comparison_cohorts"].items()},
                      "warnings": len(warnings)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
