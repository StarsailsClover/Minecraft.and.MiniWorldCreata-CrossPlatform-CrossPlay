@echo off
REM MnMCP Quick Start
REM One-click startup

echo ==========================================
echo MnMCP Quick Start
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [Error] Python not found
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo [OK] Python found

REM Install dependencies if needed
echo.
echo Checking dependencies...

python -c "import websockets" >nul 2>&1
if errorlevel 1 (
    echo Installing websockets...
    python -m pip install websockets -q
)

python -c "import yaml" >nul 2>&1
if errorlevel 1 (
    echo Installing pyyaml...
    python -m pip install pyyaml -q
)

echo [OK] Dependencies ready

REM Show menu
echo.
echo ==========================================
echo Select Action:
echo ==========================================
echo [1] Start Proxy Server (for multiplayer)
echo [2] Run Demo (show features)
echo [3] Run Tests
echo [4] Open User Guide
echo [5] Exit
echo.

set /p choice="Enter number (1-5): "

if "%choice%"=="1" (
    cls
    echo ==========================================
    echo Starting MnMCP Proxy Server
    echo ==========================================
    echo.
    echo Configuration:
    echo   MiniWorld connects to: 127.0.0.1:8080
    echo   Minecraft connects to: 127.0.0.1:19132
    echo.
    echo Press Ctrl+C to stop server
    echo.
    python start.py
    pause
) else if "%choice%"=="2" (
    cls
    echo Running Demo...
    python demo_connection.py
    pause
) else if "%choice%"=="3" (
    cls
    echo Running Tests...
    python tests\test_crypto.py
    python tests\test_block_mapper.py
    python tests\test_protocol.py
    pause
) else if "%choice%"=="4" (
    start docs\USER_GUIDE.md
) else if "%choice%"=="5" (
    exit /b 0
) else (
    echo Invalid choice
    pause
)
