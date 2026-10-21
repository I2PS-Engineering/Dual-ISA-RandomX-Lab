#!/usr/bin/env python3
"""Apply the deliberately narrow GUI-readability and rig-ID update to SRP1V1."""
from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: patch_srp1v2.py <dpkg-deb-extracted-root>")

root = Path(sys.argv[1])
gui_file = root / "usr/lib/ztm/ztm_gui.py"
engine_file = root / "usr/lib/ztm/ztm_engine.py"
mining_file = root / "usr/lib/ztm/ztm_mining.py"
control_file = root / "DEBIAN/control"

def one(s, old, new, why):
    hits = s.count(old)
    if hits != 1:
        raise SystemExit(f"STOP {why}: expected one occurrence, got {hits}")
    return s.replace(old, new)

g = gui_file.read_text(encoding="utf-8")
g = one(
    g,
    "self.root.title('ZTM-SRP1V1 — Zero to Monero | I2PS Engineering')",
    "self.root.title('ZTM-SRP1V2 — Zero to Monero | I2PS Engineering')",
    "window title",
)
g = one(
    g,
    "Linux x86-64 · Stable Release V1.1",
    "Linux x86-64 · Stable Release V1.2",
    "release header",
)

# Prior release scales only root-window dimensions; this does not reliably
# enlarge explicitly specified Tk fonts, button captions or checkbox labels.
start = "        size_ratio = min(target_w / 1090.0, target_h / 760.0)\n"
end = "        self.root.configure(bg=DARK)\n"
i = g.find(start)
j = g.find(end, i)
if i == -1 or j == -1:
    raise SystemExit("STOP: could not isolate previous incomplete GUI scaling")
replacement = """        # Font zoom is independent of window geometry. Physical laptop displays
        # need readable captions, not just a larger empty terminal pane.
        self._font_zoom = 1.65
        self._font_registry = {}
        self.ui_zoom_status = tk.StringVar(value='UI 165%')
        self.root.configure(bg=DARK)
"""
g = g[:i] + replacement + g[j + len(end):]

# Maintain live-updatable shared Font objects. Every explicit font references a
# reusable named Tk font, so A+/A- updates the rendered GUI without reopening it.
anchor = "    def label(self, parent, text, size=11, color=WHITE, bold=False, **kw):\n"
if g.count(anchor) != 1:
    raise SystemExit("STOP: cannot locate font factory insertion point")
font_helpers = """    def scaled_font(self, family, size, weight='normal'):
        key = (family, int(size), weight)
        font = self._font_registry.get(key)
        if font is None:
            font = tkfont.Font(
                root=self.root, family=family,
                size=max(10, round(int(size) * self._font_zoom)),
                weight=weight,
            )
            self._font_registry[key] = font
        return font

    def change_zoom(self, delta):
        self._font_zoom = max(1.25, min(2.00, round(self._font_zoom + delta, 2)))
        for (family, size, weight), font in self._font_registry.items():
            font.configure(size=max(10, round(size * self._font_zoom)))
        self.ui_zoom_status.set(f'UI {round(self._font_zoom * 100)}%')

"""
g = g.replace(anchor, font_helpers + anchor)
g = one(g, "import tkinter as tk\n", "import tkinter as tk\nfrom tkinter import font as tkfont\n", "Tk font import")

old = "font=('DejaVu Sans', size, 'bold' if bold else 'normal')"
new = "font=self.scaled_font('DejaVu Sans', size, 'bold' if bold else 'normal')"
g = one(g, old, new, "central label font")

# Map every remaining explicit GUI font to a zoom-responsive shared font.
font_expr = re.compile(r"font=\('((?:DejaVu Sans(?: Mono)?))', (\d+)(?:, '(bold|normal)')?\)")
matched = [m.group(0) for m in font_expr.finditer(g)]
if len(matched) < 10:
    raise SystemExit(f"STOP: found only {len(matched)} fixed GUI fonts")
g = font_expr.sub(
    lambda m: f"font=self.scaled_font({m.group(1)!r}, {m.group(2)}, {m.group(3)!r})"
    if m.group(3) else f"font=self.scaled_font({m.group(1)!r}, {m.group(2)})",
    g,
)
if re.search(r"font=\('DejaVu Sans", g):
    raise SystemExit("STOP: unscaled explicit font remains")

# Tk Checkbuttons were using the system's tiny default font. Fix all of them.
check_expr = re.compile(r"tk\.Checkbutton\((\w+),")
count = len(check_expr.findall(g))
if count < 3:
    raise SystemExit(f"STOP: expected at least three consent controls, got {count}")
