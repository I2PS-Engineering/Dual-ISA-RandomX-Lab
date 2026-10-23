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

### New V2 improvements — RC2 corrected test release

**ZTM-SRP1V2-RC2 is the corrected V2 test release for Worker 14. RC1 contained a startup optimizer crash; use RC2 instead.** The original public stable SRP1V2 remains available below.

**Step 1 — Reboot:** Stop any running benchmark normally and reboot Ubuntu. Open Terminal with **Ctrl+Alt+T**.

**Step 2 — Install:** Copy this entire checked command from the box, paste into Terminal and press **Enter**:

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/release/ztm-srp1v2-rc2/install-ztm-srp1v2-rc2.sh";b=urllib.request.urlopen(u,timeout=60).read();assert hashlib.sha256(b).hexdigest()=="9959b55d42f0b5b64068c7445c6db6739f32c21c8498795394f0ccdec3d4efbc","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

The installer checks SHA-256 and Debian version. When installation finishes, ZTM performs the same **mandatory privileged XMRig cleanup before the GUI appears** that it performs on every later desktop launch. It checks recognized XMRig executables belonging to all local users, stops them with authorized privileges and verifies they are gone; if a recognized miner remains or restarts, or authorization is denied, **the GUI will not launch**. The two separate 24-hour mining-consent checkboxes remain mandatory.

The RC2 build also fixes `UnboundLocalError: candidate_profiles` at benchmark start. It retains CPU-aware randomized thread candidates, huge-page checks and additional XMRig checks during preparation, Start Benchmark, Start Mining, and privileged mining launch.

- [RC2 GitHub pre-release / Debian package](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V2-RC2)
- [Same RC2 command as a standalone text file](https://github.com/I2PS-Engineering/ZTM_Benchmark/blob/release/ztm-srp1v2-rc2/INSTALL_RC2.txt)
- [Successful full copy-paste install test](https://github.com/I2PS-Engineering/ZTM_Benchmark/actions/runs/39897625551)
- [Passed startup-crash and actual XMRig termination regression tests](https://github.com/I2PS-Engineering/ZTM_Benchmark/actions/runs/39897333431)

**Release gate:** RC2 is a test build, not the public stable release. Its full 24-hour RandomX result and physical Worker 14 performance have not yet been validated. Process detection is restricted to recognized XMRig executables; unknown or deliberately renamed miners cannot be guaranteed.

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
