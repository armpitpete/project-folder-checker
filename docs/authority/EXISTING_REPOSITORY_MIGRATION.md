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

Batch 0 authority-machine reconciliation only.

## Allowed scope

- preserve and review the exact imported register;
- verify each local repository path and corresponding GitHub remote;
- identify existing authority, status, agent and workflow files;
- classify migration complexity and exceptions;
- define one bounded migration contract per repository;
- group migrations into reviewable batches without implementing them;
- use error-tolerant, read-only filesystem traversal that prunes generated caches and records inaccessible non-cache paths without aborting the complete register;
- for Batch 0 only, fast-forward the clean local `project-folder-checker` checkout from exact `05ae228e79cb4d591d0e984387140d08a0cdc08d` to exact remote `main` `25cab54a0dea61d9a5e36041c2d6577fb8f2e614` using fast-forward only;
- record `pewdiepie-archdaemon/odysseus` as an external-upstream exception in central control records;
- rerun the central project-control audit and write the exact Batch 0 result record.

## Forbidden changes

- no edit inside any target repository except the exact authorised `project-folder-checker` fast-forward;
- no creation, update or promotion of any other target-repository branch or pull request;
- no replacement of existing authority records;
- no migration by bulk copy without repository-specific inspection;
- no deletion, archiving, renaming or relocation of repositories;
- no deletion of the disposable proof repository;
- no claim that any unmanaged repository is controlled before its own validator passes on an exact reviewed head;
- no modification, fork, migration, branch, pull request, push, archive, rename or deletion for `pewdiepie-archdaemon/odysseus`;
- no Batch 1 or later action without separate authority.

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

## Batch 0 execution contract

The guarded runner must:

- require local `project-folder-checker` branch `main` and a clean worktree;
- accept only the exact authorised old head or resumable exact new head;
- fetch `origin/main` without tags and require it to equal the exact authorised new head;
- prove the relationship is fast-forward-only;
- apply `git merge --ff-only` when still at the old head;
- require the final head and clean worktree exactly;
- snapshot all direct local repository HEADs and require every other HEAD to remain unchanged;
- preserve the imported register and verify its source-audit hash;
- write `PROJECT_CONTROL_EXCEPTIONS.md` for the external-upstream exception;
- rerun `PROJECT_CONTROL_AUDIT.md`;
- require `project-folder-checker` to classify as `CONTROLLED`;
- retain the raw structural audit result for `odysseus` while excluding it from the owned migration queue through the exception record;
- write `EXISTING_REPOSITORY_MIGRATION_BATCH_0_RESULT.md`;
- print `OTHER_REPOSITORY_HEADS_CHANGED=0` and stop.

## Observed authority-machine failures

1. Windows Python 3.13 initially decoded GitHub CLI output through CP1252; a UTF-8 byte sequence caused the subprocess reader thread to fail. External command decoding is now explicitly UTF-8 with replacement handling.
2. `Path.rglob()` then attempted to stat an inaccessible generated model-cache file inside `odysseus\data\fastembed_cache`, raising WinError 1920. The official PowerShell entrypoint now routes through the safe scanner described above.

Both failures occurred before successful register completion. Neither authorised or made a target-repository change.

## Promotion rule

No target repository may enter implementation until its individual migration record is complete and separately authorised.

## Lane completion condition

This diagnostic lane is complete only when all 19 repositories are named, reconciled against their GitHub remotes, assigned a reviewed execution disposition and given an exact implementation route or explicit exception record.

## Stop point

Batch 0 only is authorised. Stop immediately after its exact proof record and central audit rerun. No other target-repository change is authorised.
