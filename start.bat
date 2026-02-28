@echo off
REM MnMCP Startup Script
REM Simple batch file to start the proxy server

echo ==========================================
echo MnMCP Proxy Server
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

REM Check dependencies
echo Checking dependencies...
python -c "import websockets" >nul 2>&1
if errorlevel 1 (
    echo Installing websockets...
    python -m pip install websockets
)

python -c "import yaml" >nul 2>&1
if errorlevel 1 (
    echo Installing pyyaml...
    python -m pip install pyyaml
)

echo.
echo Starting MnMCP Proxy Server...
echo.
echo Configuration:
echo   MNW Listen: 0.0.0.0:8080
echo   MC Target:  127.0.0.1:19132
echo.
echo Press Ctrl+C to stop
echo.

python start.py

pause
