@echo off
chcp 65001 >nul
echo ==========================================
echo Minecraft PaperMC 1.20.6 服务端启动器
echo Made with ❤️ by ZCNotFound
echo ==========================================
echo.

set JAVA_OPTS=-Xmx2G -Xms1G
set SERVER_JAR=paper.jar

echo 正在检查 Java 环境...
java -version 2>&1 | findstr "version" >nul
if errorlevel 1 (
    echo [错误] 未检测到 Java，请先安装 Java 17 或更高版本
    pause
    exit /b 1
)

echo [OK] Java 环境检测通过
echo.

if not exist %SERVER_JAR% (
    echo [错误] 未找到 %SERVER_JAR%
    pause
    exit /b 1
)

echo 正在启动 PaperMC 服务端...
echo 内存分配: %JAVA_OPTS%
echo.

cd paper
java %JAVA_OPTS% -jar %SERVER_JAR% nogui

echo.
echo 服务端已停止
pause
