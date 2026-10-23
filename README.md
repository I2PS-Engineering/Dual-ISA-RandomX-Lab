# ZTM — Zero to Monero

**Current stable release: ZTM-SRP1V2 — Stable Release V1.2**

**I2PS Engineering** · Built in Morocco. Engineered for the Future.

ZTM is an Ubuntu Desktop application that benchmarks real Monero RandomX performance on the user's physical CPU, tests CPU thread configurations, records real pool activity, and carries the verified result into the personal-mining workflow.

ZTM does not simulate mining.

## Stable release

ZTM-SRP1V2 is the current supported release for **Ubuntu Desktop x86-64**.

The stable benchmark is intentionally fixed:

- **24 hours only** — there is no duration selector.
- **CPU Threads: Auto** — ZTM evaluates the supported thread profiles automatically.
- Real RandomX work is executed through a separately licensed, verified XMRig installation.
- The benchmark uses a real mining-pool connection.
- Accepted/rejected shares, hashrate and tested profiles are recorded.
- Wallet and Mining remain gated until a qualifying uninterrupted 24-hour pool-verified benchmark completes.
- Only a **public Monero receiving address** is required for personal mining. ZTM never asks for a seed phrase, wallet password, private spend key or private view key.
- Ubuntu administrator authorization is requested once per open ZTM session for the privileged preparation operations. ZTM does not store the administrator password.
- A visible **Stop** control remains available during CPU work.

The benchmark authorization contains the two approved acknowledgements:

1. **I authorize real CPU work for 24 hours, including electricity use and heat.**
2. **I understand this online benchmark uses both XMRig and I2PS dev contribution.**

## Install

### New V2 improvements — RC3 deterministic optimizer test release

**ZTM-SRP1V2-RC3 is the latest controlled V2 test build.** It replaces the older RC2 test instructions above the existing public stable release; **V3 is unchanged**.

**Step 1 — Reboot:** Stop the current benchmark normally, reboot Ubuntu, and open Terminal with **Ctrl+Alt+T**.

**Step 2 — Install RC3:** Copy the entire command from this block and paste it into Terminal:

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/release/ztm-srp1v2-rc3/install-ztm-srp1v2-rc3.sh";b=urllib.request.urlopen(u,timeout=60).read();assert hashlib.sha256(b).hexdigest()=="5508b8976206fa90e883d270efd42ab6c64b33d52a0a4cab14c89ef575c0c1c2","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

The command verifies the installer SHA-256, and the installer verifies the RC3 Debian package SHA-256, size and package version. Installation then launches the existing ZTM application shortcut with mandatory authorized XMRig cleanup **before the GUI appears**. It refuses startup if recognized miners persist or restart.

**RC3 V2-only improvements:** one automatic reference plus at most ten distinct CPU/cache/RAM-ranked alternatives (11 total); **five full measured minutes per configuration**; **five seconds between profile transitions**, with stop verification and two mining-process checks; and a live GUI readout showing active threads, dataset initialization threads, profile number and elapsed/target measurement time beside the hashrate. The two 24-hour authorization checkboxes, initial development contribution, wallet rules and 24-hour-only benchmark requirement remain in place.

