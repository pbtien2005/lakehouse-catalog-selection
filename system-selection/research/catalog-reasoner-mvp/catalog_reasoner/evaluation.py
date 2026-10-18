"""Reproducible evaluation, frozen splits, official perturbations and blind sheets."""
from copy import deepcopy
import csv
import hashlib
from html import escape
import json
from pathlib import Path
from random import Random

from .application import run_case,run_requirements
from .project_io import ROOT,load_kb,load_project_config
from .scenarios import _winner
from .scoring import soft_weights
from .contracts import requirement_rows


def platform_baseline(answers):
    bindings={'databricks':'unity_catalog_databricks','aws_native':'aws_glue_data_catalog'}
    platforms=answers.get('I09',[])
    return {'candidate_ids':sorted({bindings[p] for p in platforms if p in bindings}),'unmapped_platforms':[p for p in platforms if p not in bindings and p!='none'],'policy':'Only explicit platform association; no invented Snowflake candidate.'}


def weight_sensitivity(outcomes,weights,values,settings,seed):
    if not weights:return {'status':'not_applicable_no_soft_objectives','draws':[],'top_rates':{}}
    rng=Random(seed);draws=[];top_rates={cid:0 for cid in outcomes[0]['levels']}
    ids=sorted(weights);fraction=settings['sensitivity_fraction'];n=settings['sensitivity_iterations']
    for i in range(n):
        rid=ids[i%len(ids)];factor=rng.uniform(1-fraction,1+fraction)
        changed={key:{**row,'weight':row['weight']*(factor if key==rid else 1)} for key,row in weights.items()}
        rates={cid:0 for cid in top_rates}
        for outcome in outcomes:
            _,leaders=_winner(outcome['levels'],outcome['feasible'],changed,values)
            for cid in leaders:rates[cid]+=1/(len(leaders)*len(outcomes))
        for cid,value in rates.items():top_rates[cid]+=value/n
        draws.append({'changed_weights':{rid:changed[rid]['weight']},'factor':factor,'top_rates':rates})
    return {'status':'completed','seed':seed,'iterations':n,'fraction':fraction,'method':'one_weight_at_a_time;fixed_common_completion_scenarios','top_rates':top_rates,'draws':draws}


def _leaders(result):
    rows=[r for r in result.get('ranking',[]) if r.get('top_rate') is not None]
    best=max((r['top_rate'] for r in rows),default=0)
    return sorted(r['candidate_id'] for r in rows if best>0 and r['top_rate']==best)


def robust_winners(result):
    rows=[r for r in result.get('ranking',[]) if r.get('score_interval') is not None]
    return sorted(r['candidate_id'] for r in rows if r['group']=='eligible' and all(r['score_interval'][0]>=other['score_interval'][1] for other in rows if other['candidate_id']!=r['candidate_id']))


def _count_baseline(result):
    rows=result['groups']['eligible']+result['groups']['conditional']
    counts={c['candidate_id']:sum(a['level']=='full' for a in c['assessments']) for c in rows}
    best=max(counts.values(),default=0)
    return {'candidate_ids':sorted(cid for cid,count in counts.items() if count==best),'counts':counts,'policy':'Count confirmed full only, HARD and SOFT; excluded remain excluded. Unknown earns no confirmed achievement.'}


def _decision_signature(result):
    return {'status':result['status'],'groups':{g:[c['candidate_id'] for c in rows] for g,rows in result['groups'].items()},'ranking':[{key:r.get(key) for key in ['candidate_id','score_interval','top_rate','max_regret_observed']} for r in result['ranking']]}


def _evidence_signature(result):
    return [(c['candidate_id'],[(a['requirement_id'],a['level'],a['level_interval'],a['trace']['claim_ids']) for a in c['assessments']]) for rows in result['groups'].values() for c in rows]


def perturb_form(base,kb,config):
    baseline=run_case(base,kb,config);rows=[]
    for q in config['layer2']['registry']['questions']:
        for answer in q['answers']:
            ranks=['mandatory','nice_to_have'] if q['control']=='features' and answer['id']!='none' else [None]
            for rank in ranks:
                value=answer['id']
                if q['control']=='multi':value=[value]
                elif q['control']=='features':value={'none':True,'selected':[]} if value=='none' else {'selected':[{'feature':value,'rank':rank}]}
                payload=deepcopy(base);payload['answers'][q['id']]=value
                result=run_case(payload,kb,config)
                rows.append({'question':q['id'],'answer':answer['id'],'rank':rank,'ui_enabled':q['enabled'],'decision_changed':_decision_signature(result)!=_decision_signature(baseline),'evidence_changed':_evidence_signature(result)!=_evidence_signature(baseline),'scenario_leaders':_leaders(result),'groups':{g:len(v) for g,v in result['groups'].items()},'input_issues':result.get('input_issues',[])})
    return {'baseline':base,'scope':'official form -> Layer 2 -> strict Python Layer 3; decision signature excludes echoed inputs, assumptions and traces; evidence changes tracked separately','rows':rows,'questions':{q['id']:{'any_decision_changed':any(r['decision_changed'] for r in rows if r['question']==q['id']),'any_evidence_changed':any(r['evidence_changed'] for r in rows if r['question']==q['id']),'ui_enabled':q['enabled']} for q in config['layer2']['registry']['questions']}}


