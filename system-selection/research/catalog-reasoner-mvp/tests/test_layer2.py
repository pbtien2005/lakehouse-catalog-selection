"""Group 1: actual form-v2 normalization, no KB lookup or Layer 3 execution."""

from copy import deepcopy
import importlib
import json
from pathlib import Path

import pytest


BASE = {"form_revision": "input-v2", "answers": {
    "I01": "aws", "I02": ["spark", "trino"], "I03": "iceberg",
    "I04": "100_to_999", "I05": "two_to_three", "I07": "table",
    "I08": "no", "I09": ["none"], "I10": {"none": True, "selected": []},
}}


def runtime(payload=None, assets=None):
    module = importlib.import_module("catalog_reasoner.layer2")
    if assets is None:
        assets = importlib.import_module("catalog_reasoner.layer2_io").load_assets()
    return module.normalize_form(deepcopy(BASE if payload is None else payload), assets)


def module_assets():
    return importlib.import_module("catalog_reasoner.layer2_io").load_assets()


def test_registry_mapping_cover_exactly_48_choices_and_no_legacy_keys():
    assets = module_assets()
    registry, mapping = assets["registry"], assets["mapping"]
    assert len(registry["questions"]) == 10
    assert sum(len(q["answers"]) for q in registry["questions"]) == 48
    for q in registry["questions"]:
        rule = next(r for r in mapping["questions"] if r["id"] == q["id"])
        assert set(rule["answer_effects"]) == {a["id"] for a in q["answers"]}
    assert mapping["manifest"]["form_source"] == "input-v2.md"


def test_mapping_answer_references_resolve_to_the_canonical_registry():
    assets = module_assets()
    for rule in assets["mapping"]["questions"]:
        filename, pointer = rule["answers_ref"].split("#", 1)
        assert filename == "form-v2-registry.json"
        resolved = assets["registry"]
        for part in pointer.removeprefix("/").split("/"):
            resolved = resolved[int(part)] if isinstance(resolved, list) else resolved[part]
        question = next(q for q in assets["registry"]["questions"] if q["id"] == rule["id"])
        assert resolved is question["answers"]


@pytest.mark.parametrize("defect", ["missing_question", "duplicate_question", "invalid_reference", "wrong_question_reference", "answer_drift"])
def test_asset_loader_rejects_registry_mapping_contract_drift(tmp_path, defect):
    assets = module_assets()
    mapping = deepcopy(assets["mapping"])
    if defect == "missing_question":
        mapping["questions"].pop()
    elif defect == "duplicate_question":
        mapping["questions"].append(deepcopy(mapping["questions"][0]))
    elif defect == "invalid_reference":
        mapping["questions"][0]["answers_ref"] = "form-v2-registry.json#/questions/I01/answers"
    elif defect == "wrong_question_reference":
        mapping["questions"][0]["answers_ref"] = "form-v2-registry.json#/questions/1/answers"
    else:
        mapping["questions"][0]["answer_effects"]["new_answer"] = "NO_REQUIREMENT"
    names = {"registry": "form-v2-registry.json", "mapping": "layer-2-mapping.json", "profile": "layer-2-mvp-profile.json", "config": "layer-2-runtime-config.json", "policy": "layer-2-policy.json", "dictionary": "layer-1-properties.json", "kb": "layer-1-data.json"}
    assets["mapping"] = mapping
    assets["config"]["reasoning_config_source"] = "reasoning-config.json"
    for key, filename in names.items():
        (tmp_path / filename).write_text(json.dumps(assets[key]), encoding="utf-8")
    (tmp_path / "reasoning-config.json").write_text(json.dumps(assets["reasoning_config"]), encoding="utf-8")
    with pytest.raises(ValueError, match="Registry/mapping"):
        importlib.import_module("catalog_reasoner.layer2_io").load_assets(tmp_path)


def test_known_environment_engines_formats_are_hard_without_extra_confirmation():
    result = runtime()
    assert result["readiness"] == "ready_for_assessment"
    rows = result["requirements"]
    assert {r["property_id"] for r in rows} >= {"deployment.environment", "integration.engine_operation", "catalog.format_operation", "limits.quota", "commit.concurrent_write", "security.authorization"}
    assert all(r["role"] == "HARD" for r in rows)
    assert {r["source_inputs"][0] for r in rows if r["property_id"] == "integration.engine_operation"} == {"I02"}
    assert any("đã coi lựa chọn này là bắt buộc" in r["message"] for r in result["reminders"])
    assert len(result["candidates"]) == 7
    assert all(not c["id"].startswith("synthetic") for c in result["candidates"])


