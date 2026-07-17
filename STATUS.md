---
completion_authority: true
standard: Recursive Project Improvement Standard v1.0
project_slug: project-folder-checker
project_name: Project Folder Checker
project_type: system
template_mode: false
status: AUTHORISED
authority_files:
  - docs/authority/AUTHORITY.md
  - docs/authority/EXISTING_REPOSITORY_MIGRATION.md
  - docs/authority/EXISTING_REPOSITORY_MIGRATION_REVIEW.md
---

# Project Status

## Current authority

`main` at exact merge commit `25cab54a0dea61d9a5e36041c2d6577fb8f2e614`, plus the exact current migration-lane branch head.

Reviewed sources:

- audit SHA-256 `386E0E2B79D7139D53A59491F96165469866D76F41DF842715176047CBB77844`;
- `ACTIVE_WORK.md` SHA-256 `19B3F60DEEBC67306E2156ED9138625B24CC849B45C38B8C5D42BC37318B5FAC`.

## Current lane

Batch 0 authority-machine reconciliation only.

## Allowed scope

- fast-forward the clean local `project-folder-checker` checkout from `05ae228e79cb4d591d0e984387140d08a0cdc08d` to exact remote `main` `25cab54a0dea61d9a5e36041c2d6577fb8f2e614`;
- use fast-forward only;
- record `pewdiepie-archdaemon/odysseus` as an external-upstream exception in central control records;
- rerun the central project-control audit;
- record exact Batch 0 proof;
- add and validate the fail-closed authority-machine runner for those actions.

## Forbidden changes

- no target-repository change except the authorised `project-folder-checker` fast-forward;
- no modification, fork, migration, branch, pull request, push, archive, rename or deletion for `pewdiepie-archdaemon/odysseus`;
- no review, refresh, creation or promotion of any other target control pull request;
- no repository removal or relocation;
- no deletion of the disposable proof repository.

## Validation

- local `project-folder-checker` must begin clean on branch `main` at the authorised old or resumable new head;
- `origin/main` must equal the authorised new head exactly;
- the update must be a fast-forward;
- final local head must equal the authorised new head and remain clean;
- every other local repository HEAD must remain unchanged;
- the external-upstream exception record must be written centrally;
- the rerun audit must classify `armpitpete/project-folder-checker` as `CONTROLLED`;
- the raw ownership-neutral audit may retain `pewdiepie-archdaemon/odysseus` as structurally `UNMANAGED`, while the exception record excludes it from the owned migration queue;
- final Batch 0 result must record `OTHER_REPOSITORY_HEADS_CHANGED=0`.

## Done

- Central future-project enforcement merged and proven.
- Read-only importer completed from the exact source hashes.
- Full 19-record register produced and reviewed.
- Eight existing control pull requests identified: five mergeable and three conflicted.
- Batch 0 explicitly authorised by the owner.
- Fail-closed, resumable Batch 0 authority-machine runner added.
- Windows PowerShell parser validation added for the Batch 0 runner.

## To do

- run the guarded Batch 0 command on the Windows authority machine;
- preserve `PROJECT_CONTROL_EXCEPTIONS.md`;
- preserve the rerun `PROJECT_CONTROL_AUDIT.md`;
- preserve `EXISTING_REPOSITORY_MIGRATION_BATCH_0_RESULT.md`;
- stop before Batch 1 or any other target-repository change.

## Next bounded gate

Run `tools/Run-ExistingRepositoryMigrationBatch0.ps1` on the authority machine and return the complete terminal output.

## Stop point

Stop immediately after Batch 0 proof. No other target-repository change is authorised.
