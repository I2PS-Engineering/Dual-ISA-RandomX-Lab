"""Opt-in ZTM benchmark reporting queue. No upload occurs automatically."""
import json
import sqlite3
import time
import uuid
from pathlib import Path
from urllib import request

SCHEMA = """
CREATE TABLE IF NOT EXISTS submissions (
 event_id TEXT PRIMARY KEY,
 run_id TEXT NOT NULL,
 payload TEXT NOT NULL,
 created_at INTEGER NOT NULL,
 uploaded_at INTEGER
);
CREATE INDEX IF NOT EXISTS submissions_pending ON submissions(uploaded_at);
"""


def connect(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def enqueue(conn, result, *, consent):
    if consent is not True:
        raise PermissionError("User has not authorized benchmark reporting")
    required = ("worker", "hardware", "benchmark", "profiles", "winner")
    if any(key not in result for key in required):
        raise ValueError("Incomplete benchmark payload")
    if "seed" in json.dumps(result).lower() or "private_key" in json.dumps(result).lower():
        raise ValueError("Sensitive field in benchmark payload")
    event_id = str(uuid.uuid4())
    run_id = result["benchmark"]["run_id"]
    conn.execute("INSERT INTO submissions VALUES (?, ?, ?, ?, NULL)",
                 (event_id, run_id, json.dumps(result), int(time.time())))
    conn.commit()
    return event_id


def submit_pending(conn, endpoint, registration_token, *, consent, timeout=8):
    """Only send to the configured I2PS HTTPS endpoint after explicit consent."""
    if consent is not True:
        raise PermissionError("Telemetry upload not authorized")
    if not endpoint.startswith("https://"):
        raise ValueError("HTTPS required")
    if not registration_token:
        raise ValueError("Missing registered-worker token")
    uploaded = 0
    for event_id, payload in conn.execute(
            "SELECT event_id, payload FROM submissions WHERE uploaded_at IS NULL ORDER BY created_at LIMIT 20"):
        req = request.Request(endpoint, data=payload.encode("utf-8"),
                              headers={"Content-Type": "application/json",
                                       "Authorization": "Bearer " + registration_token,
                                       "Idempotency-Key": event_id},
                              method="POST")
        with request.urlopen(req, timeout=timeout) as response:
            if response.status not in (200, 201, 202):
                raise RuntimeError("Telemetry service rejected the submission")
        conn.execute("UPDATE submissions SET uploaded_at=? WHERE event_id=?",
                     (int(time.time()), event_id))
        conn.commit()
        uploaded += 1
    return uploaded
