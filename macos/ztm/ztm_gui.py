#!/usr/bin/env python3
"""ZTM — Zero to Monero; real GUI for Ubuntu and opt-in RandomX test.
Mining requires an explicit 24-hour benchmark gate and Terms acceptance.
"""
from __future__ import annotations

import json
import os
import platform
import queue
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import threading
import webbrowser
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from ztm_eligibility import eligible
from ztm_wallet import (write_public_record, read_public_record, find_monero_gui,
                        launch_monero_gui, WalletError, OFFICIAL_WALLET_URL,
                        OFFICIAL_RESTORE_URL, OFFICIAL_KEYS_URL)

DARK = '#070e18'
PANEL = '#0c1b2d'
CYAN = '#39bfff'
WHITE = '#f2f8ff'
MUTED = '#a0b8ce'
APP = Path(__file__).resolve().parent
ENGINE = APP / 'ztm_engine.py'
RESULTS = Path.home() / 'ZTM-Results'
MINING = APP / 'ztm_mining.py'
SESSION_CLIENT = APP / 'ztm_privilege_client.py'
SESSION_BROKER = APP / 'ztm_privileged_session.py'

# I2PS benchmark defaults (public payout address only; no secret keys).
# This diagnostic alpha is not proof of a validated 24h benchmark.
BENCHMARK_POOL = 'pool.hashvault.pro:443'
BENCHMARK_PAYOUT = '4AZPLhPbHimHbCsJarX6ThB2Rqo8jrHbjLJ3oFjsgA1gVWgFBtxywdQiFkS5Vn2E3eDR69oY7F1VbfnmrqBmbHB9Jpmsz9f'
BENCHMARK_TLS = False


def os_is_supported(system=None, architecture=None) -> bool:
    return (system or platform.system()) == 'Linux' and (architecture or platform.machine()).lower() in ('x86_64', 'amd64')


def prepare_steps(pkexec='pkexec'):
    """User-visible setup steps; privileged work uses the authenticated session."""
    client = [sys.executable, str(SESSION_CLIENT)]
    return [
        ('APT refresh', client + ['apt-update']),
        ('Install prerequisites', client + ['apt-install']),
        ('Load CPU MSR support', client + ['load-msr']),
        ('Install official, SHA-256-verified XMRig', [sys.executable, str(ENGINE), '--prepare']),
    ]


def benchmark_session(pool, wallet, tls, minutes, threads):
    from ztm_engine import validate_pool, validate_address, BenchError
    pool = validate_pool(pool)
    wallet = validate_address(wallet)
    if minutes != 1440:
        raise BenchError('Stable Release V1.1 requires one uninterrupted 24-hour benchmark.')
    if threads is not None:
        raise BenchError('Stable Release V1.1 uses CPU Threads: Auto.')
    return {'pool': pool, 'wallet': wallet, 'tls': tls, 'minutes': 1440, 'threads': None}


