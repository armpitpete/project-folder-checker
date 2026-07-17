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
- tests, CI and documentation for this diagnostic lane.

## Forbidden changes

- editing any of the 19 target repositories;
- opening target-repository branches or pull requests;
- replacing or weakening existing project authority;
- bulk-copy migration without repository-specific inspection;
- deleting, moving, renaming or archiving repositories;
- deleting the disposable proof repository;
- beginning implementation before separate authority.

## Validation

- project-control validator passes in this repository;
- the migration authority names the proven audit counts;
- every inventory entry resolves to one local repository and, where applicable, one GitHub remote;
- all 19 unmanaged repositories receive one migration classification;
- every proposed implementation route identifies allowed files, expected diff, validation and stop point;
- repository diff remains limited to this migration lane's authority, register and diagnostic tooling.

## Done

- Central future-project enforcement merged to `main` using merge commit `25cab54a0dea61d9a5e36041c2d6577fb8f2e614`.
- Mandatory project creation from `armpitpete/project-template` proven end to end.
- Disposable proof repository retained at head `0ce94044cbb2cee8dd186968eb6cb2329924ca9c`.
- Central audit proved `UNMANAGED=19` and `BOOTSTRAP=1`.
- Separate migration authority opened without changing any target repository.

## To do

- Import the exact 19-repository inventory from `I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md`.
- Reconcile each entry with its local exact head and GitHub remote.
- Identify existing `AGENTS.md`, `STATUS.md`, authority and CI structures.
- Assign migration classification, risk and sequence.
- Produce one exact migration contract per repository.
- Propose bounded migration batches for separate authorisation.

## Next bounded gate

Import the exact audit inventory, reconcile all 19 repository identities and produce the complete migration register without modifying any target repository.

## Stop point

Stop before making any file change, branch or pull request in a target repository.