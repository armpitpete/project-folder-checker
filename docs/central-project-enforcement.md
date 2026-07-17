# Central Future-Project Enforcement

## Purpose

Make the mandatory project-control workflow the only supported route for creating future repositories, while independently detecting repositories that bypass or drift from that control layer.

## Canonical creation path

Use:

```text
I:\ORDER\MainVault\00_Control\Project_Bootstrap\New-OrderProject.ps1
```

The creator:

1. accepts only `armpitpete/project-template`;
2. creates the remote repository through GitHub CLI;
3. clones only beneath `I:\ORDER\GitHub`;
4. runs `scripts\initialise_project.py`;
5. runs `scripts\validate_project_control.py` before commit;
6. permits only `STATUS.md` and `docs/authority/AUTHORITY.md` to change during initialization;
7. commits and pushes the initialized authority state;
8. validates again after push;
9. runs the all-repository audit;
10. preserves any partially created repository for diagnosis rather than deleting it automatically.

## Remote-existence probe

The repository-existence check uses `System.Diagnostics.Process` to invoke:

```text
gh api repos/OWNER/REPOSITORY --silent
```

This is deliberate. Windows PowerShell can convert expected native stderr into terminating error records before `$LASTEXITCODE` and the diagnostic text can be read.

The process-based probe captures stdout, stderr and exit status directly:

- exit code `0` means the repository exists;
- GitHub `404` or `Not Found` means the repository is absent and creation may proceed;
- authentication, network and unexpected errors remain blocking.

GitHub Actions tests both an existing repository and a genuinely absent repository through the authenticated GitHub API.

## Audit classifications

Every local Git repository beneath `I:\ORDER\GitHub` is classified as exactly one of:

- `CONTROLLED` — the mandatory files exist and the project-control validator passes;
- `BOOTSTRAP` — control passes and the repository is still in its initial source-assessment state;
- `DRIFTED` — control files exist but conflict, are malformed, or fail validation;
- `UNMANAGED` — mandatory control files are absent;
- `BLOCKED` — the repository explicitly records a blocked state.

The audit is report-only. It does not edit, repair, move or delete repository files.

## Audit output

```text
I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md
```

## Disposable proof

Run:

```powershell
& "I:\ORDER\MainVault\00_Control\Project_Bootstrap\Prove-Central-Project-Control.ps1"
```

The proof creates:

```text
armpitpete/project-control-disposable-proof-20260717
```

and must finish with classification:

```text
BOOTSTRAP
```

The proof repository must remain intact until deletion is separately authorised.

## Repair history

Two initial proof attempts stopped before repository creation during the remote-existence check:

1. Windows PowerShell converted the expected `gh repo view` not-found stderr into a terminating error.
2. Suppressing PowerShell error records also discarded the expected diagnostic text, leaving an uninterpretable nonzero exit.

The final design no longer relies on PowerShell native-command stderr behavior. No remote disposable repository or local clone was created by either failed attempt.
