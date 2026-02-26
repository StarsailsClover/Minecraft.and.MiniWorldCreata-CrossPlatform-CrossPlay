#!/usr/bin/env python3
"""
PC端迷你世界网络抓包分析工具
使用Proxifier + Wireshark 或 直接Hook Winsock
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime

# 配置
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent.parent
EXTERNAL_DIR = PROJECT_DIR.parent / "MnMCPResources"
PC_GAME_DIR = EXTERNAL_DIR / "packs_downloads" / "miniworldPC_CN" / "miniworldLauncher"
CAPTURE_DIR = EXTERNAL_DIR / "packs_downloads" / "captures"

def find_game_executable():
    """查找游戏可执行文件"""
    executables = [
        "iworldpc.exe",
        "MicroMiniNew.exe",
        "minigameapppc.exe"
    ]
    
    for exe in executables:
        exe_path = PC_GAME_DIR / exe
        if exe_path.exists():
            return exe_path
    
    return None

def setup_proxifier_config():
    """创建Proxifier配置文件"""
    print("[*] Creating Proxifier configuration...")
    
    config = """# Proxifier Configuration for MiniWorld PC
# Generated: {timestamp}

[Profile]
Name=MiniWorld Capture

[Rule]
Name=MiniWorld Game
Target={game_exe}
Action=Direct

[Rule]
Name=All Other
Target=*
Action=Proxy
Proxy=127.0.0.1:8888

[Proxy]
Address=127.0.0.1
Port=8888
Protocol=SOCKS5
""".format(
        timestamp=datetime.now().isoformat(),
        game_exe=find_game_executable() or "MiniWorld.exe"
    )
    
    config_path = CAPTURE_DIR / "proxifier_config.txt"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config)
    
    print(f"[+] Proxifier config saved to: {config_path}")
    return config_path

def analyze_log_files():
    """分析游戏日志文件"""
    print("[*] Analyzing game log files...")
    
    log_files = [
        PC_GAME_DIR / "GameApp.log",
        PC_GAME_DIR / "Crash" / "*.log"
    ]
    
    network_patterns = {
        "server_ip": r"server.*?ip[\s:=]+(\d+\.\d+\.\d+\.\d+)",
        "server_port": r"server.*?port[\s:=]+(\d+)",
        "socket": r"socket[\s:=]+(\d+)",
        "connect": r"connect.*?to[\s:]+(\d+\.\d+\.\d+\.\d+):(\d+)",
        "http": r"https?://[^\s\"]+",
        "tcp": r"tcp[\s:/]+(\d+\.\d+\.\d+\.\d+):(\d+)"
    }
    
    findings = {
        "server_addresses": [],
        "ports": [],
        "urls": [],
        "connections": []
    }
    
    for log_pattern in log_files:
        if "*" in str(log_pattern):
            import glob
            log_paths = glob.glob(str(log_pattern))
        else:
            log_paths = [log_pattern] if log_pattern.exists() else []
        
        for log_path in log_paths:
            print(f"  [+] Analyzing: {log_path}")
            
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # 搜索网络相关模式
                    for pattern_name, pattern in network_patterns.items():
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            print(f"    [!] Found {pattern_name}: {matches[:3]}")  # 只显示前3个
                            
                            if pattern_name == "server_ip":
                                findings["server_addresses"].extend(matches)
                            elif pattern_name == "server_port":
                                findings["ports"].extend(matches)
                            elif pattern_name == "http":
                                findings["urls"].extend(matches)
                            elif pattern_name == "connect":
                                findings["connections"].extend(matches)
            
            except Exception as e:
                print(f"    [-] Error reading {log_path}: {e}")
    
    # 保存分析结果
    analysis_path = CAPTURE_DIR / "log_analysis.json"
    with open(analysis_path, 'w', encoding='utf-8') as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)
    
    print(f"\n[+] Analysis saved to: {analysis_path}")
    return findings

def create_wireshark_filter():
    """创建Wireshark过滤规则"""
    print("[*] Creating Wireshark filter...")
    
    # 基于已知的迷你世界服务器信息
    filters = [
        # 常见的迷你世界服务器IP段（需要实际抓包确认）
        "ip.addr == 49.234.0.0/16",  # 腾讯云IP段示例
        "ip.addr == 106.55.0.0/16",  # 腾讯云IP段示例
        "ip.addr == 129.28.0.0/16",  # 腾讯云IP段示例
        
        # 端口过滤
        "tcp.port == 20000",  # 可能的通信端口
        "tcp.port == 20001",
        "tcp.port == 30000",
        
        # 协议过滤
        "tcp",  # 主要使用TCP
        "udp",  # 可能使用UDP进行实时通信
    ]
    
    filter_text = " or ".join(filters)
    
    filter_path = CAPTURE_DIR / "wireshark_filter.txt"
    with open(filter_path, 'w', encoding='utf-8') as f:
        f.write("# Wireshark Display Filter for MiniWorld PC\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
        f.write("# Combined filter:\n")
        f.write(filter_text + "\n\n")
        f.write("# Individual filters:\n")
        for i, f in enumerate(filters, 1):
            f.write(f"# {i}. {f}\n")
    
    print(f"[+] Wireshark filter saved to: {filter_path}")
    return filter_path

def create_capture_guide():
    """创建抓包指南"""
    guide = """# PC端迷你世界网络抓包指南

