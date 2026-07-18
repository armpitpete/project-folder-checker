---
authority_record: true
standard: Recursive Project Improvement Standard v1.0
batch: 1
review_only: true
target_pull_requests_changed: 0
---

# Existing-Repository Migration Batch 1 Review

## Authority

This record reviews only:

- `armpitpete/commentate-this` PR #3;
- `armpitpete/canon-garden` PR #202;
- `armpitpete/lirava` PR #82;
- `armpitpete/merrin-voice-01` PR #50;
- `armpitpete/story-evidence-collector` PR #146.

No target pull request, branch, file, workflow, draft state or merge state was changed.

## Review standard

A promotable migration must satisfy the ownership-neutral central audit contract:

1. root `AGENTS.md`;
2. root `STATUS.md` as the singular completion authority;
3. `docs/authority/AUTHORITY.md`;
4. `scripts/validate_project_control.py`;
5. a GitHub Actions workflow that invokes the validator.

The control documents must also provide:

- `entry_authority: true` in `AGENTS.md`;
- the exact `Fixed new-chat bootstrap` section;
- initialized repository identity and `template_mode: false` in `STATUS.md`;
- exactly one each of `Current authority`, `Current lane`, `Allowed scope`, `Forbidden changes`, `Validation`, `Done`, `To do`, `Next bounded gate` and `Stop point`;
- exactly one each of `Source authority`, `Active authority`, `Decision authority`, `Completion authority` and `Governing constraints` in `docs/authority/AUTHORITY.md`;
- exactly root `STATUS.md` claiming `completion_authority: true`.

## Common finding

All five pull requests are:

- open;
- draft;
- unmerged;
- currently mergeable;
- strictly ahead of their reported current bases and zero commits behind;
- control-only in subject matter;
- green on their exact-head GitHub Actions runs.

None is promotion-ready.

The green workflows validate an earlier, weaker contract. Every PR lacks at least one mandatory central-audit file, and every `STATUS.md` lacks the complete current heading and repository-identity contract. Promotion without repair would leave the repository `UNMANAGED` or `DRIFTED` under the proven central audit.

## Contract B1-CT — commentate-this PR #3

### Reviewed state

- Base: `main` at `5fef5a4ebd443d0bd5b9cbb11c83b8d121fdcf9a`.
- Head: `a3d8c1c1cfef46d3422f32b2d0fead9b8deb5e5a`.
- History: 3 commits ahead, 0 behind.
- Scope: 3 files, +127/-0.
- Paths:
  - `.github/workflows/project-control.yml`;
  - `AGENTS.md`;
  - `STATUS.md`.
- CI: `Project control` run `29607133100` passed.
- Product leakage: none detected.

### Defects

- missing `docs/authority/AUTHORITY.md`;
- missing standalone `scripts/validate_project_control.py`;
- workflow embeds a weaker validator instead of invoking the audited script;
- `AGENTS.md` lacks canonical front matter and the exact fixed-bootstrap heading;
- `STATUS.md` lacks initialized repository identity, `template_mode: false`, `authority_files`, `Allowed scope`, `Forbidden changes` and `Validation`.

### Repair contract

- Starting head: exact `a3d8c1c1cfef46d3422f32b2d0fead9b8deb5e5a` only.
- Allowed files:
  - `.github/workflows/project-control.yml`;
  - `AGENTS.md`;
  - `STATUS.md`;
  - `docs/authority/AUTHORITY.md`;
  - `scripts/validate_project_control.py`.
- Preserve the CT-01 product lane and provider/audio stop boundaries, refreshed against current repository authority before writing.
- Replace the inline workflow program with an invocation of the repository validator.
- Prohibit script-generation, audio-rendering, provider, product or application changes.
- Validate the repository-specific validator, singular authority, exact five-path scope and GitHub Actions at the new exact head.
- Result: repair-only new head; separate exact-head promotion authority required.

## Contract B1-CG — canon-garden PR #202

### Reviewed state

