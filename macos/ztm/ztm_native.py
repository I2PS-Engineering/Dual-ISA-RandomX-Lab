#!/usr/bin/env python3
"""ZTM native macOS platform support. No administrator privileges are requested."""
from __future__ import annotations

import hashlib
import io
import os
import platform
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

VERSION = "6.26.0"
ASSETS = {
    "arm64": ("xmrig-6.26.0-macos-arm64.tar.gz", "6ae4eb4216e99a201ae9a3d2c3a7c275207c5165cfc25da1f3d735d6c4829c18"),
    "x86_64": ("xmrig-6.26.0-macos-x64.tar.gz", "1da924b358c0089e361540c4a9e6f8b09538b29efeafa2379590e0f6db358ff4"),
}
MAX_ARCHIVE_BYTES = 35 * 1024 * 1024
MAX_EXECUTABLE_BYTES = 30 * 1024 * 1024
ALLOWED_HOSTS = frozenset(("github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com"))


class MacPlatformError(RuntimeError):
    pass


def architecture() -> str:
    if platform.system() != "Darwin":
        raise MacPlatformError("This edition requires macOS.")
    machine = platform.machine().lower()
    if machine in ("aarch64", "arm64"):
        return "arm64"
    if machine in ("x86_64", "amd64"):
        return "x86_64"
    raise MacPlatformError("Unsupported Mac CPU architecture: " + machine)


def cache_directory() -> Path:
    return Path.home() / "Library" / "Application Support" / "I2PS" / "ZTM" / ("xmrig-" + VERSION)


