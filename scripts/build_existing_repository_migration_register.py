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
    output = completed.stdout.strip()
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


def parse_active_work(path: Path) -> tuple[set[str], str]:
    if not path.is_file():
        raise RegisterError(f"ACTIVE_WORK.md does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    slugs = {match.group(1).lower() for match in REPO_SLUG_RE.finditer(text)}
    return slugs, sha256_file(path)


def normalise_remote(url: str) -> str:
    patterns = (
        r"github\.com[:/](?P<slug>[^/\s]+/[^/\s]+?)(?:\.git)?$",
        r"api\.github\.com/repos/(?P<slug>[^/\s]+/[^/\s]+)$",
    )
    for pattern in patterns:
        match = re.search(pattern, url.strip())
        if match:
            return match.group("slug")
    return ""


def safe_rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def find_authority_candidates(repo: Path) -> tuple[str, ...]:
    found: list[str] = []
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        rel = safe_rel(path, repo)
        lower = rel.lower()
        if rel in REQUIRED_FILES:
            found.append(rel)
            continue
        if path.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".toml"}:
            continue
        if AUTHORITY_NAME_RE.search(path.name) or lower.startswith("docs/authority/"):
            found.append(rel)
    unique = sorted(set(found), key=str.lower)
    return tuple(unique[:40] + ([f"… plus {len(unique) - 40} more"] if len(unique) > 40 else []))


def find_workflows(repo: Path) -> tuple[str, ...]:
    root = repo / ".github" / "workflows"
    if not root.is_dir():
        return ()
    return tuple(sorted(safe_rel(path, repo) for path in root.iterdir() if path.is_file()))


def local_git_state(entry: AuditEntry) -> dict[str, Any]:
    repo = entry.local_path
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
        "missing_required_files": tuple(REQUIRED_FILES),
        "authority_candidates": (),
        "workflow_files": (),
        "errors": [],
    }
    if not repo.is_dir():
        state["errors"].append("local path does not exist")
        return state
    state["git_repository"] = (repo / ".git").exists()
    if not state["git_repository"]:
        state["errors"].append("local path is not a Git worktree")
        return state

    head = run_git(repo, ["rev-parse", "HEAD"])
    if head.returncode == 0:
        state["local_head"] = head.stdout.strip()
    else:
        state["errors"].append(f"could not resolve local HEAD: {head.stdout.strip()}")

    branch = run_git(repo, ["symbolic-ref", "--short", "-q", "HEAD"])
    state["local_branch"] = branch.stdout.strip() if branch.returncode == 0 else "DETACHED"

    status = run_git(repo, ["status", "--porcelain=v1", "--untracked-files=all"])
    if status.returncode == 0:
        lines = [line for line in status.stdout.splitlines() if line]
        state["local_status_count"] = len(lines)
        state["local_dirty"] = bool(lines)
    else:
        state["errors"].append(f"git status failed: {status.stdout.strip()}")

    origin = run_git(repo, ["remote", "get-url", "origin"])
    if origin.returncode == 0:
        state["origin_url"] = origin.stdout.strip()
        state["normalised_remote"] = normalise_remote(state["origin_url"])
        if not state["normalised_remote"]:
            state["errors"].append("origin URL could not be normalised to owner/repository")
    else:
        state["errors"].append("origin remote is missing")

    existing = tuple(relative for relative in REQUIRED_FILES if (repo / relative).is_file())
    state["existing_required_files"] = existing
    state["missing_required_files"] = tuple(relative for relative in REQUIRED_FILES if relative not in existing)
    state["authority_candidates"] = find_authority_candidates(repo)
    state["workflow_files"] = find_workflows(repo)
    return state


