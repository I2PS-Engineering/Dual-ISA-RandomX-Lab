# Existing Linux users — keep your OS

**First automated development target:** Ubuntu/Debian x86-64. Other distributions and Linux ARM64 do not yet have the same verified one-command route.

## Planned public v0.4 path

1. Download an approved I2PS release from GitHub Releases.
2. Extract the official application package.
3. Launch the app and follow its proposed first-run Setup Assistant.
4. After the user approves setup, the app checks Python, system utilities and downloads/verifies a compatible official XMRig build when needed.
5. Read the license and authorize online mining. **Installing dependencies alone never starts mining.**

**Status:** v0.4 first-run automation and 24-hour online benchmark are not implemented yet.

## For local development tests of v0.3.1

Run from the extracted `dual_isa_randomx_lab` folder:

```bash
bash install_i2ps_linux.sh --plan
bash install_i2ps_linux.sh
```

Run as a normal user, **not** `sudo bash`. The script can ask for `sudo` when it needs to install missing distribution packages, uses separately verified upstream XMRig, and is designed not to overwrite existing miner configurations.

No OS reinstall, unattended mining, pool change or existing worker reconfiguration is intended. Do not use the old development script as evidence that the v0.4 workflow has shipped.

Official XMRig: https://github.com/xmrig/xmrig/releases
