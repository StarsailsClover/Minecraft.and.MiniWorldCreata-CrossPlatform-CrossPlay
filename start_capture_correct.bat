@echo off
chcp 65001 >nul
echo ==========================================
echo MnMCP 握手验证 - 正确路径启动器
echo ==========================================
echo.

REM 设置正确的路径
set GAME_PATH="C:\Users\Sails\Documents\Coding\MnMCPResources\Resources\pc_versions\miniworldPC_CN\miniworldLauncher\MicroMiniNew.exe"
set CAPTURE_DIR="C:\Users\Sails\Documents\Coding\MnMCPResources\Resources\captures"
set TSHARK="D:\Program Files\Wireshark\tshark.exe"

echo [*] 检查游戏路径...
if not exist %GAME_PATH% (
    echo [-] 错误: 未找到游戏文件
    echo     %GAME_PATH%
    pause
    exit /b 1
)

echo [+] 游戏路径正确

echo.
echo [*] 启动抓包...
echo [*] 请按以下步骤操作:
echo     1. 等待Wireshark启动
echo     2. 选择正确的网络接口
echo     3. 开始抓包
echo     4. 然后按任意键启动游戏
echo.

REM 启动Wireshark（手动选择接口）
start "" "D:\Program Files\Wireshark\Wireshark.exe"

echo [*] 请现在配置Wireshark并开始抓包...
pause

echo.
echo [*] 启动迷你世界...
start "" %GAME_PATH%

echo.
echo [+] 游戏已启动!
echo [*] 请进行以下操作:
echo     1. 登录游戏
echo     2. 创建或加入房间
echo     3. 进行游戏操作
echo     4. 完成后停止Wireshark抓包并保存
echo.
echo [*] 按任意键结束此窗口...
pause
