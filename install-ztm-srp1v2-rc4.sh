#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || { echo 'Ubuntu x86-64 required'; exit 1; }
[[ "$(id -u)" -ne 0 ]] || { echo 'Run as an ordinary Ubuntu desktop user, not root'; exit 1; }
. /etc/os-release
[[ "$ID" == ubuntu ]] || { echo 'Ubuntu required'; exit 1; }
for cmd in python3 sha256sum stat dpkg-deb sudo apt-get; do command -v "$cmd" >/dev/null || { echo "Missing $cmd"; exit 1; }; done
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pkg="$work/ZTM-SRP1V2-RC4_amd64.deb"
python3 - "$pkg" <<'PYDOWNLOAD'
import pathlib, sys, urllib.request
url = 'https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V2-RC4/ZTM-SRP1V2-RC4_amd64.deb'
request = urllib.request.Request(url, headers={'User-Agent': 'ZTM-RC4-Verified-Installer'})
with urllib.request.urlopen(request, timeout=120) as response, open(sys.argv[1], 'wb') as output:
    while True:
        chunk = response.read(65536)
        if not chunk: break
        output.write(chunk)
PYDOWNLOAD
echo 'abd42a5ded115966dc20d761560581f2c6009575f73f433869400183404aa879  '"$pkg" | sha256sum -c -
[[ "$(stat -c %s "$pkg")" == 121844 ]] || { echo 'RC4 package size mismatch'; exit 1; }
[[ "$(dpkg-deb -f "$pkg" Package)" == 'ztm-zero-to-monero' ]] || { echo 'RC4 package identity mismatch'; exit 1; }
[[ "$(dpkg-deb -f "$pkg" Architecture)" == amd64 ]] || { echo 'RC4 architecture mismatch'; exit 1; }
[[ "$(dpkg-deb -f "$pkg" Version)" == '1.2.4~srp1v2rc4' ]] || { echo 'RC4 package version mismatch'; exit 1; }
sudo apt-get install -y "$pkg"
dpkg -s ztm-zero-to-monero | grep -q '^Version: 1.2.4~srp1v2rc4$'
command -v pkexec >/dev/null || { echo 'Missing pkexec after installation'; exit 1; }
echo 'ZTM-SRP1V2-RC4 installed. Launching ZTM with mandatory pre-GUI XMRig cleanup.'
nohup /usr/bin/ztm >/tmp/ztm-rc4-launch.log 2>&1 &
