# Repository Authority

## Source authority

- Preserved repository history.
- Existing report-only desktop application and release workflow on `main`.
- `armpitpete/project-template` at authoritative merge commit
  `820e2ed44484b847a55cf95bfdfc698e6bbf45bd`.
- Recursive Project Improvement Standard v1.0.

## Active authority

The exact current repository head named in root `STATUS.md`.

## Decision authority

This lane authorises:

- one central `New-OrderProject.ps1` creator;
- creation only from `armpitpete/project-template`;
- cloning only into `I:\ORDER\GitHub`;
- mandatory initialization and validation before the first generated-project commit;
- one read-only auditor producing exactly the five classifications
  `CONTROLLED`, `BOOTSTRAP`, `DRIFTED`, `UNMANAGED`, and `BLOCKED`;
- audit output at
  `I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md`;
- one disposable end-to-end proof, retained after proof.

## Completion authority

Root `STATUS.md` is the sole repository-level completion authority.

## Governing constraints

- Folder and repository auditing remains report-only.
- The auditor must not repair another repository.
- Project creation must refuse any template other than
  `armpitpete/project-template`.
- Generated repositories must run `scripts/initialise_project.py` and
  `scripts/validate_project_control.py` before commit and after push.
- A failed creation is preserved for diagnosis; automatic deletion is prohibited.
- The disposable proof repository must remain undeleted at the lane stop.
