# Installing ZTM-SRP1V2

## New V2 RC1 installation (test build)

**This is the new V2 test build, not the existing public stable release.** It includes CPU-aware randomized thread testing, recognized XMRig cleanup before preparation/benchmark/mining, huge-page verification and removal of the upper Ubuntu upgrade checkbox. Both 24-hour benchmark consent checkboxes remain required.

**Step 1:** Stop the current benchmark normally, then reboot Ubuntu. Open Terminal with **Ctrl+Alt+T**.

**Step 2:** Copy the **entire command** below using the code block's copy button, paste it into Terminal and press Enter:

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/release/ztm-srp1v2-rc1/install-ztm-srp1v2-rc1.sh";b=urllib.request.urlopen(u,timeout=60).read();assert hashlib.sha256(b).hexdigest()=="5cff3d3747a8d60ac8c20a83bb4a0ae4ed99112dbd3cb58d8a9a9c684a7fdba6","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

The command verifies the installer SHA-256; the installer verifies the RC1 Debian package SHA-256, size and version before installation and starts ZTM. If an existing recognized XMRig process is still running, the installer refuses to interrupt it. Installation alone does not start a benchmark or mining without consent.

- [RC1 release and Debian package](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V2-RC1)
- [Standalone copy/paste instructions](https://github.com/I2PS-Engineering/ZTM_Benchmark/blob/release/ztm-srp1v2-rc1/INSTALL_RC1.txt)
- [Passing clean Ubuntu installation test](https://github.com/I2PS-Engineering/ZTM_Benchmark/actions/runs/39895089031)

**RC1 validation status:** clean Ubuntu install and GUI smoke tests passed; real 24-hour hardware performance and physical privileged miner isolation on Worker 14 are still awaiting verification. Do not distribute RC1 as the public stable version yet.

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
