#!/usr/bin/env python3
"""
Setup script for Automotive Measurement Analysis VS Code Extension
"""

import subprocess
import sys
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

def check_prerequisites():
    """Check if prerequisites are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 11):
        print("❌ Python 3.11+ is required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check Node.js
    try:
        result = subprocess.run("node --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except:
        print("❌ Node.js not found")
        return False
    
    # Check npm
    try:
        result = subprocess.run("npm --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except:
        print("❌ npm not found")
        return False
    
    return True

def install_python_dependencies():
    """Install Python dependencies with Python 3.12 compatibility"""
    print("\n🐍 Installing Python dependencies...")
    
    python_dir = Path("python")
    if not python_dir.exists():
        print("❌ Python directory not found")
        return False
    
    # Check Python version to determine which requirements file to use
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 12:
        print("⚠️  Python 3.12 detected - using compatibility mode")
        
        # First install core dependencies
        core_requirements = python_dir / "requirements-py312.txt"
        if core_requirements.exists():
            if not run_command(f"pip install -r {core_requirements}", "Installing core Python dependencies"):
                return False
        
        # Try to install asammdf and python-can separately
        print("\n🔧 Installing automotive-specific packages...")
        
        # Try asammdf with --no-deps first
        if not run_command("pip install asammdf==8.2.9 --no-deps", "Installing asammdf (no deps)"):
            print("⚠️  asammdf installation failed - will use fallback mode")
        
        # Try python-can
        if not run_command("pip install python-can==4.5.0", "Installing python-can"):
            print("⚠️  python-can installation failed - will use fallback mode")
        
        # Install any missing dependencies manually
        manual_packages = [
            "numpy>=1.26.0",
            "pandas>=2.1.0",
            "scipy>=1.11.0",
            "matplotlib>=3.7.0"
        ]
        
        for package in manual_packages:
            if not run_command(f"pip install {package}", f"Installing {package}"):
                print(f"⚠️  Failed to install {package}")
        
        return True
    else:
        # Use standard requirements for Python 3.11
        requirements_file = python_dir / "requirements.txt"
        if not requirements_file.exists():
            print("❌ requirements.txt not found")
            return False
        
        return run_command(f"pip install -r {requirements_file}", "Installing Python dependencies")

def install_node_dependencies():
    """Install Node.js dependencies"""
    print("\n📦 Installing Node.js dependencies...")
    
    if not Path("package.json").exists():
        print("❌ package.json not found")
        return False
    
    return run_command("npm install", "Installing Node.js dependencies")

def compile_extension():
    """Compile the TypeScript extension"""
    print("\n🔨 Compiling TypeScript extension...")
    
    return run_command("npm run compile", "Compiling TypeScript extension")

def run_python_tests():
    """Run Python backend tests"""
    print("\n🧪 Running Python backend tests...")
    
    python_dir = Path("python")
    test_file = python_dir / "test_basic.py"
    
    if not test_file.exists():
        print("❌ Python test file not found")
        return False
    
    return run_command(f"python {test_file}", "Running Python backend tests")

def main():
    """Main setup function"""
    print("🚀 Setting up Automotive Measurement Analysis VS Code Extension")
    print("=" * 70)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install the required software.")
        return 1
    
    # Install dependencies
    if not install_python_dependencies():
        print("\n❌ Python dependency installation failed.")
        return 1
    
    if not install_node_dependencies():
        print("\n❌ Node.js dependency installation failed.")
        return 1
    
    # Compile extension
    if not compile_extension():
        print("\n❌ Extension compilation failed.")
        return 1
    
    # Run tests
    if not run_python_tests():
        print("\n❌ Python tests failed.")
        return 1
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Open VS Code")
    print("   2. Press Ctrl+Shift+P (or Cmd+Shift+P on Mac)")
    print("   3. Run 'Extensions: Install from VSIX...'")
    print("   4. Select the compiled extension")
    print("   5. Open a measurement file (.mdf, .mf4, .blf, .asc)")
    print("   6. Use 'Start Python Backend' command")
    print("   7. Right-click on a measurement file and select 'Open in Analysis View'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 