#!/usr/bin/env python3
"""Second surgical stage: verified XMRig process shutdown and 5s transition."""
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text()

def one(old,new,name):
 global s
 n=s.count(old)
 if n!=1:raise SystemExit(f'STOP {name}: expected 1 anchor, got {n}')
 s=s.replace(old,new)

one('"actual_threads": None, "thread_generation": 0,',
    '"actual_threads": None, "ready_threads": None, "thread_generation": 0,',
    'readiness state')
start=s.index('            # Elevate only the verified miner.')
end=s.index('            def wait_until(target_time: float) -> bool:',start)
s=s[:start]+'''            # A distinct supervised XMRig process is used for each tested profile.
            # Unlike live config reload, its old Linux workers can be verified stopped
            # before beginning the next candidate. Polkit broker ownership is preserved.
            from ztm_root_guard import process_identity
            controller_id = process_identity(os.getpid())
            if controller_id is None:
                raise BenchError('Unable to verify local controller identity')
            stop_flag = Path(tempdir) / 'stop.request'
            guard_args = [str(executable), str(cfg_path), str(stop_flag),
                          str(os.getpid()), str(controller_id[1])]
            if os.environ.get('ZTM_SESSION_SOCKET'):
                command = [sys.executable, '-u',
                           str(Path(__file__).with_name('ztm_privilege_client.py')),
                           'miner', *guard_args]
            else:
                command = ["pkexec", "/usr/bin/python3",
                           str(Path(__file__).with_name('ztm_root_guard.py')),
                           "--xmrig", str(executable), "--config", str(cfg_path),
                           "--stop-flag", str(stop_flag),
                           "--owner-pid", str(os.getpid()),
                           "--owner-start", str(controller_id[1])]
            reader = None

            def collect(child):
                assert child.stdout is not None
                last_acc = last_rej = 0
                with logfile.open('a', encoding='utf-8') as log:
                    for original in child.stdout:
                        line = original.replace(wallet, '[PUBLIC_WALLET]')
                        log.write(line)
                        clean = re.sub(r"\\x1b\\[[0-9;]*m", "", line).strip()
                        value = speed_hs(clean)
                        match = SHARE.search(clean)
                        reject = REJECTED.search(clean)
                        profile = THREAD_PROFILE.search(clean)
                        ready = THREAD_READY.search(clean)
                        with lock:
                            state['lines'] += 1
                            if value is not None:
                                collected.append(value)
                            if match:
                                a, r = int(match.group(1)), int(match.group(2))
                                if a >= last_acc: state['accepted'] += a - last_acc
                                if r >= last_rej: state['rejected'] += r - last_rej
                                last_acc, last_rej = a, r
                            if reject:
                                a, r = int(reject.group(1)), int(reject.group(2))
                                if a >= last_acc: state['accepted'] += a - last_acc
                                if r >= last_rej: state['rejected'] += r - last_rej
                                last_acc, last_rej = a, r
                            actual = (int(ready.group(1)) if ready else
                                      int(profile.group(1)) if profile else None)
                            if actual is not None and state['actual_threads'] != actual:
                                state['actual_threads'] = actual
                                state['thread_generation'] += 1
                            if ready and int(ready.group(1)) == int(ready.group(2)):
                                state['ready_threads'] = int(ready.group(1))
                            if 'huge pages' in clean.lower() and ('100%' in clean or 'enabled' in clean.lower()):
                                state['hugepages_xmrig_confirmed'] = True
                            if 'msr' in clean.lower() and ('success' in clean.lower() or 'register values' in clean.lower()):
                                state['msr_xmrig_confirmed'] = True
                            if 'new job from' in clean.lower() or 'use pool' in clean.lower():
                                state['connected'] = True
                            acc_total = state['accepted']; rej_total = state['rejected']
                        print('[XMRig] ' + clean, flush=True)
                        if value is not None:
                            print(f'  Measured XMRig speed: {value:,.1f} H/s', flush=True)
                        elif match or reject:
                            print(f'  Pool shares — accepted: {acc_total} | rejected: {rej_total}', flush=True)

            def launch_profile(active_threads: int | None):
                nonlocal proc, reader
                if proc is not None and proc.poll() is None:
                    raise BenchError('Refusing new profile while prior miner guardian is active')
                if active_threads is not None:
                    _write_profile_config(cfg_path, cfg, active_threads)
                else:
                    cfg['cpu'].pop('rx', None)
                    cfg_path.write_text(json.dumps(cfg),encoding='utf-8')
                    cfg_path.chmod(0o600)
                stop_flag.unlink(missing_ok=True)
                with lock:
                    state['actual_threads']=None
                    state['ready_threads']=None
                print(f'[ZTM optimizer] Launching supervised XMRig: active={active_threads or "auto"}, init={randomx_init}',flush=True)
                proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                      encoding='utf-8',text=True,errors='replace',bufsize=1,
                                      start_new_session=True)
                reader=threading.Thread(target=collect,args=(proc,),daemon=True)
                reader.start()
                # READY is an XMRig acknowledgement that the newly created CPU
                # worker set is active. A request/config write is not proof.
                ready_deadline=min(deadline,time.monotonic()+180)
                while time.monotonic()<ready_deadline:
                    if proc.poll() is not None:
                        raise BenchError(f'XMRig exited before thread READY (guardian {proc.returncode})')
                    with lock: acknowledged=state['ready_threads']
                    if acknowledged and (active_threads is None or acknowledged==active_threads):
                        print(f'[ZTM optimizer] READY confirmed: {acknowledged} active threads',flush=True)
                        return acknowledged
                    time.sleep(0.2)
                raise BenchError('XMRig did not confirm requested READY threads; refusing measurement')

            def stop_profile_guard():
                nonlocal proc, reader
                if proc is None: return True
                stop_flag.touch(mode=0o600,exist_ok=True)
                try: proc.wait(timeout=25)
                except subprocess.TimeoutExpired:
                    raise BenchError('Prior privileged XMRig guardian failed to exit within 25 seconds')
                if reader is not None:
                    reader.join(timeout=8)
                    if reader.is_alive():
                        raise BenchError('Previous XMRig log reader failed to finish')
                if proc.stdout is not None: proc.stdout.close()
                if proc.returncode != 0:
                    raise BenchError(f'Prior XMRig guardian terminated abnormally: {proc.returncode}')
                proc=None
                reader=None
                print('[ZTM optimizer] Previous XMRig guardian exit confirmed',flush=True)
                return True

            def verify_no_miner():
                if os.environ.get('ZTM_SESSION_SOCKET'):
                    cmd=[sys.executable,str(Path(__file__).with_name('ztm_privilege_client.py')),'cleanup-miners']
                else:
                    cmd=['pkexec','/usr/bin/python3',str(Path(__file__).with_name('ztm_startup_preflight.py'))]
                result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                      text=True,timeout=30,check=False)
                if result.stdout: print(result.stdout.strip(),flush=True)
                return result.returncode==0

            def transition_to(next_threads: int):
                # Five FULL seconds after verified shutdown. The second privileged
                # scan detects service respawns before allowing another profile.
                verify_transition(stop_profile_guard,verify_no_miner)
                launch_profile(next_threads)

''' +s[end:]
start=s.index('            def measure_profile(')
end=s.index('            try:\n                max_profiles',start)
s=s[:start]+'''            def measure_profile(label: str, requested_threads: int | None, seconds: float,
                                index: int, total: int) -> dict | None:
                # XMRig READY is verified by launch_profile before measurement.
                # Warm up outside the FIVE measured minutes, allowing thermal / pool ramp.
                warmup=min(25, max(0, seconds / 5))
                if warmup and not wait_until(time.monotonic()+warmup):
                    return None
                sample_start, acc_start, rej_start, actual_start, gen_start = snapshot()
                segment_start = time.monotonic()
                last_notice = -1
                while True:
                    now=time.monotonic()
                    elapsed=int(max(0,now-segment_start))
                    tick=elapsed//5
                    if tick!=last_notice:
                        last_notice=tick
                        with lock: observed=state['ready_threads'] or state['actual_threads']
                        notice={'phase':label,'index':index,'total':total,
                                'active':observed or requested_threads or 'auto',
                                'init':randomx_init,'elapsed':min(elapsed,int(seconds)),
                                'target':int(seconds)}
                        print('[ZTM_PROFILE] '+json.dumps(notice,separators=(',',':')),flush=True)
                    if now>=segment_start+seconds or now>=deadline or proc.poll() is not None:
                        break
                    time.sleep(min(.25,max(.01,segment_start+seconds-now)))
                if proc.poll() is not None and time.monotonic() < segment_start+seconds:
                    raise BenchError(f'XMRig stopped early during measured {label} profile')
                sample_end,acc_end,rej_end,actual_end,gen_end=snapshot()
                with lock: samples=collected[sample_start:sample_end]
                stats=_profile_stats(samples,max(0,acc_end-acc_start),max(0,rej_end-rej_start))
                stats.update({'label':label,
                    'threads_requested':requested_threads if requested_threads is not None else 'auto',
                    'threads_observed':actual_end or actual_start,
                    'seconds':round(time.monotonic()-segment_start,1),
                    'reload_generation':gen_end-gen_start,
                    'candidate_position':index,'candidate_count':total,
                    'transition_seconds':TRANSITION_SECONDS,
                    'measurement_target_seconds':int(seconds)})
                profiles.append(stats)
                print(f"[ZTM optimizer] Profile {label}: {stats['threads_observed']} threads, "
                      f"measured {stats['seconds']:.0f}/{seconds:.0f}s, median {stats['median_hs']} H/s, "
                      f"accepted {stats['accepted_shares']} rejected {stats['rejected_shares']} "
                      f"score {stats['score']}",flush=True)
                return stats

''' +s[end:]
start=s.index('            try:\n                max_profiles')
end=s.index('            except KeyboardInterrupt:',start)
s=s[:start]+'''            try:
                max_profiles, profile_seconds=_profile_limits(duration_s)
                if threads is not None or max_profiles==1:
                    launch_profile(threads)
                    remaining=max(.1,deadline-time.monotonic())
                    measure_profile('fixed' if threads is not None else 'auto-connectivity',
                                    threads,remaining,1,1)
                    selected_threads=threads or snapshot()[3]
                else:
                    print(f'[ZTM optimizer] Hardware inventory: {inventory}',flush=True)
                    # One automatic baseline, at most ten deterministic alternatives.
                    baseline_threads=launch_profile(None)
                    alternates=candidate_profiles(inventory,baseline_threads,max_profiles)
                    total=1+len(alternates)
                    print(f'[ZTM optimizer] Baseline {baseline_threads} + hardware-ranked alternatives {alternates}',flush=True)
                    baseline=measure_profile('xmrig-auto-baseline',None,profile_seconds,1,total)
                    if baseline is None or not baseline.get('median_hs'):
                        raise BenchError('Baseline produced insufficient steady hashrate samples')
                    for index,candidate in enumerate(alternates,start=2):
                        # We reserve 300 s for each profile, plus handshake/warmup.
                        if time.monotonic()+profile_seconds+TRANSITION_SECONDS>=deadline:
                            break
                        print(f'[ZTM optimizer] Stopping previous profile; next candidate {index}/{total} uses {candidate} threads',flush=True)
                        transition_to(candidate)
                        measurement=measure_profile(f'threads-{candidate}',candidate,profile_seconds,index,total)
                        if measurement is None or measurement.get('threads_observed') != candidate:
                            raise BenchError(f'Profile {candidate} failed verified thread measurement')
                    valid=[p for p in profiles if p.get('median_hs') and p.get('threads_observed')]
                    if not valid: raise BenchError('No valid measured thread profiles')
                    winner=max(valid,key=lambda p:(p['score'],p['median_hs'],-(p.get('stability_cv') or 1)))
                    selected_threads=int(winner['threads_observed'])
                    print(f'[ZTM optimizer] Winner {selected_threads} threads, median {winner["median_hs"]} H/s',flush=True)
                    if time.monotonic()+TRANSITION_SECONDS<deadline:
                        transition_to(selected_threads)
                        remaining=max(.1,deadline-time.monotonic())
                        measure_profile('winner-sustained',selected_threads,remaining,total,total)
                    else:
                        wait_until(deadline)
''' +s[end:]
start=s.index('            finally:\n                if time.monotonic() >= deadline')
end=s.index('    except (OSError, subprocess.SubprocessError)',start)
s=s[:start]+'''            finally:
                if time.monotonic() >= deadline and not interrupted.is_set():
                    reached_deadline=True
                if proc is not None:
                    stop_profile_guard()  # Verified shutdown even on cancellation.
''' +s[end:]
s=s.replace('"optimizer_profiles": profiles,', '"optimizer_profiles": profiles,\n        "optimizer_max_profiles": MAX_PROFILE_COUNT,\n        "per_profile_measurement_seconds": PROFILE_SECONDS,\n        "verified_profile_transition_seconds": TRANSITION_SECONDS,')
p.write_text(s)
print('Applied separate-guardian, 5s verified transition lifecycle')
