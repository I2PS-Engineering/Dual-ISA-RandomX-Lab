#!/bin/bash
# Prepare (only) the official native XMRig for ZTM macOS, without starting CPU work.
set -euo pipefail
umask 077
[[ "$(uname -s)" == Darwin ]] || { echo 'This preparation script requires macOS.' >&2; exit 1; }

case "$(uname -m)" in
  arm64)
    ARCHIVE='xmrig-6.26.0-macos-arm64.tar.gz'
    CHECKSUM='6ae4eb4216e99a201ae9a3d2c3a7c275207c5165cfc25da1f3d735d6c4829c18'
    ;;
  x86_64)
    ARCHIVE='xmrig-6.26.0-macos-x64.tar.gz'
    CHECKSUM='1da924b358c0089e361540c4a9e6f8b09538b29efeafa2379590e0f6db358ff4'
    ;;
  *)
    echo 'Unsupported Mac CPU architecture.' >&2
    exit 1
    ;;
esac

DEST="$HOME/Library/Application Support/ZTM/Tools"
TEMP="$(mktemp -d)"
trap 'rm -rf "$TEMP"' EXIT
URL="https://github.com/xmrig/xmrig/releases/download/v6.26.0/$ARCHIVE"

echo 'Downloading the official native XMRig 6.26.0 archive...'
/usr/bin/curl --fail --location --retry 3 --output "$TEMP/$ARCHIVE" "$URL"
printf '%s  %s\n' "$CHECKSUM" "$TEMP/$ARCHIVE" | /usr/bin/shasum -a 256 -c -
mkdir -p "$TEMP/extract"
/usr/bin/tar -xzf "$TEMP/$ARCHIVE" -C "$TEMP/extract"

XMRIG="$(find "$TEMP/extract" -type f -name xmrig | head -n 1)"
[[ -n "$XMRIG" && -f "$XMRIG" ]] || { echo 'Unexpected upstream archive contents.' >&2; exit 1; }

mkdir -p "$DEST"
/bin/cp "$XMRIG" "$DEST/xmrig"
/bin/chmod 700 "$DEST/xmrig"
echo "Native XMRig prepared at: $DEST/xmrig"
echo 'No benchmark or mining process has been started.'
