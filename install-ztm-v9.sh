#!/usr/bin/env bash
set -euo pipefail
REPO='I2PS-Engineering/ZTM_Benchmark'
PREFIX='downloads/ZTM-Zero-to-Monero_0.1.8-alpha9-final_amd64.deb.b64.part'
EXPECTED_SHA='6aec29e14d1c33bc17a9350bf5990bf998c5be2ac12c708e3bf5989c4e834c3a'
EXPECTED_SIZE='45962'
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
echo 'ZTM: downloading verified α9 final package from GitHub...'
: > "$TMP/package.b64"
for i in $(seq -w 0 99); do
  url="https://raw.githubusercontent.com/$REPO/main/${PREFIX}${i}"
  if curl -fsSL "$url" -o "$TMP/part"; then
    cat "$TMP/part" >> "$TMP/package.b64"
  else
    break
  fi
done
test -s "$TMP/package.b64" || { echo 'SECURITY STOP: package parts unavailable'; exit 1; }
base64 -d "$TMP/package.b64" > "$TMP/ztm.deb"
test "$(stat -c %s "$TMP/ztm.deb")" = "$EXPECTED_SIZE" || { echo 'SECURITY STOP: package size mismatch'; exit 1; }
echo "$EXPECTED_SHA  $TMP/ztm.deb" | sha256sum -c -
test "$(dpkg-deb -f "$TMP/ztm.deb" Package)" = 'ztm-zero-to-monero'
test "$(dpkg-deb -f "$TMP/ztm.deb" Architecture)" = 'amd64'
test "$(dpkg-deb -f "$TMP/ztm.deb" Version)" = '0.1.8~alpha9final1'
sudo apt-get install -y "$TMP/ztm.deb"
echo 'ZTM α9 final installed. Launching...'
nohup /usr/bin/ztm >/tmp/ztm-launch.log 2>&1 &
