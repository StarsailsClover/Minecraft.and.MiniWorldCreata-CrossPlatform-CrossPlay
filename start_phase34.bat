@echo off
chcp 65001 >nul
title MnMCP Phase 3/4 - End-to-End Bridge
echo ==========================================
echo  MnMCP Phase 3/4
echo  端到端连接 + 游戏功能同步
echo ==========================================
echo.

cd /d "%~dp0"

echo [*] 启动Bridge V2...
echo [*] 功能:
echo    - Minecraft 客户端连接
echo    - 迷你世界服务器连接
echo    - 方块同步
echo    - 玩家移动同步
echo    - 聊天消息转发
echo.
echo [*] 配置Minecraft连接到: localhost:25565
echo.

python src\core\bridge_v2.py

echo.
echo [*] 服务已停止
echo.
pause
