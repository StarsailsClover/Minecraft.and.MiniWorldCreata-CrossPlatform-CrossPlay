#!/usr/bin/env python3
"""
重新反编译官服APK
"""

import os
import shutil
import subprocess
from pathlib import Path

# 路径配置
EXTERNAL_DIR = Path(r"C:\Users\Sails\Documents\Coding\MnMCPResources")
APK_NAME = "miniworldMini-wp.apk"
APK_PATH = EXTERNAL_DIR / "packs_downloads" / APK_NAME
OUTPUT_DIR = EXTERNAL_DIR / "packs_downloads" / "decompiled_official"
TOOLS_DIR = Path(r"C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\tools")
APKTOOL_PATH = TOOLS_DIR / "apktool.jar"
JADX_PATH = TOOLS_DIR / "jadx" / "bin" / "jadx.bat"

def print_header():
    print("="*70)
    print("官服APK反编译")
    print("="*70)

def check_apk():
    """检查APK"""
    print("\n[1/4] 检查APK")
    
    if not APK_PATH.exists():
        print(f"  ✗ APK不存在: {APK_PATH}")
        return False
    
    size_gb = APK_PATH.stat().st_size / 1024 / 1024 / 1024
    print(f"  ✓ APK存在")
    print(f"    文件名: {APK_NAME}")
    print(f"    大小: {size_gb:.2f} GB")
    return True

def cleanup():
    """清理旧文件"""
    print("\n[2/4] 清理旧文件")
    
    # 删除旧反编译输出
    old_output = EXTERNAL_DIR / "packs_downloads" / "decompiled" / "android"
    if old_output.exists():
        try:
            shutil.rmtree(old_output)
            print(f"  ✓ 已删除旧输出: {old_output}")
        except Exception as e:
            print(f"  ⚠ 删除失败: {e}")
    
    # 删除旧的UC渠道服APK（可选）
    uc_apk = EXTERNAL_DIR / "packs_downloads" / "com.minitech.miniworld.uc.apk"
    if uc_apk.exists():
        backup_dir = EXTERNAL_DIR / "packs_downloads" / "backup"
        backup_dir.mkdir(exist_ok=True)
        try:
            shutil.move(str(uc_apk), str(backup_dir / "com.minitech.miniworld.uc.apk"))
            print(f"  ✓ UC渠道服APK已移动到backup/")
        except Exception as e:
            print(f"  ⚠ 移动失败: {e}")

def decompile():
    """反编译"""
    print("\n[3/4] 开始反编译")
    print(f"  输出目录: {OUTPUT_DIR}")
    print()
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 使用apktool
    print("  [1/2] 使用apktool反编译...")
    print("  预计时间: 5-15分钟")
    
    cmd = [
        "java", "-jar", str(APKTOOL_PATH),
        "d", str(APK_PATH),
        "-o", str(OUTPUT_DIR),
        "-f"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        if result.returncode == 0:
            print("  ✓ apktool完成")
        else:
            print(f"  ⚠ apktool警告（可能正常）")
    except Exception as e:
        print(f"  ✗ apktool失败: {e}")
        return False
    
    # 使用jadx
    print("\n  [2/2] 使用jadx反编译...")
    print("  预计时间: 10-20分钟")
    
    sources_dir = OUTPUT_DIR / "jadx_sources"
    cmd = [str(JADX_PATH), "-d", str(sources_dir), "--show-bad-code", "--no-res", str(APK_PATH)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        if sources_dir.exists() and any(sources_dir.iterdir()):
            print("  ✓ jadx完成")
        else:
            print("  ⚠ jadx未生成源代码")
    except Exception as e:
        print(f"  ✗ jadx失败: {e}")
    
    return True

def analyze():
    """分析结果"""
    print("\n[4/4] 分析结果")
    
    if not OUTPUT_DIR.exists():
        print("  ✗ 输出目录不存在")
        return
    
    # 统计文件
    smali_count = sum(1 for _ in (OUTPUT_DIR / "smali").rglob("*.smali") if (OUTPUT_DIR / "smali").exists())
    
    print(f"  ✓ 反编译完成")
    print(f"    smali文件数: {smali_count}")
    print(f"    输出目录: {OUTPUT_DIR}")
    
    # 检查关键文件
    key_files = ["AndroidManifest.xml", "smali", "jadx_sources"]
    print("\n  [关键文件]")
    for f in key_files:
        path = OUTPUT_DIR / f
        if path.exists():
            print(f"    ✓ {f}")
        else:
            print(f"    ✗ {f}")

def print_summary():
    """打印总结"""
    print("\n" + "="*70)
    print("反编译完成")
    print("="*70)
    
    print("\n[下一步]")
    print("1. 使用jadx GUI查看源代码:")
    print(f"   {JADX_PATH} {APK_PATH}")
    print("\n2. 搜索网络协议相关代码:")
    print(f"   grep -r 'socket' {OUTPUT_DIR}/smali/ --include='*.smali'")
    print("\n3. 分析数据包结构")
    print("\n4. 更新ID映射表")

def main():
    print_header()
    
    if not check_apk():
        return
    
    cleanup()
    
    if decompile():
        analyze()
        print_summary()
    else:
        print("\n✗ 反编译失败")

if __name__ == "__main__":
    main()
