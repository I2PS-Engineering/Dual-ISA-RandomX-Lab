#!/usr/bin/env python3
"""ZTM — Zero to Monero: opt-in ONLINE CPU benchmark for fresh Ubuntu.

This is an engineering diagnostic, not the public v0.4 24-hour Dev Wallet
benchmark or production release. Runs verified official XMRig v6.26.0.
Requires user-chosen pool and public Monero address and explicit consent.
Python standard library only; no sudo required to run this file.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import os
import platform
import re
import signal
import statistics
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import urllib.request
from urllib.parse import urlparse
from pathlib import Path

VERSION = "6.26.0"
ASSET = "xmrig-6.26.0-linux-static-x64.tar.gz"
ASSET_SHA256 = "fc6f8ae5f64e4f17481f7e3be29a1c56949f216a998414188003eae1db20c9e5"
URL = f"https://github.com/xmrig/xmrig/releases/download/v{VERSION}/{ASSET}"
BASE58 = re.compile(r"^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]+$")
POOL = re.compile(r"^[A-Za-z0-9.-]+:[0-9]{1,5}$")
SPEED = re.compile(r"\bspeed\s+10s/60s/15m\s+([0-9]+(?:\.[0-9]+)?|n/a)(?:\s+([kKmM]?)[hH]/s)?", re.I)
SHARE = re.compile(r"\baccepted\s*\((\d+)\s*/\s*(\d+)\)", re.I)
REJECTED = re.compile(r"\brejected\s*\((\d+)\s*/\s*(\d+)\)", re.I)
MACHINE = ("x86_64", "amd64")
MAX_ARCHIVE = 35 * 1024 * 1024
MAX_BINARY = 30 * 1024 * 1024


class BenchError(Exception):
    pass


def validate_pool(value):
    value = value.strip()
    if not POOL.fullmatch(value):
        raise BenchError("Pool must look like pool.example.org:443 (no https:// prefix).")
    host, port = value.rsplit(":", 1)
    if host.startswith(".") or ".." in host or len(host) > 253 or not (1 <= int(port) <= 65535):
        raise BenchError("Invalid pool host or port.")
    return value


def validate_address(value):
    value = value.strip()
    if len(value) not in (95, 106) or value[0] not in ("4", "8") or not BASE58.fullmatch(value):
        raise BenchError("Enter a public Monero receiving address (95 or 106 Base58 characters). Never enter a seed or private key.")
    return value


def extract_verified_archive(blob: bytes) -> bytes:
    if hashlib.sha256(blob).hexdigest() != ASSET_SHA256:
        raise BenchError("Official XMRig archive SHA-256 mismatch; refusing to install.")
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
        files = [m for m in archive.getmembers()
                 if m.isfile() and not m.issym() and m.name.rsplit("/", 1)[-1] == "xmrig"
                 and 0 < m.size < MAX_BINARY]
        if len(files) != 1:
            raise BenchError("Unexpected XMRig archive structure.")
        fh = archive.extractfile(files[0])
        if fh is None:
            raise BenchError("XMRig executable missing from official archive.")
        result = fh.read(MAX_BINARY + 1)
        if len(result) > MAX_BINARY:
            raise BenchError("XMRig binary exceeds size limit.")
        return result


def verified_release_archive(cache: Path) -> bytes:
    """Retain the SHA-256-verified upstream archive for root-side revalidation.

    The privileged session extracts its OWN root-private copy before launching
    XMRig, rather than executing a user-writable binary with root privileges.
    """
    stored=cache / ASSET
    if stored.is_file() and not stored.is_symlink():
        blob=stored.read_bytes()
        if len(blob)<=MAX_ARCHIVE and hashlib.sha256(blob).hexdigest()==ASSET_SHA256:
            return blob
    cache.mkdir(mode=0o700, parents=True, exist_ok=True)
    print(f"Downloading official XMRig {VERSION} ({ASSET}) ...",flush=True)
    req=urllib.request.Request(URL,headers={"User-Agent":"ZTM-Linux-Online-CPU/0.1"})
    with urllib.request.urlopen(req,timeout=45) as response:
        finalhost=urlparse(response.geturl()).hostname or ''
        if finalhost not in ('github.com','release-assets.githubusercontent.com','objects.githubusercontent.com'):
            raise BenchError('Official release download redirected to an unrecognized host.')
        blob=response.read(MAX_ARCHIVE+1)
    if len(blob)>MAX_ARCHIVE or hashlib.sha256(blob).hexdigest()!=ASSET_SHA256:
        raise BenchError('Official XMRig archive validation failed.')
    with tempfile.NamedTemporaryFile(dir=cache,prefix='.ztm-archive-',delete=False) as fh:
        temporary=Path(fh.name)
        fh.write(blob)
    try:
        temporary.chmod(0o600)
        os.replace(temporary,stored)
    finally:
        temporary.unlink(missing_ok=True)
    return blob


def local_binary(cache: Path, binary_override: str | None = None) -> Path:
    if binary_override:
        p = Path(binary_override).expanduser().resolve()
        if not p.is_file() or not os.access(p, os.X_OK):
            raise BenchError("The supplied --xmrig path is not an executable file.")
        return p
    if platform.system() != "Linux" or platform.machine().lower() not in MACHINE:
        raise BenchError("This quick installer currently supports Linux x86-64 only. No OS modifications made.")
    target = cache / "xmrig"
    receipt = cache / "xmrig_sha256.txt"
    blob=verified_release_archive(cache)
    exe=extract_verified_archive(blob)
    expected_hash=hashlib.sha256(exe).hexdigest()
    if target.is_file() and receipt.is_file():
        if target.is_symlink() or hashlib.sha256(target.read_bytes()).hexdigest()!=expected_hash:
            raise BenchError('Cached XMRig differs from the official verified executable.')
        return target
    cache.mkdir(mode=0o700, parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=cache,prefix='.xmrig-',delete=False) as fh:
        temporary=Path(fh.name)
        fh.write(exe)
    try:
        temporary.chmod(0o700)
        os.replace(temporary,target)
        receipt.write_text(expected_hash+'\n',encoding='ascii')
        receipt.chmod(0o600)
    finally:
        temporary.unlink(missing_ok=True)
    return target


def speed_hs(line):
    match = SPEED.search(line)
    if match is None or match.group(1).lower() == "n/a":
        return None
    value = float(match.group(1))
    units = (match.group(2) or "").lower()
    multiplier = {"": 1, "k": 1_000, "m": 1_000_000}[units]
    return value * multiplier if value > 0 else None


def prompt_if_missing(value, prompt):
    if value:
        return value
    if not sys.stdin.isatty():
        raise BenchError("Missing input. Run interactively or pass --pool and --wallet.")
    return input(prompt).strip()


def current_cpu_info():
    model = "Unknown"
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("model name"):
                model = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    return model


THREAD_PROFILE = re.compile(r"use profile\s+rx\s+\((\d+)\s+threads", re.I)
THREAD_READY = re.compile(r"READY\s+threads\s+(\d+)\s*/\s*(\d+)", re.I)


def _profile_limits(duration_s: int) -> tuple[int, int]:
    """Return (maximum total profiles including baseline, seconds per profile)."""
    if duration_s < 300:
        return 1, duration_s
    if duration_s < 900:
        return 3, 60
    if duration_s < 3600:
        return 5, 90
    return 6, 120


def _candidate_threads(logical: int, auto_threads: int | None, max_profiles: int) -> list[int]:
    logical = max(1, int(logical or 1))
    if max_profiles <= 1:
        return []
    if auto_threads is None:
        auto_threads = max(1, min(logical, logical // 2 or 1))
    auto_threads = max(1, min(logical, int(auto_threads)))
    if logical <= max_profiles + 1:
        ordered = list(range(1, logical + 1))
    else:
        ordered = [
            auto_threads,
            auto_threads - 1,
            auto_threads + 1,
            auto_threads - 2,
            auto_threads + 2,
            round(logical * 0.75),
            logical,
            max(1, round(logical * 0.5)),
        ]
    unique = []
    for n in ordered:
        n = max(1, min(logical, int(n)))
        if n not in unique:
            unique.append(n)
    # The baseline already measured auto_threads, so only return alternate profiles.
    unique = [n for n in unique if n != auto_threads]
    return unique[:max(0, max_profiles - 1)]


def _profile_stats(samples: list[float], accepted: int, rejected: int) -> dict:
    # Ignore the first sample after a live profile switch if enough data exists.
    trimmed = samples[1:] if len(samples) >= 4 else samples[:]
    median = statistics.median(trimmed) if trimmed else 0.0
    mean = statistics.fmean(trimmed) if trimmed else 0.0
    spread = statistics.pstdev(trimmed) if len(trimmed) >= 2 else 0.0
    cv = (spread / mean) if mean > 0 else 1.0
    stability = max(0.70, 1.0 - min(cv, 0.30))
    share_quality = 1.0
    total = accepted + rejected
    if total > 0:
        share_quality = max(0.50, accepted / total)
    score = median * stability * share_quality
    return {
        "samples": len(trimmed),
        "median_hs": round(median, 2) if trimmed else None,
        "mean_hs": round(mean, 2) if trimmed else None,
        "min_hs": round(min(trimmed), 2) if trimmed else None,
        "max_hs": round(max(trimmed), 2) if trimmed else None,
        "stability_cv": round(cv, 5) if trimmed else None,
        "accepted_shares": accepted,
        "rejected_shares": rejected,
        "score": round(score, 3) if trimmed else 0.0,
    }


def _write_profile_config(cfg_path: Path, cfg: dict, threads: int) -> None:
    cpu = cfg.setdefault("cpu", {})
    cpu["rx"] = [-1] * int(threads)
    temporary = cfg_path.with_name(cfg_path.name + ".new")
    temporary.write_text(json.dumps(cfg), encoding="utf-8")
    temporary.chmod(0o600)
    os.replace(temporary, cfg_path)


def run_benchmark(executable: Path, pool: str, wallet: str, tls: bool, duration_s: int,
                  threads: int | None, output_dir: Path, confirm: bool) -> tuple[dict, int]:
    if not confirm:
        if not sys.stdin.isatty():
            raise BenchError("Interactive authorization is required (or use --yes to explicitly consent).")
        print("\nYou are authorizing REAL online CPU mining for this engineering test.")
        print(f"Pool: {pool} | TLS: {'enabled' if tls else 'disabled'} | Duration: {duration_s} seconds")
        print("Mining rewards are attributed to the configured public receiving address.")
        print("XMRig also has its own configurable developer donation mechanism.")
        print("Mining consumes electricity, heats the CPU, and can be stopped with Ctrl+C.")
        if input("Type RUN to start this test: ").strip() != "RUN":
            raise BenchError("Authorization declined; no mining started.")

    output_dir.mkdir(parents=True, exist_ok=True)
    if output_dir.is_symlink():
        raise BenchError("Refusing to save results through a symlink directory.")

    collected: list[float] = []
    state = {
        "accepted": 0, "rejected": 0, "connected": False, "lines": 0,
        "actual_threads": None, "thread_generation": 0,
    }
    lock = threading.Lock()
    start_wall = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    started = time.monotonic()
    deadline = started + duration_s
    interrupted = threading.Event()
    reached_deadline = False
    runid = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
    logfile = output_dir / f"run_{runid}.log"
    logfile.touch(mode=0o600, exist_ok=False)
    logfile.chmod(0o600)
    profiles: list[dict] = []
    selected_threads: int | None = threads
    proc = None

    try:
        with tempfile.TemporaryDirectory(prefix="i2ps-rx-", dir=None) as tempdir:
            cfg_path = Path(tempdir) / "xmrig.json"
            cfg = {
                "autosave": False,
                "watch": True,
                "coin": "monero", "algo": "rx/0",
                "pools": [{
                    "url": pool, "user": wallet,
                    "pass": "ZTM-R-A-10-E-R",
                    "rig-id": "ZTM-R-A-10-E-R",
                    "tls": tls, "keepalive": True
                }],
                "cpu": {"enabled": True, "huge-pages": True},
                "randomx": {"init": -1, "rdmsr": True, "wrmsr": True, "1gb-pages": False},
                "opencl": {"enabled": False}, "cuda": {"enabled": False},
                "print-time": 10, "colors": False,
                "http": {"enabled": False},
            }
            if threads is not None:
                cfg["cpu"]["rx"] = [-1] * int(threads)
            cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
            cfg_path.chmod(0o600)

            # Elevate only the verified miner. XMRig remains one process for the entire
            # benchmark; the optimizer changes its watched config file live.
            # The privileged guardian owns and stops XMRig; user-owned controller
            # never sends signals to a root-owned process.
            from ztm_root_guard import process_identity
            controller_id = process_identity(os.getpid())
            if controller_id is None:
                raise BenchError('Unable to verify local controller identity')
            stop_flag = Path(tempdir) / 'stop.request'
            guard_args = [str(executable), str(cfg_path), str(stop_flag),
                          str(os.getpid()), str(controller_id[1])]
            if os.environ.get('ZTM_SESSION_SOCKET'):
                command = [sys.executable, '-u',
                           str(Path(__file__).with_name('ztm_privilege_client.py')),
                           'miner', *guard_args]
            else:
                command = ["pkexec", "/usr/bin/python3",
                           str(Path(__file__).with_name('ztm_root_guard.py')),
                           "--xmrig", str(executable), "--config", str(cfg_path),
                           "--stop-flag", str(stop_flag),
                           "--owner-pid", str(os.getpid()),
                           "--owner-start", str(controller_id[1])]
            print("\nStarting verified XMRig: actual CPU hashrate measurements will appear below.", flush=True)
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    encoding="utf-8", text=True, errors="replace", bufsize=1,
                                    start_new_session=True)

            def collect():
                assert proc is not None and proc.stdout is not None
                last_acc = last_rej = 0
                with logfile.open("a", encoding="utf-8") as log:
                    for original in proc.stdout:
                        line = original.replace(wallet, "[PUBLIC_WALLET]")
                        log.write(line)
                        clean = re.sub(r"\x1b\[[0-9;]*m", "", line).strip()
                        value = speed_hs(clean)
                        match = SHARE.search(clean)
                        reject = REJECTED.search(clean)
                        profile = THREAD_PROFILE.search(clean)
                        ready = THREAD_READY.search(clean)
                        with lock:
                            state["lines"] += 1
                            if value is not None:
                                collected.append(value)
                            if match:
                                now_a, now_r = int(match.group(1)), int(match.group(2))
                                if now_a >= last_acc:
                                    state["accepted"] += now_a - last_acc
                                if now_r >= last_rej:
                                    state["rejected"] += now_r - last_rej
                                last_acc, last_rej = now_a, now_r
                            if reject:
                                now_a, now_r = int(reject.group(1)), int(reject.group(2))
                                if now_a >= last_acc:
                                    state["accepted"] += now_a - last_acc
                                if now_r >= last_rej:
                                    state["rejected"] += now_r - last_rej
                                last_acc, last_rej = now_a, now_r
                            actual = None
                            if profile:
                                actual = int(profile.group(1))
                            elif ready:
                                actual = int(ready.group(1))
                            if actual is not None:
                                if state["actual_threads"] != actual:
                                    state["actual_threads"] = actual
                                    state["thread_generation"] += 1
                            if "new job from" in clean.lower() or "use pool" in clean.lower():
                                state["connected"] = True
                            acc_total = state["accepted"]
                            rej_total = state["rejected"]
                        print("[XMRig] " + clean, flush=True)
                        if value is not None:
                            print(f"  Measured XMRig speed: {value:,.1f} H/s", flush=True)
                        elif match or reject:
                            print(f"  Pool shares — accepted: {acc_total} | rejected: {rej_total}", flush=True)
                        elif any(term in clean.lower() for term in (
                                "connect error", "connection refused", "invalid address",
                                "invalid login", "unauthorized", "no active pools")):
                            print("  XMRig connection/authorization error; check the saved log.", flush=True)

            reader = threading.Thread(target=collect, daemon=True)
            reader.start()

            def wait_until(target_time: float) -> bool:
                nonlocal reached_deadline
                while True:
                    if proc.poll() is not None:
                        return False
                    now = time.monotonic()
                    if now >= deadline:
                        reached_deadline = True
                        return False
                    if now >= target_time:
                        return True
                    time.sleep(0.2)

            def snapshot() -> tuple[int, int, int, int | None, int]:
                with lock:
                    return (len(collected), state["accepted"], state["rejected"],
                            state["actual_threads"], state["thread_generation"])

            def measure_profile(label: str, requested_threads: int | None, seconds: int) -> dict | None:
                sample_start, acc_start, rej_start, actual_start, gen_start = snapshot()
                # Allow startup/reload before measuring; startup is slower because the RandomX dataset
                # must be allocated. Keep the warm-up inside this profile's time budget.
                segment_start = time.monotonic()
                warmup = max(1, min(25, seconds // 4))
                if not wait_until(min(segment_start + warmup, deadline)):
                    return None
                sample_start, acc_start, rej_start, _, _ = snapshot()
                if not wait_until(min(segment_start + seconds, deadline)):
                    # A profile can still yield useful samples if the global deadline was reached.
                    pass
                sample_end, acc_end, rej_end, actual_end, gen_end = snapshot()
                with lock:
                    samples = collected[sample_start:sample_end]
                stats = _profile_stats(samples, max(0, acc_end - acc_start), max(0, rej_end - rej_start))
                stats.update({
                    "label": label,
                    "threads_requested": requested_threads if requested_threads is not None else "auto",
                    "threads_observed": actual_end or actual_start,
                    "seconds": round(time.monotonic() - segment_start, 1),
                    "reload_generation": gen_end - gen_start,
                })
                profiles.append(stats)
                shown_threads = stats["threads_observed"] or stats["threads_requested"]
                print(f"\n[ZTM optimizer] Profile {shown_threads} thread(s): median {stats['median_hs']} H/s, "
                      f"accepted {stats['accepted_shares']}, rejected {stats['rejected_shares']}, "
                      f"score {stats['score']}", flush=True)
                return stats

            try:
                max_profiles, profile_seconds = _profile_limits(duration_s)
                if threads is not None or max_profiles == 1:
                    # Explicit thread count or very short connectivity check: measure the requested
                    # configuration for the full duration without profile switching.
                    measure_profile("fixed" if threads is not None else "auto-connectivity", threads,
                                    max(0.1, deadline - time.monotonic()))
                    selected_threads = threads or snapshot()[3]
                else:
                    # Baseline: let XMRig choose its own RandomX profile first.
                    baseline = measure_profile("xmrig-auto-baseline", None, profile_seconds)
                    auto_threads = None if baseline is None else baseline.get("threads_observed")
                    logical = os.cpu_count() or 1
                    alternates = _candidate_threads(logical, auto_threads, max_profiles)
                    for candidate in alternates:
                        if time.monotonic() + profile_seconds >= deadline:
                            break
                        print(f"\n[ZTM optimizer] Testing {candidate} active thread(s)...", flush=True)
                        _write_profile_config(cfg_path, cfg, candidate)
                        before_gen = snapshot()[4]
                        # Give XMRig a short window to observe and apply the config change before
                        # starting the timed profile window. It remains the same privileged process.
                        reload_deadline = min(time.monotonic() + 15, deadline)
                        while proc.poll() is None and time.monotonic() < reload_deadline:
                            _, _, _, observed, generation = snapshot()
                            if observed == candidate and generation > before_gen:
                                break
                            time.sleep(0.25)
                        measure_profile(f"threads-{candidate}", candidate, profile_seconds)

                    valid = [p for p in profiles if p.get("median_hs") and p.get("threads_observed")]
                    if valid:
                        winner = max(valid, key=lambda p: (p["score"], p["median_hs"], -p.get("stability_cv", 1)))
                        selected_threads = int(winner["threads_observed"])
                        print(f"\n[ZTM optimizer] Winner: {selected_threads} active thread(s) "
                              f"({winner['median_hs']} H/s median during search).", flush=True)
                        _write_profile_config(cfg_path, cfg, selected_threads)
                        # Continue the remaining benchmark time on the selected profile.
                        if time.monotonic() < deadline:
                            remaining = max(0.1, deadline - time.monotonic())
                            measure_profile("winner-sustained", selected_threads, remaining)
                    else:
                        selected_threads = auto_threads
                        print("\n[ZTM optimizer] Insufficient profile samples; continuing XMRig automatic profile.", flush=True)
                        wait_until(deadline)
            except KeyboardInterrupt:
                interrupted.set()
                print("\nStopping XMRig by user request...", flush=True)
            finally:
                if time.monotonic() >= deadline and not interrupted.is_set():
                    reached_deadline = True
                # Ask the root guardian to stop its child before temporary
                # config is removed. Privileged process cannot be terminated
                # directly by this normal-user controller.
                stop_flag.touch(mode=0o600, exist_ok=True)
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    print('[ZTM] CRITICAL: privileged miner guardian did not stop; check sudo pgrep -a -x xmrig', flush=True)
                    raise BenchError('Privileged XMRig did not confirm shutdown')
                reader.join(timeout=5)
                if proc.stdout:
                    proc.stdout.close()
    except (OSError, subprocess.SubprocessError) as e:
        raise BenchError(f"Could not launch/read XMRig: {e}") from e

    elapsed = round(time.monotonic() - started, 1)
    with lock:
        values = collected[:]
        snapshots = state.copy()
    ran_full_time = reached_deadline and not interrupted.is_set() and len(values) > 0
    online_verified = snapshots["accepted"] > 0
    status = ("MEASURED_POOL_VERIFIED" if ran_full_time and online_verified else
              "PARTIAL_NO_ACCEPTED_SHARES" if ran_full_time else
              "STOPPED_OR_INCOMPLETE")
    report = {
        "project": "I2PS Dual-ISA RandomX Lab — online CPU engineering benchmark",
        "classification": "engineering_online_optimizer",
        "recorded_at_utc": start_wall,
        "host_os": platform.platform(), "architecture": platform.machine(),
        "cpu_model": current_cpu_info(), "logical_cpus": os.cpu_count(),
        "xmrig_version_target": VERSION, "xmrig_executable": str(executable),
        "pool": pool, "tls": tls,
        "threads_requested": threads if threads else "automatic_optimizer",
        "selected_threads": selected_threads,
        "requested_seconds": duration_s, "elapsed_seconds": elapsed,
        "hashrate_samples": len(values),
        "median_hs": round(statistics.median(values), 2) if values else None,
        "mean_hs": round(statistics.fmean(values), 2) if values else None,
        "min_hs": round(min(values), 2) if values else None,
        "max_hs": round(max(values), 2) if values else None,
        "accepted_shares": snapshots["accepted"], "rejected_shares": snapshots["rejected"],
        "optimizer_profiles": profiles,
        "status": status, "actual_24_hour_benchmark": bool(duration_s >= 86400 and elapsed >= 86400 and ran_full_time and online_verified),
        "source": "XMRig console readings; profile search uses sustained median, stability and rejection quality",
    }
    target = output_dir / f"run_{runid}.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    target.chmod(0o600)
    print("\n" + "=" * 63)
    print(" I2PS RANDOMX — ACTUAL ONLINE CPU TEST RESULT")
    print("=" * 63)
    print(f" CPU:                 {report['cpu_model']}")
    print(f" Selected threads:    {report['selected_threads']}")
    print(f" Profiles tested:     {len(report['optimizer_profiles'])}")
    print(f" Elapsed:             {elapsed:.1f} seconds / {duration_s} requested")
    print(f" Median hashrate:     {report['median_hs']} H/s")
    print(f" Average hashrate:    {report['mean_hs']} H/s")
    print(f" Accepted / rejected: {report['accepted_shares']} / {report['rejected_shares']}")
    print(f" Verification:        {status}")
    print(f" JSON report:         {target}")
    print(f" Diagnostic log:      {logfile}")
    print("=" * 63)
    if not values:
        return report, 3
    return report, 0 if ran_full_time and online_verified else 2

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="Only download and verify official XMRig; no mining")
    parser.add_argument("--session-stdin", action="store_true", help="Read pool, public wallet, duration and thread setting as JSON from stdin")
    parser.add_argument("--pool", help="Pool host:port supporting Monero/RandomX; prompted if omitted")
    parser.add_argument("--wallet", help="Public Monero receiving address; prompted if omitted; never a private key")
    parser.add_argument("--minutes", type=int, default=1440, help="Stable release benchmark duration: fixed at 1440 minutes (24 hours)")
    parser.add_argument("--seconds", type=int, help=argparse.SUPPRESS)  # internal automated test option
    parser.add_argument("--threads", type=int, help="Mining CPU threads; default: XMRig chooses")
    parser.add_argument("--no-tls", action="store_true", help="For pools without TLS; default requires TLS")
    parser.add_argument("--xmrig", help="Use an existing XMRig executable instead of downloading it")
    parser.add_argument("--yes", action="store_true", help="Explicitly authorize CPU work without interactive RUN prompt")
    parser.add_argument("--plan", action="store_true", help="Show what this test would do; do not download or mine")
    parser.add_argument("--output", default=str(Path.home() / "i2ps-randomx-results"), help="Output directory for report/log")
    a = parser.parse_args(argv)
    if a.session_stdin:
        payload = json.loads(sys.stdin.readline())
        a.pool = payload.get("pool")
        a.wallet = payload.get("wallet")
        a.minutes = int(payload.get("minutes", 1440))
        a.threads = int(payload["threads"]) if payload.get("threads") else None
        a.no_tls = not bool(payload.get("tls", True))
        a.yes = True  # GUI explicitly confirms BEFORE invoking --session-stdin
    if os.geteuid() == 0 and not a.plan:
        raise BenchError("Run as your normal Linux user, not as root or with sudo.")
    if a.minutes != 1440 or (a.seconds is not None and a.seconds != 86400):
        raise BenchError("ZTM-SRP1V1 requires exactly 24 hours (1440 minutes / 86400 seconds).")
    if a.threads is not None and not (1 <= a.threads <= (os.cpu_count() or 1)):
        raise BenchError("--threads must be between 1 and the detected logical CPU count.")
    if a.plan:
        print("I2PS ONLINE ENGINEERING SMOKE TEST — PLAN")
        print(f"- Platform: {platform.system()} {platform.machine()} | CPUs: {os.cpu_count()}")
        print(f"- XMRig: {'existing provided executable' if a.xmrig else VERSION + ' official upstream SHA-256 pinned Linux x64'}")
        print(f"- Duration: {a.seconds or a.minutes * 60} s | Threads: {a.threads or 'automatic'}")
        print(f"- TLS: {not a.no_tls} | Results: {a.output}")
        print("- Pool and PUBLIC Monero address are required; explicit consent before any mining")
        print("- No install/mining performed; no OS files or settings modified")
        return 0
    if a.prepare:
        local_binary(Path.home() / ".local" / "share" / "i2ps-randomx-test" / "xmrig-6.26.0", a.xmrig)
        print("ZTM PREPARATION COMPLETE: verified XMRig ready; no mining started", flush=True)
        return 0
    pool = validate_pool(prompt_if_missing(a.pool, "Pool server (host:port): "))
    wallet = validate_address(prompt_if_missing(a.wallet, "PUBLIC Monero receiving address (not private key): "))
    print(f"I2PS ENGINEERING ONLINE CPU TEST • CPU: {current_cpu_info()}")
    print("Only supported for Linux x86-64 in this version; existing OS is preserved.")
    executable = local_binary(Path.home() / ".local" / "share" / "i2ps-randomx-test" / "xmrig-6.26.0", a.xmrig)
    print(f"XMRig ready: {executable}")
    _, code = run_benchmark(executable, pool, wallet, not a.no_tls,
                            a.seconds or a.minutes * 60, a.threads,
                            Path(a.output).expanduser(), a.yes)
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (BenchError, OSError, ValueError, KeyboardInterrupt) as exc:
        print(f"I2PS benchmark not started/completed: {exc}", file=sys.stderr)
        sys.exit(1)
