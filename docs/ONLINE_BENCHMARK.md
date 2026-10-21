# ZTM-SRP1V2 — 24-hour online RandomX benchmark

This document describes the benchmark implemented by **ZTM-SRP1V2 — Stable Release V1.2**.

## Fixed benchmark rules

- Online RandomX CPU work.
- Ubuntu Desktop x86-64.
- Real XMRig execution.
- Real mining-pool connection.
- **Exactly 24 hours** for the stable benchmark.
- **CPU Threads: Auto**.
- No duration selector in the normal GUI.
- Explicit authorization before CPU work.
- Visible Stop control during the run.
- An interrupted run is not treated as a completed qualifying benchmark.

The engine also enforces the 24-hour rule. Release verification confirmed that a 24-hour plan is accepted and a 60-minute plan is rejected.

## Required acknowledgements

The stable GUI requires exactly these two benchmark acknowledgements:

1. **I authorize real CPU work for 24 hours, including electricity use and heat.**
2. **I understand this online benchmark uses both XMRig and I2PS dev contribution.**

## Measurement

ZTM observes the machine under a real RandomX workload and records the behavior of the tested configurations.

Measurements can include:

- tested CPU thread profiles;
- sustained hashrate samples;
- selected profile;
- accepted shares;
- rejected shares;
- elapsed time;
- pool-verification status.

ZTM chooses the strongest configuration from the profiles it actually tested. That is not a claim that every possible hardware/software configuration has been exhaustively tested.

## Qualification

Wallet and personal mining remain locked until ZTM finds a qualifying uninterrupted 24-hour pool-verified benchmark result for the machine.

Shorter sessions cannot be combined to create a qualifying 24-hour result.

## Benchmark identity

The stable release uses worker identification:

`ZTM-RX1V2-L`

in both supported pool-identification fields.

## Safety

RandomX can place sustained load on the CPU and cooling system.

Use ZTM only on machines you own or are authorized to operate. Monitor the hardware appropriately for its environment.

## Winning configuration at completion

After a qualifying 24-hour pool-verified run, ZTM displays the **Winning Configuration**, including the selected active threads, score, tested profile, sustained hashrate median/mean/min/max, highest reading across the full run, peak from tested profiles, accepted/rejected shares, elapsed seconds and saved JSON report. The peak result is not substituted for sustained performance.
