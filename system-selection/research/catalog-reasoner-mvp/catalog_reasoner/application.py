"""Official pure form -> mapping -> validation -> four-step inference."""
from copy import deepcopy
from itertools import combinations

from .contracts import assumptions_used,requirement_rows,validate_inputs
from .domains import translate_document,validate_semantics
from .hard_filter import filter_hard
from .layer2 import normalize_form
from .project_lookup import lookup_project
from .scenarios import explore_scenarios
from .scoring import score_candidates


def run_requirements(kb,document,config):
    document=deepcopy(document)
    reasoning=config['reasoning'];dictionary=config['dictionary']
    if not isinstance(document,dict):
        validate_inputs(kb,document,reasoning)
    empty={key:[] for key in ['eligible','conditional','excluded']}
    if document.get('readiness')=='needs_input_correction':
        return {'status':'input_error','groups':empty,'ranking':[],'input_issues':deepcopy(document.get('input_issues',[])),'requirements':deepcopy(document),'assumptions':deepcopy(document.get('assumptions',[])),'config':{'reasoning':deepcopy(reasoning),'layer2':deepcopy(config['layer2']['config']),'settings':deepcopy(config['settings'])},'inference_executed':False}
    validate_inputs(kb,document,reasoning)
    validate_semantics(kb,document,dictionary)
    for key in ['candidates','requirements','objectives']:
        if key in document:document[key].sort(key=lambda row:row['id'])
    rows=requirement_rows(document)
    path_mode=document.get('revisions',{}).get('form')=='input-v3'
    if path_mode:
        from .path_resolution import resolve_and_lookup
        lookups=resolve_and_lookup(kb,document['candidates'],rows,reasoning,dictionary,config['implementation_profiles'],document.get('implementation_context',{}))
    else:
        lookups=lookup_project(kb,document['candidates'],rows,reasoning,dictionary)
    unresolved=deepcopy(document.get('unresolved',[]))
    if unresolved:
        for c in lookups:
            c.setdefault('input_conditions',[]).extend({'input_ref':f"U-{i}",**u,'reason':'unresolved_form_input_not_assumed_unneeded','claim_ids':[]} for i,u in enumerate(unresolved))
            if c.get('functional_summary'):
                c['functional_summary']['input_conditions']=deepcopy(c['input_conditions'])
                if c['functional_summary']['status']=='eligible':c['functional_summary']['status']='conditional'
    filtered=filter_hard(lookups)
    ranking,weights=score_candidates(filtered['groups'],rows,reasoning)
    if path_mode:
        from .evidence_scenarios import explore_evidenced_scenarios
        scenarios=explore_evidenced_scenarios(filtered['groups'],weights,reasoning,dictionary,config['settings'],config['quality_policy'])
    else:scenarios=explore_scenarios(filtered['groups'],weights,reasoning,dictionary,config['settings'])
    metrics={m['candidate_id']:m for m in scenarios['metrics']}
    for c in ranking:
        c.update(metrics[c['candidate_id']]);c['top_rate_interpretation']='completion_fraction_within_evidenced_joint_profiles_only_not_all_catalogs' if path_mode else 'completion_scenario_fraction_not_probability_of_real_world_suitability'
    for group in ['eligible','conditional']:
        for c in filtered['groups'][group]:c.update(metrics[c['candidate_id']])
    overlaps=[{'candidate_ids':[a['candidate_id'],b['candidate_id']],'interval':[max(a['score_interval'][0],b['score_interval'][0]),min(a['score_interval'][1],b['score_interval'][1])],'requirement_ids':sorted(weights),'claim_ids':sorted({cid for r in a['score_trace']+b['score_trace'] for cid in r['claim_ids']})} for a,b in combinations(ranking,2) if a['score_interval'] is not None and b['score_interval'] is not None and max(a['score_interval'][0],b['score_interval'][0])<=min(a['score_interval'][1],b['score_interval'][1])]
    assumptions=deepcopy(document.get('assumptions',[]))+assumptions_used(document,reasoning)
    assumptions.append({'parameter':'mvp_settings','value':deepcopy(config['settings']),'assumption':True})
    if path_mode:assumptions.append({'parameter':'quality_policy','value':deepcopy(config['quality_policy']),'assumption':True})
    assumptions.extend({'parameter':f"weight.{rid}",**row,'assumption':True} for rid,row in weights.items() if row['weight_defaulted'])
    return {'status':'ok','inference_executed':True,'stage':'1-4','synthetic_data':kb.get('manifest',{}).get('synthetic',False),'kb_revision':kb.get('manifest',{}).get('revision'),**filtered,'ranking':ranking,'score_overlaps':overlaps,'scenarios':scenarios,'unknowns':scenarios['unknowns'],'unresolved_inputs':unresolved,'assumptions':assumptions,'profile_assumptions':deepcopy(document.get('profile_assumptions',{})),'requirements':deepcopy(document),'config':{'reasoning':deepcopy(reasoning),'layer2':deepcopy(config['layer2']['config']),'settings':deepcopy(config['settings'])},'limits':['KB source review does not establish that the proposed infrastructure has been deployed or independently tested.','Metrics concern one selected intact implementation profile per candidate; alternative profiles are not mixed or optimized by scenario.' if path_mode else 'Candidate bindings are trace only; no joint path resolver.','Scenario fractions are completions under explicit assumptions, not calibrated real-world probabilities.','Sampled regret is an observed lower bound; the reported upper bound is conservative.','Unresolved form needs keep conclusions conditional and are not automatically scored.']}


