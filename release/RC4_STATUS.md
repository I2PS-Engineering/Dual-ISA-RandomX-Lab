# ZTM V2 RC4 — verified candidate status

**Scope:** V2 only. Stable V2, RC3 installation instructions and V3 are unchanged.

## CI evidence

The RC4 candidate build and automated checks passed in [GitHub Actions run 39915037047](https://github.com/I2PS-Engineering/ZTM_Benchmark/actions/runs/39915037047).

The build reconstructs the verified RC3 Debian package, applies `release/patch_rc4.py`, checks the package version `1.2.4~srp1v2rc4`, compiles installed Python modules and runs topology and GUI checks.

## Implemented in this candidate

- 15-minute measured window per profile (900 seconds).
- Seven-profile maximum: original XMRig automatic baseline and **up to** six distinct alternative active-thread counts.
- Deterministic candidate ordering informed by detected CPU core count and cache inventory.
- Existing RC3 supervised XMRig lifecycle, verified five-second transition and GUI live progress retained.
- 24-hour minimum benchmark duration and existing consent/startup protections retained.

## Not implemented or not yet verified

- **Exactly seven meaningful profiles on all CPUs**: count-only profiles cannot guarantee six alternatives on machines with fewer than seven logical CPU counts.
- **Explicit XMRig per-thread CPU affinity** and topology-aware cache-domain or NUMA placement: inventory is collected but not enforced in the current engine.
- Separate empirical dataset initialization latency optimization; `randomx.init` is not a steady-state hashrate control.
- Live 24-hour Ubuntu hardware validation and HashVault VarDiff / accepted-share comparisons.
- 24-hour physical-hardware acceptance and measured HashVault results (the RC4 prerelease and checksum-verified installer are public).

**Release status:** RC4 is published as a development **prerelease**, not the production stable version. A pinned-SHA installer is published for controlled Ubuntu testing. Do not claim full hardware-aware CPU affinity or verified live HashVault gains. Do not modify V3.

## Published RC4 test installation

- [RC4 prerelease](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V2-RC4)
- [RC4 verified installer script](https://github.com/I2PS-Engineering/ZTM_Benchmark/blob/release/ztm-srp1v2-rc4/install-ztm-srp1v2-rc4.sh)
- Package SHA-256: `abd42a5ded115966dc20d761560581f2c6009575f73f433869400183404aa879` (121,844 bytes, `1.2.4~srp1v2rc4`)
- Installer SHA-256: `d009b90e8642e85496618282503d1c27cebf26c255537fc15592d049a7316d60`

