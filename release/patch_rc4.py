#!/usr/bin/env python3
"""Apply V2 RC4 changes to the extracted RC3 Debian package. Fail closed."""
from pathlib import Path
import sys,shutil
if len(sys.argv)!=2: raise SystemExit('usage: patch_rc4.py <extracted RC3 package root>')
root=Path(sys.argv[1]);lib=root/'usr/lib/ztm'
engine=lib/'ztm_engine.py';gui=lib/'ztm_gui.py'
def replace_once(path,old,new):
    data=path.read_text()
    if data.count(old)!=1: raise SystemExit(f'RC4 STOP {path.name}: expected one {old!r}, found {data.count(old)}')
    path.write_text(data.replace(old,new))
replace_once(engine,'PROFILE_SECONDS = 300','PROFILE_SECONDS = 900')
replace_once(engine,'MAX_PROFILE_COUNT = 11','MAX_PROFILE_COUNT = 7')
replace_once(gui,'05:00','15:00')
# Existing GUI code derives live targets from engine structured progress.
# The topology runtime is copied from the isolated V2 source branch.
source=Path(__file__).with_name('ztm_surgical_runtime.py')
if not source.exists(): raise SystemExit('RC4 STOP: topology source absent')
shutil.copy2(source,lib/'ztm_surgical_runtime.py')
replace_once(root/'DEBIAN/control','Version: 1.2.3~srp1v2rc3','Version: 1.2.4~srp1v2rc4')
assert (lib/'ztm_startup_preflight.py').exists()
assert 'ztm_startup_preflight.py' in (root/'usr/bin/ztm').read_text()
print('RC4 staged: 7 maximum profiles, 900 seconds, topology-aware ranking')
