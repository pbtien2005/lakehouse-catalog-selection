"""JSON I/O for the official MVP. No decisions in the server or UI."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from .application import run_case
from .layer2_io import load_assets

ROOT=Path(__file__).resolve().parents[1]


def load_kb():
    return json.loads((ROOT.parent/'catalog-knowledge-base/layer-1-data.json').read_text(encoding='utf-8-sig'))


def load_project_config():
    layer2=load_assets();mapping=ROOT.parent/'catalog-knowledge-base/layer-2-kb-values.json'
    values=json.loads(mapping.read_text(encoding='utf-8'))
    kb_path=ROOT.parent/'catalog-knowledge-base/layer-1-data.json'
    if hashlib.sha256(kb_path.read_bytes()).hexdigest()!=values['manifest']['kb_sha256']:
        raise ValueError('Value mapping KB hash is stale; review explicit mappings before running.')
    config={'layer2':layer2,'reasoning':layer2['reasoning_config'],'dictionary':layer2['dictionary'],'value_mapping':values,'settings':json.loads((ROOT/'mvp-settings.json').read_text(encoding='utf-8'))}
    base=ROOT.parent/'catalog-knowledge-base'
    names={'evidence_overlay':'verified-path-evidence-2026-10-18.json','implementation_profiles':'implementation-profiles-v1.json','value_mapping_v3_rows':'layer-2-v3-value-rows.json'}
    for key,name in names.items():
        path=base/name
        if path.exists():config[key]=json.loads(path.read_text(encoding='utf-8-sig'))
    if config.get('evidence_overlay'):
        expected=config['evidence_overlay'].get('manifest',{}).get('base_kb_sha256')
        if expected!=hashlib.sha256(kb_path.read_bytes()).hexdigest():
            raise ValueError('Evidence overlay base KB hash is stale; review sources before running form v3.')
    config['knowledge_asset_hashes']={name:hashlib.sha256((base/name).read_bytes()).hexdigest() for name in names.values() if (base/name).exists()}
    config['quality_policy']=json.loads((ROOT/'quality-policy.json').read_text(encoding='utf-8'))
    return config


def main(argv=None):
    parser=argparse.ArgumentParser(description='Official local form-v2 -> Layer 2 -> Layer 3')
    parser.add_argument('--answers',help='JSON file; stdin if omitted')
    parser.add_argument('--output')
    args=parser.parse_args(argv)
    try:
        payload=json.loads(Path(args.answers).read_text(encoding='utf-8-sig') if args.answers else sys.stdin.read())
        result=run_case(payload,load_kb(),load_project_config())
        text=json.dumps(result,ensure_ascii=True,sort_keys=True,allow_nan=False)+'\n'
        if args.output:
            path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
        else:print(text,end='')
        return 0 if result['status']=='ok' else 2
    except (ValueError,OSError,KeyError,TypeError) as error:
        print(json.dumps({'status':'data_error','message':str(error),'inference_executed':False}))
        return 2


if __name__=='__main__':raise SystemExit(main())
