#!/usr/bin/env python3
"""Tests for all five project-control classifications and central profiles."""

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

DEFAULT_WORKFLOW = """\
name: Project control
on: [push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - run: python scripts/validate_project_control.py
"""

CANON_COMMAND = (
    "python3 scripts/validate_project_control.py "
    "--repository armpitpete/canon-garden"
)

CANON_WORKFLOW = f"""\
name: Canon Garden CI
on: [push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - run: {CANON_COMMAND}
"""

VALIDATOR = """\
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--repository")
parser.parse_args()
print("PASS: fixture validator")
raise SystemExit(0)
"""

FAILING_VALIDATOR = """\
print("FAIL: fixture drift")
raise SystemExit(1)
"""

MUTATING_VALIDATOR = """\
from pathlib import Path
Path("validator-created.txt").write_text("mutation", encoding="utf-8")
print("PASS: but mutated")
raise SystemExit(0)
"""


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stdout)
    return completed.stdout


def make_status(slug: str, status: str, *, canon_like: bool = False) -> str:
    project_name = "Canon Garden" if canon_like else slug
    project_type = "application" if canon_like else "system"
    return (
        "---\n"
        "completion_authority: true\n"
        "standard: Recursive Project Improvement Standard v1.0\n"
        f"project_slug: {slug}\n"
        f"project_name: {project_name}\n"
        f"project_type: {project_type}\n"
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
    remote: str | None = None,
    add_remote: bool = True,
    canon_profile: bool = False,
    status_slug: str | None = None,
    workflow_text: str | None = None,
) -> Path:
    repo = root / name
    repo.mkdir()
    git(repo, "init")
    if add_remote:
        remote_url = remote or f"https://github.com/armpitpete/{name}.git"
        git(repo, "remote", "add", "origin", remote_url)
    if not managed:
        (repo / "README.md").write_text("# unmanaged\n", encoding="utf-8")
        return repo

    slug = status_slug or ("canon-garden" if canon_profile else name)
    (repo / "scripts").mkdir()
    (repo / "docs" / "authority").mkdir(parents=True)
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / "AGENTS.md").write_text(AGENTS, encoding="utf-8")
    (repo / "STATUS.md").write_text(
        make_status(slug, status, canon_like=canon_profile), encoding="utf-8"
    )
    (repo / "docs" / "authority" / "AUTHORITY.md").write_text(
        AUTHORITY, encoding="utf-8"
    )
    (repo / "scripts" / "validate_project_control.py").write_text(
        validator, encoding="utf-8"
    )

    if canon_profile:
        (repo / "scripts" / "ci-guardrail-check.js").write_text(
            'console.log("PASS");\n', encoding="utf-8"
        )
        workflow_name = "validate-entries.yml"
        workflow = workflow_text if workflow_text is not None else CANON_WORKFLOW
    else:
        workflow_name = "project-control.yml"
        workflow = workflow_text if workflow_text is not None else DEFAULT_WORKFLOW

    (repo / ".github" / "workflows" / workflow_name).write_text(
        workflow, encoding="utf-8"
    )
    return repo


def classify(repo: Path, *, run_validators: bool = True):
    return AUDIT.classify_repository(
        repo, owner="armpitpete", run_validators=run_validators
    )


