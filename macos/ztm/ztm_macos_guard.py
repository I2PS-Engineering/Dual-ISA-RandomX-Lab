#!/usr/bin/env python3
"""Unprivileged macOS XMRig lifecycle guard.

The controller holds this process's stdin open. On controller loss, stdin closes,
and this guard signals and waits for its own process-group child.
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import threading
from pathlib import Path

stop = threading.Event()
child: subprocess.Popen | None = None


def terminate_child() -> None:
    global child
    if child is None or child.poll() is not None:
        return
    for sig, timeout in ((signal.SIGINT, 6), (signal.SIGTERM, 4), (signal.SIGKILL, 2)):
        if child.poll() is not None:
            return
        try:
            os.killpg(child.pid, sig)
        except ProcessLookupError:
            return
        try:
            child.wait(timeout=timeout)
            return
        except subprocess.TimeoutExpired:
            continue


def signal_stop(_sig: int, _frame: object) -> None:
    stop.set()
    terminate_child()


def stdin_monitor() -> None:
    # The parent never writes. EOF signifies that the controller died or exited.
    try:
        while sys.stdin.buffer.read(4096):
            pass
    except (OSError, ValueError):
        pass
    finally:
        stop.set()
        terminate_child()


def main(argv: list[str] | None = None) -> int:
    global child
    parser = argparse.ArgumentParser()
    parser.add_argument("--xmrig", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args(argv)
    from ztm_native import verified_binary
    verified_path = verified_binary().resolve()
    chosen = Path(args.xmrig).resolve(strict=True)
    if verified_path != chosen:
        raise RuntimeError("The requested XMRig path is not the verified native binary.")
    config = Path(args.config).resolve(strict=True)
    if not config.is_file() or config.is_symlink():
        raise RuntimeError("Untrusted or missing mining configuration.")
    if os.geteuid() == 0:
        raise RuntimeError("Do not execute the ZTM macOS miner as root.")

    signal.signal(signal.SIGTERM, signal_stop)
    signal.signal(signal.SIGINT, signal_stop)
    child = subprocess.Popen(
        [str(verified_path), "--config", str(config)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        start_new_session=True,
        close_fds=True,
    )
    watcher = threading.Thread(target=stdin_monitor, daemon=True)
    watcher.start()
    try:
        assert child.stdout is not None
        for line in child.stdout:
            if stop.is_set():
                break
            print(line.rstrip("\n"), flush=True)
        return_code = child.wait()
        return return_code if not stop.is_set() else 0
    finally:
        stop.set()
        terminate_child()
        if child.stdout is not None:
            child.stdout.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print("[ZTM] Native miner guard error: " + str(error), file=sys.stderr, flush=True)
        raise SystemExit(1)
