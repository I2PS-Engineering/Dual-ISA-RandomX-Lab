#!/usr/bin/env bash
# I2PS quick online RandomX CPU engineering test bootstrap.
# Downloads a reviewed script, verifies its SHA-256, then runs interactively.
set -Eeuo pipefail
[[ "$(id -u)" != 0 ]] || { echo "Run as your normal Linux user, not sudo." >&2; exit 1; }
for cmd in curl sha256sum gzip bash; do
  command -v "$cmd" >/dev/null || { echo "Missing $cmd; install standard Ubuntu prerequisites first." >&2; exit 1; }
done
URL='https://raw.githubusercontent.com/I2PS-Engineering/Dual-ISA-RandomX-Lab/main/quickstart/i2ps-randomx-linux-test.sh.gz'
DIGEST='b6707d3c9e1a169ca1d00a37db9eeac7b931984ecaa355bf50c14742c128efc3'
WORK="$(mktemp -d)"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT
curl --fail --location --silent --show-error --retry 2 --max-time 60 "$URL" -o "$WORK/test.sh.gz"
printf '%s  %s\n' "$DIGEST" "$WORK/test.sh.gz" | sha256sum --check --status || { echo 'Benchmark download checksum mismatch; aborted.' >&2; exit 1; }
gzip -dc "$WORK/test.sh.gz" > "$WORK/test.sh"
bash -n "$WORK/test.sh" || { echo "Invalid benchmark script." >&2; exit 1; }
exec bash "$WORK/test.sh" "$@"