def cpu_model() -> str:
    architecture()
    for args in (
        ["/usr/sbin/sysctl", "-n", "machdep.cpu.brand_string"],
        ["/usr/sbin/system_profiler", "SPHardwareDataType", "-json"],
        ["/usr/sbin/sysctl", "-n", "hw.model"],
    ):
        try:
            p = subprocess.run(args, capture_output=True, text=True, timeout=6, check=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if p.returncode != 0:
            continue
        value = p.stdout.strip()
        if "-json" in args:
            import json
            try:
                for entry in json.loads(value).get("SPHardwareDataType", []):
                    chip = entry.get("chip_type") or entry.get("cpu_type")
                    if chip:
                        return str(chip)
            except (ValueError, KeyError, TypeError):
                pass
        elif value:
            return value
    return platform.processor() or platform.machine()


def process_identity(pid: int) -> tuple[int, str] | None:
    """Identify one macOS PID and its start time, guarding against PID reuse."""
    if not isinstance(pid, int) or pid < 1:
        return None
    try:
        result = subprocess.run(
            ["/bin/ps", "-p", str(pid), "-o", "lstart="],
            capture_output=True, text=True, timeout=4, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return pid, result.stdout.strip()


def process_identity_alive(pid: int, start: str) -> bool:
    identity = process_identity(pid)
    return bool(identity and start and identity[1] == start)


def child_command(component: str, *args: str) -> list[str]:
    """Start a subcommand using the same signed app executable or the dev launcher."""
    if component not in ("prepare", "engine", "mining", "guardian"):
        raise MacPlatformError("Unknown ZTM subprocess component.")
    if getattr(sys, "frozen", False):
        return [sys.executable, "--ztm-child", component, *args]
    launcher = Path(__file__).with_name("launcher.py")
    return [sys.executable, str(launcher), "--ztm-child", component, *args]


def _verified_archive(blob: bytes, expected_digest: str) -> bytes:
    if len(blob) > MAX_ARCHIVE_BYTES or hashlib.sha256(blob).hexdigest() != expected_digest:
        raise MacPlatformError("Official XMRig download SHA-256 mismatch; refusing to execute.")
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
        matches = [
            member for member in archive.getmembers()
            if member.isfile() and not member.issym() and not member.islnk()
            and member.name.rsplit("/", 1)[-1] == "xmrig"
            and 0 < member.size <= MAX_EXECUTABLE_BYTES
        ]
        if len(matches) != 1:
            raise MacPlatformError("XMRig archive did not contain one regular executable.")
        stream = archive.extractfile(matches[0])
        if stream is None:
            raise MacPlatformError("XMRig executable could not be extracted.")
        executable = stream.read(MAX_EXECUTABLE_BYTES + 1)
        if len(executable) > MAX_EXECUTABLE_BYTES:
            raise MacPlatformError("XMRig executable exceeds allowed size.")
        # Mach-O magic values: 32-bit, 64-bit, and fat/universal in either endian.
        if executable[:4] not in (
            bytes.fromhex("cffaedfe"), bytes.fromhex("feedfacf"),
            bytes.fromhex("cefaedfe"), bytes.fromhex("feedface"),
            bytes.fromhex("cafebabe"), bytes.fromhex("bebafeca"),
        ):
            raise MacPlatformError("XMRig download is not a Mach-O executable.")
        return executable


def verified_binary(cache: Path | None = None) -> Path:
    arch = architecture()
    name, expected_digest = ASSETS[arch]
    location = cache or cache_directory()
    if location.is_symlink():
        raise MacPlatformError("Refusing a symbolic-link XMRig cache.")
    location.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(location, 0o700)
    archive_path = location / name
    if archive_path.is_symlink():
        raise MacPlatformError("Refusing a symbolic-link archive.")

    if archive_path.is_file():
        archive_blob = archive_path.read_bytes()
        if hashlib.sha256(archive_blob).hexdigest() != expected_digest:
            raise MacPlatformError("Cached XMRig archive failed verification.")
    else:
        url = f"https://github.com/xmrig/xmrig/releases/download/v{VERSION}/{name}"
        print(f"[ZTM] Downloading official XMRig {VERSION} for macOS {arch}...", flush=True)
        req = urllib.request.Request(url, headers={"User-Agent": "ZTM-macOS-P1"})
        with urllib.request.urlopen(req, timeout=90) as response:
            host = urlparse(response.geturl()).hostname or ""
            if host not in ALLOWED_HOSTS:
                raise MacPlatformError("Unexpected download redirect host.")
            archive_blob = response.read(MAX_ARCHIVE_BYTES + 1)
        executable = _verified_archive(archive_blob, expected_digest)
        with tempfile.NamedTemporaryFile(dir=location, prefix=".download-", delete=False) as output:
            temporary = Path(output.name)
            output.write(archive_blob)
        try:
            temporary.chmod(0o600)
            os.replace(temporary, archive_path)
        finally:
            temporary.unlink(missing_ok=True)

    executable = _verified_archive(archive_blob, expected_digest)
    executable_path = location / "xmrig"
    if executable_path.is_symlink():
        raise MacPlatformError("Refusing a symbolic-link miner.")
    binary_sha = hashlib.sha256(executable).hexdigest()
    if executable_path.is_file():
        if hashlib.sha256(executable_path.read_bytes()).hexdigest() != binary_sha:
            raise MacPlatformError("Cached XMRig binary does not match verified archive.")
    else:
        with tempfile.NamedTemporaryFile(dir=location, prefix=".xmrig-", delete=False) as output:
            temporary = Path(output.name)
            output.write(executable)
        try:
            temporary.chmod(0o700)
            os.replace(temporary, executable_path)
        finally:
            temporary.unlink(missing_ok=True)
    executable_path.chmod(0o700)
    print("[ZTM] Verified native macOS XMRig archive and executable.", flush=True)
    return executable_path


def main(argv: list[str] | None = None) -> int:
    args = list(argv or [])
    if args != ["prepare"]:
        raise MacPlatformError("Run preparation explicitly from the ZTM GUI.")
    print(f"[ZTM] macOS {architecture()} — no sudo, APT, pkexec or MSR writes.", flush=True)
    executable = verified_binary()
    print(f"[ZTM] Ready: {executable}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (MacPlatformError, OSError, ValueError) as error:
        print("[ZTM] Preparation error: " + str(error), file=sys.stderr)
        raise SystemExit(1)
