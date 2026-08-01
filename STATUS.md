---
completion_authority: true
standard: Recursive Project Improvement Standard v1.0
project_slug: project-folder-checker
project_name: Project Folder Checker
project_type: system
template_mode: false
status: IMPLEMENTING
authority_files:
  - docs/authority/AUTHORITY.md
---

# Project Status

## Current authority

`main` at exact commit `25cab54a0dea61d9a5e36041c2d6577fb8f2e614`.

Shared repository-control contracts are governed by `armpitpete/merrin-project-controls` Foundation v0.1 at exact commit `b784573ad86d8d54ba1108dc1bf952260ee4c6bb`.

## Current lane

Maintain the local Windows project creator, folder inspection and read-only repository-control audit tooling.

Project Folder Checker is not the authority for shared cross-repository contracts and must not bulk-migrate other repositories from stale project lanes.

## Allowed scope

- local project and folder inspection;
- local project-creation PowerShell tooling;
- read-only repository-control auditing;
- reporting structural drift against explicitly selected shared contracts;
- tests, CI and documentation for these local tools.

## Forbidden changes

- defining competing shared-control contracts;
- automatically editing another repository;
- bulk-merging or repairing repository-control pull requests;
- deleting, moving, renaming or editing scanned project content;
- storing private repository inventories in public output;
- creating a second completion authority.

## Validation

- project-control validator passes;
- audit classification tests pass;
- PowerShell scripts parse successfully;
- generated-project fixtures initialise and validate;
- public output contains no private repository inventory or local control-plane record.

## Done

- Existing report-only folder inspection application preserved.
- Central local project creator and read-only audit tooling implemented and merged.
- One disposable proof repository created and exercised.
- Sensitive repository inventory and migration work moved behind private visibility.
- The stale existing-repository migration PR was closed without merge.
- Canonical shared-control authority assigned to `merrin-project-controls`.

## To do

- align local template installation with versioned contracts from `merrin-project-controls`;
- remove or clearly supersede obsolete cross-repository migration documentation;
- mark the disposable proof as completed before archival;
- retain only generic, privacy-safe audit output.

## Next bounded gate

Integrate one version-pinned shared control from `merrin-project-controls` into the local project-creation path and prove that the generated fixture remains deterministic and privacy-safe.

## Stop point

Stop before any cross-repository write, bulk migration, proof-repository deletion or shared-contract modification without a separately reviewed exact-head change.