def _blind_sheet(cases,config):
    registry={q['id']:q for q in config['layer2']['registry']['questions']}
    names=sorted((c['name'] for c in config['layer2']['kb']['scopes']))
    pages=[]
    for case in cases:
        answers=[]
        for qid,value in case['form_answers']['answers'].items():
            answers.append(f"<li>{escape(registry[qid]['label'])}: {escape(json.dumps(value,ensure_ascii=False))}</li>")
        ranks=''.join(f'<tr><td>{escape(name)}</td><td>____</td><td>____________________________</td></tr>' for name in names)
        pages.append(f'<section><h1>{escape(case["id"])} · DỮ LIỆU TỔNG HỢP</h1><p>{escape(case["description"])}</p><ul>{"".join(answers)}</ul><p>Phạm vi chung: đọc dữ liệu/load metadata; số bảng trong một catalog; concurrent append; branching catalog; atomic publication metadata.</p><table><thead><tr><th>Ứng viên</th><th>Hạng</th><th>Lý do / chưa đủ thông tin</th></tr></thead><tbody>{ranks}</tbody></table><p>Độ tự tin: ____ · Thông tin cần hỏi thêm: ______________________</p><p>Nhận xét: __________________________________________________</p></section>')
    return '<!doctype html><html lang="vi"><meta charset="utf-8"><title>Phiếu chuyên gia — không kèm kết quả hệ thống</title><style>@page{size:A4;margin:16mm}body{font:11pt Arial;line-height:1.35}h1{font-size:15pt}section{break-after:page}section:last-child{break-after:auto}table{border-collapse:collapse;width:100%}td,th{border:1px solid #aaa;padding:7px;text-align:left}li{margin:3px 0}</style>'+''.join(pages)+'</html>'


def main():
    config=load_project_config();kb=load_kb();out=ROOT/'outputs/mvp';out.mkdir(parents=True,exist_ok=True)
    def write(name,value):
        path=out/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
    manifest=json.loads((ROOT/'cases/split-manifest.json').read_text())
    for split,expected in manifest['sha256'].items():
        assert hashlib.sha256((ROOT/'cases'/f'{split}.json').read_bytes()).hexdigest()==expected,'Frozen case split changed'
    calibration=json.loads((ROOT/'cases/calibration.json').read_text())['cases']
    # No holdout outcome is used for any implementation or weight tuning.
    all_rows=[];results={};sensitivity={}
    for split in ['calibration','holdout']:
        cases=calibration if split=='calibration' else json.loads((ROOT/'cases/holdout.json').read_text())['cases']
        for case in cases:
            result=run_case(case['form_answers'],kb,config);results[case['id']]=result
            write(f"results/{case['id']}.json",result)
            platform=platform_baseline(case['form_answers']['answers']);count=_count_baseline(result)
            leaders=_leaders(result)
            row={'profile':case['id'],'split':split,'status':result['status'],**{g:len(v) for g,v in result['groups'].items()},'scenario_leaders':leaders,'robust_eligible_winner':robust_winners(result),'platform_baseline':platform,'count_baseline':count,'differs_from_platform':leaders!=platform['candidate_ids'],'differs_from_count':leaders!=count['candidate_ids']}
            all_rows.append(row)
            if split=='calibration':
                if result['status']=='ok':
                    weights=soft_weights(requirement_rows(result['requirements']),config['reasoning'])
                    sensitivity[case['id']]=weight_sensitivity(result['scenarios']['outcomes'],weights,config['reasoning']['level_to_value'],config['settings']['evaluation'],config['reasoning']['seed'])
                else:sensitivity[case['id']]={'status':'not_applicable_invalid_input','draws':[],'top_rates':{}}
    write('summary.json',all_rows);write('weight-sensitivity-calibration.json',sensitivity)
    with (out/'summary.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(all_rows[0]));writer.writeheader();writer.writerows({key:json.dumps(value,ensure_ascii=False) if isinstance(value,(list,dict)) else value for key,value in row.items()} for row in all_rows)
    write('form-perturbations.json',perturb_form(calibration[1]['form_answers'],kb,config))
    for label,cid in [('easy','SYNTHETIC-C01'),('many-unknown','SYNTHETIC-C05'),('no-eligible','SYNTHETIC-C04')]:write(f'written-{label}-full-trace.json',results[cid])
    fixture=json.loads((ROOT/'examples/synthetic-mvp-case.json').read_text())
    (ROOT/'outputs/synthetic-ui-three-groups.json').write_text(json.dumps(run_requirements(fixture['kb'],fixture['requirements'],config),ensure_ascii=False)+'\n',encoding='utf-8')
    all_cases=calibration+json.loads((ROOT/'cases/holdout.json').read_text())['cases']
    (out/'expert-score-sheet.html').write_text(_blind_sheet(all_cases,config),encoding='utf-8')
    behavior={'different_scenario_leaders':len({tuple(r['scenario_leaders']) for r in all_rows if r['scenario_leaders']})>1,'has_excluded_real_candidate':any(r['excluded'] for r in all_rows),'has_conditional':any(r['conditional'] for r in all_rows),'has_no_eligible':any(r['status']=='ok' and not r['eligible'] for r in all_rows),'has_eligible':any(r['eligible'] for r in all_rows),'reason':'A missing claim is not none. Catalog quota and unresolved paths keep every real scope conditional; do not alter KB to force behavior coverage.'}
    write('behavior-coverage.json',behavior)
    mapping=config['value_mapping'];gaps=[r for r in mapping['rows'] if not r['accepted_kb_values']]
    write('kb-coverage-gaps.json',{'mapping_revision':mapping['manifest']['revision'],'rows':gaps,'policy':'No guessed equivalence; KB kept unchanged.'})
    write('evaluation-config.json',{'settings':config['settings'],'reasoning':config['reasoning'],'split_manifest':manifest,'holdout_used_for_tuning':False})
    print(json.dumps({'profiles':len(all_rows),'behavior_coverage':behavior,'sensitivity_draws':{cid:len(v['draws']) for cid,v in sensitivity.items()},'output_directory':str(out)},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
