"""Synthetic implementation portfolios: evidence never combines incompatible paths."""
from copy import deepcopy

import pytest

from catalog_reasoner.hard_filter import filter_hard
from catalog_reasoner.project_io import load_project_config


@pytest.fixture
def fixture():
    config = load_project_config()
    scope = 'synthetic_scope_a'
    claims = [
        {'id': 'synthetic_read_a', 'scope_id': scope, 'property_id': 'integration.engine_operation', 'qualifiers': {'engine': 'spark', 'format': 'iceberg', 'operation': 'read', 'api': 'read_a', 'connector': 'connector_a'}, 'level': 'full'},
        {'id': 'synthetic_branch_a', 'scope_id': scope, 'property_id': 'workflow.branching', 'qualifiers': {'object_scope': 'catalog', 'api': 'branch_a'}, 'level': 'full'},
    ]
    kb = {'manifest': {'synthetic': True}, 'scopes': [{'id': scope}, {'id': 'synthetic_scope_b'}], 'claims': claims}
    candidate = {'id': 'synthetic_catalog', 'scope_id': scope}
    requirements = [
        {'id': 'H-read', 'property_id': 'integration.engine_operation', 'qualifiers': {'engine': 'spark', 'format': 'iceberg', 'operation': 'read', 'api': None}, 'role': 'HARD', 'status': 'ready', 'min_level_if_applicable': 'full'},
        {'id': 'H-branch', 'property_id': 'workflow.branching', 'qualifiers': {'object_scope': 'catalog', 'api': None}, 'role': 'HARD', 'status': 'ready', 'min_level_if_applicable': 'full'},
    ]
    profile = {'id': 'synthetic_plan_a', 'scope_id': scope, 'context': {'environment': 'on_prem', 'format': 'iceberg', 'engines': ['spark']}, 'bindings': {'integration.engine_operation': [{'when': {'engine': 'spark', 'operation': 'read'}, 'qualifiers': {'api': 'read_a', 'connector': 'connector_a'}}], 'workflow.branching': {'api': 'branch_a'}}, 'claim_ids': [c['id'] for c in claims], 'compatibility_evidence': [{'url': 'https://example.org/synthetic-profile', 'locator': 'Synthetic fixture only'}]}
    return kb, [candidate], requirements, config['reasoning'], config['dictionary'], {'profiles': [profile]}, {'environment': 'on_prem', 'format': 'iceberg', 'engines': ['spark'], 'storage': None}


def resolve(data):
    from catalog_reasoner.path_resolution import resolve_and_lookup
    return resolve_and_lookup(*data)


def test_complete_profile_binds_controllable_choices_without_uncovered_api(fixture):
    rows = resolve(fixture)
    assert filter_hard(rows)['groups']['eligible']
    assert rows[0]['selected_profile_id'] == 'synthetic_plan_a'
    assert rows[0]['functional_summary']['status'] == 'eligible'
    assert all(a['level'] == 'full' for a in rows[0]['assessments'])
    assert rows[0]['implementation_profiles'][0]['compatibility_evidence']


def test_separate_profiles_cannot_supply_each_others_successes(fixture):
    kb, _, _, _, _, portfolio, _ = fixture
    original = deepcopy(portfolio['profiles'][0])
    kb['claims'][1]['level'] = 'none'
    kb['claims'].extend([
        {**deepcopy(kb['claims'][0]), 'id': 'synthetic_read_b', 'qualifiers': {**kb['claims'][0]['qualifiers'], 'api': 'read_b'}, 'level': 'none'},
        {**deepcopy(kb['claims'][1]), 'id': 'synthetic_branch_b', 'qualifiers': {'object_scope': 'catalog', 'api': 'branch_b'}, 'level': 'full'},
    ])
    other = deepcopy(original)
    other['id'] = 'synthetic_plan_b'
    other['claim_ids'] = ['synthetic_read_b', 'synthetic_branch_b']
    other['bindings']['integration.engine_operation'][0]['qualifiers']['api'] = 'read_b'
    other['bindings']['workflow.branching']['api'] = 'branch_b'
    portfolio['profiles'].append(other)
    rows = resolve(fixture)
    assert not filter_hard(rows)['groups']['eligible']
    assert filter_hard(rows)['groups']['conditional']
    assert all(p['group'] == 'excluded' for p in rows[0]['implementation_profiles'])
    assert rows[0]['selected_profile_id'] is None
    assert 'unseen_implementation_paths_not_ruled_out' in rows[0]['path_resolution_limits']


