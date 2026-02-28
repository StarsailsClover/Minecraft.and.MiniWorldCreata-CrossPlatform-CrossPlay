@echo off
chcp 65001 >nul
echo ==========================================
echo MnMCP 一键部署和启动脚本
echo ==========================================
echo.

REM 设置路径
set PROJECT_DIR=%~dp0
set PYTHON=python

REM 检查Python
echo [*] 检查Python环境...
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo [-] 错误: 未找到Python
    echo     请安装Python 3.11+ 并添加到PATH
    pause
    exit /b 1
)
echo [+] Python已安装

REM 检查虚拟环境
echo.
echo [*] 检查虚拟环境...
if not exist "%PROJECT_DIR%venv" (
    echo [*] 创建虚拟环境...
    %PYTHON% -m venv "%PROJECT_DIR%venv"
    if errorlevel 1 (
        echo [-] 创建虚拟环境失败
        pause
        exit /b 1
    )
)
echo [+] 虚拟环境已准备

REM 激活虚拟环境
echo.
echo [*] 激活虚拟环境...
call "%PROJECT_DIR%venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [-] 激活虚拟环境失败
    pause
    exit /b 1
)
echo [+] 虚拟环境已激活

REM 安装依赖
echo.
echo [*] 安装/更新依赖...
pip install -q -r "%PROJECT_DIR%requirements.txt"
if errorlevel 1 (
    echo [-] 安装依赖失败
    pause
    exit /b 1
)
echo [+] 依赖已安装

REM 初始化解密环境
echo.
echo [*] 初始化解密环境...
set MNCP_KEY=MnMCP_Secure_Key_2024
setx MNCP_KEY "%MNCP_KEY%" >nul 2>&1
echo [+] 环境变量已设置

REM 检查配置文件
echo.
echo [*] 检查配置文件...
if not exist "%USERPROFILE%\.mnmcp\config.json" (
    echo [*] 创建默认配置...
    if not exist "%USERPROFILE%\.mnmcp" mkdir "%USERPROFILE%\.mnmcp"
    copy "%PROJECT_DIR%config\config.example.json" "%USERPROFILE%\.mnmcp\config.json" >nul
    echo [+] 配置文件已创建
) else (
    echo [+] 配置文件已存在
)

REM 运行测试
echo.
echo [*] 运行导入测试...
%PYTHON% "%PROJECT_DIR%test_import.py"
if errorlevel 1 (
    echo [-] 导入测试失败
    pause
    exit /b 1
)
echo [+] 导入测试通过

echo.
echo ==========================================
echo 部署完成！
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
%PYTHON% "%PROJECT_DIR%start_proxy.py"
goto exit

:run_tests
echo.
echo [*] 运行测试...
%PYTHON% -m pytest "%PROJECT_DIR%tests\" -v
goto exit

:exit
echo.
echo [*] 退出...
deactivate >nul 2>&1
pause
exit /b 0
