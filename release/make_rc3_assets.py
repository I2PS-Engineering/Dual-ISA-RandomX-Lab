#!/usr/bin/env python3
"""Create checksum-pinned RC3 release assets from CI-built V2-only Debian."""
from pathlib import Path
import hashlib,sys
if len(sys.argv)!=2:raise SystemExit("usage: make_rc3_assets.py <candidate.deb>")
pkg=Path(sys.argv[1]);data=pkg.read_bytes();sha=hashlib.sha256(data).hexdigest();size=len(data)
assert size>40000
assert pkg.name=="ZTM-SRP1V2-RC3_amd64.deb"
url="https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/release/ztm-srp1v2-rc3/dist/ZTM-SRP1V2-RC3_amd64.deb"
script="""#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || { echo "Ubuntu x86-64 required"; exit 1; }
[[ "$(id -u)" -ne 0 ]] || { echo "Launch as an ordinary Ubuntu desktop user"; exit 1; }
. /etc/os-release
[[ "$ID" == ubuntu ]] || { echo "Ubuntu required"; exit 1; }
for cmd in python3 sha256sum stat dpkg-deb sudo apt-get;do command -v "$cmd" >/dev/null || { echo "Missing $cmd"; exit 1; };done
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pkg="$work/ZTM-SRP1V2-RC3_amd64.deb"
python3 - "$pkg" <<'PYDOWNLOAD'
import pathlib,sys,urllib.request
url='PACKAGE_URL'
pathlib.Path(sys.argv[1]).write_bytes(urllib.request.urlopen(url,timeout=60).read())
PYDOWNLOAD
echo "PKG_SHA  $pkg" | sha256sum -c -
[[ "$(stat -c %s "$pkg")" == PKG_BYTES ]] || exit 1
[[ "$(dpkg-deb -f "$pkg" Version)" == '1.2.3~srp1v2rc3' ]] || exit 1
sudo apt-get install -y "$pkg"
dpkg -s ztm-zero-to-monero | grep -q '^Version: 1.2.3~srp1v2rc3$'
command -v pkexec >/dev/null || { echo 'Missing pkexec after installation'; exit 1; }
echo 'ZTM-SRP1V2-RC3 installed; launching with pre-GUI XMRig cleanup...'
nohup /usr/bin/ztm >/tmp/ztm-rc3-launch.log 2>&1 &
""".replace("PACKAGE_URL",url).replace("PKG_SHA",sha).replace("PKG_BYTES",str(size))
Path('install-ztm-srp1v2-rc3.sh').write_text(script)
insthash=hashlib.sha256(script.encode()).hexdigest()
command=("python3 -c 'import hashlib,subprocess,urllib.request;"+
    'u="https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/release/ztm-srp1v2-rc3/install-ztm-srp1v2-rc3.sh";'+
    'b=urllib.request.urlopen(u,timeout=60).read();'+
    f'assert hashlib.sha256(b).hexdigest()=="{insthash}","SECURITY STOP: installer checksum mismatch";'+
    'subprocess.run(["bash","-s"],input=b,check=True)' + "'")
Path('INSTALL_RC3.txt').write_text('ZTM-SRP1V2-RC3 — V2-only Ubuntu x86-64 test build\n\nStep 1 — Stop the current benchmark and reboot Ubuntu.\nStep 2 — Open Terminal (Ctrl+Alt+T), copy and paste this entire command:\n\n'+command+'\n')
Path('SHA256SUMS_RC3.txt').write_text(sha+'  dist/ZTM-SRP1V2-RC3_amd64.deb\n'+insthash+'  install-ztm-srp1v2-rc3.sh\n')
Path('RELEASE_RC3_NOTES.md').write_text("""# ZTM-SRP1V2-RC3 — V2-only deterministic profile optimization
**Pre-release / test build**, derived from SHA-256-pinned official RC2. The public stable V2 and V3 remain untouched.

- Up to **11 total profiles**: automatic XMRig baseline and up to 10 deterministic CPU/cache/RAM-informed alternatives.
- **300 seconds measured per profile**, excluding readiness and stabilization.
- Before the next profile: confirmed guardian shutdown, authorized XMRig cleanup, five-second interval, and repeat check. Fail closed on a persistent/restarting miner.
- Live GUI beside hashrate: current profile X/Y, active threads, dataset initialization threads, elapsed/target test time.
- Retains RC2's pre-GUI cleanup, crash fix, 24-hour consent, wallet and huge-page behavior.
- Memory type may be unknown when Linux hardware/kernel EDAC does not expose it.
- CI and virtual GUI validation do not establish 24-hour Worker 14 performance.
""")
print('PACKAGE_SHA256',sha,'PACKAGE_BYTES',size,'INSTALLER_SHA256',insthash)