def test_capacity_requirement_keeps_quantity_type_without_support_threshold():
    quota = next(r for r in runtime()["requirements"] if r["property_id"] == "limits.quota")
    assert quota["min_level_if_applicable"] is None
    assert quota["demand_interval"] == module_assets()["config"]["table_count_intervals"]["100_to_999"]
    assert quota["operator"] == "capacity_covers_demand_interval"


def test_fact_hard_flag_can_be_disabled_without_turning_into_soft():
    assets = module_assets()
    assets["config"]["default_environment_facts_as_hard"] = False
    result = runtime(assets=assets)
    assert not any(set(r["source_inputs"]) & {"I01", "I02", "I03"} for r in result["requirements"])
    assert not result["objectives"]
    assert result["normalized_context"]["I01"] == "aws"


@pytest.mark.parametrize("question,value", [("I01", "multi_cloud"), ("I02", ["other"]), ("I03", "mixed"), ("I03", "not_chosen")])
def test_unspecific_answers_stay_unresolved_not_hard(question, value):
    payload = deepcopy(BASE)
    payload["answers"][question] = value
    result = runtime(payload)
    assert any(u["source_input"] == question for u in result["unresolved"])
    assert not any(r["source_inputs"] == [question] for r in result["requirements"])


def test_nice_to_have_uses_config_low_weight_and_defaulted_flag():
    payload = deepcopy(BASE)
    payload["answers"]["I10"] = {"selected": [{"feature": "branching", "rank": "mandatory"}, {"feature": "metadata_federation", "rank": "nice_to_have"}]}
    result = runtime(payload)
    soft = result["objectives"][0]
    assert soft["weight"] == module_assets()["reasoning_config"]["rank_to_weight"]["low"]
    assert soft["weight_defaulted"] is True
    assert soft["weight_rank"] == "low"
    assert any(r["property_id"] == "workflow.branching" and r["role"] == "HARD" for r in result["requirements"])
    assert any(a["parameter"] == "rank_to_weight.low" and a["value"] == soft["weight"] for a in result["assumptions"])


@pytest.mark.parametrize("question,value,code", [
    ("I02", ["trino_presto"], "E_LEGACY_FORM_ANSWER"),
    ("I02", ["starrocks_doris"], "E_LEGACY_FORM_ANSWER"),
    ("I04", "100_to_1000", "E_LEGACY_FORM_ANSWER"),
    ("I07", "column_row", "E_LEGACY_FORM_ANSWER"),
    ("I09", ["none", "databricks"], "E_EXCLUSIVE_NONE"),
    ("I10", {"none": True, "selected": [{"feature": "branching", "rank": "mandatory"}]}, "E_EXCLUSIVE_NONE"),
    ("I10", {"selected": [{"feature": "branching"}]}, "E_RANK_MISSING_OR_INVALID"),
    ("I10", {"selected": [{"feature": "branching", "rank": "important"}]}, "E_RANK_MISSING_OR_INVALID"),
    ("I01", ["aws", "azure"], "E_CARDINALITY"),
    ("I01", "planet_x", "E_INVALID_ANSWER"),
])
def test_invalid_inputs_keep_raw_answers_and_field_specific_errors(question, value, code):
    payload = deepcopy(BASE)
    payload["answers"][question] = value
    result = runtime(payload)
    assert result["readiness"] == "needs_input_correction"
    assert any(e["code"] == code and e["field"].startswith(f"answers.{question}") for e in result["input_issues"])
    assert result["raw_answers"][question] == value
    if question == "I02":
        assert not any(r["source_inputs"] == ["I02"] for r in result["requirements"])


def test_unknown_is_distinct_from_explicit_no_and_inactive_streaming():
    unknown = deepcopy(BASE)
    unknown["answers"].update(I08="unknown", I07="unclear", I06="yes")
    result = runtime(unknown)
    assert {u["source_input"] for u in result["unresolved"]} >= {"I07", "I08"}
    assert not any(r["property_id"] == "integration.streaming_write" for r in result["requirements"])
    assert not any(u["source_input"] == "I08" for u in runtime()["unresolved"])


def test_missing_answers_are_unresolved_not_fabricated_defaults():
    result = runtime({"form_revision": "input-v2", "answers": {}})
    assert not result["requirements"]
    assert not result["objectives"]
    assert any(u["source_input"] == "I01" and u["state"] == "unanswered" for u in result["unresolved"])


