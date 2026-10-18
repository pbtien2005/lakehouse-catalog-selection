"""End-to-end MVP properties; all fixture catalog names are synthetic."""
from copy import deepcopy
import importlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def modules():
    return importlib.import_module('catalog_reasoner.application'), importlib.import_module('catalog_reasoner.project_io')


@pytest.fixture
def data():
    _, io = modules()
    config = io.load_project_config()
    def req(rid, prop, qualifiers, role='HARD'):
        return {'id':rid,'property_id':prop,'qualifiers':qualifiers,'role':role,'status':'ready','min_level_if_applicable':'full'}
    hard = req('H-cloud','deployment.environment',{'environment':'aws_regional_service'})
    soft = req('S-branch','workflow.branching',{'object_scope':'catalog','api':'nessie_api'},'SOFT')
    kb = {'manifest':{'synthetic':True},'scopes':[{'id':f'synthetic_{x}'} for x in 'abc'],'claims':[]}
    for x, level in zip('abc',['full','none','unknown']):
        for suffix, r, value in [('cloud',hard,level),('branch',soft,'none' if x=='a' else 'full')]:
            kb['claims'].append({'id':f'synthetic_{x}_{suffix}','scope_id':f'synthetic_{x}','property_id':r['property_id'],'qualifiers':deepcopy(r['qualifiers']),'level':value})
    doc={'candidates':[{'id':s['id'],'scope_id':s['id']} for s in kb['scopes']],'requirements':[hard],'objectives':[soft],'readiness':'ready_for_assessment'}
    return kb, doc, config


def run(data):
    return modules()[0].run_requirements(*data)


def test_excluded_candidates_never_enter_ranking(data):
    result=run(data)
    assert [c['candidate_id'] for c in result['groups']['excluded']]==['synthetic_b']
    assert 'synthetic_b' not in {r['candidate_id'] for r in result['ranking']}


def test_unknown_never_becomes_unconditional_pass_or_failure(data):
    result=run(data)
    assert [c['candidate_id'] for c in result['groups']['conditional']]==['synthetic_c']
    assert result['groups']['conditional'][0]['hard_conditions'][0]['claim_ids']==['synthetic_c_cloud']


def test_increasing_a_claim_cannot_lower_absolute_score(data):
    before=run(data)
    data[0]['claims'][1]['level']='full'
    after=run(data)
    get=lambda r:next(c['score_interval'] for c in r['ranking'] if c['candidate_id']=='synthetic_a')
    assert all(a>=b for a,b in zip(get(after),get(before)))


def test_seed_order_and_pure_inputs_are_deterministic(data):
    original=deepcopy(data); first=run(data)
    assert run(data)==first and data==original
    data[0]['claims'].reverse();data[1]['candidates'].reverse()
    assert run(data)==first


def test_no_eligible_has_relaxation_trace(data):
    for c in data[0]['claims']:
        if c['property_id']=='deployment.environment':c['level']='none'
    result=run(data)
    assert not result['groups']['eligible'] and result['relaxations']
    assert result['relaxations'][0]['removed_requirement_id']=='H-cloud'


@pytest.mark.parametrize('defect',['unknown_property','unknown_qualifier','partial_binary','bad_quantity','missing_qualifier'])
def test_dictionary_and_rubric_errors_are_not_unknown(data,defect):
    if defect=='unknown_property':data[1]['requirements'][0]['property_id']='not.a.property'
    elif defect=='unknown_qualifier':data[0]['claims'][0]['qualifiers']['typo']='aws'
    elif defect=='partial_binary':data[0]['claims'][0]['level']='partial'
    elif defect=='missing_qualifier':data[1]['requirements'][0]['qualifiers']={}
    else:
        data[0]['claims'].append({'id':'synthetic_bad_quota','scope_id':'synthetic_a','property_id':'limits.quota','qualifiers':{'resource':'tables','boundary':'catalog'},'value':{'amount':-1,'unit':'tables'}})
    with pytest.raises(ValueError):run(data)


def test_readiness_blocks_all_computation(data):
    data[1].update(readiness='needs_input_correction',input_issues=[{'field':'answers.I10','code':'E_RANK_MISSING_OR_INVALID'}])
    result=run(data)
    assert result['status']=='input_error' and result['ranking']==[]
    assert all(not rows for rows in result['groups'].values())
    assert result['config']['reasoning']==data[2]['reasoning']


@pytest.mark.parametrize('amount,upper,boundary,expected',[(200,99,True,'eligible'),(50,99,True,'conditional'),(10,99,True,'excluded'),(200,99,False,'conditional'),(None,99,True,'conditional'),(200,None,True,'conditional')])
def test_quota_only_compares_known_numbers_and_confirmed_boundary(data,amount,upper,boundary,expected):
    kb,doc,_=data
    kb['claims']=[{'id':'synthetic_quota','scope_id':'synthetic_a','property_id':'limits.quota','qualifiers':{'resource':'tables','boundary':'catalog'},'value':None if amount is None else {'amount':amount,'unit':'tables'},'observation_context':{'limit_kind':'fixed'}}]
    doc['candidates']=doc['candidates'][:1]
    doc['requirements']=[{'id':'H-quota','property_id':'limits.quota','qualifiers':{'resource':'tables','boundary':'catalog'},'role':'HARD','operator':'capacity_covers_demand_interval','demand_interval':{'lower':20,'upper':upper},'boundary_confirmed':boundary}]
    doc['objectives']=[]
    assert run(data)['groups'][expected]


