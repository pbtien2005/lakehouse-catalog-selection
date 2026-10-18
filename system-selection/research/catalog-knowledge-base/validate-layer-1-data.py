"""Validate the authored layer-1 dataset. No network calls or product inference.

Run: python validate-layer-1-data.py --write-reports
The reports measure record integrity and collection coverage, not factual truth.
"""
import argparse
from collections import Counter
from datetime import date
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parent
OFFICIAL_HOSTS = {
    'polaris.apache.org', 'gravitino.apache.org', 'projectnessie.org',
    'docs.unitycatalog.io', 'docs.databricks.com', 'docs.aws.amazon.com',
    'hive.apache.org', 'trino.io', 'iceberg.apache.org',
}
REPOSITORIES = {
    ('apache', 'polaris'), ('apache', 'gravitino'), ('apache', 'hive'),
    ('projectnessie', 'nessie'), ('unitycatalog', 'unitycatalog'),
}


def no_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f'Duplicate JSON key: {key}')
        obj[key] = value
    return obj


def read_json(name):
    return json.loads((BASE / name).read_text(encoding='utf-8-sig'),
                      object_pairs_hook=no_duplicate_keys)


def known(claim):
    return claim.get('level') != 'unknown' and claim.get('value', True) is not None


def official(url):
    u = urlparse(url)
    if u.scheme != 'https' or not u.netloc or u.username or u.password:
        return False
    if u.hostname in OFFICIAL_HOSTS:
        return True
    parts = u.path.strip('/').split('/')
    return u.hostname == 'raw.githubusercontent.com' and tuple(parts[:2]) in REPOSITORIES


