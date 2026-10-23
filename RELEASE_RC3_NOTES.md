# ZTM-SRP1V2-RC3 — V2-only deterministic profile optimization
**Pre-release / test build**, derived from SHA-256-pinned official RC2. The public stable V2 and V3 remain untouched.

- Up to **11 total profiles**: automatic XMRig baseline and up to 10 deterministic CPU/cache/RAM-informed alternatives.
- **300 seconds measured per profile**, excluding readiness and stabilization.
- Before the next profile: confirmed guardian shutdown, authorized XMRig cleanup, five-second interval, and repeat check. Fail closed on a persistent/restarting miner.
- Live GUI beside hashrate: current profile X/Y, active threads, dataset initialization threads, elapsed/target test time.
- Retains RC2's pre-GUI cleanup, crash fix, 24-hour consent, wallet and huge-page behavior.
- Memory type may be unknown when Linux hardware/kernel EDAC does not expose it.
- CI and virtual GUI validation do not establish 24-hour Worker 14 performance.
