"""ZTM Intelligence offline administrator dashboard (stdlib-only, $0 hosting).
Run locally: python3 intelligence/local_admin.py --import /path/to/reports --serve
The HTTP listener is bound to 127.0.0.1 and API requests require a session token.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import re
import secrets
import sqlite3
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

MAX_REPORT_BYTES = 2_000_000
ZTM_ID = re.compile(r"^[A-HJ-NP-Z2-9]{5}$")
SCHEMA = """
CREATE TABLE IF NOT EXISTS benchmark_reports (
 report_id TEXT PRIMARY KEY,
 worker_id TEXT NOT NULL,
 run_id TEXT NOT NULL,
 cpu_model TEXT NOT NULL,
 arch TEXT,
 os TEXT,
 version TEXT,
 is_qualified INTEGER NOT NULL,
 active_threads INTEGER,
 mean_hs REAL,
 median_hs REAL,
 max_hs REAL,
 accepted INTEGER NOT NULL,
 rejected INTEGER NOT NULL,
 report_json TEXT NOT NULL,
 imported_at INTEGER NOT NULL,
 UNIQUE (worker_id,run_id)
);
CREATE INDEX IF NOT EXISTS idx_reports_cpu ON benchmark_reports(cpu_model);
CREATE INDEX IF NOT EXISTS idx_reports_imported ON benchmark_reports(imported_at);
"""
def database(db_path):
    path = Path(db_path)
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    conn.executescript(SCHEMA)
    return conn

def as_nonnegative_number(v):
    if v is None or isinstance(v,bool): return None
    try:
        n=float(v)
        return n if math.isfinite(n) and n >= 0 else None
    except (TypeError,ValueError): return None

def first(*items):
    return next((x for x in items if x is not None),None)

def normalize(report):
    """Accept current ZTM run JSON and the proposed worker/hardware/benchmark envelope.
    Untrusted incoming reports remain unverified by default.
    """
    if not isinstance(report,dict):
        raise ValueError("Report must be an object")
    worker=report.get("worker") or {}
    hardware=report.get("hardware") or {}
    benchmark=report.get("benchmark") or {}
    winner=report.get("winner") or report.get("winning_configuration") or {}
    if not all(isinstance(v,dict) for v in (worker,hardware,benchmark,winner)):
        raise ValueError("Invalid nested object")
    ztm_id=first(worker.get("ztm_id"),report.get("ztm_id"),"LEGACY")
    if ztm_id != "LEGACY" and not ZTM_ID.fullmatch(str(ztm_id)):
        raise ValueError("Invalid five-character ZTM ID")
    # Old SRP1V2 reports have shared worker identity; keep them separately
    # under LEGACY. Never pretend they are unique or remotely registered.
    run_id=str(first(benchmark.get("run_id"),report.get("run_id"),report.get("runid"),""))
    if not run_id or len(run_id)>128:
        # Stable hash identifies old data without a run ID, without altering it.
        run_id=hashlib.sha256(json.dumps(report,sort_keys=True).encode()).hexdigest()[:32]
    cpu=str(first(hardware.get("cpu_model"),report.get("cpu_model"),"Unknown"))[:240]
    threads=first(winner.get("threads"),winner.get("active_threads"))
    if threads is not None:
        threads=int(threads)
        if threads<1 or threads>4096: raise ValueError("Invalid active threads")
    means=as_nonnegative_number(first(winner.get("sustained_mean_hs"),report.get("mean_hs")))
    medians=as_nonnegative_number(first(winner.get("sustained_median_hs"),report.get("median_hs")))
    peaks=as_nonnegative_number(first(winner.get("highest_recorded_hs"),report.get("max_hs")))
    accepted=int(first(report.get("accepted_shares"),winner.get("accepted_shares"),0))
    rejected=int(first(report.get("rejected_shares"),winner.get("rejected_shares"),0))
    if accepted<0 or rejected<0:raise ValueError("Negative shares")
    qualified=bool(first(benchmark.get("qualifying"),report.get("actual_24_hour_benchmark"),False))
    # The importer makes no certification claim based on client supplied flags.
    return {
        "worker_id":str(ztm_id),"run_id":run_id,"cpu_model":cpu,
        "arch":str(first(worker.get("architecture"),hardware.get("architecture"),"")),
        "os":str(first(worker.get("os"),hardware.get("os"),"")),
        "version":str(first(worker.get("version"),benchmark.get("ztm_version"),"")),
        "is_qualified":int(qualified),"active_threads":threads,
        "mean_hs":means,"median_hs":medians,"max_hs":peaks,
        "accepted":accepted,"rejected":rejected,
    }

def import_report(conn,report):
    packed=json.dumps(report,ensure_ascii=False,sort_keys=True)
    if len(packed.encode()) > MAX_REPORT_BYTES: raise ValueError("Report exceeds 2 MB")
    row=normalize(report)
    key=hashlib.sha256((row["worker_id"]+"|"+row["run_id"]).encode()).hexdigest()
    before=conn.total_changes
    conn.execute("""INSERT OR IGNORE INTO benchmark_reports (
        report_id,worker_id,run_id,cpu_model,arch,os,version,is_qualified,
        active_threads,mean_hs,median_hs,max_hs,accepted,rejected,report_json,imported_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (key,row["worker_id"],row["run_id"],row["cpu_model"],row["arch"],row["os"],
         row["version"],row["is_qualified"],row["active_threads"],row["mean_hs"],
         row["median_hs"],row["max_hs"],row["accepted"],row["rejected"],packed,int(time.time())))
    conn.commit()
    return conn.total_changes > before

