# Project Folder Checker

[![Build Windows app](https://github.com/armpitpete/project-folder-checker/actions/workflows/build-windows.yml/badge.svg)](https://github.com/armpitpete/project-folder-checker/actions/workflows/build-windows.yml)
[![Project control](https://github.com/armpitpete/project-folder-checker/actions/workflows/project-control.yml/badge.svg)](https://github.com/armpitpete/project-folder-checker/actions/workflows/project-control.yml)

Project Folder Checker is a small, safe Windows desktop tool for checking project folders.

It also provides the central read-only audit used to enforce project-control
authority across repositories beneath `I:\ORDER\GitHub`.

## Desktop folder inspection

The desktop app scans a selected folder and creates a plain Markdown report
showing whether the folder looks clean, messy, or worth reviewing.

It is designed to answer one simple question:

> Is this project folder clean enough to leave alone?

### Download the Windows app

For normal use, download the Windows `.exe` from GitHub Releases:

```text
Releases → latest release → Project.Folder.Checker.exe
```

Then:

1. Double-click the app.
2. Click **Choose Folder to Scan**.
3. Select the project folder you want to check.

Windows may warn that the app is from an unknown publisher because it is not
code-signed.

### What the desktop app checks

- total files and folders;
- file types found;
- large files;
- possible old drafts;
- duplicate filenames;
- recently changed files;
- empty folders;
- suggested clean-up actions.

### Desktop safety boundary

The desktop app is report-only. It does not:

- delete files;
- move files;
- rename files;
- edit files;
- reorganise folders;
- automatically clean anything.

The app gives information. The user decides what to do next.

### Desktop report output

The report is saved beside the app and opens automatically.

Filename format:

```text
NAME OF FOLDER report.md
```

## Central future-project enforcement

The repository also contains the mandatory future-project creation and auditing
tools.

Canonical documentation:

```text
docs/central-project-enforcement.md
```

### Install the central tools

From a current local checkout:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\tools\Install-Central-Project-Control.ps1
```

The installer writes verified copies to:

```text
I:\ORDER\MainVault\00_Control\Project_Bootstrap
```

### Create a future project

```powershell
& "I:\ORDER\MainVault\00_Control\Project_Bootstrap\New-OrderProject.ps1" `
  -RepositoryName "example-project" `
  -ProjectName "Example Project" `
  -ProjectType "system"
```

The creator refuses non-authoritative templates and always uses:

```text
armpitpete/project-template
```

It creates the repository, clones it into `I:\ORDER\GitHub`, initialises its
authority records, validates them, commits the exact initialisation diff and
pushes the resulting `main`.

### Audit every local repository

```powershell
& "I:\ORDER\MainVault\00_Control\Project_Bootstrap\Run-ProjectControlAudit.ps1"
```

The audit writes:

```text
I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md
```

Every Git repository directly beneath `I:\ORDER\GitHub` is classified as:

- `CONTROLLED`;
- `BOOTSTRAP`;
- `DRIFTED`;
- `UNMANAGED`;
- `BLOCKED`.

Repositories classified as `DRIFTED`, `UNMANAGED` or `BLOCKED` must not continue
project work until the recorded control problem is resolved.

The audit is read-only. It does not repair or alter scanned repositories.

### Prove the complete workflow

```powershell
& "I:\ORDER\MainVault\00_Control\Project_Bootstrap\Prove-Central-Project-Control.ps1"
```

The proof creates and retains one disposable private repository, verifies its
pushed authority state and requires the audit to classify it as `BOOTSTRAP`.
It stops before deletion.

## Current desktop version

`v0.9`

Current desktop behaviour:

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

### Windows app

- Windows.

### Source and central enforcement tools

- Windows;
- Python 3.10 or newer;
- Git;
- GitHub CLI authenticated with `gh auth login`.

The Python code uses only standard-library modules.

## Run the desktop app from source

```powershell
git clone https://github.com/armpitpete/project-folder-checker.git
cd project-folder-checker
python "src\Project Folder Checker.pyw"
```

Or double-click:

```text
src/Project Folder Checker.pyw
```

## Build a one-file Windows app

See:

```text
docs/build-windows.md
```

## Governing safety rule

Project Folder Checker reports only.

It must not delete, move, rename, edit or automatically repair scanned project
content.

## Licence

MIT Licence.
