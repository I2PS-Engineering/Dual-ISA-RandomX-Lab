# Online RandomX benchmarking — approved v0.4 specification

**Status: APPROVED DESIGN / NOT IMPLEMENTED.**

## Core rules

- **Online only. No offline benchmark is available.**
- Real RandomX computation executes on the machine's **physical CPU** using a supported XMRig build.
- A live mining-pool connection is required throughout each active benchmarking interval.
- The **initial benchmark lasts a minimum of 24 hours of continuous active operation** to assess sustained performance. Do not count outages as successful active time and do not mark interrupted benchmarks complete.
- **All mining rewards attributable to the initial 24-hour benchmark are directed to the Dev Wallet.** This fact must be prominently disclosed before the first pool connection.
- Show that mining uses CPU resources and electricity and can cause thermal load. Require explicit, informed authorization before starting any online mining.
- **Stop** must remain available throughout the run and must terminate mining.
- No pool mining begins solely because the user installed dependencies or launched the program.

## Authorization screen — exact two acknowledgments

1. “I understand this benchmark uses my CPU continuously for approximately 24 hours so I can get the best result running my own RandomX miner.”
2. “I understand the terms and conditions of using I2PS RandomX CPU Benchmark software.”

The program must additionally explain the **Dev Wallet** payout arrangement prominently, not hide it inside the checkboxes.

## Dev Wallet text

> **Dev Wallet** — This contributes in the development of the software, of its future versions, and keeping it alive and always free, as it was first intended.

The GUI is **not** to display the payout wallet address or any private wallet key. A concealed GUI address must not conceal the beneficiary or prevent auditing the actual mining payout behavior.

## Measurement protocol (engineering proposal)

- Detect CPU model, ISA, physical/logical cores, available memory, platform, supported RandomX variant and XMRig version.
- Use configured live pool; capture observed H/s, accepted/rejected/stale share counts, difficulty, uptime, and connection interruptions.
- Test planned thread profiles for **sufficient sustained observation**, not only transient peak H/s. Avoid changing many independent variables simultaneously.
- Record test profile, start/end timestamps, accepted active seconds, ambient/power/thermal context where available and mining engine exit status.
- Distinguish local XMRig hashrate from pool-estimated hashrate and pool-reported shares.
- Compare profiles by repeated stable intervals, reporting averages, medians, stability and rejection metrics. Do not call a result “optimal” beyond the set of configurations actually tested.
- Persist progress safely for diagnostic review, but a paused/restarted run is not a successful continuous 24-hour test.
- After completion, generate a report and **then** guide the user to enter a personal public Monero receiving address.

## Testing gate

No public claim of operational 24-hour online benchmarking until complete real-hardware trials confirm connectivity, logging, exact payout routing, time accounting, Stop behavior, errors, thermal handling and reporting.
