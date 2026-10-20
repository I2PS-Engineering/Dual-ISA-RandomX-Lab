# ZTM — Zero to Monero: one-command Ubuntu installation

**Current GitHub-hosted engineering build: 0.1.2-alpha3-surgical** (20 October 2026). The application is not a completed or 24-hour-verified production release.

On a fresh **Ubuntu Desktop x86-64**, open Terminal as your normal user and paste this single command (**do not prefix with sudo**):

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/Dual-ISA-RandomX-Lab/296244e5f3861bf5125194ff06bb29c6fa0aa8b2/install-ztm-v3.sh";b=urllib.request.urlopen(u,timeout=30).read();assert hashlib.sha256(b).hexdigest()=="ec836fe9b855cd6b05025851e76e6938b19e8c32087791b655d521ebdd36fe95","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

### Then in the GUI

1. Click **Prepare Linux + Install XMRig**. ZTM displays real APT and XMRig setup output.
2. Under **Benchmark Setup**, CPU threads are **Auto**; the default duration is **24 hours** and can still be changed in this alpha.
3. Pool, TLS connection details, and benchmark payout are embedded in the application, not shown as editable benchmark fields. Benchmark payout goes to the configured I2PS test receiving address. Verify the intended receiving address and consent before mining.
4. Read and tick both authorization checkboxes, then click **Start Real RandomX Benchmark**. No CPU mining should begin until explicit authorization.
5. Open the local results folder when the run ends. The full 24-hour performance and payout flow has **not been independently validated**.

### Verification

- Bootstrap source is pinned to GitHub commit `296244e5f3861bf5125194ff06bb29c6fa0aa8b2` and checked against SHA-256 `ec836fe9b855cd6b05025851e76e6938b19e8c32087791b655d521ebdd36fe95` before execution.
- The pinned bootstrap validates the Ed25519-signed manifest `downloads/latest-ztm-v3.json` using its embedded publisher key, then downloads and SHA-256-checks the package.
- Current ZTM package: `downloads/ZTM-Zero-to-Monero_0.1.2-alpha3-surgical_amd64.deb`, 23,212 bytes, SHA-256 `0fbedd3c8660299d17f2708857e9905654e905a6f76410f2bd428dda464eb800`.
- Repository file hashes and the local signed-manifest check were verified; clean Ubuntu installation and a complete real 24-hour mining run still require physical-machine testing.

**Compatibility:** Ubuntu Desktop x86-64; not Windows/macOS. After an Ubuntu migration, use the same command. This is an engineering alpha.
