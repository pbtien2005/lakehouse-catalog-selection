"""Versioned, source-backed evidence overlays. Historical KB is never edited."""
from copy import deepcopy


def merge_knowledge(kb, overlay):
    result = deepcopy(kb)
    original = {c['id']: c for c in result['claims']}
    scopes = {s['id'] for s in result['scopes']}
    removed = set()
    added = set()
    for claim in overlay.get('claims', []):
        cid = claim.get('id')
        if not isinstance(cid, str) or not cid or cid in original or cid in added:
            raise ValueError(f'Evidence overlay claim ID is invalid or duplicated: {cid}')
        if claim.get('scope_id') not in scopes or not claim.get('evidence'):
            raise ValueError(f'Evidence overlay claim requires a known scope and evidence: {cid}')
        for source in claim['evidence']:
            if not isinstance(source, dict) or not source.get('url', '').startswith('https://') or not source.get('locator'):
                raise ValueError(f'Evidence overlay source requires HTTPS URL and locator: {cid}')
        for sid in claim.get('supersedes_claim_ids', []):
            prior = original.get(sid)
            if prior is None or any(prior.get(key) != claim.get(key) for key in ['scope_id', 'property_id', 'qualifiers']):
                raise ValueError(f'Evidence overlay supersedes a different fact: {sid}')
            if prior.get('level') not in [None, 'unknown'] or prior.get('value') is not None:
                raise ValueError(f'Evidence overlay cannot hide a known conflicting fact: {sid}')
            removed.add(sid)
        added.add(cid)
    result['claims'] = sorted([c for c in result['claims'] if c['id'] not in removed] + deepcopy(overlay.get('claims', [])), key=lambda c: c['id'])
    extension = deepcopy(overlay.get('manifest', {}))
    extension['superseded_unknown_claim_ids'] = sorted(removed)
    result.setdefault('manifest', {})['base_revision'] = result.get('manifest', {}).get('revision')
    result['manifest']['revision'] = str(result['manifest']['base_revision']) + '+' + str(extension.get('revision', 'source-overlay'))
    result['manifest']['knowledge_extensions'] = [extension]
    return result


def extend_value_mapping(mapping, kb, curated_rows):
    """Only explicit reviewed aliases or exact identifiers are accepted in v3."""
    result = deepcopy(mapping)
    existing = {(r['property_id'], r['qualifier'], r['input_value']): r for r in result['rows']}
    for row in curated_rows:
        existing[(row['property_id'], row['qualifier'], row['input_value'])] = deepcopy(row)
    literals = {}
    for claim in kb['claims']:
        for qualifier, value in claim['qualifiers'].items():
            literals.setdefault((claim['property_id'], qualifier, value), []).append(claim['id'])
    for key, claim_ids in sorted(literals.items()):
        if key in existing and existing[key]['accepted_kb_values']:
            continue
        prop, qualifier, value = key
        existing[key] = {'id': 'EXACT:' + ':'.join(key), 'property_id': prop, 'qualifier': qualifier, 'input_value': value, 'accepted_kb_values': [value], 'evidence_claim_ids': sorted(claim_ids), 'status': 'mapped', 'reason': 'Exact identifier in reviewed merged KB; no alias or compatibility inferred.'}
    result['rows'] = list(existing.values())
    result['manifest']['revision'] = 'layer2-kb-values-v3-evidenced-paths-v1'
    result['manifest']['policy'] = 'Explicit aliases and exact values; implementation profile selection is joint, not per-property best claim.'
    return result
