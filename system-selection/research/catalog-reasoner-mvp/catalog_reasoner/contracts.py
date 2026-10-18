"""Input validation and explicit configuration assumptions; no inference or I/O."""

from copy import deepcopy
from math import isfinite


LEVELS = ("none", "partial", "full")
LOOKUP_POLICIES = {
    "candidate_unit": "one_explicit_KB_scope",
    "unknown_open_domain": "observed_compatible_values_plus_uncovered_case",
    "finite_domains": "explicit_qualifier_domains_are_the_complete_allowed_set",
    "conflicting_claims": "unknown_not_last_claim_wins",
    "missing_claim_qualifier": "not_a_wildcard",
    "claim_status": "use_supplied_claims_and_preserve_status_and_limits_in_trace",
}


def requirement_rows(document):
    return document["requirements"] + document.get("objectives", [])


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def _records(rows, kind):
    _require(isinstance(rows, list), f"{kind} must be an array")
    ids = []
    for row in rows:
        _require(isinstance(row, dict) and isinstance(row.get("id"), str) and bool(row["id"]), f"{kind} needs nonempty string IDs")
        ids.append(row["id"])
    _require(len(ids) == len(set(ids)), f"Duplicate {kind} ID")


def _qualifiers(values, nullable):
    _require(isinstance(values, dict), "qualifiers must be a flat object")
    for key, value in values.items():
        _require(isinstance(key, str) and bool(key), "Invalid qualifier key")
        _require((nullable and value is None) or (isinstance(value, str) and bool(value)), f"Invalid qualifier {key}")


def validate_inputs(kb, document, config):
    """Reject malformed input; preserve conflicting *claims* for unknown inference."""
    _require(all(isinstance(x, dict) for x in [kb, document, config]), "Inputs must be JSON objects")
    for key in ["level_to_value", "rank_to_weight", "parameter_metadata", "lookup_assumptions"]:
        _require(isinstance(config.get(key), dict), f"Missing config object: {key}")
    _require(set(config["level_to_value"]) == set(LEVELS), "level_to_value must define none/partial/full")
    values = [config["level_to_value"][level] for level in LEVELS]
    _require(all(_number(v) for v in values) and values == sorted(values), "level_to_value must be finite and monotone")
    _require(bool(config["rank_to_weight"]) and all(_number(w) and w > 0 for w in config["rank_to_weight"].values()), "Weights must be finite and positive")
    _require(type(config.get("seed")) is int, "seed must be an integer")
    _require(type(config.get("max_scenarios")) is int and config["max_scenarios"] > 0, "max_scenarios must be a positive integer")
    _require(config.get("default_hard_min_level") in LEVELS, "Invalid default_hard_min_level")
    _require(config.get("default_weight_rank") in config["rank_to_weight"], "Invalid default_weight_rank")
    _require(config["lookup_assumptions"] == LOOKUP_POLICIES, "Unsupported lookup policy; no silent policy substitution")
    for key in ["level_to_value", "rank_to_weight", "max_scenarios", "seed", "default_hard_min_level", "default_weight_rank"]:
        _require(config["parameter_metadata"].get(key, {}).get("assumption") is True, f"Config parameter {key} must be marked assumption")
    _require(set(config) == {"level_to_value", "rank_to_weight", "max_scenarios", "seed", "default_hard_min_level", "default_weight_rank", "parameter_metadata", "lookup_assumptions"}, "Unknown config parameter")

    for key in ["scopes", "claims"]:
        _records(kb.get(key), key)
    _records(document.get("requirements"), "requirement")
    _records(document.get("objectives", []), "objective")
    _records(requirement_rows(document), "combined requirement/objective")
    _require(all(r.get("role") == "SOFT" for r in document.get("objectives", [])), "Separate objectives must explicitly have role SOFT")
    _records(document.get("candidates"), "candidate")
    scopes = {s["id"] for s in kb["scopes"]}
    for candidate in document["candidates"]:
        _require(candidate.get("scope_id") in scopes, f"Unknown candidate scope: {candidate.get('scope_id')}")
    for claim in kb["claims"]:
        _require(claim.get("scope_id") in scopes, "Claim refers to unknown scope")
        _require(isinstance(claim.get("property_id"), str) and bool(claim["property_id"]), "Claim needs property_id")
        _qualifiers(claim.get("qualifiers", {}), nullable=False)
        _require(claim.get("level") in (*LEVELS, "unknown", None), f"Invalid claim level: {claim.get('level')}")
    for requirement in requirement_rows(document):
        _require(requirement.get("role") in {"HARD", "SOFT"}, "Requirement role must be HARD or SOFT")
        _require(isinstance(requirement.get("property_id"), str) and bool(requirement["property_id"]), "Requirement needs property_id")
        qualifiers = requirement.get("qualifiers", {})
        _qualifiers(qualifiers, nullable=True)
        _require(requirement.get("status", "ready") in {"ready", "needs_context", "needs_rank", "proposed_needs_confirmation"}, "Invalid requirement status")
        minimum = requirement.get("min_level_if_applicable")
        _require(minimum is None or minimum in LEVELS, "Invalid requirement minimum")
        domains = requirement.get("qualifier_domains", {})
        _require(isinstance(domains, dict), "qualifier_domains must be an object")
        for key, domain in domains.items():
            _require(isinstance(key, str) and bool(key), "Invalid domain key")
            _require(isinstance(domain, list) and bool(domain) and all(isinstance(x, str) and bool(x) for x in domain), "Domains must be nonempty string arrays")
            _require(len(domain) == len(set(domain)), "Duplicate qualifier-domain value")
            _require(qualifiers.get(key) is None or qualifiers[key] in domain, "Known qualifier contradicts its allowed domain")


def assumptions_used(document, config):
    """Echo every numeric parameter, including parameters reserved for later stages."""
    records = []
    requirements = requirement_rows(document)
    for key in ["level_to_value", "rank_to_weight", "max_scenarios", "seed", "default_hard_min_level", "default_weight_rank"]:
        value = config[key]
        leaves = sorted(value.items()) if isinstance(value, dict) else [(None, value)]
        for leaf, item in leaves:
            records.append({
                "parameter": f"{key}.{leaf}" if leaf else key,
                "value": deepcopy(item), "assumption": True,
                "applied_in_stage12": key == "default_hard_min_level" and any(r["role"] == "HARD" and r.get("min_level_if_applicable") is None for r in requirements),
                "note": config["parameter_metadata"][key].get("note", ""),
            })
            if key == "default_hard_min_level":
                records[-1]["requirements"] = sorted(r["id"] for r in requirements if r["role"] == "HARD" and r.get("min_level_if_applicable") is None)
    for key, value in sorted(config["lookup_assumptions"].items()):
        records.append({"parameter": f"lookup.{key}", "value": value, "assumption": True, "applied_in_stage12": True})
    for key, default in [("status", "ready"), ("qualifiers", {})]:
        missing = sorted(r["id"] for r in requirements if key not in r)
        if missing:
            records.append({"parameter": f"requirement.{key}", "value": default, "assumption": True, "applied_in_stage12": True, "requirements": missing})
    return records
