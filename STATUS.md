---
completion_authority: true
standard: Recursive Project Improvement Standard v1.0
project_slug: project-folder-checker
project_name: Project Folder Checker
project_type: system
template_mode: false
status: REVIEW
authority_files:
  - docs/authority/AUTHORITY.md
  - docs/authority/EXISTING_REPOSITORY_MIGRATION.md
  - docs/authority/EXISTING_REPOSITORY_MIGRATION_REVIEW.md
  - docs/authority/EXISTING_REPOSITORY_MIGRATION_BATCH_0_RESULT.md
  - docs/authority/EXISTING_REPOSITORY_MIGRATION_BATCH_1_REVIEW.md
---

# Project Status

## Current authority

- `main` at exact merge commit `25cab54a0dea61d9a5e36041c2d6577fb8f2e614`.
- Migration lane: project-folder-checker PR #12 on `agent/existing-repository-control-migration`; resolve and verify its exact current head before acting.
- Canon Garden control candidate: PR #202 at exact head `d64a82ddecc29d8685396f6c431418b9b055cf31`, based on `main` at `4768a2dd3c1d7216b3fc9889d917cb1cf55fa167`.
- Canon Garden product authority: PR #201 at exact head `4346bfe11da0fa96ec89a5b79826997c25595035`.

Reviewed sources remain:

- source audit SHA-256 `386E0E2B79D7139D53A59491F96165469866D76F41DF842715176047CBB77844`;
- `ACTIVE_WORK.md` SHA-256 `19B3F60DEEBC67306E2156ED9138625B24CC849B45C38B8C5D42BC37318B5FAC`;
- Batch 0 audit SHA-256 `B382391D7BBBF14024B3BD182263D753CBC117E7C55E0E651D75B482C76B5D36`;
- Batch 0 exception-record SHA-256 `748052AF3903A176E52B64DF5F79B9E7A71A7DAA511D1FAC6FF073AA08030698`.

## Current lane

B1-CG central-audit reconciliation is implemented on PR #12. The active gate is independent exact-head promotion review of that single reconciliation commit.

## Allowed scope

- review the exact PR #12 reconciliation head and its single parent;
- verify the starting-head-to-current-head diff is exactly the five authorised files;
- verify the unchanged default five-file profile;
- verify the centrally owned, verified-identity Canon Garden profile and all positive and negative tests;
- verify complete GitHub Actions results;
- preserve Canon Garden PRs #201 and #202 unchanged;
- prepare a separate exact-head promotion or repair decision.

## Forbidden changes

- no modification of Canon Garden PR #201 or PR #202;
- no target-repository self-declared, folder-name, wildcard or filename-fallback profile;
- no weakening of the default five-file profile;
- no project-template creation-path or classification change;
- no ready transition or merge of project-folder-checker PR #12;
- no merge of Canon Garden PR #202;
- no other Batch 1 or Batch 2 work;
- no repository deletion, relocation or disposable-proof deletion.

## Validation

Required reconciliation validation:

```text
python scripts/validate_project_control.py --repository armpitpete/project-folder-checker
python scripts/test_audit_project_controls.py
python -m py_compile scripts/audit_project_controls.py scripts/test_audit_project_controls.py
```

The profile suite must preserve all five classifications and prove:

- exact verified Canon Garden identity is `CONTROLLED`;
- missing guardrail is `UNMANAGED`;
- competing workflow is `DRIFTED`;
- missing, altered or duplicate exact validator commands are `DRIFTED`;
- non-Canon, spoofed-folder, missing-remote, unparseable-remote and self-declared cases cannot activate the profile;
- repository validator execution preserves a clean worktree;
- a mutating validator is detected as `DRIFTED`.

The complete PR #12 GitHub Actions suite must pass at the exact reconciliation head.

## Done

- Central future-project enforcement merged and proven.
- Batch 0 completed with central audit `CONTROLLED=1`, `BOOTSTRAP=1`, `DRIFTED=0`, `UNMANAGED=18`, `BLOCKED=0`.
- Batch 1 review produced five bounded repair contracts.
- B1-CT was repaired, reviewed, merge-committed and locally verified; Commentate This is `CONTROLLED`.
- Canon Garden PR #202 was repaired and reconciled to current `main`; exact-head CI run `29643962608` passed.
- The central auditor now retains the unchanged default profile and defines one centrally owned Canon Garden integrated-workflow profile.
- Sixteen profile tests cover the existing classifications, positive profile selection, negative profile cases, spoof prevention and read-only validation.
- Canon Garden PRs #201 and #202 remained unchanged during the central-audit reconciliation.

## To do

- perform independent exact-head promotion review of the PR #12 reconciliation commit;
- if approved, separately authorise PR #12 readiness and merge method;
- after merge, install the central auditor into MainVault and rerun the complete local audit;
- return Canon Garden PR #202 for exact-head promotion review under the installed profile;
- separately authorise any Canon Garden ready transition or merge;
- continue no other Batch 1 lane until the B1-CG control sequence reaches its authorised stop.

## Next bounded gate

Review the exact current PR #12 head, confirm its sole parent is `a75c06728e1730e4afd4bb4dc41e1f7197b4e6a1`, confirm the reconciliation diff is exactly the five authorised paths, verify complete CI, and issue either an exact-head promotion contract or one bounded repair contract.

## Stop point

Stop before marking PR #12 ready, merging PR #12, modifying or merging Canon Garden PR #202, modifying PR #201, installing unmerged central tooling, or beginning another Batch 1 lane.
