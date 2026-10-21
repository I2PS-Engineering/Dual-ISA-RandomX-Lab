# ZTM-SRP1V1 — Stable Release V1.1

ZTM-SRP1V1 is the first stable-release baseline of Zero to Monero for Ubuntu Desktop x86-64.

## Approved stable-release behavior

- Benchmark duration is locked to exactly **24 hours**.
- The normal GUI has **no duration selector**.
- CPU threads remain **Auto**.
- Header: **Linux x86-64 · Stable Release V1.1**.
- **CPU Threads: Auto** appears directly beneath the release label.
- First acknowledgement: **I authorize real CPU work for 24 hours, including electricity use and heat.**
- Second acknowledgement: **I understand this online benchmark uses both XMRig and I2PS dev contribution.**
- The separate Dev Wallet explanatory sentence has been removed.
- Benchmark button: **START 24-HOUR RANDOMX BENCHMARK**.
- Adaptive GUI sizing is retained.
- Official ZTM 0–10K H/s application/desktop icon is retained.
- Rig ID: **ZTM-R-A-10-E-R**.
- One administrator authorization per open ZTM session is retained.
- Optimizer, Wallet, Mining, 24-hour eligibility verification, donation behavior, and clean XMRig shutdown guardian are retained.

## Package

- File: ZTM-SRP1V1_amd64.deb
- Debian version: 1.1.0~srp1v1
- Architecture: amd64
- SHA-256: acd4bee9a502e39a673cbf39679710553fd83720cc261f5915166e8eb1c6dd56
- Bytes: 45728

## Verification

The release build verified the immutable alpha9 final package before modification, applied the stable-release patch with exact-match guards, compiled the Python sources, confirmed the approved GUI text and absence of the duration selector, proved the engine accepts 24 hours and rejects a 60-minute run, verified both pool-identification fields use ZTM-R-A-10-E-R, verified the desktop launcher and icon, checked package metadata, and confirmed every package file outside the approved GUI/engine/control edit scope remained byte-for-byte unchanged.

The physical 24-hour performance run remains the real-hardware validation of sustained hashrate and pool behavior.
