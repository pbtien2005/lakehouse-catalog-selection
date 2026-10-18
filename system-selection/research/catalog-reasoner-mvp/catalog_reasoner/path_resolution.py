"""Choose one evidenced implementation intact; never join unrelated best claims.

Profiles prescribe controllable API/connector choices. Their context describes
applicability and may never fill a missing user fact. The portfolio is open: a
failed listed recipe does not prove that every possible implementation fails.
"""
from copy import deepcopy
from urllib.parse import urlparse

from .hard_filter import filter_hard
from .project_lookup import lookup_project


DESIGN_QUALIFIERS = frozenset({
    'api', 'connector', 'engine_release', 'access_path', 'action', 'client',
    'client_path', 'table_type', 'metadata_representation',
})
CONTEXT_KEYS = frozenset({'environment', 'format', 'storage', 'engines', 'operations'})


def _require(condition, path, message):
    if not condition:
        raise ValueError(f'{path}: {message}')


def _rules(value):
    return value if isinstance(value, list) else [{'when': {}, 'qualifiers': value}]


def _validated_profiles(kb, dictionary, registry):
    _require(isinstance(registry, dict), 'profiles', 'expected registry object')
    profiles = registry.get('profiles')
    _require(isinstance(profiles, list), 'profiles', 'expected array')
    properties = {p['id']: p for p in dictionary['properties']}
    claims = {c['id']: c for c in kb['claims']}
    scopes = {s['id'] for s in kb['scopes']}
    seen = set()
    for index, profile in enumerate(profiles):
        path = f'profiles[{index}]'
        _require(isinstance(profile, dict), path, 'expected object')
        pid = profile.get('id')
        _require(isinstance(pid, str) and pid and pid not in seen, path + '.id', 'expected unique nonempty string')
        seen.add(pid)
        scope = profile.get('scope_id')
        _require(scope in scopes, path + '.scope_id', 'unknown KB scope')
        ids = profile.get('claim_ids')
        _require(isinstance(ids, list) and ids and all(isinstance(cid, str) and cid in claims for cid in ids), path + '.claim_ids', 'expected nonempty known claim IDs')
        _require(len(ids) == len(set(ids)), path + '.claim_ids', 'duplicate claim ID')
        _require(all(claims[cid]['scope_id'] == scope for cid in ids), path + '.claim_ids', 'claim scope differs from implementation scope')
        evidence = profile.get('compatibility_evidence')
        _require(isinstance(evidence, list) and evidence, path + '.compatibility_evidence', 'joint compatibility evidence is required')
        for item in evidence:
            _require(isinstance(item, dict), path + '.compatibility_evidence', 'expected evidence object')
            url = item.get('url')
            parsed = urlparse(url) if isinstance(url, str) else None
            _require(parsed is not None and parsed.scheme == 'https' and bool(parsed.netloc) and isinstance(item.get('locator'), str) and bool(item['locator'].strip()), path + '.compatibility_evidence', 'expected HTTPS source and locator')
        context = profile.get('context')
        _require(isinstance(context, dict) and not set(context) - CONTEXT_KEYS, path + '.context', 'unknown context key or non-object')
        for key, value in context.items():
            valid = isinstance(value, str) and bool(value)
            if key in {'engines', 'operations'}:
                valid = isinstance(value, list) and bool(value) and all(isinstance(v, str) and bool(v) for v in value) and len(value) == len(set(value))
            _require(valid, path + '.context.' + key, 'expected explicit nonempty context value')
        bindings = profile.get('bindings')
        _require(isinstance(bindings, dict), path + '.bindings', 'expected property binding object')
        for prop, value in bindings.items():
            bpath = path + '.bindings.' + prop
            _require(prop in properties, bpath, 'unknown dictionary property')
            allowed = set(properties[prop]['qualifiers'] + properties[prop].get('optional_qualifiers', []))
            _require(isinstance(value, (dict, list)) and bool(value), bpath, 'expected qualifiers or rule array')
            for rule in _rules(value):
                _require(isinstance(rule, dict) and not set(rule) - {'when', 'qualifiers'}, bpath, 'invalid binding rule')
                when, qualifiers = rule.get('when', {}), rule.get('qualifiers')
                _require(isinstance(when, dict) and not set(when) - allowed and all(isinstance(v, str) and v for v in when.values()), bpath + '.when', 'invalid selector qualifiers')
                _require(isinstance(qualifiers, dict) and bool(qualifiers) and not set(qualifiers) - (allowed & DESIGN_QUALIFIERS) and all(isinstance(v, str) and v for v in qualifiers.values()), bpath + '.qualifiers', 'only evidenced design qualifiers can be bound; user facts cannot be overwritten')
                # A binding must have one coherent witness, not a Cartesian join
                # of API from one claim and connector from another.
                witness = [claims[cid] for cid in ids if claims[cid]['property_id'] == prop and all(claims[cid]['qualifiers'].get(k) == v for k, v in {**when, **qualifiers}.items())]
                _require(bool(witness), bpath, 'no same-property claim witnesses the complete binding')
    return sorted(deepcopy(profiles), key=lambda p: p['id'])


