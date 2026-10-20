# ZTM — One-command Ubuntu Desktop installer

**Latest published signed engineering release: ZTM 0.1.2-alpha3-surgical (20 October 2026).**
This is the alpha2 UI with only the requested benchmark setup changes: HashVault pool, configured receiving address and TLS internal to the application, CPU Threads Auto, 24-hour default duration (still adjustable), and the two authorization checkboxes retained.

## Step 1 — Install directly from GitHub

On Ubuntu Desktop **x86-64**, open Terminal **as your ordinary user** (do not add sudo to this command). Copy and paste this one line:

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/Dual-ISA-RandomX-Lab/83a0e08bb82c39125bac4c49c9e8b062f21c4e2f/install-ztm-v3.sh";b=urllib.request.urlopen(u,timeout=30).read();assert hashlib.sha256(b).hexdigest()=="ec836fe9b855cd6b05025851e76e6938b19e8c32087791b655d521ebdd36fe95", "SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

No ZIP or manually downloaded .deb is required. The pinned immutable GitHub bootstrap is checked against the SHA-256 above before execution. The bootstrap installs curl/openssl dependencies using apt as needed, retrieves the signed alpha3 manifest, verifies its Ed25519 signature and the Debian package size/SHA-256, installs the .deb, and starts ZTM. Ubuntu will ask for your administrative password when needed. Installation does **not** silently start mining.

## Step 2 — Prepare benchmarking

In the **original ZTM GUI**, click **PREPARE LINUX + INSTALL XMRIG** and watch the integrated live terminal until preparation succeeds.

## Step 3 — Start the real benchmark

The pool endpoint, payout address, and TLS mode are embedded in the benchmark controller and are not editable fields. CPU Threads is **Auto**. Duration defaults to **1440 minutes (24 hours)** but remains selectable in this engineering alpha. Review both existing CPU mining and Dev Wallet acknowledgment checkboxes, check them, then click **START REAL RANDOMX BENCHMARK**. Mining is real CPU work with electricity and thermal load; **STOP** remains available.

## Step 4 — Results

Results appear in `~/ZTM-Results`.

## Security and release status

- [Installer source](../install-ztm-v3.sh)
- [Signed release manifest](../downloads/latest-ztm-v3.json)
- [Detached signature](../downloads/latest-ztm-v3.sig)
- [Pinned public verification key](../downloads/ztm-v3-public.pem)
- [Ubuntu x86-64 .deb](../downloads/ZTM-Zero-to-Monero_0.1.2-alpha3-surgical_amd64.deb)
- Built package SHA-256: `0fbedd3c8660299d17f2708857e9905654e905a6f76410f2bd428dda464eb800`.
- Original alpha2's prior installer remains unchanged for reproducibility, but this page points to the new signed alpha3.
- **Not validated yet:** installation on the user's clean Ubuntu hardware; any live accepted pool share; uninterrupted 24-hour benchmarking; independent ownership confirmation of the embedded payout address.
- The engineering-alpha signing key is provisional; a production release requires an I2PS-controlled signing key and further testing.
