#!/usr/bin/env python3
"""
Build script for creating Windows EXE from desktop app.
Run this to create the standalone executable.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install PyInstaller")
            return False

def build_exe():
    """Build the EXE using PyInstaller."""
    project_root = Path(__file__).parent.parent
    desktop_dir = Path(__file__).parent
    spec_file = desktop_dir / "pyinstaller.spec"
    
    print(f"Building EXE from {spec_file}")
    print(f"Project root: {project_root}")
    
    # Change to project root for building
    os.chdir(project_root)
    
    try:
        # Build with PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            exe_path = project_root / "dist" / "RealFlipBatchAnalyzer_v2.exe"
            if exe_path.exists():
                print(f"✓ EXE built successfully: {exe_path}")
                print(f"  Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
                return exe_path
            else:
                print("✗ EXE file not found after build")
                return None
        else:
            print("✗ Build failed:")
            print(result.stderr)
            return None
            
    except Exception as e:
        print(f"✗ Build error: {e}")
        return None

def main():
    """Main build process."""
    print("RealFlip Desktop Batch Analyzer - EXE Builder")
    print("=" * 50)
    
    if not check_dependencies():
        return 1
    
    exe_path = build_exe()
    if exe_path:
        print("\n✓ Build completed successfully!")
        print(f"  Executable: {exe_path}")
        print(f"\nTo test:")
        print(f"  1. Double-click {exe_path}")
        print(f"  2. Or run from command line: {exe_path} --help")
        return 0
    else:
        print("\n✗ Build failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
