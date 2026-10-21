"""ZTM Intelligence ingestion API. Railway-ready; no public database access."""
import hashlib
import hmac
import json
import os
import re
import secrets
import uuid
from contextlib import contextmanager

import psycopg
from fastapi import FastAPI, Header, HTTPException, Request
from psycopg.types.json import Jsonb

app = FastAPI(title="I2PS ZTM Intelligence API", docs_url=None, redoc_url=None)
ID_RE = re.compile(r"^[A-HJ-NP-Z2-9]{5}$")
MAX_BYTES = 1_000_000


@contextmanager
def connection():
    uri = os.environ.get("DATABASE_URL")
    if not uri:
        raise RuntimeError("DATABASE_URL not configured")
    with psycopg.connect(uri, connect_timeout=5) as conn:
        yield conn


def token_hash(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def authorized_worker(conn, token):
    if not token:
        raise HTTPException(401, "Missing worker credential")
    hashed = token_hash(token)
    worker = conn.execute(
        "SELECT worker_uuid, ztm_id FROM ztm_worker_credentials "
        "WHERE token_hash=%s AND revoked_at IS NULL", (hashed,)).fetchone()
    if not worker:
        raise HTTPException(403, "Invalid or revoked credential")
    return worker


@app.get("/health")
def health():
    try:
        with connection() as conn:
            conn.execute("SELECT 1").fetchone()
        return {"status": "ok", "database": "connected"}
    except Exception:
        raise HTTPException(503, "Database unavailable")


@app.post("/v1/admin/register")
def register(data: dict, authorization: str | None = Header(default=None)):
    secret = os.environ.get("ZTM_ADMIN_BOOTSTRAP_TOKEN")
    if not secret or not authorization or not hmac.compare_digest(authorization, "Bearer " + secret):
        raise HTTPException(403, "Administrator authorization required")
    requested = data.get("ztm_id")
    if not isinstance(requested, str) or not ID_RE.fullmatch(requested):
        raise HTTPException(422, "Invalid ZTM ID")
    worker_uuid = uuid.uuid4()
    credential = secrets.token_urlsafe(48)
    with connection() as conn:
        existing = conn.execute("SELECT 1 FROM ztm_workers WHERE ztm_id=%s", (requested,)).fetchone()
        if existing:
            raise HTTPException(409, "ZTM ID collision; generate another")
        conn.execute(
            "INSERT INTO ztm_workers (worker_uuid,ztm_id,consent_version) VALUES (%s,%s,%s)",
            (worker_uuid, requested, data.get("consent_version", "v1")))
        conn.execute(
            "INSERT INTO ztm_worker_credentials (worker_uuid,token_hash) VALUES (%s,%s)",
            (worker_uuid, token_hash(credential)))
    return {"worker_uuid": str(worker_uuid), "ztm_id": requested, "worker_token": credential}


@app.post("/v1/results")
async def results(request: Request, authorization: str | None = Header(default=None),
                  idempotency_key: str | None = Header(default=None)):
    if not idempotency_key or len(idempotency_key) > 128:
        raise HTTPException(422, "Valid Idempotency-Key required")
    body = await request.body()
    if len(body) > MAX_BYTES:
        raise HTTPException(413, "Result too large")
    try:
        doc = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(422, "Invalid JSON")
    if not isinstance(doc, dict) or any(k not in doc for k in
        ("worker", "hardware", "benchmark", "profiles", "winner")):
        raise HTTPException(422, "Missing report fields")
    with connection() as conn:
        worker_uuid, ztm_id = authorized_worker(conn, (authorization or "").removeprefix("Bearer ").strip())
        if doc["worker"].get("ztm_id") != ztm_id:
            raise HTTPException(403, "Report worker identity mismatch")
        # Treat client results as unverified submissions, not certified measurements.
        existing = conn.execute(
            "SELECT 1 FROM ztm_ingested_events WHERE worker_uuid=%s AND event_id=%s",
            (worker_uuid, idempotency_key)).fetchone()
        if existing:
            return {"status": "duplicate", "event_id": idempotency_key}
        conn.execute(
            "INSERT INTO ztm_ingested_events(worker_uuid,event_id,report) VALUES (%s,%s,%s)",
            (worker_uuid, idempotency_key, Jsonb(doc)))
        conn.execute("UPDATE ztm_workers SET last_seen=now() WHERE worker_uuid=%s", (worker_uuid,))
    return {"status": "accepted", "event_id": idempotency_key, "verification": "pending"}
