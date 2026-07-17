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
- record conflicts requiring repository-specific decisions.

## Forbidden changes

- no edits inside any of the 19 target repositories;
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