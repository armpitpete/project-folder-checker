#!/usr/bin/env python3
"""Tests for all five project-control classifications."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("audit_project_controls.py")
SPEC = importlib.util.spec_from_file_location("audit_project_controls", MODULE_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)

STATUS_HEADINGS = """\
## Current authority

Fixture authority.

## Current lane

Fixture lane.

## Allowed scope

- fixture control files.

## Forbidden changes

- unrelated changes.

## Validation

Run the validator.

## Done

- fixture created.

## To do

- none.

## Next bounded gate

Remain bounded.

## Stop point

Stop before unrelated work.
"""

AUTHORITY = """\
# Repository Authority

## Source authority

Fixture source.

## Active authority

Fixture head.

## Decision authority

Fixture contract.

## Completion authority

Root STATUS.md.

## Governing constraints

Read-only fixture.
"""

AGENTS = """\
---
entry_authority: true
standard: Recursive Project Improvement Standard v1.0
---

# Project Entry Rules

## Fixed new-chat bootstrap

Read STATUS.md before acting.
"""

WORKFLOW = """\
name: Project control
on: [push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - run: python scripts/validate_project_control.py
"""

VALIDATOR = """\
print("PASS: fixture validator")
raise SystemExit(0)
"""

FAILING_VALIDATOR = """\
print("FAIL: fixture drift")
raise SystemExit(1)
"""


def git(repo: Path, *args: str) -> None:
    completed = subprocess.run(
        ["git", *args], cwd=repo, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stdout)


def make_status(slug: str, status: str) -> str:
    return (
        "---\n"
        "completion_authority: true\n"
        "standard: Recursive Project Improvement Standard v1.0\n"
        f"project_slug: {slug}\n"
        f"project_name: {slug}\n"
        "project_type: system\n"
        "template_mode: false\n"
        f"status: {status}\n"
        "---\n\n"
        "# Project Status\n\n"
        + STATUS_HEADINGS
    )


def create_repo(
    root: Path,
    name: str,
    *,
    status: str = "IMPLEMENTING",
    validator: str = VALIDATOR,
    managed: bool = True,
) -> Path:
    repo = root / name
    repo.mkdir()
    git(repo, "init")
    git(repo, "remote", "add", "origin", f"https://github.com/armpitpete/{name}.git")
    if not managed:
        (repo / "README.md").write_text("# unmanaged\n", encoding="utf-8")
        return repo

    (repo / "scripts").mkdir()
    (repo / "docs" / "authority").mkdir(parents=True)
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / "AGENTS.md").write_text(AGENTS, encoding="utf-8")
    (repo / "STATUS.md").write_text(make_status(name, status), encoding="utf-8")
    (repo / "docs" / "authority" / "AUTHORITY.md").write_text(
        AUTHORITY, encoding="utf-8"
    )
    (repo / "scripts" / "validate_project_control.py").write_text(
        validator, encoding="utf-8"
    )
    (repo / ".github" / "workflows" / "project-control.yml").write_text(
        WORKFLOW, encoding="utf-8"
    )
    return repo


class ClassificationTests(unittest.TestCase):
    def test_all_five_states(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repos = {
                "controlled": create_repo(root, "controlled", status="IMPLEMENTING"),
                "bootstrap": create_repo(root, "bootstrap", status="BOOTSTRAP"),
                "blocked": create_repo(root, "blocked", status="BLOCKED"),
                "unmanaged": create_repo(root, "unmanaged", managed=False),
                "drifted": create_repo(
                    root, "drifted", status="IMPLEMENTING", validator=FAILING_VALIDATOR
                ),
            }
            results = {
                name: AUDIT.classify_repository(
                    repo, owner="armpitpete", run_validators=True
                )
                for name, repo in repos.items()
            }
            self.assertEqual(results["controlled"].classification, "CONTROLLED")
            self.assertEqual(results["bootstrap"].classification, "BOOTSTRAP")
            self.assertEqual(results["blocked"].classification, "BLOCKED")
            self.assertEqual(results["unmanaged"].classification, "UNMANAGED")
            self.assertEqual(results["drifted"].classification, "DRIFTED")
            self.assertFalse(results["controlled"].work_blocked)
            self.assertFalse(results["bootstrap"].work_blocked)
            self.assertTrue(results["blocked"].work_blocked)
            self.assertTrue(results["unmanaged"].work_blocked)
            self.assertTrue(results["drifted"].work_blocked)
            report = AUDIT.build_report(root, list(results.values()))
            for classification in AUDIT.CLASSIFICATIONS:
                self.assertIn(f"**{classification}:** 1", report)

    def test_duplicate_completion_authority_is_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = create_repo(root, "duplicate-authority")
            (repo / "SECOND_STATUS.md").write_text(
                "---\ncompletion_authority: true\n---\n", encoding="utf-8"
            )
            result = AUDIT.classify_repository(
                repo, owner="armpitpete", run_validators=True
            )
            self.assertEqual(result.classification, "DRIFTED")
            self.assertTrue(
                any("completion authority" in reason for reason in result.reasons)
            )


if __name__ == "__main__":
    unittest.main()
