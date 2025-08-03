#!/usr/bin/env python3
"""
NET-EST Backend Code Quality Management Script

This script provides commands for maintaining code quality:
- Linting with ruff and mypy
- Code formatting with black and ruff
- Running tests with coverage
- Full quality check pipeline

Usage:
    python code_quality.py [command]

Commands:
    lint      - Run linting checks (ruff + mypy)
    format    - Format code (black + ruff format)
    test      - Run tests with coverage
    check     - Full quality check (lint + test)
    fix       - Auto-fix linting issues where possible
    help      - Show this help message
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_section(title: str) -> None:
    """Print a section header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 50}")
    print(f"🔧 {title}")
    print(f"{'=' * 50}{Colors.RESET}")

def print_success(message: str) -> None:
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str) -> None:
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.RESET}")

def run_command(cmd: List[str], description: str) -> bool:
    """Run a command and return True if successful"""
    try:
        print(f"🔄 {description}...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print_success(f"{description} completed successfully")
            if result.stdout.strip():
                print(result.stdout)
            return True
        else:
            print_error(f"{description} failed")
            if result.stderr.strip():
                print(result.stderr)
            if result.stdout.strip():
                print(result.stdout)
            return False
    except FileNotFoundError:
        print_error(f"Command not found: {' '.join(cmd)}")
        print_warning("Make sure all development dependencies are installed: python manage_deps.py install")
        return False
    except Exception as e:
        print_error(f"Error running {description}: {str(e)}")
        return False

def check_dependencies() -> bool:
    """Check if required tools are available"""
    tools = ['ruff', 'black', 'mypy', 'pytest']
    missing = []
    
    for tool in tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            missing.append(tool)
    
    if missing:
        print_error(f"Missing tools: {', '.join(missing)}")
        print_warning("Install development dependencies: python manage_deps.py install")
        return False
    
    return True

def lint_code() -> bool:
    """Run linting checks"""
    print_section("Running Linting Checks")
    
    success = True
    
    # Run ruff linting
    success &= run_command(
        ['ruff', 'check', 'src/', 'tests/'],
        "Ruff linting check"
    )
    
    # Run mypy type checking
    success &= run_command(
        ['mypy', 'src/'],
        "MyPy type checking"
    )
    
    return success

def format_code() -> bool:
    """Format code"""
    print_section("Formatting Code")
    
    success = True
    
    # Run black formatter
    success &= run_command(
        ['black', 'src/', 'tests/'] + (['--check'] if '--check' in sys.argv else []),
        "Black code formatting" + (" (check only)" if '--check' in sys.argv else "")
    )
    
    # Run ruff formatter
    success &= run_command(
        ['ruff', 'format', 'src/', 'tests/'] + (['--check'] if '--check' in sys.argv else []),
        "Ruff code formatting" + (" (check only)" if '--check' in sys.argv else "")
    )
    
    # Run isort
    success &= run_command(
        ['ruff', 'check', '--select', 'I', '--fix', 'src/', 'tests/'],
        "Import sorting with ruff"
    )
    
    return success

def run_tests() -> bool:
    """Run tests with coverage"""
    print_section("Running Tests")
    
    return run_command(
        ['pytest', '--cov=src', '--cov-report=term-missing', '--cov-report=html:htmlcov'],
        "Running tests with coverage"
    )

def fix_issues() -> bool:
    """Auto-fix linting issues where possible"""
    print_section("Auto-fixing Issues")
    
    success = True
    
    # Fix ruff issues
    success &= run_command(
        ['ruff', 'check', '--fix', 'src/', 'tests/'],
        "Auto-fixing ruff issues"
    )
    
    # Format code
    success &= format_code()
    
    return success

def full_check() -> bool:
    """Run full quality check"""
    print_section("Full Quality Check")
    
    success = True
    
    # Format check
    print("🔍 Checking code formatting...")
    sys.argv.append('--check')  # Add check flag for formatting
    success &= format_code()
    sys.argv.remove('--check')  # Remove check flag
    
    # Linting
    success &= lint_code()
    
    # Tests
    success &= run_tests()
    
    if success:
        print_success("All quality checks passed! 🎉")
    else:
        print_error("Some quality checks failed. Run 'python code_quality.py fix' to auto-fix issues.")
    
    return success

def show_help() -> None:
    """Show help message"""
    print(__doc__)

def main() -> None:
    """Main entry point"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    # Check if we're in the right directory
    if not Path('src').exists():
        print_error("This script must be run from the backend directory")
        sys.exit(1)
    
    # Check dependencies for most commands
    if command not in ['help'] and not check_dependencies():
        print_error("Dependencies check failed")
        sys.exit(1)
    
    if command == 'lint':
        success = lint_code()
    elif command == 'format':
        success = format_code()
    elif command == 'test':
        success = run_tests()
    elif command == 'check':
        success = full_check()
    elif command == 'fix':
        success = fix_issues()
    elif command == 'help':
        show_help()
        return
    else:
        print_error(f"Unknown command: {command}")
        show_help()
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
