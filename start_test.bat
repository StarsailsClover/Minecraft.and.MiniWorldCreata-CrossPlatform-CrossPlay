@echo off
chcp 65001 >nul
title MnMCP Quick Test Launcher
color 0A

REM ============================================
REM MnMCP 快速测试启动器
REM ============================================

cd /d "%~dp0"

:MENU
cls
echo.
echo  ============================================
echo   MnMCP 快速测试启动器
echo  ============================================
echo.
echo  [1] 交互式测试菜单 (推荐)
echo      完整的交互式测试环境
echo.
echo  [2] 真实连接测试
echo      执行自动化真实连接测试
echo.
echo  [3] 端到端测试
echo      运行 test_end_to_end.py
echo.
echo  [4] 组件测试
echo      运行 final_test.py
echo.
echo  [5] 启动桥接服务器
echo      仅启动 MnMCP 桥接器
echo.
echo  [6] 退出
echo.
echo  ============================================
set /p choice="请选择 [1-6]: "

if "%choice%"=="1" goto INTERACTIVE
if "%choice%"=="2" goto REAL_TEST
if "%choice%"=="3" goto END_TO_END
if "%choice%"=="4" goto FINAL_TEST
if "%choice%"=="5" goto START_BRIDGE
if "%choice%"=="6" exit

goto MENU

:INTERACTIVE
call interactive_test.bat
goto MENU

:REAL_TEST
cls
echo.
echo  ============================================
echo   真实连接测试
echo  ============================================
echo.
python real_connection_test.py
echo.
pause
goto MENU

:END_TO_END
cls
echo.
echo  ============================================
echo   端到端测试
echo  ============================================
echo.
python test_end_to_end.py
echo.
pause
goto MENU

:FINAL_TEST
cls
echo.
echo  ============================================
echo   组件测试
echo  ============================================
echo.
python final_test.py
echo.
pause
goto MENU

:START_BRIDGE
cls
echo.
echo  ============================================
echo   启动桥接服务器
echo  ============================================
echo.
python src\core\bridge_integrated.py
echo.
pause
goto MENU
