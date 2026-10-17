# Installation overview

There are two audience paths:

1. [Already using Linux](EXISTING_LINUX.md) — retain the existing OS and use the I2PS setup script.
2. [Migrating from Windows to Ubuntu](WINDOWS_TO_UBUNTU.md) — install Ubuntu from official media first, then follow the same Linux setup steps.

## Intended beginner experience (v0.4, not yet released)

Open the I2PS application → guided dependency checking → user confirms installation of missing prerequisites and independently licensed XMRig → the authorization screen explains 24-hour online mining and the Dev Wallet payout → user acknowledges terms and explicitly starts the run → results after **at least 24 completed hours** → user wallet education and address entry → separately authorized personal mining.

**No offline benchmark is available** in the intended v0.4 product.

The first-run auto-redirect and online 24-hour controller are still under development. The existing development build cannot perform the full sequence described above.

## Current development build instructions (v0.3.1 only)

For approved local testing on **Ubuntu/Debian x86-64**, obtain the privately reviewed application package, extract it, and from its `dual_isa_randomx_lab` directory run:

```bash
bash install_i2ps_linux.sh --plan
bash install_i2ps_linux.sh
```

This is **not** a public v0.4 download or a v0.4 online benchmark. If the development server does not open your browser, visit `http://127.0.0.1:8765`. The current script is not a general Linux distribution installer.

For verified public downloads, monitor the [GitHub Releases page](https://github.com/I2PS-Engineering/Dual-ISA-RandomX-Lab/releases). Do not assume the downloadable application is available until a reviewed release is published.
