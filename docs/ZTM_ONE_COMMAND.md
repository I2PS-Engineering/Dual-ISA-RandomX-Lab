# ZTM — One-command GitHub installer (engineering alpha)

**Published 20 October 2026.** The actual ZTM 0.1.0-alpha1 Ubuntu amd64 .deb is checked into this repository under downloads/. It is not yet a GitHub Release or a finished v0.4 24-hour benchmark.

## One terminal command (Ubuntu Desktop x86-64)

Copy and paste this complete line into Ubuntu Terminal. It pins the audited bootstrap to an immutable GitHub commit, verifies that script's SHA-256 before execution, then downloads and checks the **latest signed alpha manifest** and the referenced .deb. It never silently starts mining.

```bash
bash -c 'set -e; f=$(mktemp); trap '\''rm -f "$f"'\'' EXIT; curl -fLsS --proto "=https" --tlsv1.2 -o "$f" "https://raw.githubusercontent.com/I2PS-Engineering/Dual-ISA-RandomX-Lab/8ea1b588bd00fe2eb4894ee8f4e14d88e7870544/install-ztm.sh"; printf "%s  %s\n" "51114d1ee1d7aaa9f39c4e9a6a4ae73807d3482fb6bc46f99f70d838d4aaf14c" "$f" | sha256sum -c -; bash "$f"'
```

Use your ordinary Ubuntu desktop user (do not run the command through sudo). The script checks the operating system, downloads a signed release manifest, validates the Ed25519 signature with its embedded public key, confirms download size and SHA-256, displays a confirmation prompt, uses sudo apt-get for local package installation, and then launches the ZTM GUI.

In ZTM, click **Prepare Linux + Install XMRig**. The GUI displays the actual APT and XMRig installer output. Enter a pool and **public** Monero receiving address and authorize the online test. A full v0.4 24-hour Dev Wallet protocol is not yet implemented by this alpha.

## Dry-run and verification

Safest local inspection: download the same pinned bootstrap manually, verify its SHA-256 and run it with --plan or --verify-only. These modes never install or mine.

## Integrity and update mechanism

- Bootstrap: fixed GitHub commit + fixed SHA-256 included in the command.
- Version selection: mutable downloads/latest-ztm.json from the official repository, paired with downloads/latest-ztm.sig.
- Trust root: Ed25519 public key embedded in the pinned bootstrap. Updating the GitHub repository alone cannot produce an accepted forged manifest without the corresponding private signing key.
- Package: path from signed manifest, exact file length and SHA-256 verified before calling apt-get.
- XMRig: retrieved by the application from the official upstream 6.26.0 source, SHA-256 pinned in its engine.
- The signing key used here is an **engineering-alpha key created for this publication**. Before any production release, I2PS should create, hold and safeguard its own signing key and publish a newly pinned bootstrap.
- These controls substantially reduce tampering and substitution risk but do not guarantee immunity from malicious code, host compromise, stolen signing keys, or upstream vulnerabilities.

## Verification status

Four offline installer tests passed: valid signed package, no-change plan, tampered package rejection and tampered manifest rejection. Public repository tree confirms package and signed manifest. This alpha has **not** completed installation on your clean Ubuntu machine or mined an accepted live pool share; perform the machine test before claiming validated functionality.

## Source of truth

- [Installer source](../install-ztm.sh)
- [Signed latest manifest](../downloads/latest-ztm.json)
- [Signature](../downloads/latest-ztm.sig)
- [Downloaded .deb](../downloads/ZTM-Zero-to-Monero_0.1.0-alpha1_amd64.deb)
