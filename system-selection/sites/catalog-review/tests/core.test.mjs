import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {buildPayload,validatePayload,acceptBackendResult} from '../dist/core.js';
const registry=JSON.parse(await readFile('../../research/catalog-knowledge-base/form-v2-registry.json','utf8'));

test('registry contains ten questions and 48 choices',()=>{
  assert.equal(registry.questions.length,10);
  assert.equal(registry.questions.reduce((n,q)=>n+q.answers.length,0),48);
});
test('every active choice can be transmitted without changing its ID',()=>{
  for(const q of registry.questions.filter(q=>q.enabled)) for(const a of q.answers) {
    const value=q.control==='features'?(a.id==='none'?{none:true,selected:[]}:{selected:[{feature:a.id,rank:'nice_to_have'}]}):q.control==='multi'?[a.id]:a.id;
    const payload=buildPayload({[q.id]:value},registry);
    assert.deepEqual(payload.answers[q.id],value);
    assert.deepEqual(validatePayload(payload,registry),[]);
  }
});
test('inactive I06 is not submitted',()=>assert.deepEqual(buildPayload({I06:'yes'},registry).answers,{}));
test('none with a platform yields a field-specific error',()=>{
  assert.ok(validatePayload(buildPayload({I09:['none','databricks']},registry),registry).some(x=>x.code==='E_EXCLUSIVE_NONE'&&x.field==='answers.I09'));
});
test('a selected feature needs one of the two approved ranks',()=>{
  for(const rank of [undefined,'important','off','unknown']) assert.ok(validatePayload(buildPayload({I10:{selected:[{feature:'branching',rank}]}},registry),registry).some(x=>x.field.endsWith('.rank')));
});
test('none cannot coexist with a special feature',()=>assert.ok(validatePayload(buildPayload({I10:{none:true,selected:[{feature:'branching',rank:'mandatory'}]}},registry),registry).some(x=>x.code==='E_EXCLUSIVE_NONE')));
test('unknown need and no need keep distinct answer IDs',()=>{
  assert.notDeepEqual(buildPayload({I08:'unknown'},registry),buildPayload({I08:'no'},registry));
});
test('wrong labels, duplicates and wrong cardinality are errors',()=>{
  for(const draft of [{I01:'AWS'},{I02:['spark','spark']},{I01:['aws','gcp']},{I02:[]}]) assert.ok(validatePayload(buildPayload(draft,registry),registry).length);
});
test('payload copies input and does not populate missing answers',()=>{
  const draft={I02:['spark']}; const payload=buildPayload(draft,registry); payload.answers.I02.push('trino');
  assert.deepEqual(draft,{I02:['spark']}); assert.deepEqual(buildPayload({},registry).answers,{});
});
test('backend result presentation copies supplied decisions without inferring a winner',()=>{
  const data={groups:{eligible:[],conditional:[{candidate_id:'synthetic_test_only'}],excluded:[]}};
  const copy=acceptBackendResult(data);assert.deepEqual(copy,data);copy.groups.conditional.length=0;assert.equal(data.groups.conditional.length,1);
  assert.throws(()=>acceptBackendResult({items:[]}),TypeError);
});

for(const [name,payload,code] of [
  ['missing payload',null,'E_PAYLOAD'],
  ['wrong revision',{form_revision:'input-v1',answers:{}},'E_FORM_REVISION'],
  ['array answers',{form_revision:'input-v2',answers:[]},'E_PAYLOAD'],
  ['unknown question',{form_revision:'input-v2',answers:{I99:'yes'}},'E_UNKNOWN_FIELD'],
  ['legacy grouped engine',{form_revision:'input-v2',answers:{I02:['trino_presto']}},'E_LEGACY_FORM_ANSWER'],
  ['scalar multi choice',{form_revision:'input-v2',answers:{I02:'spark'}},'E_CARDINALITY'],
  ['malformed selected list',{form_revision:'input-v2',answers:{I10:{selected:'branching'}}},'E_CARDINALITY'],
  ['nonboolean none',{form_revision:'input-v2',answers:{I10:{none:'yes',selected:[]}}},'E_INVALID_ANSWER'],
  ['nonobject feature',{form_revision:'input-v2',answers:{I10:{selected:['branching']}}},'E_INVALID_ANSWER'],
  ['duplicate feature',{form_revision:'input-v2',answers:{I10:{selected:[{feature:'branching',rank:'mandatory'},{feature:'branching',rank:'nice_to_have'}]}}},'E_DUPLICATE_SELECTION'],
  ['none as ranked feature',{form_revision:'input-v2',answers:{I10:{selected:[{feature:'none',rank:'mandatory'}]}}},'E_INVALID_ANSWER'],
])test(`invalid contract: ${name}`,()=>assert.ok(validatePayload(payload,registry).some(issue=>issue.code===code)));
