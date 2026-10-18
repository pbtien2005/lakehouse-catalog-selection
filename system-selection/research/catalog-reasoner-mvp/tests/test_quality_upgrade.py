"""Quality-upgrade boundary and quantity regressions, independent synthetic data."""
from copy import deepcopy

import pytest

from catalog_reasoner.application import run_case, run_requirements
from catalog_reasoner.project_io import load_kb, load_project_config


def quantity_case(claims, lower, upper):
    config = load_project_config()
    kb = {"manifest": {"synthetic": True}, "scopes": [{"id": "synthetic_capacity"}], "claims": []}
    for index, (kind, amount) in enumerate(claims):
        kb["claims"].append({"id": f"synthetic_capacity_{index}", "scope_id": "synthetic_capacity", "property_id": "limits.quota", "qualifiers": {"resource": "tables", "boundary": "catalog"}, "value": {"amount": amount, "unit": "tables"}, "observation_context": {"limit_kind": kind}})
    doc = {"candidates": [{"id": "synthetic_capacity", "scope_id": "synthetic_capacity"}], "requirements": [{"id": "H-capacity", "property_id": "limits.quota", "qualifiers": {"resource": "tables", "boundary": "catalog"}, "role": "HARD", "operator": "capacity_covers_demand_interval", "demand_interval": {"lower": lower, "upper": upper}, "boundary_confirmed": True}], "objectives": []}
    return kb, doc, config


def test_documented_minimum_can_prove_a_smaller_exact_demand():
    result = run_requirements(*quantity_case([("demonstrated_minimum", 5)], 5, 5))
    assert result["groups"]["eligible"]


@pytest.mark.parametrize("demand", [(0, 99), (6, 6), (1, None)])
def test_demonstrated_minimum_is_not_an_invented_maximum_or_unlimited_capacity(demand):
    result = run_requirements(*quantity_case([("demonstrated_minimum", 5)], *demand))
    assert result["groups"]["conditional"] and not result["groups"]["excluded"]


def test_conflicting_fixed_and_demonstrated_capacity_stays_unknown():
    result = run_requirements(*quantity_case([("fixed", 2), ("demonstrated_minimum", 5)], 3, 3))
    assert result["groups"]["conditional"]


def test_v3_missing_storage_is_not_inferred_from_aws():
    payload = {"form_revision": "input-v3", "answers": {"I01": "aws", "I02": ["spark"], "I03": "iceberg", "I04": "lt_100", "I05": "one", "I07": "column_and_row", "I08": "yes", "I09": ["aws_native"], "I10": {"none": True, "selected": []}, "I12": {"spark": ["read"]}}}
    result = run_case(payload, load_kb(), load_project_config())
    assert result["status"] == "ok"
    assert any(row["source_input"] in ["I08", "I11"] for row in result["unresolved_inputs"])
    assert not result["groups"]["eligible"]


def test_v3_valid_read_append_has_both_operation_requirements_and_preserves_input():
    payload = {"form_revision": "input-v3", "answers": {"I01": "local_lab", "I02": ["spark"], "I03": "iceberg", "I04": "lt_100", "I05": "one", "I07": "none", "I08": "no", "I09": ["none"], "I10": {"none": False, "selected": [{"feature": "branching", "rank": "mandatory"}]}, "I11": "local_fs", "I12": {"spark": ["read", "append"]}}, "context": {"table_count_exact": 1}}
    original = deepcopy(payload)
    result = run_case(payload, load_kb(), load_project_config())
    assert result["status"] == "ok" and payload == original
    assert {row["qualifiers"]["operation"] for row in result["requirements"]["requirements"] if row["property_id"] == "integration.engine_operation"} == {"read", "append"}
    assert result["requirements"]["raw_answers"] == payload["answers"]
    assert result.get("knowledge_extensions")


def test_v2_is_not_silently_migrated_or_given_a_storage_assumption():
    result = run_case({"form_revision": "input-v2", "answers": {"I01": "aws", "I08": "yes"}}, load_kb(), load_project_config())
    assert result["status"] == "ok"
    assert result["requirements"]["revisions"]["form"] == "input-v2"
    assert any(row["state"] == "unknown_storage" for row in result["unresolved_inputs"])


def test_v3_does_not_rank_unverified_mixes_of_unknown_implementation_paths():
    payload = {"form_revision": "input-v3", "answers": {"I01": "local_lab", "I02": ["spark"], "I03": "iceberg", "I04": "lt_100", "I05": "one", "I07": "none", "I08": "no", "I09": ["none"], "I10": {"none": False, "selected": [{"feature": "branching", "rank": "nice_to_have"}]}, "I11": "local_fs", "I12": {"spark": ["read", "append"]}}, "context": {"table_count_exact": 1}}
    result = run_case(payload, load_kb(), load_project_config())
    unverified = [c for rows in result['groups'].values() for c in rows if not c.get('selected_profile_id')]
    assert unverified and all(c.get('top_rate') is None and c.get('feasible_rate') is None for c in unverified)
    assert result['scenarios']['comparison_scope'] == 'evidenced_joint_profiles_with_resolved_user_context'
    assert result['scenarios']['status'] == 'insufficient_verified_implementations_for_comparison'
    nessie = next(c for c in result['groups']['eligible'] if c['candidate_id']=='project_nessie')
    assert nessie['score_interval']==[1,1] and nessie['top_rate'] is None
