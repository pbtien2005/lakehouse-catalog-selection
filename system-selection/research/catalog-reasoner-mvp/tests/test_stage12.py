"""Behavior tests for the first review gate; scoring and scenarios are not run."""

from copy import deepcopy
import importlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def inputs():
    def load(name):
        return json.loads((ROOT / name).read_text(encoding="utf-8"))
    return load("examples/synthetic-kb.json"), load("examples/synthetic-requirements.json"), load("config.json")


def run(inputs):
    # Import inside the executed test: RED initially demonstrates missing code.
    return importlib.import_module("catalog_reasoner.pipeline").run_stage12(*inputs)


def candidate(result, cid):
    return next(c for group in result["groups"].values() for c in group if c["candidate_id"] == cid)


def assessment(result, cid, rid):
    return next(a for a in candidate(result, cid)["assessments"] if a["requirement_id"] == rid)


def alter_claim(inputs, suffix, **updates):
    next(c for c in inputs[0]["claims"] if c["id"] == suffix).update(updates)


def test_three_synthetic_groups_and_requirement_claim_trace(inputs):
    result = run(inputs)
    assert {g: [c["candidate_id"] for c in members] for g, members in result["groups"].items()} == {
        "eligible": ["synthetic_gamma"], "conditional": ["synthetic_alpha"], "excluded": ["synthetic_beta"]}
    failure = candidate(result, "synthetic_beta")["hard_failures"][0]
    assert failure["requirement_id"] == "H-environment"
    assert failure["claim_ids"] == ["synthetic_beta_environment"]


def test_absent_claim_stays_unknown_and_conditional(inputs):
    inputs[0]["claims"] = [c for c in inputs[0]["claims"] if c["id"] != "synthetic_gamma_vending_adls"]
    result = run(inputs)
    assert assessment(result, "synthetic_gamma", "H-vending")["level_interval"] == {"min": "none", "max": "full"}
    assert candidate(result, "synthetic_gamma")["group"] == "conditional"


@pytest.mark.parametrize("level", ["unknown", None])
def test_explicit_unknown_never_becomes_pass_or_failure(inputs, level):
    alter_claim(inputs, "synthetic_gamma_environment", level=level)
    result = run(inputs)
    assert candidate(result, "synthetic_gamma")["group"] == "conditional"
    assert assessment(result, "synthetic_gamma", "H-environment")["level"] == "unknown"


def test_unknown_qualifier_range_carries_both_claims(inputs):
    found = assessment(run(inputs), "synthetic_alpha", "H-vending")
    assert found["level_interval"] == {"min": "none", "max": "full"}
    assert found["trace"]["claim_ids"] == ["synthetic_alpha_vending_adls", "synthetic_alpha_vending_s3"]


def test_open_domain_includes_uncovered_values_even_if_all_observed_full(inputs):
    inputs[1]["requirements"][2].pop("qualifier_domains")
    result = run(inputs)
    assert candidate(result, "synthetic_gamma")["group"] == "conditional"
    assert "open_qualifier_domain" in assessment(result, "synthetic_gamma", "H-vending")["unknown_reasons"]


def test_missing_qualifier_is_not_a_wildcard(inputs):
    next(c for c in inputs[0]["claims"] if c["id"] == "synthetic_gamma_environment")["qualifiers"] = {}
    result = run(inputs)
    assert candidate(result, "synthetic_gamma")["group"] == "conditional"


def test_incompatible_claim_scope_or_value_cannot_supply_support(inputs):
    alter_claim(inputs, "synthetic_gamma_environment", qualifiers={"environment": "azure"})
    result = run(inputs)
    assert assessment(result, "synthetic_gamma", "H-environment")["level"] == "unknown"
    assert candidate(result, "synthetic_gamma")["group"] == "conditional"


def test_conflicting_claims_are_unknown_not_last_wins(inputs):
    other = deepcopy(next(c for c in inputs[0]["claims"] if c["id"] == "synthetic_gamma_environment"))
    other.update(id="synthetic_gamma_environment_conflict", level="none")
    inputs[0]["claims"].append(other)
    result = run(inputs)
    assert candidate(result, "synthetic_gamma")["group"] == "conditional"
    assert "conflicting_claims" in assessment(result, "synthetic_gamma", "H-environment")["unknown_reasons"]


def test_numeric_observation_is_not_converted_to_support(inputs):
    claim = next(c for c in inputs[0]["claims"] if c["id"] == "synthetic_gamma_environment")
    claim.pop("level")
    claim["value"] = {"amount": 10000, "unit": "tables"}
    assert assessment(run(inputs), "synthetic_gamma", "H-environment")["level"] == "unknown"


def test_layer2_needs_context_is_not_ignored(inputs):
    inputs[1]["requirements"][0]["status"] = "needs_context"
    assert candidate(run(inputs), "synthetic_gamma")["group"] == "conditional"


def test_legacy_entrypoint_also_blocks_layer2_input_errors(inputs):
    inputs[1]['readiness']='needs_input_correction'
    inputs[1]['input_issues']=[{'field':'answers.I10','code':'E_RANK_MISSING_OR_INVALID'}]
    result=run(inputs)
    assert result['status']=='input_error'
    assert not result['inference_executed']
    assert all(not rows for rows in result['groups'].values())


def test_legacy_entrypoint_rejects_non_object_document(inputs):
    with pytest.raises(ValueError):
        importlib.import_module('catalog_reasoner.pipeline').run_stage12(inputs[0],[],inputs[2])


