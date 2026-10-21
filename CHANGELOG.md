# Changelog

## ZTM-SRP1V1 — Stable Release V1.1 — 21 October 2026

First stable-release baseline of ZTM — Zero to Monero.

### Benchmark

- Online RandomX benchmark fixed to exactly **24 hours**.
- Duration selector removed from the normal GUI.
- Engine rejects non-24-hour benchmark durations.
- CPU thread selection fixed to **Auto** for the benchmark workflow.
- Automatic tested-profile optimizer retained.
- Pool share and sustained-hashrate measurement retained.
- Qualifying 24-hour completion remains required before Wallet/Mining unlock.

### Authorization and disclosure

- First acknowledgement:
  - **I authorize real CPU work for 24 hours, including electricity use and heat.**
- Second acknowledgement:
  - **I understand this online benchmark uses both XMRig and I2PS dev contribution.**
- Separate earlier Dev Wallet explanatory line removed.

### Interface

- Release header changed to **Linux x86-64 · Stable Release V1.1**.
- **CPU Threads: Auto** shown beneath the stable-release label.
- Benchmark button changed to **START 24-HOUR RANDOMX BENCHMARK**.
- Adaptive GUI sizing retained for compact high-resolution displays.
- Official ZTM 0–10K H/s desktop/application icon retained.

### Runtime

- Rig identification: `ZTM-R-A-10-E-R`.
- One administrator authorization per open ZTM session retained.
- Wallet and personal-mining workflow retained.
- Clean XMRig shutdown guardian retained.
- Existing developer-contribution behavior retained.

### Distribution

- Stable Debian package: `ZTM-SRP1V1_amd64.deb`.
- Debian version: `1.1.0~srp1v1`.
- Architecture: `amd64`.
- Package SHA-256: `acd4bee9a502e39a673cbf39679710553fd83720cc261f5915166e8eb1c6dd56`.
- Distributed through the GitHub Release tagged `ZTM-SRP1V1`.

Earlier development history remains available in Git history but is no longer part of the current public repository surface.
