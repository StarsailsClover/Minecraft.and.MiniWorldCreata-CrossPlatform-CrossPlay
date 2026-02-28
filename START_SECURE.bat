@echo off
chcp 65001 >nul
echo ==========================================
echo MnMCP 安全启动脚本
echo ==========================================
echo.

REM 设置解密密钥
set MNCP_KEY=MnMCP_Secure_Key_2024
echo [*] 解密密钥已设置

REM 设置项目目录
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

REM 检查Python
echo [*] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [-] 错误: 未找到Python
    pause
    exit /b 1
)
echo [+] Python已安装

REM 激活虚拟环境
echo [*] 激活虚拟环境...
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
    echo [+] 虚拟环境已激活
) else (
    echo [!] 虚拟环境不存在，使用系统Python
)

REM 测试解密功能
echo [*] 测试解密功能...
python -c "from src.security.crypto_utils import decrypt as D; print(D('ENC:1oKYhg=='))" >nul 2>&1
if errorlevel 1 (
    echo [-] 解密测试失败，请检查加密模块
    pause
    exit /b 1
)
echo [+] 解密功能正常

REM 运行导入测试
echo [*] 运行导入测试...
python test_import.py
if errorlevel 1 (
    echo [-] 导入测试失败
    pause
    exit /b 1
)

echo.
echo ==========================================
echo 系统检查通过！
echo ==========================================
echo.
echo 请选择操作:
echo   1. 启动代理服务器
echo   2. 运行测试
echo   3. 退出
echo.

set /p choice="请输入选项 (1-3): "

if "%choice%"=="1" goto start_proxy
if "%choice%"=="2" goto run_tests
if "%choice%"=="3" goto exit

echo [-] 无效选项
goto exit

:start_proxy
echo.
echo [*] 启动代理服务器...
echo [*] 按 Ctrl+C 停止
echo.
python start_proxy.py
goto exit

:run_tests
echo.
echo [*] 运行测试...
python -m pytest tests/ -v
goto exit

:exit
echo.
echo [*] 退出...
pause
exit /b 0
