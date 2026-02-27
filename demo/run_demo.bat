@echo off
chcp 65001 >nul
echo ============================================
echo MnMCP Protocol Demo
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

echo [OK] Python found

REM Run demo
echo.
echo Starting protocol demo...
echo.

python "%~dp0protocol_demo.py"

if errorlevel 1 (
    echo.
    echo [ERROR] Demo failed!
    pause
    exit /b 1
)

echo.
echo [OK] Demo completed!
pause