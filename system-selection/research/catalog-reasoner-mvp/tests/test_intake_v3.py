"""Architect-facing storage/operation intake, without implicit API choices."""
from copy import deepcopy
import importlib
import json
from pathlib import Path

import pytest

from catalog_reasoner.layer2_io import load_assets


BASE = {"form_revision": "input-v3", "answers": {
    "I01": "aws", "I02": ["spark"], "I03": "iceberg", "I04": "lt_100",
    "I05": "one", "I07": "none", "I08": "yes", "I09": ["none"],
    "I10": {"none": True, "selected": []}, "I11": "s3",
    "I12": {"spark": ["read", "append", "create_table"]},
}, "context": {"table_count_exact": 7}}


_DEFAULT = object()


def normalize(payload=_DEFAULT, assets=None):
    fn = importlib.import_module("catalog_reasoner.intake_v3").normalize_form_v3
    return fn(deepcopy(BASE if payload is _DEFAULT else payload), load_assets() if assets is None else assets)


def test_v3_records_storage_operations_and_exact_demand_with_trace():
    doc = normalize()
    assert doc["readiness"] == "ready_for_assessment"
    assert doc["revisions"]["form"] == "input-v3"
    engine = [r for r in doc["requirements"] if r["property_id"] == "integration.engine_operation"]
    assert {r["qualifiers"]["operation"] for r in engine} == {"read", "append", "create_table"}
    assert all(r["source_inputs"] == ["I02", "I12"] for r in engine)
    vending = next(r for r in doc["requirements"] if r["property_id"] == "storage.credential_vending")
    assert vending["qualifiers"]["storage"] == "s3" and vending["status"] == "ready"
    quota = next(r for r in doc["requirements"] if r["property_id"] == "limits.quota")
    assert quota["demand_interval"] == {"lower": 7, "upper": 7}
    assert quota["role"] == "HARD"
    assert not any(u["state"] == "unknown_storage" for u in doc["unresolved"])
    assert all(doc["trace"][r["id"]]["source_inputs"] == r["source_inputs"] for r in doc["requirements"])


def test_local_lab_remains_distinct_from_production_on_prem():
    payload = deepcopy(BASE); payload["answers"]["I01"] = "local_lab"
    doc = normalize(payload)
    environment = next(r for r in doc["requirements"] if r["property_id"] == "deployment.environment")
    assert environment["qualifiers"] == {"environment": "local_lab"}
    assert not any(u["source_input"] == "I01" for u in doc["unresolved"])


@pytest.mark.parametrize("storage", [None, "unknown"])
def test_storage_is_never_inferred_from_cloud(storage):
    payload = deepcopy(BASE)
    if storage is None: payload["answers"].pop("I11")
    else: payload["answers"]["I11"] = storage
    doc = normalize(payload)
    vending = next(r for r in doc["requirements"] if r["property_id"] == "storage.credential_vending")
    assert vending["status"] == "needs_context" and vending["qualifiers"]["storage"] is None
    assert any(u["state"] == "unknown_storage" for u in doc["unresolved"])


@pytest.mark.parametrize("operations", [None, {}, {"spark": ["unknown"]}])
def test_missing_operations_remain_unresolved_without_read_default(operations):
    payload = deepcopy(BASE)
    if operations is None: payload["answers"].pop("I12")
    else: payload["answers"]["I12"] = operations
    doc = normalize(payload)
    assert not any(r["property_id"] == "integration.engine_operation" for r in doc["requirements"])
    assert any(u["source_input"] == "I12" and u.get("engine") == "spark" for u in doc["unresolved"])


def test_operations_are_bound_per_engine_not_cross_product():
    payload = deepcopy(BASE)
    payload["answers"].update(I02=["spark", "trino"], I12={"spark": ["append"], "trino": ["read"]})
    rows = [r["qualifiers"] for r in normalize(payload)["requirements"] if r["property_id"] == "integration.engine_operation"]
    assert {(r["engine"], r["operation"]) for r in rows} == {("spark", "append"), ("trino", "read")}