def _context_check(profile, context):
    conditions, mismatches = [], []
    for key, expected in sorted(profile['context'].items()):
        actual = context.get(key)
        if actual is None or actual == []:
            conditions.append({'type': 'implementation_context_unknown', 'context_key': key, 'expected': deepcopy(expected), 'reason': 'profile_choice_does_not_establish_user_fact', 'claim_ids': sorted(profile['claim_ids'])})
        elif key in {'engines', 'operations'}:
            if not isinstance(actual, list) or not set(actual).issubset(expected):
                mismatches.append({'context_key': key, 'actual': deepcopy(actual), 'supported': deepcopy(expected)})
        elif actual != expected:
            mismatches.append({'context_key': key, 'actual': deepcopy(actual), 'supported': expected})
    return conditions, mismatches


def _selector_matches(requirement, when):
    asked = requirement['qualifiers']
    accepted = requirement.get('qualifier_acceptance_sets', {})
    return all(asked.get(key) is not None and (asked[key] == value or value in accepted.get(key, [])) for key, value in when.items())


def _bind_requirements(requirements, profile, context, dictionary):
    rows = deepcopy(requirements)
    props = {p['id']: p for p in dictionary['properties']}
    incompatibilities = []
    for row in rows:
        original = deepcopy(row['qualifiers'])
        acceptance = row.setdefault('qualifier_acceptance_sets', {})
        binding_trace = []
        # These are known intake facts, not values borrowed from the recipe.
        for key in ['storage', 'format']:
            if key in row['qualifiers'] and row['qualifiers'][key] is None and context.get(key) is not None:
                row['qualifiers'][key] = context[key]
                acceptance[key] = [context[key]]
                binding_trace.append({'qualifier': key, 'value': context[key], 'source': 'known_intake_context'})
        applicable = [r for r in _rules(profile['bindings'][row['property_id']]) if _selector_matches(row, r.get('when', {}))] if row['property_id'] in profile['bindings'] else []
        assigned = {}
        for rule in applicable:
            for key, value in rule['qualifiers'].items():
                if key in assigned and assigned[key] != value:
                    raise ValueError(f"profiles.{profile['id']}.bindings.{row['property_id']}: overlapping rules disagree about {key}")
                assigned[key] = value
        for key, value in sorted(assigned.items()):
            before = row['qualifiers'].get(key)
            if before is not None and before != value and value not in acceptance.get(key, []):
                incompatibilities.append({'requirement_id': row['id'], 'qualifier': key, 'requested': before, 'profile_value': value})
                continue
            row['qualifiers'][key] = value
            acceptance[key] = [value]
            binding_trace.append({'qualifier': key, 'value': value, 'source': 'evidenced_implementation_choice', 'profile_id': profile['id']})
        if row.get('status') == 'needs_context' and all(row['qualifiers'].get(key) is not None for key in props[row['property_id']]['qualifiers']):
            row['status'] = 'ready'
        row['implementation_binding_trace'] = binding_trace
        row['original_qualifiers'] = original
    return rows, incompatibilities


def _classified(candidate):
    groups = filter_hard([candidate])['groups']
    return next(rows[0] for rows in groups.values() if rows)


