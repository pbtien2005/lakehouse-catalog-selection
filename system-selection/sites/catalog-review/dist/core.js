// Form contract / presentation only. Decisions come from the official backend.
export function buildPayload(draft, registry, context) {
  const answers = {};
  for (const question of registry.questions) {
    if (question.enabled && Object.hasOwn(draft, question.id)) answers[question.id] = structuredClone(draft[question.id]);
  }
  const payload={form_revision:registry.manifest.form_revision, answers};
  if(registry.manifest.form_revision==='input-v3'&&context&&Object.keys(context).length)payload.context=structuredClone(context);
  return payload;
}

export function validatePayload(payload, registry, config) {
  const issues = [];
  const add = (code,field,message) => issues.push({code,field,message});
  if (!payload || payload.form_revision !== registry.manifest.form_revision) add('E_FORM_REVISION','form_revision',`Dùng đúng ${registry.manifest.form_revision}.`);
  const answers = payload?.answers;
  if (!answers || typeof answers !== 'object' || Array.isArray(answers)) return [...issues,{code:'E_PAYLOAD',field:'answers',message:'answers phải là object.'}];
  const questions = new Map(registry.questions.map(q=>[q.id,q]));
  for (const id of Object.keys(answers)) if (!questions.has(id)) add('E_UNKNOWN_FIELD',`answers.${id}`,'Bỏ trường ngoài form v2.');
  for (const question of registry.questions) {
    const id=question.id, value=answers[id], field=`answers.${id}`;
    if (value == null) continue;
    const allowed = new Set(question.answers.map(a=>a.id));
    const valid = (answer,path) => {
      if (registry.legacy_answer_ids.includes(answer)) add('E_LEGACY_FORM_ANSWER',path,'Đáp án cũ cần chọn lại.');
      else if (!allowed.has(answer)) add('E_INVALID_ANSWER',path,'Chọn ID đáp án trong form v2.');
    };
    if(question.control==='engine_operations') {
      if(!value||typeof value!=='object'||Array.isArray(value)){add('E_CARDINALITY',field,'Dùng danh sách thao tác cho từng engine.');continue;}
      for(const [engine,operations] of Object.entries(value)){
        const path=`${field}.${engine}`;
        if(!Array.isArray(answers[question.engine_question])||!answers[question.engine_question].includes(engine))add('E_ENGINE_NOT_SELECTED',path,'Chọn engine ở I02 trước khi khai báo thao tác.');
        else if(!Array.isArray(operations)||!operations.length)add('E_CARDINALITY',path,'Chọn thao tác hoặc Chưa rõ.');
        else{
          operations.forEach((operation,i)=>valid(operation,`${path}[${i}]`));
          if(new Set(operations).size!==operations.length)add('E_DUPLICATE_SELECTION',path,'Mỗi thao tác chỉ chọn một lần.');
          if(operations.includes(question.exclusive_answer)&&operations.length>1)add('E_EXCLUSIVE_UNKNOWN',path,'Chưa rõ không được chọn cùng thao tác cụ thể.');
        }
      }
    } else if(question.control==='single') {
      if(typeof value!=='string') add('E_CARDINALITY',field,'Chỉ chọn một đáp án.'); else valid(value,field);
    } else if(question.control==='multi') {
      if(!Array.isArray(value)) {add('E_CARDINALITY',field,'Dùng danh sách đáp án.');continue;}
      value.forEach((v,i)=>valid(v,`${field}[${i}]`));
      if(new Set(value).size!==value.length) add('E_DUPLICATE_SELECTION',field,'Mỗi đáp án chỉ chọn một lần.');
      if(question.exclusive_answer && value.includes(question.exclusive_answer)&&value.length>1) add('E_EXCLUSIVE_NONE',field,'Chọn Không hoặc các mục cụ thể, không đồng thời.');
      if(!value.length&&!question.optional) add('E_CARDINALITY',field,'Chọn ít nhất một engine.');
    } else {
      if(!value||typeof value!=='object'||Array.isArray(value)||!Array.isArray(value.selected??[])) {add('E_CARDINALITY',field,'Dùng none và selected.');continue;}
      if(Object.keys(value).some(k=>!['none','selected'].includes(k))||typeof (value.none??false)!=='boolean') add('E_INVALID_ANSWER',field,'none phải là boolean; chỉ nhận none và selected.');
      if(value.none&&value.selected?.length) add('E_EXCLUSIVE_NONE',field,'Không có nhu cầu nào không được chọn cùng nhu cầu cụ thể.');
      const seen=new Set();
      for(const [i,item] of (value.selected??[]).entries()) {
        const path=`${field}.selected[${i}]`;
        if(!item||typeof item!=='object'||Array.isArray(item)) {add('E_INVALID_ANSWER',path,'Mỗi mục cần feature và rank.');continue;}
        valid(item.feature,path+'.feature');
        if(item.feature==='none'||Object.keys(item).some(k=>!['feature','rank'].includes(k))) add('E_INVALID_ANSWER',path,'none là cờ riêng.');
        if(seen.has(item.feature)) add('E_DUPLICATE_SELECTION',path+'.feature','Mỗi nhu cầu chỉ chọn một lần.');
        seen.add(item.feature);
        if(!question.ranks.some(r=>r.id===item.rank)) add('E_RANK_MISSING_OR_INVALID',path+'.rank','Chọn Bắt buộc hoặc Nice-to-have cho nhu cầu đã chọn.');
      }
    }
  }
  if(registry.manifest.form_revision==='input-v3'){
    for(const key of Object.keys(payload))if(!['form_revision','answers','context'].includes(key))add('E_UNKNOWN_FIELD',key,'Trường ngoài hợp đồng form v3.');
    if(payload.context!==undefined){
      const context=payload.context;
      if(!context||typeof context!=='object'||Array.isArray(context))add('E_PAYLOAD','context','context phải là object.');
      else{
        for(const key of Object.keys(context))if(key!=='table_count_exact')add('E_UNKNOWN_FIELD',`context.${key}`,'Trường ngoài context form v3.');
        if(Object.hasOwn(context,'table_count_exact')){
          const exact=context.table_count_exact,interval=config?.table_count_intervals?.[answers.I04];
          if(!Number.isSafeInteger(exact)||exact<=0)add('E_TABLE_COUNT','context.table_count_exact','Nhập số nguyên dương hoặc để trống nếu chưa biết.');
          else if(!answers.I04||(interval&&(exact<interval.lower||(interval.upper!==null&&exact>interval.upper))))add('E_TABLE_COUNT_BUCKET','context.table_count_exact','Số bảng chính xác phải thuộc khoảng đã chọn ở I04.');
        }
      }
    }
  }
  return issues;
}

export function acceptBackendResult(value) {
  if (!value || !value.groups || !['eligible','conditional','excluded'].every(key=>Array.isArray(value.groups[key]))) throw new TypeError('Backend result needs eligible / conditional / excluded groups.');
  return structuredClone(value);
}
