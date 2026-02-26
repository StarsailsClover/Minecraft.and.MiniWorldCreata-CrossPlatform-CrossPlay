#!/usr/bin/env python3
"""
选择正确接口进行抓包
"""

import subprocess
import time
from pathlib import Path
from datetime import datetime

TSHARK_PATH = r"D:\Program Files\Wireshark\tshark.exe"
CAPTURE_DIR = Path(r"C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\captures")

def main():
    print("=" * 60)
    print("迷你世界PC端抓包 - 选择接口")
    print("=" * 60)
    
    # 列出所有接口
    print("\n[*] 可用网络接口：")
    result = subprocess.run(
        [TSHARK_PATH, "-D"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    
    # 推荐使用WLAN或以太网接口
    print("\n[!] 请选择你的网络接口：")
    print("    - 如果使用WiFi：选择 WLAN 或 Wi-Fi 相关的接口")
    print("    - 如果使用网线：选择 以太网 或 Ethernet 相关的接口")
    print("\n[!] 请手动运行以下命令抓包：")
    print("=" * 60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = CAPTURE_DIR / f"miniworld_manual_{timestamp}.pcapng"
    
    # 显示命令示例
    print(f"\n{tshark_path}")
    print("  -i <接口编号>")
    print(f"  -w \"{output_file}\"")
    print("  -a duration:180")
    print("\n例如（如果使用接口5）：")
    print(f'  {TSHARK_PATH} -i 5 -w "{output_file}" -a duration:180')
    
    print("\n" + "=" * 60)
    print("操作步骤：")
    print("1. 查看上面的接口列表，找到你的网络接口编号")
    print("2. 在命令行中运行上面的命令（替换<接口编号>）")
    print("3. 立即启动迷你世界并进行游戏操作")
    print("4. 等待180秒（3分钟）自动完成，或按Ctrl+C提前停止")
    print("5. 告诉我抓包完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
