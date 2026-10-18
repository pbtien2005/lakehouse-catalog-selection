"""Group 1: current contract hashes plus real Layer 2 normalization, no inference."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "catalog-reasoner-mvp"))
from catalog_reasoner.layer2 import normalize_form
from catalog_reasoner.layer2_io import load_assets


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assets = load_assets(ROOT)
    registry, mapping = assets["registry"], assets["mapping"]
    questions = {q["id"]: q for q in registry["questions"]}
    properties = {p["id"]: p for p in assets["dictionary"]["properties"]}
    anchors_doc = json.loads((ROOT / "layer-2-anchors.json").read_text(encoding="utf-8"))
    anchors = {a["property_id"]: a for a in anchors_doc["anchors"]}
    plan = json.loads((ROOT / "layer-2-property-plan.json").read_text(encoding="utf-8-sig"))
    checks = []

    def check(name, result):
        checks.append({"name": name, "passed": bool(result)})

    check("ten_unique_questions", len(registry["questions"]) == len(questions) == 10)
    check("48_canonical_answers", sum(len(q["answers"]) for q in questions.values()) == 48)
    check("nine_active_questions_streaming_inactive", sum(q["enabled"] for q in questions.values()) == 9 and not questions["I06"]["enabled"])
    check("only_two_feature_ranks", {r["id"] for r in questions["I10"]["ranks"]} == {"mandatory", "nice_to_have"})
    check("mapping_uses_v2_and_canonical_registry", mapping["manifest"]["form_source"] == "input-v2.md" and mapping["manifest"]["registry"] == "form-v2-registry.json")
    check("mapping_questions_exactly_match_registry", {q["id"] for q in mapping["questions"]} == questions.keys())
    check("all_48_answer_rules_covered", all(set(q["answer_effects"]) == {a["id"] for a in questions[q["id"]]["answers"]} for q in mapping["questions"]))
    check("mapping_reads_canonical_answer_refs", all(q["answers_ref"] == f"form-v2-registry.json#/questions/{next(i for i, item in enumerate(registry['questions']) if item['id'] == q['id'])}/answers" for q in mapping["questions"]))
    check("no_legacy_id_in_active_registry", not ({a["id"] for q in questions.values() for a in q["answers"]} & set(registry["legacy_answer_ids"])))
    targets = {p for q in mapping["questions"] for p in q["target_properties"]}
    check("12_targets_and_anchors_exist", len(targets) == len(anchors) == 12 and targets == anchors.keys() and targets <= properties.keys())
    check("anchor_types_and_qualifier_names_match_dictionary", all(a["value_type"] == properties[pid]["value_type"] and set(a["qualifier_bindings"]) == set(properties[pid]["qualifiers"]) for pid, a in anchors.items()))
    check("support_and_quantity_thresholds_match_types", all(a["hard_min_level"] == ("full" if a["value_type"] == "support" else None) for a in anchors.values()))
    check("all_37_property_plan_records_still_exist", len(plan["records"]) == len(properties) == 37 and {r["property_id"] for r in plan["records"]} == properties.keys())
    check("25_indirect_properties_preserved", sum(r["property_id"] not in targets for r in plan["records"]) == 25 and all(r["delete_from_layer1"] is False for r in plan["records"]))
    config = assets["config"]
    check("fact_HARD_flag_enabled", config["default_environment_facts_as_hard"] is True)
    check("nice_to_have_uses_unchanged_config_low", config["nice_to_have_weight_rank"] == "low" and assets["policy"]["weight_policy"]["weight_defaulted"] is True)
    check("all_seven_real_scopes_selected", set(config["candidate_scope_ids"]) == {s["id"] for s in assets["kb"]["scopes"]} and len(config["candidate_scope_ids"]) == 7)
    intervals = list(config["table_count_intervals"].values())
    check("integer_intervals_contiguous", intervals[0]["lower"] == 0 and intervals[-1]["upper"] is None and all(left["upper"] + 1 == right["lower"] for left, right in zip(intervals, intervals[1:])))
    check("candidate_bindings_explicitly_trace_only", mapping["output_contract"]["candidate_bindings_execution"] == "trace_only_deferred" and assets["policy"]["qualifier_policy"]["candidate_bindings_execution"] == "trace_only_deferred" and not anchors_doc["global_rules"]["joint_candidate_path_resolution_required"])

    base = {"form_revision": "input-v2", "answers": {"I01": "aws", "I02": ["spark", "trino"], "I03": "iceberg", "I04": "100_to_999", "I05": "two_to_three", "I07": "table", "I08": "no", "I09": ["none"], "I10": {"none": True, "selected": []}}}
    executed = []
    for question in questions.values():
        for answer in question["answers"]:
            payload = deepcopy(base)
            value = answer["id"]
            if question["control"] == "multi":
                value = [value]
            elif question["control"] == "features":
                value = {"none": True, "selected": []} if value == "none" else {"selected": [{"feature": value, "rank": "nice_to_have"}]}
            payload["answers"][question["id"]] = value
            result = normalize_form(payload, assets)
            check(f"runtime_answer:{question['id']}:{answer['id']}", result["readiness"] == "ready_for_assessment" and result["normalized_context"][question["id"]] == value and set(mapping["output_contract"]["required_sections"]) <= result.keys())
            executed.append({"id": f"SYNTHETIC-L2-{question['id']}-{answer['id']}", "synthetic_profile": True, "input": payload, "readiness": result["readiness"], "requirement_ids": [r["id"] for r in result["requirements"]], "objectives": result["objectives"], "unresolved": result["unresolved"], "layer3_executed": False})
    sample = normalize_form(base, assets)
    rows = sample["requirements"] + sample["objectives"]
    check("emitted_requirements_reference_real_properties_and_qualifiers", all(r["property_id"] in properties and set(r["qualifiers"]) == set(properties[r["property_id"]]["qualifiers"]) for r in rows))
    check("every_emitted_predicate_has_mapping_trace", all(r["id"] in sample["trace"] for r in rows))

    protected = {
        "layer-1-data.json": "043934db4b7babbc008c24f0e4cbad343093109297290df2ac1ca2b324567cb8",
        "layer-1-properties.json": "f94a6f80086eb45ac0909d14f4a33222f019d32873e81c22bff7fc63b5ef6779",
        "layer-2-property-plan.json": "46a8d9070c0fb1fb793466a948322fad3f86442c0441b9d95b31d93e6255b082",
        "../catalog-reasoner-mvp/config.json": "50a010d28a0c9054d044553851a8a743a42d93557911516f9f2aa0e4c0fe6a10",
        "../../sites/catalog-review/dist/styles.css": "31f1ab8bd7849204e15f702a4a681c4159632cd6bf00e0edb7b4441d7c4e1ddc",
    }
    for name, expected in protected.items():
        check("protected_unchanged:" + name, digest(ROOT / name) == expected)
    examples = {"manifest": {"revision": "layer2-examples-group1", "kind": "executed_group1_normalization_cases", "synthetic_profiles": True, "real_candidate_metadata": True, "layer3_executed": False}, "cases": executed}
    (ROOT / "layer-2-examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    artifact_names = ["form-v2-registry.json", "layer-2-runtime-config.json", "layer-2-mapping.json", "layer-2-policy.json", "layer-2-anchors.json", "layer-2-mvp-profile.json", "layer-2-examples.json", "layer-2-design.md", "input-v2.md", "layer-2-checks.py"]
    source_paths = [ROOT.parent / "catalog-reasoner-mvp/catalog_reasoner/layer2.py", ROOT.parent / "catalog-reasoner-mvp/catalog_reasoner/layer2_io.py", ROOT.parent.parent / "sites/catalog-review/dist/core.js", ROOT.parent.parent / "sites/catalog-review/dist/app.js", ROOT.parent.parent / "sites/catalog-review/server.mjs"]
    report = {"scope": "Group 1 contract checks and executed Layer 2 normalization; no Layer 3", "passed": all(c["passed"] for c in checks), "checks": checks, "counts": {"checks": len(checks), "canonical_questions": len(questions), "canonical_answers": len(executed), "real_candidates": len(sample["candidates"]), "properties_preserved": len(plan["records"]), "indirect_properties_preserved": len(properties.keys() - targets)}, "runtime_mapping_executed": True, "product_capabilities_validated": False, "layer3_executed": False, "artifact_sha256": {name: digest(ROOT / name) for name in artifact_names}, "source_sha256": {path.relative_to(ROOT.parent.parent).as_posix(): digest(path) for path in source_paths}, "protected_file_sha256": {name: digest(ROOT / name) for name in protected}, "limitations": sample["assessment_limits"]}
    (ROOT / "layer-2-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "counts": report["counts"], "failed": [c["name"] for c in checks if not c["passed"]]}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
