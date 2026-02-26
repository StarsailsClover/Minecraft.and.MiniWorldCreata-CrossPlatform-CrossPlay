#!/usr/bin/env python3
"""
执行迷你世界PC端网络抓包
使用Wireshark和Proxifier
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

# 配置
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent.parent
EXTERNAL_DIR = PROJECT_DIR.parent / "MnMCPResources"
CN_GAME_DIR = EXTERNAL_DIR / "packs_downloads" / "miniworldPC_CN" / "miniworldLauncher"
GLOBAL_GAME_DIR = EXTERNAL_DIR / "packs_downloads" / "miniworldPC_Global" / "miniworldOverseasgame"
CAPTURE_DIR = EXTERNAL_DIR / "packs_downloads" / "captures"

def check_environment():
    """检查抓包环境"""
    print("[*] 检查抓包环境...")
    
    # 检查Wireshark
    wireshark_paths = [
        r"C:\Program Files\Wireshark\tshark.exe",
        r"C:\Program Files (x86)\Wireshark\tshark.exe",
    ]
    
    wireshark_found = False
    for path in wireshark_paths:
        if Path(path).exists():
            print(f"[+] 找到Wireshark: {path}")
            wireshark_found = True
            break
    
    if not wireshark_found:
        print("[-] 未找到Wireshark")
        print("[!] 请安装Wireshark: https://www.wireshark.org/download.html")
        return False
    
    # 检查Proxifier
    proxifier_paths = [
        r"C:\Program Files (x86)\Proxifier\Proxifier.exe",
        r"C:\Program Files\Proxifier\Proxifier.exe",
    ]
    
    proxifier_found = False
    for path in proxifier_paths:
        if Path(path).exists():
            print(f"[+] 找到Proxifier: {path}")
            proxifier_found = True
            break
    
    if not proxifier_found:
        print("[!] 未找到Proxifier（可选，用于代理抓包）")
        print("[!] 可以直接使用Wireshark抓包")
    
    return wireshark_found

def create_capture_config():
    """创建抓包配置"""
    print("\n[*] 创建抓包配置...")
    
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Wireshark过滤规则
    filter_rules = """# Wireshark过滤规则 - 迷你世界PC版
# 创建于: {timestamp}

# 迷你世界相关流量
host mini1.cn or host miniworldgame.com or host playmini.net

# 或按端口过滤（如果发现特定端口）
# tcp.port == 20000 or tcp.port == 20001 or tcp.port == 30000

# 或捕获所有TCP/UDP（然后手动过滤）
# tcp or udp
""".format(timestamp=datetime.now().isoformat())
    
    filter_file = CAPTURE_DIR / "wireshark_filters.txt"
    with open(filter_file, 'w', encoding='utf-8') as f:
        f.write(filter_rules)
    
    print(f"[+] 过滤规则: {filter_file}")
    
    # 抓包指南
    guide = """# 迷你世界PC端抓包指南

## 准备工作

1. 确保Wireshark已安装
2. 确保有管理员权限（Windows需要管理员权限抓包）

## 抓包步骤

### 方法1: 直接抓包（推荐）

1. 启动Wireshark
2. 选择网络接口（Wi-Fi或有线网卡）
3. 设置过滤规则: `host mini1.cn or host miniworldgame.com`
4. 点击开始抓包
5. 启动迷你世界PC版
6. 执行以下操作:
   - 登录游戏
   - 创建房间
   - 邀请好友（如果有）
   - 进行游戏操作（移动、放置方块）
   - 退出游戏
7. 停止抓包
8. 保存抓包文件 (.pcapng)

### 方法2: 使用tshark命令行

```bash
# 找到你的网络接口
tshark -D

# 开始抓包（替换InterfaceName为你的接口名）
tshark -i "InterfaceName" -f "host mini1.cn" -w miniworld_capture.pcapng

# 抓包时启动游戏，操作完成后按Ctrl+C停止
```

## 分析重点

1. **登录流程**
   - 查找认证服务器IP
   - 分析登录请求/响应
   - 识别Token/Session

2. **房间管理**
   - 创建房间请求
   - 加入房间流程
   - 房间列表同步

3. **游戏同步**
   - 玩家位置同步
   - 方块操作同步
   - 聊天消息

4. **心跳包**
   - 保活机制
   - 间隔时间

## 保存位置

抓包文件保存到:
```
MnMCPResources/packs_downloads/captures/
├── cn_capture.pcapng      # 国服抓包
├── global_capture.pcapng  # 外服抓包
└── analysis/              # 分析结果
```

## 注意事项

- 抓包前关闭其他网络应用，减少干扰
- 记录抓包时的操作步骤和时间点
- 保存多个抓包文件，对比不同操作
- 注意隐私，抓包文件可能包含敏感信息
"""
    
    guide_file = CAPTURE_DIR / "CAPTURE_GUIDE.md"
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"[+] 抓包指南: {guide_file}")
    
    return True

def analyze_game_executable(game_dir, name):
    """分析游戏可执行文件"""
    print(f"\n[*] 分析{name}可执行文件...")
    
    exe_files = list(game_dir.glob("*.exe"))
    print(f"  找到 {len(exe_files)} 个EXE文件")
    
    for exe in exe_files[:5]:  # 只显示前5个
        size = exe.stat().st_size / (1024*1024)
        print(f"    - {exe.name}: {size:.2f} MB")
    
    return exe_files

def create_bat_scripts():
    """创建批处理脚本"""
    print("\n[*] 创建抓包脚本...")
    
    # 国服抓包脚本
    cn_bat = """@echo off
