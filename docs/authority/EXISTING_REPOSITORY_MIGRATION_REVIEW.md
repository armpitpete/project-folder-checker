# Existing-Repository Migration Register Review

## Authority

- Source register: `I:\ORDER\MainVault\00_Control\EXISTING_REPOSITORY_MIGRATION_REGISTER.md`
- Source audit SHA-256: `386E0E2B79D7139D53A59491F96165469866D76F41DF842715176047CBB77844`
- Active-work SHA-256: `19B3F60DEEBC67306E2156ED9138625B24CC849B45C38B8C5D42BC37318B5FAC`
- Source records reviewed: **19**
- Target-repository changes authorised: **0**

## Review finding

The generated activity classifications are useful as descriptive labels, but they are not safe implementation gates.

Five records marked `READY_FOR_CONTROL_MIGRATION` are not ready from the inspected local heads:
- one is already controlled remotely;
- one is on a diverged feature branch;
- three are stale local checkouts.

Two `INACTIVE` repositories are the only clean, exact-head-aligned candidates for designing new control PRs.

Eight repositories already have an open control PR. Five are currently mergeable and three are conflicted. No duplicate migration PR should be opened for any of them.

One repository is an external upstream for which `armpitpete` has no reported collaborator permission and must not be modified as part of this migration.

## Reviewed execution dispositions

