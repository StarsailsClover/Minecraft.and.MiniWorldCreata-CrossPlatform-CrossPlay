@echo off
title MnMCP Server - Build EXE
echo ============================================
echo   MnMCP Server - Build Script
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

echo [INFO] Cleaning previous build...
flutter clean

echo.
echo [INFO] Getting dependencies...
flutter pub get
if errorlevel 1 (
    echo [ERROR] Failed to get dependencies!
    pause
    exit /b 1
)

echo.
echo [INFO] Building Windows executable...
echo This may take a few minutes...
flutter build windows --release

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build Complete!
echo ============================================
echo.
echo Output location:
echo   build\windows\x64\runner\Release\mnmcp_server.exe
echo.
echo You can also find the full release in:
echo   build\windows\x64\runner\Release\
echo.
pause