class ClassificationTests(unittest.TestCase):
    def test_default_profile_is_unchanged(self) -> None:
        self.assertEqual(
            AUDIT.DEFAULT_PROFILE.required_files,
            (
                "AGENTS.md",
                "STATUS.md",
                "docs/authority/AUTHORITY.md",
                "scripts/validate_project_control.py",
                ".github/workflows/project-control.yml",
            ),
        )
        self.assertEqual(
            AUDIT.DEFAULT_PROFILE.workflow_path,
            ".github/workflows/project-control.yml",
        )
        self.assertIsNone(AUDIT.DEFAULT_PROFILE.exact_workflow_files)
        self.assertIsNone(AUDIT.DEFAULT_PROFILE.exact_validator_command)

    def test_all_five_states(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repos = {
                "controlled": create_repo(root, "controlled", status="IMPLEMENTING"),
                "bootstrap": create_repo(root, "bootstrap", status="BOOTSTRAP"),
                "blocked": create_repo(root, "blocked", status="BLOCKED"),
                "unmanaged": create_repo(root, "unmanaged", managed=False),
                "drifted": create_repo(
                    root,
                    "drifted",
                    status="IMPLEMENTING",
                    validator=FAILING_VALIDATOR,
                ),
            }
            results = {name: classify(repo) for name, repo in repos.items()}
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
            for classification_name in AUDIT.CLASSIFICATIONS:
                self.assertIn(f"**{classification_name}:** 1", report)

    def test_duplicate_completion_authority_is_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = create_repo(root, "duplicate-authority")
            (repo / "SECOND_STATUS.md").write_text(
                "---\ncompletion_authority: true\n---\n", encoding="utf-8"
            )
            result = classify(repo)
            self.assertEqual(result.classification, "DRIFTED")
            self.assertTrue(
                any("completion authority" in reason for reason in result.reasons)
            )

    def test_verified_canon_garden_profile_is_controlled(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = create_repo(Path(temp), "canon-garden", canon_profile=True)
            result = classify(repo)
            self.assertEqual(result.repository, "armpitpete/canon-garden")
            self.assertEqual(result.classification, "CONTROLLED")

    def test_canon_garden_missing_guardrail_is_unmanaged(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = create_repo(Path(temp), "canon-garden", canon_profile=True)
            (repo / "scripts" / "ci-guardrail-check.js").unlink()
            result = classify(repo)
            self.assertEqual(result.classification, "UNMANAGED")
            self.assertTrue(
                any("scripts/ci-guardrail-check.js" in reason for reason in result.reasons)
            )

    def test_canon_garden_competing_workflow_is_drifted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = create_repo(Path(temp), "canon-garden", canon_profile=True)
            (repo / ".github" / "workflows" / "project-control.yml").write_text(
                DEFAULT_WORKFLOW, encoding="utf-8"
            )
            result = classify(repo)
            self.assertEqual(result.classification, "DRIFTED")
            self.assertTrue(any("workflow file set" in reason for reason in result.reasons))

    def test_canon_garden_missing_exact_validator_command_is_drifted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = create_repo(
                Path(temp),
                "canon-garden",
                canon_profile=True,
                workflow_text="name: Canon Garden CI\non: [push]\n",
            )
            result = classify(repo)
            self.assertEqual(result.classification, "DRIFTED")
            self.assertTrue(any("found 0" in reason for reason in result.reasons))

    def test_canon_garden_altered_identity_argument_is_drifted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            altered = CANON_WORKFLOW.replace(
                "armpitpete/canon-garden", "armpitpete/not-canon-garden"
            )
            repo = create_repo(
                Path(temp),
                "canon-garden",
                canon_profile=True,
                workflow_text=altered,
            )
            result = classify(repo)
            self.assertEqual(result.classification, "DRIFTED")
            self.assertTrue(any("found 0" in reason for reason in result.reasons))

    def test_canon_garden_duplicate_exact_command_is_drifted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            duplicated = CANON_WORKFLOW + f"\n# duplicate\n# {CANON_COMMAND}\n"
            repo = create_repo(
                Path(temp),
                "canon-garden",
                canon_profile=True,
                workflow_text=duplicated,
            )
            result = classify(repo)
            self.assertEqual(result.classification, "DRIFTED")
            self.assertTrue(any("found 2" in reason for reason in result.reasons))

    def test_non_canon_repository_with_integrated_workflow_is_unmanaged(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = create_repo(
                Path(temp),
                "not-canon",
                canon_profile=True,
                status_slug="not-canon",
                remote="https://github.com/armpitpete/not-canon.git",
            )
            result = classify(repo)
            self.assertEqual(result.classification, "UNMANAGED")
            self.assertTrue(
                any(".github/workflows/project-control.yml" in reason
                    for reason in result.reasons)
            )

    def test_folder_name_cannot_activate_profile_for_different_remote(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = create_repo(
                Path(temp),
                "canon-garden",
                canon_profile=True,
                status_slug="different-repository",
                remote="https://github.com/armpitpete/different-repository.git",
            )
            result = classify(repo)
            self.assertEqual(result.repository, "armpitpete/different-repository")
            self.assertEqual(result.classification, "UNMANAGED")

    def test_folder_name_without_remote_cannot_activate_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = create_repo(
                Path(temp),
                "canon-garden",
                canon_profile=True,
                add_remote=False,
            )
            result = classify(repo)
            self.assertEqual(result.repository, "armpitpete/canon-garden")
            self.assertEqual(result.classification, "UNMANAGED")
            self.assertTrue(
                any("origin remote is missing" in reason for reason in result.reasons)
            )

    def test_unparseable_remote_cannot_activate_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = create_repo(
                Path(temp),
                "canon-garden",
                canon_profile=True,
                remote="file:///not/a/github/remote",
            )
            result = classify(repo)
            self.assertEqual(result.classification, "UNMANAGED")
            self.assertTrue(
                any("could not be normalised" in reason for reason in result.reasons)
            )

    def test_status_self_declaration_cannot_activate_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = create_repo(
                Path(temp),
                "declared-canon",
                canon_profile=True,
                status_slug="canon-garden",
                remote="https://github.com/armpitpete/declared-canon.git",
            )
            result = classify(repo)
            self.assertEqual(result.repository, "armpitpete/declared-canon")
            self.assertEqual(result.classification, "UNMANAGED")

    def test_validator_execution_preserves_clean_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = create_repo(Path(temp), "read-only-validator")
            git(repo, "config", "user.name", "Fixture")
            git(repo, "config", "user.email", "fixture@example.invalid")
            git(repo, "config", "commit.gpgsign", "false")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "fixture")
            before = AUDIT.git_status(repo)
            result = classify(repo)
            after = AUDIT.git_status(repo)
            self.assertEqual(result.classification, "CONTROLLED")
            self.assertEqual(before, "")
            self.assertEqual(after, before)

    def test_mutating_validator_is_drifted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = create_repo(
                Path(temp), "mutating-validator", validator=MUTATING_VALIDATOR
            )
            result = classify(repo)
            self.assertEqual(result.classification, "DRIFTED")
            self.assertTrue(
                any("read-only contract failed" in reason for reason in result.reasons)
            )


if __name__ == "__main__":
    unittest.main()
