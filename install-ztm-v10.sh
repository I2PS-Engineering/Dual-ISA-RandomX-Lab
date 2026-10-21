#!/usr/bin/env bash
set -Eeuo pipefail
export LC_ALL=C
umask 077

REPO='I2PS-Engineering/ZTM_Benchmark'
BASELINE_COMMIT='b0c5298341343644ce0a618f15717f7d6193aba3'
PREFIX='downloads/ZTM-Zero-to-Monero_0.1.8-alpha9-final_amd64.deb.b64.part'
BASELINE_SHA='6aec29e14d1c33bc17a9350bf5990bf998c5be2ac12c708e3bf5989c4e834c3a'
BASELINE_SIZE='45962'
BASELINE_VERSION='0.1.8~alpha9final1'
NEW_VERSION='0.1.9~alpha10final1'
RAW="https://raw.githubusercontent.com/$REPO/$BASELINE_COMMIT"

fail() { printf 'ZTM α10: %s\n' "$*" >&2; exit 1; }

[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || fail 'requires Ubuntu Linux x86-64.'
[[ "${EUID:-0}" -ne 0 ]] || fail 'run this as your normal Ubuntu desktop user, not root.'
[[ -r /etc/os-release ]] || fail 'cannot identify Linux distribution.'
. /etc/os-release
[[ "${ID:-}" == ubuntu ]] || fail 'this release targets Ubuntu Desktop.'

for cmd in python3 base64 sha256sum stat dpkg-deb sudo apt-get pgrep grep; do
  command -v "$cmd" >/dev/null || fail "missing required command: $cmd"
done

if pgrep -a -x xmrig >/dev/null 2>&1; then
  echo 'An XMRig process is already running. Stop it before upgrading ZTM.' >&2
  pgrep -a -x xmrig >&2 || true
  exit 1
fi

work="$(mktemp -d "${TMPDIR:-/tmp}/ztm-alpha10.XXXXXXXX")"
trap 'rm -rf "$work"' EXIT
baseline="$work/alpha9.deb"
newpkg="$work/ZTM-Zero-to-Monero_0.1.9-alpha10-final_amd64.deb"

printf '%s\n' 'ZTM α10: downloading the immutable verified α9 baseline...'
python3 - "$RAW" "$PREFIX" "$work/package.b64" <<'PY'
import pathlib, sys, urllib.error, urllib.request
raw, prefix, target = sys.argv[1:]
parts = []
for i in range(100):
    url = f"{raw}/{prefix}{i:02d}"
    req = urllib.request.Request(url, headers={'User-Agent': 'ZTM-Alpha10-Builder/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            final = response.geturl()
            if not final.startswith('https://raw.githubusercontent.com/'):
                raise SystemExit('SECURITY STOP: unexpected download host')
            data = response.read(7001)
    except urllib.error.HTTPError as exc:
        if exc.code == 404 and i > 0:
            break
        raise
    if not data or len(data) > 7000:
        raise SystemExit(f'SECURITY STOP: invalid package fragment {i:02d}')
    parts.append(data.decode('ascii'))
if not parts:
    raise SystemExit('SECURITY STOP: package fragments unavailable')
pathlib.Path(target).write_text(''.join(parts), encoding='ascii')
print(f'Downloaded {len(parts)} baseline fragments.')
PY

base64 -d "$work/package.b64" > "$baseline"
[[ "$(stat -c %s "$baseline")" == "$BASELINE_SIZE" ]] || fail 'baseline package size mismatch.'
printf '%s  %s\n' "$BASELINE_SHA" "$baseline" | sha256sum --status -c - || fail 'baseline SHA-256 mismatch.'
[[ "$(dpkg-deb -f "$baseline" Package)" == 'ztm-zero-to-monero' ]] || fail 'unexpected baseline package name.'
[[ "$(dpkg-deb -f "$baseline" Architecture)" == 'amd64' ]] || fail 'unexpected baseline architecture.'
[[ "$(dpkg-deb -f "$baseline" Version)" == "$BASELINE_VERSION" ]] || fail 'unexpected baseline version.'

printf '%s\n' 'ZTM α10: applying adaptive display scaling and new rig ID...'
dpkg-deb -R "$baseline" "$work/pkg" >/dev/null
cp "$work/pkg/usr/lib/ztm/ztm_engine.py" "$work/ztm_engine.before.py"

python3 - "$work/pkg" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])

gui = root / 'usr/lib/ztm/ztm_gui.py'
s = gui.read_text(encoding='utf-8')
old = """        self.root.geometry('1090x760')
        self.root.minsize(850, 650)
"""
new = """        # Adaptive display sizing for compact high-resolution laptop panels.
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        usable_w = max(850, screen_w - 80)
        usable_h = max(650, screen_h - 100)
        target_w = min(1600, usable_w, max(1090, int(screen_w * 0.86)))
        target_h = min(950, usable_h, max(760, int(screen_h * 0.86)))
        pos_x = max(0, (screen_w - target_w) // 2)
        pos_y = max(0, (screen_h - target_h) // 2)
        self.root.geometry(f'{target_w}x{target_h}+{pos_x}+{pos_y}')
        self.root.minsize(min(1000, usable_w), min(700, usable_h))

        size_ratio = min(target_w / 1090.0, target_h / 760.0)
        ui_scale = max(1.0, min(1.30, size_ratio))
        try:
            current_tk_scale = float(self.root.tk.call('tk', 'scaling'))
            self.root.tk.call('tk', 'scaling', current_tk_scale * ui_scale)
        except (tk.TclError, TypeError, ValueError):
            pass
"""
if s.count(old) != 1:
    raise SystemExit('SECURITY STOP: expected α9 GUI geometry block not found exactly once')
gui.write_text(s.replace(old, new), encoding='utf-8')

engine = root / 'usr/lib/ztm/ztm_engine.py'
e = engine.read_text(encoding='utf-8')
if e.count('ZTM-α9') != 1:
    raise SystemExit('SECURITY STOP: expected α9 rig ID not found exactly once')
if 'ZTM-R-A-10-E-R' in e:
    raise SystemExit('SECURITY STOP: new rig ID unexpectedly already present')
engine.write_text(e.replace('ZTM-α9', 'ZTM-R-A-10-E-R'), encoding='utf-8')

control = root / 'DEBIAN/control'
c = control.read_text(encoding='utf-8')
if c.count('0.1.8~alpha9final1') != 1:
    raise SystemExit('SECURITY STOP: expected α9 package version not found exactly once')
control.write_text(c.replace('0.1.8~alpha9final1', '0.1.9~alpha10final1'), encoding='utf-8')
PY

python3 -m compileall -q "$work/pkg/usr/lib/ztm"
find "$work/pkg/usr/lib/ztm" -type d -name __pycache__ -prune -exec rm -rf '{}' +

python3 - "$work/ztm_engine.before.py" "$work/pkg/usr/lib/ztm/ztm_engine.py" <<'PY'
from pathlib import Path
import sys
before = Path(sys.argv[1]).read_text(encoding='utf-8')
after = Path(sys.argv[2]).read_text(encoding='utf-8')
assert after.count('ZTM-R-A-10-E-R') == 1
assert after.replace('ZTM-R-A-10-E-R', 'ZTM-α9') == before
print('Rig-ID diff verified: literal only.')
PY

grep -Fq "screen_w = self.root.winfo_screenwidth()" "$work/pkg/usr/lib/ztm/ztm_gui.py" || fail 'adaptive GUI patch verification failed.'
grep -Fq "ui_scale = max(1.0, min(1.30" "$work/pkg/usr/lib/ztm/ztm_gui.py" || fail 'GUI scale verification failed.'
grep -Fq 'ZTM-R-A-10-E-R' "$work/pkg/usr/lib/ztm/ztm_engine.py" || fail 'rig ID verification failed.'
! grep -RFn --include='*.py' 'ZTM-α9' "$work/pkg/usr/lib/ztm" >/dev/null || fail 'old rig ID still present.'

printf '%s\n' 'ZTM α10: rebuilding and verifying the Debian package...'
dpkg-deb --build --root-owner-group "$work/pkg" "$newpkg" >/dev/null
[[ "$(dpkg-deb -f "$newpkg" Package)" == 'ztm-zero-to-monero' ]] || fail 'rebuilt package name mismatch.'
[[ "$(dpkg-deb -f "$newpkg" Architecture)" == 'amd64' ]] || fail 'rebuilt architecture mismatch.'
[[ "$(dpkg-deb -f "$newpkg" Version)" == "$NEW_VERSION" ]] || fail 'rebuilt version mismatch.'
NEW_SHA="$(sha256sum "$newpkg" | awk '{print $1}')"
NEW_SIZE="$(stat -c %s "$newpkg")"
printf 'ZTM α10 package verified: %s bytes\nSHA-256: %s\n' "$NEW_SIZE" "$NEW_SHA"

printf '%s\n' 'ZTM α10: installing. Ubuntu may request the administrator password...'
sudo apt-get install -y "$newpkg"
[[ "$(dpkg-query -W -f='${Version}' ztm-zero-to-monero 2>/dev/null)" == "$NEW_VERSION" ]] || fail 'installed package version verification failed.'
grep -Fq 'ZTM-R-A-10-E-R' /usr/lib/ztm/ztm_engine.py || fail 'installed rig ID verification failed.'
grep -Fq 'screen_w = self.root.winfo_screenwidth()' /usr/lib/ztm/ztm_gui.py || fail 'installed GUI verification failed.'

printf '%s\n' 'ZTM α10 installed and verified. Launching...'
nohup /usr/bin/ztm >/tmp/ztm-launch.log 2>&1 &
