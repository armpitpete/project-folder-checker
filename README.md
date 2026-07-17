# Project Folder Checker

[![Build Windows app](https://github.com/armpitpete/project-folder-checker/actions/workflows/build-windows.yml/badge.svg)](https://github.com/armpitpete/project-folder-checker/actions/workflows/build-windows.yml)

Project Folder Checker is a small, safe Windows desktop tool for checking project folders and repository control.

It has two report-only roles:

1. inspect an individual project folder for clean-up risks;
2. audit every Git repository under a chosen root for mandatory project control.

## Central future-project enforcement

The repository now contains the canonical enforcement tools for future projects:

```text
tools/New-OrderProject.ps1
tools/Run-ProjectControlAudit.ps1
tools/Prove-Central-Project-Control.ps1
tools/Install-Central-Project-Control.ps1
scripts/audit_project_controls.py
```

`New-OrderProject.ps1`:

- accepts only `armpitpete/project-template`;
- creates and clones beneath `I:\ORDER\GitHub`;
- runs the template initializer and validator;
- permits only the exact initialization changes;
- commits and pushes the initialized authority state;
- runs the cross-project audit;
- preserves failures for diagnosis rather than deleting them;
- treats GitHub's expected “repository not found” response as the safe creation path while keeping authentication and network failures blocking.

The all-repository auditor classifies repositories as:

- `CONTROLLED`
- `BOOTSTRAP`
- `DRIFTED`
- `UNMANAGED`
- `BLOCKED`

Default audit output:

```text
I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md
```

See `docs/central-project-enforcement.md` for the exact operating contract.

## Download the Windows app

For normal folder inspection, download the Windows `.exe` from GitHub Releases:

```text
Releases -> latest release -> Project Folder Checker.exe
```

Then:

1. Double-click the app.
2. Click **Choose Folder to Scan**.
3. Select the project folder you want to check.

Windows may warn that the app is from an unknown publisher because it is not code-signed.

## What the desktop app checks

The folder report includes:

- total files and folders;
- file types found;
- large files;
- possible old drafts;
- duplicate filenames;
- recently changed files;
- empty folders;
- suggested clean-up actions.

## Safety boundary

Project Folder Checker and the project-control auditor are report-only.

They do not:

- delete files or repositories;
- move files;
- rename files;
- edit scanned project files;
- reorganise folders;
- repair authority automatically.

The future-project creator does write only the exact new-repository authority files defined by its contract. It never deletes a failed generated repository automatically.

## Report output

The desktop report is saved beside the app and opens automatically.

Filename format:

```text
NAME OF FOLDER report.md
```

## Current desktop version

```text
v0.9
```

Current behaviour:

- simple Windows app window;
- visible app version;
- **Choose Folder to Scan** button;
- About button;
- Website button;
- Markdown report output;
- automatic report opening;
- no command window when run as `.pyw`;
- no automatic file changes.

## Requirements

For the released `.exe`:

- Windows.

For source use:

- Windows;
- Python 3.10 or newer.

The desktop application and audit use Python standard-library modules only.

The project creator additionally requires:

- Git;
- GitHub CLI `gh`;
- an authenticated GitHub session.

## Run the desktop app from source

```powershell
git clone https://github.com/armpitpete/project-folder-checker.git
cd project-folder-checker
python "src\Project Folder Checker.pyw"
```

## Build a one-file Windows app

See:

```text
docs/build-windows.md
```

## Licence

MIT Licence.
