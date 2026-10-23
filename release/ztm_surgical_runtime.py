"""I2PS ZTM SRP1V2 controlled host inventory and recognized miner preflight.

No hostname, wallet or other private data is exported. Zero shell=True usage.
"""
from __future__ import annotations

import os
import signal
import subprocess
import time
from pathlib import Path

# Exact executable basenames, not broad process substring matches.
MINER_NAMES = frozenset({'xmrig', 'xmrig-amd', 'xmrig-nvidia'})


def _integer(path, default=0):
    try:
        return int(Path(path).read_text().strip())
    except (OSError, ValueError):
        return default


def _memory_kb():
    vals = {}
    try:
        for line in Path('/proc/meminfo').read_text().splitlines():
            name, sep, value = line.partition(':')
            if sep:
                try: vals[name] = int(value.split()[0])
                except (ValueError, IndexError): pass
    except OSError:
        pass
    return vals


def cpu_inventory():
    logical = max(1, os.cpu_count() or 1)
    cpuinfo = Path('/proc/cpuinfo')
    model = 'Unknown'
    pairs = set()
    physical = 0
    try:
        fields = {}
        for group in cpuinfo.read_text(errors='replace').split('\n\n'):
            d = dict((k.strip(),v.strip()) for line in group.splitlines() if ':' in line for k,v in [line.split(':',1)])
            if 'model name' in d and model == 'Unknown': model = d['model name']
            if 'physical id' in d and 'core id' in d: pairs.add((d['physical id'],d['core id']))
            if 'processor' in d: physical += 1
    except OSError:
        pass
    physical = min(logical, _physical_core_groups() or len(pairs) or physical or logical)
    cache3 = 0
    base=Path('/sys/devices/system/cpu/cpu0/cache')
    for index in base.glob('index*'):
        try:
            if (index/'level').read_text().strip() == '3' and (index/'type').read_text().strip() in ('Unified','Data'):
                value=(index/'size').read_text().strip().upper()
                if value.endswith('M'): cache3=max(cache3,int(value[:-1])*1024*1024)
                elif value.endswith('K'): cache3=max(cache3,int(value[:-1])*1024)
        except (OSError,ValueError): pass
    mem=_memory_kb()
    topology = _cache_topology()
    return {'cpu_model':model,'logical_cpus':logical,'physical_cores':physical,
            'cache_topology':topology,'numa_nodes':_numa_nodes(),
            'l3_cache_bytes':cache3,'l2_cache_bytes':max((c['size_bytes'] for c in topology if c['level']==2), default=0),
            'l1_cache_bytes':max((c['size_bytes'] for c in topology if c['level']==1), default=0),
            'memory_type':'unknown','memory_total_kb':mem.get('MemTotal',0),
            'memory_available_kb':mem.get('MemAvailable',0),
            'hugepages_total':mem.get('HugePages_Total',0),
            'hugepages_free':mem.get('HugePages_Free',0),
            'hugepage_size_kb':mem.get('Hugepagesize',2048),
            'msr_device_present':Path('/dev/cpu/0/msr').exists()}


def _cache_topology():
    """Read Linux cache sharing groups; unknown data remains unknown."""
    root = Path('/sys/devices/system/cpu')
    result = []
    seen = set()
    for cpu in sorted(root.glob('cpu[0-9]*'), key=lambda p: int(p.name[3:])):
        for entry in (cpu / 'cache').glob('index*'):
            try:
                level = int((entry / 'level').read_text().strip())
                kind = (entry / 'type').read_text().strip()
                shared = (entry / 'shared_cpu_list').read_text().strip()
                size = (entry / 'size').read_text().strip().upper()
                multiplier = 1024 * 1024 if size.endswith('M') else 1024 if size.endswith('K') else 1
                size_bytes = int(size[:-1] if size.endswith(('M', 'K')) else size) * multiplier
                if kind not in ('Data', 'Unified') or level not in (1, 2, 3):
                    continue
                key = (level, shared, kind)
                if key not in seen:
                    seen.add(key)
                    result.append({'level': level, 'shared_cpu_list': shared, 'size_bytes': size_bytes})
            except (OSError, ValueError):
                continue
    return result


def _physical_core_groups():
    root = Path('/sys/devices/system/cpu')
    groups = set()
    for cpu in root.glob('cpu[0-9]*'):
        try:
            siblings = (cpu / 'topology/thread_siblings_list').read_text().strip()
            if siblings:
                groups.add(siblings)
        except OSError:
            pass
    return len(groups)


def _numa_nodes():
    root = Path('/sys/devices/system/node')
    return len(list(root.glob('node[0-9]*')))


