#!/usr/bin/env python3
"""
Project Integrity Check
Fixed version - works in all environments
"""

import sys
import os
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()

def log(msg, level="INFO"):
    """Simple logging without color codes"""
    print(f"[{level}] {msg}")

def check_python():
    """Check Python version"""
    version = sys.version_info
    log(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 11:
        log("Python version OK", "OK")
        return True
    else:
        log("Python 3.11+ required", "WARN")
        return False

def check_file(rel_path, desc):
    """Check if file exists"""
    full_path = SCRIPT_DIR / rel_path
    if full_path.exists():
        log(f"{desc}: OK", "OK")
        return True
    else:
        log(f"{desc}: NOT FOUND - {full_path}", "ERROR")
        return False

def main():
    print("=" * 60)
    print("MnMCP Project Integrity Check")
    print("=" * 60)
    print()
    
    checks = []
    
    # Check Python
    print("Checking Python...")
    checks.append(check_python())
    print()
    
    # Check essential files
    print("Checking essential files...")
    checks.append(check_file("start.py", "Start script"))
    checks.append(check_file("config.yaml", "Config file"))
    checks.append(check_file("demo_connection.py", "Demo script"))
    checks.append(check_file("data/mnw_block_mapping_from_go.json", "Block mapping"))
    print()
    
    # Check directories
    print("Checking directories...")
    checks.append(check_file("src", "Source code"))
    checks.append(check_file("tests", "Tests"))
    checks.append(check_file("data", "Data"))
    checks.append(check_file("docs", "Documentation"))
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"Result: {passed}/{total} checks passed")
    
    if passed == total:
        print("Status: ALL CHECKS PASSED")
        print()
        print("You can now run:")
        print("  python demo_connection.py  - See features")
        print("  python start.py            - Start server")
        return 0
    else:
        print("Status: SOME CHECKS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
