import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {buildPayload,validatePayload} from '../dist/core.js';

const registryPath='../../research/catalog-knowledge-base/form-v3-registry.json';
const v3=()=>readFile(registryPath,'utf8').then(JSON.parse);
const config=JSON.parse(await readFile('../../research/catalog-knowledge-base/layer-2-runtime-config.json','utf8'));

test('v3 transmits storage, per-engine operations and exact count unchanged',async()=>{
 const registry=await v3();
 const draft={I01:'local_lab',I02:['spark'],I04:'lt_100',I11:'local_fs',I12:{spark:['read','append']}};
 const payload=buildPayload(draft,registry,{table_count_exact:5});
 assert.deepEqual(payload,{form_revision:'input-v3',answers:draft,context:{table_count_exact:5}});
 assert.deepEqual(validatePayload(payload,registry),[]);
});

test('v3 rejects mixed unknown operations and unselected engine operations',async()=>{
 const registry=await v3();
 for(const ops of [{spark:['unknown','read']},{trino:['read']}]){
  const payload=buildPayload({I02:['spark'],I12:ops},registry);
  assert.ok(validatePayload(payload,registry).some(i=>i.field.startsWith('answers.I12.')));
 }
});

test('v3 exact table count must be positive integer in selected bucket',async()=>{
 const registry=await v3();
 for(const value of [0,100,5.5,true]){
  const payload=buildPayload({I04:'lt_100'},registry,{table_count_exact:value});
  assert.ok(validatePayload(payload,registry,config).some(i=>i.field==='context.table_count_exact'));
 }
});

test('v3 unknown storage stays unknown; omitted operations are not populated',async()=>{
 const registry=await v3();
 const payload=buildPayload({I01:'aws',I11:'unknown'},registry);
 assert.equal(payload.answers.I11,'unknown');assert.equal(payload.answers.I12,undefined);
 assert.deepEqual(validatePayload(payload,registry),[]);
});
