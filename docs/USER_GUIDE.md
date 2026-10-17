# Dual-ISA RandomX Lab — user guide

This is the public text counterpart to the planned installation PDF.

**Product:** I2PS Dual-ISA RandomX Lab  
**Author:** I2PS Engineering / I2PS Solutions  
**Use:** Free for qualifying noncommercial use; proprietary, not open source. [License](../LICENSE.md).

## What the program is for

Measure **real RandomX performance on the CPU of the user's own computer**, compare supported thread configurations over sustained operation, and report the strongest **tested** configuration. It is not a CPU simulation and does not promise a universal optimum or profitability.

## Getting started

1. Read the [release status](STATUS.md). A production-ready v0.4 application is **not yet available**.
2. When an approved download exists, select your route: [already using Linux](EXISTING_LINUX.md) or [Windows to Ubuntu](WINDOWS_TO_UBUNTU.md).
3. Open the program. The intended v0.4 first-launch assistant will check dependencies and offer to install verified XMRig, with user approval. Installation is not mining authorization.
4. Read the licensing conditions and the Dev Wallet disclosure before agreeing to CPU mining.
5. Once you authorize it, the intended online RandomX benchmark runs for **at least 24 hours of continuous active time**, with initial mining rewards directed to the Dev Wallet.
6. Review share and sustained hashrate metrics; an interrupted run must not be labeled complete.
7. After completion, enter **only your own public Monero receiving address** to configure personal mining. If you lack a wallet, see [official wallet resources](MONERO_WALLET_GUIDE.md).
8. Personal mining uses a distinct authorized session; built-in Dev Donate remains part of the planned developer-support model, with exact terms pending specification.

## First authorization

**Exactly two acknowledgments** appear in the approved v0.4 interface:

1. “I understand this benchmark uses my CPU continuously for approximately 24 hours so I can get the best result running my own RandomX miner.”
2. “I understand the terms and conditions of using I2PS RandomX CPU Benchmark software.”

The Dev Wallet recipient and electricity/CPU implications are disclosed **separately and prominently**. Users must be able to **stop mining** at any time.

## Security

Never paste private spend/view keys, seed phrases or passwords into this app. Keep the local server inaccessible to public networks. Back up files before an OS migration.

## Further reading

[Installation](INSTALLATION.md) · [Benchmark specification](ONLINE_BENCHMARK.md) · [Wallet guide](MONERO_WALLET_GUIDE.md) · [FAQ](FAQ.md) · [Support](../SUPPORT.md)