def validate(data, dictionary, register):
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    manifest = data['manifest']
    revision_date = date.fromisoformat(manifest['created_on'])
    groups = {g['id'] for g in dictionary['groups']}
    props = {p['id']: p for p in dictionary['properties']}
    scopes = {s['id']: s for s in data['scopes']}
    sources = {s['url']: s for s in register['sources']}
    check(len(props) == len(dictionary['properties']) == 37, 'Dictionary must have 37 distinct properties')
    check(len(groups) == 11, 'Dictionary must have 11 groups')
    check(all(p['group'] in groups for p in props.values()), 'Unknown property group')
    check(len(scopes) == len(data['scopes']) == 7, 'Expected seven distinct scopes')
    check(len({s['catalog_id'] for s in scopes.values()}) == 7, 'Expected seven distinct technologies')
    check(set(manifest['catalogs_in_research_scope']) == {s['catalog_id'] for s in scopes.values()}, 'Manifest scope mismatch')
    check(manifest['property_dictionary'] == 'layer-1-properties.json', 'Dictionary reference mismatch')
    check(manifest['property_dictionary_sha256'] == hashlib.sha256((BASE / manifest['property_dictionary']).read_bytes()).hexdigest(), 'Dictionary hash mismatch')
    check(len(sources) == len(register['sources']), 'Duplicate source URL')
    check(len({s['id'] for s in register['sources']}) == len(sources), 'Duplicate source ID')
    for sid, scope in scopes.items():
        check(all(scope.get(k) for k in ('catalog_id', 'name', 'edition', 'deployment_mode')), f'{sid}: missing scope fields')
        check(bool(scope.get('release')) != bool(scope.get('as_of')), f'{sid}: select release or as_of')
        check(scope['deployment_mode'] in ('self_managed', 'managed'), f'{sid}: invalid deployment mode')
        if scope.get('as_of'):
            check(date.fromisoformat(scope['as_of']) <= revision_date, f'{sid}: future as_of')
    ids = set()
    keys = {}
    used_urls = set()
    for c in data['claims']:
        cid = c.get('id', '<missing>')
        check(cid not in ids, f'{cid}: duplicate claim ID')
        ids.add(cid)
        check(c.get('scope_id') in scopes, f'{cid}: invalid scope reference')
        check(c.get('property_id') in props, f'{cid}: invalid property reference')
        if c.get('property_id') not in props:
            continue
        p = props[c['property_id']]
        q = c.get('qualifiers', {})
        check(isinstance(q, dict), f'{cid}: qualifiers must be an object')
        check(set(p['qualifiers']) <= set(q), f'{cid}: missing required qualifiers')
        check(set(q) <= set(p['qualifiers'] + p['optional_qualifiers']), f'{cid}: undeclared qualifier')
        check(all(isinstance(v, str) and v.strip() for v in q.values()), f'{cid}: empty/non-string qualifier')
        check(isinstance(c.get('note'), str) and bool(c['note'].strip()), f'{cid}: missing note')
        check(isinstance(c.get('limits'), list) and all(isinstance(x, str) for x in c['limits']), f'{cid}: invalid limits')
        check(c.get('status') == 'draft', f'{cid}: unreviewed data must remain draft')
        check(('level' in c) != ('value' in c), f'{cid}: use exactly one of level/value')
        typ = p['value_type']
        if typ == 'support':
            levels = dictionary['rubrics'][p['rubric_ref']]['ordered_levels'] + ['unknown']
            check('level' in c and c.get('level') in levels, f'{cid}: invalid support level')
            if c.get('level') == 'partial':
                check(bool(c.get('covered_parts')) and bool(c.get('unmet_parts')), f'{cid}: partial needs covered/unmet parts')
        else:
            v = c.get('value')
            check('value' in c, f'{cid}: missing typed value')
            if v is not None:
                if typ == 'text':
                    check(isinstance(v, str) and bool(v.strip()), f'{cid}: text value required')
                elif typ == 'string_set':
                    check(isinstance(v, list) and all(isinstance(x, str) and x for x in v), f'{cid}: string set required')
                    if isinstance(v, list):
                        check(len(v) == len(set(v)), f'{cid}: duplicate set member')
                elif typ == 'quantity':
                    check(isinstance(v, dict), f'{cid}: quantity object required')
                    if isinstance(v, dict):
                        amount = v.get('amount')
                        check(type(amount) in (int, float) and math.isfinite(amount), f'{cid}: finite numeric amount required')
                        check(isinstance(v.get('unit'), str) and bool(v['unit']), f'{cid}: unit required')
                    context = c.get('observation_context', {})
                    check(set(p['observation_context_fields']) <= set(context), f'{cid}: missing observation context')
        evidence = c.get('evidence', [])
        check(isinstance(evidence, list), f'{cid}: evidence must be a list')
        check(not known(c) or bool(evidence), f'{cid}: known claim has no evidence')
        for e in evidence:
            url = e.get('url', '')
            used_urls.add(url)
            check(official(url), f'{cid}: non-official or unsafe evidence URL: {url}')
            check(url in sources, f'{cid}: URL missing from source register')
            check(e.get('kind') in ('official_doc', 'official_repository'), f'{cid}: invalid evidence kind')
            check(isinstance(e.get('locator'), str) and bool(e['locator'].strip()), f'{cid}: missing source section')
            check(date.fromisoformat(e['retrieved_at']) <= revision_date, f'{cid}: future retrieval date')
            if url in sources:
                check(e['kind'] == sources[url]['kind'], f'{cid}: evidence kind mismatch')
                check(e['retrieved_at'] == sources[url]['retrieved_at'], f'{cid}: retrieval date mismatch')
                check(sources[url]['access'] == 'read_relevant_sections', f'{cid}: source not recorded as read')
        key = (c['scope_id'], c['property_id'], json.dumps(q, sort_keys=True))
        answer = json.dumps(c.get('level', c.get('value')), sort_keys=True)
        if key in keys:
            check(False, f'{cid}: duplicate/conflicting claim key also used by {keys[key][0]} (answers {answer}, {keys[key][1]})')
        keys[key] = (cid, answer)
        check(not any(k in c for k in ('weight', 'score', 'rank')), f'{cid}: scoring leaked into facts')
    check(used_urls == set(sources), 'Source register contains unused or missing URLs')
    for url, s in sources.items():
        check(official(url), f'Source {s["id"]}: unapproved official source')
        check(bool(s.get('title')) and bool(s.get('document_scope')), f'Source {s["id"]}: missing title/scope')
    return errors


