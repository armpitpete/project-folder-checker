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

## Centrally owned audit profiles

The default profile remains unchanged and applies to every repository unless an exact verified remote identity is present in the centrally owned profile map.

### Default profile

Required files:

1. `AGENTS.md`;
2. `STATUS.md`;
3. `docs/authority/AUTHORITY.md`;
4. `scripts/validate_project_control.py`;
5. `.github/workflows/project-control.yml`.

The default workflow must invoke `validate_project_control.py`. No alternative workflow filename, wildcard lookup or repository-declared exception is accepted.

### Canon Garden integrated profile

Exactly one non-default profile is approved:

```text
repository identity: armpitpete/canon-garden
workflow: .github/workflows/validate-entries.yml
additional required file: scripts/ci-guardrail-check.js
exact workflow set: validate-entries.yml only
exact validator command:
python3 scripts/validate_project_control.py --repository armpitpete/canon-garden
```

The complete required file set is:

1. `AGENTS.md`;
2. `STATUS.md`;
3. `docs/authority/AUTHORITY.md`;
4. `scripts/validate_project_control.py`;
5. `.github/workflows/validate-entries.yml`;
6. `scripts/ci-guardrail-check.js`.

A missing required file is `UNMANAGED`. An additional workflow, missing validator command, altered repository argument or duplicate exact command is `DRIFTED`.

### Profile selection authority

Non-default profile selection is:

- centrally owned;
- keyed only by an exact repository identity normalised from the configured GitHub `origin` remote;
- unavailable when the remote is missing or cannot be normalised;
- unaffected by folder name, `STATUS.md`, repository content, command-line owner input or any target-repository declaration.

A repository cannot select, request or imitate a non-default profile. Repositories without an exact verified profile identity continue under the unchanged default profile.

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
