#!/usr/bin/env python3
"""Validate the repository-level project-control structure."""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID_STATUSES = {
    "UNASSESSED", "DIAGNOSTIC", "DESIGN", "AUTHORISED", "IMPLEMENTING",
    "VALIDATING", "REVIEW", "READY", "AUTHORITATIVE", "BLOCKED",
    "SUPERSEDED", "CLOSED", "BOOTSTRAP",
}
REQUIRED_FILES = [
    "AGENTS.md",
    "STATUS.md",
    "docs/authority/AUTHORITY.md",
    "scripts/validate_project_control.py",
    "scripts/audit_project_controls.py",
    "scripts/test_audit_project_controls.py",
    "tools/New-OrderProject.ps1",
    "tools/Run-ProjectControlAudit.ps1",
    "tools/Prove-Central-Project-Control.ps1",
    "tools/Install-Central-Project-Control.ps1",
    ".github/workflows/project-control.yml",
]
REQUIRED_STATUS_HEADINGS = [
    "Current authority", "Current lane", "Allowed scope", "Forbidden changes",
    "Validation", "Done", "To do", "Next bounded gate", "Stop point",
]
REQUIRED_AUTHORITY_HEADINGS = [
    "Source authority", "Active authority", "Decision authority",
    "Completion authority", "Governing constraints",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repository",
        default=os.environ.get("GITHUB_REPOSITORY", "armpitpete/project-folder-checker"),
    )
    return parser.parse_args()


def front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML front matter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("unterminated YAML front matter")
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line or line.startswith(" ") or line.lstrip().startswith("-"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def markdown_files() -> list[Path]:
    ignored = {".git", ".venv", "node_modules", "vendor", "dist", "build"}
    return [
        path for path in ROOT.rglob("*.md")
        if not any(part in ignored for part in path.parts)
    ]


def main() -> int:
    args = parse_args()
    failures: list[str] = []

    if args.repository != "armpitpete/project-folder-checker":
        failures.append(
            "repository identity must be armpitpete/project-folder-checker; "
            f"found {args.repository!r}"
        )

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            failures.append(f"missing required file: {relative}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    status_text = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    authority_text = (ROOT / "docs/authority/AUTHORITY.md").read_text(encoding="utf-8")

    try:
        meta = front_matter(status_text)
    except ValueError as exc:
        failures.append(f"STATUS.md {exc}")
        meta = {}

    if meta.get("completion_authority") != "true":
        failures.append("STATUS.md must declare completion_authority: true")
    if meta.get("standard") != "Recursive Project Improvement Standard v1.0":
        failures.append("STATUS.md names the wrong parent standard")
    if meta.get("project_slug") != "project-folder-checker":
        failures.append("STATUS.md project_slug must be project-folder-checker")
    if meta.get("template_mode") != "false":
        failures.append("STATUS.md template_mode must be false")
    if meta.get("status") not in VALID_STATUSES:
        failures.append(f"invalid status: {meta.get('status')!r}")

    for heading in REQUIRED_STATUS_HEADINGS:
        count = len(re.findall(rf"(?m)^## {re.escape(heading)}\s*$", status_text))
        if count != 1:
            failures.append(
                f"STATUS.md must contain exactly one ## {heading}; found {count}"
            )

    for heading in REQUIRED_AUTHORITY_HEADINGS:
        count = len(re.findall(rf"(?m)^## {re.escape(heading)}\s*$", authority_text))
        if count != 1:
            failures.append(
                "docs/authority/AUTHORITY.md must contain exactly one "
                f"## {heading}; found {count}"
            )

    if "entry_authority: true" not in agents_text:
        failures.append("AGENTS.md must declare entry_authority: true")
    if "Fixed new-chat bootstrap" not in agents_text:
        failures.append("AGENTS.md must include the fixed new-chat bootstrap")

    claims: list[str] = []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        try:
            metadata = front_matter(text)
        except ValueError:
            metadata = {}
        if metadata.get("completion_authority") == "true":
            claims.append(path.relative_to(ROOT).as_posix())
    if claims != ["STATUS.md"]:
        failures.append(
            "exactly root STATUS.md must claim completion authority; found "
            + ", ".join(claims)
        )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print(f"Project control failed with {len(failures)} error(s).")
        return 1

    print("PASS: project-folder-checker project control is valid")
    print(f"repository={args.repository}")
    print(f"status={meta.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
