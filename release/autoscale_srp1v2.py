#!/usr/bin/env python3
"""Surgical SRP1V2 auto-scaling patch: presentation geometry only."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: autoscale_srp1v2.py <installed-ztm_gui.py>")
p = Path(sys.argv[1])
g = p.read_text(encoding="utf-8")

def one(old, new, name):
    global g
    n = g.count(old)
    if n != 1:
        raise SystemExit(f"STOP scaling {name}: expected 1 occurrence, found {n}")
    g = g.replace(old, new)

one("""        usable_w = max(850, screen_w - 80)
        usable_h = max(650, screen_h - 100)
        target_w = min(1600, usable_w, max(1090, int(screen_w * 0.86)))
        target_h = min(950, usable_h, max(760, int(screen_h * 0.86)))""",
"""        # Scale to the actual display instead of enforcing desktop-sized minimums.
        usable_w = max(560, screen_w - 60)
        usable_h = max(420, screen_h - 90)
        target_w = min(1600, usable_w, max(780, int(screen_w * 0.88)))
        target_h = min(950, usable_h, max(550, int(screen_h * 0.88)))""", "screen geometry")
one("""        self.root.minsize(min(1000, usable_w), min(700, usable_h))

        # Font zoom is independent of window geometry. Physical laptop displays
        # need readable captions, not just a larger empty terminal pane.
        self._font_zoom = 1.65
        self._font_registry = {}
        self.ui_zoom_status = tk.StringVar(value='UI 165%')""",
"""        self._initial_width = target_w
        self.root.minsize(min(760, usable_w), min(540, usable_h))

        # Select a readable zoom from detected display size on each launch.
        # Manual A-/A+ controls continue to use the same font registry.
        if screen_h <= 800 or target_w < 1000:
            self._font_zoom = 0.95
        elif screen_h <= 950 or target_w < 1200:
            self._font_zoom = 1.10
        elif screen_h <= 1100:
            self._font_zoom = 1.30
        else:
            self._font_zoom = 1.65
        self._font_registry = {}
        self.ui_zoom_status = tk.StringVar(value=f'UI {round(self._font_zoom * 100)}%')""", "initial zoom")
one("size=max(10, round(int(size) * self._font_zoom))",
    "size=max(8, round(int(size) * self._font_zoom))", "minimum font")
one("self._font_zoom = max(1.25, min(2.00, round(self._font_zoom + delta, 2)))",
    "self._font_zoom = max(0.85, min(2.00, round(self._font_zoom + delta, 2)))", "zoom range")
one("font.configure(size=max(10, round(size * self._font_zoom)))",
    "font.configure(size=max(8, round(size * self._font_zoom)))", "font resizing")
one("style.configure('ZTM.TButton', font=self.scaled_font('DejaVu Sans', 10, 'bold'), padding=(18, 13))",
    "style.configure('ZTM.TButton', font=self.scaled_font('DejaVu Sans', 10, 'bold'), padding=((9, 7) if self._font_zoom < 1.15 else (18, 13)))", "button padding")
one("self.label(bar, 'ZTM', 23, CYAN, True)",
    "self.label(bar, 'ZTM', 20 if self._initial_width < 1050 else 23, CYAN, True)", "brand size")
one("self.label(bar, '  ZERO TO MONERO  |  I2PS ENGINEERING', 13, WHITE, True)",
    "self.label(bar, '  ZERO TO MONERO  |  I2PS ENGINEERING', 9 if self._initial_width < 1050 else 13, WHITE, True)", "subtitle size")
one("self.label(release_box, 'Linux x86-64 · Stable Release V1.2', 10, MUTED, True)",
    "self.label(release_box, 'Linux x86-64 · Stable Release V1.2', 8 if self._initial_width < 1050 else 10, MUTED, True)", "release size")
one("self.label(release_box, 'CPU Threads: Auto', 9, CYAN, True)",
    "self.label(release_box, 'CPU Threads: Auto', 8 if self._initial_width < 1050 else 9, CYAN, True)", "thread label size")
one("wraplength=max(600, int(self.root.winfo_screenwidth() * 0.80))",
    "wraplength=max(450, self._initial_width - 85)", "preparation wrapping")
one("wraplength=990, justify='left'",
    "wraplength=max(420, self._initial_width - 85), justify='left'", "consent wrapping")

assert "'ZTM-SRP1V2" in g and "self.upgrade_all" in g
p.write_text(g, encoding="utf-8")
print("Applied SRP1V2 display auto-scaling; no other application files modified.")
