# Existing Linux users - direct installation from GitHub

**Keep your current operating system.** No reinstall, reformatting or miner reconfiguration.

The user-friendly public distribution route uses the official GitHub bootstrap, rather than downloading an old development ZIP. On supported Ubuntu/Debian, open Terminal:

```bash
curl -fL --proto '=https' --tlsv1.2 -o install_from_github.sh https://raw.githubusercontent.com/I2PS-Engineering/Dual-ISA-RandomX-Lab/main/install_from_github.sh
bash install_from_github.sh --plan
# When an approved stable app release is available:
bash install_from_github.sh
```

The tool checks release availability and platform compatibility, verifies SHA-256, preserves local data and the previous installation, and asks before opening the app. It will not mine or silently install a random GitHub commit.

To check for releases without installing: `bash install_from_github.sh --check`.

**Current status:** The installer/checker is published and the app's local update-check UI has been tested. No approved stable binary I2PS application Release has been published. The intended v0.4 online-only 24-hour benchmark and first-launch automatic dependency wizard are not implemented yet.

The older `install_i2ps_linux.sh` script belongs to the privately tested v0.3.x development package; once a stable package ships, it can be run from the downloaded app to prepare separately licensed and verified XMRig, after consent.

See [complete GitHub installation/updates guide](GITHUB_INSTALLATION.md), [Windows-to-Ubuntu instructions](WINDOWS_TO_UBUNTU.md), and [release status](STATUS.md).
