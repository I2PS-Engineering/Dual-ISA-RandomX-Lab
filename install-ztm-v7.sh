#!/usr/bin/env bash
# ZTM Benchmark — 0.1.6-alpha7: pinned GitHub installer, Ubuntu Desktop x86-64.
set -Eeuo pipefail
export LC_ALL=C
umask 077
REPO='I2PS-Engineering/ZTM_Benchmark'
PACKAGE_COMMIT='89d137b4b862f9e9e8fbc5c28ad931b7c0f1b804'
VERSION='0.1.6-alpha7-guard'
DPKG_VERSION='0.1.6~alpha7guard1'
PACKAGE_SHA='cf642be63edee15179acb8b3454ae7539948c346d8573fb23d9731e4e250cffc'
PACKAGE_SIZE='31792'
BASE='downloads/ZTM-Zero-to-Monero_0.1.6-alpha7-guard_amd64.deb.b64'
RAW="https://raw.githubusercontent.com/$REPO/$PACKAGE_COMMIT"
if [[ "${1:-}" == '--help' ]]; then
  printf '%s\n' 'ZTM installer for Ubuntu Desktop x86-64; no mining until GUI authorization.'
  exit 0
fi
[[ $# == 0 ]] || { echo 'Unexpected installer argument' >&2; exit 2; }
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || { echo 'Ubuntu Linux x86-64 required.' >&2; exit 1; }
[[ "$EUID" != 0 ]] || { echo 'Run as your normal desktop user (not root).' >&2; exit 1; }
[[ -r /etc/os-release ]] || { echo 'Linux release information unavailable.' >&2; exit 1; }
. /etc/os-release
[[ "${ID:-}" == ubuntu ]] || { echo 'Ubuntu Desktop is required for this build.' >&2; exit 1; }
for cmd in python3 sha256sum stat dpkg-deb sudo apt-get; do
  command -v "$cmd" >/dev/null || { echo "Missing installer prerequisite: $cmd" >&2; exit 1; }
done
work="$(mktemp -d "${TMPDIR:-/tmp}/ztm-install.XXXXXXXX")"
trap 'rm -rf "$work"' EXIT
pkg="$work/ztm.deb"
printf '%s\n' "ZTM $VERSION — downloading the pinned package from I2PS GitHub."
python3 - "$RAW" "$BASE" "$pkg" <<'PY'
import base64
import pathlib
import sys
import urllib.request

raw, base, target = sys.argv[1:]
expected_sizes = (6000, 6000, 6000, 6000, 6000, 6000, 6000, 392)
parts = []
for index, expected in enumerate(expected_sizes):
    url = f'{raw}/{base}.part{index:02d}'
    request = urllib.request.Request(url, headers={'User-Agent': 'ZTM-GitHub-Installer/0.1.6'})
    with urllib.request.urlopen(request, timeout=45) as response:
        if not response.geturl().startswith('https://raw.githubusercontent.com/'):
            raise SystemExit('SECURITY STOP: unexpected download host')
        data = response.read(expected + 1)
    if len(data) != expected:
        raise SystemExit(f'SECURITY STOP: package fragment {index} size mismatch')
    parts.append(data.decode('ascii'))
try:
    package = base64.b64decode(''.join(parts), validate=True)
except Exception as exc:
    raise SystemExit('SECURITY STOP: invalid package encoding') from exc
pathlib.Path(target).write_bytes(package)
PY
[[ "$(stat -c %s "$pkg")" == "$PACKAGE_SIZE" ]] || { echo 'SECURITY STOP: package size mismatch' >&2; exit 1; }
printf '%s  %s\n' "$PACKAGE_SHA" "$pkg" | sha256sum --status -c - || { echo 'SECURITY STOP: package checksum mismatch' >&2; exit 1; }
[[ "$(dpkg-deb -f "$pkg" Package)" == 'ztm-zero-to-monero' ]] || { echo 'SECURITY STOP: wrong package' >&2; exit 1; }
[[ "$(dpkg-deb -f "$pkg" Architecture)" == 'amd64' ]] || { echo 'SECURITY STOP: wrong package architecture' >&2; exit 1; }
[[ "$(dpkg-deb -f "$pkg" Version)" == "$DPKG_VERSION" ]] || { echo 'SECURITY STOP: wrong package version' >&2; exit 1; }
if pgrep -f '^(/usr/bin/)?python3.*ztm_(engine|mining)\.py' >/dev/null 2>&1 || pgrep -x xmrig >/dev/null 2>&1; then
  echo 'XMRig or ZTM mining is still running. Stop the active process(es) before installing this update.' >&2
  exit 1
fi
echo 'Verified package. Ubuntu may request your administrator password for installation.'
sudo apt-get update
sudo apt-get install -y "$pkg"
command -v ztm >/dev/null || { echo 'ZTM launcher missing after install' >&2; exit 1; }
echo 'Starting ZTM. Benchmarking and personal mining require separate user authorization.'
exec ztm
