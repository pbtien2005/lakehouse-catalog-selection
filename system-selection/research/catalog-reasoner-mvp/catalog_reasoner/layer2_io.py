"""Asset loading / JSON CLI for Layer 2; does not execute Layer 3."""

import argparse
import json
from pathlib import Path

from .layer2 import normalize_form


def load_assets(root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[2] / "catalog-knowledge-base"
    names = {"registry": "form-v2-registry.json", "mapping": "layer-2-mapping.json", "profile": "layer-2-mvp-profile.json", "config": "layer-2-runtime-config.json", "policy": "layer-2-policy.json", "dictionary": "layer-1-properties.json", "kb": "layer-1-data.json"}
    assets = {key: json.loads((root / name).read_text(encoding="utf-8-sig")) for key, name in names.items()}
    assets["reasoning_config"] = json.loads((root / assets["config"]["reasoning_config_source"]).read_text(encoding="utf-8-sig"))
    questions = assets["registry"]["questions"]
    rules = {r["id"]: r for r in assets["mapping"]["questions"]}
    if len(rules) != len(assets["mapping"]["questions"]) or set(rules) != {q["id"] for q in questions}:
        raise ValueError("Registry/mapping question IDs differ or are duplicated")
    for index, question in enumerate(questions):
        rule = rules[question["id"]]
        expected_ref = f"form-v2-registry.json#/questions/{index}/answers"
        if rule.get("answers_ref") != expected_ref:
            raise ValueError(f"Registry/mapping answers_ref mismatch: {question['id']}")
        if set(rule["answer_effects"]) != {a["id"] for a in question["answers"]}:
            raise ValueError(f"Registry/mapping answer mismatch: {question['id']}")
    return assets


def main(argv=None):
    parser = argparse.ArgumentParser(description="Normalize form-v2 answers only; no inference")
    parser.add_argument("--answers", required=True)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        result = normalize_form(json.loads(Path(args.answers).read_text(encoding="utf-8-sig")), load_assets())
        serialized = json.dumps(result, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
        if args.output:
            target = Path(args.output)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(serialized, encoding="utf-8")
        else:
            print(serialized, end="")
        return 0 if result["readiness"] == "ready_for_assessment" else 2
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
