@echo off
REM MnMCP - Start Here
REM Main entry point for new users

echo ==========================================
echo  MnMCP - Minecraft & MiniWorld
echo  Cross-Platform Multiplayer
echo ==========================================
echo.
echo  Welcome! This tool helps you start
echo  cross-platform multiplayer gaming.
echo.
echo  [1] Quick Start (Recommended)
echo      - Check dependencies
echo      - Start server or demo
echo.
echo  [2] Full Deployment
echo      - Complete setup
echo      - Install all dependencies
echo      - Open user guide
echo.
echo  [3] View Documentation
echo      - Open user guide
echo      - Read instructions
echo.
echo  [4] Exit
echo.

set /p choice="Select option (1-4): "

if "%choice%"=="1" (
    call QUICK_START.bat
) else if "%choice%"=="2" (
    call DEPLOY_AND_START.bat
) else if "%choice%"=="3" (
    start docs\USER_GUIDE.md
) else if "%choice%"=="4" (
    exit /b 0
) else (
    echo Invalid option
    pause
)