g = check_expr.sub(
    r"tk.Checkbutton(\1, font=self.scaled_font('DejaVu Sans', 11),", g
)

# Add accessible live zoom buttons without disturbing layout or navigation.
release_anchor = """        self.label(release_box, 'CPU Threads: Auto', 9, CYAN, True).pack(anchor='e')
"""
if g.count(release_anchor) != 1:
    raise SystemExit("STOP: cannot locate top-right release status")
controls = """        zoom_bar = tk.Frame(bar, bg=PANEL)
        zoom_bar.pack(side='right', padx=(0, 16))
        tk.Button(zoom_bar, text='A−', command=lambda: self.change_zoom(-0.15),
                  font=self.scaled_font('DejaVu Sans', 10, 'bold'),
                  fg=WHITE, bg='#17344c', relief='flat', padx=9, pady=5).pack(side='left')
        tk.Label(zoom_bar, textvariable=self.ui_zoom_status,
                 font=self.scaled_font('DejaVu Sans', 9),
                 fg=CYAN, bg=PANEL, padx=8).pack(side='left')
        tk.Button(zoom_bar, text='A+', command=lambda: self.change_zoom(+0.15),
                  font=self.scaled_font('DejaVu Sans', 10, 'bold'),
                  fg=WHITE, bg='#17344c', relief='flat', padx=9, pady=5).pack(side='left')
"""
g = g.replace(release_anchor, release_anchor + controls)

# Explicitly increase ttk button hit targets, not just caption point size.
g = one(
    g,
    "style.configure('ZTM.TButton', font=self.scaled_font('DejaVu Sans', 10, 'bold'), padding=(13, 10))",
    "style.configure('ZTM.TButton', font=self.scaled_font('DejaVu Sans', 10, 'bold'), padding=(18, 13))",
    "ttk button size",
)

# Prevent the long explanatory subtitle from running off the edge at zoom 165%.
g = one(
    g,
    "self.label(main, 'Preparation runs APT update, installs prerequisites, then downloads verified official XMRig.\\nPool and payout are preconfigured; no mining begins without authorization.', 10, MUTED, justify='left')",
    "self.label(main, 'Preparation runs APT update, installs prerequisites, then downloads verified official XMRig.\\nPool and payout are preconfigured; no mining begins without authorization.', 10, MUTED, justify='left', wraplength=max(600, target_w - 100))",
    "preparation subtitle wrapping",
)

# Keep the stable 24-hour consent strings, engine timing, wallet and optimizer intact.
gui_file.write_text(g, encoding="utf-8")

e = engine_file.read_text(encoding="utf-8")
if e.count("ZTM-R-A-10-E-R") != 2:
    raise SystemExit("STOP: benchmark worker ID expected exactly twice")
e = e.replace("ZTM-R-A-10-E-R", "ZTM-RX1V2-L")
engine_file.write_text(e, encoding="utf-8")

m = mining_file.read_text(encoding="utf-8")
for key in ("'pass'", "'rig-id'"):
    original = f"{key}: 'ZTM-I2PS-Donate' if donation else 'ZTM-Personal-Mining',"
    m = one(m, original, f"{key}: 'ZTM-RX1V2-L',", f"personal mining {key}")
mining_file.write_text(m, encoding="utf-8")

c = control_file.read_text(encoding="utf-8")
c = one(c, "Version: 1.1.0~srp1v1", "Version: 1.2.0~srp1v2", "Debian version")
control_file.write_text(c, encoding="utf-8")

# Blocking invariants for the new package.
assert "Linux x86-64 · Stable Release V1.2" in g
assert "UI 165%" in g and "def change_zoom(self, delta):" in g
assert "from tkinter import font as tkfont" in g
assert "I authorize real CPU work for 24 hours, including electricity use and heat." in g
assert "I understand this online benchmark uses both XMRig and I2PS dev contribution." in g
assert "START 24-HOUR RANDOMX BENCHMARK" in g
assert "minutes = 1440" in g and "duration_menu" not in g
assert "a.minutes != 1440" in e and "a.seconds != 86400" in e
assert e.count("ZTM-RX1V2-L") == 2
assert m.count("ZTM-RX1V2-L") == 2
assert "ZTM-R-A-10-E-R" not in e
print(
    f"ZTM-SRP1V2 patched: {len(matched)} explicit font declarations and "
    f"{count} checkboxes now respond to 165% default zoom. "
    "Benchmark and personal-mining worker ID = ZTM-RX1V2-L."
)
