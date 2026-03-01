@echo off
REM MnMCP Launcher
REM Main entry point for Windows

echo ============================================
echo  MnMCP - Minecraft and MiniWorld
echo  Cross-Platform Multiplayer
echo ============================================
echo.

REM Check Python (try multiple methods)
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    echo.
    echo Please install Python 3.11+ from https://python.org
    echo Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Menu
echo Select option:
echo [1] Check Project Integrity
echo [2] Run Demo (Show features)
echo [3] Start Server
echo [4] Exit
echo.

set /p choice="Enter 1-4: "

if "%choice%"=="1" (
    echo.
    echo Running integrity check...
    python check_project_integrity.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo Running demo...
    python demo_connection.py
    pause
) else if "%choice%"=="3" (
    echo.
    echo Starting server...
    echo Press Ctrl+C to stop
echo.
    python start.py
) else if "%choice%"=="4" (
    exit /b 0
) else (
    echo Invalid choice
    pause
)
