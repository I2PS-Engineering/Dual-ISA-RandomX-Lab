# Installing ZTM-SRP1V2

## New V2 RC3 installation — controlled test build

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
