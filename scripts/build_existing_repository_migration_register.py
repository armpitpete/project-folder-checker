#!/usr/bin/env python3
"""Build a read-only migration register from PROJECT_CONTROL_AUDIT.md.

This script never edits a scanned repository. It reads local Git metadata and
uses authenticated `gh api` GET requests to reconcile GitHub state.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DEFAULT_AUDIT = Path(r"I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md")
DEFAULT_ACTIVE_WORK = Path(r"I:\ORDER\MainVault\00_Control\ACTIVE_WORK.md")
DEFAULT_OUTPUT = Path(r"I:\ORDER\MainVault\00_Control\EXISTING_REPOSITORY_MIGRATION_REGISTER.md")
EXPECTED_COUNT = 19
REQUIRED_FILES = (
    "AGENTS.md",
    "STATUS.md",
    "docs/authority/AUTHORITY.md",
    "scripts/validate_project_control.py",
    ".github/workflows/project-control.yml",
)
CONTROL_OVERLAP_PATHS = {
    "AGENTS.md",
    "STATUS.md",
    "docs/authority/AUTHORITY.md",
    "scripts/validate_project_control.py",
    ".github/workflows/project-control.yml",
}
IGNORED_DIRS = {
    ".git", ".venv", "venv", "node_modules", "vendor", "dist", "build",
    "__pycache__", ".idea", ".vs", "bin", "obj",
}
AUTHORITY_NAME_RE = re.compile(
    r"(?:^|[_\-.])(status|authority|decision|manifest|agents|governance|roadmap|handoff|completion)(?:[_\-.]|$)",
    re.IGNORECASE,
)
REPO_SLUG_RE = re.compile(r"\b([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\b")
FINDING_RE = re.compile(
    r"(?ms)^### UNMANAGED — `(?P<repository>[^`]+)`\s*\n\n"
    r"(?P<body>.*?)(?=^### |^## Operating rule|\Z)"
)
LOCAL_PATH_RE = re.compile(r"(?m)^- Local path: `(?P<path>[^`]+)`\s*$")
REASON_RE = re.compile(r"(?m)^- (?P<reason>.+)$")


class RegisterError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class AuditEntry:
    repository: str
    local_path: Path
    audit_reasons: tuple[str, ...]


@dataclasses.dataclass
class PullRequestRecord:
    number: int
    title: str
    state: str
    draft: bool
    merged: bool
    head_sha: str
    base_sha: str
    merge_commit_sha: str
    html_url: str
    files: tuple[str, ...]

    @property
    def coverage(self) -> tuple[str, ...]:
        return tuple(sorted(CONTROL_OVERLAP_PATHS.intersection(self.files)))


@dataclasses.dataclass
class RepositoryRecord:
    audit: AuditEntry
    local_exists: bool
    git_repository: bool
    local_head: str
    local_branch: str
    local_dirty: bool
    local_status_count: int
    origin_url: str
    normalised_remote: str
    remote_exists: bool
    remote_archived: bool
    remote_disabled: bool
    remote_default_branch: str
    remote_default_head: str
    local_head_on_remote: bool
    comparison_status: str
    ahead_by: int
    behind_by: int
    active_evidence: bool
    existing_required_files: tuple[str, ...]
    missing_required_files: tuple[str, ...]
    authority_candidates: tuple[str, ...]
    workflow_files: tuple[str, ...]
    control_prs: tuple[PullRequestRecord, ...]
    errors: tuple[str, ...]
    migration_classification: str = ""
    migration_route: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--active-work", type=Path, default=DEFAULT_ACTIVE_WORK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--expected-count", type=int, default=EXPECTED_COUNT)
    parser.add_argument("--owner", default="armpitpete")
    parser.add_argument("--skip-github", action="store_true")
    return parser.parse_args()


def run(command: list[str], *, cwd: Path | None = None, timeout: int = 90) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RegisterError(f"required command is unavailable: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RegisterError(f"command timed out: {' '.join(command)}") from exc


def run_git(repo: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], cwd=repo)


def gh_json(endpoint: str) -> tuple[int, Any | None, str]:
    completed = run(["gh", "api", endpoint], timeout=120)
    output = (completed.stdout or "").strip()
    if completed.returncode != 0:
        return completed.returncode, None, output
    try:
        return 0, json.loads(output), ""
    except json.JSONDecodeError as exc:
        return 1, None, f"invalid JSON from gh api {endpoint}: {exc}: {output[:400]}"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def parse_audit(path: Path, expected_count: int) -> list[AuditEntry]:
    if not path.is_file():
        raise RegisterError(f"audit file does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    entries: list[AuditEntry] = []
    for match in FINDING_RE.finditer(text):
        repository = match.group("repository").strip()
        body = match.group("body")
        path_match = LOCAL_PATH_RE.search(body)
        if not path_match:
            raise RegisterError(f"UNMANAGED finding has no local path: {repository}")
        reasons = []
        for reason_match in REASON_RE.finditer(body):
            reason = reason_match.group("reason").strip()
            if reason.startswith("Local path:") or reason.startswith("Project work blocked:"):
                continue
            reasons.append(reason)
        entries.append(AuditEntry(repository, Path(path_match.group("path")), tuple(reasons)))
    if len(entries) != expected_count:
        raise RegisterError(
            f"expected {expected_count} UNMANAGED repositories, found {len(entries)} in {path}"
        )
    repositories = [entry.repository.lower() for entry in entries]
    if len(set(repositories)) != len(repositories):
        duplicates = sorted(name for name, count in Counter(repositories).items() if count > 1)
        raise RegisterError(f"duplicate repository entries in audit: {', '.join(duplicates)}")
    return sorted(entries, key=lambda item: item.repository.lower())


def active_repositories(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    text = path.read_text(encoding="utf-8", errors="replace")
    return {match.group(1).lower() for match in REPO_SLUG_RE.finditer(text)}


def normalise_remote(remote: str) -> str:
    patterns = (
        r"github\.com[:/](?P<slug>[^/\s]+/[^/\s]+?)(?:\.git)?$",
        r"api\.github\.com/repos/(?P<slug>[^/\s]+/[^/\s]+)$",
    )
    for pattern in patterns:
        match = re.search(pattern, remote)
        if match:
            return match.group("slug")
    return ""


def local_state(entry: AuditEntry) -> tuple[dict[str, Any], list[str]]:
    repo = entry.local_path
    errors: list[str] = []
    state: dict[str, Any] = {
        "local_exists": repo.is_dir(),
        "git_repository": False,
        "local_head": "",
        "local_branch": "",
        "local_dirty": False,
        "local_status_count": 0,
        "origin_url": "",
        "normalised_remote": "",
        "existing_required_files": (),
        "missing_required_files": REQUIRED_FILES,
        "authority_candidates": (),
        "workflow_files": (),
    }
    if not repo.is_dir():
        errors.append(f"local path does not exist: {repo}")
        return state, errors
    probe = run_git(repo, ["rev-parse", "--is-inside-work-tree"])
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        errors.append("local path is not a Git worktree")
        return state, errors
    state["git_repository"] = True

    commands = {
        "local_head": ["rev-parse", "HEAD"],
        "local_branch": ["branch", "--show-current"],
        "origin_url": ["config", "--get", "remote.origin.url"],
    }
    for key, args in commands.items():
        completed = run_git(repo, args)
        if completed.returncode == 0:
            state[key] = completed.stdout.strip()
        else:
            errors.append(f"git {' '.join(args)} failed with exit {completed.returncode}")

    status = run_git(repo, ["status", "--porcelain=v1", "--untracked-files=all"])
    if status.returncode == 0:
        lines = [line for line in status.stdout.splitlines() if line]
        state["local_status_count"] = len(lines)
        state["local_dirty"] = bool(lines)
    else:
        errors.append(f"git status failed with exit {status.returncode}")

    state["normalised_remote"] = normalise_remote(state["origin_url"])
    existing = tuple(relative for relative in REQUIRED_FILES if (repo / relative).is_file())
    state["existing_required_files"] = existing
    state["missing_required_files"] = tuple(
        relative for relative in REQUIRED_FILES if relative not in existing
    )
    authority_candidates: list[str] = []
    workflow_files: list[str] = []
    for path in repo.rglob("*"):
        if not path.is_file() or any(part in IGNORED_DIRS for part in path.parts):
            continue
        relative = path.relative_to(repo).as_posix()
        if relative.startswith(".github/workflows/"):
            workflow_files.append(relative)
        if path.suffix.lower() in {".md", ".json", ".yaml", ".yml"} and AUTHORITY_NAME_RE.search(path.name):
            authority_candidates.append(relative)
    state["authority_candidates"] = tuple(sorted(set(authority_candidates)))
    state["workflow_files"] = tuple(sorted(set(workflow_files)))
    return state, errors


def list_control_prs(repository: str) -> tuple[tuple[PullRequestRecord, ...], list[str]]:
    errors: list[str] = []
    code, payload, diagnostic = gh_json(
        f"repos/{repository}/pulls?state=all&sort=updated&direction=desc&per_page=100"
    )
    if code != 0 or not isinstance(payload, list):
        return (), [f"could not list pull requests: {diagnostic or f'exit {code}'}"]
    records: list[PullRequestRecord] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        number = int(item.get("number", 0))
        title = str(item.get("title", ""))
        head = item.get("head") if isinstance(item.get("head"), dict) else {}
        base = item.get("base") if isinstance(item.get("base"), dict) else {}
        head_sha = str(head.get("sha", ""))
        base_sha = str(base.get("sha", ""))
        files_code, files_payload, files_diag = gh_json(
            f"repos/{repository}/pulls/{number}/files?per_page=100"
        )
        if files_code != 0 or not isinstance(files_payload, list):
            errors.append(
                f"could not inspect files for PR #{number}: {files_diag or f'exit {files_code}'}"
            )
            files = ()
        else:
            files = tuple(
                sorted(
                    str(file.get("filename", ""))
                    for file in files_payload
                    if isinstance(file, dict) and file.get("filename")
                )
            )
        record = PullRequestRecord(
            number=number,
            title=title,
            state=str(item.get("state", "")),
            draft=bool(item.get("draft", False)),
            merged=bool(item.get("merged_at")),
            head_sha=head_sha,
            base_sha=base_sha,
            merge_commit_sha=str(item.get("merge_commit_sha") or ""),
            html_url=str(item.get("html_url", "")),
            files=files,
        )
        if record.coverage or re.search(r"project.control|governance|authority|status", title, re.IGNORECASE):
            records.append(record)
    return tuple(records), errors


def remote_state(repository: str, local_head: str, *, skip_github: bool) -> dict[str, Any]:
    state: dict[str, Any] = {
        "remote_exists": False,
        "remote_archived": False,
        "remote_disabled": False,
        "remote_default_branch": "",
        "remote_default_head": "",
        "local_head_on_remote": False,
        "comparison_status": "",
        "ahead_by": 0,
        "behind_by": 0,
        "control_prs": (),
        "errors": [],
    }
    if skip_github:
        state["errors"].append("GitHub reconciliation skipped")
        return state

    code, payload, diagnostic = gh_json(f"repos/{repository}")
    if code != 0 or not isinstance(payload, dict):
        state["errors"].append(f"remote repository could not be read: {diagnostic or f'exit {code}'}")
        return state
    state["remote_exists"] = True
    state["remote_archived"] = bool(payload.get("archived", False))
    state["remote_disabled"] = bool(payload.get("disabled", False))
    default_branch = str(payload.get("default_branch", ""))
    state["remote_default_branch"] = default_branch

    if default_branch:
        branch_code, branch_payload, branch_diag = gh_json(f"repos/{repository}/commits/{default_branch}")
        if branch_code == 0 and isinstance(branch_payload, dict):
            state["remote_default_head"] = str(branch_payload.get("sha", ""))
        else:
            state["errors"].append(
                f"default-branch head could not be read: {branch_diag or f'exit {branch_code}'}"
            )

    if local_head:
        commit_code, commit_payload, _ = gh_json(f"repos/{repository}/commits/{local_head}")
        state["local_head_on_remote"] = commit_code == 0 and isinstance(commit_payload, dict)
        if state["remote_default_head"]:
            compare_code, compare_payload, compare_diag = gh_json(
                f"repos/{repository}/compare/{state['remote_default_head']}...{local_head}"
            )
            if compare_code == 0 and isinstance(compare_payload, dict):
                state["comparison_status"] = str(compare_payload.get("status", ""))
                state["ahead_by"] = int(compare_payload.get("ahead_by", 0))
                state["behind_by"] = int(compare_payload.get("behind_by", 0))
            else:
                state["errors"].append(
                    f"head comparison could not be read: {compare_diag or f'exit {compare_code}'}"
                )

    prs, pr_errors = list_control_prs(repository)
    state["control_prs"] = prs
    state["errors"].extend(pr_errors)
    return state


def classify(record: RepositoryRecord) -> tuple[str, str]:
    if not record.local_exists or not record.git_repository:
        return "EXCEPTION — LOCAL REPOSITORY UNAVAILABLE", "Resolve local identity before migration."
    if record.normalised_remote and record.normalised_remote.lower() != record.audit.repository.lower():
        return "EXCEPTION — IDENTITY CONFLICT", "Resolve local-origin and audit identity before migration."
    if not record.remote_exists:
        return "EXCEPTION — REMOTE UNRESOLVED", "Resolve remote existence or adopt a local-only exception record."
    if record.remote_archived or record.remote_disabled:
        return "EXCEPTION — REMOTE ARCHIVED OR DISABLED", "Record archival exception; do not inject active controls."
    if record.local_dirty:
        return "BLOCKED — DIRTY WORKTREE", "Preserve and reconcile local uncommitted work before any control branch."
    if not record.local_head_on_remote:
        return "BLOCKED — LOCAL HEAD NOT ON REMOTE", "Publish or reconcile the exact local head before migration."
    open_covering = [pr for pr in record.control_prs if pr.state == "open" and pr.coverage]
    if open_covering:
        return "EXISTING CONTROL PR — REVIEW FIRST", "Review the existing control PR; do not create a duplicate migration branch."
    merged_covering = [pr for pr in record.control_prs if pr.merged and pr.coverage]
    if merged_covering and record.missing_required_files:
        return "LOCAL CHECKOUT STALE AFTER CONTROL MERGE", "Synchronise local authority before reassessing migration need."
    if record.active_evidence:
        return "ACTIVE — REPOSITORY-SPECIFIC MIGRATION", "Design one exact control PR preserving the current active lane."
    if record.authority_candidates or record.workflow_files:
        return "INACTIVE OR UNKNOWN — AUTHORITY-PRESERVING MIGRATION", "Inspect existing authority and workflows before a bounded control PR."
    return "INACTIVE OR UNKNOWN — STANDARD MIGRATION", "Apply the standard control skeleton only after exact-head review."


def inspect_entry(entry: AuditEntry, active_slugs: set[str], *, skip_github: bool) -> RepositoryRecord:
    local, local_errors = local_state(entry)
    repository_for_remote = local.get("normalised_remote") or entry.repository
    remote = remote_state(repository_for_remote, local["local_head"], skip_github=skip_github)
    errors = tuple(local_errors + list(remote["errors"]))
    record = RepositoryRecord(
        audit=entry,
        local_exists=local["local_exists"],
        git_repository=local["git_repository"],
        local_head=local["local_head"],
        local_branch=local["local_branch"],
        local_dirty=local["local_dirty"],
        local_status_count=local["local_status_count"],
        origin_url=local["origin_url"],
        normalised_remote=local["normalised_remote"],
        remote_exists=remote["remote_exists"],
        remote_archived=remote["remote_archived"],
        remote_disabled=remote["remote_disabled"],
        remote_default_branch=remote["remote_default_branch"],
        remote_default_head=remote["remote_default_head"],
        local_head_on_remote=remote["local_head_on_remote"],
        comparison_status=remote["comparison_status"],
        ahead_by=remote["ahead_by"],
        behind_by=remote["behind_by"],
        active_evidence=(entry.repository.lower() in active_slugs or repository_for_remote.lower() in active_slugs),
        existing_required_files=local["existing_required_files"],
        missing_required_files=local["missing_required_files"],
        authority_candidates=local["authority_candidates"],
        workflow_files=local["workflow_files"],
        control_prs=remote["control_prs"],
        errors=errors,
    )
    record.migration_classification, record.migration_route = classify(record)
    return record


def md_code(value: str) -> str:
    return f"`{value or '—'}`"


def join_code(values: tuple[str, ...]) -> str:
    return ", ".join(md_code(value) for value in values) if values else "—"


def expected_diff(record: RepositoryRecord) -> tuple[str, ...]:
    paths = list(record.missing_required_files)
    if "AGENTS.md" in record.existing_required_files:
        paths.append("AGENTS.md — preserve existing repository-specific instructions and add only missing parent entry rules")
    if "STATUS.md" in record.existing_required_files:
        paths.append("STATUS.md — reconcile rather than replace")
    if record.workflow_files and ".github/workflows/project-control.yml" in record.missing_required_files:
        paths.append("existing workflow integration may replace standalone workflow creation")
    return tuple(paths)


def validation_commands(record: RepositoryRecord) -> tuple[str, ...]:
    repository = record.normalised_remote or record.audit.repository
    return (
        f"python scripts/validate_project_control.py --repository {repository}",
        "git diff --check",
        "git status --short",
        "repository-native tests and CI named by its existing authority",
        "rerun central Run-ProjectControlAudit.ps1 after merge and require the repository to leave UNMANAGED",
    )


def migration_contract(record: RepositoryRecord) -> list[str]:
    repository = record.normalised_remote or record.audit.repository
    existing_prs = []
    for pr in record.control_prs:
        existing_prs.append(
            f"#{pr.number} {pr.state}{' draft' if pr.draft else ''}{' merged' if pr.merged else ''} "
            f"head={pr.head_sha or '—'} coverage={','.join(pr.coverage) or 'none'}"
        )
    allowed_files = expected_diff(record)
    forbidden = (
        "all manuscript, source, application, hardware, asset and generated-output files",
        "existing authority records except the exact additive/reconciliation edits named in the contract",
        "branch history rewriting, force push, squash or rebase unless the repository's existing authority explicitly requires it",
        "repository deletion, archiving, renaming, movement or visibility changes",
    )
    lines = [
        "#### Proposed migration contract", "",
        f"1. **Repository and local path:** {md_code(repository)} at {md_code(str(record.audit.local_path))}.",
        f"2. **Exact inspected head:** local {md_code(record.local_head)} on branch {md_code(record.local_branch)}; remote default {md_code(record.remote_default_head)} on {md_code(record.remote_default_branch)}.",
        f"3. **Existing authority files:** {join_code(record.authority_candidates)}.",
        f"4. **Conflicting or missing controls:** audit: {'; '.join(record.audit.audit_reasons) or 'none'}; missing: {join_code(record.missing_required_files)}; errors: {'; '.join(record.errors) or 'none'}.",
        "5. **Canonical `AGENTS.md` strategy:** " + (
            "preserve the existing file and add only missing parent entry rules and fixed bootstrap"
            if "AGENTS.md" in record.existing_required_files else
            "add root `AGENTS.md` derived from the template, then append repository-specific instructions discovered during exact-head inspection"
        ) + ".",
        "6. **Singular `STATUS.md` strategy:** " + (
            "reconcile the existing root status into the required singular completion authority without discarding its current lane"
            if "STATUS.md" in record.existing_required_files else
            "create root `STATUS.md` from the repository's real current authority; do not use a generic placeholder state"
        ) + ".",
        "7. **Validator and CI strategy:** add the repository validator; integrate it into existing CI where architecture requires one workflow, otherwise add `.github/workflows/project-control.yml`.",
        f"8. **Allowed files:** {join_code(allowed_files)}.",
        f"9. **Forbidden changes:** {'; '.join(forbidden)}.",
        f"10. **Expected diff:** additions or bounded reconciliations only in the allowed control files; no target-project content diff.",
        f"11. **Validation commands:** {'; '.join(validation_commands(record))}.",
        "12. **Review and merge method:** one draft PR from the exact reviewed base; promote only after validator, native CI and exact diff pass; use the repository's established merge method, otherwise merge commit.",
        "13. **Exact stop point:** stop after opening and validating the draft control PR; no merge without separate exact-head authority.",
    ]
    if existing_prs:
        lines.extend(["", f"Existing control-related PR evidence: {'; '.join(existing_prs)}."])
    return lines


def build_register(
    audit_path: Path,
    audit_hash: str,
    active_path: Path,
    records: list[RepositoryRecord],
) -> str:
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    classifications = Counter(record.migration_classification for record in records)
    batches: defaultdict[str, list[str]] = defaultdict(list)
    for record in records:
        batches[record.migration_classification].append(record.normalised_remote or record.audit.repository)
    lines = [
        "---",
        "standard: Recursive Project Improvement Standard v1.0",
        "role: existing-repository-migration-register",
        f"generated: {now}",
        f"source_audit: {audit_path}",
        f"source_audit_sha256: {audit_hash}",
        f"active_work_source: {active_path}",
        f"repository_count: {len(records)}",
        "target_repositories_changed: 0",
        "---", "",
        "# Existing-Repository Control Migration Register", "",
        "## Authority and boundary", "",
        f"This register imports exactly {len(records)} `UNMANAGED` findings from "
        f"`{audit_path}` at SHA-256 `{audit_hash}`.", "",
        "The inspection is read-only. It does not fetch, checkout, edit, stage, commit, push, branch, open a target-repository PR, move, archive or delete any target repository.", "",
        "## Summary", "",
    ]
    for classification, count in sorted(classifications.items()):
        lines.append(f"- **{classification}:** {count}")
    lines.extend(["", "## Inventory", "", "| # | Repository | Local path | Local head | Remote default head | Dirty | Classification |", "|---:|---|---|---|---|---|---|"])
    for index, record in enumerate(records, 1):
        repository = record.normalised_remote or record.audit.repository
        lines.append(
            f"| {index} | {md_code(repository)} | {md_code(str(record.audit.local_path))} | "
            f"{md_code(record.local_head)} | {md_code(record.remote_default_head)} | "
            f"{'YES' if record.local_dirty else 'NO'} | {record.migration_classification} |"
        )
    lines.extend(["", "## Proposed migration batches", ""])
    batch_order = [
        "EXISTING CONTROL PR — REVIEW FIRST",
        "LOCAL CHECKOUT STALE AFTER CONTROL MERGE",
        "ACTIVE — REPOSITORY-SPECIFIC MIGRATION",
        "INACTIVE OR UNKNOWN — AUTHORITY-PRESERVING MIGRATION",
        "INACTIVE OR UNKNOWN — STANDARD MIGRATION",
        "BLOCKED — DIRTY WORKTREE",
        "BLOCKED — LOCAL HEAD NOT ON REMOTE",
        "EXCEPTION — IDENTITY CONFLICT",
        "EXCEPTION — REMOTE UNRESOLVED",
        "EXCEPTION — REMOTE ARCHIVED OR DISABLED",
        "EXCEPTION — LOCAL REPOSITORY UNAVAILABLE",
    ]
    for classification in batch_order:
        repositories = sorted(batches.get(classification, []), key=str.lower)
        if repositories:
            lines.extend([f"### {classification}", ""])
            lines.extend(f"- {md_code(repository)}" for repository in repositories)
            lines.append("")
    lines.extend(["## Complete repository records", ""])
    for index, record in enumerate(records, 1):
        repository = record.normalised_remote or record.audit.repository
        lines.extend([
            f"### {index}. {repository}", "",
            f"- Audit identity: {md_code(record.audit.repository)}",
            f"- Local path: {md_code(str(record.audit.local_path))}",
            f"- Local repository exists: **{'YES' if record.local_exists else 'NO'}**",
            f"- Git worktree: **{'YES' if record.git_repository else 'NO'}**",
            f"- Local head: {md_code(record.local_head)}",
            f"- Local branch: {md_code(record.local_branch)}",
            f"- Local dirty: **{'YES' if record.local_dirty else 'NO'}** ({record.local_status_count} status entries)",
            f"- Origin URL: {md_code(record.origin_url)}",
            f"- Normalised remote: {md_code(record.normalised_remote)}",
            f"- Remote exists: **{'YES' if record.remote_exists else 'NO'}**",
            f"- Remote archived/disabled: **{'YES' if record.remote_archived or record.remote_disabled else 'NO'}**",
            f"- Remote default branch/head: {md_code(record.remote_default_branch)} / {md_code(record.remote_default_head)}",
            f"- Local head exists on remote: **{'YES' if record.local_head_on_remote else 'NO'}**",
            f"- Default-head comparison: {md_code(record.comparison_status)}; ahead={record.ahead_by}; behind={record.behind_by}",
            f"- Active-work evidence: **{'YES' if record.active_evidence else 'NO'}**",
            f"- Existing mandatory files: {join_code(record.existing_required_files)}",
            f"- Missing mandatory files: {join_code(record.missing_required_files)}",
            f"- Authority candidates: {join_code(record.authority_candidates)}",
            f"- Workflow files: {join_code(record.workflow_files)}",
            f"- Migration classification: **{record.migration_classification}**",
            f"- Migration route: {record.migration_route}",
            f"- Diagnostic errors: {'; '.join(record.errors) or 'none'}", "",
        ])
        lines.extend(migration_contract(record))
        lines.extend(["", "---", ""])
    lines.extend([
        "## Lane stop", "",
        "All target repositories remain unchanged. Each migration requires separate repository-specific authority before implementation.", "",
    ])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        if not args.skip_github:
            auth = run(["gh", "auth", "status"], timeout=60)
            if auth.returncode != 0:
                raise RegisterError(f"GitHub CLI is not authenticated: {auth.stdout.strip()}")
        entries = parse_audit(args.audit, args.expected_count)
        active_slugs = active_repositories(args.active_work)
        records = [inspect_entry(entry, active_slugs, skip_github=args.skip_github) for entry in entries]
        if len(records) != args.expected_count:
            raise RegisterError(f"internal record count mismatch: expected {args.expected_count}, got {len(records)}")
        before_status = {
            record.audit.local_path: run_git(record.audit.local_path, ["status", "--porcelain=v1", "--untracked-files=all"]).stdout
            for record in records if record.git_repository
        }
        register = build_register(args.audit, sha256_file(args.audit), args.active_work, records)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(register, encoding="utf-8", newline="\n")
        changed = []
        for record in records:
            if not record.git_repository:
                continue
            after = run_git(record.audit.local_path, ["status", "--porcelain=v1", "--untracked-files=all"]).stdout
            if before_status[record.audit.local_path] != after:
                changed.append(str(record.audit.local_path))
        if changed:
            raise RegisterError("target repository worktree changed during read-only import: " + ", ".join(changed))
        print("MIGRATION REGISTER IMPORTED")
        print(f"Repository count: {len(records)}")
        print(f"Output: {args.output}")
        print("TARGET_REPOSITORIES_CHANGED=0")
        return 0
    except RegisterError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
