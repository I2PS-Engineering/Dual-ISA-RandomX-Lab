#!/usr/bin/env python3
"""Single-entry-point launcher for the native ZTM macOS app and its child modes.

The frozen app launches its own embedded Python runtime with --ztm-child.
No external Python installation is required for the distributed .app.
"""
from __future__ import annotations

import sys


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args[:1] != ["--ztm-child"]:
        if args:
            raise SystemExit("ZTM does not support interactive command-line benchmark overrides.")
        from ztm_gui import main as run_gui
        return run_gui()

    if len(args) < 2:
        raise SystemExit("Missing ZTM internal component.")
    mode = args[1]
    rest = args[2:]
    if mode == "prepare":
        from ztm_native import main as prepare
        return prepare(["prepare"])
    if mode == "engine":
        from ztm_engine import main as benchmark
        return benchmark(rest)
    if mode == "mining":
        from ztm_mining import main as mine
        return mine(rest)
    if mode == "guardian":
        from ztm_macos_guard import main as guardian
        return guardian(rest)
    raise SystemExit("Unknown ZTM internal mode.")


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result is None else result)
    except (KeyboardInterrupt, OSError, RuntimeError, ValueError) as error:
        print("[ZTM] " + str(error), file=sys.stderr, flush=True)
        raise SystemExit(1)
