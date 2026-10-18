"""Absolute weighted sum. Excluded candidates are never ranked."""
from math import isfinite


def soft_weights(requirements,config):
    rows={}
    for r in requirements:
        if r['role']!='SOFT':continue
        defaulted='weight' not in r or r.get('weight_defaulted',False)
        value=r.get('weight',config['rank_to_weight'][r.get('weight_rank',config['default_weight_rank'])])
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not isfinite(value) or value<=0:
            raise ValueError(f"requirements.{r['id']}.weight: must be finite and positive")
        rows[r['id']]={'weight':value,'weight_defaulted':defaulted}
    return rows


def score_candidates(groups,requirements,config):
    weights=soft_weights(requirements,config);total=sum(x['weight'] for x in weights.values())
    ranking=[]
    for group in ['eligible','conditional']:
        for c in groups[group]:
            trace=[]
            for a in c['assessments']:
                if a['role']=='SOFT':
                    trace.append({'requirement_id':a['requirement_id'],**weights[a['requirement_id']],'level_interval':a['level_interval'],'claim_ids':a['trace']['claim_ids']})
            interval=[sum(row['weight']*config['level_to_value'][row['level_interval'][bound]] for row in trace)/total for bound in ['min','max']] if total else None
            c.update(score_interval=interval,score_trace=trace)
            ranking.append({'candidate_id':c['candidate_id'],'group':group,'score_interval':interval,'score_trace':trace})
    return sorted(ranking,key=lambda r:r['candidate_id']),weights
