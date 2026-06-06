# Build a one-file Windows app

These steps build Project Folder Checker into one `.exe` file.

## 1. Install Python

Install Python 3.10 or newer from the official Python website.

During install, tick:

```text
Add Python to PATH
```

## 2. Clone the repo

```powershell
git clone https://github.com/armpitpete/project-folder-checker.git
cd project-folder-checker
```

## 3. Install build tool

```powershell
python -m pip install pyinstaller
```

Or install from this repo's requirements file:

```powershell
python -m pip install -r requirements.txt
```

## 4. Build the app

Without a custom icon:

```powershell
python -m PyInstaller --onefile --windowed --name "Project Folder Checker" "src\Project Folder Checker.pyw"
```

With an icon, put an `.ico` file in `assets/` and run:

```powershell
python -m PyInstaller --onefile --windowed --icon "assets\project_folder_checker_icon.ico" --name "Project Folder Checker" "src\Project Folder Checker.pyw"
```

## 5. Find the app

After the build finishes, open:

```text
dist
```

Inside will be:

```text
Project Folder Checker.exe
```

## 6. Use it

Either:

- double-click the `.exe`, then choose a folder
- drag a folder onto the `.exe`

The app creates a report beside the `.exe` and opens it automatically.

## 7. Clean build files

After testing, these can be deleted:

```text
build/
Project Folder Checker.spec
```

Keep:

```text
dist/Project Folder Checker.exe
```

## Safety note

The app only scans and reports. It should not automatically delete, move, rename, or modify files in the scanned folder.
