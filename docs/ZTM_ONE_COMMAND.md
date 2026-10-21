# ZTM_Benchmark — One-command installation (α9 final)

This is the current ZTM α9 integration release for Ubuntu Desktop x86-64.

## Step 1 — Stop any existing miner

Close any older ZTM instance and confirm no XMRig process is already running.

```bash
pgrep -a -x xmrig
```

No output means no XMRig process is running.

## Step 2 — Install ZTM α9 final

Run this exact command as your normal Ubuntu desktop user, not root:

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/e2dfa994c7fa4a209fca03d79485605c19bb58c7/install-ztm-v9.sh";b=urllib.request.urlopen(u,timeout=30).read();assert hashlib.sha256(b).hexdigest()=="02d7ebdab9326ffa2de6f0646c77919e5a5ed7203f3706d3c3872f4d79c3991c","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

The bootstrap is pinned to installer commit `e2dfa994c7fa4a209fca03d79485605c19bb58c7` and verifies its SHA-256 before executing it.

The installer then downloads the α9 final package from immutable package commit `b0c5298341343644ce0a618f15717f7d6193aba3`, verifies:

- Debian package: `ztm-zero-to-monero`
- Architecture: `amd64`
- Debian version: `0.1.8~alpha9final1`
- Package size: `45,962` bytes
- Package SHA-256: `6aec29e14d1c33bc17a9350bf5990bf998c5be2ac12c708e3bf5989c4e834c3a`

The installer uses Python's built-in HTTPS downloader and does not require curl to already be installed.

## α9 final changes

- Benchmark worker / rig ID is exactly `ZTM-α9`, using the Greek alpha character.
- Official ZTM 0–10K H/s performance-gauge icon is installed for the application/desktop shortcut.
- Desktop launcher behavior is retained.
- One-administrator-authentication session behavior is retained.
- Benchmark optimizer, Wallet, Mining, donation logic, 24-hour unlock gate, and miner shutdown guardian are unchanged.

XMRig supports a string `rig-id`; pool-side rig-ID display is a third-party extension and therefore the exact Unicode presentation on HashVault is validated by the live pool test rather than assumed.

## i7 24-hour validation

Use CPU Threads: Auto and select 24 hours. Let the benchmark finish without interruption. After completion, compare the selected profile, median/average H/s, accepted/rejected shares, and final sustained profile against the previous ~1,000 H/s reference.

A completed 24-hour pool-verified run should unlock Wallet and Mining; a partial run must not.

[α9 final release notes](ZTM_ALPHA9_FINAL.md) · [Repository](https://github.com/I2PS-Engineering/ZTM_Benchmark)
