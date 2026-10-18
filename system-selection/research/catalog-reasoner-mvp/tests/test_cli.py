"""Exercise file-to-JSON use of the two implemented steps."""

import importlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def arguments():
    return ["--kb", str(ROOT / "examples/synthetic-kb.json"), "--requirements", str(ROOT / "examples/synthetic-requirements.json"), "--config", str(ROOT / "config.json")]


def test_cli_writes_reviewable_json(tmp_path):
    output = tmp_path / "nested/result.json"
    main = importlib.import_module("catalog_reasoner.cli").main
    assert main(arguments() + ["--output", str(output)]) == 0
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["stage"] == "1-2"
    assert result["groups"]["excluded"][0]["candidate_id"] == "synthetic_beta"
    assert result["not_run"] == ["stage_3_soft_scoring", "stage_4_scenarios_and_unknown_impact"]


def test_cli_stdout_is_json(capsys):
    main = importlib.import_module("catalog_reasoner.cli").main
    assert main(arguments()) == 0
    assert json.loads(capsys.readouterr().out)["synthetic_data"] is True


@pytest.mark.parametrize("kind", ["missing_file", "malformed_json", "invalid_config"])
def test_cli_bad_inputs_produce_error_json_not_recommendations(tmp_path, capsys, kind):
    args = arguments()
    if kind == "missing_file":
        args[1] = str(tmp_path / "missing.json")
    elif kind == "malformed_json":
        bad = tmp_path / "bad.json"
        bad.write_text("not-json", encoding="utf-8")
        args[1] = str(bad)
    else:
        bad = tmp_path / "bad-config.json"
        config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        config["seed"] = "invalid"
        bad.write_text(json.dumps(config), encoding="utf-8")
        args[5] = str(bad)
    main = importlib.import_module("catalog_reasoner.cli").main
    assert main(args) == 2
    error = json.loads(capsys.readouterr().out)
    assert error["stage"] == "1-2"
    assert "error" in error and "groups" not in error
