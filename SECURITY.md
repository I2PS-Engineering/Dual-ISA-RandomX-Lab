# Security policy and responsible use

## Support and reporting

Report security concerns **privately** to **engineering@i2psolutions.com**, with subject **Dual-ISA RandomX Lab — Security**. Do not post private keys, seed phrases, wallet recovery data, credentials or private miner configurations in GitHub issues.

## Operational boundaries

- The benchmarking/mining application operates only with the machine owner's explicit authorization.
- The software must not mine silently after installation, run hidden tasks, or defeat Stop/exit requests.
- Initial online benchmarking routes rewards to the **Dev Wallet**; beneficiary, 24-hour operation and costs must be disclosed before consent.
- Personal mining is a **separate** user-authorized operation.
- Only public Monero receiving addresses are needed. Never request private spend keys, private view keys or wallet seeds.
- Use independently released and integrity-verified XMRig; preserve its GPLv3 rights and default developer contribution.
- A local control server should remain loopback-only. Do not expose it to the Internet without an explicit authentication/security design.
- Benchmark exports should omit hostnames, local IPs, wallet secrets, pool credentials and raw configuration files.
- XMRig can stress CPU, cooling and power. Users should monitor equipment and use systems they have permission to operate.

## Status

The full 24-hour online architecture and its security controls are **not released or hardware-verified**. Do not treat design previews as security assurance.
