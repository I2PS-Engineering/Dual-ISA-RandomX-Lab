# Installing ZTM-SRP1V2

## New V2 RC2 installation — corrected test build

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
