#!/usr/bin/env python3
"""
Bootstrapper that guarantees a clean virtual environment before running the CSP extractor.

Usage:
    python run_extractor.py        # normal interactive workflow
    python run_extractor.py -- ... # pass extra args to fetch_api_params.py (future-friendly)
"""

from __future__ import annotations

import hashlib
import platform
import subprocess
import sys
import venv
from pathlib import Path
from typing import Iterable


ROOT_DIR = Path(__file__).resolve().parent
VENV_DIR = ROOT_DIR / ".venv"
REQUIREMENTS_FILE = ROOT_DIR / "requirements.txt"
HASH_FILE = VENV_DIR / ".requirements_hash"


def _venv_paths() -> tuple[Path, Path]:
    if platform.system() == "Windows":
        python_path = VENV_DIR / "Scripts" / "python.exe"
        pip_path = VENV_DIR / "Scripts" / "pip.exe"
    else:
        python_path = VENV_DIR / "bin" / "python"
        pip_path = VENV_DIR / "bin" / "pip"
    return python_path, pip_path


def _run(cmd: Iterable[str], **kwargs) -> None:
    subprocess.run(list(cmd), check=True, **kwargs)


def ensure_virtualenv() -> None:
    if VENV_DIR.exists():
        return

    print("🔧 Creating isolated virtual environment in .venv ...")
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(VENV_DIR)


def requirements_hash() -> str:
    data = REQUIREMENTS_FILE.read_bytes()
    return hashlib.sha256(data).hexdigest()


def ensure_dependencies(python_path: Path, pip_path: Path) -> None:
    desired_hash = requirements_hash()
    if HASH_FILE.exists() and HASH_FILE.read_text().strip() == desired_hash:
        return

    print("📦 Installing project requirements inside the virtual environment ...")
    _run(
        [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    _run(
        [str(pip_path), "install", "-r", str(REQUIREMENTS_FILE)],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    HASH_FILE.write_text(desired_hash, encoding="utf-8")


def run_cli(python_path: Path, forward_args: list[str]) -> int:
    command = [str(python_path), str(ROOT_DIR / "fetch_api_params.py"), *forward_args]
    return subprocess.call(command)


def main() -> int:
    if not REQUIREMENTS_FILE.exists():
        print("❌ requirements.txt not found; cannot bootstrap dependencies.", file=sys.stderr)
        return 1

    ensure_virtualenv()
    python_path, pip_path = _venv_paths()

    if not python_path.exists():
        print("❌ Virtual environment looks corrupted; deleting .venv and retrying might help.", file=sys.stderr)
        return 1

    ensure_dependencies(python_path, pip_path)

    try:
        return run_cli(python_path, sys.argv[1:])
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
