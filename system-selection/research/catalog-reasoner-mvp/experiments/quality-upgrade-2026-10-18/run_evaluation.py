"""Reproducible acceptance run for documented paths and synthetic boundaries."""
from copy import deepcopy
import csv
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
sys.path.insert(0,str(PROJECT))
from catalog_reasoner.application import run_case
from catalog_reasoner.project_io import load_kb,load_project_config


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    plan=read(HERE/'evaluation-config.json')
    kb,config=load_kb(),load_project_config()
    frozen=read(PROJECT/'cases/split-manifest.json')
    for split in ['calibration','holdout']:
        assert sha(PROJECT/f'cases/{split}.json')==frozen['sha256'][split],f'Frozen {split} changed'
    out=HERE/'results';out.mkdir(exist_ok=True)
    forms=HERE/'forms';forms.mkdir(exist_ok=True)
    summary=[];checks=[];all_claim_ids={c['id'] for c in kb['claims']}|{c['id'] for c in config['evidence_overlay']['claims']}
    protected=[PROJECT/'config.json',PROJECT/'mvp-settings.json',PROJECT.parent/'catalog-knowledge-base/layer-1-data.json',PROJECT/'cases/calibration.json',PROJECT/'cases/holdout.json']
    before={str(p.relative_to(PROJECT.parent)):sha(p) for p in protected}
    for case in plan['cases']:
        base=plan['base_cases'][case['base']]
        payload=read(HERE/base['source_form']);payload['form_revision']='input-v3'
        payload['answers'].update(deepcopy(base['additional_facts']))
        payload['answers'].update(deepcopy(case.get('answer_overrides',{})))
        if not case.get('omit_exact'):
            payload['context']={'table_count_exact':case.get('exact_override',base['exact_count']['value'])}
        write(forms/(case['id']+'.json'),payload)
        result=run_case(payload,kb,config)
        for _ in range(1,plan['verification_repeats']):assert result==run_case(payload,kb,config),case['id']+' determinism'
        expected=case.get('expected_status','ok');assert result['status']==expected,(case['id'],result.get('input_issues'))
        row={'case_id':case['id'],'kind':case['kind'],'status':result['status'],'groups':{g:len(c) for g,c in result['groups'].items()},'reference_candidate':base['reference_candidate']}
        if expected=='ok':
            candidate=next(c for rows in result['groups'].values() for c in rows if c['candidate_id']==base['reference_candidate'])
            assert candidate['group']==case['expected_group'],(case['id'],candidate['hard_conditions'],candidate.get('input_conditions'))
            assert candidate['functional_summary']['status']==case['expected_functional'],case['id']
            if 'expected_score_interval' in case:assert candidate['score_interval']==case['expected_score_interval']
            rows=result['requirements']['requirements']+result['requirements']['objectives'];rids={r['id'] for r in rows}
            for group,candidates in result['groups'].items():
                for c in candidates:
                    for a in c['assessments']:
                        assert a['requirement_id'] in rids
                        assert set(a['trace']['claim_ids'])<=all_claim_ids
                    if group=='eligible':assert not c['hard_conditions'] and not c.get('input_conditions')
            row.update(reference_group=candidate['group'],profile=candidate.get('selected_profile_id'),functional_status=candidate['functional_summary']['status'],hard_passes=len(candidate['hard_passes']),hard_conditions=len(candidate['hard_conditions']),hard_failures=len(candidate['hard_failures']),score_interval=candidate['score_interval'],top_rate=candidate['top_rate'],remaining_input_conditions=candidate.get('input_conditions',[]))
        else:
            assert not result['inference_executed']
            row['input_issues']=result['input_issues']
        write(out/(case['id']+'.json'),result)
        write(out/(case['id']+'.requirements.json'),result['requirements'])
        summary.append(row);checks.append({'case_id':case['id'],'status':'pass','expected_status':expected,'same_seed_full_json_equal':True})
    after={str(p.relative_to(PROJECT.parent)):sha(p) for p in protected};assert before==after
    write(out/'summary.json',summary)
    with (out/'summary.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        keys=['case_id','kind','status','reference_candidate','reference_group','profile','functional_status','hard_passes','hard_conditions','hard_failures','score_interval','top_rate','groups']
        writer=csv.DictWriter(stream,fieldnames=keys,extrasaction='ignore');writer.writeheader()
        for row in summary:writer.writerow({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in row.items()})
    write(out/'verification.json',{'status':'pass','date':plan['review_date'],'checks':checks,'original_kb_weights_config_frozen_inputs_unchanged':True,'protected_before':before,'protected_after':after,'config':{'evaluation':plan,'reasoning':config['reasoning'],'settings':config['settings'],'quality_policy':config['quality_policy']},'knowledge_asset_hashes':config['knowledge_asset_hashes'],'scope':'documented design feasibility; not infrastructure execution, external expert validation or an independent holdout','result_sha256':{p.name:sha(p) for p in sorted(out.glob('*.json')) if p.name!='verification.json'}})
    for row in summary:print(json.dumps({k:row[k] for k in ['case_id','status','groups','reference_candidate']},ensure_ascii=True))


if __name__=='__main__':main()