def _ranked_counts(inventory, auto_threads):
    logical = max(1, int(inventory['logical_cpus']))
    physical = max(1, min(logical, int(inventory['physical_cores'])))
    l3 = max(0, int(inventory.get('l3_cache_bytes', 0)))
    cache_cap = max(1, l3 // (2 * 1024 * 1024)) if l3 else physical
    auto = max(1, min(logical, int(auto_threads or min(physical, cache_cap))))
    # Prefer physically independent workers, then cache fit, then SMT
    # expansion. These are PRIOR scores, not measured RandomX performance.
    def score(n):
        smt_penalty = max(0, n - physical) / physical
        cache_penalty = max(0, n - cache_cap) / cache_cap
        distance = abs(n - auto) / logical
        # NUMA/cache topology is recorded for diagnosis; count-only XMRig
        # config cannot guarantee NUMA locality or independent core placement.
        return (2.0 * cache_penalty + 1.4 * smt_penalty
                + 0.25 * distance - 0.10 * min(n, physical) / physical)
    return auto, sorted((n for n in range(1, logical + 1) if n != auto),
                        key=lambda n: (score(n), abs(n - auto), n))


def candidate_profiles(inventory, auto_threads, max_profiles, seed=None):
    """Deterministic hardware-ranked ACTIVE thread counts; baseline excluded.

    init threads are a separate startup setting. Never claim that active
    profile changes test different dataset initialization configurations.
    """
    _, ranked = _ranked_counts(inventory, auto_threads)
    return ranked[:max(0, int(max_profiles) - 1)]


def choose_init_threads(inventory, auto_threads, seed=None):
    """Choose dataset initialization parallelism conservatively and repeatably."""
    logical = max(1, int(inventory['logical_cpus']))
    physical = max(1, min(logical, int(inventory['physical_cores'])))
    return physical


def recognized_miners(uid=None, exclude=()):
    """Only real /proc executable basenames on the owned machine, never generic 'miner'."""
    found=[]
    ignored=set(int(x) for x in exclude)
    for directory in Path('/proc').iterdir():
        if not directory.name.isdecimal(): continue
        pid=int(directory.name)
        if pid in ignored or pid == os.getpid(): continue
        try:
            exe=os.readlink(directory/'exe')
            basename=Path(exe.removesuffix(' (deleted)')).name.lower()
            if basename not in MINER_NAMES: continue
            status=(directory/'status').read_text()
            line=next(x for x in status.splitlines() if x.startswith('Uid:'))
            owner=int(line.split()[1])
            if uid is not None and owner not in (uid,0): continue
            stat=(directory/'stat').read_text()
            start_ticks=stat.rsplit(')',1)[-1].strip().split()[19]
            found.append((pid,start_ticks,owner,basename))
        except (OSError,StopIteration,ValueError,IndexError): continue
    return found


def stop_recognized_miners(uid, emit=print, exclude=(), timeout=4):
    """Root-broker-only operation. Do not signal ambiguous/renamed/unrelated processes."""
    if os.geteuid() != 0: raise PermissionError('Miner cleanup must run inside authorized root broker')
    for attempt in range(3):
        found=recognized_miners(uid,exclude)
        if not found: return True
        for pid,ticks,owner,name in found:
            # Re-check identity immediately before sending any signal (PID reuse).
            current=next((p for p in recognized_miners(uid,exclude) if p[0]==pid and p[1]==ticks),None)
            if not current: continue
            emit(f'[ZTM] Stopping recognized competing {name} process PID {pid} (owner {owner})')
            try: os.kill(pid,signal.SIGTERM)
            except ProcessLookupError: continue
            until=time.monotonic()+timeout
            while time.monotonic()<until:
                if not any(p[0]==pid and p[1]==ticks for p in recognized_miners(uid,exclude)): break
                time.sleep(0.1)
            # Fail closed; do not escalate to SIGKILL without separate authorization.
        time.sleep(0.3)
    remaining=recognized_miners(uid,exclude)
    if remaining: emit(f'[ZTM] STOP: {len(remaining)} recognized miner(s) remain or were restarted')
    return not remaining


def prepare_hugepages(emit=print):
    """Attempt non-persistent RandomX 2 MiB huge pages on sufficiently provisioned Linux.

    Avoid shrinking existing allocations or changing sysctl on small systems.
    """
    mem=_memory_kb(); size=mem.get('Hugepagesize',2048)
    if size != 2048:
        emit('[ZTM] Huge pages: unsupported size; leaving host untouched')
        return True
    existing=mem.get('HugePages_Total',0)
    target=max(existing,1168)
    need=(target-existing)*size
    # Require 1GiB reserve beyond requested huge pages; leave smaller hosts unchanged.
    if mem.get('MemAvailable',0) < need+1024*1024:
        emit('[ZTM] Huge pages: insufficient available RAM, keeping current reservation')
        return True
    if target > existing:
        if os.geteuid()!=0: raise PermissionError('Root broker required')
        result=subprocess.run(['/usr/sbin/sysctl','-w',f'vm.nr_hugepages={target}'],
                              capture_output=True,text=True,timeout=20,check=False)
        if result.returncode: emit('[ZTM] Huge-page allocation failed (nonfatal): '+result.stderr.strip()[:160])
    after=_memory_kb()
    emit(f"[ZTM] Huge pages verified: total={after.get('HugePages_Total',0)} free={after.get('HugePages_Free',0)} size_kB={size}")
    return True
