---
authority_record: true
standard: Recursive Project Improvement Standard v1.0
batch: 1
review_only: false
target_pull_requests_changed_during_central_reconciliation: 0
---

# Existing-Repository Migration Batch 1 Review

## Authority

This record governs the Batch 1 control-migration sequence for:

- `armpitpete/commentate-this` PR #3;
- `armpitpete/canon-garden` PR #202;
- `armpitpete/lirava` PR #82;
- `armpitpete/merrin-voice-01` PR #50;
- `armpitpete/story-evidence-collector` PR #146.

The initial review changed no target pull request, branch, file, workflow, draft state or merge state. Later execution remains separately bounded by repository and exact head.

## Review standard

The unchanged default central profile requires:

1. root `AGENTS.md`;
2. root `STATUS.md` as the singular completion authority;
3. `docs/authority/AUTHORITY.md`;
4. `scripts/validate_project_control.py`;
5. `.github/workflows/project-control.yml`.

The control documents must provide:

- `entry_authority: true` in `AGENTS.md`;
- the exact `Fixed new-chat bootstrap` section;
- initialized repository identity and `template_mode: false` in `STATUS.md`;
- exactly one each of `Current authority`, `Current lane`, `Allowed scope`, `Forbidden changes`, `Validation`, `Done`, `To do`, `Next bounded gate` and `Stop point`;
- exactly one each of `Source authority`, `Active authority`, `Decision authority`, `Completion authority` and `Governing constraints`;
- exactly root `STATUS.md` claiming `completion_authority: true`.

One centrally owned non-default profile is separately approved for the verified remote identity `armpitpete/canon-garden`. It preserves Canon Garden's sole integrated workflow and does not weaken or generalise the default profile.

## Initial review result

At the initial review, all five target pull requests were open, draft, unmerged, mergeable, strictly ahead of their reported bases with zero commits behind, control-only in subject matter, and green on exact-head CI. Each required repair before promotion.

## Contract B1-CT — commentate-this PR #3

### Initial reviewed state

- Base: `main` at `5fef5a4ebd443d0bd5b9cbb11c83b8d121fdcf9a`.
- Head: `a3d8c1c1cfef46d3422f32b2d0fead9b8deb5e5a`.
- History: 3 ahead, 0 behind.
- Initial paths: `.github/workflows/project-control.yml`, `AGENTS.md`, `STATUS.md`.
- CI: `Project control` run `29607133100` passed.
- Product leakage: none.

### Repair contract

Allowed files:

- `.github/workflows/project-control.yml`;
- `AGENTS.md`;
- `STATUS.md`;
- `docs/authority/AUTHORITY.md`;
- `scripts/validate_project_control.py`.

Preserve the CT-01 product lane and provider/audio stop boundaries. Replace the embedded validator with the standalone repository validator. Prohibit script-generation, audio-rendering, provider, product and application changes.

### Completed result

- Repair head: `038d41a7de58f59266aa3497ecd1fa44f4ea35f7`.
- Merge commit: `c3ef2d0b15c3ca54669a819dfae794e94817188f`.
- First parent: `5fef5a4ebd443d0bd5b9cbb11c83b8d121fdcf9a`.
- Second parent: `038d41a7de58f59266aa3497ecd1fa44f4ea35f7`.
- Post-merge CI run: `29641655705`, success.
- Proof-output files preserved: 39.
- Central result: `armpitpete/commentate-this` is `CONTROLLED`.
- Audit after completion: `CONTROLLED=2`, `BOOTSTRAP=1`, `DRIFTED=0`, `UNMANAGED=17`, `BLOCKED=0`.
- Other repository heads changed during local completion: 0.

## Contract B1-CG — canon-garden PR #202

### Initial reviewed state

- Base: `main` at `e46a68760c7c7a9e931c5f70c9cd7239acd26830`.
- Head: `dba89b9df57828c84c89d57e8d38261fe5ca6027`.
- History: 7 ahead, 0 behind.
- Initial paths:
  - `.github/workflows/validate-entries.yml`;
  - `AGENTS.md`;
  - `STATUS.md`;
  - `scripts/ci-guardrail-check.js`;
  - `scripts/validate_project_control.py`.
- CI: Canon Garden run `29607439089` passed.
- Product leakage: none.

### Repair contract

Allowed files:

- `.github/workflows/validate-entries.yml`;
- `AGENTS.md`;
- `STATUS.md`;
- `docs/authority/AUTHORITY.md`;
- `scripts/ci-guardrail-check.js`;
- `scripts/validate_project_control.py`.

Preserve exactly one integrated Canon Garden workflow and exactly one repository-specific validator command. Preserve the active PR #201 human-proof lane. Prohibit application, database, UI, schema, fixture, deployment and PR #201 implementation changes.

### Current repaired and reconciled state

