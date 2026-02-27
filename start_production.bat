@echo off
chcp 65001 >nul
title MnMCP Production Server
echo ==========================================
echo  MnMCP 生产环境启动器
echo ==========================================
echo.

echo [*] 检查环境...

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装!
    pause
    exit /b 1
)

echo [+] Python检查通过

REM 检查Java (可选，用于PaperMC)
java -version >nul 2>&1
if errorlevel 1 (
    echo [!] Java未安装，PaperMC服务器将无法启动
    echo [!] 将使用纯Python代理模式
) else (
    echo [+] Java检查通过
)

echo.
echo [*] 启动MnMCP桥接器...
echo.

cd /d "%~dp0"
python src\core\bridge_integrated.py

echo.
echo [*] 服务已停止
echo.
pause
