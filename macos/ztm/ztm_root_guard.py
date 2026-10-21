#!/usr/bin/env python3
"""Privilege-bounded XMRig lifecycle guardian invoked through polkit (pkexec).

Owns and terminates its root XMRig child when the ordinary-user controller
requests stop OR exits. No sudo password storage, no daemon or service.
"""
from __future__ import annotations
import argparse
import ctypes
import os
from pathlib import Path
import pwd
import signal
import subprocess
import sys
import time

PR_SET_PDEATHSIG = 1


def process_identity(pid: int):
    """Return (state, startticks, realuid) for an existing Linux process."""
    try:
        stat = Path(f'/proc/{pid}/stat').read_text()
        post = stat.rsplit(')', 1)[1].strip().split()
        uid = next(x for x in Path(f'/proc/{pid}/status').read_text().splitlines()
                   if x.startswith('Uid:')).split()[1]
        return post[0], post[19], int(uid)  # starttime is stat field 22.
    except (OSError, ValueError, IndexError, StopIteration):
        return None


def child_parent_death():
    """If the guardian is abruptly terminated, signal the miner too."""
    ctypes.CDLL(None, use_errno=True).prctl(PR_SET_PDEATHSIG, signal.SIGTERM, 0, 0, 0)


def stop_miner(proc, grace=7.0):
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGINT)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait(timeout=5)


def guard(binary, cfg, stop_flag, owner_pid, owner_ticks):
    caller_uid_str = os.environ.get('PKEXEC_UID')
    if caller_uid_str is not None:
        owner = process_identity(owner_pid)
        if not owner or owner[2] != int(caller_uid_str):
            raise SystemExit('SECURITY STOP: controller ownership mismatch')
    owner_start = process_identity(owner_pid)
    if not owner_start or owner_start[1] != owner_ticks or owner_start[0] == 'Z':
        raise SystemExit('SECURITY STOP: controller process is no longer active')
    binary, cfg, stop_flag = (Path(binary).resolve(), Path(cfg).resolve(), Path(stop_flag))
    if not binary.is_file() or binary.name != 'xmrig' or not binary.is_file():
        raise SystemExit('SECURITY STOP: unexpected miner executable')
    if not cfg.is_file() or cfg.name != 'xmrig.json' or stop_flag.parent != cfg.parent:
        raise SystemExit('SECURITY STOP: unexpected configuration location')
    if cfg.is_symlink() or stop_flag.is_symlink():
        raise SystemExit('SECURITY STOP: symlinked mining config/control')
    # This root helper is only allowed to execute the known cached XMRig path.
    if caller_uid_str is not None:
        expected = (Path(pwd.getpwuid(int(caller_uid_str)).pw_dir) /
                    '.local/share/i2ps-randomx-test/xmrig-6.26.0/xmrig').resolve()
        if binary != expected:
            raise SystemExit('SECURITY STOP: unrecognized XMRig path')
    proc = subprocess.Popen([str(binary),'--config',str(cfg),'--no-color'],
                            stdin=subprocess.DEVNULL, stdout=None, stderr=subprocess.STDOUT,
                            start_new_session=True, preexec_fn=child_parent_death)
    stopped_by_controller = False
    try:
        while proc.poll() is None:
            identity = process_identity(owner_pid)
            if (stop_flag.exists() or identity is None or identity[0] == 'Z' or
                identity[1] != owner_ticks):
                stopped_by_controller = True
                stop_miner(proc)
                break
            time.sleep(0.2)
    except BaseException:
        stop_miner(proc)
        raise
    finally:
        stop_miner(proc)
    return 0 if stopped_by_controller else (proc.returncode or 0)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--xmrig',required=True)
    p.add_argument('--config',required=True)
    p.add_argument('--stop-flag',required=True)
    p.add_argument('--owner-pid',required=True,type=int)
    p.add_argument('--owner-start',required=True)
    a=p.parse_args()
    return guard(a.xmrig,a.config,a.stop_flag,a.owner_pid,a.owner_start)

if __name__ == '__main__':
    sys.exit(main())
