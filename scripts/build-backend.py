#!/usr/bin/env python3
"""
Build script to create standalone Python backend executable using PyInstaller
"""

import subprocess
import sys
import shutil
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"   Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} failed:")
        print(f"      Error: {e.stderr}")
        return False

def install_build_dependencies():
    """Install PyInstaller and other build dependencies"""
    dependencies = [
        "pyinstaller>=6.0.0",
        "setuptools>=68.0.0",
        "wheel>=0.40.0"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    return True

def create_pyinstaller_spec():
    """Create PyInstaller spec file with proper configuration"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['python/server.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('python/parsers/*.py', 'parsers'),
        ('python/models/*.py', 'models'),
        ('python/utils/*.py', 'utils'),
    ],
    hiddenimports=[
        'uvicorn.loops.auto',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.http.auto',
        'uvicorn.lifespan.on',
        'asammdf',
        'can',
        'numpy',
        'pandas',
        'fastapi',
        'pydantic',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='automotive-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('automotive-backend.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ PyInstaller spec file created")
    return True

def build_executable():
    """Build the standalone executable"""
    return run_command(
        "pyinstaller --clean automotive-backend.spec",
        "Building standalone executable"
    )

def create_distribution_package():
    """Create distribution package with executable and metadata"""
    dist_dir = Path("dist/automotive-backend-package")
    
    # Clean and create distribution directory
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True)
    
    # Copy executable
    exe_name = "automotive-backend.exe" if os.name == 'nt' else "automotive-backend"
    exe_source = Path("dist") / exe_name
    exe_dest = dist_dir / exe_name
    
    if exe_source.exists():
        shutil.copy2(exe_source, exe_dest)
        print(f"✅ Copied executable to {exe_dest}")
    else:
        print(f"❌ Executable not found: {exe_source}")
        return False
    
    # Create version info
    version_info = f"""
Automotive Analysis Backend
Version: 0.1.0
Platform: {sys.platform}
Python: {sys.version}
Built with PyInstaller
"""
    
    with open(dist_dir / "VERSION.txt", "w") as f:
        f.write(version_info)
    
    # Create startup script
    if os.name == 'nt':
        startup_script = f"""@echo off
echo Starting Automotive Analysis Backend...
"{exe_name}" --port 8000
pause
"""
        with open(dist_dir / "start-backend.bat", "w") as f:
            f.write(startup_script)
    else:
        startup_script = f"""#!/bin/bash
echo "Starting Automotive Analysis Backend..."
./{exe_name} --port 8000
"""
        startup_file = dist_dir / "start-backend.sh"
        with open(startup_file, "w") as f:
            f.write(startup_script)
        startup_file.chmod(0o755)
    
    print(f"✅ Distribution package created in {dist_dir}")
    return True

def main():
    """Main build function"""
    print("🏗️  Building Automotive Analysis Backend Executable")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required for building")
        return 1
    
    # Install build dependencies
    if not install_build_dependencies():
        print("❌ Failed to install build dependencies")
        return 1
    
    # Create PyInstaller spec
    if not create_pyinstaller_spec():
        print("❌ Failed to create PyInstaller spec")
        return 1
    
    # Build executable
    if not build_executable():
        print("❌ Failed to build executable")
        return 1
    
    # Create distribution package
    if not create_distribution_package():
        print("❌ Failed to create distribution package")
        return 1
    
    print("\n🎉 Build completed successfully!")
    print("\n📦 Distribution packages:")
    print("   - dist/automotive-backend-package/")
    print("   - Contains standalone executable and startup scripts")
    print("   - No Python installation required on target machines")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 