# Installing ZTM — latest V2 RC4.1 or stable SRP1V2

## Latest corrected V2 RC4.1 installation — controlled prerelease

**RC4.1 fixes RC4 displaying Profile 1/4 on four-logical-CPU hardware.** It introduces six different hardware-aware XMRig CPU-affinity configurations plus the original automatic baseline. All seven get 15 measured minutes, followed by the 24-hour winner continuation. It is a development prerelease, not the production stable release; V3 remains untouched.

**1. Stop any benchmark and reboot Ubuntu.** Open Terminal (**Ctrl+Alt+T**) as a normal Ubuntu Desktop x86-64 user, not root.

**2. Copy the following command and paste it into Terminal:**

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V2-RC4.1/install-ztm-srp1v2-rc41.sh";b=urllib.request.urlopen(u,timeout=60).read();assert hashlib.sha256(b).hexdigest()=="6c3685ed78ed2802394702baa7a470528fd5aa5958a18a36c3faab4809372266","SECURITY STOP: RC4.1 installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

The command verifies the installer SHA-256 before executing it. The installer validates the released Debian package's pinned SHA-256, byte count, package name, architecture and version before running `sudo apt-get install` and launching ZTM through its authorized pre-GUI XMRig cleanup.

| Verified RC4.1 item | Value |
| --- | --- |
| Release | `ZTM-SRP1V2-RC4.1` |
| Debian version | `1.2.5~srp1v2rc41` |
| Architecture | `amd64` |
| Package size | `133066` bytes |
| Package SHA-256 | `b1649334daf85d504b0423297dcf4fe6d34bace125fece642c120f6cc7cdd7fa` |
| Installer SHA-256 | `6c3685ed78ed2802394702baa7a470528fd5aa5958a18a36c3faab4809372266` |
| Profiles | One XMRig auto + exactly six different CPU-affinity maps (requires ≥3 permitted logical CPUs) |
| Measurement | 15 minutes per profile, plus separate readiness/warm-up and verified 5-second transitions |
| Overall benchmark | Minimum 24 hours, unchanged |

After the seven profiles, ZTM reuses the **winning CPU-affinity map** rather than only its active-thread count. Original XMRig logging, dual consent, huge-page setup, developer contribution and wallet policy remain unchanged.

**Special cases and limitations:** Fewer than three allowed logical CPUs cannot produce six distinct active affinity subsets, so RC4.1 refuses the seven-profile benchmark instead of faking duplicate results. The GUI/configuration and installer were tested in Ubuntu CI, but live 24-hour HashVault testing remains necessary.

- [RC4.1 official GitHub prerelease](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V2-RC4.1)
- [Exact install instructions file](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V2-RC4.1/INSTALL_RC41.txt)
- [Verified package checksums](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V2-RC4.1/SHA256SUMS_RC41.txt)
- [Passing Ubuntu CI and full public installer test](https://github.com/I2PS-Engineering/ZTM_Benchmark/actions/runs/39933285557)
- [RC4.1 standalone source](https://github.com/I2PS-Engineering/ZTM_Benchmark/tree/release/ztm-srp1v2-rc4-1)

The original [RC4](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V2-RC4) and [RC3](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V2-RC3) are archived test releases, not the latest recommended controlled test.

---

## Existing public stable release

**Stable Release V1.2** supports Ubuntu Desktop on x86-64 systems.

## Before installing

Close any previous ZTM instance and make sure an existing XMRig process is not running:

```bash
pgrep -a -x xmrig
```

No output means no XMRig process is currently running.

Run the installer as your **normal Ubuntu desktop user**, not as root.

## Recommended one-command installation

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/main/install-ztm-srp1v2.sh";b=urllib.request.urlopen(u,timeout=60).read();assert hashlib.sha256(b).hexdigest()=="10e308155184646a6dd51ec3001e46bead4947139ed79e77378604e7156cb8ec","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

This verifies the installer before executing it.

The installer then verifies the stable Debian package before installation.

## One-file README ZIP

Download [ZTM-SRP1V2_Linux_One_Command_README.zip](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V2/ZTM-SRP1V2_Linux_One_Command_README.zip). Extract `README.txt`, then copy the installer command into Terminal.

## Manual installation

Release page:

https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V2

Download:

- `ZTM-SRP1V2_amd64.deb`
- `SHA256SUMS.txt`

Expected package SHA-256:

`3b7f64101ea1f4b5239e85cb4b2b584ee7a19cf78ae82b112e9f4a19d53e3a1a`

Install the verified package:

```bash
sudo apt install ./ZTM-SRP1V2_amd64.deb
```

## What installation does

Installation places ZTM and its desktop/application launcher on Ubuntu.

Installation itself does **not** start the benchmark.

Inside ZTM, **Prepare Linux + Install XMRig** performs the supported preparation after explicit authorization.

## First benchmark

The stable benchmark is fixed at:

- Duration: **24 hours**
- CPU Threads: **Auto**

There is no shorter benchmark option in ZTM-SRP1V2.

Read and check both acknowledgements, then select **START 24-HOUR RANDOMX BENCHMARK**.

## Updating

For a future stable release, use the installer published with that release. Do not replace a running ZTM/XMRig process during a benchmark.
