#!/usr/bin/env python3
"""One-prompt, session-scoped privilege broker for ZTM.

Launched ONCE using polkit/pkexec when user clicks Prepare Linux. Handles ONLY
four fixed maintenance operations and verified XMRig guardian operations;
never interprets arbitrary shell text or executes arbitrary binaries.
Ends when the original GUI process ends, and stops owned miners on exit.
"""
from __future__ import annotations
import argparse
import hashlib
import tempfile
import json
import os
from pathlib import Path
import pwd
import shutil
import signal
import socket
import stat
import subprocess
import sys
import threading
import time

from ztm_root_guard import process_identity
from ztm_engine import ASSET, ASSET_SHA256, MAX_ARCHIVE, extract_verified_archive

PACKAGES = ['ca-certificates', 'curl', 'tar', 'python3', 'kmod', 'msr-tools']
OPERATIONS = {
    'apt-update': ['/usr/bin/apt-get', 'update'],
    'apt-install': ['/usr/bin/apt-get', 'install', '-y', *PACKAGES],
    'apt-upgrade': ['/usr/bin/apt-get', 'upgrade', '-y'],
    'load-msr': ['/usr/sbin/modprobe', 'msr'],
}
MAX_FRAME = 8192


def validate_controller(pid: int, start_ticks: str, caller_uid: int) -> bool:
    ident = process_identity(pid)
    return bool(ident and ident[0] not in ('Z', 'X') and
                ident[1] == start_ticks and ident[2] == caller_uid)


def approved_paths(xmrig: str, config: str, stop_flag: str, uid: int) -> tuple[str,str,str]:
    home = Path(pwd.getpwuid(uid).pw_dir)
    binary = Path(xmrig)
    expected = home / '.local/share/i2ps-randomx-test/xmrig-6.26.0/xmrig'
    if binary.is_symlink() or binary.resolve() != expected.resolve() or not binary.is_file():
        raise ValueError('Unexpected XMRig binary location')
    config_file = Path(config)
    control = Path(stop_flag)
    if not config_file.is_file() or config_file.is_symlink() or config_file.name != 'xmrig.json':
        raise ValueError('Unexpected mining configuration file')
    if control.is_symlink() or config_file.parent.resolve() != control.parent.resolve() or control.name != 'stop.request':
        raise ValueError('Unexpected miner stop file')
    folder = config_file.parent
    fs = folder.stat()
    if fs.st_uid != uid or stat.S_IMODE(fs.st_mode) != 0o700 or folder.is_symlink():
        raise ValueError('Miner configuration directory ownership/mode rejected')
    if config_file.stat().st_uid != uid:
        raise ValueError('Miner configuration owner rejected')
    archive = expected.parent / ASSET
    if archive.is_symlink() or not archive.is_file() or archive.stat().st_size>MAX_ARCHIVE:
        raise ValueError('Official XMRig archive missing; run Prepare Linux first')
    return str(expected), str(config_file), str(control)