chcp 65001 >nul
echo ==========================================
echo 迷你世界国服抓包启动器
echo ==========================================
echo.

REM 设置游戏路径
set GAME_DIR="{cn_dir}"
set GAME_EXE="{cn_exe}"

REM 检查游戏是否存在
if not exist %GAME_EXE% (
    echo [错误] 未找到游戏文件: %GAME_EXE%
    pause
    exit /b 1
)

echo [*] 启动Wireshark抓包...
echo [*] 请手动开始抓包，然后按任意键启动游戏...
start "" "{wireshark}"
pause

echo [*] 启动迷你世界国服...
start "" %GAME_EXE%

echo.
echo [+] 游戏已启动
echo [*] 请进行以下操作:
echo     1. 登录游戏
echo     2. 创建房间
echo     3. 进行游戏操作
echo     4. 退出游戏
echo.
echo [*] 游戏退出后，请停止Wireshark抓包并保存
echo [*] 按任意键结束...
pause
""".format(
        cn_dir=CN_GAME_DIR,
        cn_exe=CN_GAME_DIR / "iworldpc.exe",
        wireshark=r"C:\Program Files\Wireshark\Wireshark.exe"
    )
    
    cn_bat_file = CAPTURE_DIR / "capture_cn.bat"
    with open(cn_bat_file, 'w', encoding='utf-8') as f:
        f.write(cn_bat)
    
    print(f"[+] 国服抓包脚本: {cn_bat_file}")
    
    # 外服抓包脚本
    global_bat = """@echo off
chcp 65001 >nul
echo ==========================================
echo 迷你世界外服抓包启动器
echo ==========================================
echo.

REM 设置游戏路径
set GAME_DIR="{global_dir}"
set GAME_EXE="{global_exe}"

REM 检查游戏是否存在
if not exist %GAME_EXE% (
    echo [错误] 未找到游戏文件: %GAME_EXE%
    pause
    exit /b 1
)

echo [*] 启动Wireshark抓包...
echo [*] 请手动开始抓包，然后按任意键启动游戏...
start "" "{wireshark}"
pause

echo [*] 启动迷你世界外服...
start "" %GAME_EXE%

echo.
echo [+] 游戏已启动
echo [*] 请进行以下操作:
echo     1. 登录游戏
echo     2. 创建房间
echo     3. 进行游戏操作
echo     4. 退出游戏
echo.
echo [*] 游戏退出后，请停止Wireshark抓包并保存
echo [*] 按任意键结束...
pause
""".format(
        global_dir=GLOBAL_GAME_DIR,
        global_exe=GLOBAL_GAME_DIR / "iworldpc.exe",
        wireshark=r"C:\Program Files\Wireshark\Wireshark.exe"
    )
    
    global_bat_file = CAPTURE_DIR / "capture_global.bat"
    with open(global_bat_file, 'w', encoding='utf-8') as f:
        f.write(global_bat)
    
    print(f"[+] 外服抓包脚本: {global_bat_file}")
    
    return True

def generate_summary():
    """生成总结报告"""
    print("\n[*] 生成总结报告...")
    
    summary = """# 迷你世界PC端抓包准备完成

## 准备状态

- [x] Wireshark检查
- [x] 抓包配置创建
- [x] 游戏文件分析
- [x] 抓包脚本生成

## 文件位置

```
MnMCPResources/packs_downloads/captures/
├── wireshark_filters.txt    # Wireshark过滤规则
├── CAPTURE_GUIDE.md         # 抓包详细指南
├── capture_cn.bat           # 国服抓包启动脚本
└── capture_global.bat       # 外服抓包启动脚本
```

## 立即执行

### 抓包国服
1. 双击运行 `capture_cn.bat`
2. 按照提示操作
3. 保存抓包文件为 `cn_capture.pcapng`

### 抓包外服
1. 双击运行 `capture_global.bat`
2. 按照提示操作
3. 保存抓包文件为 `global_capture.pcapng`

## 抓包重点

1. **登录阶段**: 捕获认证流程
2. **创建房间**: 捕获房间管理协议
3. **游戏过程**: 捕获同步协议
4. **退出阶段**: 捕获断开连接

## 下一步

抓包完成后，将.pcapng文件放到captures目录，运行分析工具。
"""
    
    summary_file = CAPTURE_DIR / "README.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"[+] 总结报告: {summary_file}")
    
    return summary_file

def main():
    """主函数"""
    print("=" * 60)
    print("迷你世界PC端抓包准备工具")
    print("=" * 60)
    
    # 检查环境
    if not check_environment():
        print("\n[-] 环境检查失败，请安装所需软件")
        return False
    
    # 创建配置
    create_capture_config()
    
    # 分析游戏文件
    print("\n[*] 分析国服游戏...")
    analyze_game_executable(CN_GAME_DIR, "国服")
    
    print("\n[*] 分析外服游戏...")
    analyze_game_executable(GLOBAL_GAME_DIR, "外服")
    
    # 创建脚本
    create_bat_scripts()
    
    # 生成总结
    summary_file = generate_summary()
    
    print("\n" + "=" * 60)
    print("准备完成!")
    print("=" * 60)
    print(f"\n所有文件保存到: {CAPTURE_DIR}")
    print("\n下一步:")
    print("1. 双击运行 capture_cn.bat 抓包国服")
    print("2. 双击运行 capture_global.bat 抓包外服")
    print("3. 保存抓包文件到captures目录")
    print("\n抓包完成后告诉我，我会继续分析!")
    
    return True

if __name__ == "__main__":
    main()
