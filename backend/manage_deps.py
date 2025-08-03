#!/usr/bin/env python3
"""
Dependency Management Script for NET-EST Backend
Provides easy commands for managing dependencies with pip-tools
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def ensure_venv():
    """Ensure we're in a virtual environment"""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("❌ Please activate the virtual environment first:")
        print("   .\\venv\\Scripts\\activate")
        return False
    return True

def update_dependencies():
    """Update and compile all dependency files"""
    print("🚀 Updating NET-EST Dependencies")
    print("=" * 50)
    
    if not ensure_venv():
        return False
    
    success = True
    
    # Compile production requirements
    success &= run_command(
        "pip-compile requirements.in --upgrade", 
        "Compiling production requirements"
    )
    
    # Compile development requirements
    success &= run_command(
        "pip-compile requirements-dev.in --upgrade", 
        "Compiling development requirements"
    )
    
    if success:
        print("\n✅ All dependencies updated successfully!")
        print("📝 Remember to commit both .in and .txt files to version control")
    else:
        print("\n❌ Some dependency updates failed")
    
    return success

def install_dependencies():
    """Install dependencies from compiled files"""
    print("📦 Installing NET-EST Dependencies")
    print("=" * 50)
    
    if not ensure_venv():
        return False
    
    success = True
    
    # Install production dependencies
    success &= run_command(
        "pip install -r requirements.txt", 
        "Installing production dependencies"
    )
    
    # Install development dependencies
    success &= run_command(
        "pip install -r requirements-dev.txt", 
        "Installing development dependencies"
    )
    
    if success:
        print("\n✅ All dependencies installed successfully!")
    else:
        print("\n❌ Some dependency installations failed")
    
    return success

def check_outdated():
    """Check for outdated packages"""
    print("🔍 Checking for outdated packages")
    print("=" * 50)
    
    if not ensure_venv():
        return False
    
    return run_command("pip list --outdated", "Checking outdated packages")

def show_help():
    """Show help information"""
    print("NET-EST Dependency Management")
    print("=" * 30)
    print("Usage: python manage_deps.py [command]")
    print()
    print("Commands:")
    print("  update    - Update and compile all dependency files")
    print("  install   - Install dependencies from compiled files")
    print("  outdated  - Check for outdated packages")
    print("  help      - Show this help message")
    print()
    print("Files:")
    print("  requirements.in      - Production dependencies (edit this)")
    print("  requirements.txt     - Compiled production dependencies (auto-generated)")
    print("  requirements-dev.in  - Development dependencies (edit this)")
    print("  requirements-dev.txt - Compiled development dependencies (auto-generated)")

def main():
    """Main function"""
    os.chdir(Path(__file__).parent)
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "update":
        update_dependencies()
    elif command == "install":
        install_dependencies()
    elif command == "outdated":
        check_outdated()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
