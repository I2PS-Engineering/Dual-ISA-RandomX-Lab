#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: build_srp1v1.py <extracted-package-root>")

root = Path(sys.argv[1])
gui = root / "usr/lib/ztm/ztm_gui.py"
engine = root / "usr/lib/ztm/ztm_engine.py"
control = root / "DEBIAN/control"

def replace_exact(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"SECURITY STOP: {label}: expected exactly one match, found {count}")
    return text.replace(old, new)

s = gui.read_text(encoding="utf-8")

s = replace_exact(
    s,
    "        self.root.title('ZTM — Zero to Monero | I2PS Engineering')\n",
    "        self.root.title('ZTM-SRP1V1 — Zero to Monero | I2PS Engineering')\n",
    "GUI title",
)

s = replace_exact(
    s,
    """        self.root.geometry('1090x760')
        self.root.minsize(850, 650)
""",
    """        # Adaptive display sizing for compact high-resolution laptop panels.
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        usable_w = max(850, screen_w - 80)
        usable_h = max(650, screen_h - 100)
        target_w = min(1600, usable_w, max(1090, int(screen_w * 0.86)))
        target_h = min(950, usable_h, max(760, int(screen_h * 0.86)))
        pos_x = max(0, (screen_w - target_w) // 2)
        pos_y = max(0, (screen_h - target_h) // 2)
        self.root.geometry(f'{target_w}x{target_h}+{pos_x}+{pos_y}')
        self.root.minsize(min(1000, usable_w), min(700, usable_h))

        size_ratio = min(target_w / 1090.0, target_h / 760.0)
        ui_scale = max(1.0, min(1.30, size_ratio))
        try:
            current_tk_scale = float(self.root.tk.call('tk', 'scaling'))
            self.root.tk.call('tk', 'scaling', current_tk_scale * ui_scale)
        except (tk.TclError, TypeError, ValueError):
            pass
""",
    "adaptive GUI geometry",
)

s = replace_exact(
    s,
    "        self.duration = tk.StringVar(value='1440 minutes — 24-hour observation')\n",
    "",
    "duration variable removal",
)

s = replace_exact(
    s,
    "        self.label(bar, '  Linux x86-64 · Engineering Preview', 10, MUTED).pack(side='right')\n",
    """        release_box = tk.Frame(bar, bg=PANEL)
        release_box.pack(side='right')
        self.label(release_box, 'Linux x86-64 · Stable Release V1.1', 10, MUTED, True).pack(anchor='e')
        self.label(release_box, 'CPU Threads: Auto', 9, CYAN, True).pack(anchor='e')
""",
    "stable release header",
)

s = replace_exact(
    s,
    """def benchmark_session(pool, wallet, tls, minutes, threads):
    from ztm_engine import validate_pool, validate_address, BenchError
    pool = validate_pool(pool)
    wallet = validate_address(wallet)
    if minutes not in (1, 10, 30, 60, 1440):
        raise BenchError('Choose one of the supported durations.')
    if threads and not (1 <= threads <= (os.cpu_count() or 1)):
        raise BenchError('Thread count exceeds detected CPU count.')
    return {'pool': pool, 'wallet': wallet, 'tls': tls, 'minutes': minutes, 'threads': threads}
""",
    """def benchmark_session(pool, wallet, tls, minutes, threads):
    from ztm_engine import validate_pool, validate_address, BenchError
    pool = validate_pool(pool)
    wallet = validate_address(wallet)
    if minutes != 1440:
        raise BenchError('Stable Release V1.1 requires one uninterrupted 24-hour benchmark.')
    if threads is not None:
        raise BenchError('Stable Release V1.1 uses CPU Threads: Auto.')
    return {'pool': pool, 'wallet': wallet, 'tls': tls, 'minutes': 1440, 'threads': None}
""",
    "GUI benchmark-session lock",
)

start_marker = "        self.label(setup, '2   BENCHMARK SETUP', 11, CYAN, True).pack(anchor='w')\n"
end_marker = "        panels.add(setup, minsize=265, stretch='never')\n"
start = s.find(start_marker)
end = s.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit("SECURITY STOP: benchmark setup block not found")
end += len(end_marker)

setup = """        self.label(setup, '2   BENCHMARK SETUP', 11, CYAN, True).pack(anchor='w')
        self.label(setup, '24-HOUR BENCHMARK', 10, WHITE, True).pack(anchor='w', pady=(7, 5))
        tk.Checkbutton(setup, text='I authorize real CPU work for 24 hours, including electricity use and heat.', variable=self.confirm_power, bg=PANEL, fg=WHITE, activebackground=PANEL, activeforeground=WHITE, selectcolor=DARK).pack(anchor='w')
        tk.Checkbutton(setup, text='I understand this online benchmark uses both XMRig and I2PS dev contribution.', variable=self.confirm_reward, bg=PANEL, fg=WHITE, activebackground=PANEL, activeforeground=WHITE, selectcolor=DARK, wraplength=990, justify='left').pack(anchor='w')
        buttons = tk.Frame(setup, bg=PANEL)
        buttons.pack(fill='x', pady=(8,0))
        self.benchmark_btn = ttk.Button(buttons, text='START 24-HOUR RANDOMX BENCHMARK', style='ZTM.TButton', command=self.benchmark, state='disabled')
        self.benchmark_btn.pack(side='left')
        ttk.Button(buttons, text='OPEN RESULTS FOLDER', style='ZTM.TButton', command=self.open_results).pack(side='left', padx=10)
        tk.Label(buttons, textvariable=self.rate, bg=PANEL, fg=CYAN, font=('DejaVu Sans', 13, 'bold')).pack(side='right')
        tk.Label(setup, textvariable=self.shares, bg=PANEL, fg=MUTED, font=('DejaVu Sans', 9)).pack(anchor='e')
        panels.add(setup, minsize=245, stretch='never')
"""
s = s[:start] + setup + s[end:]