def list_control_prs(repository: str) -> tuple[PullRequestRecord, ...]:
    code, payload, diagnostic = gh_json(f"repos/{repository}/pulls?state=all&sort=updated&direction=desc&per_page=50")
    if code != 0 or not isinstance(payload, list):
        return ()
    candidates: list[PullRequestRecord] = []
    for pr in payload:
        title = str(pr.get("title") or "")
        body = str(pr.get("body") or "")
        head_ref = str((pr.get("head") or {}).get("ref") or "")
        marker = " ".join((title, body, head_ref)).lower()
        if not any(token in marker for token in ("project-control", "project control", "governance", "authority")):
            continue
        number = int(pr.get("number"))
        files_code, files_payload, _ = gh_json(f"repos/{repository}/pulls/{number}/files?per_page=100")
        files: tuple[str, ...] = ()
        if files_code == 0 and isinstance(files_payload, list):
            files = tuple(sorted(str(item.get("filename") or "") for item in files_payload if item.get("filename")))
        candidates.append(PullRequestRecord(
            number=number,
            title=title,
            state=str(pr.get("state") or ""),
            draft=bool(pr.get("draft")),
            merged=bool(pr.get("merged_at")),
            head_sha=str((pr.get("head") or {}).get("sha") or ""),
            base_sha=str((pr.get("base") or {}).get("sha") or ""),
            merge_commit_sha=str(pr.get("merge_commit_sha") or ""),
            html_url=str(pr.get("html_url") or ""),
            files=files,
        ))
    return tuple(candidates[:10])


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
        state["errors"].append(f"GitHub repository could not be read: {diagnostic or f'exit {code}'}")
        return state
    state["remote_exists"] = True
    state["remote_archived"] = bool(payload.get("archived"))
    state["remote_disabled"] = bool(payload.get("disabled"))
    state["remote_default_branch"] = str(payload.get("default_branch") or "")

    default_branch = state["remote_default_branch"]
    if default_branch:
        branch_code, branch_payload, branch_diag = gh_json(f"repos/{repository}/commits/{default_branch}")
        if branch_code == 0 and isinstance(branch_payload, dict):
            state["remote_default_head"] = str(branch_payload.get("sha") or "")
        else:
            state["errors"].append(f"remote default head could not be read: {branch_diag or f'exit {branch_code}'}")

    if local_head:
        head_code, head_payload, _ = gh_json(f"repos/{repository}/commits/{local_head}")
        state["local_head_on_remote"] = head_code == 0 and isinstance(head_payload, dict)
        if state["local_head_on_remote"] and state["remote_default_head"]:
            compare_code, compare_payload, compare_diag = gh_json(
                f"repos/{repository}/compare/{state['remote_default_head']}...{local_head}"
            )
            if compare_code == 0 and isinstance(compare_payload, dict):
                state["comparison_status"] = str(compare_payload.get("status") or "")
                state["ahead_by"] = int(compare_payload.get("ahead_by") or 0)
                state["behind_by"] = int(compare_payload.get("behind_by") or 0)
            else:
                state["errors"].append(f"local/default comparison failed: {compare_diag or f'exit {compare_code}'}")
        elif not state["local_head_on_remote"]:
            state["errors"].append("local HEAD is not present in the GitHub repository")

    state["control_prs"] = list_control_prs(repository)
    return state


