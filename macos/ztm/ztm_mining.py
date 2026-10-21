#!/usr/bin/env python3
"""ZTM macOS P1: verified native XMRig with upstream and I2PS dev contributions.

Donation fraction is scheduling time, not a guaranteed revenue or accepted-share fraction.
No XMRig subprocess survives deliberate termination of this controller.
"""
from __future__ import annotations
import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from ztm_engine import validate_address, local_binary, validate_pool, VERSION, current_cpu_info, speed_hs, SHARE, REJECTED
from ztm_eligibility import latest_qualified_report

HASHVAULT = 'pool.hashvault.pro:443'
# Public mining address used for initial Dev Wallet benchmark (ownership verification remains operationally required).
I2PS_RECEIVING_ADDRESS = '4AZPLhPbHimHbCsJarX6ThB2Rqo8jrHbjLJ3oFjsgA1gVWgFBtxywdQiFkS5Vn2E3eDR69oY7F1VbfnmrqBmbHB9Jpmsz9f'
I2PS_CYCLE_SECONDS = 6000  # 100 min time base
I2PS_SLOT_SECONDS = 60  # one minute per 100 min, switching one process


def mining_config(address: str, *, donation: bool = False, threads: int | None = None) -> dict:
    address = validate_address(I2PS_RECEIVING_ADDRESS if donation else address)
    configuration = {
        'autosave': False, 'watch': True, 'coin': 'monero', 'algo': 'rx/0',
        'donate-level': 1,  # preserve the upstream XMRig donation, separate from I2PS
        'pools': [{'url': validate_pool(HASHVAULT), 'user': address,
                   'pass': 'ZTM-I2PS-Donate' if donation else 'ZTM-Personal-Mining',
                   'rig-id': 'ZTM-I2PS-Donate' if donation else 'ZTM-Personal-Mining',
                   'tls': False, 'keepalive': True}],
        'cpu': {'enabled': True, 'huge-pages': False},
        'randomx': {'init': -1, 'rdmsr': False, 'wrmsr': False, '1gb-pages': False},
        'opencl': {'enabled': False}, 'cuda': {'enabled': False},
        'print-time': 10, 'colors': False, 'http': {'enabled': False},
    }
    if threads is not None:
        if not isinstance(threads, int) or not 1 <= threads <= (os.cpu_count() or 1):
            raise ValueError('Invalid benchmark-selected CPU thread count')
        configuration['cpu']['rx'] = [-1] * threads
    return configuration


def write_config(path: Path, cfg: dict) -> None:
    temp = path.with_suffix('.new')
    temp.write_text(json.dumps(cfg), encoding='utf-8')
    temp.chmod(0o600)
    os.replace(temp, path)


def mining_cycle(current: float, start: float) -> bool:
    """One 60-second I2PS interval per 6000-second cycle, after the initial 5940 seconds."""
    progress = (current - start) % I2PS_CYCLE_SECONDS
    return progress >= I2PS_CYCLE_SECONDS - I2PS_SLOT_SECONDS


def mine(address: str, result_dir: Path | None = None) -> int:
    qualified = latest_qualified_report(result_dir)
    if qualified is None:
        raise SystemExit('PERSONAL MINING LOCKED: complete a verified uninterrupted 24-hour benchmark first.')
    if qualified.get('cpu_model') != current_cpu_info() or qualified.get('logical_cpus') != os.cpu_count():
        raise SystemExit('PERSONAL MINING LOCKED: the 24-hour benchmark belongs to another CPU or system.')
    threads = int(qualified['selected_threads'])
    if not 1 <= threads <= (os.cpu_count() or 1):
        raise SystemExit('PERSONAL MINING LOCKED: qualified CPU profile does not match this machine.')
    address = validate_address(address)
    binary = local_binary(Path.home() / 'Library' / 'Application Support' / 'I2PS' / 'ZTM' / f'xmrig-{VERSION}')
    with tempfile.TemporaryDirectory(prefix='ztm-mine-') as directory:
        path = Path(directory) / 'xmrig.json'
        write_config(path, mining_config(address, threads=threads))
        # macOS uses a non-root guardian; controller stdin closure stops XMRig.
        from ztm_native import child_command
        command = child_command('guardian', '--xmrig', str(binary),
                                '--config', str(path))
        process = subprocess.Popen(command,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            errors='replace', bufsize=1, start_new_session=True)
        started = time.monotonic()
        print(f'[ZTM] Using qualified 24-hour benchmark: {threads} active CPU thread(s)', flush=True)
        current_donation = False
        import threading
        def reader():
            accepted = rejected = 0
            for original in process.stdout:
                raw = original.strip()
                line = raw.replace(address, '[USER_WALLET]').replace(I2PS_RECEIVING_ADDRESS, '[DEV_WALLET]')
                print('[XMRig] ' + line, flush=True)
                speed = speed_hs(raw)
                if speed is not None:
                    print(f'  Measured XMRig speed: {speed:,.1f} H/s', flush=True)
                good = SHARE.search(raw)
                bad = REJECTED.search(raw)
                if good or bad:
                    match = good or bad
                    accepted = max(accepted, int(match.group(1)))
                    rejected = max(rejected, int(match.group(2)))
                    print(f'  Pool shares — accepted: {accepted} | rejected: {rejected}', flush=True)
        thread = threading.Thread(target=reader, daemon=True)
        thread.start()
        try:
            while process.poll() is None:
                donor = mining_cycle(time.monotonic(), started)
                if donor != current_donation:
                    write_config(path, mining_config(address, donation=donor, threads=threads))
                    print('[ZTM] I2PS contribution interval' if donor else '[ZTM] Personal mining resumed', flush=True)
                    current_donation = donor
                time.sleep(1.0)
        except KeyboardInterrupt:
            print('[ZTM] Stopping personal mining', flush=True)
        finally:
            if process.stdin is not None and not process.stdin.closed:
                process.stdin.close()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                print('[ZTM] CRITICAL: native miner shutdown not confirmed', flush=True)
                raise RuntimeError('Native XMRig did not confirm shutdown')
            thread.join(timeout=4)
    return 0 if process.returncode in (0, -signal.SIGTERM, -signal.SIGINT) else (process.returncode or 0)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--session-stdin', action='store_true')
    parser.add_argument('--output', default=str(Path.home() / 'ZTM-Results'))
    args = parser.parse_args(argv)
    if not args.session_stdin or os.geteuid() == 0:
        raise SystemExit('Use ZTM GUI as a normal macOS desktop user.')
    payload = json.loads(sys.stdin.readline())
    if payload.get('authorized') is not True:
        raise SystemExit('Mining Terms & Conditions acceptance required.')
    return mine(payload.get('public_address', ''), Path(args.output))

if __name__ == '__main__':
    sys.exit(main())
