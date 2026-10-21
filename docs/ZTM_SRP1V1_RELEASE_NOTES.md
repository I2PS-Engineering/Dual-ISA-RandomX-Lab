# ZTM-SRP1V1 — Stable Release V1.1

ZTM-SRP1V1 is the first stable-release baseline of Zero to Monero for Ubuntu Desktop x86-64.

## Stable benchmark

- Benchmark duration is locked to exactly **24 hours**.
- The normal GUI has no duration selector.
- CPU threads remain **Auto**.
- The engine rejects shorter benchmark durations.
- The tested-profile optimizer and real-pool measurement workflow are retained.

## GUI

- Header: **Linux x86-64 · Stable Release V1.1**.
- **CPU Threads: Auto** appears directly beneath the release label.
- First acknowledgement: **I authorize real CPU work for 24 hours, including electricity use and heat.**
- Second acknowledgement: **I understand this online benchmark uses both XMRig and I2PS dev contribution.**
- The previous separate Dev Wallet explanatory sentence is removed.
- Benchmark button: **START 24-HOUR RANDOMX BENCHMARK**.
- Adaptive display sizing is retained.
- Official ZTM 0–10K H/s application/desktop icon is retained.

## Runtime

- Rig identification: **ZTM-R-A-10-E-R**.
- One administrator authorization per open ZTM session is retained.
- Wallet and Mining qualification logic is retained.
- Developer-contribution behavior is retained.
- Clean XMRig shutdown behavior is retained.

## Package

- File: `ZTM-SRP1V1_amd64.deb`
- Debian version: `1.1.0~srp1v1`
- Architecture: `amd64`
- SHA-256: `acd4bee9a502e39a673cbf39679710553fd83720cc261f5915166e8eb1c6dd56`
- Size: `45,728` bytes

## Verification

The stable release build used exact-match guards for the approved changes, compiled the application Python sources, confirmed the required GUI strings and absence of the duration selector, confirmed a 24-hour plan is accepted while a 60-minute plan is rejected, verified both pool-identification fields, verified the desktop launcher and icon, checked package metadata, and confirmed files outside the approved GUI/engine/control edit scope remained unchanged.

Real hashrate remains a machine-specific measurement produced by the physical 24-hour run.
