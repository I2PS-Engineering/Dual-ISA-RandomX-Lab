#!/usr/bin/env bash
set -Eeuo pipefail
export LC_ALL=C
umask 077

REPO='I2PS-Engineering/ZTM_Benchmark'
PACKAGE_COMMIT='b0c5298341343644ce0a618f15717f7d6193aba3'
PREFIX='downloads/ZTM-Zero-to-Monero_0.1.8-alpha9-final_amd64.deb.b64.part'
EXPECTED_SHA='6aec29e14d1c33bc17a9350bf5990bf998c5be2ac12c708e3bf5989c4e834c3a'
EXPECTED_SIZE='45962'
DPKG_VERSION='0.1.8~alpha9final1'
RAW="https://raw.githubusercontent.com/$REPO/$PACKAGE_COMMIT"

[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || { echo 'ZTM α9 requires Ubuntu Linux x86-64.' >&2; exit 1; }
[[ "${EUID:-0}" -ne 0 ]] || { echo 'Run this command as your normal Ubuntu desktop user, not root.' >&2; exit 1; }
[[ -r /etc/os-release ]] || { echo 'Cannot identify Linux distribution.' >&2; exit 1; }
. /etc/os-release
[[ "${ID:-}" == ubuntu ]] || { echo 'This ZTM release targets Ubuntu Desktop.' >&2; exit 1; }
for cmd in python3 base64 sha256sum stat dpkg-deb sudo apt-get; do
  command -v "$cmd" >/dev/null || { echo "Missing required command: $cmd" >&2; exit 1; }
done

work="$(mktemp -d "${TMPDIR:-/tmp}/ztm-alpha9-install.XXXXXXXX")"
trap 'rm -rf "$work"' EXIT
pkg="$work/ztm.deb"

echo 'ZTM α9: downloading the pinned, verified package from I2PS Engineering GitHub...'
python3 - "$RAW" "$PREFIX" "$work/package.b64" <<'PY'
import pathlib, sys, urllib.error, urllib.request
raw, prefix, target = sys.argv[1:]
parts=[]
for i in range(100):
    url=f"{raw}/{prefix}{i:02d}"
    req=urllib.request.Request(url,headers={'User-Agent':'ZTM-Alpha9-Installer/1.0'})
    try:
        with urllib.request.urlopen(req,timeout=45) as response:
            final=response.geturl()
            if not final.startswith('https://raw.githubusercontent.com/'):
                raise SystemExit('SECURITY STOP: unexpected download host')
            data=response.read(7001)
    except urllib.error.HTTPError as exc:
        if exc.code == 404 and i > 0:
            break
        raise
    if not data or len(data) > 7000:
        raise SystemExit(f'SECURITY STOP: package fragment {i:02d} invalid')
    parts.append(data.decode('ascii'))
if not parts:
    raise SystemExit('SECURITY STOP: package fragments unavailable')
pathlib.Path(target).write_text(''.join(parts),encoding='ascii')
print(f'Downloaded {len(parts)} verified package fragments.')
PY

base64 -d "$work/package.b64" > "$pkg"
[[ "$(stat -c %s "$pkg")" == "$EXPECTED_SIZE" ]] || { echo 'SECURITY STOP: package size mismatch.' >&2; exit 1; }
printf '%s  %s\n' "$EXPECTED_SHA" "$pkg" | sha256sum --status -c - || { echo 'SECURITY STOP: package SHA-256 mismatch.' >&2; exit 1; }
[[ "$(dpkg-deb -f "$pkg" Package)" == 'ztm-zero-to-monero' ]] || { echo 'SECURITY STOP: unexpected package name.' >&2; exit 1; }
[[ "$(dpkg-deb -f "$pkg" Architecture)" == 'amd64' ]] || { echo 'SECURITY STOP: wrong architecture.' >&2; exit 1; }
[[ "$(dpkg-deb -f "$pkg" Version)" == "$DPKG_VERSION" ]] || { echo 'SECURITY STOP: wrong package version.' >&2; exit 1; }

if pgrep -a -x xmrig >/dev/null 2>&1; then
  echo 'An XMRig process is already running. Stop it before upgrading ZTM.' >&2
  pgrep -a -x xmrig >&2 || true
  exit 1
fi

echo 'Package verified. Ubuntu may request your administrator password for installation.'
sudo apt-get install -y "$pkg"
command -v ztm >/dev/null || { echo 'ZTM launcher missing after installation.' >&2; exit 1; }

echo 'ZTM α9 final installed. Launching...'
nohup /usr/bin/ztm >/tmp/ztm-launch.log 2>&1 &
