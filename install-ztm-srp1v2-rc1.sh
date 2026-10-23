#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || { echo "Ubuntu x86-64 required"; exit 1; }
[[ "${EUID}" -ne 0 ]] || { echo "Launch as your ordinary Ubuntu user"; exit 1; }
. /etc/os-release
[[ "${ID}" == ubuntu ]] || { echo "Ubuntu required"; exit 1; }
for cmd in python3 sha256sum stat dpkg-deb sudo apt-get; do command -v "$cmd" >/dev/null || { echo "Missing: $cmd"; exit 1; }; done
if pgrep -a -f '(^|/)(xmrig|xmrig-amd|xmrig-nvidia)([[:space:]]|$)' >/dev/null 2>&1; then
  echo "A miner is running. STOP its old run before updating; this installer will not terminate a benchmark."
  exit 1
fi
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pkg="$work/ZTM-SRP1V2-RC1_amd64.deb"
python3 - "$pkg" <<'PYDOWNLOAD'
import pathlib,sys,urllib.request
u='https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/release/ztm-srp1v2-rc1/dist/ZTM-SRP1V2-RC1_amd64.deb'
pathlib.Path(sys.argv[1]).write_bytes(urllib.request.urlopen(u,timeout=60).read())
PYDOWNLOAD
echo "cc010eca0cd1616a15a82c4748f8ee3c9a4b03b5664a8a94c873271b2651cbf3  $pkg" | sha256sum -c -
[[ "$(stat -c%s "$pkg")" == 50038 ]] || exit 1
[[ "$(dpkg-deb -f "$pkg" Version)" == 1.2.1~srp1v2rc1 ]] || exit 1
sudo apt-get install -y "$pkg"
[[ "$(dpkg-query -W -f='${Version}' ztm-zero-to-monero)" == 1.2.1~srp1v2rc1 ]] || exit 1
echo 'ZTM-SRP1V2-RC1 installed; launching...'
nohup /usr/bin/ztm >/tmp/ztm-rc1-launch.log 2>&1 &