def test_no_eligible_candidate_triggers_single_hard_relaxations(inputs):
    for c in inputs[0]["claims"]:
        if c["property_id"] == "deployment.environment":
            c["level"] = "none"
    result = run(inputs)
    assert not result["groups"]["eligible"]
    suggestion = next(r for r in result["relaxations"] if r["removed_requirement_id"] == "H-environment")
    assert suggestion["eligible_after_relaxation"] == ["synthetic_beta", "synthetic_gamma"]
    assert suggestion["conditional_after_relaxation"] == ["synthetic_alpha"]
    gamma_trace = next(t for t in suggestion["trace"] if t["candidate_id"] == "synthetic_gamma")
    assert {p["requirement_id"] for p in gamma_trace["remaining_passes"]} == {"H-format", "H-vending"}
    assert all(p["claim_ids"] for p in gamma_trace["remaining_passes"])


def test_no_false_promise_when_one_relaxation_cannot_fix_two_failures(inputs):
    for c in inputs[0]["claims"]:
        if c["property_id"] in {"deployment.environment", "catalog.format_operation"}:
            c["level"] = "none"
    result = run(inputs)
    assert result["relaxations"]
    assert all(not r["eligible_after_relaxation"] for r in result["relaxations"])


def test_only_soft_requirements_do_not_exclude(inputs):
    inputs[1]["requirements"] = [r for r in inputs[1]["requirements"] if r["role"] == "SOFT"]
    result = run(inputs)
    assert len(result["groups"]["eligible"]) == 3
    assert result["relaxations"] == []


def test_layer2_separate_objectives_are_not_silently_lost(inputs):
    inputs[1]["objectives"] = [r for r in inputs[1]["requirements"] if r["role"] == "SOFT"]
    inputs[1]["requirements"] = [r for r in inputs[1]["requirements"] if r["role"] == "HARD"]
    result = run(inputs)
    assert {r["requirement_id"] for r in candidate(result, "synthetic_gamma")["assessments"]} == {"H-environment", "H-format", "H-vending", "S-branching", "S-federation", "S-authorization"}


def test_same_inputs_seed_and_order_permutations_are_deterministic_and_pure(inputs):
    original = deepcopy(inputs)
    first = run(inputs)
    assert run(inputs) == first
    assert inputs == original
    inputs[0]["claims"].reverse()
    inputs[1]["requirements"].reverse()
    inputs[1]["candidates"].reverse()
    assert run(inputs) == first


def test_config_numeric_assumptions_are_echoed_even_for_reserved_stages(inputs):
    result = run(inputs)
    recorded = {a["parameter"]: a["value"] for a in result["assumptions"]}
    assert recorded["seed"] == inputs[2]["seed"]
    assert recorded["level_to_value.partial"] == inputs[2]["level_to_value"]["partial"]
    assert recorded["rank_to_weight.high"] == inputs[2]["rank_to_weight"]["high"]
    assert all(a["assumption"] is True for a in result["assumptions"])


def test_missing_hard_minimum_uses_flagged_config_default(inputs):
    inputs[1]["requirements"][0].pop("min_level_if_applicable")
    result = run(inputs)
    assert any(a["parameter"] == "default_hard_min_level" and a.get("requirements") == ["H-environment"] for a in result["assumptions"])


@pytest.mark.parametrize("kind", ["claim_id", "requirement_id", "candidate_id", "unknown_scope", "invalid_level", "invalid_role", "empty_domain", "nonstring_qualifier"])
def test_invalid_inputs_are_rejected_without_inventing_a_result(inputs, kind):
    if kind == "claim_id":
        inputs[0]["claims"].append(deepcopy(inputs[0]["claims"][0]))
    elif kind == "requirement_id":
        inputs[1]["requirements"].append(deepcopy(inputs[1]["requirements"][0]))
    elif kind == "candidate_id":
        inputs[1]["candidates"].append(deepcopy(inputs[1]["candidates"][0]))
    elif kind == "unknown_scope":
        inputs[1]["candidates"][0]["scope_id"] = "missing_scope"
    elif kind == "invalid_level":
        inputs[0]["claims"][0]["level"] = "probably"
    elif kind == "invalid_role":
        inputs[1]["requirements"][0]["role"] = "MAYBE"
    elif kind == "empty_domain":
        inputs[1]["requirements"][2]["qualifier_domains"]["storage"] = []
    else:
        inputs[1]["requirements"][0]["qualifiers"]["environment"] = ["aws", "azure"]
    with pytest.raises(ValueError):
        run(inputs)


@pytest.mark.parametrize("kind", ["unmarked_number", "nonmonotone_values", "invalid_seed", "invalid_max_scenarios", "invalid_weight", "invalid_minimum"])
def test_invalid_config_is_rejected(inputs, kind):
    config = inputs[2]
    if kind == "unmarked_number":
        config["parameter_metadata"]["seed"]["assumption"] = False
    elif kind == "nonmonotone_values":
        config["level_to_value"]["none"] = config["level_to_value"]["full"] + 1
    elif kind == "invalid_seed":
        config["seed"] = "random"
    elif kind == "invalid_max_scenarios":
        config["max_scenarios"] = 0
    elif kind == "invalid_weight":
        config["rank_to_weight"]["low"] = -1
    else:
        config["default_hard_min_level"] = "unknown"
    with pytest.raises(ValueError):
        run(inputs)
