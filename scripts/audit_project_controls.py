#!/usr/bin/env python3
"""Audit project-control state across local Git repositories.

The auditor is report-only. It never edits a scanned repository.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

DEFAULT_ROOT = Path(r"I:\ORDER\GitHub")
DEFAULT_OUTPUT = Path(r"I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md")
PARENT_STANDARD = "Recursive Project Improvement Standard v1.0"
CLASSIFICATIONS = ("CONTROLLED", "BOOTSTRAP", "DRIFTED", "UNMANAGED", "BLOCKED")
VALID_STATUSES = {
    "UNASSESSED", "DIAGNOSTIC", "DESIGN", "AUTHORISED", "IMPLEMENTING",
    "VALIDATING", "REVIEW", "READY", "AUTHORITATIVE", "BLOCKED",
    "SUPERSEDED", "CLOSED", "BOOTSTRAP",
}
REQUIRED_FILES = (
    "AGENTS.md",
    "STATUS.md",
    "docs/authority/AUTHORITY.md",
    "scripts/validate_project_control.py",
    ".github/workflows/project-control.yml",
)
REQUIRED_STATUS_HEADINGS = (
    "Current authority", "Current lane", "Allowed scope", "Forbidden changes",
    "Validation", "Done", "To do", "Next bounded gate", "Stop point",
)
REQUIRED_AUTHORITY_HEADINGS = (
    "Source authority", "Active authority", "Decision authority",
    "Completion authority", "Governing constraints",
)
SEVERITY_ORDER = {
    "BLOCKED": 0,
    "UNMANAGED": 1,
    "DRIFTED": 2,
    "BOOTSTRAP": 3,
    "CONTROLLED": 4,
}


@dataclasses.dataclass(frozen=True)
class AuditResult:
    name: str
    path: Path
    repository: str
    classification: str
    declared_status: str
    work_blocked: bool
    reasons: tuple[str, ...]
    validator_summary: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--owner", default="armpitpete")
    parser.add_argument("--skip-repository-validators", action="store_true")
    parser.add_argument("--fail-on-control-problems", action="store_true")
    return parser.parse_args()


def run(command: list[str], *, cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


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


def heading_count(text: str, heading: str) -> int:
    return len(re.findall(rf"(?m)^## {re.escape(heading)}\s*$", text))


def markdown_files(root: Path) -> list[Path]:
    ignored = {
        ".git", ".venv", "venv", "node_modules", "vendor",
        "dist", "build", "__pycache__",
    }
    return [
        path for path in root.rglob("*.md")
        if not any(part in ignored for part in path.parts)
    ]


def repository_identity(repo: Path, owner: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    completed = run(["git", "config", "--get", "remote.origin.url"], cwd=repo)
    remote = completed.stdout.strip()
    if completed.returncode != 0 or not remote:
        notes.append("origin remote is missing; identity inferred from folder name")
        return f"{owner}/{repo.name}", notes
    patterns = (
        r"github\.com[:/](?P<slug>[^/\s]+/[^/\s]+?)(?:\.git)?$",
        r"api\.github\.com/repos/(?P<slug>[^/\s]+/[^/\s]+)$",
    )
    for pattern in patterns:
        match = re.search(pattern, remote)
        if match:
            return match.group("slug"), notes
    notes.append(f"origin remote could not be normalised: {remote}")
    return f"{owner}/{repo.name}", notes


def git_status(repo: Path) -> str:
    completed = run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=repo
    )
    if completed.returncode != 0:
        return f"<git-status-error:{completed.returncode}>"
    return completed.stdout


def completion_claims(repo: Path) -> list[str]:
    claims: list[str] = []
    for path in markdown_files(repo):
        try:
            metadata = front_matter(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValueError):
            continue
        if metadata.get("completion_authority") == "true":
            claims.append(path.relative_to(repo).as_posix())
    return sorted(claims)


def static_checks(repo: Path, repository: str) -> tuple[list[str], dict[str, str]]:
    failures: list[str] = []
    metadata: dict[str, str] = {}
    missing = [relative for relative in REQUIRED_FILES if not (repo / relative).is_file()]
    if missing:
        return [f"missing required file: {item}" for item in missing], metadata

    try:
        status_text = (repo / "STATUS.md").read_text(encoding="utf-8")
        agents_text = (repo / "AGENTS.md").read_text(encoding="utf-8")
        authority_text = (repo / "docs/authority/AUTHORITY.md").read_text(encoding="utf-8")
        workflow_text = (repo / ".github/workflows/project-control.yml").read_text(
            encoding="utf-8"
        )
    except (OSError, UnicodeDecodeError) as exc:
        return [f"required control file could not be read: {exc}"], metadata

    try:
        metadata = front_matter(status_text)
    except ValueError as exc:
        failures.append(f"STATUS.md {exc}")

    if metadata.get("completion_authority") != "true":
        failures.append("STATUS.md must declare completion_authority: true")
    if metadata.get("standard") != PARENT_STANDARD:
        failures.append(f"STATUS.md must name {PARENT_STANDARD}")
    status = metadata.get("status", "")
    if status not in VALID_STATUSES:
        failures.append(f"invalid or missing status: {status!r}")

    template_mode = metadata.get("template_mode")
    if template_mode not in {"true", "false"}:
        failures.append("template_mode must be true or false")
    if template_mode == "true" and repository != "armpitpete/project-template":
        failures.append("template_mode: true is allowed only for armpitpete/project-template")
    if template_mode == "false":
        slug = metadata.get("project_slug", "")
        if not slug or slug == "project-template":
            failures.append("generated repository identity has not been initialized")
        if repository.split("/", 1)[-1] != slug:
            failures.append(f"project_slug {slug!r} does not match repository {repository!r}")

    for heading in REQUIRED_STATUS_HEADINGS:
        count = heading_count(status_text, heading)
        if count != 1:
            failures.append(f"STATUS.md must contain exactly one ## {heading}; found {count}")
    for heading in REQUIRED_AUTHORITY_HEADINGS:
        count = heading_count(authority_text, heading)
        if count != 1:
            failures.append(
                "docs/authority/AUTHORITY.md must contain exactly one "
                f"## {heading}; found {count}"
            )

    if "entry_authority: true" not in agents_text:
        failures.append("AGENTS.md must declare entry_authority: true")
    if "Fixed new-chat bootstrap" not in agents_text:
        failures.append("AGENTS.md must include the fixed new-chat bootstrap")
    if PARENT_STANDARD not in agents_text:
        failures.append(f"AGENTS.md must name {PARENT_STANDARD}")

    claims = completion_claims(repo)
    if claims != ["STATUS.md"]:
        failures.append(
            "exactly root STATUS.md must claim completion authority; found "
            + (", ".join(claims) if claims else "none")
        )
    if "validate_project_control.py" not in workflow_text:
        failures.append("project-control workflow must invoke validate_project_control.py")
    return failures, metadata


def run_repository_validator(repo: Path, repository: str) -> tuple[bool, str, list[str]]:
    before = git_status(repo)
    completed = run(
        [sys.executable, str(repo / "scripts/validate_project_control.py"),
         "--repository", repository],
        cwd=repo,
        timeout=90,
    )
    after = git_status(repo)
    reasons: list[str] = []
    output = completed.stdout.strip()
    summary = output.splitlines()[-1] if output else f"exit={completed.returncode}"
    if before != after:
        reasons.append("repository validator changed the worktree; read-only contract failed")
    if completed.returncode != 0:
        excerpt = " | ".join(output.splitlines()[-5:]) if output else "no output"
        reasons.append(f"repository validator failed with exit {completed.returncode}: {excerpt}")
        return False, summary, reasons
    return True, summary, reasons


def classify_repository(repo: Path, *, owner: str, run_validators: bool) -> AuditResult:
    repository, identity_notes = repository_identity(repo, owner)
    missing = [relative for relative in REQUIRED_FILES if not (repo / relative).is_file()]
    if missing:
        reasons = tuple(identity_notes + [f"missing required file: {item}" for item in missing])
        return AuditResult(
            repo.name, repo, repository, "UNMANAGED", "", True, reasons, "not run"
        )

    failures, metadata = static_checks(repo, repository)
    validator_summary = "static checks only"
    if run_validators:
        ok, validator_summary, validator_reasons = run_repository_validator(repo, repository)
        if not ok:
            failures.extend(validator_reasons)

    reasons = identity_notes + failures
    declared_status = metadata.get("status", "")
    if failures:
        classification, blocked = "DRIFTED", True
    elif declared_status == "BLOCKED":
        classification, blocked = "BLOCKED", True
    elif declared_status in {"BOOTSTRAP", "UNASSESSED"}:
        classification, blocked = "BOOTSTRAP", False
    else:
        classification, blocked = "CONTROLLED", False
    return AuditResult(
        repo.name, repo, repository, classification, declared_status,
        blocked, tuple(reasons), validator_summary,
    )


def find_repositories(root: Path) -> list[Path]:
    if not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")
    return sorted(
        path for path in root.iterdir()
        if path.is_dir() and (path / ".git").exists()
    )


def escape_table(text: str) -> str:
    return text.replace("|", r"\|").replace("\n", " ")


def build_report(root: Path, results: list[AuditResult]) -> str:
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    counts = Counter(result.classification for result in results)
    blocked_count = sum(result.work_blocked for result in results)
    report = [
        "---",
        f"standard: {PARENT_STANDARD}",
        "role: project-control-audit",
        f"generated: {now}",
        f"repository_root: {root}",
        f"repository_count: {len(results)}",
        f"work_blocked_count: {blocked_count}",
        "---", "", "# Project Control Audit", "",
        f"Generated: `{now}`", f"Repository root: `{root}`", "",
        "## Summary", "",
    ]
    for classification in CLASSIFICATIONS:
        report.append(f"- **{classification}:** {counts[classification]}")
    report.extend([
        f"- **Repositories where project work is blocked:** {blocked_count}", "",
        "## Classification contract", "",
        "- `CONTROLLED` — mandatory control structure and validator pass.",
        "- `BOOTSTRAP` — controls pass; source authority is not yet established.",
        "- `DRIFTED` — controls exist but conflict, fail validation or contain stale identity.",
        "- `UNMANAGED` — one or more mandatory control files are absent.",
        "- `BLOCKED` — controls pass and the authoritative project status is explicitly blocked.",
        "", "## Repository results", "",
        "| Classification | Repository | Declared status | Work blocked | Validator |",
        "|---|---|---|---|---|",
    ])
    ordered = sorted(
        results,
        key=lambda item: (SEVERITY_ORDER[item.classification], item.repository.lower()),
    )
    for result in ordered:
        report.append(
            "| " + " | ".join((
                result.classification,
                f"`{escape_table(result.repository)}`",
                escape_table(result.declared_status or "—"),
                "YES" if result.work_blocked else "NO",
                escape_table(result.validator_summary),
            )) + " |"
        )
    report.extend(["", "## Findings", ""])
    for result in ordered:
        report.extend([
            f"### {result.classification} — `{result.repository}`", "",
            f"- Local path: `{result.path}`",
            f"- Project work blocked: **{'YES' if result.work_blocked else 'NO'}**",
        ])
        if result.reasons:
            report.extend(f"- {reason}" for reason in result.reasons)
        else:
            report.append("- No control defects detected.")
        report.append("")
    report.extend([
        "## Operating rule", "",
        "Project work must not continue in repositories classified as "
        "`UNMANAGED`, `DRIFTED` or `BLOCKED`.", "",
        "This audit is report-only. It does not change any scanned repository.", "",
    ])
    return "\n".join(report)


def main() -> int:
    args = parse_args()
    results = [
        classify_repository(
            repository,
            owner=args.owner,
            run_validators=not args.skip_repository_validators,
        )
        for repository in find_repositories(args.root)
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_report(args.root, results), encoding="utf-8", newline="\n")
    print(f"Wrote project-control audit: {args.output}")
    for classification in CLASSIFICATIONS:
        print(f"{classification}={sum(r.classification == classification for r in results)}")
    problems = any(r.classification in {"UNMANAGED", "DRIFTED"} for r in results)
    return 2 if args.fail_on_control_problems and problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
