"""Pure architect-facing v3 intake. V2 behavior stays independently available.

Storage and workload actions are user facts, not inferred from a cloud/provider.
API/path selection remains the resolver's responsibility and is never a form field.
"""
from copy import deepcopy

from .layer2 import normalize_form


STORAGE_VALUES = ("s3", "adls_gen2", "gcs", "local_fs", "hdfs", "unknown")
OPERATION_VALUES = ("read", "append", "merge", "overwrite", "create_table", "unknown")


def normalize_form_v3(payload, assets):
    """Normalize explicit storage/actions and optional exact capacity, without I/O."""
    source = payload if isinstance(payload, dict) else {}
    raw = source.get("answers", {})
    answers = raw if isinstance(raw, dict) else {}
    legacy_answers = {k: deepcopy(v) for k, v in answers.items() if k not in {"I11", "I12"}}
    local_lab = answers.get("I01") == "local_lab"
    if local_lab:
        legacy_answers.pop("I01")
    document = normalize_form({"form_revision": "input-v2", "answers": legacy_answers if isinstance(raw, dict) else raw}, assets)
    document["raw_answers"] = deepcopy(raw)
    document["raw_context"] = deepcopy(source.get("context", {}))
    document["revisions"].update(form="input-v3", registry="form-v3-registry-v1", intake="intake-v3-v1")
    document["profile_assumptions"]["engine_operation"] = "explicit_per_engine_I12_no_default"
    document["assessment_limits"]["workload_operations"] = "explicit_per_engine_actions"

    def issue(code, field, message):
        document["input_issues"].append({"code": code, "field": field, "message": message})

    def unresolved(qid, state, reason, **extra):
        document["unresolved"].append({"source_input": qid, "state": state, "reason": reason, **extra})

    def add_requirement(qid, suffix, property_id, qualifiers, source_inputs, *, status="ready", binding_path=None):
        rid = f"R-{qid}-{suffix}"
        bindings = {"api": {"source": "candidate_path", "path": binding_path, "execution": "trace_only_deferred"}} if binding_path else {}
        row = {"id": rid, "logical_need_id": f"N-{qid}", "source_inputs": source_inputs,
               "property_id": property_id, "role": "HARD", "status": status,
               "qualifiers": qualifiers, "candidate_bindings": bindings,
               "acceptance_anchor": property_id, "min_level_if_applicable": assets["config"]["hard_min_level"],
               "binding_sources": {"form": source_inputs, "profile": "intake-v3-v1", "candidate_bindings": "trace_only_deferred"}}
        document["requirements"].append(row)
        document["trace"][rid] = {"source_inputs": source_inputs, "mapping_rule": "intake-v3-v1",
            "property_id": property_id, "raw_answers": {qid: deepcopy(answers.get(qid)) for qid in source_inputs},
            "candidate_bindings_execution": "trace_only_deferred"}
        return row

    if not isinstance(payload, dict):
        issue("E_PAYLOAD", "$", "Payload phải là object có form_revision và answers.")
    if source.get("form_revision") != "input-v3":
        issue("E_FORM_REVISION", "form_revision", "Dùng form_revision=input-v3 cho storage và thao tác từng engine.")
    for key in sorted(set(source) - {"form_revision", "answers", "context"}):
        issue("E_UNKNOWN_FIELD", key, "Trường ngoài hợp đồng form v3.")

    if local_lab:
        document["normalized_context"]["I01"] = "local_lab"
        document["unresolved"] = [u for u in document["unresolved"] if u["source_input"] != "I01"]
        if assets["config"]["default_environment_facts_as_hard"]:
            add_requirement("I01", "environment", "deployment.environment", {"environment": "local_lab"}, ["I01"])
            document["reminders"].append({"source_input": "I01", "message": "Lab cục bộ chỉ xác nhận phạm vi lab, không chứng minh triển khai on-prem sản xuất."})

    storage = answers.get("I11")
    if storage is not None and (not isinstance(storage, str) or storage not in STORAGE_VALUES):
        issue("E_INVALID_ANSWER", "answers.I11", "Chọn storage trong form v3 hoặc Chưa biết.")
    elif storage is not None:
        document["normalized_context"]["I11"] = storage
    if isinstance(storage, str) and storage in STORAGE_VALUES and storage != "unknown":
        for row in document["requirements"]:
            if row["property_id"] == "storage.credential_vending":
                row["qualifiers"]["storage"] = storage
                row["status"] = "ready"
                row["source_inputs"] = ["I08", "I11"]
                row["binding_sources"]["form"] = ["I08", "I11"]
                document["trace"][row["id"]].update(source_inputs=["I08", "I11"], storage_input=storage)
        document["unresolved"] = [u for u in document["unresolved"] if not (u["source_input"] == "I08" and u["state"] == "unknown_storage")]

    selected_engines = document["normalized_context"].get("I02", [])
    operations = answers.get("I12", {})
    if not isinstance(operations, dict):
        issue("E_CARDINALITY", "answers.I12", "Dùng object theo engine, mỗi engine có danh sách thao tác.")
        operations = {}
    valid_operations = {}
    for engine, values in sorted(operations.items()):
        field = f"answers.I12.{engine}"
        if engine not in selected_engines:
            issue("E_ENGINE_NOT_SELECTED", field, "Chọn engine ở I02 trước khi khai báo thao tác.")
        elif not isinstance(values, list) or not values:
            issue("E_CARDINALITY", field, "Chọn ít nhất một thao tác hoặc Chưa rõ.")
        elif any(not isinstance(v, str) or v not in OPERATION_VALUES for v in values):
            issue("E_INVALID_ANSWER", field, "Chọn thao tác có trong form v3.")
        elif len(values) != len(set(values)):
            issue("E_DUPLICATE_SELECTION", field, "Mỗi thao tác chỉ chọn một lần.")
        elif "unknown" in values and len(values) != 1:
            issue("E_EXCLUSIVE_UNKNOWN", field, "Chưa rõ không được chọn cùng thao tác cụ thể.")
        else:
            valid_operations[engine] = sorted(values)
    if "I12" in answers and isinstance(answers["I12"], dict):
        document["normalized_context"]["I12"] = deepcopy(valid_operations)

    removed = {r["id"] for r in document["requirements"] if r["property_id"] == "integration.engine_operation"}
    document["requirements"] = [r for r in document["requirements"] if r["id"] not in removed]
    for rid in removed:
        document["trace"].pop(rid, None)
    normalized_format = document["normalized_context"].get("I03")
    fmt = normalized_format if normalized_format in {"iceberg", "delta", "hudi"} else None
    for engine in selected_engines:
        values = valid_operations.get(engine)
        if not values or values == ["unknown"]:
            unresolved("I12", "unknown_operations", "Chưa rõ thao tác của engine; không tự giả định chỉ đọc.", engine=engine)
            continue
        if engine == "other" or not assets["config"]["default_environment_facts_as_hard"]:
            continue
        for operation in values:
            qid = "I02" if operation == "read" else "I12"
            add_requirement(qid, engine + "-" + operation, "integration.engine_operation",
                            {"engine": engine, "format": fmt, "operation": operation, "api": None},
                            ["I02", "I12"], status="ready" if fmt else "needs_context",
                            binding_path=engine + "_" + operation + "_path.api")

    context = source.get("context", {})
    if not isinstance(context, dict):
        issue("E_PAYLOAD", "context", "context phải là object; có thể bỏ nếu chưa biết số bảng chính xác.")
    else:
        for key in sorted(set(context) - {"table_count_exact"}):
            issue("E_UNKNOWN_FIELD", f"context.{key}", "Trường ngoài context form v3.")
        if "table_count_exact" in context:
            exact = context["table_count_exact"]
            bucket = document["normalized_context"].get("I04")
            interval = assets["config"]["table_count_intervals"].get(bucket)
            if type(exact) is not int or exact <= 0:
                issue("E_TABLE_COUNT", "context.table_count_exact", "Nhập số nguyên dương hoặc để trống nếu chưa biết.")
            elif interval is None or exact < interval["lower"] or (interval["upper"] is not None and exact > interval["upper"]):
                issue("E_TABLE_COUNT_BUCKET", "context.table_count_exact", "Số bảng chính xác phải thuộc khoảng đã chọn ở I04.")
            else:
                document["normalized_context"]["table_count_exact"] = exact
                for row in document["requirements"]:
                    if row["property_id"] == "limits.quota":
                        row["demand_interval"] = {"lower": exact, "upper": exact}
                        document["trace"][row["id"]]["context_inputs"] = ["context.table_count_exact"]
                document["assumptions"].append({"parameter": "context.table_count_exact", "value": exact,
                    "assumption": False, "source": "explicit_input_not_default"})
    document["readiness"] = "needs_input_correction" if document["input_issues"] else "ready_for_assessment"
    return document
