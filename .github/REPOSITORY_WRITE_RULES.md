# Repository Write Rules — Real-Thing Proof consumer v0.1

## Canonical authorities

This repository consumes, but does not redefine, these exact authorities:

```text
Threadkeeper protocol:
  repository: armpitpete/threadkeeper
  commit: a5bc55336c86097301b378d8654ac92a26ef81e5

Shared Project Status v2 control:
  repository: armpitpete/merrin-project-controls
  commit: 7bc8b7f5ef921851ad163093f089d28d8128bf6c
  schema: schemas/project-status.schema.json
  validator: scripts/validate_project_status.py
```

Local controls may strengthen these authorities. They must not weaken or compete with them.

## Governing rule

> Never test a proxy when the claim concerns the real thing. Never allow `complete` to absorb implementation, deployment, live verification and human acceptance into one vague word.

## Local creator boundary

Project Folder Checker may create a local project from the separately governed mandatory template and may generate a deterministic initial `project-status.json` record.

The generated record must:

- keep percentage and completion likelihood as planning information only;
- preserve all eight lifecycle stages;
- begin with no unsupported PASS result;
- use `INSUFFICIENT` for missing required evidence;
- never infer deployment, live behaviour, human acceptance or completion;
- contain no local path, credential, private inventory or control-plane data.

A generated fixture proves only the creator and validator behaviour. It does not prove that another repository adopted the control, deployed anything, behaves correctly live or received human acceptance.

## Audit boundary

Audit behaviour is read-only. It may report structural drift against an explicitly pinned contract. It must not edit, migrate, merge, repair, archive or delete another repository.

## Protected boundaries

This lane does not authorise:

- `project-template` mutation;
- cross-repository writes;
- bulk migration;
- lifecycle reclassification;
- deployment or production activation;
- historical record rewriting;
- disclosure of private repository inventory or local paths;
- deletion or archival of the disposable proof repository;
- merge without exact-head checks and independent review;
- a portfolio-wide adoption claim.

## Adoption record

- rollout issue: `armpitpete/threadkeeper#123`;
- local issue: `armpitpete/project-folder-checker#14`;
- baseline: `d361bc866385cd0791082e9a4c22a8f0615a4b1e`.
