#!/usr/bin/env python3
"""
检查官服APK
"""

import zipfile
import re
from pathlib import Path

APK_PATH = Path(r"C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\miniworldMini-wp.apk")

def check_apk():
    print("="*70)
    print("检查官服APK")
    print("="*70)
    
    if not APK_PATH.exists():
        print(f"✗ APK不存在: {APK_PATH}")
        return False
    
    size_gb = APK_PATH.stat().st_size / 1024 / 1024 / 1024
    print(f"✓ APK存在")
    print(f"  文件名: {APK_PATH.name}")
    print(f"  大小: {size_gb:.2f} GB")
    print()
    
    # 检查包名
    print("[检查包名]")
    try:
        with zipfile.ZipFile(APK_PATH, 'r') as zf:
            if "AndroidManifest.xml" in zf.namelist():
                content = zf.read("AndroidManifest.xml").decode('utf-8', errors='ignore')
                match = re.search(r'package="([^"]+)"', content)
                if match:
                    package = match.group(1)
                    print(f"  包名: {package}")
                    
                    if package == "com.minitech.miniworld":
                        print("  ✅ 确认: 这是官方包！")
                        return True
                    elif ".uc" in package or ".channel" in package:
                        print(f"  ⚠️  警告: 这可能还是渠道服 ({package})")
                        return False
                    else:
                        print(f"  ℹ️  包名: {package}")
                        return True
    except Exception as e:
        print(f"  ✗ 检查失败: {e}")
    
    return False

if __name__ == "__main__":
    check_apk()
