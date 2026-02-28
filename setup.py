#!/usr/bin/env python3
"""
MnMCP Setup and Deployment Script
Unified setup, dependency installation, and launch tool
"""

import sys
import os
import subprocess
import importlib
import argparse
import json
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

# Configuration
REQUIRED_DEPS = {
    "websockets": "websockets>=12.0",
    "yaml": "pyyaml>=6.0",
}

OPTIONAL_DEPS = {
    "cryptography": "cryptography>=41.0.0",
    "rich": "rich>=13.0.0",
}

PYTHON_MIN_VERSION = (3, 11)

def print_status(message, status="info"):
    """Print colored status message"""
    colors = {
        "ok": "\033[92m",
        "warn": "\033[93m",
        "error": "\033[91m",
        "info": "\033[94m",
        "reset": "\033[0m"
    }
    color = colors.get(status, colors["info"])
    print(f"{color}[{status.upper()}]{colors['reset']} {message}")

def check_python_version():
    """Check if Python version is sufficient"""
    version = sys.version_info
    if version.major < PYTHON_MIN_VERSION[0] or \
       (version.major == PYTHON_MIN_VERSION[0] and version.minor < PYTHON_MIN_VERSION[1]):
        print_status(f"Python {version.major}.{version.minor} is too old. Need {PYTHON_MIN_VERSION[0]}.{PYTHON_MIN_VERSION[1]}+", "error")
        return False
    print_status(f"Python {version.major}.{version.minor}.{version.micro} OK", "ok")
    return True

def check_pip():
    """Check if pip is available"""
    try:
        # First try 'pip' command
        result = subprocess.run(["pip", "--version"], 
                      capture_output=True)
        if result.returncode == 0:
            print_status("pip is available", "ok")
            return True
    except FileNotFoundError:
        pass
    
    # Then try 'python -m pip'
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True)
        if result.returncode == 0:
            print_status("pip is available (via python -m pip)", "ok")
            return True
    except Exception:
        pass
    
    print_status("pip not found. Please install pip.", "error")
    print_status("Download get-pip.py from https://bootstrap.pypa.io/get-pip.py", "info")
    return False

def install_dependency(package_name, package_spec):
    """Install a single dependency"""
    print_status(f"Installing {package_name}...", "info")
    
    # Try Tsinghua mirror first (for China users)
    mirrors = [
        "https://pypi.tuna.tsinghua.edu.cn/simple",
        "https://pypi.org/simple",
    ]
    
    for mirror in mirrors:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_spec, 
                 "-i", mirror, "--quiet"],
                capture_output=True,
                timeout=60
            )
            if result.returncode == 0:
                print_status(f"{package_name} installed successfully", "ok")
                return True
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue
    
    # Try without mirror as last resort
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_spec, "--quiet"],
            capture_output=True,
            timeout=120
        )
        if result.returncode == 0:
            print_status(f"{package_name} installed successfully", "ok")
            return True
    except Exception as e:
        print_status(f"Failed to install {package_name}: {e}", "error")
    
    return False

def check_and_install_dependencies(auto_install=True):
    """Check and install all dependencies"""
    print_status("Checking dependencies...", "info")
    
    missing_required = []
    missing_optional = []
    
    # Check required dependencies
    for module_name, package_spec in REQUIRED_DEPS.items():
        try:
            importlib.import_module(module_name)
            print_status(f"{module_name}: OK", "ok")
        except ImportError:
            print_status(f"{module_name}: NOT FOUND", "warn")
            missing_required.append((module_name, package_spec))
    
    # Check optional dependencies
    for module_name, package_spec in OPTIONAL_DEPS.items():
        try:
            importlib.import_module(module_name)
            print_status(f"{module_name}: OK (optional)", "ok")
        except ImportError:
            print_status(f"{module_name}: NOT FOUND (optional)", "warn")
            missing_optional.append((module_name, package_spec))
    
    # Install missing dependencies
    if auto_install:
        if missing_required:
            print_status(f"Installing {len(missing_required)} required dependencies...", "info")
            for module_name, package_spec in missing_required:
                if not install_dependency(module_name, package_spec):
                    print_status(f"Failed to install required dependency: {module_name}", "error")
                    return False
        
        if missing_optional:
            print_status(f"Installing {len(missing_optional)} optional dependencies...", "info")
            for module_name, package_spec in missing_optional:
                install_dependency(module_name, package_spec)  # Don't fail on optional
    
    return len(missing_required) == 0 or auto_install

def check_project_files():
    """Check if all required project files exist"""
    print_status("Checking project files...", "info")
    
    required_files = [
        ("config.yaml", "Configuration file"),
        ("start.py", "Main startup script"),
        ("data/mnw_block_mapping_from_go.json", "Block mapping data"),
        ("src/core/proxy_server_v2.py", "Proxy server"),
        ("src/protocol/block_mapper.py", "Block mapper"),
    ]
    
    all_ok = True
    for filepath, description in required_files:
        if Path(filepath).exists():
            print_status(f"{description}: OK", "ok")
        else:
            print_status(f"{description}: MISSING ({filepath})", "error")
            all_ok = False
    
    return all_ok

