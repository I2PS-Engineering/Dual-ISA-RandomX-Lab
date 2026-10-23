#!/usr/bin/env bash
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
url="https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V2-RC4.1/ZTM-SRP1V2-RC4.1_amd64.deb"
req=urllib.request.Request(url,headers={"User-Agent":"ZTM-RC41-Verified-Installer"})
with urllib.request.urlopen(req,timeout=120) as response, open(sys.argv[1],"wb") as out:
    while True:
        chunk=response.read(65536)
        if not chunk: break
        out.write(chunk)
PYDOWNLOAD
echo "b1649334daf85d504b0423297dcf4fe6d34bace125fece642c120f6cc7cdd7fa  $pkg" | sha256sum -c -
[[ "$(stat -c %s "$pkg")" == 133066 ]] || { echo "RC4.1 package byte-size mismatch"; exit 1; }
[[ "$(dpkg-deb -f "$pkg" Package)" == ztm-zero-to-monero ]] || exit 1
[[ "$(dpkg-deb -f "$pkg" Architecture)" == amd64 ]] || exit 1
[[ "$(dpkg-deb -f "$pkg" Version)" == '1.2.5~srp1v2rc41' ]] || exit 1
sudo apt-get install -y "$pkg"
dpkg -s ztm-zero-to-monero | grep -q '^Version: 1.2.5~srp1v2rc41$'
command -v pkexec >/dev/null || { echo "Missing pkexec after installation"; exit 1; }
echo "ZTM RC4.1 installed. Launching with authorized pre-GUI XMRig cleanup."
nohup /usr/bin/ztm >/tmp/ztm-rc41-launch.log 2>&1 &