- Current base: `main` at `4768a2dd3c1d7216b3fc9889d917cb1cf55fa167`.
- Current PR #202 head: `d64a82ddecc29d8685396f6c431418b9b055cf31`.
- History: 9 ahead, 0 behind.
- Final diff: exactly the six authorised control paths.
- Reconciliation commit first parent: `afe4d719573f0a9bed56c1330c449225bffaf43b`.
- Reconciliation commit second parent: `4768a2dd3c1d7216b3fc9889d917cb1cf55fa167`.
- Exact-head Canon Garden CI run: `29643962608`, success.
- Current product-authority PR #201 head: `4346bfe11da0fa96ec89a5b79826997c25595035`.
- PR #201 and PR #202 remain open, draft and unmerged.

### Central-audit reconciliation requirement

The default five-file profile remains unchanged. Canon Garden uses one stronger integrated workflow and therefore requires one narrow centrally owned profile selected only by the exact verified remote identity `armpitpete/canon-garden`.

The profile requires:

- `AGENTS.dd`;
- `STATUS.md`;
- `docs/authority/AUTHORITY.md`;
- `scripts/validate_project_control.py`;
- `.github/workflows/validate-entries.yml`;
- `scripts/ci-guardrail-check.js`;
- exactly one workflow file, `validate-entries.yml`;
- exactly one command:
  `python3 scripts/validate_project_control.py --repository armpitpete/canon-garden`.

No folder name, status metadata, repository content, wildcard, fallback filename or target declaration may activate the profile.

Canon Garden promotion remains blocked until the central reconciliation is independently reviewed, merged, installed and proven by the local audit.

## Contract B1-LI — lirava PR #82

### Initial reviewed state

- Base: `main` at `1e5a6c1989cea6a987f2df33fab7e3d680630f30`.
- Head: `019031b61edac5affacaa34d8f71b8c48189c262`.
- History: 3 ahead, 0 behind.
- Initial paths: `.github/workflows/project-control.yml`, `AGENTS.md`, `STATUS.md`.
- CI: Build run `29606981732` and Project control run `29606981763` passed.
- Product leakage: none.

### Repair contract

Allowed files:

- `.github/workflows/project-control.yml`;
- `AGENTS.md`;
- `STATUS.md`;
- `docs/authority/AUTHORITY.md`;
- `scripts/validate_project_control.py`.

Preserve all pre-existing Lirava Codex instructions byte-for-byte after the control preamble. Refresh current product authority before writing. Replace the embedded validator. Prohibit code, prompt, UI, test, product-contract and behaviour changes. Rerun both Build and Project control workflows.

### Current disposition

`REPAIR REQUIRED`; no B1-LI implementation is authorised in the B1-CG lane.

## Contract B1-MV — merrin-voice-01 PR #50

### Initial reviewed state

- Base: `main` at `8df52377de753c8c910d67fc31405782d52a1be8`.
- Head: `9982abf4112f220a74356ca615feacdcdca77937`.
- History: 3 ahead, 0 behind.
- Initial paths: `.github/workflows/project-control.yml`, `AGENTS.md`, `STATUS.md`.
- CI: Project control run `29606906848` passed.
- Hardware leakage: none.

### Repair contract

Allowed files:

- `.github/workflows/project-control.yml`;
- `AGENTS.md`;
- `STATUS.md`;
- `docs/authority/AUTHORITY.md`;
- `scripts/validate_project_control.py`.

Refresh the diagnostic lane from current electrical authority. Replace the embedded validator. Prohibit circuit, symbol, coordinate, value, footprint, PCB, routing, panel, fabrication, purchasing and manufacturing changes.

### Current disposition

`REPAIR REQUIRED`; no B1-MV implementation is authorised in the B1-CG lane.

## Contract B1-SEC — story-evidence-collector PR #146

### Initial reviewed state

- Base: `main` at `17289a439f3b9573f7372b66fa24936b672e7c68`.
- Head: `6b9bba1b3a85da360b338a93547f29a68259792f`.
- History: 3 ahead, 0 behind.
- Initial paths: `.github/workflows/project-control.yml`, `AGENTS.md`, `STATUS.md`.
- CI: Project control run `29607089209` passed.
- Collector/server/report leakage: none.

### Repair contract

Allowed files:

- `.github/workflows/project-control.yml`;
- `AGENTS.md`;
- `STATUS.md`;
- `docs/authority/AUTHORITY.md`;
- `scripts/validate_project_control.py`.

Reverify PRs #144 and #145 before retaining or changing `BLOCKED` status. Replace the embedded validator. Prohibit collector, live-server, report-generator, schema, fixture and product changes.

### Current disposition

`REPAIR REQUIRED`; no B1-SEC implementation is authorised in the B1-CG lane.

## Current Batch 1 disposition

| Repository | Current control state | Decision |
|---|---|---|
| `commentate-this` | merged and locally verified `CONTROLLED` | COMPLETE |
| `canon-garden` | PR #202 repaired and current-main reconciled; central profile reconciliation prepared on PR #12 | CENTRAL REVIEW REQUIRED |
| `lirava` | initial repair contract only | REPAIR REQUIRED |
| `merrin-voice-01` | initial repair contract only | REPAIR REQUIRED |
| `story-evidence-collector` | initial repair contract only | REPAIR REQUIRED |

## Stop point

Stop before marking project-folder-checker PR #12 ready, merging PR #12, installing unmerged central tooling, modifying or merging Canon Garden PR #202, modifying PR #201, or beginning another Batch 1 contract.
