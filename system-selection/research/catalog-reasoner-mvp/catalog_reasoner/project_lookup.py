"""Property-aware lookup, accepted alternatives, and quantity comparison."""
from copy import deepcopy
from itertools import product

from .contracts import LEVELS


def _matches(actual, key, value, accepted):
    return actual.get(key) in accepted[key] if key in accepted else actual.get(key)==value


def _quota(claims, requirement):
    if not requirement.get('boundary_confirmed'):
        return 'none','full',['quota_boundary_not_confirmed']
    amounts=[];minimums=[]
    for c in claims:
        value=c.get('value')
        kind=c.get('observation_context',{}).get('limit_kind')
        if not isinstance(value,dict) or value.get('unit')!='tables' or kind not in {'fixed','confirmed','demonstrated_minimum'}:
            return 'none','full',['quota_value_or_account_conditions_unknown']
        (minimums if kind=='demonstrated_minimum' else amounts).append(value['amount'])
    lo=requirement['demand_interval']['lower'];hi=requirement['demand_interval']['upper']
    if amounts and (len(set(amounts))!=1 or (minimums and max(minimums)>amounts[0])):
        return 'none','full',['quota_missing_or_conflicting']
    if not amounts:
        if minimums and hi is not None and hi<=max(minimums):
            return 'full','full',[]
        return 'none','full',['documented_minimum_does_not_cover_demand'] if minimums else ['quota_missing_or_conflicting']
    amount=amounts[0]
    if amount<lo:
        return 'none','none',[]
    if hi is not None and amount>=hi:
        return 'full','full',[]
    return 'none','full',['demand_interval_straddles_quota_or_has_open_upper_bound']


def lookup_project(kb,candidates,requirements,config,dictionary):
    props={p['id']:p for p in dictionary['properties']}
    result=[]
    for candidate in sorted(candidates,key=lambda c:c['id']):
        assessments=[]
        for req in sorted(requirements,key=lambda r:r['id']):
            prop=props[req['property_id']];asked=req['qualifiers'];accepted=req.get('qualifier_acceptance_sets',{})
            all_claims=sorted((c for c in kb['claims'] if c['scope_id']==candidate['scope_id'] and c['property_id']==req['property_id']),key=lambda c:c['id'])
            claims=[c for c in all_claims if all(key not in c['qualifiers'] or value is None or _matches(c['qualifiers'],key,value,accepted) for key,value in asked.items())]
            conditions=[];cases=[]
            if req.get('domain_gaps'):
                cases=[{'qualifiers':deepcopy(asked),'level_interval':{'min':'none','max':'full'},'claim_ids':[],'unknown_reasons':['coverage_gap']}]
                conditions.append({'type':'coverage_gap','values':deepcopy(req['domain_gaps'])})
            else:
                dimensions=sorted(set(asked)|{key for c in claims for key in c['qualifiers']})
                choices=[]
                for key in dimensions:
                    if asked.get(key) is not None:
                        choices.append([asked[key]])
                    else:
                        finite=req.get('qualifier_domains',{}).get(key)
                        values=sorted(finite) if finite is not None else sorted({c['qualifiers'][key] for c in claims if key in c['qualifiers']})+[None]
                        choices.append(values)
                        conditions.append({'type':'qualifier_unresolved','qualifier':key,'allowed_values':deepcopy(finite),'domain_complete':finite is not None})
                for values in product(*choices):
                    assignment=dict(zip(dimensions,values))
                    complete=[c for c in claims if all(value is not None and _matches(c['qualifiers'],key,value,accepted) for key,value in assignment.items())]
                    reasons=[];low,high='none','full'
                    if not complete:
                        reasons=['no_matching_claim']
                    elif prop['value_type']=='quantity':
                        low,high,reasons=_quota(complete,req)
                    else:
                        levels={c.get('level') for c in complete}
                        if len(levels)==1 and next(iter(levels)) in LEVELS:
                            low=high=next(iter(levels))
                        else:
                            reasons=['claim_level_unknown' if any(x not in LEVELS for x in levels) else 'conflicting_claims']
                    if req.get('status','ready')!='ready':
                        low,high='none','full';reasons.append('requirement_not_ready')
                    cases.append({'qualifiers':assignment,'level_interval':{'min':low,'max':high},'claim_ids':sorted(c['id'] for c in complete),'unknown_reasons':reasons})
            low=min((c['level_interval']['min'] for c in cases),key=LEVELS.index)
            high=max((c['level_interval']['max'] for c in cases),key=LEVELS.index)
            used={cid for c in cases for cid in c['claim_ids']}
            assessments.append({'requirement_id':req['id'],'property_id':req['property_id'],'role':req['role'],'min_level':(req.get('min_level_if_applicable') or config['default_hard_min_level']) if req['role']=='HARD' else None,'level':low if low==high else 'unknown','level_interval':{'min':low,'max':high},'conditions':conditions,'unknown_reasons':sorted({reason for c in cases for reason in c['unknown_reasons']}),'trace':{'requirement_id':req['id'],'scope_id':candidate['scope_id'],'requested_qualifiers':deepcopy(asked),'candidate_bindings':deepcopy(req.get('candidate_bindings',{})),'domain_mapping':deepcopy(req.get('domain_mapping_trace',[])),'claim_ids':sorted(used),'claims':[deepcopy(c) for c in all_claims if c['id'] in used],'cases':cases}})
        result.append({'candidate_id':candidate['id'],'scope_id':candidate['scope_id'],'name':candidate.get('name',candidate['id']),'assessments':assessments})
    return result
