#!/usr/bin/env python3
"""Apply isolated RC4.1 V2 ONLY affinity hotfix to extracted RC4 Debian.

No V3 files are read or written. The existing RC4 asset stays immutable.
"""
from pathlib import Path
import shutil
import sys

if len(sys.argv)!=2:
    raise SystemExit('usage: patch_rc41.py <unpacked RC4 deb root>')
root=Path(sys.argv[1])
lib=root/'usr/lib/ztm'
engine=lib/'ztm_engine.py'
runtime=lib/'ztm_surgical_runtime.py'
gui=lib/'ztm_gui.py'
control=root/'DEBIAN/control'

def exact(path,old,new,label):
    source=path.read_text()
    hits=source.count(old)
    if hits!=1:
        raise SystemExit(f'SECURITY STOP RC4.1 {label}: expected one anchor, found {hits}')
    path.write_text(source.replace(old,new))

src=Path(__file__).with_name('ztm_affinity_profiles.py')
if not src.exists():
    raise SystemExit('SECURITY STOP: affinity planner not present')
shutil.copy2(src,lib/'ztm_affinity_profiles.py')

# The Linux topology is inspected at runtime; respect process affinity and
# SMT siblings instead of naively treating cpu0's L3 as the whole CPU.
exact(runtime,
    '    topology = _cache_topology()\n    return {',
    '    topology = _cache_topology()\n'
    '    from ztm_affinity_profiles import sysfs_topology\n'
    '    placement = sysfs_topology()\n'
    '    logical = max(1, len(placement["allowed_cpu_ids"]))\n'
    '    physical = max(1, min(logical, len(placement["core_groups"])))\n'
    '    return {',
    'collect allowed topology')
exact(runtime,
    "'cache_topology':topology,'numa_nodes':_numa_nodes(),",
    "'cache_topology':topology,'numa_nodes':_numa_nodes(),**placement,",
    'return topology in inventory')

# Only the public, documented XMRig CPU affinity array is used.
exact(engine,
    '            def launch_profile(active_threads: int | None):',
    '            from ztm_affinity_profiles import generate_affinity_profiles, set_xmrig_affinity_config\n'
    '            def launch_profile(active_threads: int | dict | None):',
    'import seven-profile planner near launch')

exact(engine,
    '''                if active_threads is not None:
                    _write_profile_config(cfg_path, cfg, active_threads)
                else:
                    cfg['cpu'].pop('rx', None)''',
    '''                if isinstance(active_threads, dict):
                    requested_ids = list(active_threads['cpu_ids'])
                    active_threads = set_xmrig_affinity_config(
                        cfg, requested_ids, inventory['allowed_cpu_ids'])
                    cfg_path.write_text(json.dumps(cfg), encoding='utf-8')
                    cfg_path.chmod(0o600)
                    print(f'[ZTM optimizer] Explicit XMRig cpu.rx affinity: {requested_ids}',flush=True)
                elif active_threads is not None:
                    _write_profile_config(cfg_path, cfg, active_threads)
                else:
                    cfg['cpu'].pop('rx', None)''',
    'apply real XMRig CPU affinity')

exact(engine,
    '''                    # One automatic baseline, at most ten deterministic alternatives.
                    baseline_threads=launch_profile(None)
                    alternates=candidate_profiles(inventory,baseline_threads,max_profiles)
                    total=1+len(alternates)
                    print(f'[ZTM optimizer] Baseline {baseline_threads} + hardware-ranked alternatives {alternates}',flush=True)''',
    '''                    # FIXED: exactly one original XMRig baseline and SIX different
                    # explicit affinity layouts for machines with >=3 usable CPUs.
                    baseline_threads=launch_profile(None)
                    alternates=generate_affinity_profiles(inventory,baseline_threads,max_profiles)
                    if len(alternates)!=6 or len({tuple(p['cpu_ids']) for p in alternates})!=6:
                        raise BenchError('RC4.1 requires six unique CPU-affinity alternatives')
                    total=7
                    print(f'[ZTM optimizer] Baseline auto={baseline_threads}; '
                          f'six CPU/cache/SMT ranked affinity profiles={alternates}',flush=True)''',
    'always generate six alternatives')

