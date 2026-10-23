# Changelog

## ZTM-SRP1V2-RC4 — Ubuntu V2 development prerelease — 23 October 2026

- **Current latest controlled V2 test build:** `ZTM-SRP1V2-RC4` (prerelease; not a new stable version).
- Verified Ubuntu x86-64 package version `1.2.4~srp1v2rc4`.
- Original XMRig automatic baseline plus up to six unique, hardware-ranked active-thread alternatives (**maximum seven profiles**).
- **15 minutes per measured profile**, replacing RC3's five-minute window.
- Existing supervised XMRig stop/restart process and five-second verified transitions preserved from RC3.
- CPU inventory collects physical/logical core information, SMT sibling groups, detected L1/L2/L3 cache capacities and sharing domains, NUMA-node count and memory availability; deterministic hardware-informed thread-count ranking.
- Live GUI displays current profile, active and dataset-initialization threads, and elapsed/target time `15:00`.
- Existing 24-hour benchmark requirement, authorization, contribution and wallet workflow unchanged.
- **Limitations:** RC4 does not yet enforce per-thread CPU affinity or NUMA placement; on processors with fewer than six distinct alternatives it tests fewer than seven profiles. Full physical 24-hour HashVault testing pending.
- RC4 package SHA-256: `abd42a5ded115966dc20d761560581f2c6009575f73f433869400183404aa879`; package size: 121,844 bytes.
- Exact Ubuntu installer SHA-256: `d009b90e8642e85496618282503d1c27cebf26c255537fc15592d049a7316d60`; verified on [Ubuntu CI](https://github.com/I2PS-Engineering/ZTM_Benchmark/actions/runs/39930914536).
- [RC4 installation](README.md#install) · [RC4 prerelease](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V2-RC4).
- The V2 stable release and V3 remain unchanged.


## ZTM-SRP1V2 — Linux GUI Readability Update V1.2 — 21 October 2026

- Default font zoom increased to **165%** across terminal, navigation, consent labels, buttons and wallet interface.
- **A− / A+** zoom buttons adjust the UI between 125% and 200% without altering the benchmark.
- Button padding and descriptive text wrapping improved for laptop displays.
- New pool rig ID **`ZTM-RX1V2-L`** for the benchmark and personal-mining pool identification.
- After successful qualifying 24-hour completion, the engine prints and records **Winning Configuration** and the GUI displays it, including selected active threads, optimization score, measured sustained median/mean/min/max, peak rates, accepted/rejected shares, elapsed time and report path.
- Fixed **24-hour** benchmarking, CPU Threads: Auto, consent, eligibility gate, donation mechanism and termination logic retained.
- Ubuntu x86-64 package: **`ZTM-SRP1V2_amd64.deb`**; Debian version `1.2.0~srp1v2`.
- Debian SHA-256: `ab4e8339a100957df62b2dc83849d9efe6dee3b1fc51fca41a18f7a7b5f18077`.

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
