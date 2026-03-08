@echo off
title MnMCP Server
echo ============================================
echo   MnMCP Server Launcher
echo   v0.4.0
echo ============================================
echo.

REM Check if Flutter is installed
where flutter >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Flutter not found!
    echo Please install Flutter from https://flutter.dev
    pause
    exit /b 1
)

echo [OK] Flutter found
flutter --version
echo.

REM Check if dependencies are installed
if not exist "pubspec.lock" (
    echo [INFO] Installing dependencies...
    call flutter pub get
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo [INFO] Starting MnMCP Server...
echo.

REM Run in desktop mode
flutter run -d windows

if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with error!
    pause
)
