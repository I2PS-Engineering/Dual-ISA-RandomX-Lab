#!/usr/bin/env python3
"""ZTM authenticated-session client, deliberately unprivileged.

Talks to the single session-scoped root broker started through desktop polkit.
Does not cache any authentication secret and cannot issue arbitrary commands.
"""
from __future__ import annotations
import argparse
import json
import os
import socket
import sys
from pathlib import Path

ALLOWED = {'apt-update', 'apt-install', 'apt-upgrade', 'load-msr', 'miner', 'shutdown', 'ping'}


def call(operation: str, args: list[str] | None = None, sock_path: str | None = None, emit=print) -> int:
    if operation not in ALLOWED:
        raise ValueError('Unsupported privileged operation')
    path = sock_path or os.environ.get('ZTM_SESSION_SOCKET', '')
    if not path:
        raise RuntimeError('No active ZTM authorized session. Use Prepare Linux first.')
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
        conn.settimeout(20)
        conn.connect(path)
        conn.sendall((json.dumps({'op': operation, 'args': args or []}) + '\n').encode('utf-8'))
        conn.settimeout(None)
        with conn.makefile('r', encoding='utf-8', errors='replace') as replies:
            for line in replies:
                msg = json.loads(line)
                if msg['type'] == 'line': emit(msg['text'])
                if msg['type'] == 'exit': return int(msg['code'])
    raise RuntimeError('Privileged session disconnected before operation completed')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('operation', choices=sorted(ALLOWED))
    p.add_argument('arguments', nargs='*')
    a = p.parse_args()
    try:
        return call(a.operation, a.arguments)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f'ZTM authorized session error: {exc}', file=sys.stderr, flush=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
