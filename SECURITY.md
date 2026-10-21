# Security policy — ZTM-SRP1V2

This policy applies to the current stable release, **ZTM-SRP1V2 — Stable Release V1.2**.

## Reporting a security issue

Report security concerns privately to **engineering@i2psolutions.com**.

Suggested subject:

**ZTM-SRP1V2 — Security**

Do not publish sensitive vulnerability details in a public issue before they have been reviewed.

## Security boundaries

ZTM is designed around the following boundaries:

- CPU mining/benchmarking begins only after explicit user authorization.
- The stable benchmark duration is fixed at **24 hours**.
- The user must check both benchmark acknowledgements before the benchmark starts.
- A visible Stop control remains available during CPU work.
- ZTM must not silently mine after installation.
- ZTM must not ignore Stop/exit requests or intentionally persist mining after the application session ends.
- Ubuntu privileged preparation uses a per-session authorization broker. ZTM does not store the user's administrator password and does not install a permanent passwordless sudo rule.
- The benchmark and mining engine use a separately licensed XMRig installation that is integrity-verified before use.
- Only a **public Monero receiving address** is required from the user for personal mining.
- ZTM never needs a recovery seed, wallet password, private spend key or private view key.
- Benchmark/result data should not expose wallet secrets, login credentials or unrelated local machine secrets.
- XMRig can create sustained CPU, electrical and thermal load. Run ZTM only on hardware you own or are authorized to operate.

## Developer contribution

The stable authorization explicitly states:

**I understand this online benchmark uses both XMRig and I2PS dev contribution.**

XMRig's upstream developer contribution is governed independently by XMRig and its GPLv3-licensed implementation. I2PS developer-contribution behavior belongs to ZTM and does not change XMRig's license.

## Release integrity

The official stable package is distributed through the GitHub Release tagged **ZTM-SRP1V2**.

Package identity:

- `ZTM-SRP1V2_amd64.deb`
- Debian version `1.2.0~srp1v2`
- SHA-256 `ab4e8339a100957df62b2dc83849d9efe6dee3b1fc51fca41a18f7a7b5f18077`

The official installer verifies package size, SHA-256, package name, architecture and Debian version before installation.

## Current validation boundary

The stable package and its release invariants have been verified. Hashrate, thermals, pool behavior and sustained performance remain machine-specific and are measured by the real 24-hour hardware run.
