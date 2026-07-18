#!/usr/bin/env python3
"""Regression for cache pruning and inaccessible-path tolerance."""
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).with_name("run_existing_repository_migration_register_safe.py")


def load_runner():
    spec = importlib.util.spec_from_file_location("migration_register_safe_runner_probe", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load safe runner: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    runner = load_runner()
    base = runner.load_base_module()
    root = Path(tempfile.mkdtemp(prefix="migration-register-safe-scan-"))
    try:
        authority = root / "docs" / "authority" / "DECISION.md"
        authority.parent.mkdir(parents=True)
        authority.write_text("# Decision\n", encoding="utf-8")
        cache_file = (
            root / "data" / "fastembed_cache" /
            "models--qdrant--all-MiniLM-L6-v2-onnx" / "AUTHORITY.json"
        )
        cache_file.parent.mkdir(parents=True)
        cache_file.write_text("{}\n", encoding="utf-8")

        candidates, warnings = runner.safe_authority_candidates(base, root)
        if "docs/authority/DECISION.md" not in candidates:
            raise SystemExit("normal authority file was not discovered")
        if any("fastembed_cache" in candidate for candidate in candidates):
            raise SystemExit("generated cache content was not pruned")
        if warnings:
            raise SystemExit(f"unexpected warnings: {warnings!r}")

        def fake_walk(path, *, topdown, onerror, followlinks):
            if Path(path) != root or not topdown or followlinks:
                raise AssertionError("unexpected os.walk arguments")
            onerror(OSError(1920, "cannot access", str(root / "data" / "blocked")))
            yield str(root), [], ["STATUS.md"]

        with mock.patch.object(runner.os, "walk", side_effect=fake_walk):
            candidates, warnings = runner.safe_authority_candidates(base, root)

        if "STATUS.md" not in candidates:
            raise SystemExit("scan did not continue after inaccessible path")
        if len(warnings) != 1 or "filesystem scan skipped inaccessible path" not in warnings[0]:
            raise SystemExit(f"inaccessible path was not recorded: {warnings!r}")

        print("PASS: generated caches pruned; inaccessible paths recorded without abort")
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
