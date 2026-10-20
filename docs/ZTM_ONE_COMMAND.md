# ZTM — One-command Ubuntu Desktop installer

**Latest published engineering release: ZTM 0.1.4-alpha5-optimizer.**

This is the existing alpha4 ZTM interface with a surgical benchmark-engine update only.

- GUI, Wallet tab, logo, layout, terminal, Duration control, CPU Threads display and both authorization checkboxes are unchanged.
- Embedded HashVault connection, configured Dev Wallet payout, MSR/huge-page preparation and dedicated worker identity `ZTM-Zero-to-Monero` are retained.
- **CPU Threads: Auto** now benchmarks multiple active-thread profiles internally, scores sustained performance/stability/share quality, selects the best measured profile and uses it for the remainder of the selected benchmark duration.
- The benchmark still stops automatically at the selected duration, and closing ZTM still stops its miner process.

## One command

Run this as your normal Ubuntu Desktop x86-64 user:

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/Dual-ISA-RandomX-Lab/7bc2a91ba0c389db63dbea322afa86067aa29aa2/install-ztm-v5.sh";b=urllib.request.urlopen(u,timeout=30).read();assert hashlib.sha256(b).hexdigest()=="e615232a75c3497dee9ec167cfa277381a03dc3f9d5df42db9babe1db5b3cb83","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

The pinned installer reconstructs the alpha5 Debian package from immutable GitHub-hosted transfer fragments at package commit `fd444f718724d40b423d3b058d4adf2fe49b7d92`, then verifies the completed package before installation.

Verified package:
- Debian version: `0.1.4~alpha5optimizer1`
- architecture: `amd64`
- package size: **27,448 bytes**
- package SHA-256: `ef41146e5de18201bb5f0a92d2729006c9b00bdff9b851ce2fd5a66884c52daf`

After installation ZTM launches. Mining does not start until the existing GUI authorization is completed.

## Automatic optimizer behavior

The selected overall Duration remains the hard deadline. Profile exploration is part of that duration, not added on top.

- under 5 minutes: single-profile connectivity/measurement run;
- 5–15 minutes: up to 3 total profiles, 60 seconds each;
- 15–60 minutes: up to 5 total profiles, 90 seconds each;
- 60 minutes or more: up to 6 total profiles, 120 seconds each.

ZTM first measures XMRig Auto, then tests sensible alternate thread counts. The best measured profile is chosen using sustained median hashrate, stability, and accepted/rejected share quality. The remaining time runs on the selected profile.

See [alpha5 release notes](ZTM_ALPHA5_RELEASE_NOTES.md).

## Validation status

Package metadata, package hash, unchanged GUI/Wallet hashes, and synthetic end-to-end optimizer behavior were verified locally. The synthetic test hot-switched one miner process across 2 → 1 → 3 → 4 threads, selected the controlled 2-thread winner, retained cumulative share accounting, continued with the winner, and stopped at the configured deadline.

A real Ubuntu/HashVault alpha5 run is still required to validate the optimizer against physical hardware. The successful live run shown with the previous build verifies real mining and accepted shares, not alpha5 profile selection.
