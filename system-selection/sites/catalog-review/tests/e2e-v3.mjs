// Actual local UI -> official Python inference; no injected decision fixture.
import {createRequire} from 'node:module';
import {existsSync,writeFileSync,mkdirSync} from 'node:fs';
import {spawn} from 'node:child_process';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const server=spawn(process.execPath,['server.mjs'],{env:{...process.env,PORT:'0'},windowsHide:true});
let browser;
const report={official_pipeline:true,checks:[],page_errors:[],layout_findings:[]};
try{
 const url=await new Promise((resolve,reject)=>{
  server.stdout.on('data',chunk=>{const m=String(chunk).match(/Local: (http:\/\/127\.0\.0\.1:\d+)/);if(m)resolve(m[1]);});server.on('error',reject);
 });
 const executablePath=['C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find(existsSync);
 browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
 const page=await browser.newPage();page.on('pageerror',error=>report.page_errors.push(error.message));
 await page.goto(url+'/#form');await page.locator('#profile-form').waitFor();
 const choose=async(name,value)=>{const input=page.locator(`[name="${name}"][value="${value}"]`);if(!await input.isChecked())await input.locator('..').click();};
 assert.equal(await page.locator('.form-field').count(),11);
 await choose('I01','local_lab');await choose('I02','spark');
 await page.locator('[name="I12-spark"]').first().waitFor();
 for(const [qid,value] of Object.entries({I03:'iceberg',I04:'lt_100',I05:'one',I07:'none',I08:'no',I09:'none',I11:'local_fs'}))await choose(qid,value);
 await choose('I10-feature','branching');await page.locator('[name="I10-rank-branching"]').selectOption('mandatory');
 const exactInput=page.locator('[name="table_count_exact"]');
 assert.ok(await exactInput.evaluate(input=>{const style=getComputedStyle(input),rect=input.getBoundingClientRect();return Number(style.opacity)>0&&style.pointerEvents!=='none'&&rect.width>0&&rect.height>0;}),'Exact count input must be visible and operable');
 for(const operation of ['read','append','create_table'])await choose('I12-spark',operation);
 await choose('I12-spark','unknown');
 await page.getByRole('button',{name:'Xem kết quả đánh giá'}).click();
 assert.ok((await page.locator('#form-errors').textContent()).includes('I12.spark'));
 assert.equal(await page.locator('#form-errors').evaluate(e=>e===document.activeElement),true);
 await page.locator('[name="I12-spark"][value="unknown"]').locator('..').click();
 await page.locator('[name="table_count_exact"]').fill('100');
 await page.getByRole('button',{name:'Xem kết quả đánh giá'}).click();
 assert.ok((await page.locator('#form-errors').textContent()).includes('context.table_count_exact'));
 await page.locator('[name="table_count_exact"]').fill('1');
 report.checks.push('mutually exclusive unknown operations and inconsistent exact count show field-specific errors and keyboard focus');
 const expected={form_revision:'input-v3',answers:{I01:'local_lab',I02:['spark'],I03:'iceberg',I04:'lt_100',I05:'one',I07:'none',I08:'no',I09:['none'],I10:{none:false,selected:[{feature:'branching',rank:'mandatory'}]},I11:'local_fs',I12:{spark:['read','append','create_table']}},context:{table_count_exact:1}};
 const responsePromise=page.waitForResponse(response=>response.url().endsWith('/api/run')&&response.request().method()==='POST');
 await page.getByRole('button',{name:'Xem kết quả đánh giá'}).click();
 const response=await responsePromise;assert.deepEqual(response.request().postDataJSON(),expected);
 assert.equal(response.status(),200);const result=await response.json();assert.equal(result.inference_executed,true);
 await page.locator('[data-group="conditional"]').waitFor();
 for(const group of ['eligible','conditional','excluded'])assert.equal(await page.locator(`[data-group="${group}"] .catalog-row`).count(),result.groups[group].length);
 const nessie=Object.values(result.groups).flat().find(c=>c.candidate_id==='project_nessie');
 assert.ok(nessie?.proposed_implementation,'Nessie requires an evidenced selected implementation');
 const nessieRow=page.locator('[data-candidate="project_nessie"]');
 assert.equal(await nessieRow.locator('[data-implementation-profile]').getAttribute('data-implementation-profile'),nessie.proposed_implementation.id);
 const branch=nessie.assessments.find(a=>a.property_id==='workflow.branching');
 assert.ok(branch.trace.claim_ids.length,'Native catalog branching has a claim witness');
 for(const claim of branch.trace.claim_ids)assert.ok((await nessieRow.textContent()).includes(claim));
 assert.ok((await nessieRow.locator('[data-implementation-profile]').textContent()).includes('quota'));
 report.checks.push('selected Nessie implementation, native branching claim, prerequisites, versions and still-enforced quota are shown');
 if(result.scenarios.comparison_scope==='evidenced_joint_profiles_with_resolved_user_context'){
  assert.ok(await page.locator('[data-comparison-scope]').count(),'Scenario comparison scope must be disclosed');
  if(result.scenarios.status==='insufficient_verified_implementations_for_comparison'){
   const comparisonText=await page.locator('[data-comparison-scope]').textContent();
   assert.ok(comparisonText.includes('chưa có so sánh tỷ lệ đứng đầu'));
   assert.ok(comparisonText.includes('bảy'));
  }
  report.checks.push('scenario comparison eligibility and insufficient verified alternatives are disclosed');
 }
 assert.deepEqual(JSON.parse(await page.locator('#submitted-payload').textContent()),expected);
 report.checks.push('input-v3 storage/actions/exact count survive actual browser payload; group counts and submitted payload match official result');
 report.groups=Object.fromEntries(Object.entries(result.groups).map(([group,rows])=>[group,rows.length]));
 await page.goto(url+'/#form');await page.locator('#profile-form').waitFor();
 await page.locator('[name="I10-rank-branching"]').selectOption('nice_to_have');
 const softResponsePromise=page.waitForResponse(response=>response.url().endsWith('/api/run')&&response.request().method()==='POST');
 await page.getByRole('button',{name:'Xem kết quả đánh giá'}).click();
 const softResponse=await softResponsePromise;assert.equal(softResponse.status(),200);
 const softResult=await softResponse.json();
 await page.locator('[data-comparison-scope]').waitFor();
 assert.equal(softResult.scenarios.status,'insufficient_verified_implementations_for_comparison');
 assert.ok((await page.locator('[data-comparison-scope]').textContent()).includes('chưa có so sánh tỷ lệ đứng đầu'));
 const softNessie=Object.values(softResult.groups).flat().find(c=>c.candidate_id==='project_nessie');
 assert.deepEqual(softNessie.score_interval,[1,1]);assert.equal(softNessie.top_rate,null);
 report.checks.push('single verified implementation keeps SOFT interval but shows unavailable top-rate comparison; seven catalogs are not presented as ranked');
 await page.setViewportSize({width:375,height:812});
 for(const view of ['report','form']){
  if(view==='form'){await page.goto(url+'/#form');await page.locator('#profile-form').waitFor();}
  const width=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth}));
  if(width.document>width.viewport)report.layout_findings.push({view,...width});
 }
 await page.locator('[name="I01"][value="aws"]').scrollIntoViewIfNeeded();await page.locator('[name="I01"][value="aws"]').focus();await page.keyboard.press('ArrowDown');
 assert.equal(await page.locator('[name="I01"][value="azure"]').isChecked(),true);
 const focus=await page.evaluate(()=>({outline:getComputedStyle(document.activeElement).outlineStyle,width:document.activeElement.getBoundingClientRect().width}));
 assert.ok(focus.outline!=='none'&&focus.width>0);report.checks.push('radio keyboard navigation and visible focus pass at narrow width');
 assert.deepEqual(report.page_errors,[]);assert.deepEqual(report.layout_findings,[]);
 report.status='passed';mkdirSync('artifacts',{recursive:true});writeFileSync('artifacts/e2e-v3.json',JSON.stringify(report,null,2)+'\n');
 await page.screenshot({path:'artifacts/e2e-v3-mobile.png',fullPage:true});console.log(JSON.stringify(report,null,2));
}finally{if(browser)await browser.close();server.kill();}
