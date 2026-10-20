# ZTM_Benchmark — One-command installation (v0.1.5-alpha6-mining)

**Engineering alpha, 20 October 2026.** The original alpha5 benchmark appearance and existing controls are retained; this release adds the gated Wallet and Mining navigation and personal mining mode.

## Step 1 — Install and launch on Ubuntu Desktop x86-64

Stop any running earlier ZTM mining/benchmark and close that ZTM window first. Open Ubuntu Terminal as your normal desktop user (not sudo), and copy this **single complete command**:

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/0a1054a2f28de7d49ac3c538f789682a6a5a3b40/install-ztm-v6.sh";b=urllib.request.urlopen(u,timeout=30).read();assert hashlib.sha256(b).hexdigest()=="523cfe41db898b4d689a64b99ad5286c896a890d9c534f5f66d8ea43e53ff505","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

The pinned bootstrap verifies its own SHA-256, downloads the GitHub-published package from pinned commit `6d0568aa93631199338cf016b5dc8473b2ab7673` as seven fixed-size transfer fragments, rebuilds the original .deb, checks its SHA-256 and Debian metadata, updates APT, installs the application and opens its GUI. Mining does not start automatically.

**Package SHA-256:** `86262258c70707ad15a4154935175f8394bc3b5d98c4f305b692e90fac4109cd`  
**Package size:** 30,380 bytes.  
**Debian version:** `0.1.5~alpha6mining1`.

## Step 2 — Prepare Linux + XMRig

Click **PREPARE LINUX + INSTALL XMRIG** in the unchanged benchmark page. Its terminal displays the setup and miner output. Pool, payout and TLS remain internal to benchmarking; CPU threads use the existing automatic optimizer and duration defaults to 24 hours in this engineering build.

## Step 3 — Complete the benchmark

Start the authorized online benchmark and allow it to complete **24 uninterrupted hours** with actual accepted shares. ZTM saves a report in `~/ZTM-Results`. Short, cancelled, interrupted or shareless tests do not unlock personal mining. Before eligibility, Wallet and Mining appear grey; clicking either displays the completion requirement without opening the tab. This is enforced in GUI navigation and the personal-mining backend, using a locally stored benchmark report.

## Step 4 — Wallet and Mining

After qualifying completion, open **WALLET**. Choose an existing wallet (enter only the public Monero receiving address) or create one in the official Monero GUI (where password, private keys and recovery seed remain). Select **START MINING** to open the new **MINING** tab. Read **VIEW TERMS**, accept the one Terms & Conditions checkbox and press **START MINING**. **STOP MINING** and application exit end the session.

Personal mining uses HashVault and the selected thread profile. It retains XMRig's native `donate-level: 1` for XMRig developers and uses a separate 60-second I2PS pool interval per 6,000 seconds. Scheduled time does not guarantee a 1% share/revenue fraction; the independent schedules can overlap. Terms are included with the installed application, not repeated as banners throughout the GUI.

## Validation boundary

Local alpha6 eligibility/navigation tests passed and GitHub package bytes were checked against the tested local .deb; these checks are **not** a real 24-hour Ubuntu test. Real physical testing is still needed to verify the completed 24-hour unlock, wallet-to-mining transition, sustained dual donation behavior, correct pool worker attribution, and process termination. The eligibility file is a local report, not cryptographically attested proof.

[Source repository](https://github.com/I2PS-Engineering/ZTM_Benchmark) · [Alpha6 release package fragments](https://github.com/I2PS-Engineering/ZTM_Benchmark/tree/main/downloads) · [Mining integration status](ZTM_ALPHA6_MINING_INTEGRATION_STATUS.md)
