@echo off
REM MnMCP Unified Launcher
REM This is the main entry point for Windows users

echo ==========================================
echo  MnMCP - Minecraft & MiniWorld
echo  Cross-Platform Multiplayer
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.11 or higher:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH"
    echo during installation.
    echo.
    pause
    exit /b 1
)

REM Run the Python setup script
python setup.py

pause