def classify_records(records: list[RepositoryRecord]) -> None:
    remote_groups: dict[str, list[RepositoryRecord]] = defaultdict(list)
    for record in records:
        key = record.normalised_remote.lower() if record.normalised_remote else record.audit.repository.lower()
        remote_groups[key].append(record)

    for record in records:
        duplicate = len(remote_groups[record.normalised_remote.lower() if record.normalised_remote else record.audit.repository.lower()]) > 1
        errors = list(record.errors)
        if record.normalised_remote and record.normalised_remote.lower() != record.audit.repository.lower():
            errors.append(
                f"audit repository {record.audit.repository} does not match origin {record.normalised_remote}"
            )
        open_complete_prs = [
            pr for pr in record.control_prs
            if pr.state == "open" and len(pr.coverage) >= 4
        ]
        merged_control_prs = [pr for pr in record.control_prs if pr.merged and pr.merge_commit_sha]
        partial_control = 0 < len(record.existing_required_files) < len(REQUIRED_FILES)
        reconciliation_exception = (
            not record.local_exists
            or not record.git_repository
            or not record.remote_exists
            or not record.normalised_remote
            or not record.local_head
            or not record.local_head_on_remote
            or record.local_branch == "DETACHED"
            or record.local_dirty
            or bool(errors)
        )

        if record.remote_archived:
            classification = "ARCHIVED"
            route = "Create an exception record only; do not migrate unless the repository is explicitly reactivated."
        elif duplicate:
            classification = "DUPLICATE"
            route = "Resolve the canonical local worktree and remote identity before any control migration."
        elif reconciliation_exception:
            classification = "EXCEPTIONAL"
            route = "Resolve local/remote reconciliation defects on a separate bounded gate before control implementation."
        elif record.active_evidence:
            classification = "ACTIVE"
            if open_complete_prs:
                pr = open_complete_prs[0]
                route = f"Review and promote existing control PR #{pr.number} at exact head {pr.head_sha}; do not create a duplicate migration PR."
            elif merged_control_prs and record.local_head != record.remote_default_head:
                pr = merged_control_prs[0]
                route = f"Synchronise the local worktree to the remote authority containing merged control PR #{pr.number}, then rerun the audit."
            else:
                route = "Design a repository-specific control PR that preserves the active lane and existing authority."
        elif open_complete_prs:
            classification = "READY_FOR_CONTROL_MIGRATION"
            pr = open_complete_prs[0]
            route = f"Use existing control PR #{pr.number} at exact head {pr.head_sha} as the migration vehicle after repository-specific review."
        elif not partial_control and not record.authority_candidates:
            classification = "READY_FOR_CONTROL_MIGRATION"
            route = "Create a repository-specific control PR from the exact reconciled head using the canonical skeleton."
        else:
            classification = "INACTIVE"
            route = "Record an inactive or blocked authoritative state, then adapt controls around existing authority without reactivating project work."

        record.errors = tuple(errors)
        record.migration_classification = classification
        record.migration_route = route


def inspect_entry(entry: AuditEntry, active_slugs: set[str], *, skip_github: bool) -> RepositoryRecord:
    local = local_git_state(entry)
    repository_for_remote = local["normalised_remote"] or entry.repository
    remote = remote_state(repository_for_remote, local["local_head"], skip_github=skip_github)
    errors = tuple(local["errors"] + remote["errors"])
    active = entry.repository.lower() in active_slugs or repository_for_remote.lower() in active_slugs
    return RepositoryRecord(
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
        active_evidence=active,
        existing_required_files=local["existing_required_files"],
        missing_required_files=local["missing_required_files"],
        authority_candidates=local["authority_candidates"],
        workflow_files=local["workflow_files"],
        control_prs=remote["control_prs"],
        errors=errors,
    )


def md_code(value: str) -> str:
    return f"`{value.replace('`', '')}`" if value else "—"


def md_list(items: tuple[str, ...] | list[str], empty: str = "None") -> str:
    return ", ".join(md_code(item) for item in items) if items else empty


def proposed_strategies(record: RepositoryRecord) -> tuple[str, str, str, list[str]]:
    existing = set(record.existing_required_files)
    agents = (
        "Extend the existing root `AGENTS.md`; preserve all repository-specific instructions and prepend the fixed entry authority."
        if "AGENTS.md" in existing
        else "Create root `AGENTS.md` from the canonical entry skeleton, then add repository-specific boundaries."
    )
    status = (
        "Reconcile the existing root `STATUS.md`; retain one singular completion authority and preserve exact current project authority."
        if "STATUS.md" in existing
        else "Create root `STATUS.md` only after existing status/authority records are reconciled; do not invent project state."
    )
    if record.workflow_files:
        ci = (
            "Integrate `scripts/validate_project_control.py` into the existing CI architecture; do not add a parallel workflow where the repository enforces a single-workflow rule."
        )
    else:
        ci = "Create the validator and one project-control workflow using the repository's supported runtime."
    expected = list(record.missing_required_files)
    if "STATUS.md" in existing:
        expected.append("STATUS.md (bounded reconciliation only)")
    if "AGENTS.md" in existing:
        expected.append("AGENTS.md (bounded extension only)")
    return agents, status, ci, sorted(set(expected), key=str.lower)


