#!/usr/bin/env python3
"""
自动化抓包工具 - 迷你世界PC端
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

# 配置
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent.parent
EXTERNAL_DIR = PROJECT_DIR.parent / "MnMCPResources"
CAPTURE_DIR = EXTERNAL_DIR / "packs_downloads" / "captures"
TSHARK_PATH = r"D:\Program Files\Wireshark\tshark.exe"

def get_network_interfaces():
    """获取网络接口列表"""
    print("[*] 检测网络接口...")
    
    try:
        result = subprocess.run(
            [TSHARK_PATH, "-D"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        interfaces = []
        for line in result.stdout.split('\n'):
            if line.strip():
                # 格式: 1. \Device\NPF_{GUID} (Network Name)
                parts = line.split('(')
                if len(parts) >= 2:
                    idx = line.split('.')[0].strip()
                    name = parts[1].rstrip(')')
                    interfaces.append((idx, name))
                    print(f"  [{idx}] {name}")
        
        return interfaces
    
    except Exception as e:
        print(f"[-] 获取接口失败: {e}")
        return []

def start_capture(interface_idx, output_file, duration=300):
    """启动自动抓包"""
    print(f"\n[*] 开始抓包...")
    print(f"[*] 接口: {interface_idx}")
    print(f"[*] 输出: {output_file}")
    print(f"[*] 时长: {duration}秒")
    print("\n" + "="*60)
    print("🎮 开始抓包 - 请立即启动迷你世界并进行游戏操作！")
    print("="*60 + "\n")
    
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 不使用过滤器，捕获所有流量
    cmd = [
        TSHARK_PATH,
        "-i", interface_idx,
        "-w", str(output_file),
        "-a", f"duration:{duration}"
    ]
    
    try:
        # 启动抓包进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"[+] 抓包进程已启动 (PID: {process.pid})")
        print(f"[*] 将自动运行 {duration} 秒")
        print("[*] 或按 Ctrl+C 提前停止\n")
        
        # 显示倒计时
        start_time = time.time()
        while True:
            elapsed = int(time.time() - start_time)
            remaining = duration - elapsed
            
            if remaining <= 0:
                break
            
            print(f"\r[*] 抓包中... 剩余时间: {remaining}秒", end='', flush=True)
            time.sleep(1)
            
            # 检查进程是否结束
            if process.poll() is not None:
                break
        
        print("\n\n[+] 抓包完成！")
        
        # 等待进程结束
        process.wait(timeout=10)
        
        # 检查文件
        if output_file.exists():
            size = output_file.stat().st_size / (1024*1024)
            print(f"[+] 抓包文件: {output_file}")
            print(f"[+] 文件大小: {size:.2f} MB")
            return True
        else:
            print("[-] 抓包文件未生成")
            return False
    
    except KeyboardInterrupt:
        print("\n\n[!] 用户中断抓包")
        if process:
            process.terminate()
            process.wait(timeout=5)
        
        if output_file.exists():
            size = output_file.stat().st_size / (1024*1024)
            print(f"[+] 抓包文件: {output_file}")
            print(f"[+] 文件大小: {size:.2f} MB")
            return True
        return False
    
    except Exception as e:
        print(f"\n[-] 抓包错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("迷你世界PC端自动抓包工具")
    print("=" * 60)
    
    # 检查tshark
    if not Path(TSHARK_PATH).exists():
        print(f"[-] 未找到tshark: {TSHARK_PATH}")
        return False
    
    # 获取网络接口
    interfaces = get_network_interfaces()
    if not interfaces:
        print("[-] 未找到网络接口")
        return False
    
    # 选择接口（自动选择第一个非回环接口）
    selected_idx = None
    for idx, name in interfaces:
        if 'loopback' not in name.lower() and 'adapter for loopback' not in name.lower():
            selected_idx = idx
            print(f"\n[+] 自动选择接口: [{idx}] {name}")
            break
    
    if not selected_idx:
        selected_idx = interfaces[0][0]
        print(f"\n[+] 使用默认接口: [{selected_idx}] {interfaces[0][1]}")
    
    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = CAPTURE_DIR / f"miniworld_capture_{timestamp}.pcapng"
    
    # 开始抓包
    success = start_capture(selected_idx, output_file, duration=180)  # 3分钟
    
    if success:
        print("\n" + "=" * 60)
        print("抓包完成！")
        print("=" * 60)
        print(f"\n下一步: 运行分析工具")
        print(f"python tools/pc_capture/analyze_pcap.py")
        return True
    else:
        print("\n[-] 抓包失败")
        return False

if __name__ == "__main__":
    main()
