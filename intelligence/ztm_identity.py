"""ZTM installation identity and consent-safe hardware inventory.

Public worker name: ZTM-<VERSION>-<L|M>/<X64|ARM64>-<ZTM_ID>.
The five-character ZTM ID is a label, NOT an authentication credential.
Remote uniqueness is guaranteed only after registration with the I2PS API.
"""
from __future__ import annotations

import json
import os
import platform
import re
import secrets
import tempfile
import uuid
from pathlib import Path

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
ID_PATTERN = re.compile(r"^[A-Z2-9]{5}$")
RELEASE_PATTERN = re.compile(r"^[A-Z0-9]+$")
DEFAULT_ROOT = Path.home() / ".local" / "share" / "ztm"
IDENTITY_FILE = "worker_identity.json"


def system_code(system=None):
    system = system or platform.system()
    table = {"Linux": "L", "Darwin": "M"}
    if system not in table:
        raise ValueError("Unsupported operating system: " + system)
    return table[system]


def architecture_code(machine=None):
    machine = (machine or platform.machine()).lower()
    table = {"x86_64": "X64", "amd64": "X64", "aarch64": "ARM64", "arm64": "ARM64"}
    if machine not in table:
        raise ValueError("Unsupported architecture: " + machine)
    return table[machine]


def create_ztm_id():
    return "".join(secrets.choice(ALPHABET) for _ in range(5))


def load_or_create(root=DEFAULT_ROOT):
    root = Path(root)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = root / IDENTITY_FILE
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if not ID_PATTERN.fullmatch(data.get("ztm_id", "")):
            raise ValueError("Invalid stored ZTM ID; refusing to overwrite identity")
        if not data.get("install_uuid"):
            raise ValueError("Missing installation UUID")
        return data
    data = {"ztm_id": create_ztm_id(), "install_uuid": str(uuid.uuid4()),
            "registration_status": "unregistered", "schema_version": 1}
    fd, tmp = tempfile.mkstemp(dir=root, prefix=".identity-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, 0o600)
        # Exclusive link prevents overwriting another process's identity.
        try:
            os.link(tmp, path)
        except FileExistsError:
            return load_or_create(root)
        return data
    finally:
        Path(tmp).unlink(missing_ok=True)


def worker_name(version, identity, os_code=None, arch_code=None):
    if not RELEASE_PATTERN.fullmatch(version):
        raise ValueError("Invalid version")
    ztm_id = identity["ztm_id"]
    if not ID_PATTERN.fullmatch(ztm_id):
        raise ValueError("Invalid ZTM ID")
    os_code = os_code or system_code()
    arch_code = arch_code or architecture_code()
    if os_code not in ("L", "M") or arch_code not in ("X64", "ARM64"):
        raise ValueError("Unsupported platform")
    return f"ZTM-{version}-{os_code}/{arch_code}-{ztm_id}"


def mining_safe_worker_name(version, identity, os_code=None, arch_code=None):
    """Use after verifying the target pool's worker-name grammar.

    The GUI can show the canonical slash form. Pool protocol integrations
    may require a different separator, avoiding silent rejected shares.
    """
    return worker_name(version, identity, os_code, arch_code).replace("/", "_")


def linux_cpuinfo():
    result = {}
    path = Path("/proc/cpuinfo")
    if not path.exists():
        return result
    for line in path.read_text(errors="replace").splitlines():
        if ":" not in line:
            continue
        key, value = (piece.strip() for piece in line.split(":", 1))
        if key in ("model name", "vendor_id", "cpu family", "model", "stepping", "cache size", "flags") and key not in result:
            if key == "flags":
                result["features"] = value.split()
            else:
                result[key.replace(" ", "_")] = value
    return result


def total_memory_bytes():
    if platform.system() == "Linux":
        p = Path("/proc/meminfo")
        if p.exists():
            m = re.search(r"^MemTotal:\s+(\d+) kB", p.read_text(), re.MULTILINE)
            if m:
                return int(m.group(1)) * 1024
    return None


def hardware_snapshot():
    """No serial numbers, MAC addresses, wallets, usernames or public IP."""
    return {"os": platform.system(), "os_release": platform.release(),
            "architecture": architecture_code(), "machine": platform.machine(),
            "cpu_model": platform.processor() or linux_cpuinfo().get("model_name") or "unknown",
            "cpu_logical_threads": os.cpu_count(),
            "ram_bytes": total_memory_bytes(),
            "linux_cpuinfo": linux_cpuinfo() if platform.system() == "Linux" else {},
            "schema_version": 1}
