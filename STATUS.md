---
completion_authority: true
standard: Recursive Project Improvement Standard v1.0
project_slug: project-folder-checker
project_name: Project Folder Checker
project_type: system
template_mode: false
status: DIAGNOSTIC
authority_files:
  - docs/authority/AUTHORITY.md
  - docs/authority/EXISTING_REPOSITORY_MIGRATION.md
---

# Project Status

## Current authority

`main` at exact merge commit `25cab54a0dea61d9a5e36041c2d6577fb8f2e614`, plus the exact current migration-lane branch head.

## Current lane

Existing-repository control migration for the 19 repositories classified `UNMANAGED` by the proven central audit.

## Allowed scope

- import and preserve the exact audit inventory;
- reconcile local repository paths with GitHub remotes;
- inspect existing authority and workflow structures;
- classify migration complexity and exceptions;
- design one exact bounded migration contract per repository;
- define reviewable migration batches;
- add read-only diagnostic import tooling, tests, CI and documentation for this lane.

## Forbidden changes

- editing any of the 19 target repositories;
- opening target-repository branches or pull requests;
- replacing or weakening existing project authority;
- bulk-copy migration without repository-specific inspection;
- running `git fetch`, checkout, reset, pull, add, commit or push in a target repository;
- deleting, moving, renaming or archiving repositories;
- deleting the disposable proof repository;
- beginning implementation before separate authority.

## Validation

- project-control validator passes in this repository;
- the migration authority names the proven audit counts;
- the importer rejects any inventory count other than exactly 19;
- every inventory entry resolves to one local path and records one exact local head;
- GitHub reconciliation uses read-only API requests and does not update local refs;
- all 19 unmanaged repositories receive one migration classification and one complete 13-field contract;
- fixture proof confirms no target worktree changes;
- repository diff remains limited to migration authority, importer, tests, wrapper and CI.

## Done

- Central future-project enforcement merged to `main` using merge commit `25cab54a0dea61d9a5e36041c2d6577fb8f2e614`.
- Mandatory project creation from `armpitpete/project-template` proven end to end.
- Disposable proof repository retained at head `0ce94044cbb2cee8dd186968eb6cb2329924ca9c`.
- Central audit proved `UNMANAGED=19` and `BOOTSTRAP=1`.
- Separate migration authority opened without changing any target repository.
- Read-only migration importer implemented.
- Exact 19-entry fixture import passed.
- Count-mismatch rejection passed.
- Fixture worktree preservation passed for all 19 repositories.

## To do

- Run the importer against `I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md` and `ACTIVE_WORK.md` on the authority machine.
- Preserve the generated register at `I:\ORDER\MainVault\00_Control\EXISTING_REPOSITORY_MIGRATION_REGISTER.md`.
- Import the generated register into this diagnostic lane.
- Review the 19 classifications, exact heads, existing migration vehicles and proposed routes.
- Propose bounded migration batches for separate authorisation.

## Next bounded gate

Run the read-only importer on the Windows authority machine, then import the complete generated register without modifying any target repository.

## Stop point

Stop before making any file change, branch or pull request in a target repository.