s = replace_exact(
    s,
    """            minutes = int(self.duration.get().split(' ', 1)[0])
            threads = None  # CPU threads always Auto for this engineering benchmark
            session = benchmark_session(BENCHMARK_POOL, BENCHMARK_PAYOUT, BENCHMARK_TLS, minutes, threads)
""",
    """            minutes = 1440
            threads = None
            session = benchmark_session(BENCHMARK_POOL, BENCHMARK_PAYOUT, BENCHMARK_TLS, minutes, threads)
""",
    "GUI benchmark handler lock",
)

s = replace_exact(
    s,
    """        text = (f'ZTM will start REAL RandomX CPU mining.\\n\\nDuration: {minutes} minute(s)\\nCPU threads: Auto\\n\\nPool rewards go to the configured I2PS Dev Wallet.\\nMining consumes electricity and creates heat. You can STOP it at any time.\\n\\nStart now?')
""",
    """        text = ('ZTM-SRP1V1 will start a REAL RandomX CPU benchmark.\\n\\nDuration: 24 hours\\nCPU threads: Auto\\n\\nMining consumes electricity and creates heat. You can STOP it at any time.\\n\\nStart now?')
""",
    "GUI benchmark confirmation",
)

s = s.replace(
    "UNSUPPORTED: this engineering build targets Linux x86-64 only.",
    "UNSUPPORTED: ZTM-SRP1V1 targets Linux x86-64 only.",
)

gui.write_text(s, encoding="utf-8")

e = engine.read_text(encoding="utf-8")

e = replace_exact(
    e,
    '    parser.add_argument("--minutes", type=int, default=10, help="Run duration in whole minutes (default: 10)")\n',
    '    parser.add_argument("--minutes", type=int, default=1440, help="Stable release benchmark duration: fixed at 1440 minutes (24 hours)")\n',
    "engine minutes default",
)

e = replace_exact(
    e,
    '        a.minutes = int(payload.get("minutes", 10))\n',
    '        a.minutes = int(payload.get("minutes", 1440))\n',
    "engine session minutes default",
)

e = replace_exact(
    e,
    """    if not (1 <= a.minutes <= 1440) or (a.seconds is not None and not 1 <= a.seconds <= 86400):
        raise BenchError("Duration must be between 1 and 1440 minutes.")
""",
    """    if a.minutes != 1440 or (a.seconds is not None and a.seconds != 86400):
        raise BenchError("ZTM-SRP1V1 requires exactly 24 hours (1440 minutes / 86400 seconds).")
""",
    "engine duration lock",
)

rig_count = e.count("ZTM-α9")
if rig_count != 2:
    raise SystemExit(f"SECURITY STOP: rig ID carry-forward: expected exactly two pool-identification fields, found {rig_count}")
e = e.replace("ZTM-α9", "ZTM-R-A-10-E-R")
engine.write_text(e, encoding="utf-8")

c = control.read_text(encoding="utf-8")
c = replace_exact(c, "0.1.8~alpha9final1", "1.1.0~srp1v1", "Debian version")
control.write_text(c, encoding="utf-8")

# Stable-release invariants.
g = gui.read_text(encoding="utf-8")
en = engine.read_text(encoding="utf-8")
checks = {
    "stable release label": "Linux x86-64 · Stable Release V1.1" in g,
    "CPU Threads Auto header": "CPU Threads: Auto" in g,
    "fixed 24-hour acknowledgement": "I authorize real CPU work for 24 hours" in g,
    "requested contribution acknowledgement": "I understand this online benchmark uses both XMRig and I2PS dev contribution." in g,
    "removed Dev Wallet explanatory line": "Dev Wallet: initial benchmark rewards support I2PS software development." not in g,
    "removed duration selector": "duration_menu" not in g and "'DURATION'" not in g,
    "GUI fixed duration": "minutes = 1440" in g,
    "engine fixed duration": "a.minutes != 1440" in en and "a.seconds != 86400" in en,
    "adaptive GUI": "screen_w = self.root.winfo_screenwidth()" in g and "ui_scale = max(1.0, min(1.30" in g,
    "rig ID carry-forward": "ZTM-R-A-10-E-R" in en and "ZTM-α9" not in en,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("SECURITY STOP: invariant failure(s): " + ", ".join(failed))

print("ZTM-SRP1V1 patch applied and invariants verified.")
