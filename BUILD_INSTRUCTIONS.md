# Building the Executable (.exe) File

This guide will help you create a Windows executable file for Auto PR Bot Studio.

## Prerequisites

1. Python 3.8 or higher installed
2. All project dependencies installed

## Quick Build

### Option 1: Using the build script (Recommended)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the build script:
   ```bash
   python build_exe.py
   ```

3. Find your executable:
   - Location: `dist/Auto-PR-Bot-Studio.exe`
   - The .exe file is ready to distribute!

### Option 2: Using PyInstaller directly

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build using the spec file:
   ```bash
   pyinstaller Auto-PR-Bot-Studio.spec --clean --noconfirm
   ```

3. Or build with command line:
   ```bash
   pyinstaller --name=Auto-PR-Bot-Studio --onefile --windowed --add-data="autopr_bot;autopr_bot" ui.py
   ```

## Output

After building, you'll find:
- `dist/Auto-PR-Bot-Studio.exe` - The executable file (ready to distribute)
- `build/` - Temporary build files (can be deleted)
- `Auto-PR-Bot-Studio.spec` - PyInstaller specification file

## Notes

- The executable is a standalone file that includes all dependencies
- No need to install Python on the target machine
- File size will be approximately 15-30 MB
- First launch may take a few seconds to extract and start

## Troubleshooting

If you encounter issues:

1. **Missing modules error**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Build fails**: Try cleaning and rebuilding
   ```bash
   rmdir /s build dist
   python build_exe.py
   ```

3. **Import errors**: Check that all Python files are in the correct directories

## Distribution

You can distribute the `dist/Auto-PR-Bot-Studio.exe` file directly to users. They don't need Python installed to run it.

