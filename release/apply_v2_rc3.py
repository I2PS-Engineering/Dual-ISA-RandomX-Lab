#!/usr/bin/env python3
"""ZTM V2 RC3 ONLY: deterministic profile test and verified stop/restart.

Input: dpkg-deb -R extraction of V2 RC2 source. Never edits V3.
"""
from pathlib import Path
import sys
if len(sys.argv)!=2: raise SystemExit('usage: apply_v2_rc3.py <extracted-rc2-root>')
root=Path(sys.argv[1]); lib=root/'usr/lib/ztm'
engine=lib/'ztm_engine.py'; gui=lib/'ztm_gui.py'; runtime=lib/'ztm_surgical_runtime.py'

def one(path,old,new,label):
    s=path.read_text()
    if s.count(old)!=1:raise SystemExit(f'STOP {label}: expected exactly one anchor, observed {s.count(old)}')
    path.write_text(s.replace(old,new))

# Deterministic candidates and hardware inventory, no RNG.
r=runtime.read_text()
r=r.replace('import random\n','')
r=r.replace('    cache3 = 0\n', '    cache3 = 0\n    cache2 = 0\n')
r=r.replace("                elif value.endswith('K'): cache3=max(cache3,int(value[:-1])*1024)\n", "                elif value.endswith('K'): cache3=max(cache3,int(value[:-1])*1024)\n")
# Both L2 and L3 assessed from cache hierarchy with shared masks available.
needle='''        except (OSError,ValueError): pass
    mem=_memory_kb()
    return {'cpu_model':model,'''
assert r.count(needle)==1
r=r.replace(needle,'''            if (index/'level').read_text().strip() == '2' and (index/'type').read_text().strip() in ('Unified','Data'):
                value=(index/'size').read_text().strip().upper()
                multiplier = 1024*1024 if value.endswith('M') else 1024 if value.endswith('K') else 1
                cache2=max(cache2,int(value.rstrip('KM'))*multiplier)
        except (OSError,ValueError): pass
    # EDAC exposes memory technology on some kernels; absence is not evidence of DDR type.
    types = set()
    for dimm in Path('/sys/devices/system/edac/mc').glob('mc*/dimm*/dimm_mem_type'):
        try:
            kind=dimm.read_text().strip().upper()
            if kind not in ('','UNKNOWN','N/A','UNDEFINED','EMPTY','0'):
                types.add(kind)
        except OSError: pass
    memory_type=','.join(sorted(types)) if types else 'unknown'
    mem=_memory_kb()
    return {'cpu_model':model,''')
r=r.replace("            'l3_cache_bytes':cache3,'memory_total_kb':mem.get('MemTotal',0),", "            'l2_cache_bytes':cache2,'l3_cache_bytes':cache3, 'memory_type':memory_type,\n            'memory_total_kb':mem.get('MemTotal',0),")
i=r.index('def candidate_profiles(')
j=r.index('\ndef recognized_miners(', i)
r=r[:i]+'''def _cache_based_limit(inventory):
    logical=max(1,int(inventory['logical_cpus']))
    l3=max(0,int(inventory.get('l3_cache_bytes') or 0))
    l2=max(0,int(inventory.get('l2_cache_bytes') or 0))
    physical=max(1,min(logical,int(inventory.get('physical_cores') or logical)))
    # RandomX typically benefits from ~2 MiB L3 per concurrently active dataset user.
    cache_slots=l3//(2*1024*1024) if l3 else physical
    technology=str(inventory.get('memory_type','unknown')).upper()
    if any(old in technology for old in ('DDR2','DDR3')):
        # Conservative cap for older memory buses; measured hashrate still selects winner.
        cache_slots=min(cache_slots,physical)
    if not l3 and l2:
        cache_slots=min(cache_slots,max(1,l2//(256*1024)))
    available_kb=max(0,int(inventory.get('memory_available_kb') or 0))
    # ~2 GiB dataset + 1 GiB operating-headroom; do not guess DDR latency.
    if available_kb and available_kb < 3*1024*1024:
        cache_slots=min(cache_slots,physical)
    return max(1,min(logical,cache_slots))


def candidate_profiles(inventory, auto_threads, max_profiles=11, seed=None):
    """Hardware-ranked unique alternatives; baseline XMRig automatic is counted separately.

    Memory technology is recorded when observable; there is no validated universal
    DDR-generation-to-hashrate multiplier, so no fabricated DDR weighting is used.
    """
    logical=max(1,int(inventory['logical_cpus']))
    phys=max(1,min(logical,int(inventory.get('physical_cores') or logical)))
    cap=_cache_based_limit(inventory)
    auto=max(1,min(logical,int(auto_threads or cap)))
    # Rank by proximity to cache + physical-core sweet spot, then steady ascending.
    def rank(threads):
        return (abs(threads-cap), int(threads>phys), abs(threads-phys), threads)
    ordered=sorted((n for n in range(1,logical+1) if n!=auto),key=rank)
    return ordered[:max(0,min(11,int(max_profiles))-1)]


def choose_init_threads(inventory, auto_threads, seed=None):
    """Single deterministic dataset initialization per miner run."""
    logical=max(1,int(inventory['logical_cpus']))
    physical=max(1,min(logical,int(inventory.get('physical_cores') or logical)))
    # Dataset init can use physical cores without overcommitting SMT.
    return physical

''' + r[j:]
runtime.write_text(r)