@pytest.mark.parametrize("value,field", [
    (0, "context.table_count_exact"), (-1, "context.table_count_exact"), (True, "context.table_count_exact"),
    (7.5, "context.table_count_exact"), (100, "context.table_count_exact"), ("7", "context.table_count_exact"),
])
def test_invalid_or_out_of_bucket_exact_count_is_rejected(value, field):
    payload = deepcopy(BASE); payload["context"]["table_count_exact"] = value
    doc = normalize(payload)
    assert doc["readiness"] == "needs_input_correction"
    assert any(i["field"] == field for i in doc["input_issues"])


@pytest.mark.parametrize("patch,field", [
    ({"I11": "S3"}, "answers.I11"),
    ({"I12": []}, "answers.I12"),
    ({"I12": {"spark": ["read", "unknown"]}}, "answers.I12.spark"),
    ({"I12": {"spark": ["read", "read"]}}, "answers.I12.spark"),
    ({"I12": {"trino": ["read"]}}, "answers.I12.trino"),
    ({"I12": {"spark": ["drop_database"]}}, "answers.I12.spark"),
    ({"I12": {"spark": "read"}}, "answers.I12.spark"),
])
def test_invalid_v3_answers_have_field_specific_errors(patch, field):
    payload = deepcopy(BASE); payload["answers"].update(patch)
    doc = normalize(payload)
    assert doc["readiness"] == "needs_input_correction"
    assert any(i["field"] == field for i in doc["input_issues"])


def test_absent_exact_count_preserves_original_hard_bucket():
    payload = deepcopy(BASE); payload.pop("context")
    quota = next(r for r in normalize(payload)["requirements"] if r["property_id"] == "limits.quota")
    assert quota["demand_interval"] == {"lower": 0, "upper": 99}
    assert quota["role"] == "HARD"


def test_v3_normalization_is_pure_and_deterministic():
    assets, payload = load_assets(), deepcopy(BASE)
    before = deepcopy((assets, payload))
    assert normalize(payload, assets) == normalize(payload, assets)
    assert (assets, payload) == before


def test_existing_v2_normalizer_contract_remains_unchanged():
    from catalog_reasoner.layer2 import normalize_form
    payload = {"form_revision": "input-v2", "answers": {"I01": "aws", "I02": ["spark"], "I03": "iceberg"}}
    doc = normalize_form(payload, load_assets())
    assert any(r["qualifiers"].get("operation") == "read" for r in doc["requirements"])
    assert doc["revisions"]["form"] == "input-v2"


@pytest.mark.parametrize("payload", [None, [], {"form_revision": "input-v3", "answers": []},
    {"form_revision": "input-v2", "answers": {}},
    {"form_revision": "input-v3", "answers": {}, "context": []},
    {"form_revision": "input-v3", "answers": {}, "context": {"secret": 5}},
    {"form_revision": "input-v3", "answers": {}, "secret": 5},
    {"form_revision": "input-v3", "answers": {"I03": ["iceberg"]}},
    {"form_revision": "input-v3", "answers": {"I02": {"spark": True}}}])
def test_malformed_payload_returns_input_issues(payload):
    assert normalize(payload)["readiness"] == "needs_input_correction"


def test_registry_and_normalizer_use_same_storage_and_operation_domains():
    module = importlib.import_module("catalog_reasoner.intake_v3")
    path = Path(__file__).resolve().parents[2] / "catalog-knowledge-base/form-v3-registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    questions = {q["id"]: q for q in registry["questions"]}
    assert {a["id"] for a in questions["I11"]["answers"]} == set(module.STORAGE_VALUES)
    assert {a["id"] for a in questions["I12"]["answers"]} == set(module.OPERATION_VALUES)
    assert "local_lab" in {a["id"] for a in questions["I01"]["answers"]}
