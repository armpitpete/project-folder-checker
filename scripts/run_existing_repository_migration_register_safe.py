#!/usr/bin/env python3
"""Run the migration-register importer with Windows-safe repository traversal.

This front-end patches only the read-only filesystem inventory boundary. It
preserves the base importer's audit parsing, Git/GitHub reconciliation,
classification, register generation and no-target-change verification.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

BASE_SCRIPT = Path(__file__).with_name("build_existing_repository_migration_register.py")
IGNORED_DIRECTORY_NAMES = {
    ".git", ".venv", "venv", "node_modules", "vendor", "dist", "build",
    "__pycache__", ".idea", ".vs", "bin", "obj", ".cache", "cache",
    "caches", "fastembed_cache", ".huggingface", "huggingface",
}
AUTHORITY_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".toml"}


def load_base_module():
    spec = importlib.util.spec_from_file_location("migration_register_base", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load base importer: {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def ignored_directory(name: str) -> bool:
    lower = name.lower()
    return (
        lower in IGNORED_DIRECTORY_NAMES
        or lower.endswith("_cache")
        or lower.startswith("models--")
    )


def safe_relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def walk_repository_files(repo: Path) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    warnings: list[str] = []

    def on_error(error: OSError) -> None:
        filename = getattr(error, "filename", None)
        location = safe_relative(Path(filename), repo) if filename else "<unknown>"
        warnings.append(f"filesystem scan skipped inaccessible path: {location}: {error}")

    for root, dirnames, filenames in os.walk(
        repo, topdown=True, onerror=on_error, followlinks=False
    ):
        dirnames[:] = sorted(
            (name for name in dirnames if not ignored_directory(name)),
            key=str.lower,
        )
        root_path = Path(root)
        for filename in sorted(filenames, key=str.lower):
            files.append(root_path / filename)
    return files, warnings


def safe_authority_candidates(base: Any, repo: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    found: list[str] = []
    files, warnings = walk_repository_files(repo)
    for path in files:
        relative = safe_relative(path, repo)
        lower = relative.lower()
        if relative in base.REQUIRED_FILES:
            found.append(relative)
            continue
        if path.suffix.lower() not in AUTHORITY_SUFFIXES:
            continue
        if base.AUTHORITY_NAME_RE.search(path.name) or lower.startswith("docs/authority/"):
            found.append(relative)
    unique = sorted(set(found), key=str.lower)
    limited = unique[:40] + ([f"… plus {len(unique) - 40} more"] if len(unique) > 40 else [])
    return tuple(limited), tuple(warnings)


def safe_workflows(repo: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    root = repo / ".github" / "workflows"
    try:
        if not root.is_dir():
            return (), ()
    except OSError as exc:
        return (), (f"workflow scan failed: {safe_relative(root, repo)}: {exc}",)

    workflows: list[str] = []
    warnings: list[str] = []
    try:
        entries = sorted(root.iterdir(), key=lambda item: item.name.lower())
    except OSError as exc:
        return (), (f"workflow scan failed: {safe_relative(root, repo)}: {exc}",)
    for path in entries:
        try:
            if path.is_file():
                workflows.append(safe_relative(path, repo))
        except OSError as exc:
            warnings.append(
                f"workflow scan skipped inaccessible path: {safe_relative(path, repo)}: {exc}"
            )
    return tuple(workflows), tuple(warnings)


def install_legacy_function_patches(base: Any) -> None:
    """Patch the packaged importer variant that exposes scan helper functions."""

    if not hasattr(base, "find_authority_candidates"):
        return

    def authority_candidates(repo: Path) -> tuple[str, ...]:
        candidates, _warnings = safe_authority_candidates(base, repo)
        return candidates

    def workflows(repo: Path) -> tuple[str, ...]:
        result, _warnings = safe_workflows(repo)
        return result

    base.find_authority_candidates = authority_candidates
    if hasattr(base, "find_workflows"):
        base.find_workflows = workflows


def install_current_local_state_patch(base: Any) -> None:
    """Patch the canonical importer variant whose scan is inline in local_state."""

    if not hasattr(base, "local_state"):
        return

    def local_state(entry: Any) -> tuple[dict[str, Any], list[str]]:
        repo = entry.local_path
        errors: list[str] = []
        try:
            local_exists = repo.is_dir()
        except OSError as exc:
            local_exists = False
            errors.append(f"local path could not be inspected: {repo}: {exc}")
        state: dict[str, Any] = {
            "local_exists": local_exists,
            "git_repository": False,
            "local_head": "",
            "local_branch": "",
            "local_dirty": False,
            "local_status_count": 0,
            "origin_url": "",
            "normalised_remote": "",
            "existing_required_files": (),
            "missing_required_files": base.REQUIRED_FILES,
            "authority_candidates": (),
            "workflow_files": (),
        }
        if not local_exists:
            errors.append(f"local path does not exist: {repo}")
            return state, errors

        probe = base.run_git(repo, ["rev-parse", "--is-inside-work-tree"])
        if probe.returncode != 0 or (probe.stdout or "").strip() != "true":
            errors.append("local path is not a Git worktree")
            return state, errors
        state["git_repository"] = True

        commands = {
            "local_head": ["rev-parse", "HEAD"],
            "local_branch": ["branch", "--show-current"],
            "origin_url": ["config", "--get", "remote.origin.url"],
        }
        for key, args in commands.items():
            completed = base.run_git(repo, args)
            if completed.returncode == 0:
                state[key] = (completed.stdout or "").strip()
            else:
                errors.append(f"git {' '.join(args)} failed with exit {completed.returncode}")

        status = base.run_git(repo, ["status", "--porcelain=v1", "--untracked-files=all"])
        if status.returncode == 0:
            lines = [line for line in (status.stdout or "").splitlines() if line]
            state["local_status_count"] = len(lines)
            state["local_dirty"] = bool(lines)
        else:
            errors.append(f"git status failed with exit {status.returncode}")

        state["normalised_remote"] = base.normalise_remote(state["origin_url"])
        existing: list[str] = []
        for relative in base.REQUIRED_FILES:
            try:
                if (repo / relative).is_file():
                    existing.append(relative)
            except OSError as exc:
                errors.append(f"required-file probe failed: {relative}: {exc}")
        state["existing_required_files"] = tuple(existing)
        state["missing_required_files"] = tuple(
            relative for relative in base.REQUIRED_FILES if relative not in existing
        )

        candidates, scan_warnings = safe_authority_candidates(base, repo)
        workflows, workflow_warnings = safe_workflows(repo)
        state["authority_candidates"] = candidates
        state["workflow_files"] = workflows
        errors.extend(scan_warnings)
        errors.extend(workflow_warnings)
        return state, errors

    base.local_state = local_state


def main() -> int:
    base = load_base_module()
    install_legacy_function_patches(base)
    install_current_local_state_patch(base)
    return int(base.main())


if __name__ == "__main__":
    raise SystemExit(main())