GAPS = {
    'integration.streaming_write': 'Chưa đối chiếu engine, format, mode và connector của đường streaming.',
    'authentication.method': 'Chưa thu cơ chế xác thực đúng API/scope; không được mặc định anonymous hoặc không hỗ trợ.',
    'transaction.multi_table_atomic': 'Chưa chứng minh all-or-nothing cho client path và failure boundary cụ thể.',
    'commit.concurrent_write': 'Chưa chứng minh mô hình writer, thao tác và giao thức commit tương ứng.',
    'workflow.branching': 'Chưa xác minh đủ tạo nhánh, ghi cô lập và công bố ở cấp đối tượng cụ thể.',
    'storage.credential_vending': 'Chưa chứng minh đồng thời credential tạm thời, scope dữ liệu/quyền và API/client.',
    'governance.audit': 'Chưa xác minh loại sự kiện, principal và boundary audit.',
    'governance.lineage': 'Chưa xác minh quan hệ lineage và integration thu thập cụ thể.',
    'project.support_policy': 'Chưa biên soạn policy hỗ trợ/EOL hoặc hợp đồng cho provider/edition này.',
    'project.maintenance_context': 'Chưa biên soạn trạng thái bảo trì theo phương pháp và thời điểm xác định.',
    'project.license': 'Chưa đưa được nguồn license phù hợp scope vào revision này.',
}


def coverage(data, dictionary):
    rows = []
    for scope in data['scopes']:
        for prop in dictionary['properties']:
            cs = [c for c in data['claims'] if c['scope_id'] == scope['id'] and c['property_id'] == prop['id']]
            ks = [c for c in cs if known(c)]
            us = [c for c in cs if not known(c)]
            state = 'scoped_claims_available' if ks else ('explicit_unknown_only' if us else 'not_collected')
            rows.append(dict(scope_id=scope['id'], property_id=prop['id'], group=prop['group'], collection_state=state,
                             known_claim_ids=[c['id'] for c in ks], unknown_claim_ids=[c['id'] for c in us],
                             remaining_gap=GAPS.get(prop['id'], 'Chưa thu phạm vi/điều kiện khác của thuộc tính này.') if not ks else 'Chỉ các qualifier đã ghi có bằng chứng; mọi tổ hợp chưa thu vẫn unknown.'))
    return dict(manifest=dict(data_revision=data['manifest']['revision'], cells=len(rows), meaning='collection_inventory_not_product_capability_matrix', all_uncollected_combinations='unknown'), cells=rows)


