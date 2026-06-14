"""Repository health checks for the Enterprise Data Strategy Agent."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

CRITICAL_PATHS = [
    ("pyproject.toml", "Found pyproject.toml"),
    ("README.md", "Found README.md"),
    ("src/enterprise_data_strategy_agent", "Found Python package"),
    ("data/sample_domo_inventory.json", "Found sample inventory"),
    ("config/sample_strategy_policy.yml", "Found sample policy"),
    ("examples", "Found examples directory"),
]
REQUIRED_IMPORTS = ["yaml"]
OPTIONAL_IMPORTS = ["streamlit"]


def run_doctor(root: Path | None = None) -> int:
    """Run repo checks and return a process-style exit code."""

    cwd = Path.cwd() if root is None else Path(root)
    print(f"Current directory: {cwd}")
    critical_ok = True

    if not (cwd / "pyproject.toml").exists():
        print("[ERROR] You are not in the repo root. cd into the folder containing pyproject.toml.")
        critical_ok = False

    for relative, message in CRITICAL_PATHS:
        path = cwd / relative
        if path.exists():
            print(f"[OK] {message}")
        else:
            print(f"[ERROR] Missing required path: {relative}")
            critical_ok = False

    version = sys.version_info
    if (version.major, version.minor) >= (3, 11):
        print(f"[OK] Python version {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"[ERROR] Python 3.11 or newer is required; found {version.major}.{version.minor}.{version.micro}")
        critical_ok = False

    if not (os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_PREFIX")):
        print("[WARN] Virtual environment may not be active")
    else:
        print("[OK] Virtual environment appears to be active")

    for module_name in REQUIRED_IMPORTS:
        if _can_import(module_name):
            print(f"[OK] Required package can be imported: {module_name}")
        else:
            print(f"[WARN] Required package is not importable in this environment: {module_name}")

    for module_name in OPTIONAL_IMPORTS:
        if _can_import(module_name):
            print(f"[OK] Optional UI package can be imported: {module_name}")
        else:
            print(f"[WARN] Optional UI package is not importable: {module_name}")

    before = set(sys.modules)
    if _can_import("enterprise_data_strategy_agent.cli"):
        print("[OK] CLI module can be imported")
    else:
        print("[ERROR] CLI module cannot be imported")
        critical_ok = False
    imported_by_cli = set(sys.modules) - before
    if "streamlit" in sys.modules and "streamlit" in imported_by_cli:
        print("[ERROR] Streamlit was imported during CLI startup")
        critical_ok = False
    else:
        print("[OK] Streamlit is not imported by CLI startup")

    return 0 if critical_ok else 1


def _can_import(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except Exception:
        return False


def main() -> int:
    """Entry point for ``python -m enterprise_data_strategy_agent.doctor``."""

    return run_doctor()


if __name__ == "__main__":
    raise SystemExit(main())
