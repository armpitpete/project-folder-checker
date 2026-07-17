# Central Future-Project Enforcement

## Purpose

This lane makes the project-control workflow the default creation path for future
projects and independently detects repositories created outside that path.

## Authoritative creation path

Install the central tools into:

```text
I:\ORDER\MainVault\00_Control\Project_Bootstrap
```

Create a project with:

```powershell
& "I:\ORDER\MainVault\00_Control\Project_Bootstrap\New-OrderProject.ps1" `
  -RepositoryName "example-project" `
  -ProjectName "Example Project" `
  -ProjectType "system"
```

The creator:

1. refuses any template except `armpitpete/project-template`;
2. verifies that the source repository is enabled as a GitHub template;
3. creates the remote repository;
4. clones it into `I:\ORDER\GitHub`;
5. runs `scripts\initialise_project.py`;
6. runs `scripts\validate_project_control.py`;
7. verifies that initialization changed only `STATUS.md` and
   `docs/authority/AUTHORITY.md`;
8. commits those exact changes;
9. pushes `main`;
10. validates again after push;
11. reruns the cross-project audit when the audit runner is installed.

A failed creation is preserved for diagnosis. The script never deletes a remote
repository or local clone automatically.

## Audit command

```powershell
& "I:\ORDER\MainVault\00_Control\Project_Bootstrap\Run-ProjectControlAudit.ps1"
```

The audit writes:

```text
I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md
```

## Classifications

| Classification | Meaning | Project work |
|---|---|---|
| `CONTROLLED` | Mandatory control structure and validator pass | Allowed within the recorded lane |
| `BOOTSTRAP` | Controls pass; source authority is not established | Assessment only |
| `DRIFTED` | Controls exist but conflict or fail validation | Blocked |
| `UNMANAGED` | Mandatory controls are absent | Blocked |
| `BLOCKED` | Controls pass and `STATUS.md` explicitly blocks work | Blocked |

## Read-only boundary

The auditor:

- reads repository files;
- invokes the repository's declared control validator;
- compares worktree state before and after validator execution;
- writes one external Markdown report.

It does not edit, repair, stage, commit, push, move, rename or delete anything
inside a scanned repository.

## Disposable proof

Run:

```powershell
& "I:\ORDER\MainVault\00_Control\Project_Bootstrap\Prove-Central-Project-Control.ps1"
```

The default proof repository is:

```text
armpitpete/project-control-disposable-proof-20260717
```

Proof is complete when:

- the remote repository exists;
- the clone exists beneath `I:\ORDER\GitHub`;
- initialization committed and pushed;
- repository validation passes;
- the central audit classifies it as `BOOTSTRAP`;
- `DISPOSABLE_PROOF.md` records the exact repository head.

Stop before deletion.
