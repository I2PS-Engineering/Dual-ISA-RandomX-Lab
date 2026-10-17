# I2PS Dual-ISA RandomX Lab: GitHub stable-release installation

**User-friendly distribution design | GitHub scripts implemented | No approved public binary application release yet (17 October 2026).**

The latest software is downloaded from the **official I2PS Engineering GitHub Releases**, not random source-code archives. Both Linux entry paths use the same version checker and installer. **No offline benchmark is available in the planned v0.4 architecture.** The presently available local v0.3.x development build is *not* v0.4.

## Path A - Linux is already installed

1. On an Ubuntu/Debian computer, open Terminal. You do **not** reinstall Linux, format drives, or touch existing XMRig installations.
2. Download the official bootstrap into a file (rather than running an unseen remote command):

   ```bash
   curl -fL --proto '=https' --tlsv1.2 -o install_from_github.sh \
     https://raw.githubusercontent.com/I2PS-Engineering/Dual-ISA-RandomX-Lab/main/install_from_github.sh
   ```

3. Preview the operations without downloading or modifying anything:

   ```bash
   bash install_from_github.sh --plan
   ```

4. When a reviewed and approved stable application ZIP has been published, run:

   ```bash
   bash install_from_github.sh
   ```

   This checks prerequisites, downloads the official release-checking script, selects a Linux CPU build, checks `SHA256SUMS.txt`, rejects unsafe archive contents, and installs to `~/.local/share/i2ps-randomx-lab/current`. Previous application files are retained in `previous` for manual recovery. Local benchmark data and existing app-local XMRig are preserved.

5. Agree to open the setup assistant; after installation, it confirms requirements and provides the existing verified XMRig installer. Read the I2PS terms. **No mining begins during installation or update.** The currently tested v0.3.x setup assistant still requires explicit approval to download XMRig; the automatic v0.4 first-launch wizard is not yet implemented.

## Path B - Migrating from Windows to Ubuntu

1. Back up all files outside the operating-system installation process. Download the current Ubuntu Desktop installer from <https://ubuntu.com/download/desktop>.
2. Prepare a USB installer using official Ubuntu instructions, boot it, and carefully choose the partition/disk option. **The Ubuntu installer can erase existing data.** I2PS does not replace your OS automatically.
3. Complete Ubuntu's installation, connect to the internet, and install OS updates through Ubuntu Settings or the Software Updater.
4. Open **Terminal in Ubuntu** and follow *Path A*, using the exact same `install_from_github.sh` commands. No separate I2PS download package is necessary.

## Updates after installation

The app dashboard now provides a **CHECK GITHUB UPDATES** control and checks stable-release availability after you accept the license. It reads GitHub metadata **only**: it never automatically downloads, executes or mines. To upgrade, **stop mining and close the application**, then repeat `bash install_from_github.sh` (or run the already-installed `python3 github_updates.py --check` and `--install`). The previous install is retained under `~/.local/share/i2ps-randomx-lab/previous`.

Advanced commands:

```bash
bash install_from_github.sh --check      # official stable-release metadata only
bash install_from_github.sh --no-launch # download/verify/install without opening dashboard
python3 github_updates.py --check       # checker shipped with app
python3 github_updates.py --install     # install after user approval
```

`--yes` skips only the installer confirmation and **never** accepts I2PS licensing or online mining consent. Automatic updates do not force-mine or silently change the user's wallet.

## Release signing and verification model

The installer requires a published **stable GitHub Release** containing one platform-specific I2PS ZIP and the release's `SHA256SUMS.txt`, with a matching SHA-256 digest. It refuses unknown assets, incorrect architectures, invalid archives, symlinks, traversal paths and mismatched hashes. Hashes hosted in the same GitHub release detect tampering/corruption in transit, but are not an independent publisher signature. A separately published signature can be added to a later release process.

Expected future asset names:

- `I2PS-Dual-ISA-RandomX-Lab-linux-x86_64.zip`
- `I2PS-Dual-ISA-RandomX-Lab-linux-aarch64.zip` (only if a compatible tested build is approved)
- `SHA256SUMS.txt`

Archives must contain one `dual_isa_randomx_lab/` folder with the app, including `server.py`, `LICENSE.md`, the Linux setup script, the official logo, and user guide. Do not publish the private source-bearing development ZIP as a binary-only production release. The official **XMRig** engine is **separate GPLv3 software**, fetched and verified by the app's setup tool, not smuggled into proprietary software licensing.

## Online benchmark and wallet guidance

The intended v0.4 first-run flow is: setup -> full terms and the two authorization acknowledgments -> **24 continuous hours of real online RandomX CPU work, initial mining rewards to Dev Wallet** -> measured performance report -> optional entry of **only the user's public Monero receiving address** -> personal mining with clearly disclosed built-in Dev Donate. No private spend/view keys, passwords or seeds are requested. Stop controls remain necessary. **The 24-hour mining engine and Dev Donate schedule are not implemented yet.**

Monero wallet information: <https://www.getmonero.org/downloads/> and <https://www.getmonero.org/resources/user-guides/>.

**Project:** <https://github.com/I2PS-Engineering/Dual-ISA-RandomX-Lab>  
**Engineering:** engineering@i2psolutions.com  
**License:** I2PS-owned software free for noncommercial use under PolyForm Strict 1.0.0; not open source. XMRig is under GPLv3.