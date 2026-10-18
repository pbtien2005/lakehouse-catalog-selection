"""Only jointly evidenced implementations enter v3 scenario comparisons."""
from copy import deepcopy

import pytest

from catalog_reasoner.evidence_scenarios import explore_evidenced_scenarios
from catalog_reasoner.project_io import load_project_config


def inputs():
    config=load_project_config()
    candidates=[{'candidate_id':cid,'group':'eligible','selected_profile_id':'synthetic_profile_'+cid,'assessments':[]} for cid in ['synthetic_a','synthetic_b']]
    return {'eligible':candidates,'conditional':[],'excluded':[]},{'synthetic_soft':{'weight':1}},config


def run(data):
    groups,weights,config=data
    return explore_evidenced_scenarios(groups,weights,config['reasoning'],config['dictionary'],config['settings'],config['quality_policy'])


def test_comparison_keeps_two_whole_profiles_and_is_pure():
    data=inputs();before=deepcopy(data)
    result=run(data)
    assert result['status']=='completed'
    assert result['comparison_candidate_ids']==['synthetic_a','synthetic_b']
    assert all(row['top_rate']==.5 for row in result['metrics'])
    assert data==before


@pytest.mark.parametrize('missing',['profile','user_context','unbound_design'])
def test_unverified_candidate_has_no_hypothetical_joint_feasibility(missing):
    data=inputs();candidate=data[0]['eligible'][1]
    if missing=='profile':candidate['selected_profile_id']=None
    elif missing=='user_context':candidate['input_conditions']=[{'source_input':'I12','state':'unknown_operations'}]
    else:candidate['assessments']=[{'requirement_id':'synthetic_hard','trace':{'requested_qualifiers':{'api':None},'cases':[{'qualifiers':{'api':None}}]}}]
    result=run(data)
    assert result['status']=='insufficient_verified_implementations_for_comparison'
    assert result['comparison_candidate_ids']==['synthetic_a']
    assert result['candidates_not_compared'][0]['candidate_id']=='synthetic_b'
    assert all(row['top_rate'] is None and row['feasible_rate'] is None for row in result['metrics'])
    assert all(not row['leaders'] for row in result['outcomes'])


def test_no_verified_candidates_and_no_soft_do_not_crash_or_invent_a_ranking():
    data=inputs();data[1].clear()
    for candidate in data[0]['eligible']:candidate['selected_profile_id']=None
    result=run(data)
    assert result['status']=='no_soft_objectives' and result['comparison_candidate_ids']==[]
    assert all(row['top_rate'] is None for row in result['metrics'])


@pytest.mark.parametrize('minimum',[0,True,-1])
def test_invalid_quality_policy_is_a_boundary_error(minimum):
    data=inputs();data[2]['quality_policy']['min_comparison_candidates']=minimum
    with pytest.raises(ValueError):run(data)


def test_unsupported_comparison_scope_is_a_boundary_error():
    data=inputs();data[2]['quality_policy']['comparison_scope']='independently_mix_any_path'
    with pytest.raises(ValueError):run(data)
