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

## Import authority

The exact source files are:

- `I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md`;
- `I:\ORDER\MainVault\00_Control\ACTIVE_WORK.md`.

The authorised read-only importer is:

- `scripts/build_existing_repository_migration_register.py`;
- PowerShell entrypoint `tools/Build-ExistingRepositoryMigrationRegister.ps1`.

It must:

1. verify exactly 19 `UNMANAGED` findings;
2. hash both source authority files;
3. read local Git heads, branches, origins and worktree state without fetching or changing refs;
4. use read-only GitHub API requests to reconcile remote identity, default head and existing control PRs;
5. classify every migration as `ACTIVE`, `INACTIVE`, `ARCHIVED`, `DUPLICATE`, `EXCEPTIONAL` or `READY_FOR_CONTROL_MIGRATION`;
6. emit one complete 13-field migration record per repository;
7. write `I:\ORDER\MainVault\00_Control\EXISTING_REPOSITORY_MIGRATION_REGISTER.md`;
8. report `TARGET_REPOSITORIES_CHANGED=0`.

## Allowed scope

- import the exact repository list from `I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md`;
- verify each local repository path and corresponding GitHub remote;
- identify existing authority, status, agent and workflow files;
- detect existing open or merged project-control migration vehicles;
- classify each repository as active, inactive, archived, duplicate, exceptional or ready for control migration;
- define one bounded migration contract per repository;
- group migrations into reviewable batches without implementing them;
- record conflicts requiring repository-specific decisions.

## Forbidden changes

- no edits inside any of the 19 target repositories;
- no `git fetch`, pull, checkout, reset, add, commit or push in a target repository;
- no creation of target-repository branches or pull requests;
- no replacement of existing authority records;
- no migration by bulk copy without repository-specific inspection;
- no deletion, archiving, renaming or relocation of repositories;
- no deletion of the disposable proof repository;
- no claim that any unmanaged repository is controlled before its own validator passes on an exact reviewed head.

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

## Promotion rule

No target repository may enter implementation until its individual migration record is complete and separately authorised.

## Lane completion condition

This diagnostic lane is complete only when all 19 repositories are named, reconciled against their GitHub remotes, assigned a migration classification and given an exact implementation route or an explicit exception record.

## Stop point

Stop before changing any target repository.