## 方法1: 使用Proxifier + Wireshark（推荐）

### 步骤1: 安装软件
1. 安装 Proxifier (https://www.proxifier.com/)
2. 安装 Wireshark (https://www.wireshark.org/)
3. 安装 Proxifier 的代理服务器（如 CCProxy）

### 步骤2: 配置Proxifier
1. 打开 Proxifier
2. 创建代理服务器: 127.0.0.1:8888 (SOCKS5)
3. 添加规则:
   - 目标: MiniWorld游戏进程 (iworldpc.exe)
   - 动作: Direct (直接连接)
   - 其他所有流量通过代理

### 步骤3: 启动Wireshark抓包
1. 选择网络接口（通常是Wi-Fi或有线网卡）
2. 设置过滤规则（见 wireshark_filter.txt）
3. 开始抓包

### 步骤4: 启动游戏
1. 启动迷你世界PC版
2. 登录并进入游戏
3. 进行联机操作
4. 停止Wireshark抓包并保存

## 方法2: 使用RawCap（本地回环抓包）

如果游戏使用127.0.0.1通信，使用RawCap:
```bash
RawCap.exe 127.0.0.1 miniworld_loopback.pcap
```

## 方法3: 使用Process Monitor

查看游戏的网络连接:
1. 下载 Process Monitor (https://docs.microsoft.com/sysinternals/downloads/procmon)
2. 过滤进程名: iworldpc.exe
3. 查看网络事件

## 分析重点

1. **登录流程**
   - 认证服务器IP和端口
   - 登录请求数据包格式
   - Token/Session获取

2. **房间管理**
   - 创建房间请求
   - 加入房间流程
   - 房间列表获取

3. **游戏同步**
   - 玩家位置同步
   - 方块操作同步
   - 聊天消息格式

4. **心跳包**
   - 保活机制
   - 间隔时间

## 注意事项

- 抓包前关闭其他网络应用，减少干扰
- 记录抓包时的操作步骤，便于分析
- 保存多个抓包文件，对比不同操作
"""
    
    guide_path = CAPTURE_DIR / "capture_guide.md"
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"[+] Capture guide saved to: {guide_path}")
    return guide_path

def main():
    """主函数"""
    print("=" * 60)
    print("PC端迷你世界网络抓包分析工具")
    print("=" * 60)
    
    # 检查游戏目录
    if not PC_GAME_DIR.exists():
        print(f"[-] Game directory not found: {PC_GAME_DIR}")
        print("[!] Please ensure PC version is installed")
        return False
    
    print(f"[+] Game directory found: {PC_GAME_DIR}")
    
    # 查找可执行文件
    game_exe = find_game_executable()
    if game_exe:
        print(f"[+] Game executable found: {game_exe}")
    else:
        print("[!] Game executable not found, will use default name")
    
    # 分析日志文件
    print("\n[*] Step 1: Analyzing log files...")
    findings = analyze_log_files()
    
    # 创建Proxifier配置
    print("\n[*] Step 2: Creating Proxifier configuration...")
    proxifier_config = setup_proxifier_config()
    
    # 创建Wireshark过滤规则
    print("\n[*] Step 3: Creating Wireshark filter...")
    wireshark_filter = create_wireshark_filter()
    
    # 创建抓包指南
    print("\n[*] Step 4: Creating capture guide...")
    guide_path = create_capture_guide()
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Install Proxifier and Wireshark")
    print("2. Configure Proxifier using the generated config")
    print("3. Start Wireshark with the provided filter")
    print("4. Launch MiniWorld PC and capture traffic")
    print(f"\nAll files saved to: {CAPTURE_DIR}")
    
    return True

if __name__ == "__main__":
    main()
