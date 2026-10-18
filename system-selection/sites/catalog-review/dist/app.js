import {buildPayload,validatePayload,acceptBackendResult} from './core.js';
const paths = {
  report:'M4 3h12l4 4v14H4z M15 3v5h5 M8 12h8 M8 16h6',
  sliders:'M4 7h16 M4 17h16 M8 4v6 M16 14v6',
  book:'M12 6c-3-2-7-2-9-1v15c2-1 6-1 9 1 3-2 7-2 9-1V5c-2-1-6-1-9 1z M12 6v15',
  info:'M12 11v6 M12 7h.01 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
  plus:'M12 5v14 M5 12h14',help:'M9.5 8a2.5 2.5 0 1 1 4 2c-1.5 1-1.5 1-1.5 3 M12 17h.01 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
  chevron:'m9 5 7 7-7 7',edit:'m16 3 5 5-12 12-6 1 1-6z M13 6l5 5',
  download:'M12 3v12 m-5-5 5 5 5-5 M4 15v6h16v-6',cloud:'M6 18h12a4 4 0 0 0 .3-8A6.5 6.5 0 0 0 5.5 8 5 5 0 0 0 0 10z',
  layers:'m12 3 10 5-10 5L2 8z M2 12l10 5 10-5 M2 16l10 5 10-5',database:'M20 6c0 2-3.6 4-8 4S4 8 4 6s3.6-4 8-4 8 2 8 4z M4 6v12c0 2 3.6 4 8 4s8-2 8-4V6 M4 12c0 2 3.6 4 8 4s8-2 8-4',
  grid:'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',
  check:'m8 12 3 3 5-6 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
  arrow:'M4 12h16 m-6-6 6 6-6 6',external:'M14 3h7v7 M10 14 11-11 M10 3H3v18h18v-7',
  close:'m6 6 12 12 M6 18 18 6',search:'M11 19a8 8 0 1 1 0-16 8 8 0 0 1 0 16z M17 17l4 4',
  light:'M9 18h6 M10 21h4 M8 14a6 6 0 1 1 8 0c-1 1-1 2-1 2H9s0-1-1-2',
  lock:'M5 10h14v11H5z M8 10V6a4 4 0 0 1 8 0v4',refresh:'M20 7A9 9 0 1 0 21 15 M20 2v6h-6',
  print:'M6 9V2h12v7 M6 18H3V9h18v9h-3 M6 14h12v8H6z M17 12h.01',
};

