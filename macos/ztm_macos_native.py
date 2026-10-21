"""Per-platform child invocation for native macOS ZTM-SRP1V1."""
from __future__ import annotations
import sys
from pathlib import Path

def component_command(component: str, *args: str) -> list[str]:
    if component not in {"engine", "mining", "prepare", "guard"}:
        raise ValueError("Unknown ZTM component")
    if getattr(sys, "frozen", False):
        return [sys.executable, "--ztm-" + component, *args]
    directory = Path(__file__).resolve().parent
    path = directory / ("ztm_" + component + ".py")
    if component in {"prepare", "guard"}:
        path = directory / ("ztm_macos_" + component + ".py")
    return [sys.executable, "-u", str(path), *args]
