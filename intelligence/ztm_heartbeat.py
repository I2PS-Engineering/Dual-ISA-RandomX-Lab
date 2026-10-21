"""Opt-in ZTM heartbeat reporter for the Neon Intelligence API.

This module is independent of mining control. No network operation starts
without consent=True and a per-worker bearer token.
"""
from __future__ import annotations

import json
import math
import urllib.request
from dataclasses import dataclass
from typing import Optional

STATES = {"idle", "benchmarking", "mining", "stopped"}


@dataclass
class Heartbeat:
    ztm_id: str
    state: str
    hashrate_hs: Optional[float] = None
    temperature_c: Optional[float] = None
    cpu_percent: Optional[float] = None
    ram_percent: Optional[float] = None
    active_threads: Optional[int] = None
    accepted_shares: Optional[int] = None
    rejected_shares: Optional[int] = None

    def as_payload(self):
        if len(self.ztm_id) != 5 or not self.ztm_id.isalnum() or not self.ztm_id.isupper():
            raise ValueError("Invalid ZTM ID")
        if self.state not in STATES:
            raise ValueError("Invalid worker state")
        fields = ("hashrate_hs", "temperature_c", "cpu_percent", "ram_percent",
                  "active_threads", "accepted_shares", "rejected_shares")
        data = {"ztm_id": self.ztm_id, "state": self.state}
        for key in fields:
            value = getattr(self, key)
            if value is not None:
                if not math.isfinite(float(value)) or value < 0:
                    raise ValueError("Invalid telemetry: " + key)
                if key in ("cpu_percent", "ram_percent") and value > 100:
                    raise ValueError("Percentage out of range")
                data[key] = value
        return data


def send_heartbeat(api_url, worker_token, heartbeat, *, consent, timeout=8):
    if consent is not True:
        raise PermissionError("Telemetry reporting requires explicit consent")
    if not api_url.startswith("https://"):
        raise ValueError("HTTPS is required")
    if not worker_token or len(worker_token) < 50:
        raise ValueError("Worker registration credential required")
    body = json.dumps(heartbeat.as_payload(), separators=(",", ":")).encode("utf-8")
    req = urllib.request.Request(
        api_url.rstrip("/") + "/v1/heartbeat",
        data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + worker_token},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError("Heartbeat not accepted")
        return json.loads(response.read().decode("utf-8"))
