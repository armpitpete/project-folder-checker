# Real-Thing Proof consumer v0.1

## Exact authorities

- Threadkeeper protocol: `armpitpete/threadkeeper@a5bc55336c86097301b378d8654ac92a26ef81e5`.
- Shared Project Status v2: `armpitpete/merrin-project-controls@7bc8b7f5ef921851ad163093f089d28d8128bf6c`.

Project Folder Checker consumes these controls. It does not redefine them.

## Authoritative local creation entrypoint

Use `tools/New-ControlledOrderProject.ps1` for new controlled projects.

It runs the existing mandatory-template creation path, then adds one deterministic `project-status.json` file in a separate bounded commit. The file starts with:

- planning estimate `0`;
- claimed stage `designed`;
- verified state `insufficient`;
- no lifecycle PASS result;
- no deployment, live-behaviour, human-acceptance or completion claim.

The older `New-OrderProject.ps1` remains the lower-level template creator and compatibility library. It is not the complete Project Status v2 integration entrypoint.

## Evidence boundary

Repeated fixture generation and validation prove only:

- the local generator is deterministic;
- the generated record follows the pinned consumer contract;
- percentage cannot create completion;
- proxy evidence cannot create PASS;
- generated generic output excludes named private control-plane fragments.

They do not prove another repository has adopted the control, deployed successfully, behaves correctly live or received human acceptance.

## Read-only audit rule

Project-control audits remain read-only. They may identify missing or stale structures but may not edit, repair, migrate, merge, archive or delete a consumer repository.

## Migration boundary

Existing repositories and historical status records are not rewritten by this lane. Each consumer requires its own collision-checked issue, exact branch, validation, review and merge authority.
