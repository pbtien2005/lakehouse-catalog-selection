"""Run source-adapted lab inputs through the unchanged official pipeline.

No KB enrichment, weight tuning, source-catalog binding, or cloud provisioning.
Run from any working directory with the project's existing Python interpreter.
"""
from collections import Counter
from copy import deepcopy
import csv
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0, str(PROJECT))

from catalog_reasoner.application import run_case
from catalog_reasoner.contracts import requirement_rows
from catalog_reasoner.project_io import load_kb, load_project_config


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def write_json(path, value):
    path.write_text(canonical(value) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected_hashes():
    paths = list((PROJECT.parent / "catalog-knowledge-base").glob("*.json"))
    paths += list((PROJECT / "catalog_reasoner").glob("*.py"))
    paths += list((PROJECT / "cases").glob("*.json"))
    paths += [PROJECT / "config.json", PROJECT / "mvp-settings.json"]
    return {str(p.relative_to(PROJECT.parent)): digest(p) for p in sorted(paths)}


def main():
    before = protected_hashes()
    experiment = read_json(HERE / "experiment-config.json")
    casebook = read_json(HERE / "casebook.json")
    sources = read_json(HERE / "source-register.json")
    source_ids = {s["id"] for s in sources["sources"]}
    kb, config = load_kb(), load_project_config()
    valid_claims = {c["id"] for c in kb["claims"]}
    active = {q["id"] for q in config["layer2"]["registry"]["questions"] if q["enabled"]}
    records = casebook["cases"]
    by_id = {c["id"]: c for c in records}
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    summary = []
    candidate_rows = []
    checks = []
    input_hashes = {}
    for record in records:
        case_id = record["id"]
        form_path = HERE / record["form_file"]
        payload = read_json(form_path)
        input_hashes[record["form_file"]] = digest(form_path)
        assert set(payload["answers"]) == active, f"{case_id}: active form coverage"
        assert "I06" not in payload["answers"], f"{case_id}: disabled streaming"
        assert set(record["source_ids"]) <= source_ids, f"{case_id}: unknown source reference"
        if record.get("base_case"):
            base = read_json(HERE / by_id[record["base_case"]]["form_file"])
            expected = deepcopy(base)
            expected["answers"]["I10"]["selected"][0]["rank"] = experiment["case_parameters"][case_id]["branching_rank"]["value"]
            assert payload == expected, "Counterfactual changed more than the declared priority"
        else:
            assert set(record["answer_evidence"]) == active, f"{case_id}: missing provenance"
            for evidence in record["answer_evidence"].values():
                assert evidence["basis"] in casebook["evidence_labels"]
                assert set(evidence["source_ids"]) <= source_ids
        result = run_case(payload, kb, config)
        assert result["status"] == "ok" and result["inference_executed"], f"{case_id}: invalid input"
        encoded = canonical(result)
        for _ in range(1, experiment["verification_repeats"]):
            assert encoded == canonical(run_case(payload, kb, config)), f"{case_id}: not deterministic"
        document = result["requirements"]
        rows = requirement_rows(document)
        requirement_ids = {r["id"] for r in rows}
        assert document["raw_answers"] == payload["answers"], f"{case_id}: payload changed"
        counts = Counter(r["role"] for r in rows)
        ranked_ids = {c["candidate_id"] for c in result["ranking"]}
        excluded_ids = {c["candidate_id"] for c in result["groups"]["excluded"]}
        assert not ranked_ids & excluded_ids, f"{case_id}: excluded ranked"
        candidate_details = []
        conditions_by_property = Counter()
        for group, candidates in result["groups"].items():
            for candidate in candidates:
                assert group != "eligible" or not candidate["hard_conditions"], f"{case_id}: unknown declared eligible"
                for a in candidate["assessments"]:
                    assert a["requirement_id"] in requirement_ids
                    assert a["trace"]["requirement_id"] == a["requirement_id"]
                    assert set(a["trace"]["claim_ids"]) <= valid_claims
                    if a["level"] == "unknown":
                        conditions_by_property[a["property_id"]] += 1
                if not counts["SOFT"]:
                    assert candidate.get("score_interval") is None
                    assert candidate.get("top_rate") is None
                detail = {
                    "case_id": case_id,
                    "candidate_id": candidate["candidate_id"],
                    "name": candidate["name"],
                    "scope_id": candidate["scope_id"],
                    "group": group,
                    "hard_pass_count": len(candidate["hard_passes"]),
                    "hard_condition_count": len(candidate["hard_conditions"]),
                    "hard_failure_count": len(candidate["hard_failures"]),
                    "score_interval": candidate.get("score_interval"),
                    "top_rate": candidate.get("top_rate"),
                    "max_regret_observed": candidate.get("max_regret_observed"),
                    "regret_upper_bound": candidate.get("regret_upper_bound"),
                }
                candidate_details.append(detail)
                candidate_rows.append(detail)
        row = {
            "case_id": case_id,
            "kind": record["kind"],
            "synthetic_profile": record["synthetic_profile"],
            "status": result["status"],
            "group_counts": {group: len(candidates) for group, candidates in result["groups"].items()},
            "requirement_counts": dict(sorted(counts.items())),
            "requirement_ids": sorted(requirement_ids),
            "unresolved_input_count": len(result["unresolved_inputs"]),
            "unknown_assessments_by_property": dict(sorted(conditions_by_property.items())),
            "score_policy": "no_soft_no_ranking_metrics" if not counts["SOFT"] else "absolute_weighted_sum",
            "scenario_status": result["scenarios"]["status"],
            "scenario_count": result["scenarios"]["scenario_count"],
            "no_feasible_rate": result["scenarios"]["no_feasible_rate"],
            "robust_eligible_winner": [],
            "candidate_details": candidate_details,
            "trace_file": f"results/{case_id}.json",
        }
        # This field describes only the observed eligible group; it is not a recommendation rule.
        if result["groups"]["eligible"]:
            row["robust_eligible_winner"] = None
        write_json(out / f"{case_id}.json", result)
        write_json(out / f"{case_id}.requirements.json", document)
        summary.append(row)
        checks.append({"case_id": case_id, "status": "pass", "checks": ["active_fields_and_provenance", "valid_official_pipeline_input", "payload_preserved", "declared_priority_only_counterfactual" if record.get("base_case") else "source_ids_exist", "same_seed_same_full_json", "requirement_and_claim_references_exist", "excluded_not_ranked", "unknown_not_unconditionally_eligible", "no_fabricated_no_soft_scores"]})
    after = protected_hashes()
    assert before == after, "Protected runtime, KB, configs or frozen split changed"
    write_json(out / "summary.json", summary)
    with (out / "candidate-results.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(candidate_rows[0]))
        writer.writeheader()
        for row in candidate_rows:
            writer.writerow({k: json.dumps(v) if isinstance(v, list) else v for k, v in row.items()})
    inputs = [HERE / "experiment-config.json", HERE / "casebook.json", HERE / "source-register.json", Path(__file__).resolve()]
    input_hashes.update({str(p.relative_to(HERE)): digest(p) for p in inputs})
    manifest = {
        "status": "pass",
        "review_date": experiment["review_date"],
        "execution": "official run_case; no UI automation or lakehouse infrastructure deployment",
        "case_checks": checks,
        "input_sha256": input_hashes,
        "protected_before": before,
        "protected_after": after,
        "protected_files_unchanged": before == after,
        "experiment_config": experiment,
        "model_config_echo": {"reasoning": config["reasoning"], "settings": config["settings"], "layer2": config["layer2"]["config"]},
        "result_sha256": {str(p.relative_to(HERE)): digest(p) for p in sorted(out.glob("*.json")) if p.name != "run-manifest.json"},
    }
    write_json(out / "run-manifest.json", manifest)
    for row in summary:
        print(json.dumps({k: row[k] for k in ["case_id", "status", "group_counts", "requirement_counts", "unresolved_input_count", "scenario_status", "scenario_count"]}, ensure_ascii=True))
    print(json.dumps({"protected_files_unchanged": True, "result_directory": str(out)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
