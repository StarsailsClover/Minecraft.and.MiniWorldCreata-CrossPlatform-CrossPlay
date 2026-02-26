# Minecraft Java版离线启动方案

基于PCL2启动器的离线启动原理分析，实现无需正版账号的本地测试环境。

---

## 方案概述

### 离线启动原理

Minecraft Java版支持离线模式（offline mode）：
- 不验证Microsoft/Mojang账号
- 使用本地生成的UUID和用户名
- 适合本地测试和开发

### PCL2启动器方案

**PCL2 (Plain Craft Launcher 2)** 支持离线启动：
- 自动下载游戏文件
- 支持离线账户登录
- 自动配置Java环境
- 支持模组加载

---

## 实现步骤

### 步骤1: 下载PCL2启动器

1. **访问PCL2官网**
   - 网址: https://afdian.net/a/LTCat
   - 或搜索: "PCL2 我的世界启动器"

2. **下载启动器**
   - 下载 `Plain Craft Launcher 2.exe`
   - 放到项目目录: `tools/pcl2/`

### 步骤2: 配置离线启动

1. **启动PCL2**
   ```
   tools/pcl2/Plain Craft Launcher 2.exe
   ```

2. **添加离线账户**
   - 点击"账户"
   - 选择"离线登录"
   - 输入用户名: `TestPlayer1`
   - 点击"添加"

3. **下载游戏版本**
   - 点击"版本"
   - 选择"1.20.6"
   - 点击"下载"

4. **启动游戏**
   - 选择离线账户
   - 点击"启动游戏"

### 步骤3: 配置服务端离线模式

编辑 `server/paper/server.properties`:

```properties
# 关闭正版验证
online-mode=false

# 允许飞行（测试需要）
allow-flight=true

# 游戏模式
gamemode=creative

# 最大玩家
max-players=20
```

### 步骤4: 连接测试

1. **启动服务端**
   ```bash
   cd server/paper
   java -Xmx2G -jar paper.jar nogui
   ```

2. **客户端连接**
   - 启动PCL2离线模式
   - 添加服务器: `localhost:25565`
   - 连接测试

---

## 自动化脚本

### 创建离线启动配置

```python
# setup_offline_minecraft.py
import os
import json
from pathlib import Path

MINECRAFT_DIR = Path(r"C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\tools\.minecraft")
LAUNCHER_DIR = Path(r"C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\tools\pcl2")

def setup_directories():
    """创建目录结构"""
    MINECRAFT_DIR.mkdir(parents=True, exist_ok=True)
    LAUNCHER_DIR.mkdir(parents=True, exist_ok=True)
    
    # 创建版本目录
    versions_dir = MINECRAFT_DIR / "versions"
    versions_dir.mkdir(exist_ok=True)
    
    print(f"✓ 目录已创建: {MINECRAFT_DIR}")

def create_offline_profile():
    """创建离线启动配置"""
    profile = {
        "selectedUser": {
            "account": "offline",
            "username": "TestPlayer1",
            "uuid": "00000000-0000-0000-0000-000000000001"
        },
        "clientToken": "offline-token",
        "authenticationDatabase": {
            "offline": {
                "username": "TestPlayer1",
                "uuid": "00000000-0000-0000-0000-000000000001",
                "accessToken": "offline"
            }
        }
    }
    
    profile_file = MINECRAFT_DIR / "launcher_profiles.json"
    with open(profile_file, 'w') as f:
        json.dump(profile, f, indent=2)
    
    print(f"✓ 离线配置已创建: {profile_file}")

def print_instructions():
    """打印使用说明"""
    print("\n" + "="*70)
    print("离线启动配置完成")
    print("="*70)
    print("\n[下一步]")
    print("1. 下载PCL2启动器到:", LAUNCHER_DIR)
    print("2. 启动PCL2，选择离线账户 'TestPlayer1'")
    print("3. 下载Minecraft 1.20.6")
    print("4. 启动服务端: server/start.bat")
    print("5. 客户端连接: localhost:25565")
    
    print("\n[测试账号]")
    print("  用户名: TestPlayer1")
    print("  UUID: 00000000-0000-0000-0000-000000000001")
    print("  模式: 离线模式（无需正版）")

if __name__ == "__main__":
    setup_directories()
    create_offline_profile()
    print_instructions()
```

---

## 多账号测试

### 创建多个离线账号

```python
# 账号配置
TEST_ACCOUNTS = [
    {"username": "TestPlayer1", "uuid": "00000000-0000-0000-0000-000000000001"},
    {"username": "TestPlayer2", "uuid": "00000000-0000-0000-0000-000000000002"},
    {"username": "MiniWorldBot", "uuid": "00000000-0000-0000-0000-000000000003"},
]
```

### 多实例启动

使用PCL2的多开功能：
1. 启动第一个实例（TestPlayer1）
2. 再次点击启动（TestPlayer2）
3. 两个客户端同时连接服务端

---

## 与服务端集成

### 启动脚本

```batch
# start_test_environment.bat
@echo off
echo 启动Minecraft测试环境...

# 1. 启动服务端
cd server/paper
start "Minecraft Server" java -Xmx2G -jar paper.jar nogui

# 2. 等待服务端启动
timeout /t 30

# 3. 启动PCL2
cd ../../tools/pcl2
start "PCL2" "Plain Craft Launcher 2.exe"

echo 测试环境已启动
echo 服务端: localhost:25565
echo 客户端: 使用PCL2离线模式连接
```

---

## 与GeyserMC集成

### 基岩版测试

GeyserMC允许基岩版连接Java版服务端：

1. **配置GeyserMC**
   ```yaml
   # plugins/Geyser-Spigot/config.yml
   bedrock:
     address: 0.0.0.0
     port: 19132
   
   remote:
     address: auto
     port: 25565
   
   # 允许离线模式
   auth-type: offline
   ```

2. **基岩版连接**
   - 添加服务器: `localhost:19132`
   - 无需Xbox账号
   - 直接连接测试

---

## 注意事项

### 离线模式限制

⚠️ **限制**:
- 无法连接正版服务器
- 无法使用Realms
- 无法访问Marketplace
- 皮肤可能不显示

✅ **适合场景**:
- 本地开发测试
- 协议分析
- 模组开发
- 局域网联机

### 安全性

- 离线模式仅在本地网络使用
- 不要用于公共服务器
- 适合开发和测试环境

---

## 下一步

配置完成后：
1. [启动服务端测试](SERVER_TEST.md)
2. [客户端连接测试](CLIENT_TEST.md)
3. [Wireshark抓包分析](WIRESHARK_CAPTURE.md)

---
Made with ❤️ by ZCNotFound for cross-platform gaming
