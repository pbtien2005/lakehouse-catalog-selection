"""File/JSON boundary around the pure two-step pipeline."""

import argparse
import json
from pathlib import Path

from .pipeline import run_stage12


def main(argv=None):
    parser = argparse.ArgumentParser(description="Catalog reasoner MVP: lookup and HARD filtering only")
    parser.add_argument("--kb", required=True)
    parser.add_argument("--requirements", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        data = [json.loads(Path(path).read_text(encoding="utf-8-sig")) for path in [args.kb, args.requirements, args.config]]
        result = run_stage12(*data)
        serialized = json.dumps(result, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False) + "\n"
        if args.output:
            destination = Path(args.output)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(serialized, encoding="utf-8")
        else:
            print(serialized, end="")
    except (OSError, ValueError) as error:
        print(json.dumps({"stage": "1-2", "error": str(error)}, ensure_ascii=True, sort_keys=True))
        return 2
    return 0