def test_unknown_user_storage_is_never_resolved_by_choosing_profile(fixture):
    kb, _, requirements, _, _, portfolio, context = fixture
    claim = {'id': 'synthetic_vend', 'scope_id': 'synthetic_scope_a', 'property_id': 'storage.credential_vending', 'qualifiers': {'storage': 'aws_s3', 'api': 'temporary_data_access'}, 'level': 'full'}
    kb['claims'].append(claim)
    requirements.append({'id': 'H-vend', 'property_id': claim['property_id'], 'qualifiers': {'storage': None, 'api': None}, 'role': 'HARD', 'status': 'needs_context', 'min_level_if_applicable': 'full'})
    profile = portfolio['profiles'][0]
    profile['context']['storage'] = 'aws_s3'
    profile['claim_ids'].append(claim['id'])
    profile['bindings'][claim['property_id']] = {'api': 'temporary_data_access'}
    rows = resolve(fixture)
    assert filter_hard(rows)['groups']['conditional']
    assessment = next(a for a in rows[0]['assessments'] if a['requirement_id'] == 'H-vend')
    assert assessment['level'] == 'unknown'
    assert assessment['trace']['requested_qualifiers']['storage'] is None
    context['storage'] = 'aws_s3'
    assert filter_hard(resolve(fixture))['groups']['eligible']


@pytest.mark.parametrize('defect', ['wrong_scope', 'unknown_claim', 'missing_compatibility', 'unproven_binding', 'override_user_fact'])
def test_invalid_profile_fails_closed_with_field_path(fixture, defect):
    profile = fixture[5]['profiles'][0]
    if defect == 'wrong_scope':
        profile['scope_id'] = 'synthetic_scope_b'
    elif defect == 'unknown_claim':
        profile['claim_ids'] = ['synthetic_missing']
    elif defect == 'missing_compatibility':
        profile['compatibility_evidence'] = []
    elif defect == 'unproven_binding':
        profile['bindings']['workflow.branching']['api'] = 'synthetic_unsupported_api'
    else:
        profile['bindings']['integration.engine_operation'][0]['qualifiers']['format'] = 'delta'
    with pytest.raises(ValueError, match='profiles'):
        resolve(fixture)


def test_matching_conflict_outside_profile_claim_ids_remains_unknown(fixture):
    kb = fixture[0]
    conflict = {**deepcopy(kb['claims'][0]), 'id': 'synthetic_unlisted_conflict', 'level': 'none'}
    kb['claims'].append(conflict)
    rows = resolve(fixture)
    assert filter_hard(rows)['groups']['conditional']
    read = next(a for a in rows[0]['assessments'] if a['requirement_id'] == 'H-read')
    assert 'conflicting_claims' in read['unknown_reasons']
    assert conflict['id'] in read['trace']['claim_ids']


def test_profiles_claims_and_requirements_are_pure_and_order_independent(fixture):
    original = deepcopy(fixture)
    first = resolve(fixture)
    assert fixture == original
    fixture[0]['claims'].reverse()
    fixture[2].reverse()
    fixture[5]['profiles'].reverse()
    fixture[5]['profiles'][0]['claim_ids'].reverse()
    assert resolve(fixture) == first


def test_missing_profile_keeps_raw_strict_unknown(fixture):
    fixture[5]['profiles'] = []
    rows = resolve(fixture)
    assert rows[0]['selected_profile_id'] is None
    assert rows[0]['implementation_profiles'] == []
    assert filter_hard(rows)['groups']['conditional']


def test_profile_does_not_hide_unknown_environment_or_format(fixture):
    fixture[6]['environment'] = None
    rows = resolve(fixture)
    assert filter_hard(rows)['groups']['conditional']
    assert any(c['context_key'] == 'environment' for c in rows[0]['input_conditions'])


def test_explicit_context_mismatch_does_not_force_false_support(fixture):
    fixture[6]['format'] = 'delta'
    rows = resolve(fixture)
    assert rows[0]['selected_profile_id'] is None
    assert rows[0]['implementation_profiles'][0]['status'] == 'context_mismatch'


def test_context_mismatch_cannot_fall_back_to_unconditional_raw_pass(fixture):
    # A fixed API can make raw lookup full, but the only evidenced joint recipe
    # is inapplicable to the actual user format.
    fixture[2][:] = [fixture[2][1]]
    fixture[2][0]['qualifiers']['api'] = 'branch_a'
    fixture[6]['format'] = 'delta'
    rows = resolve(fixture)
    assert filter_hard(rows)['groups']['conditional']
    assert rows[0]['selected_profile_id'] is None
    assert any(c['type'] == 'implementation_path_unverified' for c in rows[0]['input_conditions'])


def test_functional_summary_does_not_silently_remove_quota_from_eligibility(fixture):
    fixture[2].append({'id': 'H-quota', 'property_id': 'limits.quota', 'qualifiers': {'resource': 'tables', 'boundary': 'catalog'}, 'role': 'HARD', 'status': 'ready', 'operator': 'capacity_covers_demand_interval', 'demand_interval': {'lower': 0, 'upper': 99}, 'boundary_confirmed': True})
    rows = resolve(fixture)
    assert rows[0]['functional_summary']['status'] == 'eligible'
    assert filter_hard(rows)['groups']['conditional']
    assert 'H-quota' not in rows[0]['functional_summary']['hard_passes']
