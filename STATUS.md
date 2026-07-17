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
---

# Project Status

## Current authority

`main` at exact merge commit `25cab54a0dea61d9a5e36041c2d6577fb8f2e614`, plus the exact current migration-lane branch head.

Reviewed sources:

- audit SHA-256 `386E0E2B79D7139D53A59491F96165469866D76F41DF842715176047CBB77844`;
- `ACTIVE_WORK.md` SHA-256 `19B3F60DEEBC67306E2156ED9138625B24CC849B45C38B8C5D42BC37318B5FAC`.

## Current lane

Review and batch design for the 19 existing repositories reported as `UNMANAGED`.

## Allowed scope

- preserve and review the exact register;
- verify local and remote identities and heads;
- correct unsafe classifications;
- identify existing migration vehicles;
- define one safe disposition per repository;
- define bounded review and migration batches.

## Forbidden changes

- no target-repository implementation;
- no new target migration vehicle;
- no promotion of a target control change;
- no repository removal or relocation;
- no deletion of the disposable proof repository.

## Validation

- exactly 19 records reviewed;
- every record has one execution disposition;
- known existing control pull requests verified directly;
- five existing control pull requests are mergeable;
- three existing control pull requests are conflicted;
- one repository is already controlled remotely;
- one repository is an external upstream;
- target repositories changed: zero.

## Done

- Central future-project enforcement merged and proven.
- Read-only importer completed from the exact source hashes.
- Full 19-record register produced.
- Complete register review recorded in `docs/authority/EXISTING_REPOSITORY_MIGRATION_REVIEW.md`.
- `project-folder-checker` corrected from ready-to-migrate to already-controlled with a stale local checkout.
- Ellie control pull request #108 recovered from outside the importer's 50-pull-request window.
- Eight existing control pull requests identified: five mergeable and three conflicted.
- Two clean exact-head-aligned repositories identified for eventual new control design.
- Six bounded execution groups defined.

## To do

- execute no target work without separate authority;
- correct the local control inventory and external-upstream disposition;
- review existing mergeable control pull requests;
- refresh conflicted control pull requests;
- reconcile stale or divergent local authority before new control design.

## Next bounded gate

Authorise Batch 0 only: correct the stale local `project-folder-checker` checkout and record the external-upstream disposition for `pewdiepie-archdaemon/odysseus`, then rerun the central audit.

## Stop point

Stop before any target-repository change without separate explicit authority.
