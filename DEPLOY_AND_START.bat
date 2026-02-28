@echo off
REM MnMCP Deployment and Startup Script
REM Encoding: UTF-8

echo ==========================================
echo MnMCP Deployment and Startup Tool
echo Minecraft - MiniWorld Cross-Platform
echo ==========================================
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not installed. Please install Python 3.11+
    pause
    exit /b 1
)
echo [OK] Python installed

REM Check pip
echo.
echo [2/5] Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [X] pip not installed
    pause
    exit /b 1
)
echo [OK] pip installed

REM Install dependencies
echo.
echo [3/5] Installing dependencies...
echo Installing websockets...
python -m pip install websockets>=12.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo [Warning] websockets install failed, trying default mirror...
    python -m pip install websockets>=12.0
)

echo Installing pyyaml...
python -m pip install pyyaml>=6.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo [Warning] pyyaml install failed, trying default mirror...
    python -m pip install pyyaml>=6.0
)

echo Installing cryptography (optional)...
python -m pip install cryptography>=41.0.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

REM Check project files
echo.
echo [4/5] Checking project files...
if not exist "config.yaml" (
    echo [X] config.yaml not found
    pause
    exit /b 1
)
echo [OK] config.yaml exists

if not exist "data\mnw_block_mapping_from_go.json" (
    echo [X] Block mapping file not found
    pause
    exit /b 1
)
echo [OK] Block mapping file exists

if not exist "src" (
    echo [X] Source directory not found
    pause
    exit /b 1
)
echo [OK] Source directory exists

REM Run tests
echo.
echo [5/5] Running tests...
python tests\test_block_mapper.py >nul 2>&1
if errorlevel 1 (
    echo [Warning] Block mapper test failed
) else (
    echo [OK] Block mapper test passed
)

echo.
echo ==========================================
echo Deployment Complete!
echo ==========================================
echo.

REM Open user guide
echo Opening user guide...
start docs\USER_GUIDE.md

REM Menu
echo.
echo Select operation:
echo [1] Start Proxy Server
echo [2] Run Connection Demo
echo [3] Run Integrity Check
echo [4] Exit
echo.

set /p choice="Enter option (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting proxy server...
    echo Config: MNW listen 0.0.0.0:8080, MC target 127.0.0.1:19132
    echo.
    echo After start:
    echo   - Minecraft connect to 127.0.0.1:19132
    echo   - MiniWorld connect to 127.0.0.1:8080
    echo.
    python start.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo Running connection demo...
    python demo_connection.py
    pause
) else if "%choice%"=="3" (
    echo.
    echo Running integrity check...
    python check_project_integrity.py
    pause
) else if "%choice%"=="4" (
    echo.
    echo Thank you for using MnMCP!
    exit /b 0
) else (
    echo.
    echo Invalid option
    pause
)
