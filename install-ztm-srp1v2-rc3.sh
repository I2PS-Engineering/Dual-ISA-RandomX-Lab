#!/usr/bin/env bash
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
url='https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/release/ztm-srp1v2-rc3/dist/ZTM-SRP1V2-RC3_amd64.deb'
pathlib.Path(sys.argv[1]).write_bytes(urllib.request.urlopen(url,timeout=60).read())
PYDOWNLOAD
echo "0d29eeb3db7300c9bc12642350fc14b66031963033855cd3927a27d81b370af7  $pkg" | sha256sum -c -
[[ "$(stat -c %s "$pkg")" == 120950 ]] || exit 1
[[ "$(dpkg-deb -f "$pkg" Version)" == '1.2.3~srp1v2rc3' ]] || exit 1
sudo apt-get install -y "$pkg"
dpkg -s ztm-zero-to-monero | grep -q '^Version: 1.2.3~srp1v2rc3$'
command -v pkexec >/dev/null || { echo 'Missing pkexec after installation'; exit 1; }
echo 'ZTM-SRP1V2-RC3 installed; launching with pre-GUI XMRig cleanup...'
nohup /usr/bin/ztm >/tmp/ztm-rc3-launch.log 2>&1 &
