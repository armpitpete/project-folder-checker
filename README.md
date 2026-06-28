# Project Folder Checker

[![Build Windows app](https://github.com/armpitpete/project-folder-checker/actions/workflows/build-windows.yml/badge.svg)](https://github.com/armpitpete/project-folder-checker/actions/workflows/build-windows.yml)

Project Folder Checker is a small, safe Windows desktop tool for checking project folders.

It scans a selected folder and creates a plain Markdown report showing whether the folder looks clean, messy, or worth reviewing.

It is designed to answer one simple question:

Is this project folder clean enough to leave alone?

## Download the Windows app

For normal use, download the Windows `.exe` from GitHub Releases:

Releases -> latest release -> Project.Folder.Checker.exe

Then:

1. Double-click the app.
2. Click **Choose Folder to Scan**.
3. Select the project folder you want to check.

Note: Windows may warn that the app is from an unknown publisher because it is not code-signed.

## What it checks

The report includes:

- total files and folders
- file types found
- large files
- possible old drafts
- duplicate filenames
- recently changed files
- empty folders
- suggested clean-up actions

## What it does not do

Project Folder Checker is report-only.

It does **not**:

- delete files
- move files
- rename files
- edit files
- reorganise folders
- automatically clean anything

The app gives you information. You decide what to do next.

## Report output

The report is saved beside the app and opens automatically.

Report filename format:

NAME OF FOLDER report.md

Example:

project-folder-checker report.md

## Current version

v0.9

Current behaviour:

- simple Windows app window
- visible app version
- **Choose Folder to Scan** button
- About button
- Website button
- Markdown report output
- automatic report opening
- no command window when run as `.pyw`
- no automatic file changes

## Why it exists

Project folders can get messy quickly.

This tool gives a safe first look before you start cleaning anything. It is useful for checking whether a project folder is:

clean / messy / abandoned / worth fixing / safe to archive

It is designed to be boring, clear, and safe.

## Requirements

If you use the `.exe` from Releases:

- Windows

If you run from source:

- Windows
- Python 3.10 or newer

The app uses only Python standard library modules.

## Run from source

Clone the repo:

    git clone https://github.com/armpitpete/project-folder-checker.git
    cd project-folder-checker

Run:

    python "src\Project Folder Checker.pyw"

Or double-click:

    src/Project Folder Checker.pyw

## Build a one-file Windows app

See:

docs/build-windows.md

## Safety rule

This app reports only.

It should not delete, move, rename, edit, or modify scanned project files automatically.

## Licence

MIT Licence.