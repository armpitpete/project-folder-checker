# Project Folder Checker

A small Windows desktop helper for checking messy project folders.

It scans a folder and creates a simple Markdown report showing:

- total files and folders
- file types found
- large files
- possible old drafts
- duplicate filenames
- recently changed files
- empty folders
- suggested clean-up actions

It does **not** delete, move, rename, or change any files in the scanned folder.

## What it does

You can use it in two ways:

1. Double-click the app and choose a folder.
2. Drag a folder onto the app.

The report is saved beside the app and opens automatically.

Report filename format:

```text
NAME OF FOLDER report.md
```

Example:

```text
VAELINYA report.md
```

## Why it exists

Project folders can get messy quickly. This tool gives a safe first look before you start cleaning anything.

It is designed to be boring, clear, and safe.

## Current version

```text
v0.4
```

Current behaviour:

- simple app window
- choose-folder button
- drag-folder support
- Markdown report output
- automatic report opening
- no command window when run as `.pyw`
- no automatic file changes

## Requirements

- Windows
- Python 3.10 or newer

The app uses only Python standard library modules.

## Run from source

Clone the repo:

```powershell
git clone https://github.com/armpitpete/project-folder-checker.git
cd project-folder-checker
```

Run:

```powershell
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

## Safety rule

This app reports only.

It should not delete, move, rename, or modify scanned project files automatically.

## Licence

MIT Licence.