def test_missing_weight_is_flagged_not_silently_invented(data):
    row=run(data)['ranking'][0]['score_trace'][0]
    assert row['weight_defaulted'] and row['weight']==data[2]['reasoning']['rank_to_weight']['low']


def test_real_form_runs_all_seven_scopes_without_claim_alias_guessing():
    app,io=modules();config=io.load_project_config();kb=io.load_kb()
    case=json.loads((ROOT/'cases/calibration.json').read_text())['cases'][0]
    payload=deepcopy(case['form_answers']);payload['answers']['I07']='table'
    result=app.run_case(payload,kb,config)
    assert result['status']=='ok' and sum(map(len,result['groups'].values()))==7
    assert result['kb_revision']==kb['manifest']['revision']
    assert any('coverage_gap' in a['unknown_reasons'] for rows in result['groups'].values() for c in rows for a in c['assessments'])


def test_known_aws_mapping_is_explicit_and_does_not_rewrite_kb():
    app,io=modules();config=io.load_project_config();kb=io.load_kb();original=deepcopy(kb)
    result=app.run_case({'form_revision':'input-v2','answers':{'I01':'aws'}},kb,config)
    glue=next(c for rows in result['groups'].values() for c in rows if c['candidate_id']=='aws_glue_data_catalog')
    assert next(a for a in glue['assessments'] if a['property_id']=='deployment.environment')['level']=='full'
    assert kb==original and glue['group']=='conditional'


def test_sampling_is_bounded_seeded_and_regret_is_labeled(data):
    data[2]['reasoning']['max_scenarios']=1
    first=run(data)
    assert first==run(data)
    assert first['scenarios']['scenario_count']<=1
    assert first['scenarios']['mode']=='seeded_sample_with_replacement'
    assert not first['scenarios']['regret_is_exact']
    assert all(r['max_regret_observed']<=r['regret_upper_bound'] for r in first['ranking'])


def test_absolute_scores_do_not_depend_on_competitor_set(data):
    before=run(data)['groups']['eligible'][0]['score_interval']
    data[1]['candidates']=data[1]['candidates'][:1]
    assert run(data)['groups']['eligible'][0]['score_interval']==before


def test_no_soft_objectives_does_not_fabricate_a_winner(data):
    data[1]['objectives']=[]
    result=run(data)
    assert result['scenarios']['status']=='no_soft_objectives'
    assert all(r['score_interval'] is None and r['top_rate'] is None for r in result['ranking'])


def test_ties_split_credit_and_missing_claim_has_no_false_negative(data):
    data[0]['claims']=[c for c in data[0]['claims'] if c['scope_id']!='synthetic_c']
    for c in data[0]['claims']:
        c['level']='full'
    result=run(data)
    assert len(result['groups']['conditional'])==1
    assert result['scenarios']['metrics']
    assert abs(sum(r['top_rate'] for r in result['ranking'])-1)<1e-12
    assert result['unknowns'] and all('requirement_ids' in u for u in result['unknowns'])


@pytest.mark.parametrize('weight',[0,-1,True,float('inf')])
def test_invalid_soft_weight_is_a_boundary_error(data,weight):
    data[1]['objectives'][0]['weight']=weight
    with pytest.raises(ValueError):run(data)


def test_cli_runs_the_official_pipeline_and_reports_json_errors(tmp_path,capsys):
    _,io=modules()
    source=tmp_path/'answers.json';output=tmp_path/'result.json'
    source.write_text(json.dumps({'form_revision':'input-v2','answers':{'I01':'aws'}}))
    assert io.main(['--answers',str(source),'--output',str(output)])==0
    assert json.loads(output.read_text())['inference_executed']
    source.write_text('bad JSON')
    assert io.main(['--answers',str(source)])==2
    assert json.loads(capsys.readouterr().out)['status']=='data_error'


def test_relaxing_a_hard_requirement_cannot_hide_unresolved_user_needs(data):
    for claim in data[0]['claims']:
        if claim['property_id']=='deployment.environment':claim['level']='none'
    data[1]['unresolved']=[{'source_input':'I08','state':'unknown_need','reason':'Synthetic unknown need'}]
    result=run(data)
    assert result['relaxations']
    assert not result['relaxations'][0]['eligible_after_relaxation']
    assert result['relaxations'][0]['conditional_after_relaxation']


def test_api_unknown_has_no_unused_fallback_completion_variable(data):
    data[1]['candidates']=data[1]['candidates'][:1]
    data[1]['objectives'][0]['qualifiers']['api']=None
    result=run(data)
    assert result['scenarios']['total_possible_completions']==6
    assert not any(u['kind']=='uncovered_case' for u in result['unknowns'])


def test_max_scenarios_includes_counterfactual_evaluations(data,monkeypatch):
    module=importlib.import_module('catalog_reasoner.scenarios');original=module._winner;calls=[]
    def counted(*args):
        calls.append(True);return original(*args)
    monkeypatch.setattr(module,'_winner',counted)
    data[2]['reasoning']['max_scenarios']=5
    data[1]['objectives'][0]['qualifiers']['api']=None
    result=run(data)
    assert len(calls)<=5
    assert result['scenarios']['scenario_count']<=5


@pytest.mark.parametrize('document',[[],{'candidates':[],'requirements':[None]}])
def test_layer3_boundary_validates_before_sorting(data,document):
    data=list(data);data[1]=document
    with pytest.raises(ValueError):run(data)
