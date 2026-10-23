#!/usr/bin/env python3
"""Surgical RC1->RC2 patch: repair optimizer shadowing and pre-GUI XMRig gate."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit('usage: patch_rc1_to_rc2.py <dpkg-deb extracted root>')
root=Path(sys.argv[1]); lib=root/'usr/lib/ztm'

def change(path,old,new,name):
    s=path.read_text(encoding='utf-8')
    n=s.count(old)
    if n != 1: raise SystemExit(f'STOP {name}: expected one exact anchor, got {n}')
    path.write_text(s.replace(old,new),encoding='utf-8')

engine=lib/'ztm_engine.py'
change(engine,"    candidate_profiles = [\n        p for p in profiles",
      "    tested_candidate_profiles = [\n        p for p in profiles",
      'shadowing assignment')
change(engine,"(p for p in candidate_profiles if p.get('threads_observed') == selected_threads)",
      "(p for p in tested_candidate_profiles if p.get('threads_observed') == selected_threads)",
      'shadowing reference')
launcher=root/'usr/bin/ztm'
change(launcher,'exec /usr/bin/python3 /usr/lib/ztm/ztm_gui.py "$@"',
'''# An authenticated, machine-wide XMRig cleanup is mandatory on EVERY GUI launch.
# A failure or respawning miner blocks GUI startup before benchmarking is possible.
if [ "$(id -u)" -eq 0 ]; then
    echo 'ZTM: launch as your ordinary desktop user, not root.' >&2
    exit 1
fi
if ! command -v pkexec >/dev/null 2>&1; then
    echo 'ZTM: pkexec/polkit is required to check root-owned miners.' >&2
    exit 1
fi
printf '%s\n' 'ZTM: checking all recognized XMRig processes before GUI startup...'
if ! pkexec /usr/bin/python3 /usr/lib/ztm/ztm_startup_preflight.py; then
    echo 'ZTM: startup blocked. A miner remains, restarts or authorization was denied.' >&2
    exit 1
fi
exec /usr/bin/python3 /usr/lib/ztm/ztm_gui.py "$@"''','pre-GUI gate')
preflight=lib/'ztm_startup_preflight.py'
if preflight.exists(): raise SystemExit('STOP: preflight script already exists')
preflight.write_text('''#!/usr/bin/env python3
"""Machine-wide, fail-closed, fixed-operation XMRig preflight before GUI startup."""
import os
import sys
import time
from ztm_surgical_runtime import recognized_miners, stop_recognized_miners

def main() -> int:
    # Require polkit origin identity; no bare root/sudo invocation accepted.
    caller=os.environ.get('PKEXEC_UID','')
    if os.geteuid()!=0 or not caller.isdecimal() or int(caller)==0:
        print('ZTM: startup preflight requires non-root user authorization via pkexec.',
              file=sys.stderr,flush=True)
        return 4
    print('[ZTM] Startup: checking recognized XMRig processes for all local owners',flush=True)
    # uid=None includes root and all other accounts, not just the GUI owner.
    if not stop_recognized_miners(None,emit=lambda s:print(s,flush=True),timeout=4):
        print('[ZTM] Startup blocked: competing XMRig remains or restarts.',
              file=sys.stderr,flush=True)
        return 5
    time.sleep(1.25)  # Detect a service that relaunches the miner after termination.
    remaining=recognized_miners(None)
    if remaining:
        print(f'[ZTM] Startup blocked: {len(remaining)} miner(s) restarted.',
              file=sys.stderr,flush=True)
        return 6
    print('[ZTM] Startup preflight PASS: zero recognized XMRig processes.',flush=True)
    return 0

if __name__=='__main__':
    sys.exit(main())
''',encoding='utf-8')
change(root/'DEBIAN/control','Version: 1.2.1~srp1v2rc1',
       'Version: 1.2.2~srp1v2rc2','Debian version')
assert engine.read_text().count('tested_candidate_profiles')==2
assert 'candidate_profiles(inventory, auto_threads' in engine.read_text()
assert 'ztm_startup_preflight.py' in launcher.read_text()
print('RC2 patch applied: real benchmark shadowing crash fixed and pre-GUI cleanup gate installed')
