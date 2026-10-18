"""Explicit domain translation and dictionary validation. Never edits the KB."""
from copy import deepcopy
from math import isfinite

from .contracts import requirement_rows


def validate_semantics(kb, document, dictionary):
    properties={p['id']:p for p in dictionary['properties']}
    for kind, rows in [('claims',kb['claims']),('requirements',requirement_rows(document))]:
        for row in rows:
            path=f"{kind}.{row['id']}"
            prop=properties.get(row['property_id'])
            if prop is None:
                raise ValueError(f"{path}.property_id: not in property dictionary")
            qualifiers=row.get('qualifiers',{})
            allowed=set(prop['qualifiers']+prop.get('optional_qualifiers',[]))
            if set(qualifiers)-allowed:
                raise ValueError(f"{path}.qualifiers: unknown qualifier {sorted(set(qualifiers)-allowed)}")
            if set(prop['qualifiers'])-set(qualifiers):
                raise ValueError(f"{path}.qualifiers: missing required qualifier")
            if set(row.get('qualifier_domains',{}))-allowed:
                raise ValueError(f"{path}.qualifier_domains: unknown qualifier")
            if prop['value_type']=='support':
                levels=dictionary['rubrics'][prop['rubric_ref']]['ordered_levels']
                if kind=='claims' and row.get('level') not in [*levels,'unknown',None]:
                    raise ValueError(f"{path}.level: invalid for {prop['rubric_ref']}")
                if kind=='requirements' and row.get('min_level_if_applicable') not in [*levels,None]:
                    raise ValueError(f"{path}.min_level_if_applicable: invalid rubric threshold")
            elif kind=='claims' and prop['value_type']=='quantity' and row.get('value') is not None:
                amount=row['value'].get('amount') if isinstance(row['value'],dict) else None
                if isinstance(amount,bool) or not isinstance(amount,(int,float)) or not isfinite(amount) or amount<0:
                    raise ValueError(f"{path}.value.amount: expected finite nonnegative number")
            elif kind=='requirements' and prop['value_type']!='quantity':
                raise ValueError(f"{path}.property_id: descriptive property cannot be scored")
            if kind=='requirements' and prop['value_type']=='quantity':
                interval=row.get('demand_interval',{})
                lo,hi=interval.get('lower'),interval.get('upper')
                if row['property_id']!='limits.quota' or row.get('operator')!='capacity_covers_demand_interval' or isinstance(lo,bool) or not isinstance(lo,(int,float)) or not isfinite(lo) or lo<0 or (hi is not None and (isinstance(hi,bool) or not isinstance(hi,(int,float)) or not isfinite(hi) or hi<lo)):
                    raise ValueError(f"{path}.demand_interval: invalid quota requirement")


def translate_document(document, mapping):
    translated=deepcopy(document)
    rows={(r['property_id'],r['qualifier'],r['input_value']):r for r in mapping['rows']}
    for requirement in requirement_rows(translated):
        requirement['qualifier_acceptance_sets']={}
        requirement['domain_mapping_trace']=[]
        requirement['domain_gaps']=[]
        for key,value in requirement.get('qualifiers',{}).items():
            if value is None:
                continue
            row=rows.get((requirement['property_id'],key,value))
            accepted=row['accepted_kb_values'] if row else []
            requirement['qualifier_acceptance_sets'][key]=list(accepted)
            requirement['domain_mapping_trace'].append(deepcopy(row) if row else {'property_id':requirement['property_id'],'qualifier':key,'input_value':value,'accepted_kb_values':[],'reason':'No explicit mapping row; no guessed alias.'})
            if not accepted:
                requirement['domain_gaps'].append({'qualifier':key,'input_value':value})
    return translated
