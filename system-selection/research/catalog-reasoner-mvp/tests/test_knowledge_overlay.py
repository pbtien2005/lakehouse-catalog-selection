"""Source overlays cannot overwrite known claims or lose provenance."""
from copy import deepcopy

import pytest

from catalog_reasoner.knowledge import extend_value_mapping, merge_knowledge


def example():
    old = {'id':'old_unknown','scope_id':'synthetic_scope','property_id':'limits.quota','qualifiers':{'resource':'tables','boundary':'catalog'},'value':None}
    new = {**deepcopy(old),'id':'new_minimum','value':{'amount':1,'unit':'tables'},'supersedes_claim_ids':['old_unknown'],'evidence':[{'url':'https://example.org/official','locator':'Synthetic test evidence only'}]}
    return {'manifest':{'revision':'synthetic_original'},'scopes':[{'id':'synthetic_scope'}],'claims':[old]}, {'manifest':{'revision':'synthetic_extension'},'claims':[new]}


def test_only_unknown_placeholder_is_superseded_and_history_is_preserved():
    kb, extension = example(); original = deepcopy(kb)
    result = merge_knowledge(kb, extension)
    assert kb == original
    assert [c['id'] for c in result['claims']] == ['new_minimum']
    assert result['manifest']['knowledge_extensions'][0]['superseded_unknown_claim_ids'] == ['old_unknown']
    assert result['manifest']['base_revision'] == 'synthetic_original'


@pytest.mark.parametrize('defect',['duplicate','unknown_scope','missing_evidence','insecure_source','wrong_superseded','known_value','known_level','wrong_fact'])
def test_overlay_invalid_or_conflict_hiding_claims_fail_closed(defect):
    kb, extension = example(); claim=extension['claims'][0]
    if defect=='duplicate':claim['id']='old_unknown'
    elif defect=='unknown_scope':claim['scope_id']='other'
    elif defect=='missing_evidence':claim['evidence']=[]
    elif defect=='insecure_source':claim['evidence'][0]['url']='http://example.org/official'
    elif defect=='wrong_superseded':claim['supersedes_claim_ids']=['does_not_exist']
    elif defect=='known_value':kb['claims'][0]['value']={'amount':2,'unit':'tables'}
    elif defect=='known_level':kb['claims'][0]['level']='none'
    elif defect=='wrong_fact':claim['qualifiers']['boundary']='account'
    with pytest.raises(ValueError):merge_knowledge(kb,extension)


def test_exact_identifiers_do_not_invent_aliases_and_curated_relations_are_explicit():
    kb,_=example()
    mapping={'manifest':{'revision':'synthetic_mapping'},'rows':[]}
    reviewed=[{'id':'synthetic_alias','property_id':'limits.quota','qualifier':'resource','input_value':'table_count','accepted_kb_values':['tables']}]
    result=extend_value_mapping(mapping,kb,reviewed)
    rows={(r['property_id'],r['qualifier'],r['input_value']):r for r in result['rows']}
    assert rows[('limits.quota','resource','table_count')]['accepted_kb_values']==['tables']
    assert rows[('limits.quota','resource','tables')]['accepted_kb_values']==['tables']
    assert not any(key[-1]=='database' for key in rows)
    assert mapping['rows']==[]
