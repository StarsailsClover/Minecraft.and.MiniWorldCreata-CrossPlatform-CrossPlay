# 逆向工程会话记录 - Session 001
## 任务: Java/Bedrock版Minecraft服务器联机协议整合与分析
## 开始时间: 2026-02-25 23:23

### 步骤 1: 创建项目目录结构
```bash
mkdir -p tools
mkdir -p backups
mkdir -p apk_downloads
mkdir -p reverse_engineering
```
状态: ✅ 完成

### 步骤 2: 安装必要工具

#### 2.1 安装 apktool (APK反编译工具)
```powershell
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/windows/apktool.bat' -OutFile 'tools\apktool.bat'
Invoke-WebRequest -Uri 'https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar' -OutFile 'tools\apktool.jar'
```
状态: ✅ 完成
- apktool.bat: 2,386 bytes
- apktool.jar: 23,254,968 bytes

#### 2.2 安装 jadx (Java反编译器)
```powershell
Invoke-WebRequest -Uri 'https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip' -OutFile 'tools\jadx.zip'
Expand-Archive -Path 'tools\jadx.zip' -DestinationPath 'tools\jadx' -Force
```
状态: ✅ 完成
- jadx.zip: 29,887,862 bytes
- 解压到: tools\jadx\

#### 2.3 下载 frida-server (Android动态分析)
```powershell
Invoke-WebRequest -Uri 'https://github.com/frida/frida/releases/download/16.1.11/frida-server-16.1.11-android-arm64.xz' -OutFile 'tools\frida-server.xz' -TimeoutSec 120
```
状态: ✅ 完成
- frida-server.xz: 15,566,872 bytes
- 版本: 16.1.11
- 架构: android-arm64

#### 2.4 安装 Python pip
```powershell
python -c "import urllib.request; urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'tools\get-pip.py')"
python tools\get-pip.py --target="tools\python_libs"
```
状态: ✅ 完成
- pip 26.0.1 installed
- setuptools 82.0.0 installed
- wheel 0.46.3 installed
- packaging 26.0 installed

#### 2.5 创建环境设置脚本
创建了 setup_env.bat 用于快速设置环境变量
创建了 requirements.txt 记录所需Python包

### 当前工具清单
| 工具 | 版本 | 路径 | 用途 |
|------|------|------|------|
| apktool | 2.9.3 | tools\apktool.jar | APK反编译 |
| jadx | 1.4.7 | tools\jadx\ | Java反编译 |
| frida-server | 16.1.11 | tools\frida-server.xz | Android动态分析 |
| pip | 26.0.1 | tools\python_libs\ | Python包管理 |

### 下一步计划
1. 下载Minecraft相关APK文件
2. 下载迷你世界国服APK
3. 下载MiniWorld: Creata外服APK
4. 开始协议分析

### 断点记录
- 当前步骤: 工具安装完成
- 下次继续: 下载APK文件
- 备份位置: backups\session_001_backup.zip