def _functional_summary(candidate):
    functional = deepcopy(candidate)
    functional['assessments'] = [a for a in functional['assessments'] if a['property_id'] != 'limits.quota']
    classified = _classified(functional)
    return {
        'status': classified['group'],
        'hard_passes': [r['requirement_id'] for r in classified['hard_passes']],
        'hard_conditions': [r['requirement_id'] for r in classified['hard_conditions']],
        'hard_failures': [r['requirement_id'] for r in classified['hard_failures']],
        'hard_total': sum(len(classified[key]) for key in ['hard_passes', 'hard_conditions', 'hard_failures']),
        'hard_pass_count': len(classified['hard_passes']),
        'hard_unknown_count': len(classified['hard_conditions']),
        'hard_failure_count': len(classified['hard_failures']),
        'input_conditions': deepcopy(classified.get('input_conditions', [])),
        'excluded_from_functional_summary_only': ['limits.quota'],
        'quota_still_enforced_for_eligibility': True,
    }


def resolve_and_lookup(kb, candidates, requirements, config, dictionary, profiles, context):
    """Return normal lookups plus all recipe traces and one proposed whole recipe.

    Selection is deterministic: eligible before conditional; fewer pending HARD
    requirements; then profile ID. It is a prescription rule, not a utility score.
    An open portfolio of failed recipes falls back to strict unknown lookup.
    """
    _require(isinstance(context, dict), 'profiles.context', 'expected intake context object')
    portfolio = _validated_profiles(kb, dictionary, profiles)
    result = []
    for candidate in sorted(candidates, key=lambda c: c['id']):
        raw = lookup_project(kb, [candidate], requirements, config, dictionary)[0]
        alternatives, usable = [], []
        for profile in portfolio:
            if profile['scope_id'] != candidate['scope_id']:
                continue
            conditions, mismatches = _context_check(profile, context)
            bound, binding_mismatches = _bind_requirements(requirements, profile, context, dictionary)
            mismatches.extend(binding_mismatches)
            trace = {
                'id': profile['id'], 'scope_id': profile['scope_id'],
                'context': deepcopy(profile['context']), 'bindings': deepcopy(profile['bindings']),
                'claim_ids': sorted(profile['claim_ids']),
                'compatibility_evidence': deepcopy(profile['compatibility_evidence']),
                'prerequisites': deepcopy(profile.get('prerequisites', [])),
                'version_conditions': deepcopy(profile.get('version_conditions', [])),
            }
            if mismatches:
                alternatives.append({**trace, 'status': 'context_mismatch', 'context_mismatches': mismatches})
                continue
            lookup = lookup_project(kb, [candidate], bound, config, dictionary)[0]
            if conditions:
                lookup['input_conditions'] = conditions
            by_id = {r['id']: r for r in bound}
            for assessment in lookup['assessments']:
                row = by_id[assessment['requirement_id']]
                assessment['trace']['implementation_profile_id'] = profile['id']
                assessment['trace']['implementation_binding_trace'] = deepcopy(row['implementation_binding_trace'])
                assessment['trace']['original_requested_qualifiers'] = deepcopy(row['original_qualifiers'])
                assessment['trace']['compatibility_evidence'] = deepcopy(profile['compatibility_evidence'])
            classified = _classified(lookup)
            summary = _functional_summary(lookup)
            alternatives.append({**trace, 'status': 'evaluated', 'group': classified['group'], 'functional_summary': summary, 'assessments': deepcopy(lookup['assessments']), 'input_conditions': deepcopy(conditions)})
            if classified['group'] != 'excluded':
                usable.append((classified['group'] != 'eligible', len(classified['hard_conditions']) + len(conditions), profile['id'], lookup))
        if usable:
            _, _, selected_id, selected = min(usable, key=lambda item: item[:3])
            limits = ['single_proposed_profile_metrics_not_optimized_over_all_profiles', 'profile_portfolio_is_not_asserted_complete']
            selected['proposed_implementation'] = deepcopy(next(p for p in alternatives if p['id'] == selected_id))
        else:
            selected, selected_id = raw, None
            limits = ['unseen_implementation_paths_not_ruled_out', 'profile_portfolio_is_not_asserted_complete']
            selected.setdefault('input_conditions', []).append({
                'type': 'implementation_path_unverified',
                'requirement_ids': sorted(r['id'] for r in requirements),
                'claim_ids': [],
                'reason': 'no_applicable_joint_implementation_witness; absence_is_not_non_support',
            })
            selected['proposed_implementation'] = None
        selected['selected_profile_id'] = selected_id
        selected['implementation_profiles'] = alternatives
        selected['functional_summary'] = _functional_summary(selected)
        selected['path_resolution_limits'] = limits
        selected['profile_selection_rule'] = 'eligible_then_conditional_then_fewer_pending_hard_then_profile_id'
        result.append(selected)
    return result
