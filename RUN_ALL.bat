@echo off
chcp 65001 >nul
title MnMCP - Run All Components
cls

echo ============================================
echo    MnMCP - Run All Components
echo ============================================
echo.

:: Set Python path
set PYTHON_EXE=C:\Users\Sails\AppData\Local\Programs\Python\Python314\python.exe

:: Check Python
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found!
    echo Searched at: %PYTHON_EXE%
    echo.
    echo Trying 'python' command...
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not available!
        pause
        exit /b 1
    ) else (
        set PYTHON_EXE=python
        echo [OK] Found Python via PATH
    )
) else (
    echo [OK] Python found: %PYTHON_EXE%
)

echo.
cd /d "%~dp0"

:menu
cls
echo ============================================
echo    MnMCP Component Launcher
echo ============================================
echo.
echo  [1] Run Protocol Demo (Terminal)
echo  [2] Open Website (Browser)
echo  [3] Run Serial Monitor (GUI)
echo  [4] Run All Components
echo  [5] Check Python Environment
echo  [6] Exit
echo.
echo ============================================
set /p choice="Select option (1-6): "

if "%choice%"=="1" goto run_demo
if "%choice%"=="2" goto open_website
if "%choice%"=="3" goto run_serial
if "%choice%"=="4" goto run_all
if "%choice%"=="5" goto check_env
if "%choice%"=="6" goto end

echo Invalid option!
timeout /t 2 >nul
goto menu

:run_demo
cls
echo Running Protocol Demo...
echo ============================
echo.
"%PYTHON_EXE%" demo\simple_demo.py
echo.
echo Demo finished.
pause
goto menu

:open_website
cls
echo Opening Website...
echo ============================
echo.
if exist "MnMCPWebsite\index.html" (
    start "" "MnMCPWebsite\index.html"
    echo [OK] Website opened in browser
) else (
    echo [ERROR] Website file not found!
)
timeout /t 2 >nul
goto menu

:run_serial
cls
echo Running Serial Monitor...
echo ============================
echo.
if exist "tools\SerialMonitor.py" (
    start "" "%PYTHON_EXE%" tools\SerialMonitor.py
    echo [OK] Serial Monitor started
) else (
    echo [ERROR] SerialMonitor.py not found!
)
timeout /t 2 >nul
goto menu

:run_all
cls
echo Running All Components...
echo ============================
echo.
echo [1/3] Starting Protocol Demo...
start "Protocol Demo" cmd /k "echo Protocol Demo Window & echo ============================ & \"%PYTHON_EXE%\" demo\simple_demo.py"
timeout /t 1 >nul

echo [2/3] Opening Website...
if exist "MnMCPWebsite\index.html" (
    start "" "MnMCPWebsite\index.html"
)
timeout /t 1 >nul

echo [3/3] Starting Serial Monitor...
if exist "tools\SerialMonitor.py" (
    start "Serial Monitor" "%PYTHON_EXE%" tools\SerialMonitor.py
)

echo.
echo [OK] All components started!
echo Check the opened windows.
pause
goto menu

:check_env
cls
echo Checking Python Environment...
echo ============================
echo.
echo Python executable: %PYTHON_EXE%
echo.
"%PYTHON_EXE%" --version
echo.
echo Installed packages:
"%PYTHON_EXE%" -m pip list | findstr /i "cryptography pyserial"
echo.
pause
goto menu

:end
echo.
echo Goodbye!
timeout /t 1 >nul