- [ZTM-SRP1V2-RC3 GitHub pre-release](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V2-RC3)
- [Standalone RC3 install instructions](https://github.com/I2PS-Engineering/ZTM_Benchmark/blob/release/ztm-srp1v2-rc3/INSTALL_RC3.txt)
- [Passing build and 44 GUI/unit acceptance tests](https://github.com/I2PS-Engineering/ZTM_Benchmark/actions/runs/39909678446)
- [Passing clean-Ubuntu exact copy/paste installation test](https://github.com/I2PS-Engineering/ZTM_Benchmark/actions/runs/39909815681)

**Validation scope:** RC3 is an Ubuntu-tested pre-release; the complete 24-hour Worker 14 RandomX run, real hashrate and all physical privileged lifecycle transitions remain to be verified. Unknown or renamed miners are not guaranteed to be recognized.

### Existing public stable release — SRP1V2

**[Download the one-README installation ZIP](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V2/ZTM-SRP1V2_Linux_One_Command_README.zip)** — unzip, open README.txt, copy and paste its command.

Official release:

**[ZTM-SRP1V2 — Stable Release V1.2](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V2)**

Run the verified one-command installer as your normal Ubuntu desktop user:

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/main/install-ztm-srp1v2.sh";b=urllib.request.urlopen(u,timeout=60).read();assert hashlib.sha256(b).hexdigest()=="10e308155184646a6dd51ec3001e46bead4947139ed79e77378604e7156cb8ec","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

The installer downloads the stable Debian package, verifies its exact size, SHA-256, package name, architecture and Debian version before installation.

### Stable package

- Package: `ZTM-SRP1V2_amd64.deb`
- Debian version: `1.2.0~srp1v2`
- Architecture: `amd64`
- SHA-256: `3b7f64101ea1f4b5239e85cb4b2b584ee7a19cf78ae82b112e9f4a19d53e3a1a`
- Size: `47,222` bytes

## Readable GUI and winning configuration

The Linux GUI starts at **screen-adaptive text zoom**, with live **A− / A+** zoom controls (85–200%). Text, buttons, checkboxes and terminal output now scale as interface elements instead of only enlarging the window.

After a qualifying 24-hour run, **Winning Configuration** reports the selected active threads, winning tested profile, optimization score, sustained mean/median, highest recorded hashrate, profile peak, share counts, elapsed time, and saved JSON results. An instantaneous peak is distinguished from sustained performance.

Worker ID: **`ZTM-SRP1V2`**.

## What happens during the benchmark

ZTM prepares the supported Ubuntu environment and verified XMRig, then starts one 24-hour RandomX benchmark after both acknowledgements are checked.

The optimizer evaluates the supported CPU thread profiles and selects the strongest **tested** profile based on measured behavior. ZTM reports sustained performance rather than treating one short hashrate spike as the result.

A benchmark that is stopped or otherwise fails to complete the qualifying 24-hour run does not unlock the qualified personal-mining workflow.

## Wallet and personal mining

After a qualifying benchmark, the user can enter a **public Monero receiving address** and use the tested CPU configuration for personal mining.

ZTM does not create, request, store or recover private wallet secrets. Wallet creation and recovery remain the responsibility of the user's wallet software.

## Release verification

The SRP1V2 package was built with guarded stable-release changes and checked for:

- fixed 24-hour duration in both GUI and engine;
- rejection of a shorter 60-minute engine run;
- fixed CPU Threads: Auto workflow;
- approved authorization wording;
- removal of the old duration selector and extra Dev Wallet explanatory line;
- screen-detected initial zoom and adjustable font scaling;
- desktop launcher and official ZTM icon;
- rig identification `ZTM-SRP1V2`;
- preserved optimizer, Wallet, Mining, eligibility, donation and shutdown behavior;
- winning-configuration JSON and completion UI;
- package identity and SHA-256 integrity.

Real hashrate remains hardware-dependent. A 24-hour run measures the specific machine being tested; ZTM does not promise a universal hashrate or profitability.

## Documentation

- [Installation](docs/INSTALLATION.md)
- [User guide](docs/USER_GUIDE.md)
- [24-hour online benchmark](docs/ONLINE_BENCHMARK.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Monero wallet safety](docs/MONERO_WALLET_GUIDE.md)
- [Developer contribution](docs/DEV_WALLET_AND_DEV_DONATE.md)
- [FAQ](docs/FAQ.md)
- [Release notes](docs/ZTM_SRP1V1_RELEASE_NOTES.md)
- [Security policy](SECURITY.md)
- [Support](SUPPORT.md)
- [Contributing / feedback](CONTRIBUTING.md)
- [License](LICENSE.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)
- [Changelog](CHANGELOG.md)

## License

I2PS-owned ZTM software and artwork are distributed under **PolyForm Strict License 1.0.0**. The software is free for permitted noncommercial use under those terms and is **not open source**.

XMRig is independent third-party software under **GNU GPL-3.0**. Its licensing and developer contribution remain separate from I2PS-owned ZTM software.

See [LICENSE.md](LICENSE.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Contact

**I2PS Engineering / I2PS Solutions**

- Website: https://www.i2psolutions.com
- Engineering and technical support: **engineering@i2psolutions.com**
- General inquiries: **contact@i2psolutions.com**

**ZTM — Zero to Monero**  
**Built in Morocco. Engineered for the Future.**
