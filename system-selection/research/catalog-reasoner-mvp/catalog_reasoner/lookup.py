"""Step 1: exact scope/qualifier lookup and conservative support intervals."""

from copy import deepcopy
from itertools import product

from .contracts import LEVELS


def _compatible(claim, qualifiers, domains):
    values = claim.get("qualifiers", {})
    if any(value is not None and key in values and values[key] != value for key, value in qualifiers.items()):
        return False
    return not any(key in values and values[key] not in domain for key, domain in domains.items())


def _one_case(claims, assignment):
    possible = [c for c in claims if all(key not in c.get("qualifiers", {}) or c["qualifiers"][key] == value for key, value in assignment.items())]
    complete = [c for c in possible if all(value is not None and c.get("qualifiers", {}).get(key) == value for key, value in assignment.items())]
    reasons = []
    if not complete:
        reasons.append("no_matching_claim")
        if possible:
            reasons.append("incomplete_claim_qualifiers")
        levels = list(LEVELS)
    elif any(c.get("level") not in LEVELS for c in complete):
        reasons.append("claim_level_unknown_or_not_support")
        levels = list(LEVELS)
    else:
        levels = sorted({c["level"] for c in complete}, key=LEVELS.index)
        if len(levels) > 1:
            reasons.append("conflicting_claims")
            levels = list(LEVELS)
    return {
        "qualifiers": deepcopy(assignment),
        "level_interval": {"min": levels[0], "max": levels[-1]},
        "claim_ids": sorted(c["id"] for c in (complete or possible)),
        "unknown_reasons": reasons,
    }


def _lookup_requirement(kb, candidate, requirement, config):
    qualifiers = requirement.get("qualifiers", {})
    domains = requirement.get("qualifier_domains", {})
    claims = sorted((c for c in kb["claims"] if c["scope_id"] == candidate["scope_id"] and c["property_id"] == requirement["property_id"] and _compatible(c, qualifiers, domains)), key=lambda c: c["id"])
    dimensions = sorted(set(qualifiers) | set(domains) | {key for c in claims for key in c.get("qualifiers", {})})
    choices = []
    conditions = []
    open_domain = False
    for key in dimensions:
        if qualifiers.get(key) is not None:
            choices.append([qualifiers[key]])
        else:
            finite = domains.get(key)
            # None is a symbolic unobserved value, never a wildcard matching a claim.
            values = sorted(finite) if finite is not None else sorted({c["qualifiers"][key] for c in claims if key in c.get("qualifiers", {})}) + [None]
            choices.append(values)
            conditions.append({"type": "qualifier_unresolved", "qualifier": key, "allowed_values": deepcopy(finite), "domain_complete": finite is not None})
            open_domain = open_domain or finite is None
    cases = [_one_case(claims, dict(zip(dimensions, values))) for values in product(*choices)]
    reasons = {reason for case in cases for reason in case["unknown_reasons"]}
    low = min((case["level_interval"]["min"] for case in cases), key=LEVELS.index)
    high = max((case["level_interval"]["max"] for case in cases), key=LEVELS.index)
    if open_domain:
        reasons.add("open_qualifier_domain")
    if requirement.get("status", "ready") != "ready":
        low, high = LEVELS[0], LEVELS[-1]
        reasons.add("requirement_not_ready")
        conditions.append({"type": "layer2_status", "status": requirement["status"]})
    used = {cid for case in cases for cid in case["claim_ids"]}
    return {
        "requirement_id": requirement["id"],
        "property_id": requirement["property_id"],
        "role": requirement["role"],
        "min_level": (requirement.get("min_level_if_applicable") or config["default_hard_min_level"]) if requirement["role"] == "HARD" else None,
        "level": low if low == high else "unknown",
        "level_interval": {"min": low, "max": high},
        "conditions": conditions,
        "unknown_reasons": sorted(reasons),
        "trace": {
            "requirement_id": requirement["id"], "scope_id": candidate["scope_id"],
            "requested_qualifiers": deepcopy(qualifiers),
            "candidate_bindings": deepcopy(requirement.get("candidate_bindings", {})),
            "claim_ids": sorted(used),
            "claims": [deepcopy(c) for c in claims if c["id"] in used],
            "cases": cases,
        },
    }


def lookup_levels(kb, candidates, requirements, config):
    """Pure lookup. Input contracts are validated once by the pipeline."""
    return [{
        "candidate_id": candidate["id"],
        "scope_id": candidate["scope_id"],
        "assessments": [_lookup_requirement(kb, candidate, requirement, config) for requirement in sorted(requirements, key=lambda r: r["id"])],
    } for candidate in sorted(candidates, key=lambda c: c["id"])]
