#!/usr/bin/env python3
"""
MiniWorld: Creata APK 下载助手
提供下载链接和验证方法
"""

import os
import sys
from pathlib import Path

# 动态获取路径
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent
EXTERNAL_DIR = PROJECT_DIR.parent / "MnMCPResources"

APK_NAME = "miniworld_en_1.7.15.apk"
APK_PATH = EXTERNAL_DIR / "apk_downloads" / APK_NAME

def print_header():
    """打印标题"""
    print("="*70)
    print("MiniWorld: Creata APK 下载助手")
    print("版本: 1.7.15 (外服)")
    print("="*70)

def print_download_info():
    """打印下载信息"""
    print("\n[下载信息]")
    print(f"文件名: {APK_NAME}")
    print(f"目标路径: {APK_PATH}")
    print(f"预计大小: ~1.2 GB")
    
    if APK_PATH.exists():
        size_mb = APK_PATH.stat().st_size / 1024 / 1024
        print(f"当前状态: ✅ 已下载 ({size_mb:.1f} MB)")
        return True
    else:
        print(f"当前状态: ⬜ 未下载")
        return False

def print_download_sources():
    """打印下载源"""
    print("\n[下载源]")
    print("1. APKPure (推荐)")
    print("   网址: https://apkpure.net/mini-world-creata/com.playmini.miniworld")
    print("   步骤:")
    print("   - 访问网站")
    print("   - 找到版本 1.7.15")
    print("   - 点击 'Download APK'")
    print("   - 保存到:", APK_PATH)
    print()
    print("2. Uptodown (备用)")
    print("   网址: https://mini-world-creata.en.uptodown.com/android")
    print("   步骤:")
    print("   - 访问网站")
    print("   - 选择版本 1.7.15")
    print("   - 下载APK")
    print("   - 保存到:", APK_PATH)
    print()
    print("3. Aptoide (备用)")
    print("   网址: https://mini-world-creata.en.aptoide.com/")
    print("   步骤: 同上")

def print_verification():
    """打印验证信息"""
    print("\n[验证信息]")
    print("包名: com.playmini.miniworld")
    print("版本: 1.7.15")
    print("大小: ~1.2 GB")
    print("\n验证方法:")
    print("1. 使用 apktool 验证:")
    print(f"   apktool d {APK_NAME} -o test_verify")
    print("2. 检查 AndroidManifest.xml 中的版本号")
    print("3. 使用 aapt 验证:")
    print(f"   aapt dump badging {APK_NAME}")

def print_notes():
    """打印注意事项"""
    print("\n[注意事项]")
    print("⚠️  需要科学上网环境访问外服")
    print("⚠️  下载的APK仅供逆向工程研究使用")
    print("⚠️  24小时内删除")
    print("⚠️  不得用于商业用途")
    print("\n💡 提示:")
    print("- 如果下载速度慢，尝试更换下载源")
    print("- 下载后务必验证文件完整性")
    print("- 保存路径必须准确，否则反编译脚本找不到")

def create_directory():
    """创建目录"""
    apk_dir = EXTERNAL_DIR / "apk_downloads"
    if not apk_dir.exists():
        print(f"\n[创建目录] {apk_dir}")
        apk_dir.mkdir(parents=True, exist_ok=True)
        print("✓ 目录已创建")
    else:
        print(f"\n[检查目录] {apk_dir}")
        print("✓ 目录已存在")

def main():
    """主函数"""
    print_header()
    
    # 检查是否已下载
    already_downloaded = print_download_info()
    
    if already_downloaded:
        print("\n✅ APK已下载，无需重复下载")
        print(f"位置: {APK_PATH}")
        return
    
    # 创建目录
    create_directory()
    
    # 打印下载信息
    print_download_sources()
    print_verification()
    print_notes()
    
    # 提示
    print("\n" + "="*70)
    print("请手动下载APK并保存到指定位置")
    print(f"目标: {APK_PATH}")
    print("="*70)
    
    # 询问是否创建位置记录文件
    print("\n是否创建位置记录文件? (y/n): ", end="")
    # 自动创建
    location_file = SCRIPT_DIR / f"{APK_NAME}.location"
    with open(location_file, 'w') as f:
        f.write(f"FILE_MOVED_TO:\n{APK_PATH}\n")
    print(f"\n✓ 已创建位置记录: {location_file}")

if __name__ == "__main__":
    main()
