#!/usr/bin/env python3
"""Emit integrity-pinned release assets from the SAME RC4.1 package CI tested.

Do not rebuild the .deb after this stage. GitHub releases must contain exactly
the tested package. This script never changes prior RC4 or V3 assets.
"""
import hashlib
import pathlib
import sys

if len(sys.argv)!=3:
    raise SystemExit('usage: make_rc41_assets.py <audited-deb> <output-directory>')
package=pathlib.Path(sys.argv[1])
folder=pathlib.Path(sys.argv[2])
folder.mkdir(parents=True,exist_ok=True)
assert package.name=='ZTM-SRP1V2-RC4.1_amd64.deb'
blob=package.read_bytes()
assert len(blob)>100_000 and blob[:8]==b'!<arch>\n', 'Not a valid Debian ar package'
digest=hashlib.sha256(blob).hexdigest()
size=len(blob)
url='https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V2-RC4.1/ZTM-SRP1V2-RC4.1_amd64.deb'
script=r'''#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || { echo "Ubuntu x86-64 required"; exit 1; }
[[ "$(id -u)" -ne 0 ]] || { echo "Run as an ordinary Ubuntu desktop user, not root"; exit 1; }
. /etc/os-release
[[ "$ID" == ubuntu ]] || { echo "Ubuntu required"; exit 1; }
for cmd in python3 sha256sum stat dpkg-deb sudo apt-get; do command -v "$cmd" >/dev/null || { echo "Missing $cmd"; exit 1; }; done
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pkg="$work/ZTM-SRP1V2-RC4.1_amd64.deb"
python3 - "$pkg" <<'PYDOWNLOAD'
import pathlib, sys, urllib.request
url="__URL__"
req=urllib.request.Request(url,headers={"User-Agent":"ZTM-RC41-Verified-Installer"})
with urllib.request.urlopen(req,timeout=120) as response, open(sys.argv[1],"wb") as out:
    while True:
        chunk=response.read(65536)
        if not chunk: break
        out.write(chunk)
PYDOWNLOAD
echo "__DIGEST__  $pkg" | sha256sum -c -
[[ "$(stat -c %s "$pkg")" == __SIZE__ ]] || { echo "RC4.1 package byte-size mismatch"; exit 1; }
[[ "$(dpkg-deb -f "$pkg" Package)" == ztm-zero-to-monero ]] || exit 1
[[ "$(dpkg-deb -f "$pkg" Architecture)" == amd64 ]] || exit 1
[[ "$(dpkg-deb -f "$pkg" Version)" == '1.2.5~srp1v2rc41' ]] || exit 1
sudo apt-get install -y "$pkg"
dpkg -s ztm-zero-to-monero | grep -q '^Version: 1.2.5~srp1v2rc41$'
command -v pkexec >/dev/null || { echo "Missing pkexec after installation"; exit 1; }
echo "ZTM RC4.1 installed. Launching with authorized pre-GUI XMRig cleanup."
nohup /usr/bin/ztm >/tmp/ztm-rc41-launch.log 2>&1 &
'''
script=script.replace('__URL__',url).replace('__DIGEST__',digest).replace('__SIZE__',str(size))
installer=folder/'install-ztm-srp1v2-rc41.sh'
installer.write_text(script)
installer_digest=hashlib.sha256(script.encode()).hexdigest()
command=(
    "python3 -c 'import hashlib,subprocess,urllib.request;"
    "u=\"https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V2-RC4.1/install-ztm-srp1v2-rc41.sh\";"
    "b=urllib.request.urlopen(u,timeout=60).read();"
    f"assert hashlib.sha256(b).hexdigest()==\"{installer_digest}\","
    "\"SECURITY STOP: RC4.1 installer checksum mismatch\";"
    "subprocess.run([\"bash\",\"-s\"],input=b,check=True)'"
)
(folder/'INSTALL_RC41.txt').write_text(
    'ZTM RC4.1 controlled Ubuntu Desktop prerelease — original XMRig auto + six CPU-affinity profiles.\n'
    'Run as ordinary user after stopping any active benchmark and rebooting.\n\n'
    +command+'\n'
)
(folder/'SHA256SUMS_RC41.txt').write_text(
    f'{digest}  {package.name}\n'
    f'{installer_digest}  {installer.name}\n'
)
(folder/'RELEASE_RC41_NOTES.md').write_text(
    '''# ZTM-SRP1V2-RC4.1 — Corrective seven-profile V2 prerelease

This fixes RC4 showing Profile 1/4 on a four-logical-CPU worker by adding explicit
XMRig cpu.rx CPU-affinity configurations.  The original XMRig auto profile plus
six distinct cache/core/SMT-ranked affinity profiles are tested for 15 measured
minutes each. The winning profile retains its exact CPU-affinity mapping for
the sustained remainder of the 24-hour benchmark.

- Source: release/ztm-srp1v2-rc4-1 (V2 only); RC4 and V3 unchanged.
- 1 original XMRig auto baseline + exactly six optimized affinity configurations.
- Explicit Linux allowed CPU IDs and sibling groups from sysfs, L2/L3 domains and NUMA inventory.
- Fail closed on machines with fewer than three permitted logical CPUs rather than
  making up duplicate profiles.
- Existing supervised stop/start, five-second transition, two authorized consent
  checkboxes, huge-page preparation and 24-hour eligibility preserved.
- CI validates 3-/4-core, sparse masks, SMT/cache scoring, Ubuntu installation and GUI sizes.
- Still requires a physical-worker 24-hour test to verify actual HashVault behavior,
  throughput, temperature, and pinning/affinity efficacy across CPUs.
- Developer contribution and wallet policy are unchanged.

This is a **controlled development prerelease**, not a new stable release.
'''
)
print('RC4.1_PACKAGE_SHA256='+digest)
print('RC4.1_INSTALLER_SHA256='+installer_digest)
print('RC4.1_PACKAGE_SIZE='+str(size))
print('RC4.1_ONE_COMMAND='+command)
