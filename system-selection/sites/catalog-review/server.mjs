import http from 'node:http';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import {spawn} from 'node:child_process';
const root = path.resolve('dist');
const projectRoot=path.resolve('../../research/catalog-reasoner-mvp');
const settings=JSON.parse(await readFile(path.join(projectRoot,'mvp-settings.json'),'utf8')).transport;
let activeRequests=0;
const json=(res,status,data)=>res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}).end(JSON.stringify(data));
async function runOfficial(req,res){
 if(req.method!=='POST')return json(res,405,{status:'input_error',message:'Use POST /api/run.'});
 if(req.headers.origin && req.headers.origin!==`http://${req.headers.host}`)return json(res,403,{status:'input_error',message:'Origin is not allowed.'});
 if(!req.headers['content-type']?.startsWith('application/json'))return json(res,415,{status:'input_error',message:'Use application/json.'});
 if(activeRequests>=settings.max_active_requests)return json(res,503,{status:'busy',message:'Một đánh giá đang chạy; thử lại sau.'});
 let chunks=[],size=0;
 for await(const chunk of req){size+=chunk.length;if(size>settings.request_max_bytes)return json(res,413,{status:'input_error',message:'Payload quá lớn.'});chunks.push(chunk);}
 let payload;try{payload=JSON.parse(Buffer.concat(chunks).toString('utf8'));}catch{return json(res,400,{status:'input_error',message:'JSON không hợp lệ.'});}
 activeRequests++;
 try{
  const output=await new Promise((resolve,reject)=>{
   const child=spawn(process.env.CATALOG_PYTHON||'python',['-X','utf8','-m','catalog_reasoner.project_io'],{cwd:projectRoot,windowsHide:true,stdio:['pipe','pipe','pipe'],shell:false});
   const chunks=[];let bytes=0;
   const timer=setTimeout(()=>{child.kill();reject(new Error('timeout'));},settings.process_timeout_ms);
   child.stdout.on('data',chunk=>{bytes+=chunk.length;if(bytes>settings.output_max_bytes){child.kill();reject(new Error('output_limit'));}else chunks.push(chunk);});
   child.stderr.resume();child.stdin.on('error',()=>{});
   child.on('error',error=>{clearTimeout(timer);reject(error);});
   child.on('close',()=>{clearTimeout(timer);try{resolve(JSON.parse(Buffer.concat(chunks).toString('utf8')));}catch{reject(new Error('invalid_backend_response'));}});
   child.stdin.end(JSON.stringify(payload));
  });
  return json(res,output.status==='ok'?200:output.status==='input_error'?422:500,output);
 }catch{return json(res,500,{status:'backend_error',message:'Không chạy được Python backend. Kiểm tra CATALOG_PYTHON và log khởi động.'});}
 finally{activeRequests--;}
}
const shared = {
  '/form-v2-registry.json': path.resolve('../../research/catalog-knowledge-base/form-v2-registry.json'),
  '/form-v3-registry.json': path.resolve('../../research/catalog-knowledge-base/form-v3-registry.json'),
  '/layer2-runtime-config.json': path.resolve('../../research/catalog-knowledge-base/layer-2-runtime-config.json'),
};
const mime = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.svg': 'image/svg+xml', '.woff2': 'font/woff2' };
const server = http.createServer(async (req, res) => {
  try {
    const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if(pathname==='/api/run')return await runOfficial(req,res);
    if (Object.hasOwn(shared, pathname)) {
      const data = await readFile(shared[pathname]);
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }).end(data);
      return;
    }
    const file = path.resolve(root, '.' + (pathname === '/' ? '/index.html' : pathname));
    if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
    const data = await readFile(file);
    res.writeHead(200, { 'Content-Type': mime[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' }).end(data);
  } catch { res.writeHead(404).end('Not found'); }
});
server.listen(Number(process.env.PORT ?? settings.port), '127.0.0.1', () => console.log(`Local: http://127.0.0.1:${server.address().port}`));
