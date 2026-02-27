@echo off
chcp 65001 >nul
title MnMCP Interactive Test - Real Connection Test
color 0A

REM ============================================
REM MnMCP 交互式真实测试脚本
REM 实际启动客户端，执行真实握手和数据交换
REM ============================================

echo.
echo  ============================================
echo   MnMCP 交互式真实测试
echo   Interactive Real Connection Test
echo  ============================================
echo.
echo  本脚本将：
echo   1. 启动 MnMCP 桥接服务器
echo   2. 启动 Wireshark 抓包
echo   3. 等待 Minecraft 客户端连接
echo   4. 执行真实握手流程
echo   5. 测试数据包转发
echo   6. 输出详细日志
echo.
echo  请确保：
echo   - Minecraft 1.20.6 已安装
echo   - 迷你世界客户端可用
echo   - Wireshark 已安装
echo.
pause

REM 设置路径
set MNMCP_PATH=C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay
set WIRESHARK_PATH=D:\Program Files\Wireshark\Wireshark.exe
set MINIWORLD_PATH=C:\Users\Sails\Documents\Coding\MnMCPResources\Resources\pc_versions\miniworldPC_CN\miniworldLauncher\MicroMiniNew.exe

cd /d "%MNMCP_PATH%"

:MENU
cls
echo.
echo  ============================================
echo   MnMCP 交互式测试菜单
echo  ============================================
echo.
echo  [1] 完整测试流程 (推荐)
echo      启动桥接器 → 启动Wireshark → 等待MC连接 → 测试功能
echo.
echo  [2] 仅启动桥接服务器
echo      启动 MnMCP 桥接器，等待手动连接
echo.
echo  [3] 测试端到端数据流
echo      运行自动化数据流测试
echo.
echo  [4] 启动 Wireshark 抓包
echo      启动 Wireshark 并设置过滤器
echo.
echo  [5] 启动迷你世界客户端
echo      启动迷你世界用于测试
echo.
echo  [6] 查看日志
echo      查看最近的测试日志
echo.
echo  [7] 清理并退出
echo.
echo  ============================================
set /p choice="请选择操作 [1-7]: "

if "%choice%"=="1" goto FULL_TEST
if "%choice%"=="2" goto START_BRIDGE
if "%choice%"=="3" goto TEST_DATAFLOW
if "%choice%"=="4" goto START_WIRESHARK
if "%choice%"=="5" goto START_MINIWORLD
if "%choice%"=="6" goto VIEW_LOGS
if "%choice%"=="7" goto CLEANUP

echo [!] 无效选择，请重试
timeout /t 2 >nul
goto MENU

:FULL_TEST
echo.
echo  ============================================
echo   [1/6] 完整测试流程
echo  ============================================
echo.

REM Step 1: 检查环境
echo [*] 步骤 1/6: 检查环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python 未安装！
    pause
    goto MENU
)
echo [OK] Python 检查通过

REM Step 2: 启动桥接服务器
echo.
echo [*] 步骤 2/6: 启动 MnMCP 桥接服务器...
echo [i] 正在启动桥接器，端口 25565...
start "MnMCP Bridge Server" cmd /k "cd /d %MNMCP_PATH% && python src\core\bridge_integrated.py 2>&1 | tee logs\bridge_$(date +%%Y%%m%%d_%%H%%M%%S).log"

echo [OK] 桥接服务器已启动

REM Step 3: 启动 Wireshark
echo.
echo [*] 步骤 3/6: 启动 Wireshark 抓包...
if exist "%WIRESHARK_PATH%" (
    start "" "%WIRESHARK_PATH%" -k -i "\Device\NPF_Loopback" -f "tcp port 25565 or tcp port 8080"
    echo [OK] Wireshark 已启动
    echo [i] 过滤器: tcp port 25565 or tcp port 8080
) else (
    echo [!] Wireshark 未找到: %WIRESHARK_PATH%
    echo [i] 请手动启动 Wireshark
)

REM Step 4: 等待MC连接
echo.
echo [*] 步骤 4/6: 等待 Minecraft 客户端连接...
echo [i] 请在 Minecraft 1.20.6 中添加服务器：
echo     地址: localhost:25565
echo     名称: MnMCP Test
echo.
echo [i] 连接后按任意键继续测试...
pause

REM Step 5: 执行数据流测试
echo.
echo [*] 步骤 5/6: 执行端到端数据流测试...
python test_end_to_end.py > logs\test_$(date +%%Y%%m%%d_%%H%%M%%S).log 2>&1
echo [OK] 测试完成，日志已保存

REM Step 6: 总结
echo.
echo  ============================================
echo   [6/6] 测试完成！
echo  ============================================
echo.
echo [OK] 所有步骤执行完毕
echo [i] 日志位置: %MNMCP_PATH%\logs\
echo.
pause
goto MENU

:START_BRIDGE
echo.
echo  ============================================
echo   启动 MnMCP 桥接服务器
echo  ============================================
echo.
echo [*] 正在启动桥接器...
echo [*] 监听端口: 25565
echo [*] 按 Ctrl+C 停止
echo.
python src\core\bridge_integrated.py
echo.
echo [OK] 桥接器已停止
echo.
pause
goto MENU

:TEST_DATAFLOW
echo.
echo  ============================================
echo   测试端到端数据流
echo  ============================================
echo.
echo [*] 运行数据流测试...
python test_end_to_end.py
echo.
echo [OK] 测试完成
echo.
pause
goto MENU

:START_WIRESHARK
echo.
echo  ============================================
echo   启动 Wireshark 抓包
echo  ============================================
echo.
if exist "%WIRESHARK_PATH%" (
    echo [*] 启动 Wireshark...
    echo [*] 过滤器: tcp port 25565 or tcp port 8080
    start "" "%WIRESHARK_PATH%" -k -i "\Device\NPF_Loopback" -f "tcp port 25565 or tcp port 8080"
    echo [OK] Wireshark 已启动
) else (
    echo [X] Wireshark 未找到: %WIRESHARK_PATH%
    echo [i] 请检查路径或手动启动
)
echo.
pause
goto MENU

:START_MINIWORLD
echo.
echo  ============================================
echo   启动迷你世界客户端
echo  ============================================
echo.
if exist "%MINIWORLD_PATH%" (
    echo [*] 启动迷你世界...
    start "" "%MINIWORLD_PATH%"
    echo [OK] 迷你世界已启动
) else (
    echo [X] 迷你世界未找到: %MINIWORLD_PATH%
    echo [i] 请检查路径
)
echo.
pause
goto MENU

:VIEW_LOGS
echo.
echo  ============================================
echo   查看日志
echo  ============================================
echo.
if exist "logs" (
    echo [*] 可用日志文件：
    dir /b logs\*.log 2>nul
    if errorlevel 1 (
        echo [i] 暂无日志文件
    )
) else (
    echo [i] 日志目录不存在
)
echo.
pause
goto MENU

:CLEANUP
echo.
echo  ============================================
echo   清理并退出
echo  ============================================
echo.
echo [*] 正在清理...
taskkill /FI "WINDOWTITLE eq MnMCP Bridge Server" /F >nul 2>&1
echo [OK] 已停止桥接服务器
echo.
echo [OK] 清理完成
echo.
echo 感谢使用 MnMCP 交互式测试！
echo.
pause
exit
