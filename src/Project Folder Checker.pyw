from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox

LARGE_FILE_MB = 25

IGNORE_FOLDERS = {
    ".git",
    "node_modules",
    ".astro",
    "dist",
    "build",
    "__pycache__",
    ".venv",
    "venv",
}

OLD_DRAFT_WORDS = [
    "old",
    "backup",
    "copy",
    "draft",
    "final-final",
    "final2",
    "test",
    "temp",
    "archive",
]


def app_folder() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def safe_filename(text: str) -> str:
    invalid_chars = r'<>:"/\\|?*'
    cleaned = "".join("_" if char in invalid_chars else char for char in text)
    return cleaned.strip().rstrip(".")


def should_ignore(path: Path) -> bool:
    return any(part in IGNORE_FOLDERS for part in path.parts)


def file_size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def scan_folder(folder: Path) -> str:
    files = []
    folders = []
    empty_folders = []

    for path in folder.rglob("*"):
        if should_ignore(path):
            continue

        try:
            if path.is_file():
                files.append(path)

            elif path.is_dir():
                folders.append(path)
                if not any(path.iterdir()):
                    empty_folders.append(path)

        except PermissionError:
            continue

    file_types = Counter(
        file.suffix.lower() if file.suffix else "[no extension]"
        for file in files
    )

    large_files = [
        file for file in files
        if file_size_mb(file) >= LARGE_FILE_MB
    ]

    possible_old_drafts = [
        file for file in files
        if any(word in file.name.lower() for word in OLD_DRAFT_WORDS)
    ]

    duplicate_names = defaultdict(list)
    for file in files:
        duplicate_names[file.name.lower()].append(file)

    duplicate_name_groups = {
        name: paths
        for name, paths in duplicate_names.items()
        if len(paths) > 1
    }

    recent_files = sorted(
        files,
        key=lambda file: file.stat().st_mtime,
        reverse=True
    )[:20]

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    report = []
    report.append("# Project Folder Report")
    report.append("")
    report.append(f"Generated: {now}")
    report.append(f"Folder scanned: `{folder}`")
    report.append("")

    report.append("## Summary")
    report.append("")
    report.append(f"- Files found: **{len(files)}**")
    report.append(f"- Folders found: **{len(folders)}**")
    report.append(f"- Empty folders found: **{len(empty_folders)}**")
    report.append(f"- Large files over {LARGE_FILE_MB} MB: **{len(large_files)}**")
    report.append(f"- Possible old drafts: **{len(possible_old_drafts)}**")
    report.append(f"- Duplicate filenames: **{len(duplicate_name_groups)}**")
    report.append("")

    report.append("## File types")
    report.append("")
    if file_types:
        for ext, count in file_types.most_common():
            report.append(f"- `{ext}`: {count}")
    else:
        report.append("- No files found.")
    report.append("")

    report.append("## Large files")
    report.append("")
    if large_files:
        for file in sorted(large_files, key=file_size_mb, reverse=True):
            size = file_size_mb(file)
            report.append(f"- `{file.relative_to(folder)}` — {size:.1f} MB")
    else:
        report.append("- No large files found.")
    report.append("")

    report.append("## Possible old drafts")
    report.append("")
    if possible_old_drafts:
        for file in possible_old_drafts[:100]:
            report.append(f"- `{file.relative_to(folder)}`")
    else:
        report.append("- No obvious old drafts found.")
    report.append("")

    report.append("## Duplicate filenames")
    report.append("")
    if duplicate_name_groups:
        for name, paths in duplicate_name_groups.items():
            report.append(f"### `{name}`")
            for path in paths:
                report.append(f"- `{path.relative_to(folder)}`")
            report.append("")
    else:
        report.append("- No duplicate filenames found.")
    report.append("")

    report.append("## Recently changed files")
    report.append("")
    if recent_files:
        for file in recent_files:
            changed = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            report.append(f"- `{file.relative_to(folder)}` — {changed}")
    else:
        report.append("- No recent files found.")
    report.append("")

    report.append("## Empty folders")
    report.append("")
    if empty_folders:
        for folder_path in empty_folders[:100]:
            report.append(f"- `{folder_path.relative_to(folder)}`")
    else:
        report.append("- No empty folders found.")
    report.append("")

    report.append("## Suggested next clean-up actions")
    report.append("")
    report.append("1. Check the possible old drafts.")
    report.append("2. Check duplicate filenames before deleting anything.")
    report.append("3. Compress or move very large files if they are not needed for the active project.")
    report.append("4. Add or update a `README.md` if this folder does not explain itself.")
    report.append("5. Move uncertain files to a holding folder instead of deleting them.")
    report.append("")

    return "\n".join(report)


def run_scan(folder: Path) -> Path:
    report_text = scan_folder(folder)

    report_path = app_folder() / f"{safe_filename(folder.name)} report.md"
    report_path.write_text(report_text, encoding="utf-8")

    os.startfile(report_path)

    return report_path


def show_error(message: str):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Project Folder Checker", message)
    root.destroy()


def main():
    # Drag-folder-onto-app mode.
    if len(sys.argv) > 1:
        dropped_path = Path(sys.argv[1]).resolve()

        if not dropped_path.exists():
            show_error(f"This folder could not be found:\n{dropped_path}")
            return

        if not dropped_path.is_dir():
            show_error("Drop a folder onto the app, not a file.")
            return

        try:
            run_scan(dropped_path)
        except Exception as error:
            show_error(f"Something went wrong:\n{error}")

        return

    # Normal app-window mode.
    root = tk.Tk()
    root.title("Project Folder Checker")
    root.geometry("520x300")
    root.resizable(False, False)

    title = tk.Label(
        root,
        text="Project Folder Checker",
        font=("Segoe UI", 18, "bold")
    )
    title.pack(pady=(28, 8))

    subtitle = tk.Label(
        root,
        text="Choose a project folder. The app will scan it and open a Markdown report.",
        font=("Segoe UI", 10),
        wraplength=420,
        justify="center"
    )
    subtitle.pack(pady=(0, 24))

    status = tk.Label(
        root,
        text="No folder scanned yet.",
        font=("Segoe UI", 9),
        wraplength=420,
        justify="center"
    )
    status.pack(pady=(0, 18))

    def choose_and_scan():
        selected = filedialog.askdirectory(title="Choose a project folder to scan")

        if not selected:
            return

        folder = Path(selected)

        try:
            report_path = run_scan(folder)
            status.config(text=f"Report created and opened:\n{report_path.name}")

        except Exception as error:
            messagebox.showerror(
                "Project Folder Checker",
                f"Something went wrong:\n{error}"
            )

    choose_button = tk.Button(
        root,
        text="Choose Folder to Scan",
        font=("Segoe UI", 11, "bold"),
        width=24,
        height=2,
        command=choose_and_scan
    )
    choose_button.pack()

    note = tk.Label(
        root,
        text="You can also drag a folder onto this app file.",
        font=("Segoe UI", 9),
    )
    note.pack(pady=(24, 0))

    root.mainloop()


if __name__ == "__main__":
    main()
