"""Guard scenario comparisons against unverified combinations of API paths."""
from copy import deepcopy

from .path_resolution import DESIGN_QUALIFIERS
from .scenarios import explore_scenarios


def explore_evidenced_scenarios(groups, weights, config, dictionary, settings, policy):
    minimum=policy['min_comparison_candidates']
    if type(minimum) is not int or minimum<1 or policy.get('parameter_metadata',{}).get('min_comparison_candidates',{}).get('assumption') is not True:
        raise ValueError('quality_policy.min_comparison_candidates must be a positive integer marked assumption')
    if policy.get('comparison_scope')!='evidenced_joint_profiles_with_resolved_user_context':
        raise ValueError('quality_policy.comparison_scope is unsupported')
    included={'eligible':[],'conditional':[],'excluded':[]};omitted=[]
    candidates=sorted(groups['eligible']+groups['conditional'],key=lambda c:c['candidate_id'])
    for candidate in candidates:
        reasons=[]
        if not candidate.get('selected_profile_id'):reasons.append('joint_implementation_unverified')
        if candidate.get('input_conditions'):reasons.append('unresolved_user_context')
        for assessment in candidate['assessments']:
            asked=assessment['trace']['requested_qualifiers']
            keys={key for case in assessment['trace']['cases'] for key in case['qualifiers']}
            if any(asked.get(key) is None for key in keys & DESIGN_QUALIFIERS):
                reasons.append('unbound_design_choice:'+assessment['requirement_id'])
        if reasons:omitted.append({'candidate_id':candidate['candidate_id'],'reasons':sorted(set(reasons))})
        else:included[candidate['group']].append(candidate)
    result=explore_scenarios(included,weights,config,dictionary,settings)
    compared=sorted(c['candidate_id'] for rows in included.values() for c in rows)
    enough=len(compared)>=minimum
    unavailable={'top_rate':None,'feasible_rate':None,'max_regret_observed':None,'regret_upper_bound':None}
    metrics={row['candidate_id']:row for row in result['metrics']}
    for candidate in candidates:
        cid=candidate['candidate_id']
        if cid not in metrics:
            metrics[cid]={'candidate_id':cid,**unavailable,'metric_status':'unverified_joint_implementation_or_context'}
        elif not enough:
            metrics[cid].update(unavailable,metric_status='insufficient_verified_implementations_for_comparison')
        else:metrics[cid]['metric_status']='comparison_within_evidenced_implementations_only'
    if not enough:
        if weights:result['status']='insufficient_verified_implementations_for_comparison'
        result['no_feasible_rate']=None
        for outcome in result['outcomes']:
            outcome['scores']={};outcome['leaders']=[]
        for unknown in result['unknowns']:
            unknown.update(winner_change_rate=None,paired_probes=0)
    result.update(metrics=[metrics[k] for k in sorted(metrics)],comparison_scope=policy['comparison_scope'],comparison_candidate_ids=compared,candidates_not_compared=omitted,quality_policy=deepcopy(policy),portfolio_complete=False)
    return result
