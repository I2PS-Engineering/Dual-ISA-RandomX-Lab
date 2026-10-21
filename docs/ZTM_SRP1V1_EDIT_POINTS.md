# ZTM SRP1V1 edit points

## GUI lines 120-225
   120	        return tk.Label(parent, text=text, fg=color, bg=parent['bg'], font=('DejaVu Sans', size, 'bold' if bold else 'normal'), **kw)
   121	
   122	    def view(self):
   123	        style = ttk.Style(self.root)
   124	        style.theme_use('clam')
   125	        style.configure('ZTM.TButton', font=('DejaVu Sans', 10, 'bold'), padding=(13, 10))
   126	        style.configure('ZTM.TEntry', fieldbackground='#142740', foreground=WHITE, insertcolor=WHITE)
   127	        bar = tk.Frame(self.root, bg=PANEL, pady=13, padx=20)
   128	        bar.pack(fill='x')
   129	        logo = APP / 'i2ps-logo.png'
   130	        if logo.is_file():
   131	            self.logo_image = tk.PhotoImage(file=str(logo))
   132	            tk.Label(bar, image=self.logo_image, bg=PANEL).pack(side='left', padx=(0,15))
   133	        self.label(bar, 'ZTM', 23, CYAN, True).pack(side='left')
   134	        self.label(bar, '  ZERO TO MONERO  |  I2PS ENGINEERING', 13, WHITE, True).pack(side='left')
   135	        self.label(bar, '  Linux x86-64 · Engineering Preview', 10, MUTED).pack(side='right')
   136	        navigation = tk.Frame(self.root, bg='#091625', padx=20, pady=7)
   137	        navigation.pack(fill='x')
   138	        self.benchmark_nav = tk.Button(navigation, text='  BENCHMARK  ', command=lambda: self.show_page('benchmark'),
   139	            font=('DejaVu Sans', 10, 'bold'), fg=DARK, bg=CYAN, activebackground='#7fd8ff',
   140	            activeforeground=DARK, relief='flat', cursor='hand2', padx=18, pady=9)
   141	        self.benchmark_nav.pack(side='left')
   142	        self.wallet_nav = tk.Button(navigation, text='  WALLET  ', command=lambda: self.show_page('wallet'),
   143	            font=('DejaVu Sans', 10, 'bold'), fg=MUTED, bg=PANEL, activebackground='#17344c',
   144	            activeforeground=WHITE, relief='flat', cursor='hand2', padx=20, pady=9)
   145	        self.wallet_nav.pack(side='left', padx=(8,0))
   146	        self.mining_nav = tk.Button(navigation, text='  MINING  ', command=lambda: self.show_page('mining'),
   147	            font=('DejaVu Sans', 10, 'bold'), fg='#647489', bg=PANEL,
   148	            activebackground='#17344c', activeforeground=WHITE, relief='flat',
   149	            cursor='hand2', padx=20, pady=9)
   150	        self.mining_nav.pack(side='left', padx=(8,0))
   151	        self.refresh_navigation()
   152	        self.page_host = tk.Frame(self.root, bg=DARK)
   153	        self.page_host.pack(fill='both', expand=True)
   154	        main = tk.Frame(self.page_host, bg=DARK, padx=20, pady=13)
   155	        self.benchmark_page = main
   156	        main.pack(fill='both', expand=True)
   157	        self.label(main, 'ONE INSTALLATION. LIVE TERMINAL. ACTUAL RANDOMX MEASUREMENTS.', 12, CYAN, True).pack(anchor='w', pady=(0, 6))
   158	        self.label(main, 'Preparation runs APT update, installs prerequisites, then downloads verified official XMRig.\nPool and payout are preconfigured; no mining begins without authorization.', 10, MUTED, justify='left').pack(anchor='w')
   159	        tk.Checkbutton(main, text='Also upgrade already-installed Ubuntu packages (apt-get upgrade -y; optional)', variable=self.upgrade_all, bg=DARK, fg=WHITE, activebackground=DARK, activeforeground=WHITE, selectcolor=DARK).pack(anchor='w', pady=(5,0))
   160	        row = tk.Frame(main, bg=DARK)
   161	        row.pack(fill='x', pady=(12, 8))
   162	        self.prepare_btn = ttk.Button(row, text='1   PREPARE LINUX + INSTALL XMRIG', style='ZTM.TButton', command=self.prepare)
   163	        self.prepare_btn.pack(side='left')
   164	        self.stop_btn = ttk.Button(row, text='STOP', style='ZTM.TButton', command=self.stop, state='disabled')
   165	        self.stop_btn.pack(side='left', padx=10)
   166	        self.label(row, '', 10).pack(side='left')
   167	        self.label(row, '', 10).pack(side='left')
   168	        self.label(row, 'CURRENT STEP: ', 9, MUTED).pack(side='left')
   169	        self.label(row, '', 9).pack(side='left')
   170	        tk.Label(row, textvariable=self.state, fg=CYAN, bg=DARK, font=('DejaVu Sans', 10, 'bold')).pack(side='left')
   171	        panels = tk.PanedWindow(main, orient=tk.VERTICAL, sashwidth=5, bg=DARK, bd=0)
   172	        panels.pack(fill='both', expand=True)
   173	        term_frame = tk.Frame(panels, bg=PANEL, padx=10, pady=8)
   174	        self.label(term_frame, 'LIVE TERMINAL OUTPUT  •  APT / SETUP / XMRIG', 10, CYAN, True).pack(anchor='w')
   175	        terminal = tk.Frame(term_frame, bg=PANEL)
   176	        terminal.pack(fill='both', expand=True)
   177	        self.terminal = tk.Text(terminal, wrap='word', font=('DejaVu Sans Mono', 9), bg='#050b12', fg='#baf9de', insertbackground=WHITE, bd=0, state='disabled', relief='flat')
   178	        sc = ttk.Scrollbar(terminal, orient='vertical', command=self.terminal.yview)
   179	        self.terminal.configure(yscrollcommand=sc.set)
   180	        self.terminal.pack(side='left', fill='both', expand=True)
   181	        sc.pack(side='right', fill='y')
   182	        panels.add(term_frame, minsize=130, stretch='always')
   183	        setup = tk.Frame(panels, bg=PANEL, padx=10, pady=8)
   184	        self.label(setup, '2   BENCHMARK SETUP', 11, CYAN, True).pack(anchor='w')
   185	        fields = tk.Frame(setup, bg=PANEL)
   186	        fields.pack(fill='x', pady=7)
   187	        for col in range(4):
   188	            fields.grid_columnconfigure(col, weight=1 if col in (1, 3) else 0)
   189	        # Pool host is managed internally; no visible pool label.
   190	        self.pool_entry = ttk.Entry(fields, textvariable=self.pool, width=24)
   191	        # Pool is an internal benchmark default: keep the original widget ungridded.
   192	        # self.pool_entry.grid(row=0,column=1,sticky='ew',padx=(0,22))
   193	        # Wallet remains independently accessible through the existing Wallet navigation tab.
   194	        tk.Button(fields, text='OPEN WALLET TAB  →', command=lambda: self.show_page('wallet'),
   195	                  bg='#142740', fg=CYAN, activebackground='#1d3b58', activeforeground=WHITE,
   196	                  relief='flat', font=('DejaVu Sans', 9, 'bold'), cursor='hand2', padx=8, pady=6)  # ungridded on benchmark
   197	        self.label(fields, 'DURATION', 9, MUTED).grid(row=1,column=0,sticky='w',pady=5)
   198	        self.duration_menu = ttk.Combobox(fields, textvariable=self.duration, state='readonly', values=[
   199	            '1 minute — connectivity check', '10 minutes — quick diagnostic',
   200	            '30 minutes — quick diagnostic', '60 minutes — longer diagnostic',
   201	            '1440 minutes — 24-hour observation'])
   202	        self.duration_menu.grid(row=1,column=1,sticky='ew',padx=(0,22))
   203	        self.label(fields, 'CPU THREADS', 9, MUTED).grid(row=1,column=2,sticky='w')
   204	        self.thread_entry = ttk.Entry(fields, textvariable=self.threads, state='disabled')
   205	        self.thread_entry.grid(row=1,column=3,sticky='ew')
   206	        # TLS setting is bound internally; it is not user-editable on the benchmark page.
   207	        tk.Checkbutton(setup, text='I authorize real CPU work for the selected duration, including electricity use and heat.', variable=self.confirm_power, bg=PANEL, fg=WHITE, activebackground=PANEL, activeforeground=WHITE, selectcolor=DARK).pack(anchor='w')
   208	        tk.Checkbutton(setup, text='I understand this online benchmark credits pool rewards to the configured Dev Wallet; XMRig may also have an upstream developer contribution.', variable=self.confirm_reward, bg=PANEL, fg=WHITE, activebackground=PANEL, activeforeground=WHITE, selectcolor=DARK, wraplength=990, justify='left').pack(anchor='w')
   209	        self.label(setup, 'Dev Wallet: initial benchmark rewards support I2PS software development. No private keys are requested.', 9, MUTED).pack(anchor='w', pady=(3, 0))
   210	        buttons = tk.Frame(setup, bg=PANEL)
   211	        buttons.pack(fill='x', pady=(8,0))
   212	        self.benchmark_btn = ttk.Button(buttons, text='START REAL RANDOMX BENCHMARK', style='ZTM.TButton', command=self.benchmark, state='disabled')
   213	        self.benchmark_btn.pack(side='left')
   214	        ttk.Button(buttons, text='OPEN RESULTS FOLDER', style='ZTM.TButton', command=self.open_results).pack(side='left', padx=10)
   215	        tk.Label(buttons, textvariable=self.rate, bg=PANEL, fg=CYAN, font=('DejaVu Sans', 13, 'bold')).pack(side='right')
   216	        tk.Label(setup, textvariable=self.shares, bg=PANEL, fg=MUTED, font=('DejaVu Sans', 9)).pack(anchor='e')
   217	        panels.add(setup, minsize=265, stretch='never')
   218	        self.wallet_page = tk.Frame(self.page_host, bg=DARK, padx=25, pady=22)
   219	        self.build_wallet_page()
   220	        self.mining_page = tk.Frame(self.page_host, bg=DARK, padx=25, pady=22)
   221	        panel = self.wallet_panel_in(self.mining_page, 'Personal Mining — HashVault',
   222	            'Use your public Monero wallet address. CPU mining begins only when you select START MINING.')
   223	        self.label(panel, 'Your wallet receives normal mining rewards through HashVault.', 11, WHITE).pack(anchor='w', pady=(2, 12))
   224	        self.label(panel, 'CPU threads: Auto   |   Pool: HashVault', 10, MUTED).pack(anchor='w', pady=(0, 12))
   225	        terms = tk.Frame(panel, bg=PANEL)

