#!/usr/bin/env python3
"""
Python Auto-Installer for MnMCP
Downloads and installs Python if not present
"""

import os
import sys
import subprocess
import urllib.request
import tempfile
import platform
from pathlib import Path

PYTHON_VERSION = "3.11.9"
PYTHON_MIN_VERSION = (3, 11)

def print_status(message, status="info"):
    """Print status message"""
    colors = {
        "ok": "\033[92m",
        "warn": "\033[93m",
        "error": "\033[91m",
        "info": "\033[94m",
        "reset": "\033[0m"
    }
    color = colors.get(status, colors["info"])
    reset = colors["reset"]
    print(f"{color}[{status.upper()}]{reset} {message}")

def check_python_installed():
    """Check if Python is installed and version is sufficient"""
    try:
        result = subprocess.run(["python", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_str = result.stdout.strip() or result.stderr.strip()
            print_status(f"Found {version_str}", "ok")
            
            # Parse version
            version_parts = version_str.split()[1].split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1])
            
            if major > PYTHON_MIN_VERSION[0] or \
               (major == PYTHON_MIN_VERSION[0] and minor >= PYTHON_MIN_VERSION[1]):
                print_status("Python version is sufficient", "ok")
                return True
            else:
                print_status(f"Python {major}.{minor} is too old. Need {PYTHON_MIN_VERSION[0]}.{PYTHON_MIN_VERSION[1]}+", "warn")
                return False
    except FileNotFoundError:
        print_status("Python not found in PATH", "warn")
        return False
    except Exception as e:
        print_status(f"Error checking Python: {e}", "error")
        return False

def download_python_windows():
    """Download Python installer for Windows"""
    print_status("Downloading Python for Windows...", "info")
    
    # Python 3.11.9 64-bit installer
    url = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-amd64.exe"
    filename = f"python-{PYTHON_VERSION}-amd64.exe"
    
    try:
        # Create temp directory
        temp_dir = tempfile.gettempdir()
        installer_path = Path(temp_dir) / filename
        
        # Download with progress
        print_status(f"Downloading from {url}", "info")
        print_status("This may take a few minutes...", "info")
        
        def download_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, downloaded * 100 / total_size)
            sys.stdout.write(f"\r  Progress: {percent:.1f}%")
            sys.stdout.flush()
        
        urllib.request.urlretrieve(url, installer_path, reporthook=download_progress)
        print()  # New line after progress
        
        print_status(f"Downloaded to {installer_path}", "ok")
        return installer_path
        
    except Exception as e:
        print_status(f"Download failed: {e}", "error")
        return None

def install_python_windows(installer_path):
    """Install Python using the installer"""
    print_status("Installing Python...", "info")
    print_status("Please wait, this may take a few minutes...", "info")
    
    try:
        # Install with default options, add to PATH
        result = subprocess.run(
            [str(installer_path), "/quiet", "InstallAllUsers=0", 
             "PrependPath=1", "Include_test=0"],
            capture_output=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print_status("Python installed successfully!", "ok")
            return True
        else:
            print_status(f"Installation failed with code {result.returncode}", "error")
            print_status(f"Error: {result.stderr.decode()}", "error")
            return False
            
    except subprocess.TimeoutExpired:
        print_status("Installation timed out", "error")
        return False
    except Exception as e:
        print_status(f"Installation error: {e}", "error")
        return False

def download_and_install_python():
    """Main function to download and install Python"""
    system = platform.system()
    
    if system != "Windows":
        print_status(f"Auto-install not supported on {system}", "error")
        print_status("Please install Python manually:", "info")
        print("  Ubuntu/Debian: sudo apt-get install python3.11")
        print("  macOS: brew install python@3.11")
        print("  Or visit: https://python.org/downloads")
        return False
    
    # Download
    installer_path = download_python_windows()
    if not installer_path:
        return False
    
    # Install
    if install_python_windows(installer_path):
        # Clean up installer
        try:
            os.remove(installer_path)
            print_status("Cleaned up installer", "info")
        except:
            pass
        return True
    
    return False

def main():
    """Main entry point"""
    print("=" * 60)
    print("Python Auto-Installer for MnMCP")
    print("=" * 60)
    print()
    
    # Check if Python is already installed
    if check_python_installed():
        print()
        print_status("Python is ready!", "ok")
        return 0
    
    print()
    print_status("Python not found or version too old", "warn")
    print()
    
    # Ask user
    response = input("Download and install Python automatically? (y/n): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print_status("Installation cancelled", "info")
        print()
        print("You can manually install Python from:")
        print("  https://www.python.org/downloads")
        return 1
    
    print()
    
    # Download and install
    if download_and_install_python():
        print()
        print_status("Python installation complete!", "ok")
        print_status("Please restart your terminal/command prompt", "info")
        print()
        print("Then run: python setup.py")
        return 0
    else:
        print()
        print_status("Installation failed", "error")
        print()
        print("Please manually install Python from:")
        print("  https://www.python.org/downloads")
        print()
        print("Make sure to check 'Add Python to PATH' during installation")
        return 1

if __name__ == "__main__":
    sys.exit(main())
