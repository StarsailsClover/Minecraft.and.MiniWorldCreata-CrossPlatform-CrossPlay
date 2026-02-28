#!/usr/bin/env python3
"""
Deployment Verification Script
Checks if deployment is correct
"""

import sys
import os
from pathlib import Path

def check_file(path, description):
    """Check if file exists"""
    if Path(path).exists():
        print(f"  [OK] {description}: {path}")
        return True
    else:
        print(f"  [FAIL] {description}: {path} not found")
        return False

def main():
    print("=" * 50)
    print("MnMCP Deployment Verification")
    print("=" * 50)
    print()
    
    checks = []
    
    # Check batch files
    print("Checking batch files...")
    checks.append(check_file("START_HERE.bat", "Start Here"))
    checks.append(check_file("QUICK_START.bat", "Quick Start"))
    checks.append(check_file("DEPLOY_AND_START.bat", "Deploy and Start"))
    checks.append(check_file("start.bat", "Simple Start"))
    
    # Check Python files
    print("\nChecking Python files...")
    checks.append(check_file("start.py", "Main Start Script"))
    checks.append(check_file("demo_connection.py", "Demo Script"))
    checks.append(check_file("check_project_integrity.py", "Integrity Check"))
    
    # Check directories
    print("\nChecking directories...")
    checks.append(check_file("src", "Source Code"))
    checks.append(check_file("tests", "Tests"))
    checks.append(check_file("data", "Data Files"))
    checks.append(check_file("docs", "Documentation"))
    
    # Check config
    print("\nChecking configuration...")
    checks.append(check_file("config.yaml", "Config File"))
    checks.append(check_file("data/mnw_block_mapping_from_go.json", "Block Mapping"))
    
    # Check docs
    print("\nChecking documentation...")
    checks.append(check_file("README.txt", "Readme"))
    checks.append(check_file("docs/USER_GUIDE.md", "User Guide"))
    
    print()
    print("=" * 50)
    passed = sum(checks)
    total = len(checks)
    print(f"Result: {passed}/{total} checks passed")
    
    if passed == total:
        print("Status: [OK] Deployment verified!")
        print()
        print("Next steps:")
        print("  1. Double click START_HERE.bat")
        print("  2. Select Quick Start")
        print("  3. Follow instructions")
        return 0
    else:
        print("Status: [FAIL] Some files missing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
