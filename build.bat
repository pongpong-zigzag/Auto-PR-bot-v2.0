@echo off
echo ========================================
echo Auto PR Bot Studio - Building Executable
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Installing/updating dependencies...
python -m pip install -r requirements.txt

echo.
echo Building executable...
python build_exe.py

echo.
echo ========================================
if exist "dist\Auto-PR-Bot-Studio.exe" (
    echo BUILD SUCCESSFUL!
    echo.
    echo Executable location: dist\Auto-PR-Bot-Studio.exe
) else (
    echo BUILD FAILED!
    echo Please check the error messages above.
)
echo ========================================
pause