| # | Repository | Local head | Remote default head | Source class | Reviewed disposition | Exact next route |
|---:|---|---|---|---|---|---|
| 1 | `armpitpete/a-book-for-neurodivergent-minds` | `d8daa1a6698f2a86b1aa806108c4974d6788d499` | `703eb82da66d4f46f7abffb899b53b7c6bde3296` | INACTIVE | REMOTE-HEAD RECONCILIATION | Inspect/synchronise the remote default head, preserve existing `STATUS.md`, then design an inactive-state control PR. |
| 2 | `armpitpete/behringer-system-55-guide` | `03f704c659a32c71594d6142a1d014dc0584bb16` | `03f704c659a32c71594d6142a1d014dc0584bb16` | EXCEPTIONAL | DIRTY WORKTREE PRESERVATION | Inventory and preserve the seven uncommitted entries before any control branch. |
| 3 | `armpitpete/book-system-os` | `5477203daf1e88d577826cbdb1475e2f1ce69a73` | `597efe713890380c36824d557cf1bcb56df6c90a` | READY_FOR_CONTROL_MIGRATION | BRANCH-AUTHORITY DECISION | Decide whether `codex/add-publish-api-status-v1` or current `main` is authoritative; the inspected branch is diverged. |
| 4 | `armpitpete/canon-garden` | `cbfec9c90b10d5731bdbfd4cabd2856b7b6e4da3` | `e46a68760c7c7a9e931c5f70c9cd7239acd26830` | EXCEPTIONAL | EXISTING CONTROL PR — MERGEABLE REVIEW | Review PR #202 at `dba89b9df57828c84c89d57e8d38261fe5ca6027`; preserve the dirty local worktree; do not create a duplicate PR. |
| 5 | `armpitpete/commentate-this` | `d3e110c8229690bb1072c31ca4aa1d3f61f0c1c1` | `5fef5a4ebd443d0bd5b9cbb11c83b8d121fdcf9a` | ACTIVE | EXISTING CONTROL PR — MERGEABLE REVIEW | Review PR #3 at `a3d8c1c1cfef46d3422f32b2d0fead9b8deb5e5a`. |
| 6 | `armpitpete/curious-world-of-ellie-morcant` | `c8b0bdc842c2ba6fe2b6fd6d215eafbe80e356aa` | `08ba36230afad091673f5ec27cfc7cc912ec874f` | EXCEPTIONAL | EXISTING CONTROL PR — CONFLICTED REFRESH | Preserve the dirty worktree and redesign/refresh PR #108 from current authority; PR #108 is open but unmergeable at `7fe06dd3296ca6123f8942aa821e745ee139d1fc`. |
| 7 | `armpitpete/diary-of-sound` | `c30a9fd918eabec0c37036a644fe64b025846844` | `c30a9fd918eabec0c37036a644fe64b025846844` | INACTIVE | NEW CONTROL DESIGN — EXACT HEAD ALIGNED | Design an inactive-state control PR from this exact head. |
| 8 | `armpitpete/evergreen-home-control` | `3cd7a301a4acc9502c1a4a6bc46df5c428d15c01` | `ca810c09bfeda0eb8b8f16a9abaed6ca6c7156fc` | INACTIVE | REMOTE-HEAD RECONCILIATION | Inspect/synchronise the remote default head before designing inactive controls. |
| 9 | `armpitpete/lirava` | `e59a962a1d64ad263928fa3023544931dbf51357` | `1e5a6c1989cea6a987f2df33fab7e3d680630f30` | EXCEPTIONAL | EXISTING CONTROL PR — MERGEABLE REVIEW | Review PR #82 at `019031b61edac5affacaa34d8f71b8c48189c262`; preserve the dirty local worktree. |
| 10 | `armpitpete/merrin-voice-01` | `b542980d70c288dbc0914560ae21b3673c19f851` | `8df52377de753c8c910d67fc31405782d52a1be8` | EXCEPTIONAL | EXISTING CONTROL PR — MERGEABLE REVIEW | Review PR #50 at `9982abf4112f220a74356ca615feacdcdca77937`; preserve the dirty, diverged local worktree. |
| 11 | `armpitpete/merrinworld-site` | `b5c744e5bb54e78947e6ef8b978de963e27e1e01` | `5ee5b22ccebb4b2d54b75f6ee8422f9dd77ad01f` | READY_FOR_CONTROL_MIGRATION | REMOTE-HEAD RECONCILIATION | Inspect/synchronise the remote default head before designing a control PR. |
| 12 | `armpitpete/project-folder-checker` | `05ae228e79cb4d591d0e984387140d08a0cdc08d` | `25cab54a0dea61d9a5e36041c2d6577fb8f2e614` | READY_FOR_CONTROL_MIGRATION | ALREADY CONTROLLED — LOCAL CHECKOUT STALE | Do not migrate. Synchronise the local checkout to the merged PR #11 authority and rerun the central audit. |
| 13 | `armpitpete/story-evidence-collector` | `17289a439f3b9573f7372b66fa24936b672e7c68` | `17289a439f3b9573f7372b66fa24936b672e7c68` | EXCEPTIONAL | EXISTING CONTROL PR — MERGEABLE REVIEW | Review PR #146 at `6b9bba1b3a85da360b338a93547f29a68259792f`; preserve the dirty local worktree. |
| 14 | `armpitpete/synth` | `a69f0b49b961cef8b730b44474f5a14ae1611767` | `a69f0b49b961cef8b730b44474f5a14ae1611767` | INACTIVE | NEW CONTROL DESIGN — EXACT HEAD ALIGNED | Design an inactive-state control PR from this exact head. |
| 15 | `armpitpete/thisweekinsmoke` | `d21a58ebbbb80a5ae24ff43ebbacf9462b38616f` | `5f54acd8a019db190e5bc1c3f1f235ca7da82b12` | READY_FOR_CONTROL_MIGRATION | REMOTE-HEAD RECONCILIATION | Inspect/synchronise the remote default head before designing a control PR; local `main` is 55 commits behind. |
| 16 | `armpitpete/threshold-angels` | `fed594180981998c29500b240bad222aafb7a2a2` | `d36b27bce02f535293d93269e51337e680880a85` | ACTIVE | EXISTING CONTROL PR — CONFLICTED REFRESH | Refresh or replace PR #5 from current authority; PR #5 is open but unmergeable at `3d28b0cff886e65bcadfb0f0858d90f30ae7d408`. |
| 17 | `armpitpete/unmurderous-objects` | `4f94c8131ca18d708da195d9c2e7f11bcfa58020` | `dfa19a0e8351a980993607e3c711a84435fad6a3` | ACTIVE | EXISTING CONTROL PR — CONFLICTED REFRESH | Synchronise current authority and refresh or replace control PR #15; PR #15 is open but unmergeable at `95d953a702f29052cc7e9c97fe7e7ff971f788b8`. |
| 18 | `armpitpete/vaelinya-site` | `34a6ae33e825594a03e241bedb9e6ac8c35f5c6d` | `e1752cdbd777953175383ea8b6bdcd9c87ef2fb8` | READY_FOR_CONTROL_MIGRATION | REMOTE-HEAD RECONCILIATION | Inspect/synchronise the one newer remote commit before designing a control PR. |
| 19 | `pewdiepie-archdaemon/odysseus` | `dd055ee6e36581ad8c9c539e02b5b9963fbac2a1` | `28d27ee723dc41a4584cba89afb4a377d5c21342` | INACTIVE | EXTERNAL UPSTREAM — EXCLUDE | Do not inject project controls into the upstream repository. Record a local-clone exception or create an owned fork under separate authority. |