class ZTMApp:
    def __init__(self, root):
        self.root = root
        self.root.title('ZTM-SRP1V1 — Zero to Monero | I2PS Engineering')
        # Adaptive display sizing for compact high-resolution laptop panels.
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
        self.root.configure(bg=DARK)
        self.q = queue.Queue()
        self.process = None
        self.session_process = None
        self.session_dir = None
        self.busy = False
        self.prepared = False
        self.cancelled = False
        self.current_wallet = None
        self.state = tk.StringVar(value='1 · Prepare Linux & XMRig')
        self.status = tk.StringVar(value='Ready to prepare this Linux machine.')
        self.rate = tk.StringVar(value='— H/s')
        self.shares = tk.StringVar(value='Accepted — / Rejected —')
        self.threads = tk.StringVar(value='Auto')
        self.pool = tk.StringVar()
        self.wallet = tk.StringVar()
        self.wallet_validated = tk.StringVar(value='NO ADDRESS VALIDATED')
        self.local_wallet_path = tk.StringVar()
        self.wallet_file_status = tk.StringVar(value='Optional: reference a locally encrypted Monero wallet file')
        self.recovery_agreed = tk.BooleanVar(value=False)
        self.wallet_section = 'choose'
        record = read_public_record()
        if record:
            self.wallet.set(record['public_address'])
            self.local_wallet_path.set(record['local_wallet_file'])
        self.current_page = 'benchmark'
        self.mining_eligible = eligible(RESULTS)
        self.mining_terms_agreed = tk.BooleanVar(value=False)
        self.tls = tk.BooleanVar(value=True)
        self.upgrade_all = tk.BooleanVar(value=False)
        self.confirm_power = tk.BooleanVar(value=False)
        self.confirm_reward = tk.BooleanVar(value=False)
        self.view()
        self.root.after(100, self.pump)
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        if not os_is_supported():
            self.append('UNSUPPORTED: ZTM-SRP1V1 targets Linux x86-64 only.')
            self.prepare_btn.configure(state='disabled')

    def label(self, parent, text, size=11, color=WHITE, bold=False, **kw):
        return tk.Label(parent, text=text, fg=color, bg=parent['bg'], font=('DejaVu Sans', size, 'bold' if bold else 'normal'), **kw)

    def view(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('ZTM.TButton', font=('DejaVu Sans', 10, 'bold'), padding=(13, 10))
        style.configure('ZTM.TEntry', fieldbackground='#142740', foreground=WHITE, insertcolor=WHITE)
        bar = tk.Frame(self.root, bg=PANEL, pady=13, padx=20)
        bar.pack(fill='x')
        logo = APP / 'i2ps-logo.png'
        if logo.is_file():
            self.logo_image = tk.PhotoImage(file=str(logo))
            tk.Label(bar, image=self.logo_image, bg=PANEL).pack(side='left', padx=(0,15))
        self.label(bar, 'ZTM', 23, CYAN, True).pack(side='left')
        self.label(bar, '  ZERO TO MONERO  |  I2PS ENGINEERING', 13, WHITE, True).pack(side='left')
        release_box = tk.Frame(bar, bg=PANEL)
        release_box.pack(side='right')
        self.label(release_box, 'Linux x86-64 · Stable Release V1.1', 10, MUTED, True).pack(anchor='e')
        self.label(release_box, 'CPU Threads: Auto', 9, CYAN, True).pack(anchor='e')
        navigation = tk.Frame(self.root, bg='#091625', padx=20, pady=7)
        navigation.pack(fill='x')
        self.benchmark_nav = tk.Button(navigation, text='  BENCHMARK  ', command=lambda: self.show_page('benchmark'),
            font=('DejaVu Sans', 10, 'bold'), fg=DARK, bg=CYAN, activebackground='#7fd8ff',
            activeforeground=DARK, relief='flat', cursor='hand2', padx=18, pady=9)
        self.benchmark_nav.pack(side='left')
        self.wallet_nav = tk.Button(navigation, text='  WALLET  ', command=lambda: self.show_page('wallet'),
            font=('DejaVu Sans', 10, 'bold'), fg=MUTED, bg=PANEL, activebackground='#17344c',
            activeforeground=WHITE, relief='flat', cursor='hand2', padx=20, pady=9)
        self.wallet_nav.pack(side='left', padx=(8,0))
        self.mining_nav = tk.Button(navigation, text='  MINING  ', command=lambda: self.show_page('mining'),
            font=('DejaVu Sans', 10, 'bold'), fg='#647489', bg=PANEL,
            activebackground='#17344c', activeforeground=WHITE, relief='flat',
            cursor='hand2', padx=20, pady=9)
        self.mining_nav.pack(side='left', padx=(8,0))
        self.refresh_navigation()
        self.page_host = tk.Frame(self.root, bg=DARK)
        self.page_host.pack(fill='both', expand=True)
        main = tk.Frame(self.page_host, bg=DARK, padx=20, pady=13)
        self.benchmark_page = main
        main.pack(fill='both', expand=True)
        self.label(main, 'ONE INSTALLATION. LIVE TERMINAL. ACTUAL RANDOMX MEASUREMENTS.', 12, CYAN, True).pack(anchor='w', pady=(0, 6))
        self.label(main, 'Preparation runs APT update, installs prerequisites, then downloads verified official XMRig.\nPool and payout are preconfigured; no mining begins without authorization.', 10, MUTED, justify='left').pack(anchor='w')
        tk.Checkbutton(main, text='Also upgrade already-installed Ubuntu packages (apt-get upgrade -y; optional)', variable=self.upgrade_all, bg=DARK, fg=WHITE, activebackground=DARK, activeforeground=WHITE, selectcolor=DARK).pack(anchor='w', pady=(5,0))
        row = tk.Frame(main, bg=DARK)
        row.pack(fill='x', pady=(12, 8))
        self.prepare_btn = ttk.Button(row, text='1   PREPARE LINUX + INSTALL XMRIG', style='ZTM.TButton', command=self.prepare)
        self.prepare_btn.pack(side='left')
        self.stop_btn = ttk.Button(row, text='STOP', style='ZTM.TButton', command=self.stop, state='disabled')
        self.stop_btn.pack(side='left', padx=10)
        self.label(row, '', 10).pack(side='left')
        self.label(row, '', 10).pack(side='left')
        self.label(row, 'CURRENT STEP: ', 9, MUTED).pack(side='left')
        self.label(row, '', 9).pack(side='left')
        tk.Label(row, textvariable=self.state, fg=CYAN, bg=DARK, font=('DejaVu Sans', 10, 'bold')).pack(side='left')
        panels = tk.PanedWindow(main, orient=tk.VERTICAL, sashwidth=5, bg=DARK, bd=0)
        panels.pack(fill='both', expand=True)
        term_frame = tk.Frame(panels, bg=PANEL, padx=10, pady=8)
        self.label(term_frame, 'LIVE TERMINAL OUTPUT  •  APT / SETUP / XMRIG', 10, CYAN, True).pack(anchor='w')
        terminal = tk.Frame(term_frame, bg=PANEL)
        terminal.pack(fill='both', expand=True)
        self.terminal = tk.Text(terminal, wrap='word', font=('DejaVu Sans Mono', 9), bg='#050b12', fg='#baf9de', insertbackground=WHITE, bd=0, state='disabled', relief='flat')
        sc = ttk.Scrollbar(terminal, orient='vertical', command=self.terminal.yview)
        self.terminal.configure(yscrollcommand=sc.set)
        self.terminal.pack(side='left', fill='both', expand=True)
        sc.pack(side='right', fill='y')
        panels.add(term_frame, minsize=130, stretch='always')
        setup = tk.Frame(panels, bg=PANEL, padx=10, pady=8)
        self.label(setup, '2   BENCHMARK SETUP', 11, CYAN, True).pack(anchor='w')
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
        self.wallet_page = tk.Frame(self.page_host, bg=DARK, padx=25, pady=22)
        self.build_wallet_page()
        self.mining_page = tk.Frame(self.page_host, bg=DARK, padx=25, pady=22)
        panel = self.wallet_panel_in(self.mining_page, 'Personal Mining — HashVault',
            'Use your public Monero wallet address. CPU mining begins only when you select START MINING.')
        self.label(panel, 'Your wallet receives normal mining rewards through HashVault.', 11, WHITE).pack(anchor='w', pady=(2, 12))
        self.label(panel, 'CPU threads: Auto   |   Pool: HashVault', 10, MUTED).pack(anchor='w', pady=(0, 12))
        terms = tk.Frame(panel, bg=PANEL)
        terms.pack(anchor='w', pady=(0,12))
        tk.Checkbutton(terms, text='I accept the Mining Terms & Conditions.',
                       variable=self.mining_terms_agreed, bg=PANEL, fg=WHITE,
                       selectcolor=DARK, activeforeground=WHITE, activebackground=PANEL).pack(side='left')
        self.wallet_button(terms, 'VIEW TERMS', self.show_mining_terms, False).pack(side='left', padx=(12,0))
        self.mine_btn = self.wallet_button(panel, 'START MINING', self.start_mining)
        self.mine_btn.pack(side='left', padx=(0,12), pady=(0,12))
        self.mine_stop_btn = self.wallet_button(panel, 'STOP MINING', self.stop_mining, False)
        self.mine_stop_btn.pack(side='left', pady=(0,12))
        self.mine_stop_btn.configure(state='disabled')
        stats = tk.Frame(self.mining_page, bg=DARK)
        stats.pack(fill='x', pady=(16,0))
        tk.Label(stats, textvariable=self.rate, bg=DARK, fg=CYAN,
                 font=('DejaVu Sans', 14, 'bold')).pack(side='left')
        tk.Label(stats, textvariable=self.shares, bg=DARK, fg=MUTED,
                 font=('DejaVu Sans', 10)).pack(side='right')
        self.label(self.mining_page, 'Mining activity and pool responses appear in the existing live terminal on Benchmark.',
                   9, MUTED).pack(anchor='w', pady=(8,0))
        self.wallet.trace_add('write', self.wallet_changed)
        footer = tk.Frame(self.root, bg=PANEL, padx=16, pady=8)
        footer.pack(fill='x')
        tk.Label(footer, textvariable=self.status, bg=PANEL, fg=CYAN, anchor='w', font=('DejaVu Sans', 10)).pack(fill='x')
        self.append('ZTM is ready. Click PREPARE LINUX + INSTALL XMRIG to begin. No mining has started.')

    def show_page(self, page):
        """Switch tabs without recreating widgets or resetting unsaved field values."""
        if page not in ('benchmark', 'wallet', 'mining'):
            raise ValueError('Unknown ZTM page')
        self.refresh_navigation()
        if page in ('wallet', 'mining') and not self.mining_eligible:
            messagebox.showinfo('24-hour benchmark required',
                'You must complete the 24-hour benchmark for better mining results before opening Wallet or Mining.')
            return
        self.benchmark_page.pack_forget()
        self.wallet_page.pack_forget()
        self.mining_page.pack_forget()
        target = {'benchmark': self.benchmark_page, 'wallet': self.wallet_page,
                  'mining': self.mining_page}[page]
        target.pack(fill='both', expand=True)
        self.current_page = page
        for key, btn in (('benchmark', self.benchmark_nav), ('wallet', self.wallet_nav),
                         ('mining', self.mining_nav)):
            btn.configure(bg=CYAN if page == key else PANEL,
                          fg=DARK if page == key else (MUTED if self.mining_eligible else '#647489'))

    def refresh_navigation(self):
        self.mining_eligible = eligible(RESULTS)
        for item in ('wallet_nav', 'mining_nav'):
            widget = getattr(self, item, None)
            if widget:
                widget.configure(fg=MUTED if self.mining_eligible else '#647489')

    def wallet_panel_in(self, page, title, subtitle=''):
        if title:
            self.label(page, title, 14, WHITE, True).pack(anchor='w', pady=(6, 6))
        if subtitle:
            self.label(page, subtitle, 10, MUTED, justify='left', wraplength=970).pack(anchor='w', pady=(0,16))
        panel = tk.Frame(page, bg=PANEL, padx=22, pady=19)
        panel.pack(fill='x')
        return panel

    def show_mining_terms(self):
        from tkinter import messagebox
        terms_file = APP / 'MINING_TERMS.md'
        text = terms_file.read_text(encoding='utf-8') if terms_file.is_file() else 'Mining Terms are unavailable. Mining is disabled.'
        messagebox.showinfo('ZTM Mining Terms & Conditions', text)

    def start_mining(self):
        self.refresh_navigation()
        if not self.mining_eligible:
            self.show_page('mining')
            return
        if self.busy:
            messagebox.showinfo('ZTM', 'Stop the currently running task first.')
            return
        record = read_public_record()
        if record is None:
            messagebox.showinfo('Wallet required', 'Choose an existing wallet or create one first, then save its public receiving address.')
            self.show_page('wallet')
            return
        if not (APP / 'MINING_TERMS.md').is_file() or not self.mining_terms_agreed.get():
            messagebox.showerror('Acceptance required', 'Read and accept the Mining Terms & Conditions before starting.')
            return
        self.current_wallet = record['public_address']
        self.busy_start('3 · Personal mining running')
        self.status.set('Personal mining started; use STOP to finish.')
        self.mine_btn.configure(state='disabled')
        self.mine_stop_btn.configure(state='normal')
        def work():
            # A returning user may already be eligible without clicking Prepare.
            # The first personal-mining action then establishes the one-time
            # authorized application session instead of repeatedly using pkexec.
            try:
                self.ensure_authorized_session()
            except Exception as exc:
                self.q.put(('line','Authorization error: '+str(exc)))
                self.q.put(('done-mine',1))
                return
            cmd = [sys.executable, '-u', str(MINING), '--session-stdin', '--output', str(RESULTS)]
            result = self.run_command(cmd, json.dumps({'public_address': record['public_address'], 'authorized': True}))
            self.q.put(('done-mine', result))
        threading.Thread(target=work, daemon=True).start()

    def stop_mining(self):
        if self.busy and 'Personal mining' in self.state.get():
            self.stop()

    def wallet_changed(self, *args):
        """Never persist wallet details; a prior validation is invalid after an edit."""
        self.wallet_validated.set('NOT VALIDATED · CHECK PUBLIC ADDRESS')

    def check_wallet(self):
        """Validate the address shape, not ownership or pool compatibility."""
        from ztm_engine import validate_address, BenchError
        try:
            validate_address(self.wallet.get())
        except BenchError as exc:
            self.wallet_validated.set('INVALID FORMAT')
            messagebox.showerror('Wallet address', str(exc))
            return False
        self.wallet_validated.set('VALID PUBLIC ADDRESS FORMAT · OWNERSHIP NOT VERIFIED')
        return True

    def wallet_button(self, parent, title, action, primary=True):
        return tk.Button(parent, text=title, command=action,
                         bg=CYAN if primary else '#17344c',
                         fg=DARK if primary else WHITE,
                         activebackground='#7fd8ff' if primary else '#254966',
                         activeforeground=DARK if primary else WHITE,
                         relief='flat', cursor='hand2',
                         font=('DejaVu Sans', 11, 'bold'), padx=19, pady=12)

    def wallet_panel(self, title, subtitle=''):
        page = self.wallet_page
        self.label(page, 'WALLET', 23, CYAN, True).pack(anchor='w')
        if title:
            self.label(page, title, 14, WHITE, True).pack(anchor='w', pady=(6, 6))
        if subtitle:
            self.label(page, subtitle, 10, MUTED, justify='left', wraplength=970).pack(anchor='w', pady=(0, 16))
        panel = tk.Frame(page, bg=PANEL, padx=22, pady=19)
        panel.pack(fill='x')
        return panel

    def build_wallet_page(self, section='choose'):
        """Wallet tab is ONLY: existing wallet vs create one; then recovery help."""
        self.wallet_section = section
        page = self.wallet_page
        for widget in page.winfo_children():
            widget.destroy()
        if section == 'choose':
            panel = self.wallet_panel('Do you already have a Monero wallet?',
                'Choose one path. ZTM never requests, handles, or saves your wallet password, private keys, or recovery words.')
            self.wallet_button(panel, 'I HAVE AN EXISTING WALLET',
                               lambda: self.build_wallet_page('existing')).pack(fill='x', pady=(4, 14))
            self.wallet_button(panel, 'I DO NOT HAVE A WALLET — CREATE ONE',
                               lambda: self.build_wallet_page('create'), False).pack(fill='x')
            return
        if section == 'existing':
            panel = self.wallet_panel('Existing wallet',
                'Copy your PUBLIC receiving address from your Monero wallet. You may also select the existing encrypted wallet file for your reference. ZTM does not open that file.')
            self.label(panel, 'PUBLIC MONERO RECEIVING ADDRESS', 10, CYAN, True).pack(anchor='w')
            tk.Entry(panel, textvariable=self.wallet, bg='#142740', fg=WHITE, insertbackground=WHITE,
                     font=('DejaVu Sans Mono', 10), relief='flat').pack(fill='x', ipady=9, pady=(7,8))
            self.wallet_button(panel, 'CHECK ADDRESS FORMAT', self.check_wallet, False).pack(anchor='w', pady=(0, 8))
            tk.Label(panel, textvariable=self.wallet_validated, fg=CYAN, bg=PANEL,
                     font=('DejaVu Sans', 9, 'bold')).pack(anchor='w')
            self.label(panel, 'LOCAL WALLET FILE (OPTIONAL — REFERENCE ONLY)', 10, CYAN, True).pack(anchor='w', pady=(20, 7))
            row = tk.Frame(panel, bg=PANEL)
            row.pack(fill='x')
            tk.Entry(row, textvariable=self.local_wallet_path, bg='#142740', fg=WHITE,
                     insertbackground=WHITE, relief='flat', font=('DejaVu Sans', 10)).pack(side='left', fill='x', expand=True, ipady=9)
            self.wallet_button(row, 'BROWSE', self.choose_wallet_file, False).pack(side='left', padx=(10,0))
            self.label(panel, 'Wallet files remain in their original location. ZTM stores only the public address and an optional file path.',
                       9, MUTED, wraplength=950, justify='left').pack(anchor='w', pady=(7,14))
            self.wallet_button(panel, 'START MINING →', self.save_wallet_address).pack(anchor='w')
            self.wallet_button(page, '← BACK', lambda: self.build_wallet_page('choose'), False).pack(anchor='w', pady=(15,0))
            return
        if section == 'create':
            panel = self.wallet_panel('Create a new Monero wallet',
                'ZTM opens the official Monero wallet application to generate your actual wallet. Your wallet password and secret recovery phrase stay outside ZTM.')
            instructions = [
                '1  Open the official Monero GUI Wallet and choose CREATE A NEW WALLET.',
                '2  Choose a name and folder on this computer for your wallet.',
                '3  Choose and confirm a strong password in the official wallet.',
                '4  Save the secret recovery phrase securely OFFLINE, away from the wallet file.',
                '5  Finish creating the wallet; copy its PUBLIC receiving address.'
            ]
            for line in instructions:
                self.label(panel, line, 10, WHITE, wraplength=945, justify='left').pack(anchor='w', pady=4)
            self.wallet_button(panel, 'OPEN OFFICIAL MONERO WALLET', self.open_official_wallet).pack(anchor='w', pady=(17, 8))
            self.wallet_button(panel, 'DOWNLOAD OFFICIAL WALLET (IF NOT INSTALLED)',
                               lambda: webbrowser.open(OFFICIAL_WALLET_URL), False).pack(anchor='w', pady=(0,12))
            self.label(panel, 'The encrypted wallet is saved locally by Monero wallet software; no ZTM server receives its password or keys.',
                       9, MUTED, wraplength=900, justify='left').pack(anchor='w')
            nav = tk.Frame(page, bg=DARK)
            nav.pack(fill='x', pady=(12,0))
            self.wallet_button(nav, 'WALLET CREATED — RECOVERY INSTRUCTIONS →',
                               lambda: self.build_wallet_page('recovery')).pack(side='left')
            self.wallet_button(nav, '← BACK', lambda: self.build_wallet_page('choose'), False).pack(side='left', padx=(12,0))
            return
        if section == 'recovery':
            panel = self.wallet_panel('Wallet files & recovery — important notice',
                'Read this before using the new receiving address. ZTM does not keep a backup of your secrets and cannot recover your wallet for you.')
            messages = [
                'LOCAL FILES: The official Monero wallet saves an encrypted wallet file and a .keys file in the folder you chose. Locate the folder in the official wallet’s Settings / Info (Wallet path).',
                'PUBLIC ADDRESS: Find your receiving address under Receive / Account in the official wallet. This public address can be shared to receive mining rewards.',
                'PASSWORD: Needed to open the local encrypted wallet. It is NOT the 25-word recovery seed. ZTM cannot retrieve or reset this password.',
                'RECOVERY SEED: In the official wallet open Settings → Wallet → Show seed & keys (wording varies by version), unlock it locally, and write the recovery words down OFFLINE. Never paste them into ZTM, websites, chats or cloud storage.',
                'RESTORE: If the computer or wallet file is lost, use the official Monero wallet’s Restore from seed flow. Your wallet password alone cannot restore a lost wallet without the recovery seed.',
                'YOUR RESPONSIBILITY: You are solely responsible for backing up, protecting, remembering and recovering your wallet, password and secret recovery material. I2PS does not receive, retain, restore, or guarantee recovery of these materials.'
            ]
            for item in messages:
                self.label(panel, item, 9, WHITE, wraplength=950, justify='left').pack(anchor='w', pady=(0, 9))
            buttons = tk.Frame(page, bg=DARK)
            buttons.pack(fill='x', pady=(10,0))
            self.wallet_button(buttons, 'OFFICIAL MONERO RESTORE GUIDE ↗',
                               lambda: webbrowser.open(OFFICIAL_RESTORE_URL), False).pack(side='left')
            self.wallet_button(buttons, 'OFFICIAL KEY RECOVERY GUIDE ↗',
                               lambda: webbrowser.open(OFFICIAL_KEYS_URL), False).pack(side='left', padx=12)
            self.wallet_button(page, 'CONTINUE TO PUBLIC ADDRESS →',
                               lambda: self.build_wallet_page('existing')).pack(anchor='w', pady=(13, 0))
            return
        raise ValueError('Invalid wallet screen')

    def choose_wallet_file(self):
        file = filedialog.askopenfilename(title='Select existing encrypted Monero wallet file (optional)',
            initialdir=str(Path.home() / 'Monero' / 'wallets'),
            filetypes=[('Monero wallet files', '*'), ('All files', '*')])
        if file:
            self.local_wallet_path.set(file)

    def save_wallet_address(self):
        if not self.check_wallet():
            return
        try:
            path = write_public_record(self.wallet.get(), self.local_wallet_path.get())
        except (ValueError, OSError) as exc:
            messagebox.showerror('Wallet selection', str(exc))
            return
        self.status.set(f'Public address linked locally. Reference stored in {path}')
        self.show_page('mining')

    def open_official_wallet(self):
        try:
            launch_monero_gui()
            self.status.set('Official Monero wallet opened. Follow its create-wallet/password/recovery wizard.')
        except (WalletError, OSError) as exc:
            if messagebox.askyesno('Official Monero wallet required',
                                   str(exc)+'\n\nOpen official Monero downloads in your browser?'):
                webbrowser.open(OFFICIAL_WALLET_URL)

    def append(self, line):
        line = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', line).replace('\r', '\n')
        if self.current_wallet:
            line = line.replace(self.current_wallet, '[PUBLIC_WALLET]')
        self.terminal.configure(state='normal')
        self.terminal.insert('end', line.rstrip() + '\n')
        # Bounded display for long 24h sessions
        count = int(self.terminal.index('end-1c').split('.')[0])
        if count > 5000:
            self.terminal.delete('1.0', '1000.0')
        self.terminal.see('end')
        self.terminal.configure(state='disabled')
        speed = re.search(r'Measured XMRig speed:\s*([0-9,.]+ H/s)', line)
        if speed:
            self.rate.set(speed.group(1))
        shares = re.search(r'Pool shares.*accepted:\s*(\d+)\s*\|\s*rejected:\s*(\d+)', line)
        if shares:
            self.shares.set(f'Accepted {shares.group(1)} / Rejected {shares.group(2)}')

    def busy_start(self, step):
        self.busy = True
        self.cancelled = False
        self.state.set(step)
        self.prepare_btn.configure(state='disabled')
        self.benchmark_btn.configure(state='disabled')
        self.stop_btn.configure(state='normal')

    def busy_end(self):
        self.busy = False
        self.process = None
        self.current_wallet = None
        self.stop_btn.configure(state='disabled')
        self.prepare_btn.configure(state='normal')
        self.benchmark_btn.configure(state='normal' if self.prepared else 'disabled')

    def run_command(self, command, stdin_payload=None):
        if self.cancelled:
            return 130
        self.q.put(('line', '$ ' + ' '.join('***' if x.startswith('4') and len(x)>80 else x for x in command)))
        try:
            p = subprocess.Popen(command, stdin=subprocess.PIPE if stdin_payload else subprocess.DEVNULL,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 errors='replace', bufsize=1, start_new_session=True)
            self.process = p
            if stdin_payload:
                p.stdin.write(stdin_payload + '\n')
                p.stdin.flush()
                p.stdin.close()
            for line in p.stdout:
                if self.cancelled:
                    break
                self.q.put(('line', line))
            if self.cancelled and p.poll() is None:
                self.terminate_process(p)
            return p.wait()
        except Exception as e:
            self.q.put(('line', 'ERROR: ' + str(e)))
            return 1
        finally:
            self.process = None

    def ensure_authorized_session(self):
        """Authenticate once per GUI session; never retain the password."""
        if self.session_process is not None and self.session_process.poll() is None:
            return
        from ztm_root_guard import process_identity
        identity = process_identity(os.getpid())
        if identity is None:
            raise RuntimeError('Cannot validate GUI process identity')
        directory = Path(tempfile.mkdtemp(prefix='ztm-authorized-'))
        directory.chmod(0o700)
        socket_path = directory / 'session.sock'
        proc = subprocess.Popen(
            ['pkexec', '/usr/bin/python3', str(SESSION_BROKER),
             '--socket', str(socket_path), '--owner-pid', str(os.getpid()),
             '--owner-start', str(identity[1])],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.session_process = proc
        self.session_dir = directory
        deadline = time.monotonic() + 120
        try:
            while time.monotonic() < deadline and not self.cancelled:
                if proc.poll() is not None:
                    raise RuntimeError('Ubuntu administrator authorization was cancelled or failed')
                if socket_path.is_socket():
                    import socket
                    try:
                        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as probe:
                            probe.settimeout(0.2)
                            probe.connect(str(socket_path))
                            probe.sendall(b'{"op":"ping","args":[]}\n')
                            if b'"code": 0' in probe.recv(128):
                                os.environ['ZTM_SESSION_SOCKET']=str(socket_path)
                                self.q.put(('line','[ZTM] Administrator authorization active for this ZTM session.'))
                                return
                    except (OSError,ValueError):
                        pass
                time.sleep(0.25)
            raise RuntimeError('Authorization timed out or was cancelled')
        except BaseException:
            os.environ.pop('ZTM_SESSION_SOCKET',None)
            if proc.poll() is None:
                # The root broker also monitors this GUI PID and self-terminates.
                try:
                    from ztm_privilege_client import call
                    call('shutdown',sock_path=str(socket_path),emit=lambda msg:None)
                except Exception: pass
            raise

    def close_authorized_session(self):
        from ztm_privilege_client import call
        path=os.environ.pop('ZTM_SESSION_SOCKET',None)
        if path:
            try: call('shutdown',sock_path=path,emit=lambda msg:None)
            except (OSError,RuntimeError,ValueError): pass
        self.session_process=None
        self.session_dir=None

    def prepare(self):
        if self.busy or not os_is_supported(): return
        if os.geteuid() == 0:
            messagebox.showerror('ZTM', 'Launch ZTM as your regular desktop user, not root.')
            return
        if not shutil.which('pkexec'):
            messagebox.showerror('ZTM', 'pkexec is not installed. Install polkit/pkexec using Ubuntu software tools, then relaunch.')
            return
        if not messagebox.askyesno('ZTM system preparation', 'ZTM will run apt-get update, install required packages, and download official XMRig 6.26.0 (SHA-256 verified).'+ ('\nSystem packages will also be upgraded.' if self.upgrade_all.get() else '') + '\n\nUbuntu will request administrator authorization. Continue?'):
            return
        self.busy_start('1 · Preparing APT and XMRig')
        def work():
            try:
                self.ensure_authorized_session()
            except Exception as exc:
                self.q.put(('line','Authorization error: '+str(exc)))
                self.q.put(('done-prepare',(False,'Administrator authorization',1)))
                return
            steps = prepare_steps()
            if self.upgrade_all.get():
                steps.insert(1, ('Upgrade installed packages', [sys.executable,str(SESSION_CLIENT),'apt-upgrade']))
            for caption, cmd in steps:
                self.q.put(('status', caption))
                result = self.run_command(cmd)
                if result != 0 or self.cancelled:
                    self.q.put(('done-prepare', (False, caption, result)))
                    return
            self.q.put(('done-prepare', (True, 'Preparation complete', 0)))
        threading.Thread(target=work, daemon=True).start()

    def benchmark(self):
        if self.busy or not self.prepared: return
        try:
            minutes = 1440
            threads = None
            session = benchmark_session(BENCHMARK_POOL, BENCHMARK_PAYOUT, BENCHMARK_TLS, minutes, threads)
        except Exception as e:
            messagebox.showerror('Benchmark configuration', str(e))
            return
        if not (self.confirm_power.get() and self.confirm_reward.get()):
            messagebox.showerror('Authorization required', 'Read and check both benchmark acknowledgments before starting.')
            return
        text = ('ZTM-SRP1V1 will start a REAL RandomX CPU benchmark.\n\nDuration: 24 hours\nCPU threads: Auto\n\nMining consumes electricity and creates heat. You can STOP it at any time.\n\nStart now?')
        if not messagebox.askyesno('Authorize REAL CPU benchmark', text):
            return
        RESULTS.mkdir(parents=True, exist_ok=True)
        self.current_wallet = session['wallet']
        self.busy_start('2 · Online CPU benchmark running')
        self.status.set('Real XMRig online benchmark is running. Press STOP to interrupt.')
        def work():
            cmd = [sys.executable, '-u', str(ENGINE), '--session-stdin', '--output', str(RESULTS)]
            result = self.run_command(cmd, json.dumps(session))
            self.q.put(('done-bench', result))
        threading.Thread(target=work, daemon=True).start()

    def terminate_process(self, proc):
        try:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGINT)
        except ProcessLookupError:
            pass
        except OSError:
            try: proc.terminate()
            except OSError: pass

    def stop(self):
        if not self.busy: return
        prompt = ('Stop personal mining now?' if 'Personal mining' in self.state.get()
                  else 'Stop the current operation? An interrupted benchmark is not complete.')
        if not messagebox.askyesno('Stop ZTM task', prompt):
            return
        self.cancelled = True
        if self.process:
            self.terminate_process(self.process)
        self.status.set('Stopping the active operation…')

    def pump(self):
        try:
            for _ in range(300):
                typ, payload = self.q.get_nowait()
                if typ == 'line': self.append(payload)
                elif typ == 'status': self.status.set(payload)
                elif typ == 'done-prepare':
                    ok, caption, status = payload
                    self.prepared = ok
                    self.busy_end()
                    self.state.set('2 · Ready for online benchmark' if ok else 'Preparation incomplete')
                    self.status.set('Ready. Authorize CPU work to start benchmarking.' if ok else f'Setup failed/stopped: {caption} (exit {status}). Review terminal output.')
                elif typ == 'done-mine':
                    self.busy_end()
                    self.mine_btn.configure(state='normal')
                    self.mine_stop_btn.configure(state='disabled')
                    self.status.set('Personal mining stopped.' if payload == 0 else f'Personal mining exited ({payload}).')
                elif typ == 'done-bench':
                    self.refresh_navigation()
                    self.busy_end()
                    self.state.set('2 · Finished' if payload == 0 else '2 · Partial / stopped')
                    self.status.set('Measured report written to ~/ZTM-Results.' if payload == 0 else f'Benchmark incomplete (exit {payload}). View log/report in ~/ZTM-Results.')
        except queue.Empty:
            pass
        self.root.after(100, self.pump)

    def open_results(self):
        RESULTS.mkdir(parents=True, exist_ok=True)
        if shutil.which('xdg-open'):
            subprocess.Popen(['xdg-open', str(RESULTS)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            messagebox.showinfo('Results folder', str(RESULTS))

    def close(self):
        if self.busy:
            if not messagebox.askyesno('Exit ZTM', 'An operation is in progress. Stop it and close?'):
                return
            self.cancelled = True
            if self.process:
                self.terminate_process(self.process)
            # delay destruction, allowing controller to stop XMRig in its own session
            self.root.after(1200, self.destroy_and_close_session)
            return
        self.destroy_and_close_session()

    def destroy_and_close_session(self):
        try: self.close_authorized_session()
        finally: self.root.destroy()


def main():
    root = tk.Tk()
    ZTMApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
