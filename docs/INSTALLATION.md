# Installing ZTM-SRP1V1

**Stable Release V1.1** supports Ubuntu Desktop on x86-64 systems.

## Before installing

Close any previous ZTM instance and make sure an existing XMRig process is not running:

```bash
pgrep -a -x xmrig
```

No output means no XMRig process is currently running.

Run the installer as your **normal Ubuntu desktop user**, not as root.

## Recommended one-command installation

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V1/install-ztm-srp1v1.sh";b=urllib.request.urlopen(u,timeout=60).read();assert hashlib.sha256(b).hexdigest()=="ec069736a9e683b3e6294a4af066963a0c21ae2d5e835157a483c4c2b31b85ff","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

This verifies the installer before executing it.

The installer then verifies the stable Debian package before installation.

## Manual installation

Release page:

https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V1

Download:

- `ZTM-SRP1V1_amd64.deb`
- `SHA256SUMS.txt`

Expected package SHA-256:

`acd4bee9a502e39a673cbf39679710553fd83720cc261f5915166e8eb1c6dd56`

Install the verified package:

```bash
sudo apt install ./ZTM-SRP1V1_amd64.deb
```

## What installation does

Installation places ZTM and its desktop/application launcher on Ubuntu.

Installation itself does **not** start the benchmark.

Inside ZTM, **Prepare Linux + Install XMRig** performs the supported preparation after explicit authorization.

## First benchmark

The stable benchmark is fixed at:

- Duration: **24 hours**
- CPU Threads: **Auto**

There is no shorter benchmark option in ZTM-SRP1V1.

Read and check both acknowledgements, then select **START 24-HOUR RANDOMX BENCHMARK**.

## Updating

For a future stable release, use the installer published with that release. Do not replace a running ZTM/XMRig process during a benchmark.