## Reviewed totals

- **Already controlled; local audit repair only:** 1
- **External upstream; exclude or fork decision:** 1
- **Existing control PR, mergeable review:** 5
- **Existing control PR, conflicted refresh:** 3
- **New control design from exact aligned head:** 2
- **Remote-head reconciliation before design:** 5
- **Branch-authority decision:** 1
- **Dirty-worktree preservation before design:** 1
- **Total:** 19

## Migration batch order

### Batch 0 — Correct the control inventory

1. `armpitpete/project-folder-checker`: synchronise the stale local checkout and rerun the audit; no migration PR.
2. `pewdiepie-archdaemon/odysseus`: record an external-upstream exception or separately authorise an owned fork.

### Batch 1 — Review existing mergeable control PRs

Each PR remains an independent exact-head gate:

1. `armpitpete/commentate-this` — PR #3 — `a3d8c1c1cfef46d3422f32b2d0fead9b8deb5e5a`
2. `armpitpete/canon-garden` — PR #202 — `dba89b9df57828c84c89d57e8d38261fe5ca6027`
3. `armpitpete/lirava` — PR #82 — `019031b61edac5affacaa34d8f71b8c48189c262`
4. `armpitpete/merrin-voice-01` — PR #50 — `9982abf4112f220a74356ca615feacdcdca77937`
5. `armpitpete/story-evidence-collector` — PR #146 — `6b9bba1b3a85da360b338a93547f29a68259792f`

### Batch 2 — Refresh conflicted existing control PRs

1. `armpitpete/threshold-angels` — PR #5
2. `armpitpete/unmurderous-objects` — PR #15
3. `armpitpete/curious-world-of-ellie-morcant` — PR #108

No old conflicted head may be promoted. Each refresh requires an exact current-main contract and separate authority.

### Batch 3 — Design new controls on aligned inactive repositories

1. `armpitpete/diary-of-sound`
2. `armpitpete/synth`

### Batch 4 — Reconcile clean stale checkouts, then design

Order by increasing divergence:

1. `armpitpete/vaelinya-site` — behind 1
2. `armpitpete/merrinworld-site` — behind 2
3. `armpitpete/a-book-for-neurodivergent-minds` — behind 3
4. `armpitpete/evergreen-home-control` — behind 11
5. `armpitpete/thisweekinsmoke` — behind 55

### Batch 5 — Resolve exceptional local authority

1. `armpitpete/book-system-os`: choose the authoritative branch/base.
2. `armpitpete/behringer-system-55-guide`: preserve and classify the seven dirty entries.

## Stop point

This review authorises no target-repository edit, fetch, checkout, reset, pull, branch, PR update, merge, archive, fork or deletion.

The next gate must name exactly one repository or one explicitly bounded review batch and its exact heads.
