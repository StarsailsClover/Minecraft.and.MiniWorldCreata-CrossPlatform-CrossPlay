@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo    MnMCP 一键部署脚本 (Windows)
echo ========================================

:: 1. 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请确保已安装并添加到 PATH。
    pause
    exit /b 1
)
echo [1/5] Python 环境检查通过

:: 2. 检查依赖包
pip show cryptography >nul 2>&1
if errorlevel 1 (
    echo [警告] 未检测到 cryptography 包，正在自动安装...
    pip install cryptography
)
pip show pyserial >nul 2>&1
if errorlevel 1 (
    echo [警告] 未检测到 pyserial 包，正在自动安装...
    pip install pyserial
)

:: 3. 设置解密密钥
if not defined DEPLOY_KEY (
    echo.
    echo [提示] 未检测到环境变量 DEPLOY_KEY，请输入解密密钥（输入时不可见）：
    set /p "key=密钥: " <nul
    set "DEPLOY_KEY=%key%"
    echo.
)

:: 4. 解密配置
echo [2/5] 正在解密配置文件...
python scripts\decrypt_config.py
if errorlevel 1 (
    echo [错误] 解密失败，请检查 DEPLOY_KEY 是否正确。
    pause
    exit /b 1
)

:: 5. 启动网站
echo [3/5] 启动介绍网站...
start "" "MnMCPWebsite\index.html"

:: 6. 启动串口监视器（可选）
echo [4/5] 是否启动串口监视器？(Y/N)
choice /c YN /n /m "输入 Y 启动，N 跳过："
if errorlevel 2 goto skip_serial
    echo [5/5] 正在启动串口监视器...
    start "" python tools\SerialMonitor.py
:skip_serial

echo.
echo ========================================
echo    部署完成！网站已打开，串口工具已就绪。
echo ========================================
pause