def run_tests():
    """Run project tests"""
    print_status("Running tests...", "info")
    
    test_files = [
        ("tests/test_crypto.py", "Crypto tests"),
        ("tests/test_block_mapper.py", "Block mapper tests"),
        ("tests/test_protocol.py", "Protocol tests"),
    ]
    
    all_passed = True
    for test_file, description in test_files:
        if not Path(test_file).exists():
            print_status(f"{description}: FILE NOT FOUND", "warn")
            continue
        
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0:
                print_status(f"{description}: PASSED", "ok")
            else:
                print_status(f"{description}: FAILED", "warn")
                all_passed = False
        except Exception as e:
            print_status(f"{description}: ERROR - {e}", "warn")
            all_passed = False
    
    return all_passed

def start_server(config_file="config.yaml"):
    """Start the proxy server"""
    print_status("Starting MnMCP Proxy Server...", "info")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from utils.config_loader import Config
        from core.proxy_server_v2 import create_proxy, ProxyConfig
        
        config = Config.from_yaml(config_file)
        proxy_config = config.to_proxy_config()
        
        if not proxy_config:
            print_status("Using default configuration", "warn")
            proxy_config = ProxyConfig()
        
        print()
        print("=" * 50)
        print("Server Configuration:")
        print(f"  MNW Listen: {proxy_config.mnw_host}:{proxy_config.mnw_port}")
        print(f"  MC Target:  {proxy_config.mc_host}:{proxy_config.mc_port}")
        print(f"  Max Clients: {proxy_config.max_clients}")
        print("=" * 50)
        print()
        
        async def run():
            proxy = await create_proxy(proxy_config)
            await proxy.start()
        
        import asyncio
        asyncio.run(run())
        
    except KeyboardInterrupt:
        print_status("\nServer stopped by user", "info")
    except Exception as e:
        print_status(f"Server error: {e}", "error")
        import traceback
        traceback.print_exc()

def show_menu():
    """Show interactive menu"""
    print()
    print("=" * 50)
    print("MnMCP Setup and Launch Tool")
    print("=" * 50)
    print()
    print("[1] Full Setup (Check + Install + Test)")
    print("[2] Quick Start Server")
    print("[3] Run Demo")
    print("[4] Run Tests Only")
    print("[5] Check System Only")
    print("[6] Exit")
    print()
    
    choice = input("Select option (1-6): ").strip()
    return choice

def check_and_install_python():
    """Check Python and offer to install if needed"""
    if check_python_version():
        return True
    
    print_status("Python not found or version too old", "warn")
    print()
    
    # Check if install_python.py exists
    if Path("install_python.py").exists():
        response = input("Run Python auto-installer? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            print_status("Running Python installer...", "info")
            result = subprocess.run([sys.executable, "install_python.py"])
            if result.returncode == 0:
                print_status("Python installed! Please restart terminal and run setup again.", "ok")
                return False  # Need restart
            else:
                print_status("Auto-install failed", "error")
    
    print()
    print("Please install Python manually:")
    print("  1. Download from https://python.org/downloads")
    print("  2. Install Python 3.11 or higher")
    print("  3. Check 'Add Python to PATH' during installation")
    print()
    return False

def main():
    parser = argparse.ArgumentParser(description="MnMCP Setup Tool")
    parser.add_argument("--setup", action="store_true", help="Run full setup")
    parser.add_argument("--check", action="store_true", help="Check system only")
    parser.add_argument("--test", action="store_true", help="Run tests only")
    parser.add_argument("--start", action="store_true", help="Start server directly")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    
    args = parser.parse_args()
    
    # If no args, show menu
    if not any([args.setup, args.check, args.test, args.start, args.demo]):
        choice = show_menu()
        
        if choice == "1":
            args.setup = True
        elif choice == "2":
            args.start = True
        elif choice == "3":
            args.demo = True
        elif choice == "4":
            args.test = True
        elif choice == "5":
            args.check = True
        else:
            print_status("Goodbye!", "info")
            return 0
    
    print()
    print("=" * 50)
    print("MnMCP - Minecraft & MiniWorld Cross-Platform")
    print("=" * 50)
    print()
    
    # Check Python version first, offer to install
    if not check_and_install_python():
        return 1
    
    # Check pip
    if not check_pip():
        print_status("pip not available. Please install pip.", "error")
        return 1
    
    # Continue with setup...
    
    # Check pip
    if not check_pip():
        return 1
    
    # Handle different modes
    if args.check:
        print_status("Running system check only...", "info")
        check_and_install_dependencies(auto_install=False)
        check_project_files()
        return 0
    
    if args.test:
        print_status("Running tests only...", "info")
        run_tests()
        return 0
    
    if args.demo:
        print_status("Running demo...", "info")
        try:
            subprocess.run([sys.executable, "demo_connection.py"])
        except Exception as e:
            print_status(f"Demo error: {e}", "error")
        return 0
    
    if args.setup:
        print_status("Running full setup...", "info")
        
        # Install dependencies
        if not check_and_install_dependencies(auto_install=True):
            print_status("Setup failed: Could not install dependencies", "error")
            print_status("Please manually run: pip install websockets pyyaml", "info")
            return 1
        
        # Check project files
        if not check_project_files():
            print_status("Setup failed: Missing project files", "error")
            return 1
        
        # Run tests
        run_tests()
        
        print()
        print_status("Setup completed successfully!", "ok")
        print()
        
        # Ask to start server
        response = input("Start server now? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            args.start = True
        else:
            return 0
    
    if args.start:
        start_server(args.config)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