- Base: `main` at `e46a68760c7c7a9e931c5f70c9cd7239acd26830`.
- Head: `dba89b9df57828c84c89d57e8d38261fe5ca6027`.
- History: 7 commits ahead, 0 behind.
- Scope: 5 files, +160/-1.
- Paths:
  - `.github/workflows/validate-entries.yml`;
  - `AGENTS.md`;
  - `STATUS.md`;
  - `scripts/ci-guardrail-check.js`;
  - `scripts/validate_project_control.py`.
- CI: integrated `Canon Garden CI` run `29607439089` passed project control, source validation, CI architecture and production build.
- Product leakage: none detected.

### Defects

- missing `docs/authority/AUTHORITY.md`;
- validator enforces only the earlier reduced contract;
- `AGENTS.md` lacks canonical front matter and the exact fixed-bootstrap heading;
- `STATUS.md` lacks initialized repository identity, `template_mode: false`, `authority_files`, `Allowed scope`, `Forbidden changes` and `Validation`.

### Repair contract

- Starting head: exact `dba89b9df57828c84c89d57e8d38261fe5ca6027` only.
- Allowed files:
  - `.github/workflows/validate-entries.yml`;
  - `AGENTS.md`;
  - `STATUS.md`;
  - `docs/authority/AUTHORITY.md`;
  - `scripts/ci-guardrail-check.js`;
  - `scripts/validate_project_control.py`.
- Preserve the single integrated Canon Garden CI workflow; do not add a competing workflow.
- Preserve the guardrail requirement that exactly one project-control validation command exists.
- Refresh the human-proof lane against current Canon Garden authority before writing status.
- Prohibit application, database, UI, schema, fixture, deployment and PR #201 implementation changes.
- Rerun the full integrated CI, not merely the control validator.
- Result: repair-only new head; separate exact-head promotion authority required.

## Contract B1-LI — lirava PR #82

### Reviewed state

- Base: `main` at `1e5a6c1989cea6a987f2df33fab7e3d680630f30`.
- Head: `019031b61edac5affacaa34d8f71b8c48189c262`.
- History: 3 commits ahead, 0 behind.
- Scope: 3 files, +133/-0.
- Paths:
  - `.github/workflows/project-control.yml`;
  - `AGENTS.md`;
  - `STATUS.md`.
- CI: `Build` run `29606981732` and `Project control` run `29606981763` both passed.
- Product leakage: none detected.

### Defects

- missing `docs/authority/AUTHORITY.md`;
- missing standalone `scripts/validate_project_control.py`;
- workflow embeds a weaker validator;
- injected `AGENTS.md` header lacks canonical front matter and the exact fixed-bootstrap heading;
- `STATUS.md` lacks initialized repository identity, `template_mode: false`, `authority_files`, `Allowed scope`, `Forbidden changes` and `Validation`.

### Repair contract

- Starting head: exact `019031b61edac5affacaa34d8f71b8c48189c262` only.
- Allowed files:
  - `.github/workflows/project-control.yml`;
  - `AGENTS.md`;
  - `STATUS.md`;
  - `docs/authority/AUTHORITY.md`;
  - `scripts/validate_project_control.py`.
- Preserve all pre-existing Lirava Codex instructions byte-for-byte after the control preamble.
- Refresh the active product lane from current `main` and open PR authority; do not assume PRs #80-#81 remain current without verification.
- Replace the inline workflow program with the repository validator.
- Prohibit code, prompt, UI, test, product-contract and behaviour changes.
- Rerun both the application Build workflow and project-control workflow at the new exact head.
- Result: repair-only new head; separate exact-head promotion authority required.

## Contract B1-MV — merrin-voice-01 PR #50

### Reviewed state

- Base: `main` at `8df52377de753c8c910d67fc31405782d52a1be8`.
- Head: `9982abf4112f220a74356ca615feacdcdca77937`.
- History: 3 commits ahead, 0 behind.
- Scope: 3 files, +128/-0.
- Paths:
  - `.github/workflows/project-control.yml`;
  - `AGENTS.md`;
  - `STATUS.md`.
