"""Step 2: three-way HARD filtering and single-HARD removal diagnostics."""

from copy import deepcopy

from .contracts import LEVELS


def _classify(candidate, removed_requirement=None):
    failures, conditions, passes = [], [], []
    for row in candidate["assessments"]:
        if row["role"] != "HARD" or row["requirement_id"] == removed_requirement:
            continue
        threshold = LEVELS.index(row["min_level"])
        low, high = (LEVELS.index(row["level_interval"][key]) for key in ["min", "max"])
        reason = {
            "requirement_id": row["requirement_id"], "min_level": row["min_level"],
            "level_interval": deepcopy(row["level_interval"]),
            "claim_ids": list(row["trace"]["claim_ids"]),
            "conditions": deepcopy(row["conditions"]),
            "unknown_reasons": list(row["unknown_reasons"]),
        }
        if high < threshold:
            reason["reason"] = "maximum_supported_level_below_minimum"
            failures.append(reason)
        elif low < threshold or row["level"] == "unknown" or row["unknown_reasons"]:
            reason["reason"] = "support_not_established_for_every_allowed_case"
            conditions.append(reason)
        else:
            reason["reason"] = "minimum_met_for_every_declared_case"
            passes.append(reason)
    return {
        **deepcopy(candidate),
        "group": "excluded" if failures else "conditional" if conditions or candidate.get("input_conditions") else "eligible",
        "hard_failures": failures, "hard_conditions": conditions, "hard_passes": passes,
    }


def filter_hard(lookups):
    """Relaxations are diagnostics only; they never alter the original groups."""
    groups = {key: [] for key in ["eligible", "conditional", "excluded"]}
    for candidate in sorted(lookups, key=lambda c: c["candidate_id"]):
        classified = _classify(candidate)
        groups[classified["group"]].append(classified)
    relaxations = []
    if not groups["eligible"]:
        hard_ids = sorted({r["requirement_id"] for c in lookups for r in c["assessments"] if r["role"] == "HARD"})
        for rid in hard_ids:
            after = [_classify(c, removed_requirement=rid) for c in sorted(lookups, key=lambda c: c["candidate_id"])]
            relaxations.append({
                "removed_requirement_id": rid,
                "eligible_after_relaxation": [c["candidate_id"] for c in after if c["group"] == "eligible"],
                "conditional_after_relaxation": [c["candidate_id"] for c in after if c["group"] == "conditional"],
                "excluded_after_relaxation": [c["candidate_id"] for c in after if c["group"] == "excluded"],
                "diagnostic_only": True,
                "trace": [{"candidate_id": c["candidate_id"], "removed_requirement_id": rid, "remaining_failures": c["hard_failures"], "remaining_conditions": c["hard_conditions"], "remaining_passes": c["hard_passes"], "remaining_input_conditions": c.get("input_conditions", [])} for c in after],
            })
    return {"groups": groups, "relaxations": relaxations}
