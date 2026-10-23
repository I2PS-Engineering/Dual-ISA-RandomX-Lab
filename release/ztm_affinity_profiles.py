"""Deterministic RandomX CPU-affinity planner for ZTM V2.

XMRig's cpu.rx short array assigns ONE mining worker to each listed OS CPU ID.
Dataset initialization threads are independent and are not treated as a
steady-state throughput dimension. CPU sets are taken from the *allowed*
Linux affinity mask, not guessed from os.cpu_count().

No private identifiers are collected and no host tuning is performed here.
"""
from __future__ import annotations
import itertools
import os
from pathlib import Path


class ProfilePlanError(RuntimeError):
    pass


def parse_cpu_list(raw):
    """Parse Linux cpulist syntax: '0-3,8,10-11'."""
    output=set()
    for part in str(raw or '').strip().split(','):
        part=part.strip()
        if not part:
            continue
        try:
            if '-' in part:
                a,b=(int(x.strip()) for x in part.split('-',1))
                if a<0 or b<a or b-a>65536:
                    raise ValueError('invalid CPU range')
                output.update(range(a,b+1))
            else:
                cpu=int(part)
                if cpu<0:
                    raise ValueError('negative CPU ID')
                output.add(cpu)
        except (ValueError,TypeError) as exc:
            raise ProfilePlanError('Invalid sysfs CPU list: '+repr(raw)) from exc
    return sorted(output)


def allowed_cpu_ids():
    try:
        return sorted(int(x) for x in os.sched_getaffinity(0))
    except (AttributeError,OSError):
        return list(range(max(1,os.cpu_count() or 1)))


def sysfs_topology(allowed=None):
    """Read Linux shared-thread and cache/NUMA domains, restricted to usable IDs."""
    cpus=allowed_cpu_ids() if allowed is None else sorted(set(int(x) for x in allowed))
    permitted=set(cpus)
    core_groups=set()
    for cpu in cpus:
        p=Path(f'/sys/devices/system/cpu/cpu{cpu}/topology/thread_siblings_list')
        try:
            group=tuple(x for x in parse_cpu_list(p.read_text()) if x in permitted)
        except (OSError,ProfilePlanError):
            group=(cpu,)
        if group:
            core_groups.add(group)
    # In containerized / heterogeneous systems, every permitted CPU must
    # belong to at least one grouping.
    grouped=set(x for g in core_groups for x in g)
    core_groups.update((x,) for x in cpus if x not in grouped)
    l3=[]
    l2=[]
    seen=set()
    for cpu in cpus:
        for entry in Path(f'/sys/devices/system/cpu/cpu{cpu}/cache').glob('index*'):
            try:
                level=int((entry/'level').read_text().strip())
                kind=(entry/'type').read_text().strip()
                if level not in (2,3) or kind not in ('Data','Unified'):
                    continue
                shared=tuple(x for x in parse_cpu_list((entry/'shared_cpu_list').read_text()) if x in permitted)
                raw=(entry/'size').read_text().strip().upper()
                factor=1024*1024 if raw.endswith('M') else 1024 if raw.endswith('K') else 1
                size=int(raw[:-1] if factor>1 else raw)*factor
                key=(level,shared)
                if shared and key not in seen:
                    seen.add(key)
                    (l3 if level==3 else l2).append({'cpu_ids':list(shared),'size_bytes':size})
            except (OSError,ValueError,ProfilePlanError):
                continue
    numa=[]
    for node in Path('/sys/devices/system/node').glob('node[0-9]*'):
        try:
            group=sorted(permitted.intersection(parse_cpu_list((node/'cpulist').read_text())))
            if group:
                numa.append(group)
        except (OSError,ProfilePlanError):
            continue
    return {'allowed_cpu_ids':cpus,'core_groups':[list(g) for g in sorted(core_groups)],
            'l2_domains':l2,'l3_domains':l3,'numa_cpu_groups':numa}


def _groups(inventory, allowed):
    permitted=set(allowed)
    raw=inventory.get('core_groups') or []
    groups=[]
    used=set()
    for entry in raw:
        group=tuple(sorted(permitted.intersection(int(x) for x in entry)))
        group=tuple(x for x in group if x not in used)
        if group:
            groups.append(group)
            used.update(group)
    groups.extend((x,) for x in allowed if x not in used)
    return groups


def _orders(allowed, groups, inventory):
    # Physical-core-first spreads workers across actual physical cores
    # before assigning additional SMT siblings.
    ordered_groups=sorted(groups,key=lambda g:(g[0],len(g)))
    physical=[]
    for layer in range(max(len(g) for g in ordered_groups)):
        physical.extend(g[layer] for g in ordered_groups if len(g)>layer)
    sibling=[x for g in ordered_groups for x in g]
    domains=inventory.get('l3_domains') or []
    local=[]
    for d in sorted(domains,key=lambda d:(-int(d.get('size_bytes',0)),min(d['cpu_ids']))):
        local.extend(x for x in physical if x in set(d['cpu_ids']) and x not in local)
    local.extend(x for x in physical if x not in local)
    numa=inventory.get('numa_cpu_groups') or []
    balanced=[]
    banks=[list(x for x in physical if x in set(group)) for group in numa]
    while any(banks):
        for bank in banks:
            if bank:
                x=bank.pop(0)
                if x not in balanced: balanced.append(x)
    balanced.extend(x for x in physical if x not in balanced)
    variants=[physical,sibling,local,balanced,list(reversed(physical)),list(reversed(sibling))]
    unique=[]
    for sequence in variants:
        seq=tuple(dict.fromkeys(sequence))
        if set(seq)==set(allowed) and seq not in unique:
            unique.append(seq)
    return unique


