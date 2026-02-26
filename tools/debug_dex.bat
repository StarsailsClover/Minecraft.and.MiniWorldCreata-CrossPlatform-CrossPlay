@echo off
echo DEX Source Debugger
echo ===================
echo.

set DEX=C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\java_sources

echo [1] Checking directory...
if exist "%DEX%" (
    echo [OK] Directory exists
) else (
    echo [FAIL] Directory NOT found
    echo Looking for: %DEX%
    pause
    exit /b 1
)

echo.
echo [2] Counting Java files...
for /f %%a in ('dir /s /b "%DEX%\*.java" 2^>nul ^| find /c /v ""') do set COUNT=%%a
echo Found: %COUNT% Java files

echo.
echo [3] Listing sample files...
dir /s /b "%DEX%\*.java" 2>nul | findstr /n "." | findstr "^1:\|^2:\|^3:\|^4:\|^5:"

echo.
echo Press any key to run PowerShell version...
pause >nul

powershell -ExecutionPolicy Bypass -Command "Write-Host 'PowerShell is working!'; Get-ChildItem -Path '%DEX%' -Filter '*.java' -Recurse | Select-Object -First 5 | Format-Table Name, Length"