# ZTM — One-command Ubuntu Desktop installer

**Latest published engineering release: ZTM 0.1.3-alpha4-surgical.**

This is the existing ZTM interface with a surgical backend update only:
- HashVault pool and payout remain internally configured.
- CPU Threads remains **Auto**.
- Duration remains **24 hours by default** and adjustable in this engineering release.
- The two benchmark authorization checkboxes remain.
- Wallet tab, terminal, logo, layout and visual design remain unchanged.
- **Prepare Linux + Install XMRig** now installs `kmod` and `msr-tools`, loads the Linux `msr` module, and the verified XMRig process is elevated through `pkexec` so XMRig can apply its own RandomX MSR preset and huge-page allocation.
- HashVault worker identity is fixed to **ZTM-Zero-to-Monero** using both the pool password field and XMRig `rig-id`.

## One command

Run this as your normal Ubuntu Desktop x86-64 user:

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/Dual-ISA-RandomX-Lab/b636d5d488d72d8ab0f7b79776f320b07866cf16/install-ztm-v4.sh";b=urllib.request.urlopen(u,timeout=30).read();assert hashlib.sha256(b).hexdigest()=="70a9b7371c95f5c50ab314342c24078c4bcbeac18d06a7f72e4de7d71335a1fa","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

The pinned installer downloads the alpha4 Debian package from immutable package commit `166f14e9d2c80cbf6f7664f1be4e55baba8e067e` and verifies:

- package path: `downloads/ZTM-Zero-to-Monero_0.1.3-alpha4-surgical_amd64.deb`
- package size: **23,440 bytes**
- package SHA-256: `27f241dae46c4077abf6a92d1bc46a2084b6e4de730bf6924f2d4ea03e6dc535`
- Debian version: `0.1.3~alpha4surgical1`

After installation, ZTM launches. Mining still does not start until the user explicitly authorizes it in the GUI.

## Worker identity note

HashVault can use the pool password as the worker name, while XMRig also supports a pool-side `rig-id`. This build sets both to `ZTM-Zero-to-Monero`.

If ZTM uses the **same receiving address** as the existing Linux fleet, HashVault will still include it in that wallet's total worker count. The dedicated name makes it visibly separate; a completely separate wallet dashboard requires a separate receiving address.

## Validation status

Local structural and simulated end-to-end testing passed:
- package syntax and metadata verified;
- GUI source differs from alpha3 only in backend preparation steps;
- XMRig test configuration includes huge pages, MSR, and dedicated worker name;
- accepted-share parsing updates the existing GUI counter.

Still requires a real Ubuntu test to confirm the machine reports successful MSR application, non-zero/100% huge pages, the dedicated worker identity on HashVault, and a real accepted share.
