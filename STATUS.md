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

`main` at exact commit `05ae228e79cb4d591d0e984387140d08a0cdc08d`.

## Current lane

Central future-project enforcement and all-repository control auditing.

## Allowed scope

- mandatory repository entry and completion authority;
- central project-creation PowerShell tooling;
- read-only project-control auditing;
- control classifications and Markdown reporting;
- tests, CI and documentation for this lane.

## Forbidden changes

- deleting, moving, renaming or editing scanned project content;
- automatic repair of another repository;
- deleting the disposable proof repository;
- weakening the mandatory template route;
- creating a second completion authority;
- unrelated desktop-app redesign.

## Validation

- project-control validator passes;
- audit classification tests pass for all five states;
- PowerShell scripts parse successfully;
- generated-project fixture initialises and validates;
- repository diff contains only authorised control, audit and documentation files.

## Done

- Existing report-only folder inspection application preserved.
- Central enforcement architecture selected.
- Exact classification contract defined.

## To do

- Implement and validate the central project creator.
- Implement and validate all-repository auditing.
- Install central scripts into MainVault.
- Create and validate one disposable repository from the mandatory template.
- Stop before deletion of the disposable repository.

## Next bounded gate

Implement the authorised central bootstrap and audit tooling, publish it for review,
then run one disposable proof repository through the complete workflow.

## Stop point

Stop before deleting the disposable proof repository or merging this implementation
without exact-head authority.
