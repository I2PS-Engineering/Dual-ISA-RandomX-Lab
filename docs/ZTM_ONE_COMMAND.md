# ZTM — One-command GitHub installation (Ubuntu Desktop x86-64)
**Current published engineering alpha: 0.1.1-alpha2, including the Wallet tab. Published 20 October 2026.**

From a **fresh Ubuntu Desktop x86-64** installation, open Terminal as your normal user (do not prefix the command with sudo), paste **this single command**, and press Enter:

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/Dual-ISA-RandomX-Lab/88b10f0c9bc6587ea5fbcfc275d5728c3cba3ef3/install-ztm-v2.sh";b=urllib.request.urlopen(u,timeout=30).read();assert hashlib.sha256(b).hexdigest()=="339d241363a7d5f7b518c7094d7feec5ed4f9e4e090762973ece768b5501518c", "SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

No separate manual file download is needed. The single command authenticates the installer against a fixed SHA-256 and immutable GitHub commit, downloads the signed current alpha manifest, verifies its Ed25519 signature, obtains and checks the exact Ubuntu `.deb`, installs the ZTM application and starts the GUI.

## What the user sees next

1. In the launched ZTM GUI click **PREPARE LINUX + INSTALL XMRIG**. This visibly runs the required APT setup and downloads a SHA-256-pinned official XMRig 6.26.0 package.
2. On the **Wallet** tab choose **Existing Wallet** (public receiving address) or **Create Wallet** (opens the official Monero GUI; it must be installed separately). The official wallet software handles local encryption/password and private keys; ZTM does not.
3. Enter the pool and TLS settings, choose CPU threads and diagnostic duration, read and check the two alpha-test authorizations, then explicitly select **START REAL RANDOMX BENCHMARK**. Results appear in the GUI and are saved to `~/ZTM-Results`.

**Installation never starts mining automatically.** The actual mining test requires a pool, public address, and distinct informed user consent. The operator's wallet receives this alpha test's rewards; this is NOT the production v0.4 first-24-hour Dev Wallet flow.

## Authenticity controls

- The one-command bootstrap is pinned to GitHub commit `88b10f0c9bc6587ea5fbcfc275d5728c3cba3ef3` and SHA-256 `339d241363a7d5f7b518c7094d7feec5ed4f9e4e090762973ece768b5501518c`.
- Inside the script, the mutable current-alpha manifest is verified against an embedded **Ed25519 engineering-alpha public key**, before any package is installed.
- The `.deb` filename, expected version, architecture, exact byte count and SHA-256 are checked against the signed manifest; the install stops if any verification fails.
- This is a development signing key generated for the alpha; I2PS must replace/assume custody of a production signing key and pin a corresponding reviewed installer before public production distribution.
- These mechanisms reduce substitution/tampering risks; they do **not** establish immunity to malware, stolen signing keys, vulnerable dependencies or compromised machines.

## Verification performed before publication

- Signed alpha2 manifest verified using the matching local Ed25519 public key.
- GitHub Git-blob hashes for installer, manifest, signature and actual `.deb` match the locally generated files.
- Non-root simulated installation workflow succeeded, including signature, checksum, dpkg metadata and launcher flow, without changing system packages.
- Deliberate signature tampering was rejected.
- Wallet UI tests: 17 passed in the prior local alpha2 suite.
- **Not yet verified**: installation and XMRig provisioning on a separate clean Ubuntu computer, an accepted live mining share, or a continuous 24-hour benchmark.

This is a GitHub-hosted **engineering alpha package**, not a finished v0.4 production benchmark. The binary is published under `downloads/`, not GitHub Releases.
