#!/usr/bin/env bash
set -Eeuo pipefail
export LC_ALL=C
umask 077
URL='https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V1/ZTM-SRP1V1_amd64.deb'
EXPECTED_SHA='acd4bee9a502e39a673cbf39679710553fd83720cc261f5915166e8eb1c6dd56'
EXPECTED_SIZE='45728'
EXPECTED_VERSION='1.1.0~srp1v1'
fail() { printf 'ZTM-SRP1V1: %s\n' "$*" >&2; exit 1; }
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || fail 'requires Ubuntu Linux x86-64.'
[[ "${EUID:-0}" -ne 0 ]] || fail 'run as your normal Ubuntu desktop user, not root.'
[[ -r /etc/os-release ]] || fail 'cannot identify Linux distribution.'
. /etc/os-release
[[ "${ID:-}" == ubuntu ]] || fail 'this release targets Ubuntu Desktop.'
for cmd in python3 sha256sum stat dpkg-deb sudo apt-get pgrep; do
  command -v "$cmd" >/dev/null || fail "missing required command: $cmd"
done
if pgrep -a -x xmrig >/dev/null 2>&1; then
  echo 'An XMRig process is already running. Stop it before upgrading ZTM.' >&2
  pgrep -a -x xmrig >&2 || true
  exit 1
fi
work="$(mktemp -d "${TMPDIR:-/tmp}/ztm-srp1v1-install.XXXXXXXX")"
trap 'rm -rf "$work"' EXIT
pkg="$work/ZTM-SRP1V1_amd64.deb"
python3 - "$URL" "$pkg" <<'PY'
import pathlib, sys, urllib.request
url, target = sys.argv[1:]
req = urllib.request.Request(url, headers={'User-Agent':'ZTM-SRP1V1-Installer/1.0'})
with urllib.request.urlopen(req, timeout=60) as response:
    final = response.geturl()
    if 'github.com/' not in final and 'githubusercontent.com/' not in final:
        raise SystemExit('SECURITY STOP: unexpected download host')
    data = response.read()
pathlib.Path(target).write_bytes(data)
print(f'Downloaded {len(data)} bytes.')
PY
[[ "$(stat -c %s "$pkg")" == "$EXPECTED_SIZE" ]] || fail 'package size mismatch.'
printf '%s  %s\n' "$EXPECTED_SHA" "$pkg" | sha256sum --status -c - || fail 'package SHA-256 mismatch.'
[[ "$(dpkg-deb -f "$pkg" Package)" == 'ztm-zero-to-monero' ]] || fail 'unexpected package name.'
[[ "$(dpkg-deb -f "$pkg" Architecture)" == 'amd64' ]] || fail 'wrong architecture.'
[[ "$(dpkg-deb -f "$pkg" Version)" == "$EXPECTED_VERSION" ]] || fail 'wrong package version.'
sudo apt-get install -y "$pkg"
[[ "$(dpkg-query -W -f='${Version}' ztm-zero-to-monero 2>/dev/null)" == "$EXPECTED_VERSION" ]] || fail 'installed version verification failed.'
echo 'ZTM-SRP1V1 installed and verified. Launching...'
nohup /usr/bin/ztm >/tmp/ztm-launch.log 2>&1 &
