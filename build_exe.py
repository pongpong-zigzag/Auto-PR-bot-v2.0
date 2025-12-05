"""
Build script to create Windows executable using PyInstaller.
Run: python build_exe.py
"""

import subprocess
import sys
import os
import shutil

def build_executable():
    """Build the executable using PyInstaller."""
    
    print("="*60)
    print("Auto PR Bot Studio - Executable Builder")
    print("="*60)
    
    # Check if PyInstaller is installed
    try:
        result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("[OK] PyInstaller found (version: " + result.stdout.strip() + ")")
        else:
            raise FileNotFoundError
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[OK] PyInstaller installed")
    
    # Clean previous builds
    if os.path.exists("build"):
        print("\nCleaning previous build directory...")
        shutil.rmtree("build")
    
    if os.path.exists("dist"):
        print("Cleaning previous dist directory...")
        shutil.rmtree("dist")
    
    print("\n" + "="*60)
    print("Building executable...")
    print("="*60 + "\n")
    
    # Build using the spec file
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "Auto-PR-Bot-Studio.spec",
        "--clean",
        "--noconfirm"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        
        exe_path = os.path.join("dist", "Auto-PR-Bot-Studio.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024*1024)
            
            print("\n" + "="*60)
            print("[SUCCESS] Build completed successfully!")
            print("="*60)
            print(f"\nExecutable location: {exe_path}")
            print(f"File size: {file_size:.2f} MB")
            print("\nYou can now distribute this .exe file!")
            print("="*60)
        else:
            print("\n[ERROR] Executable file not found in dist folder")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Error during build: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that PyInstaller is working: python -m PyInstaller --version")
        sys.exit(1)
    except FileNotFoundError:
        print("\n[ERROR] PyInstaller not found. Please install it:")
        print("   pip install pyinstaller")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()
