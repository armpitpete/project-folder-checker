# Existing-Repository Control Migration Authority

## Trigger

The proven central audit completed on 2026-07-17 with:

```text
CONTROLLED=0
BOOTSTRAP=1
DRIFTED=0
UNMANAGED=19
BLOCKED=0
```

The single `BOOTSTRAP` repository is the retained disposable proof repository at exact head
`0ce94044cbb2cee8dd186968eb6cb2329924ca9c`.

## Lane purpose

Convert the 19 existing unmanaged local repositories into explicitly controlled repositories without overwriting, simplifying or contradicting their existing project authority.

## Current phase

Inventory and migration-contract design only.

## Allowed scope

- import the exact repository list from `I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md`;
- verify each local repository path and corresponding GitHub remote;
- identify existing authority, status, agent and workflow files;
- classify each repository as active, inactive, archived, duplicate, exceptional or ready for control migration;
- define one bounded migration contract per repository;
- group migrations into reviewable batches without implementing them;
- record conflicts requiring repository-specific decisions;
- use error-tolerant, read-only filesystem traversal that prunes generated caches and records inaccessible non-cache paths without aborting the complete register.

## Forbidden changes

- no edits inside any of the 19 target repositories;
- no creation of target-repository branches or pull requests;
- no replacement of existing authority records;
- no migration by bulk copy without repository-specific inspection;
- no deletion, archiving, renaming or relocation of repositories;
- no deletion of the disposable proof repository;
- no claim that any unmanaged repository is controlled before its own validator passes on an exact reviewed head;
- no fetch, checkout, reset, pull, clean or filesystem-permission change during diagnostic import.

## Required migration record

Each repository must receive a proposed record containing:

1. repository and local path;
2. exact inspected head;
3. existing authority files;
4. conflicting or missing controls;
5. proposed canonical `AGENTS.md` path and content strategy;
6. proposed singular `STATUS.md` authority strategy;
7. validator and CI integration strategy;
8. allowed files;
9. forbidden changes;
10. expected diff;
11. validation commands;
12. review and merge method;
13. exact stop point.

## Read-only importer contract

The importer must:

- read only the source audit, active-work record, local Git metadata, repository files and GitHub GET endpoints;
- decode external command output explicitly as UTF-8 with replacement handling;
- prune `.git`, virtual environments, dependency trees, build products, generated caches, `fastembed_cache`, and `models--*` directories before file access;
- use error-tolerant traversal that does not follow links;
- record inaccessible non-cache paths as diagnostics instead of terminating the whole import;
- write only `I:\ORDER\MainVault\00_Control\EXISTING_REPOSITORY_MIGRATION_REGISTER.md`;
- compare every target worktree status before and after import and require zero changes.

## Observed authority-machine failures

1. Windows Python 3.13 initially decoded GitHub CLI output through CP1252; a UTF-8 byte sequence caused the subprocess reader thread to fail. External command decoding is now explicitly UTF-8 with replacement handling.
2. `Path.rglob()` then attempted to stat an inaccessible generated model-cache file inside `odysseus\data\fastembed_cache`, raising WinError 1920. The official PowerShell entrypoint now routes through the safe scanner described above.

Both failures occurred before successful register completion. Neither authorised or made a target-repository change.

## Successful authority-machine import

The safe-scan importer completed successfully on 2026-07-17 and wrote:

`I:\ORDER\MainVault\00_Control\EXISTING_REPOSITORY_MIGRATION_REGISTER.md`.

Exact imported evidence:

```text
SOURCE_AUDIT_SHA256=386E0E2B79D7139D53A59491F96165469866D76F41DF842715176047CBB77844
ACTIVE_WORK_SHA256=19B3F60DEEBC67306E2156ED9138625B24CC849B45C38B8C5D42BC37318B5FAC
REPOSITORIES=19
ACTIVE=3
INACTIVE=5
ARCHIVED=0
DUPLICATE=0
EXCEPTIONAL=6
READY_FOR_CONTROL_MIGRATION=5
TARGET_REPOSITORIES_CHANGED=0
```

This proves that all 19 audit entries were imported, reconciled and classified without changing any target repository. The generated register remains the detailed authority for the repository names, exact heads, reconciliation evidence and individual migration contracts and must be reviewed before any migration implementation.

## Promotion rule

No target repository may enter implementation until its individual migration record is complete and separately authorised.

## Lane completion condition

This diagnostic lane is complete only when all 19 repositories are named, reconciled against their GitHub remotes, assigned a migration classification and given an exact implementation route or an explicit exception record.

## Stop point

Stop before changing any target repository.