def build_register(
    records: list[RepositoryRecord], *, audit_path: Path, audit_hash: str,
    active_path: Path, active_hash: str
) -> str:
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    counts = Counter(record.migration_classification for record in records)
    lines = [
        "---",
        "standard: Recursive Project Improvement Standard v1.0",
        "role: existing-repository-migration-register",
        f"generated: {now}",
        f"source_audit: {audit_path}",
        f"source_audit_sha256: {audit_hash}",
        f"active_work: {active_path}",
        f"active_work_sha256: {active_hash}",
        f"repository_count: {len(records)}",
        "implementation_authorised: false",
        "---", "", "# Existing-Repository Control Migration Register", "",
        "## Authority", "",
        f"- Source audit: `{audit_path}`",
        f"- Source audit SHA-256: `{audit_hash}`",
        f"- Active-work authority: `{active_path}`",
        f"- Active-work SHA-256: `{active_hash}`",
        f"- Exact repositories imported: **{len(records)}**",
        "- This register is diagnostic. It authorises no target-repository change.", "",
        "## Classification summary", "",
    ]
    for classification in (
        "ACTIVE", "INACTIVE", "ARCHIVED", "DUPLICATE", "EXCEPTIONAL", "READY_FOR_CONTROL_MIGRATION"
    ):
        lines.append(f"- **{classification}:** {counts[classification]}")
    lines.extend(["", "## Inventory", "",
        "| Classification | Repository | Local head | Remote default head | Local state | Existing migration vehicle |",
        "|---|---|---|---|---|---|",
    ])
    for record in records:
        vehicles = []
        for pr in record.control_prs:
            if pr.coverage:
                state = "MERGED" if pr.merged else ("DRAFT" if pr.draft else pr.state.upper())
                vehicles.append(f"PR #{pr.number} {state} `{pr.head_sha}`")
        local_state = "DIRTY" if record.local_dirty else "CLEAN"
        lines.append(
            f"| {record.migration_classification} | `{record.audit.repository}` | "
            f"{md_code(record.local_head)} | {md_code(record.remote_default_head)} | {local_state} | "
            f"{'<br>'.join(vehicles) if vehicles else 'None detected'} |"
        )

    lines.extend(["", "## Repository migration records", ""])
    for index, record in enumerate(records, start=1):
        agents, status, ci, expected = proposed_strategies(record)
        compare = record.comparison_status or "unavailable"
        lines.extend([
            f"### {index:02d}. `{record.audit.repository}`", "",
            f"- **Migration classification:** `{record.migration_classification}`",
            f"- **Migration route:** {record.migration_route}", "",
            "#### 1. Repository and local path", "",
            f"- Audit identity: `{record.audit.repository}`",
            f"- Local path: `{record.audit.local_path}`",
            f"- Origin URL: {md_code(record.origin_url)}",
            f"- Normalised remote: {md_code(record.normalised_remote)}", "",
            "#### 2. Exact inspected head", "",
            f"- Local branch: {md_code(record.local_branch)}",
            f"- Local HEAD: {md_code(record.local_head)}",
            f"- Working tree: **{'DIRTY' if record.local_dirty else 'CLEAN'}** ({record.local_status_count} porcelain entries)",
            f"- GitHub default branch: {md_code(record.remote_default_branch)}",
            f"- GitHub default head: {md_code(record.remote_default_head)}",
            f"- Local HEAD present remotely: **{'YES' if record.local_head_on_remote else 'NO'}**",
            f"- Local/default comparison: `{compare}`; ahead `{record.ahead_by}`; behind `{record.behind_by}`", "",
            "#### 3. Existing authority files", "",
            f"- Authority/status candidates: {md_list(record.authority_candidates)}",
            f"- Existing workflows: {md_list(record.workflow_files)}", "",
            "#### 4. Conflicting or missing controls", "",
            f"- Existing mandatory controls: {md_list(record.existing_required_files)}",
            f"- Missing mandatory controls: {md_list(record.missing_required_files)}",
            f"- Audit findings: {md_list(list(record.audit.audit_reasons))}",
            f"- Reconciliation exceptions: {md_list(list(record.errors))}", "",
            "#### 5. Proposed `AGENTS.md` strategy", "", agents, "",
            "#### 6. Proposed singular `STATUS.md` strategy", "", status, "",
            "#### 7. Validator and CI integration strategy", "", ci, "",
            "#### 8. Allowed files", "",
            "- Only the repository-specific control files named by the final exact migration contract.",
            "- Existing authority files only where the contract specifies bounded reconciliation.",
            "- Existing CI workflow files only where integration is required by repository architecture.", "",
            "#### 9. Forbidden changes", "",
            "- No source, manuscript, product, circuit, application or content change.",
            "- No replacement or deletion of existing authority records.",
            "- No branch, PR or implementation until this repository's migration contract is separately authorised.",
            "- No squash or rebase assumption; merge method must be explicitly selected per repository.", "",
            "#### 10. Expected diff", "",
            f"- Proposed files: {md_list(expected)}",
            "- Exact line-level diff remains to be designed from the repository's own authority.", "",
            "#### 11. Validation commands", "",
            f"- `python scripts/validate_project_control.py --repository {record.audit.repository}`",
            "- repository-native test or validation suite required by existing authority",
            "- `git diff --check`",
            "- central project-control audit rerun after promotion", "",
            "#### 12. Review and merge method", "",
            "- One repository-specific draft PR from an exact inspected base.",
            "- Exact-head review before promotion.",
            "- Merge method must follow repository authority; no automatic squash or rebase.", "",
            "#### 13. Exact stop point", "",
            "Stop after the migration contract is reviewed. Do not alter the target repository without separate explicit implementation authority.", "",
            "#### Existing migration vehicles", "",
        ])
        if record.control_prs:
            for pr in record.control_prs:
                coverage = md_list(list(pr.coverage))
                state = "MERGED" if pr.merged else ("DRAFT" if pr.draft else pr.state.upper())
                lines.append(
                    f"- PR #{pr.number} — **{state}** — head `{pr.head_sha}` — base `{pr.base_sha}` — "
                    f"control coverage: {coverage} — {pr.html_url}"
                )
        else:
            lines.append("- None detected in the most recently updated 50 pull requests.")
        lines.append("")

    lines.extend([
        "## Batch design", "",
        "Batches must be proposed only after human review of this register. A batch may group repositories with the same migration route, but each repository retains its own exact base, contract, validation and stop point.", "",
        "## Stop point", "",
        "Stop before changing any target repository. The disposable proof repository remains preserved and is not part of the 19-repository migration set.", "",
    ])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    entries = parse_audit(args.audit, args.expected_count)
    active_slugs, active_hash = parse_active_work(args.active_work)
    audit_hash = sha256_file(args.audit)
    records = [inspect_entry(entry, active_slugs, skip_github=args.skip_github) for entry in entries]
    classify_records(records)
    report = build_register(
        records,
        audit_path=args.audit,
        audit_hash=audit_hash,
        active_path=args.active_work,
        active_hash=active_hash,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8", newline="\n")
    print(f"Wrote migration register: {args.output}")
    print(f"SOURCE_AUDIT_SHA256={audit_hash}")
    print(f"ACTIVE_WORK_SHA256={active_hash}")
    print(f"REPOSITORIES={len(records)}")
    for classification in (
        "ACTIVE", "INACTIVE", "ARCHIVED", "DUPLICATE", "EXCEPTIONAL", "READY_FOR_CONTROL_MIGRATION"
    ):
        print(f"{classification}={sum(r.migration_classification == classification for r in records)}")
    print("TARGET_REPOSITORIES_CHANGED=0")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RegisterError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