const h = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const icon = name => `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="${paths[name]||paths.info}"/></svg>`;
const main=document.querySelector('#main');
const storageKey='catalog-review-form-v3';
let registry,settings,draft={},contextDraft={},submitted=null,result=null,busy=false,backendError='',requestId=0;
const heading=(title,subtitle,actions='')=>`<div class="document-heading"><div><h1>${h(title)}</h1><p>${h(subtitle)}</p></div><div class="document-actions">${actions}</div></div>`;
const footer=()=>'<footer class="document-footer"><span>Catalog Review · Công cụ hỗ trợ quyết định kỹ thuật</span><span>Form v3 · Python backend · 7 scope</span></footer>';
const tabs=()=>'<nav class="report-tabs" aria-label="Nội dung bản đánh giá"><a href="#report">Kết quả đánh giá</a><a href="#form">Yêu cầu của bạn</a><a href="#assumptions">Giả định & giới hạn</a></nav>';
function label(qid,value){return registry.questions.find(q=>q.id===qid)?.answers.find(a=>a.id===value)?.label??value;}
const reference=value=>h(value).replace(/([_-])/g,'$1<wbr>');
function safeHttps(value){try{const url=new URL(value);return url.protocol==='https:'?h(url.href):null;}catch{return null;}}
function implementationPanel(row){
 const profile=row.proposed_implementation,summary=row.functional_summary;
 if(!profile)return row.implementation_profiles?'<p>Chưa có đường tích hợp đã kiểm chứng bằng nguồn cho hồ sơ này; chưa đủ căn cứ để kết luận catalog không hỗ trợ.</p>':'';
 const items=values=>(values??[]).map(value=>`<li>${h(typeof value==='string'?value:JSON.stringify(value))}</li>`).join('')||'<li>Không có mục bổ sung trong profile; xem điều kiện của từng claim.</li>';
 const sources=(profile.compatibility_evidence??[]).map(item=>{const url=safeHttps(item.url);return `<li>${url?`<a href="${url}" target="_blank" rel="noopener noreferrer">Nguồn đường tích hợp</a>`:h(item.url)} · ${h(item.locator??'')}</li>`;}).join('');
 return `<section data-implementation-profile="${h(profile.id)}"><h4>Đường tích hợp có bằng chứng: ${reference(profile.id)}</h4>${summary?`<p>Yêu cầu chức năng có chứng cứ đạt: ${h(summary.hard_pass_count)}/${h(summary.hard_total)}; còn điều kiện: ${h(summary.hard_unknown_count)}; không đạt: ${h(summary.hard_failure_count)}. Phần này tách quota để đọc mức bao phủ chức năng; quota vẫn là HARD khi xét đủ điều kiện.</p>`:''}<p>Đây là mức phù hợp của thiết kế được tài liệu hỗ trợ, chưa phải chứng nhận triển khai thực tế. Các yêu cầu được chứng minh bằng claim bên dưới.</p><details><summary>Phạm vi, điều kiện triển khai và nguồn</summary><pre>${h(JSON.stringify(profile.context,null,2))}</pre><h4>Điều kiện cần</h4><ul>${items(profile.prerequisites)}</ul><h4>Điều kiện phiên bản</h4><ul>${items(profile.version_conditions)}</ul><h4>Nguồn tương thích toàn đường</h4><ul>${sources}</ul><p>Claim của profile: ${(profile.claim_ids??[]).map(reference).join(', ')}.</p></details></section>`;
}
function decisionPanel(){
 const summary=result.decision_summary;if(!summary)return '';
 const byId=new Map(Object.values(result.groups).flat().map(row=>[row.candidate_id,row]));
 const names=(summary.documented_fit_candidate_ids??[]).map(id=>byId.get(id)?.name??id);
 return `<section class="report-section"><h2>Kết luận theo bằng chứng hiện có</h2><p>${names.length?`Đường tích hợp có nguồn đáp ứng yêu cầu đã khai báo: ${names.map(h).join(', ')}.`:'Chưa có đường tích hợp được chứng minh đáp ứng toàn bộ yêu cầu đã khai báo.'}</p><p>Đánh giá mức phù hợp của thiết kế trong phạm vi profile, chưa xác nhận hạ tầng đã triển khai. Các ứng viên còn điều kiện cần thêm bằng chứng; chưa thể hiểu là không hỗ trợ.</p>${summary.no_soft_ranking?'<p>Hồ sơ không có tiêu chí SOFT nên không tạo điểm hoặc người thắng bằng số.</p>':''}</section>`;
}
function comparisonPanel(){
 const scenario=result.scenarios;
 if(scenario?.comparison_scope!=='evidenced_joint_profiles_with_resolved_user_context')return '';
 const compared=scenario.comparison_candidate_ids??[],omitted=scenario.candidates_not_compared??[];
 const insufficient=scenario.status==='insufficient_verified_implementations_for_comparison';
 return `<section class="report-section" data-comparison-scope="${h(scenario.comparison_scope)}"><h2>Phạm vi so sánh kịch bản</h2><p>Chỉ so sánh các ứng viên có đường tích hợp có nguồn và dữ kiện người dùng đã xác định: ${h(compared.length)} ứng viên. Đây chưa phải xếp hạng đầy đủ cả bảy catalog.</p>${insufficient?'<p role="status">Chưa đủ phương án đã kiểm chứng, nên chưa có so sánh tỷ lệ đứng đầu hoặc regret. Khoảng điểm SOFT vẫn được giữ theo bằng chứng hiện có.</p>':result.decision_summary?.no_soft_ranking?'<p>Không có tiêu chí SOFT nên chưa có so sánh tỷ lệ đứng đầu hoặc regret.</p>':''}${omitted.length?`<details><summary>Các ứng viên chưa được đưa vào so sánh và lý do</summary><pre>${h(JSON.stringify(omitted,null,2))}</pre></details>`:''}</section>`;
}
function reasonList(row){
 const requirements=new Map([...(result.requirements?.requirements??[]),...(result.requirements?.objectives??[])].map(r=>[r.id,r]));
 const rows=[['hard_failures','Không đạt HARD'],['hard_conditions','Chưa đủ bằng chứng cho HARD'],['hard_passes','Đáp ứng HARD trong phạm vi đã khai báo']].flatMap(([key,text])=>(row[key]??[]).map(reason=>{
  const req=requirements.get(reason.requirement_id),qid=req?.source_inputs?.[0],title=registry.questions.find(q=>q.id===qid)?.label??req?.property_id??reason.requirement_id;
  return `<li><strong>${h(title)}</strong>: ${h(text)}. Yêu cầu ${reference(reason.requirement_id)}; ${reason.claim_ids.length?'claim '+reason.claim_ids.map(reference).join(', '):'chưa có claim khớp'}.</li>`;
 }));
 for(const reason of row.input_conditions??[]){
  const input=reason.source_input??reason.context_key??'Đường tích hợp';
  const explanation=reason.type==='implementation_path_unverified'?'chưa có bằng chứng cho một đường tích hợp tương thích toàn bộ':reason.type==='implementation_context_unknown'?'thiếu dữ kiện để xác nhận phạm vi của đường tích hợp':'thông tin chưa rõ; chưa thể coi là không cần';
  rows.push(`<li>${h(input)}: ${h(explanation)}${reason.input_ref?` (${reference(reason.input_ref)})`:''}; ${(reason.claim_ids??[]).length?'claim '+reason.claim_ids.map(reference).join(', '):'chưa có claim xác nhận điều kiện này'}.</li>`);
 }
 for(const reason of row.score_trace??[])rows.push(`<li>SOFT ${reference(reason.requirement_id)}: trọng số ${h(reason.weight)}, mức [${h(reason.level_interval.min)}, ${h(reason.level_interval.max)}]; ${reason.claim_ids.length?'claim '+reason.claim_ids.map(reference).join(', '):'chưa có claim khớp'}.</li>`);
 return `<ul class="reason-list">${rows.join('')}</ul>`;
}
function questionControl(q){
 const value=draft[q.id];
 if(q.control==='engine_operations'){
  const engines=draft.I02??[];
  if(!engines.length)return '<p>Chọn engine ở I02 trước. Không có đáp án sẽ giữ là chưa rõ, không tự coi là chỉ đọc.</p>';
  return engines.map(engine=>`<fieldset><legend>${h(label('I02',engine))}</legend><div class="choice-grid">${q.answers.map(a=>`<label class="choice"><input type="checkbox" name="I12-${h(engine)}" value="${h(a.id)}" ${value?.[engine]?.includes(a.id)?'checked':''}><span>${h(a.label)}</span></label>`).join('')}</div></fieldset>`).join('');
 }
 if(q.control==='features'){
  const selected=value?.selected??[];
  return q.answers.map(a=>{
   if(a.id==='none')return `<label class="choice"><input type="checkbox" name="I10-none" value="none" ${value?.none?'checked':''}><span>${h(a.label)}</span></label>`;
   const item=selected.find(x=>x.feature===a.id);
   return `<div class="priority-row"><label class="choice"><input type="checkbox" name="I10-feature" value="${h(a.id)}" ${item?'checked':''}><span>${h(a.label)}</span></label><select class="select-input" name="I10-rank-${h(a.id)}" aria-label="Mức ưu tiên: ${h(a.label)}"><option value="">Chọn mức ưu tiên</option>${q.ranks.map(r=>`<option value="${r.id}" ${item?.rank===r.id?'selected':''}>${h(r.label)}</option>`).join('')}</select></div>`;
  }).join('');
 }
 return `<div class="choice-grid">${q.answers.map(a=>`<label class="choice"><input type="${q.control==='multi'?'checkbox':'radio'}" name="${q.id}" value="${h(a.id)}" ${(Array.isArray(value)?value.includes(a.id):value===a.id)?'checked':''}><span>${h(a.label)}</span></label>`).join('')}</div>`+(q.id==='I04'?`<label for="table-count-exact">Số bảng chính xác (nếu biết)</label><input class="text-input" type="number" id="table-count-exact" name="table_count_exact" step="1" min="1" value="${h(contextDraft.table_count_exact??'')}" aria-describedby="exact-count-help"><small id="exact-count-help">Có thể để trống. Số chính xác phải nằm trong khoảng đã chọn; không tự thay thế bằng cận trên của khoảng.</small>`:'');
}
function renderForm(){
 const help=settings.default_environment_facts_as_hard?'Với I01–I03 cụ thể: đã coi lựa chọn này là bắt buộc. Đa cloud, Hỗn hợp, Khác vẫn chưa rõ.':'I01–I03 được giữ làm bối cảnh theo cờ config; không tự tạo HARD.';
 return heading('Hồ sơ yêu cầu','Một lần nhập theo đúng registry form v3.', '<a class="btn" href="#report">Xem bản đánh giá</a>')+tabs()+`<p class="form-intro">${h(help)} Nice-to-have dùng trọng số thấp từ config. Khai báo storage và thao tác từng engine; không cần chọn API. Lab cục bộ khác on-prem sản xuất. Số bảng vẫn là yêu cầu HARD; thiếu bằng chứng quota giữ kết luận có điều kiện.</p><form id="profile-form" class="survey" novalidate><section class="form-section"><div class="form-section-heading"><div><h2>Yêu cầu của bạn</h2><p>Đáp án được giữ theo ID; backend sẽ giữ rõ thông tin chưa biết.</p></div></div>${registry.questions.filter(q=>q.enabled).map(q=>`<div class="form-field"><div class="field-label" id="label-${q.id}">${q.id} · ${h(q.label)}${q.optional?'<small>Tùy chọn</small>':''}</div><div class="field-control" role="group" aria-labelledby="label-${q.id}">${questionControl(q)}</div></div>`).join('')}</section><div id="form-errors" role="alert" tabindex="-1"></div><div class="form-bottom"><p>Đánh giá bằng Python trên KB hiện tại. I06 streaming đang bất hoạt. Thiếu bằng chứng được giữ là chưa rõ.</p><button type="submit" class="btn btn-primary" ${busy?'disabled':''}>Xem kết quả đánh giá${icon('arrow')}</button></div></form>`+footer();
}
function renderReport(){
 const head=heading('Lựa chọn catalog cho lakehouse','Kết quả chỉ được đọc từ backend chính thức.', '<a class="btn btn-primary" href="#form">Chỉnh sửa yêu cầu</a>')+tabs();
 if(!result)return head+`<section class="empty-result" role="status"><h2>${busy?'Đang đánh giá trên backend':backendError?'Không hoàn tất đánh giá':'Chưa có kết quả từ backend'}</h2><p>${h(backendError||'Điền form và gửi để chạy Lớp 2 và Lớp 3 chính thức.')}</p><a class="btn" href="#form">Mở form</a></section>`+footer();
 if(result.status==='input_error')return head+`<section role="alert"><h2>Cần sửa câu trả lời</h2><pre>${h(JSON.stringify(result.input_issues,null,2))}</pre><a class="btn" href="#form">Sửa form</a></section>`+footer();
 const names={eligible:'Đủ điều kiện',conditional:'Còn điều kiện',excluded:'Bị loại'};
 const percent=value=>value==null?'Không áp dụng':new Intl.NumberFormat('vi',{style:'percent'}).format(value);
 return head+`<p>${result.synthetic_data?'DỮ LIỆU TỔNG HỢP · ':''}KB: ${h(result.kb_revision??'synthetic')}. Tỷ lệ đứng đầu là tỷ lệ trong các kịch bản giả định, chưa là xác suất phù hợp thực tế.</p>${!result.groups.eligible.length?'<p role="status">Chưa có ứng viên đủ điều kiện chắc chắn. Xem điều kiện và gợi ý nới phía dưới.</p>':''}`+decisionPanel()+comparisonPanel()+Object.entries(names).map(([group,title])=>`<section class="report-section" data-group="${group}"><h2>${title}</h2>${result.groups[group].map(row=>`<article class="catalog-row" data-candidate="${h(row.candidate_id)}"><div><h3>${h(row.name??row.candidate_id)}</h3><p class="score-interval">${row.score_interval?`Khoảng điểm tuyệt đối [${h(row.score_interval.join(', '))}]`:'Không có điểm SOFT áp dụng'}</p>${group!=='excluded'?`<p>Tỷ lệ đứng đầu kịch bản: ${h(percent(row.top_rate))}. Regret lớn nhất quan sát: ${h(row.max_regret_observed??'Không áp dụng')}; cận trên: ${h(row.regret_upper_bound??'Không áp dụng')}.</p>`:''}<p>HARD đạt: ${row.hard_passes.length}; còn điều kiện: ${row.hard_conditions.length}; không đạt: ${row.hard_failures.length}.</p>${implementationPanel(row)}${reasonList(row)}<details><summary>Lý do, yêu cầu và claim</summary><pre>${h(JSON.stringify({hard_failures:row.hard_failures,hard_conditions:row.hard_conditions,hard_passes:row.hard_passes,input_conditions:row.input_conditions,score_trace:row.score_trace,assessments:row.assessments},null,2))}</pre></details></div></article>`).join('')||'<p>Không có ứng viên trong nhóm này.</p>'}</section>`).join('')+`<section class="report-section"><h2>Khoảng điểm giao nhau</h2><p>Các cặp sau có khoảng điểm chồng lấn; chưa có thứ tự chắc chắn từ khoảng điểm.</p><pre>${h(JSON.stringify(result.score_overlaps??[],null,2))}</pre></section>`+(result.relaxations?.length?`<section class="report-section" id="relaxations"><h2>Gợi ý nới yêu cầu từ backend</h2><p>Chỉ là chẩn đoán; không tự sửa câu trả lời. Nới một yêu cầu có thể vẫn chưa đủ.</p><pre>${h(JSON.stringify(result.relaxations,null,2))}</pre></section>`:'')+`<details><summary>Unknown theo ảnh hưởng đến người đứng đầu</summary><pre>${h(JSON.stringify({scenario_mode:result.scenarios?.mode,scenario_count:result.scenarios?.scenario_count,unknowns:result.unknowns,unresolved_inputs:result.unresolved_inputs},null,2))}</pre></details><details><summary>Payload đã gửi</summary><pre id="submitted-payload">${h(JSON.stringify(submitted,null,2))}</pre></details>`+footer();
}
function renderInfo(view){
 return heading(view==='assumptions'?'Giả định và giới hạn':view==='method'?'Phương pháp':'Bằng chứng và nguồn','Đọc từ cùng kết quả Python chính thức.')+tabs()+`<div class="info-document"><div class="prose"><p>Form → ánh xạ Lớp 2 → kiểm tra hợp đồng → tra claim và đường tích hợp có nguồn → lọc HARD → điểm SOFT tuyệt đối → kịch bản có seed. Thiếu claim là unknown.</p><p>Form v3 có thể đề xuất một profile tương thích có bằng chứng cho các scope đã nghiên cứu; không ghép đường tốt nhất của từng thuộc tính thành một giải pháp. Chưa có đánh giá độc lập hoặc xác nhận hạ tầng đã triển khai.</p>${result?`<pre>${h(JSON.stringify(view==='evidence'||view==='knowledge'?{requirements:result.requirements,groups:result.groups}:{assumptions:result.assumptions,profile_assumptions:result.profile_assumptions,input_revisions:result.input_revisions,limits:result.limits},null,2))}</pre>`:'<p>Gửi form để xem bằng chứng và giả định của ca cụ thể.</p>'}</div></div>`+footer();
}
function render(){
 const view=location.hash.slice(1)||'form';
 main.innerHTML=view==='form'?renderForm():view==='report'?renderReport():renderInfo(view);
 document.querySelectorAll('[data-icon]').forEach(el=>el.innerHTML=icon(el.dataset.icon));
 const count=document.querySelector('.nav-count');if(count)count.textContent=String(registry.questions.filter(q=>q.enabled).length);
}
function readDraft(form){
 const data=new FormData(form),next={};
 for(const q of registry.questions.filter(q=>q.enabled)){
  if(q.control==='engine_operations'){
   const selected={};
   for(const engine of next.I02??[])if(data.has(`I12-${engine}`))selected[engine]=data.getAll(`I12-${engine}`);
   if(Object.keys(selected).length)next[q.id]=selected;
  }else if(q.control==='features'){
   const selected=data.getAll('I10-feature').map(feature=>({feature,rank:data.get(`I10-rank-${feature}`)||null}));
   if(selected.length||data.has('I10-none'))next[q.id]={none:data.has('I10-none'),selected};
  }else if(q.control==='multi'){
   if(data.has(q.id))next[q.id]=data.getAll(q.id);
  }else if(data.has(q.id))next[q.id]=data.get(q.id);
 }
 return next;
}
function readContext(form){const value=new FormData(form).get('table_count_exact');return value!==null&&String(value).trim()!==''?{table_count_exact:Number(value)}:{};}
document.addEventListener('change',event=>{const form=event.target.closest('#profile-form');if(form){draft=readDraft(form);contextDraft=readContext(form);if(event.target.name==='I02'){const target=form.querySelector('[aria-labelledby="label-I12"]');target.innerHTML=questionControl(registry.questions.find(q=>q.id==='I12'));}}});
document.addEventListener('submit',async event=>{
 if(event.target.id!=='profile-form')return;
 event.preventDefault();draft=readDraft(event.target);contextDraft=readContext(event.target);
 const payload=buildPayload(draft,registry,contextDraft),issues=validatePayload(payload,registry,settings);
 if(issues.length){const box=document.querySelector('#form-errors');box.className='form-errors';box.innerHTML=issues.map(x=>`${h(x.field)}: ${h(x.message)}`).join('<br>');box.scrollIntoView({block:'center'});box.focus();return;}
 if(busy)return;
 submitted=payload;result=null;busy=true;backendError='';const current=++requestId;
 try{localStorage.setItem(storageKey,JSON.stringify(payload));}catch{}
 window.dispatchEvent(new CustomEvent('catalog-form-submit',{detail:structuredClone(payload)}));
 location.hash='report';render();
 try{
  const response=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const data=await response.json();if(current!==requestId)return;
  if(!response.ok&&data.status!=='input_error')throw new Error(data.message||'Backend không hoàn tất đánh giá.');
  result=acceptBackendResult(data);
  window.dispatchEvent(new CustomEvent('catalog-backend-result',{detail:structuredClone(result)}));
 }catch(error){if(current===requestId)backendError=error.message;}
 finally{if(current===requestId){busy=false;render();}}
});
window.addEventListener('catalog-backend-result',event=>{
 try{result=acceptBackendResult(event.detail);location.hash='report';render();}
 catch(error){document.querySelector('#toast').textContent=error.message;}
});
window.addEventListener('hashchange',()=>{render();main.focus({preventScroll:true});});
document.querySelector('#new-profile').addEventListener('click',()=>{++requestId;busy=false;draft={};contextDraft={};submitted=null;result=null;backendError='';try{localStorage.removeItem(storageKey);}catch{}location.hash='form';render();});
document.querySelector('#workspace-switch').addEventListener('click',()=>{location.hash='form';});
try{
 const responses=await Promise.all([fetch('/form-v3-registry.json'),fetch('/layer2-runtime-config.json')]);
 if(responses.some(r=>!r.ok))throw new Error('Không tải được registry/config form v3.');
 [registry,settings]=await Promise.all(responses.map(r=>r.json()));
 try{const saved=JSON.parse(localStorage.getItem(storageKey));if(saved&&!validatePayload(saved,registry,settings).length){submitted=saved;draft=structuredClone(saved.answers);contextDraft=structuredClone(saved.context??{});}}catch{}
 render();
}catch(error){main.innerHTML=heading('Không tải được form v3',error.message);}
