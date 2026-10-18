"""Finite completions with seeded sampling, tie splitting and observed regret."""
from itertools import product
from math import prod
from random import Random

from .contracts import LEVELS


def _dimension_id(cid,a,key):
    if key in {'format','storage'}:
        return f"context:{key}"
    return f"qualifier:{cid}:{a['requirement_id']}:{key}"


def _winner(levels,feasible,weights,values):
    total=sum(r['weight'] for r in weights.values())
    scores={cid:sum(weights[rid]['weight']*values[level] for rid,level in rows.items() if rid in weights)/total for cid,rows in levels.items() if feasible[cid]} if total else {}
    leaders=sorted(cid for cid,score in scores.items() if score==max(scores.values())) if scores else []
    return scores,leaders


def explore_scenarios(groups,weights,config,dictionary,settings):
    candidates=sorted(groups['eligible']+groups['conditional'],key=lambda c:c['candidate_id'])
    props={p['id']:p for p in dictionary['properties']}
    domains={};metadata={};plans={}
    for c in candidates:
        cid=c['candidate_id'];plans[cid]=[]
        for a in c['assessments']:
            cases=a['trace']['cases'];dims={}
            for key in sorted({k for case in cases for k in case['qualifiers']}):
                if a['trace']['requested_qualifiers'].get(key) is not None:continue
                vid=_dimension_id(cid,a,key);dims[key]=vid
                domains.setdefault(vid,set()).update(case['qualifiers'].get(key) for case in cases)
                metadata.setdefault(vid,{'id':vid,'kind':'qualifier','requirement_ids':set(),'claim_ids':set()})
                metadata[vid]['requirement_ids'].add(a['requirement_id']);metadata[vid]['claim_ids'].update(a['trace']['claim_ids'])
            cell_ids=[]
            prop=props[a['property_id']]
            rubric=dictionary['rubrics'][prop['rubric_ref']]['ordered_levels'] if prop['value_type']=='support' else ['none','full']
            for index,case in enumerate(cases):
                lo,hi=case['level_interval']['min'],case['level_interval']['max']
                if lo==hi:cell_ids.append(None);continue
                vid=f"support:{cid}:{a['requirement_id']}:{index}"
                domains[vid]=set(level for level in rubric if LEVELS.index(lo)<=LEVELS.index(level)<=LEVELS.index(hi))
                metadata[vid]={'id':vid,'kind':'support','requirement_ids':{a['requirement_id']},'claim_ids':set(case['claim_ids'])}
                cell_ids.append(vid)
            fallback=f"uncovered:{cid}:{a['requirement_id']}"
            # A shared format/storage can take a value not observed for this scope.
            if any(vid.startswith('context:') for vid in dims.values()):
                domains[fallback]=set(rubric)
                metadata[fallback]={'id':fallback,'kind':'uncovered_case','requirement_ids':{a['requirement_id']},'claim_ids':set()}
            plans[cid].append((a,dims,cell_ids,fallback))
    ordered={vid:sorted(values,key=lambda x:(x is None,str(x))) for vid,values in sorted(domains.items()) if len(values)>1}
    fixed={vid:next(iter(values)) for vid,values in domains.items() if len(values)==1}
    variable_ids=list(ordered);total=prod(len(v) for v in ordered.values())
    cap=config['max_scenarios'];rng=Random(config['seed']);exact=total<=cap
    pairs=[]
    if exact:
        assignments=[dict(zip(variable_ids,values)) for values in product(*ordered.values())]
    else:
        fraction=settings['scenario_policy']['impact_budget_fraction']
        if not isinstance(fraction,(int,float)) or isinstance(fraction,bool) or not 0<=fraction<1:
            raise ValueError('scenario_policy.impact_budget_fraction must be in [0,1)')
        base_count=max(1,cap-int(cap*fraction))
        assignments=[{vid:rng.choice(values) for vid,values in ordered.items()} for _ in range(base_count)]
        for step in range(cap-base_count):
            vid=variable_ids[step%len(variable_ids)];base_index=step%base_count
            base=assignments[base_index];values=ordered[vid]
            changed={**base,vid:values[(values.index(base[vid])+1)%len(values)]}
            pairs.append((vid,base_index,len(assignments)));assignments.append(changed)

    def evaluate(assignment):
        selected={**fixed,**assignment};levels={};feasible={}
        for cid,rows in plans.items():
            levels[cid]={};feasible[cid]=True
            for a,dims,cell_ids,fallback in rows:
                cases=a['trace']['cases'];index=next((i for i,case in enumerate(cases) if all(case['qualifiers'].get(key)==selected[vid] for key,vid in dims.items())),None)
                if index is None:
                    level=selected[fallback]
                else:
                    level=selected[cell_ids[index]] if cell_ids[index] else cases[index]['level_interval']['min']
                levels[cid][a['requirement_id']]=level
                if a['role']=='HARD' and LEVELS.index(level)<LEVELS.index(a['min_level']):feasible[cid]=False
        scores,leaders=_winner(levels,feasible,weights,config['level_to_value'])
        return {'levels':levels,'feasible':feasible,'scores':scores,'leaders':leaders}

    outcomes=[evaluate(a) for a in assignments]
    records={c['candidate_id']:{'candidate_id':c['candidate_id'],'top_rate':None if not weights else 0,'feasible_rate':0,'max_regret_observed':None if not weights else 0,'regret_upper_bound':None if not weights else config['level_to_value']['full']-config['level_to_value']['none']} for c in candidates}
    for outcome in outcomes:
        best=max(outcome['scores'].values(),default=settings['scenario_policy']['infeasible_utility'])
        for cid,row in records.items():
            row['feasible_rate']+=int(outcome['feasible'][cid])/len(outcomes)
            if weights:
                if cid in outcome['leaders']:row['top_rate']+=1/(len(outcome['leaders'])*len(outcomes))
                utility=outcome['scores'].get(cid,settings['scenario_policy']['infeasible_utility'])
                row['max_regret_observed']=max(row['max_regret_observed'],best-utility)
    # Paired interventions hold all other variables fixed. Probe budget is explicit.
    probes={vid:{'changes':0,'evaluations':0} for vid in variable_ids};used=0
    if weights:
        if exact:
            index_by_assignment={tuple(a[vid] for vid in variable_ids):i for i,a in enumerate(assignments)}
            for step in range(cap):
                if not variable_ids:break
                vid=variable_ids[step%len(variable_ids)];base_index=(step//len(variable_ids))%len(assignments)
                base=assignments[base_index];values=ordered[vid]
                changed={**base,vid:values[(values.index(base[vid])+1)%len(values)]}
                pairs.append((vid,base_index,index_by_assignment[tuple(changed[key] for key in variable_ids)]))
        for vid,base_index,changed_index in pairs:
            different=outcomes[changed_index]['leaders']!=outcomes[base_index]['leaders']
            probes[vid]['changes']+=int(different);probes[vid]['evaluations']+=1;used+=1
    unknowns=[]
    for vid in variable_ids:
        meta=metadata[vid];n=probes[vid]['evaluations']
        unknowns.append({**meta,'requirement_ids':sorted(meta['requirement_ids']),'claim_ids':sorted(meta['claim_ids']),'domain':ordered[vid],'winner_change_rate':probes[vid]['changes']/n if n else None,'paired_probes':n})
    unknowns.sort(key=lambda r:(r['winner_change_rate'] is None,-(r['winner_change_rate'] or 0),r['id']))
    return {'status':'completed' if weights else 'no_soft_objectives','mode':'exhaustive' if exact else 'seeded_sample_with_replacement','total_possible_completions':total,'scenario_count':len(outcomes),'counterfactual_comparisons':used,'counterfactual_evaluations':0 if exact else len(pairs),'counterfactuals_included_in_scenario_count':True,'regret_is_exact':exact,'max_regret_is_observed_lower_bound':not exact,'no_feasible_rate':sum(not any(o['feasible'].values()) for o in outcomes)/len(outcomes),'metrics':list(records.values()),'unknowns':unknowns,'outcomes':outcomes,'policy':settings['scenario_policy']}
