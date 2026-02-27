@echo off
chcp 65001 >nul
title MnMCP Protocol Demo
cls

echo ============================================
echo    MnMCP Protocol Demo
echo    Minecraft ↔ MiniWorld Protocol Demo
echo ============================================
echo.
echo [Step 1] Checking Python installation...
echo.

:: 使用完整路径调用Python
set PYTHON_EXE=C:\Users\Sails\AppData\Local\Programs\Python\Python314\python.exe

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found at: %PYTHON_EXE%
    echo.
    echo Trying to find Python automatically...
    where python >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not found in PATH!
        echo Please install Python 3.11 or higher from python.org
        pause
        exit /b 1
    ) else (
        for /f "tokens=*" %%a in ('where python') do (
            set PYTHON_EXE=%%a
            goto found_python
        )
    )
)

:found_python
echo [OK] Python found: %PYTHON_EXE%
echo.

:: Check Python version
for /f "tokens=*" %%v in ('"%PYTHON_EXE%" --version 2^>^&1') do (
    echo [OK] Python version: %%v
)
echo.

echo [Step 2] Checking required packages...
echo.

:: Check cryptography
"%PYTHON_EXE%" -c "import cryptography" 2>nul
if errorlevel 1 (
    echo [WARNING] cryptography not found. Installing...
    "%PYTHON_EXE%" -m pip install cryptography
) else (
    echo [OK] cryptography installed
)

:: Check pyserial
"%PYTHON_EXE%" -c "import serial" 2>nul
if errorlevel 1 (
    echo [WARNING] pyserial not found. Installing...
    "%PYTHON_EXE%" -m pip install pyserial
) else (
    echo [OK] pyserial installed
)

echo.
echo [Step 3] Starting Protocol Demo...
echo.

:: Change to script directory
cd /d "%~dp0"

:: Run the demo
echo ============================================
echo    Starting Demo - Press Ctrl+C to stop
echo ============================================
echo.

"%PYTHON_EXE%" demo\simple_demo.py

if errorlevel 1 (
    echo.
    echo [ERROR] Demo failed with error code %errorlevel%
    pause
    exit /b 1
)

echo.
echo [OK] Demo completed successfully!
pause