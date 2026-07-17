# Existing-Repository Migration Register Review

## Authority

- Source register: `I:\ORDER\MainVault\00_Control\EXISTING_REPOSITORY_MIGRATION_REGISTER.md`
- Source audit SHA-256: `386E0E2B79D7139D53A59491F96165469866D76F41DF842715176047CBB77844`
- Active-work SHA-256: `19B3F60DEEBC67306E2156ED9138625B24CC849B45C38B8C5D42BC37318B5FAC`
- Source records reviewed: **19**
- Target-repository changes authorised during review: **0**

## Review finding

The generated activity classifications are useful as descriptive labels, but they are not safe implementation gates.

Five records marked `READY_FOR_CONTROL_MIGRATION` are not ready from the inspected local heads:
- one is already controlled remotely;
- one is on a diverged feature branch;
- three are stale local checkouts.

Two `INACTIVE` repositories are the only clean, exact-head-aligned candidates for designing new control PRs.

## Reviewed execution dispositions

### Already controlled; stale local checkout — 1

- `armpitpete/project-folder-checker`
  - local audited head: `05ae228e79cb4d591d0e984387140d08a0cdc08d`;
  - remote authority: merge commit `25cab54a0dea61d9a5e36041c2d6577fb8f2e614`;
  - route: fast-forward local `main`; do not create another control PR.

### External upstream; exclude or fork decision — 1

- `pewdiepie-archdaemon/odysseus`
  - remote owner is outside `armpitpete`;
  - route: record external-upstream exception;
  - do not modify, fork or migrate without separate authority.

### Existing control PR; mergeable review — 5

- `armpitpete/commentate-this` PR #3 — `a3d8c1c1cfef46d3422f32b2d0fead9b8deb5e5a`.
- `armpitpete/canon-garden` PR #202 — `dba89b9df57828c84c89d57e8d38261fe5ca6027`.
- `armpitpete/lirava` PR #82 — `019031b61edac5affacaa34d8f71b8c48189c262`.
- `armpitpete/merrin-voice-01` PR #50 — `9982abf4112f220a74356ca615feacdcdca77937`.
- `armpitpete/story-evidence-collector` PR #146 — `6b9bba1b3a85da360b338a93547f29a68259792f`.

### Existing control PR; conflicted refresh — 3

- `armpitpete/threshold-angels` PR #5 — `3d28b0cff886e65bcadfb0f0858d90f30ae7d408`.
- `armpitpete/unmurderous-objects` PR #15 — `95d953a702f29052cc7e9c97fe7e7ff971f788b8`.
- `armpitpete/curious-world-of-ellie-morcant` PR #108 — `7fe06dd3296ca6123f8942aa821e745ee139d1fc`.

Ellie PR #108 was missed by the register's most-recent-50-PR inspection window. It remains open and must be refreshed rather than duplicated.

### New control design from exact aligned head — 2

- `armpitpete/diary-of-sound` — `c30a9fd918eabec0c37036a644fe64b025846844`.
- `armpitpete/synth` — `a69f0b49b961cef8b730b44474f5a14ae1611767`.

### Remote-head reconciliation before design — 5

- `armpitpete/vaelinya-site` — behind 1.
- `armpitpete/merrinworld-site` — behind 2.
- `armpitpete/a-book-for-neurodivergent-minds` — behind 3.
- `armpitpete/evergreen-home-control` — behind 11.
- `armpitpete/thisweekinsmoke` — behind 55.

### Branch-authority decision — 1

- `armpitpete/book-system-os`: clean feature branch diverged from `main`; select the authoritative base before control design.

### Dirty-worktree preservation before design — 1

- `armpitpete/behringer-system-55-guide`: preserve and classify seven uncommitted entries before any migration branch.

## Batch order

### Batch 0 — inventory correction

1. Fast-forward the clean local `project-folder-checker` checkout to exact remote `main` `25cab54a0dea61d9a5e36041c2d6577fb8f2e614`.
2. Record `pewdiepie-archdaemon/odysseus` as an external-upstream exception.
3. Rerun the central audit.
4. Stop.

**Owner authority granted.** Execute only through `tools/Run-ExistingRepositoryMigrationBatch0.ps1`. Preserve every other repository HEAD and stop after the Batch 0 result record.

### Batch 1 — existing mergeable control PR review

Review the five mergeable PRs independently. No group merge authority.

### Batch 2 — conflicted control PR refresh

Refresh the three conflicted PRs independently from exact current authority. No duplicate PRs.

### Batch 3 — aligned inactive repositories

Design repository-specific controls for `diary-of-sound` and `synth`, one exact-head gate at a time.

### Batch 4 — clean stale checkout reconciliation

Reconcile the five clean stale checkouts in increasing divergence order, rerun the audit, then design controls separately.

### Batch 5 — exceptional local authority

Resolve `book-system-os` branch authority and preserve/classify the Behringer dirty worktree before control design.

## Global boundaries

- Every repository remains an independent exact-head gate.
- No bulk migration branch or cross-repository commit.
- No target project content change.
- No squash or rebase assumption.
- No merge without separate exact-head authority.
- Preserve the disposable proof repository.

## Stop point

Batch 0 only is authorised. Stop immediately after its proof record and central audit rerun. No Batch 1 or other target-repository action is authorised.
