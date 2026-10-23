# Installing ZTM — latest V2 RC4 or stable SRP1V2

## Latest V2 RC4 installation — controlled development prerelease

**ZTM-SRP1V2-RC4 is the newest public V2 test build.** The stable release remains ZTM-SRP1V2. V3 is untouched. Use Ubuntu Desktop x86-64 and install as your normal desktop user, **not root**.

**1. Stop any running benchmark and reboot Ubuntu.** After reboot, open Terminal (**Ctrl+Alt+T**). Do not upgrade during a benchmark.

**2. Copy and paste the complete verified RC4 installation command:**

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/release/ztm-srp1v2-rc4/install-ztm-srp1v2-rc4.sh";b=urllib.request.urlopen(u,timeout=60).read();assert hashlib.sha256(b).hexdigest()=="d009b90e8642e85496618282503d1c27cebf26c255537fc15592d049a7316d60","SECURITY STOP: RC4 installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

This command checks the RC4 installation script SHA-256 before executing it. The installer validates the **published RC4 Debian package** against its pinned SHA-256, exact byte size, package identity, architecture, and version, then installs it and launches ZTM. The RC3 startup miner preflight remains in place, including mandatory authorized XMRig cleanup before GUI startup.

**RC4 verification data:**

| Item | Value |
| --- | --- |
| Package name | `ztm-zero-to-monero` |
| Release asset | `ZTM-SRP1V2-RC4_amd64.deb` |
| Debian version | `1.2.4~srp1v2rc4` |
| Architecture | `amd64` |
| Package size | 121,844 bytes |
| Package SHA-256 | `abd42a5ded115966dc20d761560581f2c6009575f73f433869400183404aa879` |
| Installer SHA-256 | `d009b90e8642e85496618282503d1c27cebf26c255537fc15592d049a7316d60` |

**What RC4 changes:** It tests the original XMRig automatic baseline plus up to six hardware-ranked active-thread alternatives (seven total maximum), allocates **15 measured minutes per profile**, and retains a five-second verified transition between profiles. Live GUI progress shows profile, active/init threads, and elapsed/target time. Existing 24-hour run requirement, two acknowledgements, developer contribution, wallet rules and protected startup remain unchanged.

The count ranking considers detectable CPU/cache/SMT information, but **does not enforce per-miner-thread CPU affinity or NUMA placement**. Machines with fewer than seven distinct thread-count choices will test fewer profiles rather than duplicate candidates. The fifteen-minute window may help observe HashVault variable difficulty, but does not guarantee that pool-side hashrate or VarDiff stabilizes. Physical-worker 24-hour testing remains pending.

Links: [RC4 GitHub prerelease](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V2-RC4) · [RC4 shell installer](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V2-RC4/install-ztm-srp1v2-rc4.sh) · [RC4 checksums](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V2-RC4/SHA256SUMS_RC4.txt) · [Latest successful RC4 build and installer test](https://github.com/I2PS-Engineering/ZTM_Benchmark/actions/runs/39930914536) · [Known limitations](https://github.com/I2PS-Engineering/ZTM_Benchmark/blob/release/ztm-srp1v2-rc4/release/RC4_STATUS.md).

**Earlier controlled builds:** [RC3 archive](https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V2-RC3). Use the RC4 instructions above for the latest test version.

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
