#!/usr/bin/env python3
"""Apply five auditable, narrowly scoped improvements to extracted SRP1V2 .deb.

Input is a package extraction (`dpkg-deb -R`) of the verified current stable
package. This script does not fetch, publish, mine or alter a machine.
"""
from pathlib import Path
import shutil,sys

if len(sys.argv)!=2:raise SystemExit('usage: patch_srp1v2_surgical.py <dpkg-deb -R extracted root>')
root=Path(sys.argv[1]); lib=root/'usr/lib/ztm'
source=Path(__file__).with_name('ztm_surgical_runtime.py')
if not lib.is_dir():raise SystemExit('STOP: no extracted ZTM package')

def replace(path,old,new,label):
    s=path.read_text()
    if s.count(old)!=1:raise SystemExit(f'STOP {label}: expected one anchor, got {s.count(old)}')
    path.write_text(s.replace(old,new))

GUI=lib/'ztm_gui.py';ENGINE=lib/'ztm_engine.py';BROKER=lib/'ztm_privileged_session.py';CLIENT=lib/'ztm_privilege_client.py'; MINING=lib/'ztm_mining.py'
# 1: Do not remove two benchmark consent controls, only the top apt checkbox.
replace(GUI,"        self.upgrade_all = tk.BooleanVar(value=False)\n",'', 'upgrade model')
s=GUI.read_text()
line=next((l for l in s.splitlines(True) if "text='Also upgrade already-installed Ubuntu packages" in l),None)
if not line:raise SystemExit('STOP: upgrade checkbox not found')
replace(GUI,line,'','upgrade checkbox widget')
replace(GUI,
"'ZTM will run apt-get update, install required packages, and download official XMRig 6.26.0 (SHA-256 verified).'+ ('\\nSystem packages will also be upgraded.' if self.upgrade_all.get() else '') + '\\n\\nUbuntu will request administrator authorization. Continue?'",
"'ZTM will update and upgrade installed Ubuntu packages, prepare Huge Pages and MSR, install required packages and verified XMRig 6.26.0.\\n\\nUbuntu will request administrator authorization. Continue?'",'preparation consent prompt')
replace(GUI,
"            steps = prepare_steps()\n            if self.upgrade_all.get():\n                steps.insert(1, ('Upgrade installed packages', [sys.executable,str(SESSION_CLIENT),'apt-upgrade']))\n",
"            steps = prepare_steps()\n",'upgrade flow')
replace(GUI,
"        ('APT refresh', client + ['apt-update']),\n        ('Install prerequisites', client + ['apt-install']),\n        ('Load CPU MSR support', client + ['load-msr']),",
"        ('Stop competing XMRig processes', client + ['cleanup-miners']),\n        ('APT refresh', client + ['apt-update']),\n        ('Upgrade installed Ubuntu packages', client + ['apt-upgrade']),\n        ('Install prerequisites', client + ['apt-install']),\n        ('Prepare RandomX Huge Pages', client + ['prepare-hugepages']),\n        ('Load CPU MSR support', client + ['load-msr']),",'prepare tasks')
# Two checkpoints, at preparation and at benchmark/personal-mining start.
replace(GUI,
"            cmd = [sys.executable, '-u', str(ENGINE), '--session-stdin', '--output', str(RESULTS)]\n            result = self.run_command(cmd, json.dumps(session))",
"            check = self.run_command([sys.executable, str(SESSION_CLIENT), 'cleanup-miners'])\n            if check != 0:\n                self.q.put(('line','[ZTM] Benchmark blocked: competing miners did not stop.'))\n                self.q.put(('done-bench', check))\n                return\n            cmd = [sys.executable, '-u', str(ENGINE), '--session-stdin', '--output', str(RESULTS)]\n            result = self.run_command(cmd, json.dumps(session))",'benchmark preflight')
replace(GUI,
"            cmd = [sys.executable, '-u', str(MINING), '--session-stdin', '--output', str(RESULTS)]\n            result = self.run_command(cmd, json.dumps({'public_address': record['public_address'], 'authorized': True}))",
"            check = self.run_command([sys.executable, str(SESSION_CLIENT), 'cleanup-miners'])\n            if check != 0:\n                self.q.put(('line','[ZTM] Personal mining blocked: competing miners did not stop.'))\n                self.q.put(('done-mine',check))\n                return\n            cmd = [sys.executable, '-u', str(MINING), '--session-stdin', '--output', str(RESULTS)]\n            result = self.run_command(cmd, json.dumps({'public_address': record['public_address'], 'authorized': True}))",'mining preflight')
# Broker keeps allowlist fixed, owner credentials checked by its existing handle().
replace(CLIENT,
"'apt-upgrade', 'load-msr', 'miner'",
"'apt-upgrade', 'load-msr', 'prepare-hugepages', 'cleanup-miners', 'miner'",'client operations')
replace(BROKER,
"from ztm_engine import ASSET, ASSET_SHA256, MAX_ARCHIVE, extract_verified_archive",
"from ztm_engine import ASSET, ASSET_SHA256, MAX_ARCHIVE, extract_verified_archive\nfrom ztm_surgical_runtime import recognized_miners, stop_recognized_miners, prepare_hugepages",'broker imports')
replace(BROKER,
"            elif op=='miner' and len(arguments)==5:",
"            elif op=='cleanup-miners' and not arguments:\n                # Authorized by peer credentials and GUI lifetime. Fixed behavior, no arguments.\n                success=stop_recognized_miners(self.uid,emit=lambda message:self.send(conn,'line',text=message))\n                self.send(conn,'exit',code=0 if success else 3)\n            elif op=='prepare-hugepages' and not arguments:\n                prepare_hugepages(emit=lambda message:self.send(conn,'line',text=message))\n                self.send(conn,'exit',code=0)\n            elif op=='miner' and len(arguments)==5:",'privileged operations')
replace(BROKER,
"                bin_file,cfg_file,flag_file=approved_paths(binary,cfg,stop_flag,self.uid)",
"                # Second broker-side check closes the gap after the GUI preflight.\n                if recognized_miners(self.uid,exclude=tuple(self.miners)):\n                    raise ValueError('Competing XMRig is active or restarting. Stop mining services before proceeding.')\n                bin_file,cfg_file,flag_file=approved_paths(binary,cfg,stop_flag,self.uid)",'miner last moment check')
# Engine: hardware-aware profile selection with RNG, log distinct initialization.
replace(ENGINE,
"import statistics\n",
"import statistics\nimport secrets\nfrom ztm_surgical_runtime import cpu_inventory, candidate_profiles, choose_init_threads\n",'engine import')
replace(ENGINE,
"                    logical = os.cpu_count() or 1\n                    alternates = _candidate_threads(logical, auto_threads, max_profiles)",
"                    inventory = cpu_inventory()\n                    alternates = candidate_profiles(inventory, auto_threads, max_profiles, seed=profile_seed)\n                    print(f'[ZTM optimizer] Hardware: {inventory}', flush=True)\n                    print(f'[ZTM optimizer] Randomized candidate order: {alternates}', flush=True)", 'candidate generation')
replace(ENGINE,
"    profiles: list[dict] = []\n    selected_threads: int | None = threads",
"    profiles: list[dict] = []\n    inventory = cpu_inventory()\n    profile_seed = secrets.randbits(64)\n    randomx_init = choose_init_threads(inventory, None, seed=profile_seed)\n    print(f'[ZTM optimizer] RandomX dataset initialization threads for this run: {randomx_init}',flush=True)\n    selected_threads: int | None = threads",'random initializer')
replace(ENGINE,
'"randomx": {"init": -1, "rdmsr": True, "wrmsr": True, "1gb-pages": False}',
'"randomx": {"init": randomx_init, "rdmsr": True, "wrmsr": True, "1gb-pages": False}', 'randomx init')
replace(ENGINE,
'        "cpu_model": current_cpu_info(), "logical_cpus": os.cpu_count(),',
'        "cpu_model": current_cpu_info(), "logical_cpus": os.cpu_count(),\n        "cpu_inventory": inventory, "optimizer_random_seed": profile_seed,\n        "randomx_initialization_threads": randomx_init,\n        "init_threads_note": "RandomX initialization is fixed per process; live candidate reloads vary active threads only",', 'report inventory')
# Explicitly separate independently logged status from success claims.
replace(ENGINE,
'        "source": "XMRig console readings; profile search uses sustained median, stability and rejection quality",',
'        "source": "XMRig console readings; profile search uses sustained median, stability and rejection quality",\n        "hugepages_reserved": inventory.get("hugepages_total"),\n        "hugepages_free_pre_run": inventory.get("hugepages_free"),\n        "msr_device_detected": inventory.get("msr_device_present"),', 'reported memory optimization')
# Personal mining retains previous winner-thread decision and wallet rules.
shutil.copy2(source, lib/source.name)
# Mark clearly as locally testable candidate; no assumption of automatic public release.
control=root/'DEBIAN/control'
replace(control,'Version: 1.2.0~srp1v2','Version: 1.2.1~srp1v2rc1','candidate version')
assert GUI.read_text().count('self.confirm_power')>=2
assert GUI.read_text().count('self.confirm_reward')>=2
assert 'self.upgrade_all' not in GUI.read_text()
assert 'minutes = 1440' in GUI.read_text()
assert 'ZTM-SRP1V2' in GUI.read_text()
print('OK: SRP1V2 targeted patch applied (GUI, engine, broker, client, helper, control)')