def test_payload_extra_fields_and_wrong_revision_are_reported():
    payload = deepcopy(BASE)
    payload["form_revision"] = "input-v1"
    payload["answers"]["operations"] = "important"
    result = runtime(payload)
    assert result["readiness"] == "needs_input_correction"
    assert {e["field"] for e in result["input_issues"]} >= {"form_revision", "answers.operations"}


def test_output_is_pure_deterministic_and_every_predicate_has_trace():
    assets = module_assets()
    before = deepcopy(assets)
    first = runtime(assets=assets)
    assert runtime(assets=assets) == first
    assert assets == before
    for row in first["requirements"]:
        assert row["id"] in first["trace"]
        assert first["trace"][row["id"]]["source_inputs"] == row["source_inputs"]
    assert first["assessment_limits"]["candidate_bindings_execution"] == "trace_only_deferred"


REGISTRY = json.loads((Path(__file__).resolve().parents[2] / "catalog-knowledge-base/form-v2-registry.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("qid,answer", [(q["id"], a["id"]) for q in REGISTRY["questions"] for a in q["answers"]])
def test_every_canonical_answer_executes_a_normalization_rule(qid, answer):
    question = next(q for q in REGISTRY["questions"] if q["id"] == qid)
    payload = deepcopy(BASE)
    if question["control"] == "multi":
        value = [answer]
    elif question["control"] == "features":
        value = {"none": True, "selected": []} if answer == "none" else {"selected": [{"feature": answer, "rank": "nice_to_have"}]}
    else:
        value = answer
    payload["answers"][qid] = value
    result = runtime(payload)
    assert result["readiness"] == "ready_for_assessment"
    assert result["normalized_context"][qid] == value
    assert len(result["candidates"]) == 7
    rule = next(q for q in module_assets()["mapping"]["questions"] if q["id"] == qid)
    effect = rule["answer_effects"][answer]
    direct = [r for r in result["requirements"] if r["source_inputs"] == [qid]]
    if effect.startswith("HARD"):
        assert direct
    elif effect in {"NO_REQUIREMENT", "unresolved_not_HARD", "inactive_trace_only", "optional_context_and_reminder", "context_not_proof_of_no_concurrency"}:
        assert not direct
    elif effect.startswith("mandatory_HARD_or"):
        assert any(r["source_inputs"] == [qid] and r["weight_defaulted"] for r in result["objectives"])


@pytest.mark.parametrize("payload", [
    None,
    {"form_revision": "input-v2", "answers": []},
    {"form_revision": "input-v2", "answers": {"I10": []}},
    {"form_revision": "input-v2", "answers": {"I10": {"selected": ["bad"]}}},
    {"form_revision": "input-v2", "answers": {"I10": {"selected": [{"feature": "branching", "rank": []}]}}},
    {"form_revision": "input-v2", "answers": {"I02": ["spark", "spark"]}},
    {"form_revision": "input-v2", "answers": {"I10": {"none": "yes", "selected": []}}},
])
def test_malformed_json_shapes_return_input_issues(payload):
    assets = module_assets()
    module = importlib.import_module("catalog_reasoner.layer2")
    result = module.normalize_form(payload, assets)
    assert result["readiness"] == "needs_input_correction"
    assert result["input_issues"]


def test_layer2_cli_produces_normalization_only(tmp_path, capsys):
    cli = importlib.import_module("catalog_reasoner.layer2_io")
    source = tmp_path / "answers.json"
    target = tmp_path / "nested/out.json"
    source.write_text(json.dumps(BASE), encoding="utf-8")
    assert cli.main(["--answers", str(source), "--output", str(target)]) == 0
    result = json.loads(target.read_text(encoding="utf-8"))
    assert result["assessment_limits"]["layer3_executed"] is False
    assert cli.main(["--answers", str(source)]) == 0
    assert json.loads(capsys.readouterr().out)["readiness"] == "ready_for_assessment"
    source.write_text("not json", encoding="utf-8")
    assert cli.main(["--answers", str(source)]) == 2
    assert "error" in json.loads(capsys.readouterr().out)


@pytest.mark.parametrize("key,value", [("default_environment_facts_as_hard", 1), ("weight", 0)])
def test_invalid_runtime_config_is_an_error_not_a_different_decision(key, value):
    assets = module_assets()
    if key == "weight":
        assets["reasoning_config"]["rank_to_weight"]["low"] = value
    else:
        assets["config"][key] = value
    with pytest.raises(ValueError):
        runtime(assets=assets)
