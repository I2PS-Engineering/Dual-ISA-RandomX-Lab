# Dual-ISA RandomX Lab

**I2PS Engineering** · *Zero to Monero — Part 2*  
**Built in Morocco. Engineered for the future.**

> **Free to use under a proprietary license — NOT open source.**  
> **v0.4 online-only 24-hour benchmarking is in development, not a completed release.**

## About the project

Dual-ISA RandomX Lab is a CPU benchmarking application by I2PS Engineering. Its purpose is to help users measure real RandomX performance on their own hardware, test thread configurations, compare sustained hashrate and understand the results. The laboratory investigates **x86-64 and ARM64** systems and uses **XMRig** as a separately licensed third-party execution engine.

It does **not** simulate CPU performance.

### Important release distinction

| Item | Status |
| --- | --- |
| v0.3.1 Linux Quickstart and local application | Development/test build, **not yet approved as a public production release** |
| v0.4 authorization screen | UI preview built; no mining triggered by its preview button |
| v0.4 online-only, 24-hour benchmark controller | **Not implemented or live-validated yet** |
| v0.4 automatic first-run setup flow | Planned; not completed |
| v0.4 personal wallet mining and built-in Dev Donate | Approved design; full implementation and verification pending |

**Do not use existing v0.3.x builds as if they implement the approved v0.4 flow.** Older prototypes have an offline benchmark; **the intended v0.4 product has no offline benchmark option**.

## Planned v0.4 user journey

1. **Open the I2PS application.** Review the license and setup requirements.
2. **Prepare the machine.** A first-run assistant will check dependencies and, after confirmation, install a separately licensed official XMRig build with integrity verification.
3. **Authorize the online benchmark.** Read the prominent CPU/electricity and **Dev Wallet** disclosures, accept the two authorization acknowledgments, and explicitly start mining.
4. **Run at least 24 hours** of real CPU RandomX mining/benchmarking against a pool. **Initial benchmark rewards are directed to the Dev Wallet.** An interrupted run is not marked complete.
5. **Review sustained performance.** Compare tested CPU thread profiles, average/median hashrate, share results and stability; do not promise an untested optimum.
6. **Configure your own Monero wallet.** After completion, supply **only a public receiving address**, or follow the official wallet guides. Private keys and recovery seeds are never requested.
7. **Start personal mining separately** with the tested configuration. The built-in **Dev Donate** mechanism supports I2PS development, future updates and continuous support. The contribution rate and switching details have **not yet been finalized**, and will need clear disclosure before activation.

### Dev Wallet

> **Dev Wallet** — This contributes in the development of the software, of its future versions, and keeping it alive and always free, as it was first intended.

The initial 24-hour run uses CPU resources and electricity; its mining rewards benefit the Dev Wallet. This fact must be explained **before** the user authorizes mining. The application must provide a Stop control. This is not an offline benchmark or a simulation.

## Documentation

- [Project and implementation status](docs/STATUS.md)
- [Installation overview](docs/INSTALLATION.md)
- [Already using Linux](docs/EXISTING_LINUX.md)
- [Migrating from Windows to Ubuntu](docs/WINDOWS_TO_UBUNTU.md)
- [24-hour online benchmark specification](docs/ONLINE_BENCHMARK.md)
- [Wallet and private-key safety](docs/MONERO_WALLET_GUIDE.md)
- [Dev Wallet and Dev Donate policy](docs/DEV_WALLET_AND_DEV_DONATE.md)
- [Software architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Screenshots and guide status](docs/MEDIA.md)
- [Security and responsible operation](SECURITY.md)
- [Licensing terms](LICENSE.md)
- [Third-party licenses](THIRD_PARTY_NOTICES.md)
- [Changelog](CHANGELOG.md)
- [Contact and support](SUPPORT.md)

## Downloads

**No v0.4 release is available yet.** The intended destination for approved distributable builds and manuals is [GitHub Releases](https://github.com/I2PS-Engineering/Dual-ISA-RandomX-Lab/releases). Do not treat UI mockups, development ZIPs or placeholder screenshots as production binaries.

XMRig is **not bundled** with this repository's documents. Obtain XMRig only from its [official repository](https://github.com/xmrig/xmrig), respecting GPLv3.

## Legal and rights

Copyright © 2026 **I2PS Solutions**. All rights reserved in I2PS-owned materials.

The I2PS software is licensed under **PolyForm Strict 1.0.0**: noncommercial use is permitted, but the license does not grant permission to redistribute, rebrand, modify, sublicense or commercialize I2PS software. Public GitHub visibility **does not** make this project open source. XMRig has independent GPLv3 rights. See [LICENSE.md](LICENSE.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

The relationship between noncommercial licensing and revenue-generating mining must be reviewed and clearly resolved before public deployment.

## Official I2PS

- Website: https://www.i2psolutions.com
- Engineering: **engineering@i2psolutions.com**
- General: **contact@i2psolutions.com**

**I2PS Engineering — Built in Morocco. Engineered for the future.**
