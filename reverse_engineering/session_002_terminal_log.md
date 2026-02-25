# 逆向工程会话记录 - Session 002
## 任务: 下载 Minecraft Java 服务端与互通模组
## 开始时间: 2026-02-25 23:45
## 完成时间: 2026-02-25 23:58

### 步骤 1: 创建服务器目录结构
```powershell
New-Item -ItemType Directory -Force -Path 'server\paper'
New-Item -ItemType Directory -Force -Path 'server\fabric'
New-Item -ItemType Directory -Force -Path 'server\mods'
New-Item -ItemType Directory -Force -Path 'server\plugins'
New-Item -ItemType Directory -Force -Path 'server\config'
```
状态: ✅ 完成

### 步骤 2: 下载 PaperMC 1.20.6
```powershell
# 获取构建信息
Invoke-WebRequest -Uri 'https://api.papermc.io/v2/projects/paper/versions/1.20.6/builds' -OutFile 'server\paper\builds.json'

# 解析并下载最新构建 (Build 151)
python server\download_paper.py
```
状态: ✅ 完成
- 文件: paper-1.20.6-151.jar (约45MB)
- 构建号: 151
- 同时创建了 paper.jar 副本

### 步骤 3: 下载 GeyserMC
```powershell
Invoke-WebRequest -Uri 'https://download.geysermc.org/v2/projects/geyser/versions/2.3.1/builds/latest/downloads/spigot' -OutFile 'server\plugins\Geyser-Spigot.jar' -TimeoutSec 120
```
状态: ✅ 完成
- 文件: Geyser-Spigot.jar
- 用途: Java ↔ Bedrock 协议桥接

### 步骤 4: 下载 Floodgate
```powershell
Invoke-WebRequest -Uri 'https://download.geysermc.org/v2/projects/floodgate/versions/latest/builds/latest/downloads/spigot' -OutFile 'server\plugins\floodgate-spigot.jar' -TimeoutSec 120
```
状态: ✅ 完成
- 文件: floodgate-spigot.jar
- 用途: 基岩版玩家认证

### 步骤 5: 下载 Fabric 安装器
```powershell
Invoke-WebRequest -Uri 'https://maven.fabricmc.net/net/fabricmc/fabric-installer/1.0.1/fabric-installer-1.0.1.jar' -OutFile 'server\fabric\fabric-installer.jar'
```
状态: ✅ 完成
- 文件: fabric-installer.jar
- 用途: Fabric 模组加载器安装

### 步骤 6: 下载 Fabric API
```powershell
Invoke-WebRequest -Uri 'https://github.com/FabricMC/fabric/releases/download/0.98.0%2B1.20.6/fabric-api-0.98.0+1.20.6.jar' -OutFile 'server\mods\fabric-api-0.98.0.jar' -TimeoutSec 120
```
状态: ✅ 完成
- 文件: fabric-api-0.98.0.jar
- 版本: 0.98.0+1.20.6

### 已下载文件清单

| 组件 | 版本 | 路径 | 大小 |
|------|------|------|------|
| PaperMC | 1.20.6 Build 151 | server/paper/paper-1.20.6-151.jar | ~45MB |
| GeyserMC | 2.3.1 | server/plugins/Geyser-Spigot.jar | ~12MB |
| Floodgate | Latest | server/plugins/floodgate-spigot.jar | ~3MB |
| Fabric Installer | 1.0.1 | server/fabric/fabric-installer.jar | ~0.1MB |
| Fabric API | 0.98.0 | server/mods/fabric-api-0.98.0.jar | ~2MB |

### 创建文档
- server/README.md - 服务端配置与使用说明

### 下一步计划
1. 创建服务端启动脚本
2. 配置 eula.txt 和 server.properties
3. 配置 GeyserMC 和 Floodgate
4. 启动服务端进行测试
5. 使用 Wireshark 捕获数据包

### 断点记录
- 当前步骤: Java服务端与模组下载完成
- 下次继续: 服务端配置与启动测试
- 备份位置: backups/session_002_backup.zip