## Duration references
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_eligibility.py:1:"""Eligibility for ZTM personal mining: measured, uninterrupted 24h pool-verified benchmark."""
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_eligibility.py:20:                isinstance(report.get('selected_threads'), int) and
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_eligibility.py:21:                report['selected_threads'] > 0 and
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_eligibility.py:28:    """Find one complete 24-hour, pool-verified run; shorter runs cannot be combined.
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:4:This is an engineering diagnostic, not the public v0.4 24-hour Dev Wallet
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:177:THREAD_PROFILE = re.compile(r"use profile\s+rx\s+\((\d+)\s+threads", re.I)
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:178:THREAD_READY = re.compile(r"READY\s+threads\s+(\d+)\s*/\s*(\d+)", re.I)
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:181:def _profile_limits(duration_s: int) -> tuple[int, int]:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:183:    if duration_s < 300:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:184:        return 1, duration_s
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:185:    if duration_s < 900:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:187:    if duration_s < 3600:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:192:def _candidate_threads(logical: int, auto_threads: int | None, max_profiles: int) -> list[int]:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:196:    if auto_threads is None:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:197:        auto_threads = max(1, min(logical, logical // 2 or 1))
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:198:    auto_threads = max(1, min(logical, int(auto_threads)))
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:203:            auto_threads,
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:204:            auto_threads - 1,
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:205:            auto_threads + 1,
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:206:            auto_threads - 2,
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:207:            auto_threads + 2,
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:217:    # The baseline already measured auto_threads, so only return alternate profiles.
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:218:    unique = [n for n in unique if n != auto_threads]
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:248:def _write_profile_config(cfg_path: Path, cfg: dict, threads: int) -> None:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:250:    cpu["rx"] = [-1] * int(threads)
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:257:def run_benchmark(executable: Path, pool: str, wallet: str, tls: bool, duration_s: int,
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:258:                  threads: int | None, output_dir: Path, confirm: bool) -> tuple[dict, int]:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:263:        print(f"Pool: {pool} | TLS: {'enabled' if tls else 'disabled'} | Duration: {duration_s} seconds")
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:277:        "actual_threads": None, "thread_generation": 0,
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:282:    deadline = started + duration_s
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:290:    selected_threads: int | None = threads
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:312:            if threads is not None:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:313:                cfg["cpu"]["rx"] = [-1] * int(threads)
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:381:                                if state["actual_threads"] != actual:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:382:                                    state["actual_threads"] = actual
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:417:                            state["actual_threads"], state["thread_generation"])
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:419:            def measure_profile(label: str, requested_threads: int | None, seconds: int) -> dict | None:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:437:                    "threads_requested": requested_threads if requested_threads is not None else "auto",
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:438:                    "threads_observed": actual_end or actual_start,
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:443:                shown_threads = stats["threads_observed"] or stats["threads_requested"]
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:444:                print(f"\n[ZTM optimizer] Profile {shown_threads} thread(s): median {stats['median_hs']} H/s, "
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:450:                max_profiles, profile_seconds = _profile_limits(duration_s)
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:451:                if threads is not None or max_profiles == 1:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:453:                    # configuration for the full duration without profile switching.
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:454:                    measure_profile("fixed" if threads is not None else "auto-connectivity", threads,
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:456:                    selected_threads = threads or snapshot()[3]
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:460:                    auto_threads = None if baseline is None else baseline.get("threads_observed")
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:462:                    alternates = _candidate_threads(logical, auto_threads, max_profiles)
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:477:                        measure_profile(f"threads-{candidate}", candidate, profile_seconds)
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:479:                    valid = [p for p in profiles if p.get("median_hs") and p.get("threads_observed")]
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:482:                        selected_threads = int(winner["threads_observed"])
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:483:                        print(f"\n[ZTM optimizer] Winner: {selected_threads} active thread(s) "
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:485:                        _write_profile_config(cfg_path, cfg, selected_threads)
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:489:                            measure_profile("winner-sustained", selected_threads, remaining)
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:491:                        selected_threads = auto_threads
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:532:        "threads_requested": threads if threads else "automatic_optimizer",
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:533:        "selected_threads": selected_threads,
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:534:        "requested_seconds": duration_s, "elapsed_seconds": elapsed,
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:542:        "status": status, "actual_24_hour_benchmark": bool(duration_s >= 86400 and elapsed >= 86400 and ran_full_time and online_verified),
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:552:    print(f" Selected threads:    {report['selected_threads']}")
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:554:    print(f" Elapsed:             {elapsed:.1f} seconds / {duration_s} requested")
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:569:    parser.add_argument("--session-stdin", action="store_true", help="Read pool, public wallet, duration and thread setting as JSON from stdin")
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:572:    parser.add_argument("--minutes", type=int, default=10, help="Run duration in whole minutes (default: 10)")
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:574:    parser.add_argument("--threads", type=int, help="Mining CPU threads; default: XMRig chooses")
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:586:        a.threads = int(payload["threads"]) if payload.get("threads") else None
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:591:    if not (1 <= a.minutes <= 1440) or (a.seconds is not None and not 1 <= a.seconds <= 86400):
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:593:    if a.threads is not None and not (1 <= a.threads <= (os.cpu_count() or 1)):
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:594:        raise BenchError("--threads must be between 1 and the detected logical CPU count.")
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:599:        print(f"- Duration: {a.seconds or a.minutes * 60} s | Threads: {a.threads or 'automatic'}")
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_engine.py:615:                            a.seconds or a.minutes * 60, a.threads,
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_mining.py:21:# Public mining address used for initial Dev Wallet benchmark (ownership verification remains operationally required).
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_mining.py:27:def mining_config(address: str, *, donation: bool = False, threads: int | None = None) -> dict:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_mining.py:41:    if threads is not None:
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_mining.py:42:        if not isinstance(threads, int) or not 1 <= threads <= (os.cpu_count() or 1):
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_mining.py:44:        configuration['cpu']['rx'] = [-1] * threads
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_mining.py:64:        raise SystemExit('PERSONAL MINING LOCKED: complete a verified uninterrupted 24-hour benchmark first.')
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_mining.py:66:        raise SystemExit('PERSONAL MINING LOCKED: the 24-hour benchmark belongs to another CPU or system.')
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_mining.py:67:    threads = int(qualified['selected_threads'])
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_mining.py:68:    if not 1 <= threads <= (os.cpu_count() or 1):
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_mining.py:74:        write_config(path, mining_config(address, threads=threads))
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_mining.py:94:        print(f'[ZTM] Using qualified 24-hour benchmark: {threads} active CPU thread(s)', flush=True)
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_mining.py:119:                    write_config(path, mining_config(address, donation=donor, threads=threads))
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:3:Mining requires an explicit 24-hour benchmark gate and Terms acceptance.
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:41:# This diagnostic alpha is not proof of a validated 24h benchmark.
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:62:def benchmark_session(pool, wallet, tls, minutes, threads):
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:67:        raise BenchError('Choose one of the supported durations.')
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:68:    if threads and not (1 <= threads <= (os.cpu_count() or 1)):
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:70:    return {'pool': pool, 'wallet': wallet, 'tls': tls, 'minutes': minutes, 'threads': threads}
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:92:        self.duration = tk.StringVar(value='1440 minutes — 24-hour observation')
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:93:        self.threads = tk.StringVar(value='Auto')
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:135:        self.label(bar, '  Linux x86-64 · Engineering Preview', 10, MUTED).pack(side='right')
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:197:        self.label(fields, 'DURATION', 9, MUTED).grid(row=1,column=0,sticky='w',pady=5)
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:198:        self.duration_menu = ttk.Combobox(fields, textvariable=self.duration, state='readonly', values=[
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:201:            '1440 minutes — 24-hour observation'])
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:202:        self.duration_menu.grid(row=1,column=1,sticky='ew',padx=(0,22))
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:203:        self.label(fields, 'CPU THREADS', 9, MUTED).grid(row=1,column=2,sticky='w')
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:204:        self.thread_entry = ttk.Entry(fields, textvariable=self.threads, state='disabled')
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:207:        tk.Checkbutton(setup, text='I authorize real CPU work for the selected duration, including electricity use and heat.', variable=self.confirm_power, bg=PANEL, fg=WHITE, activebackground=PANEL, activeforeground=WHITE, selectcolor=DARK).pack(anchor='w')
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:208:        tk.Checkbutton(setup, text='I understand this online benchmark credits pool rewards to the configured Dev Wallet; XMRig may also have an upstream developer contribution.', variable=self.confirm_reward, bg=PANEL, fg=WHITE, activebackground=PANEL, activeforeground=WHITE, selectcolor=DARK, wraplength=990, justify='left').pack(anchor='w')
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:209:        self.label(setup, 'Dev Wallet: initial benchmark rewards support I2PS software development. No private keys are requested.', 9, MUTED).pack(anchor='w', pady=(3, 0))
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:224:        self.label(panel, 'CPU threads: Auto   |   Pool: HashVault', 10, MUTED).pack(anchor='w', pady=(0, 12))
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:256:            messagebox.showinfo('24-hour benchmark required',
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:257:                'You must complete the 24-hour benchmark for better mining results before opening Wallet or Mining.')
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:483:        # Bounded display for long 24h sessions
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:628:            minutes = int(self.duration.get().split(' ', 1)[0])
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:629:            threads = None  # CPU threads always Auto for this engineering benchmark
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:630:            session = benchmark_session(BENCHMARK_POOL, BENCHMARK_PAYOUT, BENCHMARK_TLS, minutes, threads)
/tmp/ztm-sr-inspect/root/usr/lib/ztm/ztm_gui.py:637:        text = (f'ZTM will start REAL RandomX CPU mining.\n\nDuration: {minutes} minute(s)\nCPU threads: Auto\n\nPool rewards go to the configured I2PS Dev Wallet.\nMining consumes electricity and creates heat. You can STOP it at any time.\n\nStart now?')
