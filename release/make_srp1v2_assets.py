#!/usr/bin/env python3
"""Build pinned installer, single-README ZIP and GitHub release notes from V1.2 .deb."""
from pathlib import Path
import hashlib
import sys
import zipfile

if len(sys.argv) != 3:
    raise SystemExit("usage: make_srp1v2_assets.py <deb-path> <output-folder>")
pkg = Path(sys.argv[1])
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)

expected_name = "ZTM-SRP1V2_amd64.deb"
if pkg.name != expected_name:
    raise SystemExit("Unexpected package name")
data = pkg.read_bytes()
sha = hashlib.sha256(data).hexdigest()
size = len(data)
if not (size > 20000 and len(sha) == 64):
    raise SystemExit("Invalid release package")
if pkg.resolve() != (out / expected_name).resolve():
    (out / expected_name).write_bytes(data)

stable_installer = Path("install-ztm-srp1v1.sh").read_text(encoding="utf-8")
checks = {
    "stable-release tag": stable_installer.count("ZTM-SRP1V1") >= 4,
    "old SHA": stable_installer.count("acd4bee9a502e39a673cbf39679710553fd83720cc261f5915166e8eb1c6dd56") == 1,
    "old size": "EXPECTED_SIZE='45728'" in stable_installer,
    "old version": "EXPECTED_VERSION='1.1.0~srp1v1'" in stable_installer,
}
if not all(checks.values()):
    raise SystemExit("STOP: baseline installer format unexpected: " + str(checks))
installer = (
    stable_installer
    .replace("ZTM-SRP1V1", "ZTM-SRP1V2")
    .replace("ztm-srp1v1", "ztm-srp1v2")
    .replace("acd4bee9a502e39a673cbf39679710553fd83720cc261f5915166e8eb1c6dd56", sha)
    .replace("EXPECTED_SIZE='45728'", f"EXPECTED_SIZE='{size}'")
    .replace("1.1.0~srp1v1", "1.2.0~srp1v2")
)
if "ZTM-SRP1V1" in installer or "ztm-srp1v1" in installer:
    raise SystemExit("STOP: prior installer references remain")
# Same-version rig-ID hotfix must reinstall the existing package.
installer = installer.replace('sudo apt-get install -y "$pkg"', 'sudo apt-get install --reinstall -y "$pkg"')
installer_file = out / "install-ztm-srp1v2.sh"
installer_file.write_text(installer, encoding="utf-8")
installer_file.chmod(0o755)
installer_sha = hashlib.sha256(installer_file.read_bytes()).hexdigest()
command = (
    "python3 -c 'import hashlib,subprocess,urllib.request;"
    'u="https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V2/install-ztm-srp1v2.sh";'
    "b=urllib.request.urlopen(u,timeout=60).read();"
    f'assert hashlib.sha256(b).hexdigest()=="{installer_sha}","SECURITY STOP: installer checksum mismatch";'
    'subprocess.run(["bash","-s"],input=b,check=True)' + "\n"
)
(out / "COPY_PASTE_COMMAND.txt").write_text(command, encoding="utf-8")
(out / "SHA256SUMS.txt").write_text(
    f"{sha}  {expected_name}\n"
    f"{installer_sha}  install-ztm-srp1v2.sh\n",
    encoding="utf-8"
)
readme = (
    "ZTM-SRP1V2 — Linux Readability Update (V1.2)\n"
    "============================================\n\n"
    "1. Stop XMRig and close any previous ZTM session.\n"
    "2. Open Terminal as your ordinary Ubuntu desktop user.\n"
    "3. Copy the following ENTIRE command into Terminal and press Enter:\n\n"
    + command +
    "\nThe installer verifies both installer and Debian package checksums.\n"
    "Initial interface zoom adapts to the screen. Adjust using A− and A+ in the GUI header.\n"
    "New rig ID: ZTM-SRP1V2.\n"
    "After a qualifying 24-hour benchmark, the app displays Winning Configuration\n"
    "with measured peak and sustained performance and selected threads.\n"
    "The 24-hour benchmark rule and automatic optimizer remain in force.\n"
)
with zipfile.ZipFile(out / "ZTM-SRP1V2_Linux_One_Command_README.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("README.txt", readme)
notes = f"""# ZTM-SRP1V2 — Linux Readability Update V1.2

**Current Linux release; worker identification: `ZTM-SRP1V2`.**

Built from the SHA-256-verified ZTM-SRP1V1 Debian baseline.

## Improvements

- Automatic display-aware real GUI font scaling for compact and large screens, including terminal, navigation, consent labels and buttons.
- Instant **A− / A+** controls to adjust text from 125% to 200%, independently of window dimensions.
- Increased button padding and long text wrapping.
- Benchmark pool `pass` and `rig-id` updated to `ZTM-SRP1V2`.
- Personal mining pool identification updated to `ZTM-SRP1V2`.
- **Winning Configuration** automatically displayed upon successful completion of a qualifying 24-hour run, and written to the result JSON. Includes winning active threads, optimization score, peak and sustained hashrates, measured accepted/rejected shares, and tested profile details. Peak and sustained measurements are clearly separated.

## Unchanged behavior

- **24 hours only**, enforced in GUI and engine; no shortened benchmark.
- CPU Threads: Auto and profile optimizer.
- Consent disclosures, initial development contribution, wallet/mining gate, pool verification, and shutdown behavior.
- Native Ubuntu Desktop x86-64 release; no claims of Mac support.

## Package

- `{expected_name}`
- Debian version `1.2.0~srp1v2`
- SHA-256 `{sha}`
- {size} bytes

## Validation

- Unmodified files from SRP1V1 verified byte-for-byte after rebuild.
- Python compiled successfully and engine accepted 24 hours but rejected 60 minutes.
- GUI constructed in virtual Ubuntu 1366 × 768 display; font zoom increased and decreased successfully.
- Debian package metadata, launcher, icon and rig IDs verified.
- Actual 24-hour hardware qualification remains a separate runtime experiment.
"""
(out / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8")
print(f"deb_sha256={sha}")
print(f"deb_bytes={size}")
print(f"installer_sha256={installer_sha}")
print(f"release_dir={out}")
