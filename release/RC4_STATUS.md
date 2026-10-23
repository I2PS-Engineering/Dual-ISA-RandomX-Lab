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
- Public RC4 release assets and installation command.

**Release gate:** Do not promote this candidate to a public RC4 installer or claim full hardware-aware optimization until the missing capabilities are implemented and tested. Do not modify V3.