def import_path(conn,path):
    path=Path(path)
    if path.is_file(): paths=[path]
    elif path.is_dir(): paths=sorted(path.rglob("*.json"))
    else: raise FileNotFoundError(path)
    success=duplicate=invalid=0
    for f in paths:
        try:
            if f.stat().st_size>MAX_REPORT_BYTES:raise ValueError("File too large")
            parsed=json.loads(f.read_text(encoding="utf-8"))
            if import_report(conn,parsed):success+=1
            else:duplicate+=1
        except (ValueError,OSError,TypeError) as e:
            invalid+=1
            print(f"SKIP {f.name}: {e}")
    return {"imported":success,"duplicates":duplicate,"invalid":invalid}

def dashboard_data(conn):
    counts=conn.execute("""SELECT COUNT(*) runs,COUNT(DISTINCT worker_id) workers,
        COUNT(DISTINCT cpu_model) cpus, COALESCE(SUM(is_qualified),0) qualified
        FROM benchmark_reports""").fetchone()
    cpus=[dict(row) for row in conn.execute("""SELECT cpu_model, COUNT(*) runs,
        ROUND(AVG(median_hs),1) median_average_hs, MAX(max_hs) peak_hs,
        SUM(is_qualified) qualified FROM benchmark_reports
        GROUP BY cpu_model ORDER BY runs DESC, cpu_model LIMIT 50""")]
    runs=[dict(row) for row in conn.execute("""SELECT worker_id,run_id,cpu_model,arch,os,
        version,is_qualified,active_threads,ROUND(mean_hs,1) mean_hs,
        ROUND(median_hs,1) median_hs,ROUND(max_hs,1) max_hs,accepted,rejected,imported_at
        FROM benchmark_reports ORDER BY imported_at DESC,run_id LIMIT 250""")]
    return {"summary":dict(counts),"cpus":cpus,"runs":runs,
            "warning":"Local imports are unverified observations; qualified means client-reported eligibility, not independent certification."}

class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self,format,*args):
        pass
    def do_GET(self):
        path=urlsplit(self.path).path
        if path=="/":
            content=Path(self.server.html_file).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Cache-Control","no-store")
            self.send_header("Referrer-Policy","no-referrer")
            self.send_header("X-Frame-Options","DENY")
            self.send_header("Content-Security-Policy","default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(content)
            return
        if path!="/api/summary":
            self.send_error(404)
            return
        token=self.headers.get("Authorization","").removeprefix("Bearer ").strip()
        if not secrets.compare_digest(token,self.server.admin_token):
            self.send_error(401,"Administrator token required")
            return
        with database(self.server.db_file) as conn:
            payload=json.dumps(dashboard_data(conn)).encode()
        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

def serve(db_file,port=8765,html_file=None):
    html_file=html_file or Path(__file__).parent/"dashboard.html"
    token=secrets.token_urlsafe(32)
    server=ThreadingHTTPServer(("127.0.0.1",port),DashboardHandler)
    server.admin_token=token
    server.db_file=str(db_file)
    server.html_file=str(html_file)
    print(f"Local dashboard: http://127.0.0.1:{port}/#token={token}",flush=True)
    print("Only localhost is bound. Stop with Ctrl+C. Never share this access URL.",flush=True)
    try:server.serve_forever()
    finally:server.server_close()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",default=str(Path.home()/".local/share/ztm/intelligence.db"))
    parser.add_argument("--import",dest="source",help="Import one report JSON or a folder of reports")
    parser.add_argument("--serve",action="store_true")
    parser.add_argument("--port",type=int,default=8765)
    args=parser.parse_args()
    with database(args.db) as conn:
        if args.source:print(json.dumps(import_path(conn,args.source)))
        if not args.source and not args.serve:parser.error("Supply --import or --serve")
    if args.serve:serve(args.db,args.port)

if __name__=="__main__":
    main()
