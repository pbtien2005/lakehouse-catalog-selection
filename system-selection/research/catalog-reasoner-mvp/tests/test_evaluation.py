from copy import deepcopy
import importlib
import json
from pathlib import Path


def test_weight_sensitivity_is_seeded_one_weight_at_a_time():
    module=importlib.import_module('catalog_reasoner.evaluation')
    outcomes=[{'levels':{'synthetic_a':{'s1':'full','s2':'none'},'synthetic_b':{'s1':'none','s2':'full'}},'feasible':{'synthetic_a':True,'synthetic_b':True}}]
    weights={'s1':{'weight':1},'s2':{'weight':1}}
    settings={'sensitivity_fraction':0.3,'sensitivity_iterations':10}
    before=deepcopy((outcomes,weights))
    a=module.weight_sensitivity(outcomes,weights,{'none':0,'partial':0.5,'full':1},settings,42)
    assert a==module.weight_sensitivity(outcomes,weights,{'none':0,'partial':0.5,'full':1},settings,42)
    assert (outcomes,weights)==before
    assert len(a['draws'])==10
    assert all(len(draw['changed_weights'])==1 for draw in a['draws'])
    assert abs(sum(a['top_rates'].values())-1)<1e-12


def test_platform_baseline_has_no_invented_snowflake_catalog():
    module=importlib.import_module('catalog_reasoner.evaluation')
    assert module.platform_baseline({'I09':['snowflake']})['candidate_ids']==[]
    assert module.platform_baseline({'I09':['aws_native']})['candidate_ids']==['aws_glue_data_catalog']


def test_frozen_split_uses_ten_distinct_synthetic_profiles():
    root=Path(__file__).resolve().parents[1]/'cases'
    rows=[json.loads((root/f'{name}.json').read_text()) for name in ['calibration','holdout']]
    assert [len(doc['cases']) for doc in rows]==[6,4]
    assert len({c['id'] for doc in rows for c in doc['cases']})==10
    assert all(c['synthetic_profile'] for doc in rows for c in doc['cases'])


def test_robust_winners_are_computed_from_eligible_interval_bounds():
    module=importlib.import_module('catalog_reasoner.evaluation')
    result={'ranking':[{'candidate_id':'synthetic_a','group':'eligible','score_interval':[1,1]},{'candidate_id':'synthetic_b','group':'conditional','score_interval':[0,0.5]}]}
    assert module.robust_winners(result)==['synthetic_a']
    result['ranking'][0]['score_interval']=[0,1]
    assert module.robust_winners(result)==[]