one(engine,'import secrets\n','', 'remove RNG import')
one(engine,'    profile_seed = secrets.randbits(64)\n    randomx_init = choose_init_threads(inventory, None, seed=profile_seed)',
    '    randomx_init = choose_init_threads(inventory, None)', 'deterministic initialization')
one(engine,'                    alternates = candidate_profiles(inventory, auto_threads, max_profiles, seed=profile_seed)',
    '                    alternates = candidate_profiles(inventory, auto_threads, max_profiles)', 'ranked candidates')
one(engine,"                    print(f'[ZTM optimizer] Randomized candidate order: {alternates}', flush=True)",
    "                    print(f'[ZTM optimizer] Hardware-ranked candidate order: {alternates}', flush=True)", 'log deterministic')
one(engine,'"cpu_inventory": inventory, "optimizer_random_seed": profile_seed,',
    '"cpu_inventory": inventory, "profile_strategy": "deterministic_hardware_ranked",', 'report strategy')
# RC2 already corrected the candidate_profiles local-variable collision.
if '    candidate_profiles = [\n        p for p in profiles' in engine.read_text():
    one(engine,'    candidate_profiles = [\n        p for p in profiles',
        '    tested_candidate_profiles = [\n        p for p in profiles', 'legacy shadow regression')
    one(engine,"(p for p in candidate_profiles if p.get('threads_observed') == selected_threads)",
        "(p for p in tested_candidate_profiles if p.get('threads_observed') == selected_threads)", 'legacy shadow ref')
assert '    tested_candidate_profiles = [' in engine.read_text()

start=engine.read_text();i=start.index('def _profile_limits(');j=start.index('def _profile_stats(',i)
start=start[:i]+'''PROFILE_SECONDS = 900
MAX_PROFILE_COUNT = 7  # baseline plus up to six distinct hardware-ranked alternatives
TRANSITION_SECONDS = 5.0


def _profile_limits(duration_s: int) -> tuple[int,int]:
    """Fifteen measured minutes per candidate, no shortened search."""
    if duration_s < PROFILE_SECONDS:
        return 1, duration_s
    # Leave enough time for a baseline + future winner and transitions.
    return MAX_PROFILE_COUNT, PROFILE_SECONDS


def verify_transition(stop_guard, verify_absent, delay=TRANSITION_SECONDS, sleep=time.sleep):
    """Fail closed: require prior guardian exit and two clean miner scans around gap."""
    if not stop_guard():
        raise BenchError('Previous XMRig guardian has not confirmed shutdown')
    if not verify_absent():
        raise BenchError('Competing XMRig remains after profile stop')
    sleep(delay)
    if not verify_absent():
        raise BenchError('Competing XMRig restarted during five-second profile gap')
    return True


''' +start[j:]
engine.write_text(start)
# Remaining engine lifecycle modified separately below with exact landmarks.

# GUI: add compact live profile readout beside existing hashrate.
one(gui,"        self.rate = tk.StringVar(value='— H/s')\n",
"        self.rate = tk.StringVar(value='— H/s')\n        self.profile_live = tk.StringVar(value='Profile — | Active — | Init — | — / 15:00')\n",'GUI live model')
one(gui,"        tk.Label(setup, textvariable=self.shares, bg=PANEL, fg=MUTED, font=self.scaled_font('DejaVu Sans', 9)).pack(anchor='e')",
"        tk.Label(setup, textvariable=self.profile_live, bg=PANEL, fg=CYAN, font=self.scaled_font('DejaVu Sans', 9, 'bold')).pack(anchor='e')\n        tk.Label(setup, textvariable=self.shares, bg=PANEL, fg=MUTED, font=self.scaled_font('DejaVu Sans', 9)).pack(anchor='e')", 'live readout position')
one(gui,'        if self.current_wallet:\n            line = line.replace(self.current_wallet, \'[PUBLIC_WALLET]\')\n',
'''        if line.startswith('[ZTM_PROFILE] '):
            try:
                info=json.loads(line[len('[ZTM_PROFILE] '):])
                elapsed=max(0,int(info.get('elapsed',0)))
                target=max(1,int(info.get('target',900)))
                fmt=lambda n:f'{n//60:02d}:{n%60:02d}'
                self.profile_live.set(
                    f"Profile {info.get('index','—')}/{info.get('total','—')} | "
                    f"Active {info.get('active','—')} | Init {info.get('init','—')} | "
                    f"{fmt(elapsed)} / {fmt(target)}")
            except (ValueError,TypeError,KeyError):
                pass
            return
        if self.current_wallet:
            line = line.replace(self.current_wallet, '[PUBLIC_WALLET]')
''', 'GUI structured progress parser')
one(gui,"        self.busy_start('2 · Online CPU benchmark running')\n",
    "        self.busy_start('2 · Online CPU benchmark running')\n        self.profile_live.set('Profile starting | Active — | Init — | 00:00 / 05:00')\n", 'live reset')
one(gui,"        self.busy = False\n        self.process = None\n        self.current_wallet = None\n",
    "        self.busy = False\n        self.process = None\n        self.current_wallet = None\n        # Keep the last tested profile visible after completion.\n",'retention')
control=root/'DEBIAN/control'
one(control,'Version: 1.2.2~srp1v2rc2','Version: 1.2.3~srp1v2rc3','RC3 version')
assert (lib/'ztm_startup_preflight.py').exists(), 'RC2 startup preflight must remain present'
assert 'ztm_startup_preflight.py' in (root/'usr/bin/ztm').read_text(), 'RC2 launcher preflight must remain present'
print('RC3 hardware candidate ranking, GUI status, prior RC2 protections and version applied')
