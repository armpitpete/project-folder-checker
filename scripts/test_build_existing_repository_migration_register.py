#!/usr/bin/env python3
"""Regression tests for the read-only existing-repository migration importer."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("build_existing_repository_migration_register.py")


def run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=cwd, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )


class MigrationRegisterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="migration-register-test-"))
        self.root = self.temp / "GitHub"
        self.root.mkdir()
        self.entries: list[tuple[str, Path]] = []
        for index in range(1, 20):
            name = f"repo-{index:02d}"
            path = self.root / name
            path.mkdir()
            self.assertEqual(run(["git", "init", "-b", "main"], cwd=path).returncode, 0)
            run(["git", "config", "user.email", "test@example.com"], cwd=path)
            run(["git", "config", "user.name", "Test"], cwd=path)
            (path / "README.md").write_text(f"# {name}\n", encoding="utf-8")
            run(["git", "add", "README.md"], cwd=path)
            self.assertEqual(run(["git", "commit", "-m", "Initial"], cwd=path).returncode, 0)
            run([
                "git", "remote", "add", "origin",
                f"https://github.com/armpitpete/{name}.git",
            ], cwd=path)
            self.entries.append((f"armpitpete/{name}", path))

        self.audit = self.temp / "PROJECT_CONTROL_AUDIT.md"
        lines = [
            "---", "role: project-control-audit", "---", "",
            "# Project Control Audit", "", "## Findings", "",
        ]
        for repository, path in self.entries:
            lines.extend([
                f"### UNMANAGED — `{repository}`", "",
                f"- Local path: `{path}`",
                "- Project work blocked: **YES**",
                "- missing required file: AGENTS.md", "",
            ])
        lines.extend(["## Operating rule", "", "Stop."])
        self.audit.write_text("\n".join(lines), encoding="utf-8")
        self.active = self.temp / "ACTIVE_WORK.md"
        self.active.write_text("# Active\n\n- `armpitpete/repo-01`\n", encoding="utf-8")
        self.output = self.temp / "REGISTER.md"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp)

    def command(self, expected: int = 19) -> list[str]:
        return [
            "python", str(SCRIPT),
            "--audit", str(self.audit),
            "--active-work", str(self.active),
            "--output", str(self.output),
            "--expected-count", str(expected),
            "--skip-github",
        ]

    def test_imports_exact_nineteen_without_worktree_changes(self) -> None:
        completed = run(self.command())
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        text = self.output.read_text(encoding="utf-8")
        self.assertIn("repository_count: 19", text)
        self.assertIn("### 19.", text)
        self.assertIn("TARGET_REPOSITORIES_CHANGED=0", completed.stdout)
        for _, path in self.entries:
            status = run(["git", "status", "--porcelain=v1"], cwd=path)
            self.assertEqual(status.stdout, "", f"worktree changed: {path}\n{status.stdout}")

    def test_rejects_count_mismatch(self) -> None:
        completed = run(self.command(expected=18))
        self.assertEqual(completed.returncode, 2)
        self.assertIn("expected 18 UNMANAGED repositories, found 19", completed.stderr)


if __name__ == "__main__":
    unittest.main()
