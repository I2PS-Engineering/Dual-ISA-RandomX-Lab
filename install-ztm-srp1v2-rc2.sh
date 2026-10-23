#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || exit 1
[[ "$(id -u)" -ne 0 ]] || { echo "Run as ordinary Ubuntu user"; exit 1; }
. /etc/os-release
[[ "$ID" == ubuntu ]] || { echo "Ubuntu Desktop required"; exit 1; }
for cmd in python3 sha256sum stat dpkg-deb sudo apt-get; do command -v "$cmd" >/dev/null || { echo "Missing $cmd"; exit 1; }; done
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pkg="$work/ZTM-SRP1V2-RC2_amd64.deb"
python3 - "$pkg" <<'PYDOWNLOAD'
import pathlib,sys,urllib.request
u='https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/release/ztm-srp1v2-rc2/dist/ZTM-SRP1V2-RC2_amd64.deb'
pathlib.Path(sys.argv[1]).write_bytes(urllib.request.urlopen(u,timeout=60).read())
PYDOWNLOAD
echo "a3f252639d35c981b936f765a5ac8d7439ddaff47df3b5a72491bb771a784bd1  $pkg" | sha256sum -c -
[[ "$(stat -c%s "$pkg")" == 57240 ]] || exit 1
[[ "$(dpkg-deb -f "$pkg" Version)" == 1.2.2~srp1v2rc2 ]] || exit 1
sudo apt-get install -y "$pkg"
dpkg -s ztm-zero-to-monero | grep -q '^Version: 1.2.2~srp1v2rc2$'
command -v pkexec >/dev/null || { echo 'Missing pkexec after package install'; exit 1; }
echo 'RC2 installed; pre-GUI authorization and XMRig cleanup required'
nohup /usr/bin/ztm >/tmp/ztm-rc2-launch.log 2>&1 &