def _ranking(subset, baseline_threads, groups, inventory):
    chosen=set(subset)
    n=len(chosen)
    logical=len(set(x for g in groups for x in g))
    physical=len(groups)
    smt=sum(max(0,len(chosen.intersection(g))-1) for g in groups)
    l3_penalty=0.0
    for d in inventory.get('l3_domains') or []:
        active=len(chosen.intersection(d.get('cpu_ids',[])))
        if not active: continue
        cap=max(1,int(d.get('size_bytes',0))//(2*1024*1024))
        l3_penalty+=max(0,active-cap)/cap
    if not inventory.get('l3_domains'):
        total=int(inventory.get('l3_cache_bytes',0) or 0)
        cap=max(1,total//(2*1024*1024)) if total else physical
        l3_penalty=max(0,n-cap)/cap
    l2_penalty=0.0
    for d in inventory.get('l2_domains') or []:
        active=len(chosen.intersection(d.get('cpu_ids',[])))
        if not active:continue
        cap=max(1,int(d.get('size_bytes',0))//(256*1024))
        l2_penalty+=max(0,active-cap)/cap
    # Preference only: the REAL hashrate determines the winner.
    penalty=2.0*l3_penalty+0.6*l2_penalty+1.3*smt/max(1,physical)
    penalty+=0.12*abs(n-baseline_threads)/max(1,logical)
    penalty-=0.12*n/max(1,logical)
    return round(penalty,6)


def generate_affinity_profiles(inventory, baseline_threads, max_profiles=7):
    """Return six DISTINCT hardware-ranked CPU-affinity sets for >=3 logical CPUs.

    A fixed seven profiles is mathematically impossible with 1-2 usable CPU
    IDs without pointless duplicate workloads; such systems fail closed.
    """
    allowed=sorted(set(int(x) for x in inventory.get('allowed_cpu_ids',[]) or allowed_cpu_ids()))
    if len(allowed)<3:
        raise ProfilePlanError('Seven distinct RandomX profiles need >=3 permitted logical CPUs; '
                               'refusing to fabricate duplicates')
    if len(allowed)>4096:
        raise ProfilePlanError('CPU topology exceeds supported size')
    if max_profiles!=7:
        raise ProfilePlanError('RC4.1 enforces original baseline + exactly six optimized profiles')
    groups=_groups(inventory,allowed)
    orders=_orders(allowed,groups,inventory)
    # All subsets for small and medium CPUs; bounded seed generation on servers.
    candidates=set()
    ncpu=len(allowed)
    if ncpu<=12:
        for count in range(1,ncpu+1):
            candidates.update(itertools.combinations(allowed,count))
    else:
        counts=sorted(set([1,2,3,4,6,8,ncpu,
                           max(1,int(baseline_threads)),max(1,int(baseline_threads)-1),
                           min(ncpu,int(baseline_threads)+1),
                           max(1,len(groups)),min(ncpu,max(1,len(groups)+2))]))
        for count in counts:
            for sequence in orders:
                candidates.add(tuple(sorted(sequence[:count])))
                if count<ncpu:
                    candidates.add(tuple(sorted(sequence[-count:])))
    ranked=sorted(candidates,key=lambda subset:(
        _ranking(subset,baseline_threads,groups,inventory),
        abs(len(subset)-min(len(groups),baseline_threads)),
        subset))
    if len(ranked)<6:
        raise ProfilePlanError('Cannot create six distinct permitted RandomX CPU mappings')
    # Cover distinct thread-count regimes first, then use alternate placements
    # to compare real cache and SMT effects at the SAME concurrency.
    chosen=[]
    used_counts=set()
    for subset in ranked:
        if len(subset) not in used_counts and len(chosen)<min(4,ncpu):
            chosen.append(subset);used_counts.add(len(subset))
        if len(chosen)==min(4,ncpu): break
    for subset in ranked:
        if len(chosen)==6: break
        if subset not in chosen: chosen.append(subset)
    if len(chosen)!=6 or len(set(chosen))!=6:
        raise ProfilePlanError('Seven-profile plan violated distinctness requirement')
    profiles=[]
    for ix,subset in enumerate(chosen,2):
        profiles.append({
            'label':f'affinity-{ix}',
            'cpu_ids':list(subset),
            'threads':len(subset),
            'rank_penalty':_ranking(subset,baseline_threads,groups,inventory),
            'core_count_used':sum(bool(set(subset).intersection(g)) for g in groups),
            'smt_siblings_used':sum(max(0,len(set(subset).intersection(g))-1) for g in groups)
        })
    return profiles


def set_xmrig_affinity_config(cfg, cpu_ids, allowed=None):
    """Write actual OS CPU IDs into XMRig's documented cpu.rx affinity array."""
    ids=list(cpu_ids)
    if not ids or len(ids)!=len(set(ids)) or not all(isinstance(x,int) and x>=0 for x in ids):
        raise ProfilePlanError('CPU affinity profile contains invalid or duplicate OS CPU IDs')
    permitted=set(allowed_cpu_ids() if allowed is None else allowed)
    if not set(ids).issubset(permitted):
        raise ProfilePlanError('CPU affinity profile references disallowed/offline logical CPU IDs')
    cfg.setdefault('cpu',{})['rx']=ids
    cfg['autosave']=False
    return len(ids)