def write_reports(data, dictionary, register, errors):
    cov = coverage(data, dictionary)
    report = dict(data_revision=data['manifest']['revision'], checked_on=data['manifest']['created_on'],
                  result='pass' if not errors else 'fail', errors=errors,
                  counts=dict(scopes=len(data['scopes']), groups=len(dictionary['groups']), properties=len(dictionary['properties']),
                              claims=len(data['claims']), known_claims=sum(known(c) for c in data['claims']),
                              explicit_unknown_claims=sum(not known(c) for c in data['claims']), source_urls=len(register['sources']),
                              coverage_cells=len(cov['cells'])),
                  by_scope=[dict(scope_id=s['id'], known=sum(known(c) for c in data['claims'] if c['scope_id'] == s['id']),
                                 unknown=sum(not known(c) for c in data['claims'] if c['scope_id'] == s['id']),
                                 properties_with_scoped_evidence=sum(x['collection_state'] == 'scoped_claims_available' for x in cov['cells'] if x['scope_id'] == s['id'])) for s in data['scopes']],
                  checks=['JSON syntax and duplicate keys', '37 property and 11 group dictionary references', 'seven distinct scope identities',
                          'scope release/as_of and dates', 'dictionary SHA256', 'required and optional qualifier names', 'typed levels/values and rubrics',
                          'quantity units and observation context', 'evidence required for every known claim', 'official domain/repository allowlist',
                          'source inventory and retrieval dates', 'duplicate/conflicting exact claim keys', 'no scores/weights in claims'],
                  limits=['No runtime tests were performed.', 'No automatic factual entailment or human approval is claimed.',
                          'URLs were read during research; this offline checker does not re-fetch them.',
                          'Properties with evidence are not exhaustively collected across qualifiers.'])
    for name, obj in [('layer-1-coverage.json', cov), ('layer-1-data-validation.json', report)]:
        (BASE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# Độ bao phủ thu thập dữ liệu lớp 1', '', f"Revision: `{data['manifest']['revision']}`. Ngày: **17/10/2026**.", '',
             'Bảng kiểm kê **37 thuộc tính × 7 scope**. `K` = số claim có kết luận dựa trên nguồn (gồm full/none và giá trị đã biết); `U` = claim ghi rõ unknown/null; `—` = chưa thu claim. Một ô có K chỉ chứng minh các qualifier được ghi, không phải toàn bộ thuộc tính hoặc sản phẩm. Số K không phải điểm phù hợp.', '',
             '| Property | Polaris | Gravitino | Nessie | UC OSS | UC Databricks AWS | Glue | HMS |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for prop in dictionary['properties']:
        cells = []
        for scope in data['scopes']:
            x = next(x for x in cov['cells'] if x['scope_id'] == scope['id'] and x['property_id'] == prop['id'])
            k, u = len(x['known_claim_ids']), len(x['unknown_claim_ids'])
            cells.append('/'.join(([f'{k}K'] if k else []) + ([f'{u}U'] if u else [])) or '—')
        lines.append('| `' + prop['id'] + '` | ' + ' | '.join(cells) + ' |')
    lines += ['', 'Dữ liệu: [layer-1-data.json](layer-1-data.json). Chi tiết ID claim và khoảng trống: [layer-1-coverage.json](layer-1-coverage.json). Điều kiện và mâu thuẫn nguồn: [ghi chú nghiên cứu](layer-1-research-notes.md).', '']
    (BASE / 'layer-1-coverage.md').write_text('\n'.join(lines), encoding='utf-8')
    lines = ['# Danh mục nguồn chính thức cho dữ liệu lớp 1', '',
             f"Ngày đọc: **17/10/2026**. Có **{len(register['sources'])} URL** được dùng trong [dữ liệu](layer-1-data.json).", '',
             'Mỗi trang được đọc các phần liên quan; không tuyên bố đã đọc toàn bộ site. URL lặp lại trong nhiều claim vẫn là một nguồn. Bốn file LICENSE thuộc repository chính thức; các nguồn còn lại là tài liệu chính thức của sản phẩm/engine/dịch vụ tích hợp. Inventory này được tạo từ evidence và không thay nội dung claim.', '',
             '| ID | Nguồn | Phạm vi tài liệu | Claim tham chiếu |',
             '|---|---|---|---:|']
    for s in register['sources']:
        count = sum(any(e['url'] == s['url'] for e in c['evidence']) for c in data['claims'])
        lines.append(f"| `{s['id']}` | [{s['title']}]({s['url']}) | {s['document_scope']} | {count} |")
    lines += ['', 'Section/locator và ngày đọc nằm trong từng evidence của [layer-1-data.json](layer-1-data.json). Những chỗ nội dung chưa nhất quán được ghi riêng tại [ghi chú nghiên cứu](layer-1-research-notes.md).', '']
    (BASE / 'layer-1-sources.md').write_text('\n'.join(lines), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-reports', action='store_true')
    args = parser.parse_args()
    data = read_json('layer-1-data.json')
    dictionary = read_json(data['manifest']['property_dictionary'])
    register = read_json('layer-1-source-register.json')
    errors = validate(data, dictionary, register)
    if args.write_reports:
        report = write_reports(data, dictionary, register, errors)
        print(json.dumps(dict(result=report['result'], counts=report['counts'], errors=errors), ensure_ascii=False))
    else:
        print(json.dumps(dict(result='pass' if not errors else 'fail', errors=errors), ensure_ascii=False))
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