class SessionBroker:
    def __init__(self, location: str, gui_pid: int, gui_ticks: str, user_id: int):
        self.location=location
        self.gui_pid=gui_pid
        self.gui_ticks=gui_ticks
        self.uid=user_id
        self.lock=threading.Lock()
        self.closing=threading.Event()
        self.miners: dict[int, tuple[subprocess.Popen,Path]] = {}
        self.listener: socket.socket | None = None

    def still_authorized(self):
        return validate_controller(self.gui_pid, self.gui_ticks, self.uid)

    def send(self, client, typ, **data):
        frame = json.dumps({'type':typ, **data}, ensure_ascii=True) + '\n'
        client.sendall(frame.encode('utf-8'))

    def run_task(self, client, cmd: list[str], guarded=False, flag: Path | None=None, drop_uid_env=False):
        if not self.lock.acquire(blocking=False):
            self.send(client,'line',text='Another privileged ZTM task is already running.')
            return 1
        proc=None
        try:
            environment={**os.environ, 'PKEXEC_UID':str(self.uid)}
            if drop_uid_env:
                # Identity validation is performed by THIS approved root broker.
                # The unchanged guardian permits a root-owned verified binary
                # when PKEXEC_UID is absent, and still checks owner PID/starttime.
                environment.pop('PKEXEC_UID',None)
            proc=subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, bufsize=0, start_new_session=guarded,
                    env=environment)
            if guarded:
                self.miners[proc.pid]=(proc,flag)
            assert proc.stdout is not None
            while True:
                data=proc.stdout.readline()
                if not data: break
                line=data.decode('utf-8',errors='replace').rstrip('\n')
                try: self.send(client,'line',text=line)
                except (BrokenPipeError,ConnectionResetError,OSError):
                    # A dead client must not leave a miner running.
                    if guarded and flag is not None: flag.touch(mode=0o600,exist_ok=True)
                    break
                if self.closing.is_set() and guarded and flag is not None:
                    flag.touch(mode=0o600,exist_ok=True)
            try: proc.wait(timeout=15 if guarded else 20)
            except subprocess.TimeoutExpired:
                if guarded and flag is not None: flag.touch(mode=0o600,exist_ok=True)
                try: proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.stop_guard(proc,flag)
            return proc.returncode or 0
        finally:
            if proc is not None:
                self.miners.pop(proc.pid,None)
                if proc.stdout is not None: proc.stdout.close()
            self.lock.release()

    @staticmethod
    def stop_guard(proc, flag):
        if flag is not None:
            try: flag.touch(mode=0o600,exist_ok=True)
            except OSError: pass
        try: proc.wait(timeout=7)
        except subprocess.TimeoutExpired:
            try: os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError: pass
            try: proc.wait(timeout=4)
            except subprocess.TimeoutExpired:
                try: os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError: pass

    def handle(self, conn:socket.socket):
        stream=None
        try:
            credentials=conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12)
            import struct
            _, uid, _ = struct.unpack('3i', credentials)
            if uid != self.uid or not self.still_authorized(): return
            stream=conn.makefile('rb')
            data=stream.readline(MAX_FRAME+1)
            if len(data)>MAX_FRAME: return
            req=json.loads(data)
            op=req.get('op'); arguments=req.get('args',[])
            if not isinstance(arguments,list) or any(not isinstance(a,str) for a in arguments): return
            if op in OPERATIONS and not arguments:
                code=self.run_task(conn,OPERATIONS[op]); self.send(conn,'exit',code=code)
            elif op=='miner' and len(arguments)==5:
                binary,cfg,stop_flag,owner_pid,owner_ticks=arguments
                if not owner_pid.isdecimal() or not validate_controller(int(owner_pid),owner_ticks,self.uid):
                    raise ValueError('Miner controller identity rejected')
                bin_file,cfg_file,flag_file=approved_paths(binary,cfg,stop_flag,self.uid)
                # Never run the user's mutable cached XMRig as root. Verify the
                # original upstream asset using our root-owned code's pinned SHA,
                # then execute a root-private copy extracted from that archive.
                asset=Path(bin_file).parent / ASSET
                blob=asset.read_bytes()
                if hashlib.sha256(blob).hexdigest()!=ASSET_SHA256:
                    raise ValueError('SECURITY STOP: upstream mining binary signature mismatch')
                exe=extract_verified_archive(blob)
                with tempfile.TemporaryDirectory(prefix='ztm-verified-xmrig-') as tmp:
                    root_binary=Path(tmp)/'xmrig'
                    root_binary.write_bytes(exe)
                    root_binary.chmod(0o700)
                    cmd=['/usr/bin/python3',str(Path(__file__).with_name('ztm_root_guard.py')),
                         '--xmrig',str(root_binary),'--config',cfg_file,'--stop-flag',flag_file,
                         '--owner-pid',owner_pid,'--owner-start',owner_ticks]
                    code=self.run_task(conn,cmd,guarded=True,flag=Path(flag_file),drop_uid_env=True)
                self.send(conn,'exit',code=code)
            elif op=='ping' and not arguments:
                self.send(conn,'exit',code=0)
            elif op=='shutdown' and not arguments:
                self.closing.set(); self.send(conn,'exit',code=0)
            else:
                self.send(conn,'line',text='Rejected unauthorized ZTM operation.')
                self.send(conn,'exit',code=2)
        except Exception as exc:
            try:
                self.send(conn,'line',text='Privileged operation rejected: '+str(exc))
                self.send(conn,'exit',code=2)
            except OSError: pass
        finally:
            if stream is not None: stream.close()
            try: conn.close()
            except OSError: pass

    def serve(self):
        loc=Path(self.location)
        folder=loc.parent
        info=folder.stat()
        if folder.is_symlink() or info.st_uid!=self.uid or stat.S_IMODE(info.st_mode)!=0o700:
            raise SystemExit('SECURITY STOP: invalid session socket directory')
        if not self.still_authorized(): raise SystemExit('SECURITY STOP: invalid GUI identity')
        if loc.exists() or loc.is_symlink(): raise SystemExit('SECURITY STOP: socket path already exists')
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as server:
            self.listener=server
            server.bind(self.location)
            os.chown(self.location,self.uid,-1)
            os.chmod(self.location,0o600)
            server.listen(5)
            server.settimeout(0.2)
            try:
                while not self.closing.is_set() and self.still_authorized():
                    try: conn,_ = server.accept()
                    except socket.timeout: continue
                    th=threading.Thread(target=self.handle,args=(conn,),daemon=True)
                    th.start()
            finally:
                self.closing.set()
                for proc,flag in list(self.miners.values()):
                    self.stop_guard(proc,flag)
                try: os.unlink(self.location)
                except OSError: pass
        return 0


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--socket',required=True)
    p.add_argument('--owner-pid',required=True,type=int)
    p.add_argument('--owner-start',required=True)
    a=p.parse_args()
    if os.geteuid()!=0 or 'PKEXEC_UID' not in os.environ:
        raise SystemExit('Session broker requires pkexec from an authorized local desktop user')
    return SessionBroker(a.socket,a.owner_pid,a.owner_start,int(os.environ['PKEXEC_UID'])).serve()

if __name__=='__main__':sys.exit(main())
