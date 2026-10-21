import { createHash, timingSafeEqual, randomUUID, randomBytes } from 'node:crypto';
const adminSecret = process.env.ZTM_ADMIN_BOOTSTRAP_TOKEN || '';
function response(data,status=200,headers={}){return new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json','Cache-Control':'no-store',...headers}})}
function digest(s){return createHash('sha256').update(s).digest('hex')}
function sameToken(s){if(adminSecret.length<32||!s.startsWith('Bearer '))return false;const a=Buffer.from(digest(s.slice(7)),'hex'),b=Buffer.from(digest(adminSecret),'hex');return timingSafeEqual(a,b)}
function auth(request){if(adminSecret.length<32)return response({error:'Administrator credentials not configured'},503);if(!sameToken(request.headers.get('authorization')||''))return response({error:'Forbidden'},403);return null}
async function sql(query,params=[]){
  const uri=process.env.DATABASE_URL;
  if(!uri)throw new Error('Database not configured');
  const u=new URL(uri),host=u.hostname.replace('-pooler.','.');
  const r=await fetch('https://'+host+'/sql',{method:'POST',headers:{'Neon-Connection-String':uri,'Neon-Raw-Text-Output':'true','Neon-Array-Mode':'true'},body:JSON.stringify({query,params})});
  const data=await r.json();
  if(!r.ok){const err=new Error('Database request failed');err.code=data.code;throw err}
  const fields=(data.fields||[]).map(f=>f.name);
  return (data.rows||[]).map(row=>Object.fromEntries(row.map((val,i)=>[fields[i],val])));
}
async function body(request){
  const t=request.headers.get('content-type')||'';
  if(!t.toLowerCase().startsWith('application/json'))throw new Error('Content type');
  const n=Number(request.headers.get('content-length')||0);
  if(n>1024*1024)throw new Error('Oversized');
  const text=await request.text();
  if(text.length>1024*1024)throw new Error('Oversized');
  return JSON.parse(text);
}
const dashboard="<!doctype html>\n<html lang=\"en\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n<title>I2PS ZTM Intelligence | Fleet Monitor</title>\n<style>\n:root{font-family:system-ui,-apple-system,sans-serif;color:#f2f8ff;background:#070e18}\n*{box-sizing:border-box}body{margin:0}header{background:#0c1b2d;border-bottom:1px solid #234761;padding:18px 4%;display:flex;align-items:center;gap:16px;flex-wrap:wrap}\nheader strong{font-size:22px;letter-spacing:.015em}header strong span{color:#39bfff}header small{color:#8dafc7}\nnav{display:flex;gap:8px}nav a{color:#b9d1e3;text-decoration:none;padding:9px;border-radius:8px}nav a:hover{background:#16334b}\nmain{max-width:1450px;margin:0 auto;padding:26px 4%}\nh1{font-size:26px;margin:8px 0}h2{font-size:18px;margin:0 0 14px}.muted{color:#9eb5c8}button,input{font:inherit;border:1px solid #31536a;color:#f2f8ff;background:#11263a;padding:10px 13px;border-radius:8px}button{cursor:pointer}button.primary{background:#1976ff;border-color:#1976ff}button:hover{filter:brightness(1.15)}\n#login{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}#login input{flex:1;max-width:400px}\n.cards{display:grid;grid-template-columns:repeat(4,minmax(150px,1fr));gap:14px}.panel,.card{background:#0c1b2d;border:1px solid #1e4058;border-radius:13px;padding:19px}.card label{font-size:12px;color:#9eb5c8}.card b{font-size:27px;display:block;margin-top:8px}.sections{display:grid;grid-template-columns:340px minmax(0,1fr);gap:16px;margin-top:18px}\n#workerList{max-height:600px;overflow:auto}.worker{display:block;text-align:left;width:100%;margin:6px 0;padding:12px}.worker.selected{border-color:#39bfff;background:#173b57}.worker .sub{font-size:12px;color:#98b6c9;margin-top:4px}.status{font-size:12px;float:right;color:#9eb5c8}.status.active{color:#55dfac}.status.stale{color:#ffd17a}\n.metricnav{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}canvas{width:100%;height:240px;border:1px solid #24415a;border-radius:8px;background:#071829}\ntable{width:100%;border-collapse:collapse;font-size:13px}td,th{border-bottom:1px solid #24455c;padding:10px 8px;text-align:left}th{color:#7fd8ff}#alert{min-height:20px;color:#ffd17a}\n@media(max-width:950px){.sections{grid-template-columns:1fr}.cards{grid-template-columns:repeat(2,1fr)}}@media(max-width:470px){.cards{grid-template-columns:1fr 1fr}.card b{font-size:21px}}\n</style>\n<header><strong>I2PS <span>ZTM INTELLIGENCE</span></strong><small>Engineering Fleet Monitor</small><nav><a href=\"#fleet\">Fleet</a><a href=\"#details\">Worker detail</a><a href=\"#history\">Benchmarks</a></nav></header>\n<main>\n<h1>Fleet Overview</h1><p class=\"muted\">Authenticated telemetry. A worker is active only when its latest heartbeat is within 150 seconds.</p>\n<div id=\"login\"><input type=\"password\" id=\"token\" placeholder=\"I2PS administrator access token\" autocomplete=\"off\"><button class=\"primary\" id=\"load\">Connect</button><button id=\"refresh\">Refresh</button></div><p id=\"alert\" role=\"status\"></p>\n<div class=\"cards\"><div class=\"card\"><label>Registered workers</label><b id=\"registered\">-</b></div><div class=\"card\"><label>Active workers</label><b id=\"active\">-</b></div><div class=\"card\"><label>Current fleet hashrate</label><b id=\"hashrate\">-</b></div><div class=\"card\"><label>Submitted benchmarks</label><b id=\"runs\">-</b></div></div>\n<div class=\"sections\"><section class=\"panel\" id=\"fleet\"><h2>Workers</h2><input id=\"search\" placeholder=\"Search ID, CPU, status\" style=\"width:100%\"><div id=\"workerList\" role=\"list\"></div></section>\n<section class=\"panel\" id=\"details\"><h2 id=\"workerTitle\">Select a worker</h2><div id=\"workerFacts\" class=\"muted\">No worker selected.</div>\n<div class=\"metricnav\"><button data-metric=\"hashrate_hs\">Hashrate</button><button data-metric=\"temperature_c\">Temperature</button><button data-metric=\"cpu_percent\">CPU %</button><button data-metric=\"ram_percent\">RAM %</button></div>\n<canvas id=\"chart\" width=\"900\" height=\"240\" aria-label=\"Worker measurement history\"></canvas><p class=\"muted\" id=\"chartNote\">Historical samples appear when a worker reports them.</p>\n<h2 id=\"history\">Benchmark History</h2><table><thead><tr><th>Time</th><th>Run ID</th><th>Threads</th><th>Mean H/s</th><th>Status</th></tr></thead><tbody id=\"historyRows\"><tr><td colspan=\"5\">No benchmark selected.</td></tr></tbody></table></section></div>\n</main>\n<script>\nconst el=id=>document.getElementById(id);let token='',workers=[],chosen=null,details=null,metric='hashrate_hs';\nfunction value(x){return x===null||x===undefined||x===''?'--':String(x)}\nfunction rate(n){return Number.isFinite(Number(n))?Number(n).toLocaleString(undefined,{maximumFractionDigits:1})+' H/s':'--'}\nasync function get(path){const r=await fetch(path,{headers:{Authorization:'Bearer '+token},cache:'no-store'});if(!r.ok)throw Error('API '+r.status);return r.json()}\nfunction node(tag,text,cls){const e=document.createElement(tag);e.textContent=text;if(cls)e.className=cls;return e}\nfunction draw(){\nconst list=el('workerList');list.replaceChildren();\nconst term=el('search').value.toLowerCase();\nfor(const w of workers.filter(w=>[w.ztm_id,w.cpu_model,w.connection_status,w.state].join(' ').toLowerCase().includes(term))){\nconst b=node('button','');b.type='button';b.className='worker'+(chosen===w.ztm_id?' selected':'');\nconst top=node('div',w.ztm_id+'  '+value(w.cpu_model));const status=node('span',value(w.connection_status),'status '+w.connection_status);\ntop.prepend(status);b.append(top,node('div',rate(w.hashrate_hs)+'  /  '+value(w.state),'sub'));b.onclick=()=>choose(w.ztm_id);list.append(b);\n}if(!list.children.length)list.append(node('p','No registered workers match this search.','muted'));\n}\nasync function choose(id){chosen=id;draw();el('workerTitle').textContent='Worker '+id;el('workerFacts').textContent='Loading';try{\ndetails=await get('/v1/admin/worker/'+encodeURIComponent(id));\nconst w=workers.find(w=>w.ztm_id===id);\nel('workerFacts').textContent=[value(w?.cpu_model),value(w?.connection_status),value(w?.state),rate(w?.hashrate_hs),'Last seen: '+value(w?.observed_at)].join('  |  ');\nconst rows=el('historyRows');rows.replaceChildren();\nfor(const run of details.runs||[]){const tr=document.createElement('tr');for(const x of [run.received_at,run.benchmark_id,run.winning_threads,run.sustained_mean_hs,run.verified?'Verified':'Unverified'])tr.append(node('td',value(x)));rows.append(tr)}\nif(!rows.children.length){const tr=node('tr','');const td=node('td','No benchmark submissions recorded.');td.colSpan=5;tr.append(td);rows.append(tr)}\nchart();\n}catch(e){el('alert').textContent='Worker request failed: '+e.message}}\nfunction chart(){\nconst c=el('chart'),ctx=c.getContext('2d'),W=c.width,H=c.height;ctx.clearRect(0,0,W,H);\nconst samples=(details?.telemetry||[]).filter(p=>p[metric]!==null&&p[metric]!==undefined);\nctx.fillStyle='#9bb3c7';ctx.font='14px sans-serif';\nif(!samples.length){ctx.fillText('No '+metric+' measurements received',25,H/2);el('chartNote').textContent='No values have been submitted for this metric.';return}\nconst vals=samples.map(p=>Number(p[metric])).filter(Number.isFinite);if(!vals.length)return;\nlet min=Math.min(...vals),max=Math.max(...vals);if(min===max){min-=1;max+=1}\nctx.strokeStyle='#274862';ctx.beginPath();for(let i=0;i<5;i++){const y=20+i*(H-45)/4;ctx.moveTo(35,y);ctx.lineTo(W-15,y)}ctx.stroke();\nctx.strokeStyle='#39bfff';ctx.lineWidth=2.5;ctx.beginPath();samples.forEach((p,i)=>{const x=35+i*(W-55)/Math.max(1,samples.length-1),y=H-25-(Number(p[metric])-min)/(max-min)*(H-45);if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y)});ctx.stroke();\nctx.fillStyle='#a5c9db';ctx.fillText(max.toFixed(1),4,15);ctx.fillText(min.toFixed(1),4,H-12);\nel('chartNote').textContent='Measured '+metric.replace('_',' ')+' | '+samples.length+' data points in the latest 24 hours. No interpolation of missing data.';\n}\nasync function load(){token=el('token').value.trim();if(!token){el('alert').textContent='Enter administrator credentials.';return}\nel('alert').textContent='Querying authenticated worker data...';\ntry{\nconst [fleet,stats]=await Promise.all([get('/v1/admin/workers'),get('/v1/admin/stats')]);workers=fleet.workers||[];\nel('registered').textContent=workers.length;el('active').textContent=workers.filter(w=>w.connection_status==='active').length;\nel('hashrate').textContent=rate(workers.filter(w=>w.connection_status==='active').reduce((s,w)=>s+(Number(w.hashrate_hs)||0),0));\nel('runs').textContent=stats.overview?.submitted_reports??0;el('alert').textContent='Authenticated fleet data loaded.';\ndraw();if(chosen&&workers.some(w=>w.ztm_id===chosen))await choose(chosen);else if(workers.length)await choose(workers[0].ztm_id);\n}catch(e){el('alert').textContent='Dashboard unavailable: '+e.message}\n}\nel('load').onclick=load;el('refresh').onclick=load;el('search').oninput=draw;\ndocument.querySelectorAll('[data-metric]').forEach(b=>b.onclick=()=>{metric=b.dataset.metric;chart()});\n</script></html>";
export default async function handler(request){
  const path=new URL(request.url).pathname;
  if(request.method==='GET'&&(path==='/'||path==='/dashboard'))return new Response(dashboard,{headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'}});
  if(request.method==='GET'&&path==='/health'){
    try{await sql('SELECT 1 AS ok');return response({service:'ztm-intelligence',status:'ok',database:'connected'})}catch{return response({service:'ztm-intelligence',status:'degraded',database:'unavailable'},503)}
  }
  if(request.method==='GET'&&path==='/v1/admin/stats'){
    const denial=auth(request);if(denial)return denial;
    try{const o=await sql('SELECT * FROM ztm_analytics_overview');const cpus=await sql('SELECT * FROM ztm_analytics_cpu ORDER BY submitted_runs DESC LIMIT 50');return response({overview:o[0]||{},cpus,verified_only:false})}catch{return response({error:'Statistics not available'},503)}
  }
  if(request.method==='GET'&&path==='/v1/admin/workers'){
    const denial=auth(request);if(denial)return denial;
    try{
      const workers=await sql("SELECT w.ztm_id,w.registered_at,w.last_seen,h.observed_at,h.state,h.hashrate_hs,h.temperature_c,h.cpu_percent,h.ram_percent,h.active_threads,CASE WHEN h.observed_at > now()-interval '150 seconds' THEN 'active' WHEN h.observed_at > now()-interval '5 minutes' THEN 'stale' ELSE 'offline' END AS connection_status,coalesce((SELECT e.report #>> '{hardware,cpu_model}' FROM ztm_ingested_events e WHERE e.worker_uuid=w.worker_uuid ORDER BY e.received_at DESC LIMIT 1),'Unknown') AS cpu_model FROM ztm_workers w LEFT JOIN ztm_worker_heartbeats h USING(worker_uuid) WHERE w.revoked_at IS NULL ORDER BY w.registered_at DESC LIMIT 500");
      return response({workers})
    }catch{return response({error:'Worker listing failed'},503)}
  }
  if(request.method==='GET'&&path.startsWith('/v1/admin/worker/')){
    const denial=auth(request);if(denial)return denial;
    const ztmId=path.slice('/v1/admin/worker/'.length).split('/')[0];
    if(!/^[A-HJ-NP-Z2-9]{5}$/.test(ztmId))return response({error:'Invalid worker ID'},422);
    try{
      const worker=await sql('SELECT worker_uuid,ztm_id,registered_at,last_seen FROM ztm_workers WHERE ztm_id=$1 AND revoked_at IS NULL',[ztmId]);
      if(!worker.length)return response({error:'Worker not found'},404);
      const id=worker[0].worker_uuid;
      const series=await sql("SELECT sampled_at,state,hashrate_hs,temperature_c,cpu_percent,ram_percent,active_threads,accepted_shares,rejected_shares FROM ztm_worker_telemetry WHERE worker_uuid=$1 AND sampled_at > now()-interval '24 hours' ORDER BY sampled_at DESC LIMIT 1440",[id]);
      const runs=await sql("SELECT event_id,received_at,verified,report #>> '{benchmark,run_id}' AS benchmark_id,report #>> '{winner,threads}' AS winning_threads,report #>> '{winner,sustained_mean_hs}' AS sustained_mean_hs FROM ztm_ingested_events WHERE worker_uuid=$1 ORDER BY received_at DESC LIMIT 50",[id]);
      const status=await sql('SELECT * FROM ztm_worker_heartbeats WHERE worker_uuid=$1',[id]);
      return response({worker:worker[0],heartbeat:status[0]||null,telemetry:series.reverse(),runs});
    }catch{return response({error:'Worker details unavailable'},503)}
  }
  if(request.method==='POST'&&path==='/v1/heartbeat'){
    const bearer=request.headers.get('authorization')||'';
    if(!/^Bearer [A-Za-z0-9_-]{50,}$/.test(bearer))return response({error:'Worker credential required'},401);
    let doc;try{doc=await body(request)}catch{return response({error:'Invalid heartbeat JSON'},422)}
    if(!doc||typeof doc!=='object'||!/^[A-HJ-NP-Z2-9]{5}$/.test(doc.ztm_id||'')||!['idle','benchmarking','mining','stopped'].includes(doc.state))return response({error:'Invalid heartbeat'},422);
    const vals=['hashrate_hs','temperature_c','cpu_percent','ram_percent','active_threads','accepted_shares','rejected_shares'].map(k=>doc[k]==null?null:Number(doc[k]));
    if(vals.some(x=>x!==null&&(!Number.isFinite(x)||x<0))||[2,3].some(i=>vals[i]!==null&&vals[i]>100))return response({error:'Invalid telemetry values'},422);
    try{
      const rows=await sql('SELECT w.worker_uuid FROM ztm_worker_credentials c JOIN ztm_workers w USING(worker_uuid) WHERE c.token_hash=$1 AND c.revoked_at IS NULL AND w.revoked_at IS NULL AND w.ztm_id=$2',[digest(bearer.slice(7)),doc.ztm_id]);
      if(!rows.length)return response({error:'Invalid worker credential'},403);
      const id=rows[0].worker_uuid;
      await sql('INSERT INTO ztm_worker_heartbeats(worker_uuid,observed_at,state,hashrate_hs,temperature_c,cpu_percent,ram_percent,active_threads,accepted_shares,rejected_shares) VALUES($1,now(),$2,$3,$4,$5,$6,$7,$8,$9) ON CONFLICT(worker_uuid) DO UPDATE SET observed_at=now(),state=excluded.state,hashrate_hs=excluded.hashrate_hs,temperature_c=excluded.temperature_c,cpu_percent=excluded.cpu_percent,ram_percent=excluded.ram_percent,active_threads=excluded.active_threads,accepted_shares=excluded.accepted_shares,rejected_shares=excluded.rejected_shares',[id,doc.state,...vals]);
      await sql('INSERT INTO ztm_worker_telemetry(worker_uuid,state,hashrate_hs,temperature_c,cpu_percent,ram_percent,active_threads,accepted_shares,rejected_shares) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9)',[id,doc.state,...vals]);
      await sql('UPDATE ztm_workers SET last_seen=now() WHERE worker_uuid=$1',[id]);
      return response({status:'accepted',worker:doc.ztm_id});
    }catch{return response({error:'Heartbeat unavailable'},503)}
  }
  if(request.method==='POST'&&path==='/v1/admin/register'){
    const denial=auth(request);if(denial)return denial;
    let data;try{data=await body(request)}catch{return response({error:'Invalid registration JSON'},422)}
    const ztmId=data?.ztm_id;
    if(typeof ztmId!=='string'||!/^[A-HJ-NP-Z2-9]{5}$/.test(ztmId))return response({error:'Invalid ZTM ID'},422);
    const id=randomUUID(),key=randomBytes(48).toString('base64url');
    try{
      await sql('WITH w AS (INSERT INTO ztm_workers(worker_uuid,ztm_id,consent_version) VALUES($1,$2,$3) RETURNING worker_uuid) INSERT INTO ztm_worker_credentials(worker_uuid,token_hash) SELECT worker_uuid,$4 FROM w',[id,ztmId,String(data.consent_version||'pilot-v1'),digest(key)]);
      return response({worker_uuid:id,ztm_id:ztmId,worker_token:key},201)
    }catch{return response({error:'Registration failed or ID already exists'},409)}
  }
  if(request.method==='POST'&&path==='/v1/results'){
    const authorization=request.headers.get('authorization')||'';
    const event=request.headers.get('idempotency-key')||'';
    if(!/^Bearer [A-Za-z0-9_-]{50,}$/.test(authorization))return response({error:'Worker credential required'},401);
    if(!/^[A-Za-z0-9_-]{1,128}$/.test(event))return response({error:'Invalid event ID'},422);
    let doc;try{doc=await body(request)}catch{return response({error:'Invalid result JSON'},422)}
    if(!doc||typeof doc!=='object'||!doc.worker||!doc.hardware||!doc.benchmark||!Array.isArray(doc.profiles)||!doc.winner)return response({error:'Missing report fields'},422);
    const ztmId=doc.worker.ztm_id;
    if(typeof ztmId!=='string'||!/^[A-HJ-NP-Z2-9]{5}$/.test(ztmId))return response({error:'Invalid worker ID'},422);
    const json=JSON.stringify(doc);
    if(/"(private_key|spend_key|seed_phrase|wallet_password)"\s*:/.test(json))return response({error:'Prohibited secret field'},422);
    try{
      const w=await sql('SELECT w.worker_uuid FROM ztm_worker_credentials c JOIN ztm_workers w USING(worker_uuid) WHERE c.token_hash=$1 AND c.revoked_at IS NULL AND w.revoked_at IS NULL AND w.ztm_id=$2',[digest(authorization.slice(7)),ztmId]);
      if(!w.length)return response({error:'Invalid worker credential'},403);
      const result=await sql('INSERT INTO ztm_ingested_events(worker_uuid,event_id,report) VALUES($1,$2,$3::jsonb) ON CONFLICT(worker_uuid,event_id) DO NOTHING RETURNING event_id',[w[0].worker_uuid,event,json]);
      return response({status:result.length?'accepted':'duplicate',event_id:event,verified:false},result.length?202:200);
    }catch{return response({error:'Ingestion unavailable'},503)}
  }
  return response({error:'Not found'},404)
}