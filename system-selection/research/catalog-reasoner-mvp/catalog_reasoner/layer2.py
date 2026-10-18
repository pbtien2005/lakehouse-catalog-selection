"""Group 1: pure form-v2 -> requirements. No KB inference or value aliases."""

from copy import deepcopy
from math import isfinite


def normalize_form(payload, assets):
    registry, mapping = assets["registry"], assets["mapping"]
    config, profile = assets["config"], assets["profile"]["defaults"]
    flag = config["default_environment_facts_as_hard"]
    if type(flag) is not bool:
        raise ValueError("config.default_environment_facts_as_hard must be boolean")
    rank = config["nice_to_have_weight_rank"]
    weight = assets["reasoning_config"]["rank_to_weight"][rank]
    if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not isfinite(weight) or weight <= 0:
        raise ValueError("reasoning_config.rank_to_weight low weight must be finite and positive")
    questions = {q["id"]: q for q in registry["questions"]}
    property_types = {p["id"]: p["value_type"] for p in assets["dictionary"]["properties"]}
    raw = payload.get("answers", {}) if isinstance(payload, dict) else {}
    out = {
        "revisions": {"form": registry["manifest"]["form_revision"], "registry": registry["manifest"]["revision"], "mapping": mapping["manifest"]["revision"], "policy": assets["policy"]["manifest"]["revision"], "profile": assets["profile"]["manifest"]["revision"], "config": config["manifest"]["revision"], "property_dictionary": assets["dictionary"]["manifest"]["revision"], "kb": assets["kb"]["manifest"]["revision"]},
        "raw_answers": deepcopy(raw), "normalized_context": {}, "candidates": [],
        "requirements": [], "objectives": [], "unresolved": [], "input_issues": [],
        "reminders": [], "trace": {},
        "assumptions": [{"parameter": "default_environment_facts_as_hard", "value": flag, "assumption": True}, {"parameter": "hard_min_level", "value": config["hard_min_level"], "assumption": True}],
        "profile_assumptions": deepcopy(profile),
        "assessment_limits": {"candidate_bindings_execution": "trace_only_deferred", "joint_path_resolution": "not_implemented_in_MVP", "domain_translation": "not_performed_group_2_pending", "layer3_executed": False},
    }

    def issue(code, field, message):
        out["input_issues"].append({"code": code, "field": field, "message": message})

    def unresolved(qid, state, reason):
        out["unresolved"].append({"source_input": qid, "state": state, "reason": reason})

    if not isinstance(payload, dict):
        issue("E_PAYLOAD", "$", "Payload phải là object có form_revision và answers.")
    else:
        if payload.get("form_revision") != registry["manifest"]["form_revision"]:
            issue("E_FORM_REVISION", "form_revision", "Dùng form_revision=input-v2; không tự chuyển dữ liệu v1.")
        for key in sorted(set(payload) - {"form_revision", "answers"}):
            issue("E_UNKNOWN_FIELD", key, "Trường ngoài hợp đồng form v2.")
    if not isinstance(raw, dict):
        issue("E_PAYLOAD", "answers", "answers phải là object theo ID câu hỏi.")
        raw = {}
    for key in sorted(set(raw) - set(questions)):
        issue("E_UNKNOWN_FIELD", f"answers.{key}", "Bỏ trường ngoài registry form v2.")

    valid = {}
    for qid, question in questions.items():
        value = raw.get(qid)
        if value is None:
            if question["enabled"] and not question["optional"]:
                unresolved(qid, "unanswered", "Chưa có câu trả lời; không tự đặt mặc định.")
            continue
        answer_ids = {a["id"] for a in question["answers"]}
        before = len(out["input_issues"])

        def check_answer(answer, field):
            if isinstance(answer, str) and answer in registry["legacy_answer_ids"]:
                issue("E_LEGACY_FORM_ANSWER", field, "Đáp án cũ cần chọn lại; không tự tách nhóm hoặc chuyển khoảng.")
                unresolved(qid, "legacy_unresolved", "Giữ đáp án cũ để sửa; không tạo HARD từ nhóm chưa tách.")
            elif not isinstance(answer, str) or answer not in answer_ids:
                issue("E_INVALID_ANSWER", field, "Chọn ID đáp án có trong registry form v2.")

        control = question["control"]
        if control == "single":
            if isinstance(value, (list, dict)):
                issue("E_CARDINALITY", f"answers.{qid}", "Câu này chỉ chọn một đáp án.")
            else:
                check_answer(value, f"answers.{qid}")
        elif control == "multi":
            if not isinstance(value, list):
                issue("E_CARDINALITY", f"answers.{qid}", "Câu này cần danh sách ID đáp án.")
            else:
                for index, answer in enumerate(value):
                    check_answer(answer, f"answers.{qid}[{index}]")
                if all(isinstance(x, str) for x in value) and len(value) != len(set(value)):
                    issue("E_DUPLICATE_SELECTION", f"answers.{qid}", "Mỗi đáp án chỉ chọn một lần.")
                if question.get("exclusive_answer") in value and len(value) > 1:
                    issue("E_EXCLUSIVE_NONE", f"answers.{qid}", "Chọn Không hoặc các nền tảng cụ thể; không chọn đồng thời.")
                if not value and not question["optional"]:
                    issue("E_CARDINALITY", f"answers.{qid}", "Chọn ít nhất một engine.")
        else:
            if not isinstance(value, dict) or not isinstance(value.get("selected", []), list):
                issue("E_CARDINALITY", f"answers.{qid}", "Dùng object gồm none và selected.")
            else:
                if set(value) - {"none", "selected"} or type(value.get("none", False)) is not bool:
                    issue("E_INVALID_ANSWER", f"answers.{qid}", "none phải là boolean; chỉ nhận none và selected.")
                selected = value.get("selected", [])
                if value.get("none") and selected:
                    issue("E_EXCLUSIVE_NONE", f"answers.{qid}", "Không có nhu cầu nào không được chọn cùng nhu cầu cụ thể.")
                seen = set()
                for index, item in enumerate(selected):
                    field = f"answers.{qid}.selected[{index}]"
                    if not isinstance(item, dict):
                        issue("E_INVALID_ANSWER", field, "Mỗi mục cần feature và rank.")
                        continue
                    feature = item.get("feature")
                    check_answer(feature, field + ".feature")
                    if feature == "none" or set(item) - {"feature", "rank"}:
                        issue("E_INVALID_ANSWER", field, "none là cờ riêng, không phải nhu cầu có rank.")
                    if isinstance(feature, str) and feature in seen:
                        issue("E_DUPLICATE_SELECTION", field + ".feature", "Mỗi nhu cầu chỉ chọn một lần.")
                    if isinstance(feature, str):
                        seen.add(feature)
                    if not isinstance(item.get("rank"), str) or item["rank"] not in {r["id"] for r in question["ranks"]}:
                        issue("E_RANK_MISSING_OR_INVALID", field + ".rank", "Chọn mandatory hoặc nice_to_have cho nhu cầu đã chọn.")
        if len(out["input_issues"]) == before:
            out["normalized_context"][qid] = deepcopy(value)
            if question["enabled"]:
                valid[qid] = value
            else:
                out["reminders"].append({"source_input": qid, "message": "I06 chưa bật; đáp án chỉ được giữ trong trace."})

    scopes = {s["id"]: s for s in assets["kb"]["scopes"]}
    for sid in config["candidate_scope_ids"]:
        if sid not in scopes:
            raise ValueError(f"Configured candidate scope not in KB: {sid}")
        scope = scopes[sid]
        out["candidates"].append({"id": scope["catalog_id"], "scope_id": sid, "name": scope["name"]})

    def add(qid, suffix, property_id, qualifiers, *, role="HARD", status="ready", bindings=None, extra=None):
        rid = f"R-{qid}-{suffix}"
        minimum = config["hard_min_level"] if role == "HARD" and property_types[property_id] == "support" else None
        row = {"id": rid, "logical_need_id": f"N-{qid}-{suffix}" if qid == "I10" else f"N-{qid}", "source_inputs": [qid], "property_id": property_id, "role": role, "status": status, "qualifiers": qualifiers, "candidate_bindings": bindings or {}, "acceptance_anchor": property_id, "min_level_if_applicable": minimum, "binding_sources": {"form": [qid], "profile": assets["profile"]["manifest"]["revision"], "candidate_bindings": "trace_only_deferred"}}
        if extra:
            row.update(extra)
        if role == "SOFT":
            row.update(weight=weight, weight_rank=rank, weight_defaulted=True)
            out["objectives"].append(row)
        else:
            out["requirements"].append(row)
        out["trace"][rid] = {"source_inputs": [qid], "mapping_rule": qid, "property_id": property_id, "raw_answer": deepcopy(raw[qid]), "candidate_bindings_execution": "trace_only_deferred"}

    def deferred(key, path):
        return {key: {"source": "candidate_path", "path": path, "execution": "trace_only_deferred"}}

    env = valid.get("I01")
    engines = [e for e in valid.get("I02", []) if e != "other"]
    fmt = valid.get("I03") if valid.get("I03") in {"iceberg", "delta", "hudi"} else None
    if env == "multi_cloud":
        unresolved("I01", "unknown_set", "Đa cloud chưa chỉ rõ tập cloud; không tạo HARD.")
    elif env and flag:
        add("I01", "environment", "deployment.environment", {"environment": env})
    if "other" in valid.get("I02", []):
        unresolved("I02", "unknown_identity", "Khác chưa có danh tính engine; không tạo HARD từ mục Khác.")
    if flag:
        for engine in engines:
            add("I02", engine + "-read", "integration.engine_operation", {"engine": engine, "format": fmt, "operation": profile["engine_operation"], "api": None}, status="ready" if fmt else "needs_context", bindings=deferred("api", engine + "_read_path.api"))
        if fmt:
            for operation in profile["catalog_operations"]:
                add("I03", "format-" + operation, "catalog.format_operation", {"format": fmt, "operation": operation, "api": None}, bindings=deferred("api", "metadata_path.api"))
    if valid.get("I03") in {"mixed", "not_chosen"}:
        unresolved("I03", "not_decided" if valid["I03"] == "not_chosen" else "unknown_set", "Chưa có format cụ thể; không tạo HARD từ đáp án tổng hợp.")
    for qid in ["I01", "I02", "I03"]:
        if any(r["source_inputs"] == [qid] for r in out["requirements"]):
            out["reminders"].append({"source_input": qid, "message": "đã coi lựa chọn này là bắt buộc", "config_parameter": "default_environment_facts_as_hard"})
    if "I04" in valid:
        interval = deepcopy(config["table_count_intervals"][valid["I04"]])
        add("I04", "capacity", "limits.quota", {"resource": "tables", "boundary": profile["table_count_boundary"]}, extra={"operator": "capacity_covers_demand_interval", "demand_interval": interval, "boundary_confirmed": True})
        out["assumptions"].append({"parameter": "table_count_intervals." + valid["I04"], "value": interval, "assumption": True})
    if valid.get("I05") in {"two_to_three", "more_than_three"}:
        add("I05", "concurrency", "commit.concurrent_write", {"operation": profile["concurrent_operation"], "writer_topology": profile["concurrent_topology"], "api": None}, bindings=deferred("api", "commit_path.api"))
    permission = valid.get("I07")
    if permission == "unclear":
        unresolved("I07", "unknown_need", "Chưa rõ mức phân quyền; không coi là Không cần.")
    elif permission and permission != "none":
        granularities = ["column", "row"] if permission == "column_and_row" else [permission]
        for granularity in granularities:
            for engine in engines or ["unresolved_engine"]:
                add("I07", granularity + "-" + engine, "security.authorization", {"granularity": granularity, "action": profile["authorization_action"], "access_path": None}, status="ready" if engines else "needs_context", bindings=deferred("access_path", engine + "_read_path"))
    if valid.get("I08") == "unknown":
        unresolved("I08", "unknown_need", "Chưa biết nhu cầu vending, khác với Không.")
    elif valid.get("I08") == "yes":
        add("I08", "vending", "storage.credential_vending", {"storage": None, "api": None}, status="needs_context", bindings=deferred("api", "delegation_path.api"))
        unresolved("I08", "unknown_storage", "Storage không thuộc payload form v2 và không được suy từ cloud.")
    if valid.get("I09") and valid["I09"] != ["none"]:
        out["reminders"].append({"source_input": "I09", "message": "Nền tảng đã gắn bó là bối cảnh; không tự lọc hoặc đổi trọng số."})
    features = valid.get("I10", {})
    for item in sorted(features.get("selected", []), key=lambda x: x["feature"]):
        feature = item["feature"]
        role = "HARD" if item["rank"] == "mandatory" else "SOFT"
        if feature == "branching":
            add("I10", feature, "workflow.branching", {"object_scope": profile["branching_object_scope"], "api": None}, role=role, bindings=deferred("api", "branching_path.api"))
        elif feature == "multi_table_atomic":
            bindings = {**deferred("api", "atomic_path.api"), **deferred("client_path", "atomic_path.client_path")}
            add("I10", feature, "transaction.multi_table_atomic", {"client_path": None, "failure_boundary": profile["atomic_failure_boundary"], "api": None}, role=role, bindings=bindings)
        else:
            add("I10", feature, "metadata.federation_operation", {"source_type": None, "operation": profile["federation_operation"], "api": None}, role=role, status="needs_context", bindings=deferred("api", "federation_path.api"))
            unresolved("I10", "unknown_sources", "Chưa có danh sách nguồn federation; không đặt thay người dùng.")
    if out["objectives"]:
        out["assumptions"].append({"parameter": f"rank_to_weight.{rank}", "value": weight, "assumption": True, "source": config["reasoning_config_source"], "weight_defaulted": True})
    if "I10" in valid and not features.get("none") and not features.get("selected"):
        unresolved("I10", "unanswered", "Chưa chọn nhu cầu hoặc xác nhận không có nhu cầu nào.")
    out["readiness"] = "needs_input_correction" if out["input_issues"] else "ready_for_assessment"
    return out
