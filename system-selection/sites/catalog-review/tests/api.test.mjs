import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
let server,url;
test.before(async()=>{
 server=spawn(process.execPath,['server.mjs'],{env:{...process.env,PORT:'0'},windowsHide:true});
 url=await new Promise((resolve,reject)=>{server.stdout.on('data',b=>{const m=String(b).match(/Local: (http:\/\/127\.0\.0\.1:\d+)/);if(m)resolve(m[1]);});server.on('error',reject);});
});
test.after(()=>server?.kill());
test('official API accepts canonical form, runs Python and returns seven real scopes',async()=>{
 const response=await fetch(url+'/api/run',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({form_revision:'input-v2',answers:{I01:'aws',I02:['spark'],I03:'iceberg',I04:'lt_100',I05:'one',I07:'none',I08:'no',I09:['none'],I10:{none:true,selected:[]}}})});
 assert.equal(response.status,200);
 const result=await response.json();assert.equal(result.inference_executed,true);
 assert.equal(Object.values(result.groups).flat().length,7);assert.equal(result.stage,'1-4');
});
test('invalid rank is a field-specific input error and stops inference',async()=>{
 const response=await fetch(url+'/api/run',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({form_revision:'input-v2',answers:{I10:{selected:[{feature:'branching'}]}}})});
 assert.equal(response.status,422);const result=await response.json();assert.equal(result.inference_executed,false);assert.ok(result.input_issues.some(i=>i.field.includes('rank')));
});
test('API rejects malformed JSON, oversized input and foreign origins',async()=>{
 for(const [headers,body,status] of [[{'content-type':'application/json'},'{',400],[{'content-type':'application/json'},' '.repeat(65537),413],[{'content-type':'application/json',origin:'https://unrelated.example'},'{}',403]]){
  assert.equal((await fetch(url+'/api/run',{method:'POST',headers,body})).status,status);
 }
});
