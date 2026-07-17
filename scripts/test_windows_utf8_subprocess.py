#!/usr/bin/env python3
"""Windows-safe regression for UTF-8 decoding of external command output."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("build_existing_repository_migration_register.py")


def load_importer_module():
    spec = importlib.util.spec_from_file_location("migration_register_importer_utf8_probe", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load importer module: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    importer = load_importer_module()
    completed = importer.run([
        sys.executable,
        "-c",
        "import sys; sys.stdout.buffer.write(bytes([0xD1, 0x9D]) + b' migration')",
    ])
    expected = "\u045d migration"
    if completed.returncode != 0:
        raise SystemExit(f"child command failed with exit {completed.returncode}")
    if completed.stdout != expected:
        raise SystemExit(
            f"UTF-8 decode mismatch: expected {expected!r}, got {completed.stdout!r}"
        )
    print("PASS: external command output decoded as UTF-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
