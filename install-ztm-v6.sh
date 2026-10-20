#!/usr/bin/env bash
# ZTM — Zero to Monero alpha6 gated Wallet and Mining installer for Ubuntu Desktop x86-64.
set -Eeuo pipefail
export LC_ALL=C
umask 077

REPO='I2PS-Engineering/ZTM_Benchmark'
PACKAGE_COMMIT='6d0568aa93631199338cf016b5dc8473b2ab7673'
VERSION='0.1.5-alpha6-mining'
DPKG_VERSION='0.1.5~alpha6mining1'
PACKAGE_SHA='86262258c70707ad15a4154935175f8394bc3b5d98c4f305b692e90fac4109cd'
PACKAGE_SIZE='30380'
BASE='downloads/ZTM-Zero-to-Monero_0.1.5-alpha6-mining_amd64.deb.b64'
RAW="https://raw.githubusercontent.com/$REPO/$PACKAGE_COMMIT"

[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || {
  echo 'ZTM requires Ubuntu Linux x86-64.' >&2; exit 1;
}
[[ "${EUID:-0}" -ne 0 ]] || {
  echo 'Run this as your normal desktop user, not root.' >&2; exit 1;
}
[ -r /etc/os-release ] || { echo 'Cannot identify Linux distribution.' >&2; exit 1; }
. /etc/os-release
[[ "${ID:-}" == ubuntu ]] || {
  echo 'This engineering release targets Ubuntu Desktop.' >&2; exit 1;
}

for cmd in python3 sha256sum dpkg-deb sudo apt-get; do
  command -v "$cmd" >/dev/null || { echo "Missing required command: $cmd" >&2; exit 1; }
done

work=$(mktemp -d "${TMPDIR:-/tmp}/ztm-install.XXXXXXXX")
trap 'rm -rf "$work"' EXIT
pkg="$work/ztm.deb"

echo "ZTM $VERSION — downloading verified package from I2PS Engineering GitHub..."

python3 - "$RAW" "$BASE" "$pkg" <<'PY'
import base64
import pathlib
import sys
import urllib.request

raw, base, target = sys.argv[1:]
expected_sizes = [6000, 6000, 6000, 6000, 6000, 6000, 4508]
pieces = []

for index, expected in enumerate(expected_sizes):
    url = f"{raw}/{base}.part{index:02d}"
    req = urllib.request.Request(url, headers={"User-Agent": "ZTM-GitHub-Installer/0.1.5"})
    with urllib.request.urlopen(req, timeout=45) as response:
        final = response.geturl()
        if not final.startswith("https://raw.githubusercontent.com/"):
            raise SystemExit("SECURITY STOP: unexpected download host")
        data = response.read(expected + 1)
    if len(data) != expected:
        raise SystemExit(f"SECURITY STOP: transfer fragment {index:02d} size mismatch")
    try:
        pieces.append(data.decode("ascii"))
    except UnicodeDecodeError as exc:
        raise SystemExit("SECURITY STOP: non-ASCII package fragment") from exc

encoded = "".join(pieces)
try:
    package = base64.b64decode(encoded, validate=True)
except Exception as exc:
    raise SystemExit("SECURITY STOP: invalid package encoding") from exc

pathlib.Path(target).write_bytes(package)
PY

[[ "$(stat -c %s "$pkg")" == "$PACKAGE_SIZE" ]] || {
  echo 'SECURITY STOP: package size mismatch.' >&2; exit 1;
}
printf '%s  %s\n' "$PACKAGE_SHA" "$pkg" | sha256sum --status -c - || {
  echo 'SECURITY STOP: package SHA-256 mismatch.' >&2; exit 1;
}
[[ "$(dpkg-deb -f "$pkg" Package)" == 'ztm-zero-to-monero' ]] || {
  echo 'SECURITY STOP: unexpected package name.' >&2; exit 1;
}
[[ "$(dpkg-deb -f "$pkg" Architecture)" == 'amd64' ]] || {
  echo 'SECURITY STOP: wrong package architecture.' >&2; exit 1;
}
[[ "$(dpkg-deb -f "$pkg" Version)" == "$DPKG_VERSION" ]] || {
  echo 'SECURITY STOP: wrong package version.' >&2; exit 1;
}

echo 'Verified. Ubuntu may request your administrator password for package installation.'
sudo apt-get update
sudo apt-get install -y "$pkg"
command -v ztm >/dev/null || { echo 'ZTM launcher not found after installation.' >&2; exit 1; }
echo 'Launching ZTM. Mining does not start until you authorize it in the unchanged GUI.'
exec ztm
