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
const dashboard="<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>ZTM Intelligence</title><style>body{margin:0;background:#070e18;color:#f2f8ff;font:16px system-ui}header{padding:24px 6%;background:#0c1b2d;font-size:25px;font-weight:750}b{color:#39bfff}main{max-width:960px;margin:40px auto;padding:0 20px}input,button{font:inherit;border-radius:8px;padding:13px;border:1px solid #41739b;color:white;background:#0c1b2d}button{background:#1976ff;cursor:pointer}input{min-width:260px}.cards{display:flex;gap:16px;flex-wrap:wrap}.card{background:#0c1b2d;border:1px solid #24455c;padding:24px;border-radius:12px;min-width:180px}.card strong{display:block;font-size:30px}table{border-collapse:collapse;width:100%;margin-top:24px;background:#0c1b2d}td,th{padding:14px;border-bottom:1px solid #24455c;text-align:left}th{color:#39bfff}#error{color:#7fd8ff}</style><header>I2PS <b>ZTM Intelligence</b></header><main><h1>Benchmark Analytics</h1><p>Administrator-only CPU and worker statistics. Submissions are unverified until validated.</p><input type='password' id='token' placeholder='Administrator token' autocomplete='off'><button id='load'>Load results</button><p id='error'></p><div class='cards'><div class='card'>Workers<strong id='workers'>-</strong></div><div class='card'>Submissions<strong id='submissions'>-</strong></div><div class='card'>Verified<strong id='verified'>-</strong></div></div><table><thead><tr><th>CPU model</th><th>Runs</th><th>Average H/s</th></tr></thead><tbody id='rows'></tbody></table></main><script>const e=id=>document.getElementById(id);e('load').onclick=async()=>{try{const r=await fetch('/v1/admin/stats',{headers:{Authorization:'Bearer '+e('token').value},cache:'no-store'});if(!r.ok)throw Error('Access denied or server unavailable: '+r.status);const d=await r.json();e('workers').textContent=d.overview.registered_workers;e('submissions').textContent=d.overview.submitted_reports;e('verified').textContent=d.overview.verified_reports;const t=e('rows');t.replaceChildren();for(const v of d.cpus){const tr=document.createElement('tr');for(const x of [v.cpu_model,v.submitted_runs,v.submitted_mean_hs||'-']){const td=document.createElement('td');td.textContent=String(x);tr.appendChild(td)}t.appendChild(tr)}e('error').textContent='Analytics loaded.'}catch(err){e('error').textContent=err.message}};</script></html>";
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