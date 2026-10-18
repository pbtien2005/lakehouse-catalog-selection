"""Pure orchestration for the first requested review gate, stages 1-2 only."""

from copy import deepcopy

from .contracts import assumptions_used, requirement_rows, validate_inputs
from .hard_filter import filter_hard
from .lookup import lookup_levels


def run_stage12(kb, requirement_document, config):
    if isinstance(requirement_document, dict) and requirement_document.get('readiness') == 'needs_input_correction':
        return {'status': 'input_error', 'inference_executed': False,
                'groups': {key: [] for key in ['eligible', 'conditional', 'excluded']},
                'ranking': [], 'input_issues': deepcopy(requirement_document.get('input_issues', []))}
    validate_inputs(kb, requirement_document, config)
    lookups = lookup_levels(kb, requirement_document["candidates"], requirement_rows(requirement_document), config)
    return {
        "stage": "1-2",
        "input_revisions": {
            "kb": kb.get("manifest", {}).get("revision"),
            "requirements": requirement_document.get("manifest", {}).get("revision"),
        },
        "synthetic_data": kb.get("manifest", {}).get("synthetic") is True,
        **filter_hard(lookups),
        "assumptions": assumptions_used(requirement_document, config),
        "config": deepcopy(config),
        "not_run": ["stage_3_soft_scoring", "stage_4_scenarios_and_unknown_impact"],
    }