exact(engine,
    '''                    for index,candidate in enumerate(alternates,start=2):
                        # We reserve 300 s for each profile, plus handshake/warmup.
                        if time.monotonic()+profile_seconds+TRANSITION_SECONDS>=deadline:
                            break
                        print(f'[ZTM optimizer] Stopping previous profile; next candidate {index}/{total} uses {candidate} threads',flush=True)
                        transition_to(candidate)
                        measurement=measure_profile(f'threads-{candidate}',candidate,profile_seconds,index,total)
                        if measurement is None or measurement.get('threads_observed') != candidate:
                            raise BenchError(f'Profile {candidate} failed verified thread measurement')''',
    '''                    for index,candidate in enumerate(alternates,start=2):
                        # Preserve the measured 900s; abort rather than silently
                        # omit a profile from the approved fixed-seven plan.
                        if time.monotonic()+profile_seconds+TRANSITION_SECONDS+30>=deadline:
                            raise BenchError('Insufficient time remaining for all seven full-length profiles')
                        cpu_ids=candidate['cpu_ids']
                        count=candidate['threads']
                        print(f'[ZTM optimizer] Transition {index}/{total}; '
                              f'active={count}, affinity={cpu_ids}, '
                              f'cache/SMT score={candidate["rank_penalty"]}',flush=True)
                        transition_to(candidate)
                        measurement=measure_profile(f'affinity-{index}',count,profile_seconds,index,total)
                        if measurement is None or measurement.get('threads_observed') != count:
                            raise BenchError(f'Profile {index} failed verified thread measurement')
                        measurement['cpu_ids']=list(cpu_ids)
                        measurement['affinity_rank_penalty']=candidate['rank_penalty']
                        measurement['smt_siblings_used']=candidate['smt_siblings_used']''',
    'measure six explicit CPU profiles')

exact(engine,
    '''                    selected_threads=int(winner['threads_observed'])
                    print(f'[ZTM optimizer] Winner {selected_threads} threads, median {winner["median_hs"]} H/s',flush=True)
                    if time.monotonic()+TRANSITION_SECONDS<deadline:
                        transition_to(selected_threads)''',
    '''                    selected_threads=int(winner['threads_observed'])
                    selected_affinity=winner.get('cpu_ids')
                    print(f'[ZTM optimizer] Winner {selected_threads} threads, '
                          f'affinity={selected_affinity or "xmrig-auto"}, '
                          f'median {winner["median_hs"]} H/s',flush=True)
                    if time.monotonic()+TRANSITION_SECONDS<deadline:
                        # Keep winner's tested affinity throughout the sustained
                        # remainder. Do not revert to a count-only configuration.
                        winner_launch=({'cpu_ids':list(selected_affinity)}
                                       if selected_affinity else None)
                        transition_to(winner_launch)''',
    'preserve winner physical CPU affinity')

exact(engine,
    '                    selected_threads=int(winner[\'threads_observed\'])',
    '                    selected_threads=int(winner[\'threads_observed\'])',
    'winner thread count retained') if False else None

exact(control,'Version: 1.2.4~srp1v2rc4','Version: 1.2.5~srp1v2rc41','RC4.1 package version')
assert 'PROFILE_SECONDS = 900' in engine.read_text()
assert 'MAX_PROFILE_COUNT = 7' in engine.read_text()
assert 'TRANSITION_SECONDS = 5.0' in engine.read_text()
assert 'ztm_startup_preflight.py' in (root/'usr/bin/ztm').read_text()
assert (lib/'ztm_root_guard.py').exists()
assert 'confirm_power' in gui.read_text() and 'confirm_reward' in gui.read_text()
print('RC4.1 STAGED: original XMRig auto + six distinct affinity profiles, 900s each')