def run_case(form_answers,kb,config):
    """No I/O, no LLM, no clock; fixed inputs and seed give fixed JSON."""
    is_v3=isinstance(form_answers,dict) and form_answers.get('form_revision')=='input-v3'
    if is_v3:
        from .intake_v3 import normalize_form_v3
        from .knowledge import merge_knowledge,extend_value_mapping
        if not config.get('evidence_overlay') or not config.get('implementation_profiles'):
            raise ValueError('Form v3 requires versioned evidence overlay and implementation profiles.')
        kb=merge_knowledge(kb,config['evidence_overlay'])
        value_mapping=extend_value_mapping(config['value_mapping'],kb,config.get('value_mapping_v3_rows',{}).get('rows',[]))
    else:value_mapping=config['value_mapping']
    assets={**config['layer2'],'kb':kb,'reasoning_config':config['reasoning']}
    document=normalize_form_v3(form_answers,assets) if is_v3 else normalize_form(form_answers,assets)
    if is_v3:
        context=document['normalized_context']
        for requirement in document['requirements']:
            if requirement['property_id']=='security.authorization':
                engine=next((e for e in context.get('I02',[]) if requirement['id'].endswith('-'+e)),None)
                if engine:requirement['qualifiers'].update(engine=engine,format=context.get('I03') if context.get('I03') in {'iceberg','delta','hudi'} else None)
    if document['readiness']!='needs_input_correction':
        document=translate_document(document,value_mapping)
        if is_v3:
            context=document['normalized_context']
            storage=context.get('I11')
            document['implementation_context']={'environment':None if context.get('I01')=='multi_cloud' else context.get('I01'),'format':context.get('I03') if context.get('I03') in {'iceberg','delta','hudi'} else None,'storage':None if storage=='unknown' else {'s3':'aws_s3','local_fs':'local_filesystem','adls_gen2':'azure_adls_gen2'}.get(storage,storage),'engines':context.get('I02',[]),'operations':sorted({op for ops in context.get('I12',{}).values() for op in ops if op!='unknown'})}
            document['assessment_limits'].update(candidate_bindings_execution='joint_evidenced_profile',joint_path_resolution='one_intact_profile_per_candidate')
    result=run_requirements(kb,document,config)
    result['input_revisions']=deepcopy(document['revisions'])
    result['input_revisions']['value_mapping']=value_mapping['manifest']['revision']
    if is_v3:
        result['config']['quality_policy']=deepcopy(config['quality_policy'])
        result['knowledge_extensions']=deepcopy(kb['manifest']['knowledge_extensions'])
        result['implementation_profile_revision']=config['implementation_profiles'].get('manifest',{}).get('revision')
        result['knowledge_asset_hashes']=deepcopy(config.get('knowledge_asset_hashes',{}))
        result['decision_summary']={'documented_fit_candidate_ids':[c['candidate_id'] for c in result['groups']['eligible']],'conditional_candidate_ids':[c['candidate_id'] for c in result['groups']['conditional']],'basis':'documented_design_feasibility_for_selected_profile','no_soft_ranking':not bool(document['objectives']),'portfolio_complete':False,'not_a_unique_optimum_or_deployment_certificate':True}
    return result
