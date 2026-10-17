# Installation overview: GitHub delivery

The **same official GitHub installer** serves two audiences:

1. [Already using Linux](EXISTING_LINUX.md): leave Linux installed, open Terminal, download the GitHub bootstrap, preview and run it.
2. [Migrating from Windows to Ubuntu](WINDOWS_TO_UBUNTU.md): back up data and install Ubuntu first, then follow the **identical** Terminal procedure.

Detailed instructions: [GITHUB_INSTALLATION.md](GITHUB_INSTALLATION.md).

## Beginner's three commands

```bash
curl -fL --proto '=https' --tlsv1.2 -o install_from_github.sh https://raw.githubusercontent.com/I2PS-Engineering/Dual-ISA-RandomX-Lab/main/install_from_github.sh
bash install_from_github.sh --plan
bash install_from_github.sh
```

The final command installs nothing until a reviewed **stable GitHub Release** exists with a compatible ZIP and `SHA256SUMS.txt`. Check safely using `bash install_from_github.sh --check`.

When an approved Release becomes available, installation checks architecture, verifies the checksum and ZIP safety, saves the previous install and local results, then asks whether to open the app. Inside the app, users separately accept the license and approve installation of XMRig. None of these operations starts online mining.

The intended **v0.4 online-only** benchmark workflow is setup -> two consent acknowledgments and prominent Dev Wallet notice -> 24 continuous hours of actual online RandomX CPU work -> results -> personal public Monero wallet -> explicitly authorized mining. **No offline benchmark is available** in v0.4. This runtime **has not yet been implemented**. v0.3.x contains a legacy offline prototype only.

The official GUI can check stable-release availability without performing an update. Exit the application before running the installer to update.