- CI: `Project control` run `29606906848` passed.
- Hardware leakage: none detected.

### Defects

- missing `docs/authority/AUTHORITY.md`;
- missing standalone `scripts/validate_project_control.py`;
- workflow embeds a weaker validator;
- `AGENTS.md` lacks canonical front matter and the exact fixed-bootstrap heading;
- `STATUS.md` lacks initialized repository identity, `template_mode: false`, `authority_files`, `Allowed scope`, `Forbidden changes` and `Validation`.

### Repair contract

- Starting head: exact `9982abf4112f220a74356ca615feacdcdca77937` only.
- Allowed files:
  - `.github/workflows/project-control.yml`;
  - `AGENTS.md`;
  - `STATUS.md`;
  - `docs/authority/AUTHORITY.md`;
  - `scripts/validate_project_control.py`.
- Refresh the diagnostic lane from current electrical authority and current PR state before writing status.
- Replace the inline workflow program with the repository validator.
- Prohibit circuit, symbol, coordinate, value, footprint, PCB, routing, panel, fabrication, purchasing and manufacturing changes.
- Run project-control validation at the new exact head; any pre-existing hardware CI must remain unchanged and pass if triggered.
- Result: repair-only new head; separate exact-head promotion authority required.

## Contract B1-SEC — story-evidence-collector PR #146

### Reviewed state

- Base: `main` at `17289a439f3b9573f7372b66fa24936b672e7c68`.
- Head: `6b9bba1b3a85da360b338a93547f29a68259792f`.
- History: 3 commits ahead, 0 behind.
- Scope: 3 files, +128/-0.
- Paths:
  - `.github/workflows/project-control.yml`;
  - `AGENTS.md`;
  - `STATUS.md`.
- CI: `Project control` run `29607089209` passed.
- Collector/server/report leakage: none detected.

### Defects

- missing `docs/authority/AUTHORITY.md`;
- missing standalone `scripts/validate_project_control.py`;
- workflow embeds a weaker validator;
- `AGENTS.md` lacks canonical front matter and the exact fixed-bootstrap heading;
- `STATUS.md` lacks initialized repository identity, `template_mode: false`, `authority_files`, `Allowed scope`, `Forbidden changes` and `Validation`.

### Repair contract

- Starting head: exact `6b9bba1b3a85da360b338a93547f29a68259792f` only.
- Allowed files:
  - `.github/workflows/project-control.yml`;
  - `AGENTS.md`;
  - `STATUS.md`;
  - `docs/authority/AUTHORITY.md`;
  - `scripts/validate_project_control.py`.
- Reverify the current relationship and state of PRs #144 and #145 before retaining or changing `BLOCKED` status.
- Replace the inline workflow program with the repository validator.
- Prohibit collector, live-server, report-generator, schema, fixture and product changes.
- Run project-control validation at the new exact head; any existing collector CI must remain unchanged and pass if triggered.
- Result: repair-only new head; separate exact-head promotion authority required.

## Batch disposition

| Repository | Reviewed head | CI | Scope | Decision |
|---|---|---|---|---|
| `commentate-this` | `a3d8c1c1cfef46d3422f32b2d0fead9b8deb5e5a` | PASS | control-only | REPAIR REQUIRED |
| `canon-garden` | `dba89b9df57828c84c89d57e8d38261fe5ca6027` | PASS | control-only | REPAIR REQUIRED |
| `lirava` | `019031b61edac5affacaa34d8f71b8c48189c262` | PASS | control-only | REPAIR REQUIRED |
| `merrin-voice-01` | `9982abf4112f220a74356ca615feacdcdca77937` | PASS | control-only | REPAIR REQUIRED |
| `story-evidence-collector` | `6b9bba1b3a85da360b338a93547f29a68259792f` | PASS | control-only | REPAIR REQUIRED |

## Stop point

Batch 1 review is complete. Do not update, refresh, mark ready, close or merge any target pull request without separate repository-specific exact-head authority.