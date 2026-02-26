#!/usr/bin/env python3
"""
详细检查APK来源和渠道信息
"""

import zipfile
import re
from pathlib import Path

APK_PATH = Path(r"C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\com.minitech.miniworld.uc.apk")

def check_package_name():
    """检查包名"""
    print("="*70)
    print("[1/5] 检查包名")
    print("="*70)
    
    try:
        with zipfile.ZipFile(APK_PATH, 'r') as zf:
            if "AndroidManifest.xml" in zf.namelist():
                content = zf.read("AndroidManifest.xml").decode('utf-8', errors='ignore')
                match = re.search(r'package="([^"]+)"', content)
                if match:
                    package = match.group(1)
                    print(f"包名: {package}")
                    
                    if ".uc" in package.lower():
                        print("⚠️  确认: 这是UC/九游渠道服！")
                        print("   包名包含 '.uc' 后缀")
                        return "uc"
                    elif package == "com.minitech.miniworld":
                        print("✅ 这是官方包！")
                        return "official"
                    else:
                        print(f"⚠️  未知渠道: {package}")
                        return "unknown"
    except Exception as e:
        print(f"✗ 检查失败: {e}")
    
    return None

def check_signature():
    """检查签名"""
    print("\n" + "="*70)
    print("[2/5] 检查签名文件")
    print("="*70)
    
    try:
        with zipfile.ZipFile(APK_PATH, 'r') as zf:
            meta_files = [f for f in zf.namelist() if f.startswith("META-INF/")]
            
            # 查找RSA/DSA/EC签名文件
            sig_files = [f for f in meta_files if f.endswith(('.RSA', '.DSA', '.EC'))]
            
            print(f"签名文件数: {len(sig_files)}")
            for f in sig_files:
                print(f"  - {f}")
            
            # 查找渠道标识
            channel_files = [f for f in meta_files if any(x in f.lower() for x in ['uc', 'channel', 'sdk'])]
            if channel_files:
                print(f"\n⚠️  发现渠道相关文件:")
                for f in channel_files[:5]:
                    print(f"  - {f}")
    
    except Exception as e:
        print(f"✗ 检查失败: {e}")

def check_assets():
    """检查assets目录"""
    print("\n" + "="*70)
    print("[3/5] 检查Assets目录")
    print("="*70)
    
    try:
        with zipfile.ZipFile(APK_PATH, 'r') as zf:
            assets = [f for f in zf.namelist() if f.startswith("assets/")]
            
            # 查找渠道SDK
            channel_indicators = ['uc', 'ninegame', 'channel', 'sdk']
            found = []
            
            for asset in assets:
                for indicator in channel_indicators:
                    if indicator in asset.lower():
                        found.append(asset)
                        break
            
            if found:
                print(f"⚠️  发现 {len(found)} 个渠道相关文件:")
                for f in found[:10]:
                    print(f"  - {f}")
            else:
                print("✅ 未发现明显渠道标识")
    
    except Exception as e:
        print(f"✗ 检查失败: {e}")

def check_lib():
    """检查lib目录"""
    print("\n" + "="*70)
    print("[4/5] 检查Native库")
    print("="*70)
    
    try:
        with zipfile.ZipFile(APK_PATH, 'r') as zf:
            libs = [f for f in zf.namelist() if f.startswith("lib/") and f.endswith(".so")]
            
            # 查找渠道SDK库
            channel_libs = [f for f in libs if any(x in f.lower() for x in ['uc', 'sdk', 'channel'])]
            
            print(f"Native库总数: {len(libs)}")
            
            if channel_libs:
                print(f"\n⚠️  发现 {len(channel_libs)} 个渠道相关库:")
                for f in channel_libs:
                    print(f"  - {f}")
            
            # 按架构分类
            archs = {}
            for lib in libs:
                parts = lib.split('/')
                if len(parts) >= 2:
                    arch = parts[1]
                    archs[arch] = archs.get(arch, 0) + 1
            
            print(f"\n架构分布:")
            for arch, count in archs.items():
                print(f"  - {arch}: {count} 个库")
    
    except Exception as e:
        print(f"✗ 检查失败: {e}")

def print_conclusion(channel_type):
    """打印结论"""
    print("\n" + "="*70)
    print("[5/5] 结论")
    print("="*70)
    
    if channel_type == "uc":
        print("\n🔴 确认: 这是UC/九游渠道服！")
        print("\n证据:")
        print("  1. 包名: com.minitech.miniworld.uc")
        print("  2. 包含.uc后缀")
        print("  3. 可能包含UC SDK")
        print("\n建议:")
        print("  ⚠️  渠道服协议可能有定制")
        print("  ⚠️  建议下载官服进行对比")
        print("  ✅ 官服包名: com.minitech.miniworld")
        print("\n下载地址:")
        print("  https://www.mini1.cn/")
    
    elif channel_type == "official":
        print("\n🟢 这是官方包！")
    
    else:
        print(f"\n🟡 无法确定渠道类型: {channel_type}")

def main():
    print("="*70)
    print("APK渠道来源详细检查")
    print("="*70)
    
    if not APK_PATH.exists():
        print(f"✗ APK不存在: {APK_PATH}")
        return
    
    print(f"检查文件: {APK_PATH.name}")
    print(f"文件大小: {APK_PATH.stat().st_size / 1024 / 1024:.1f} MB")
    print()
    
    channel = check_package_name()
    check_signature()
    check_assets()
    check_lib()
    print_conclusion(channel)
    
    print("\n" + "="*70)
    print("检查完成")
    print("="*70)

if __name__ == "__main__":
    main()
