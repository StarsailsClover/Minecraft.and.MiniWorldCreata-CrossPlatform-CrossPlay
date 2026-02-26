#!/usr/bin/env python3
"""
双端反编译脚本
同时反编译Android APK和PC版游戏
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime

# 导入路径解析
sys.path.insert(0, str(Path(__file__).parent))
from path_resolver import EXTERNAL_DIR, get_apk_path, get_pc_game_path, get_tool_path

# 配置
APK_PATH = EXTERNAL_DIR / "packs_downloads" / "com.minitech.miniworld.uc.apk"
PC_PATH = EXTERNAL_DIR / "packs_downloads" / "miniworldPC_CN"
OUTPUT_BASE = EXTERNAL_DIR / "packs_downloads" / "decompiled"

APKTOOL_PATH = get_tool_path("apktool.jar")
JADX_PATH = get_tool_path(r"jadx\bin\jadx.bat")

CHECKPOINT_FILE = Path(__file__).parent / "reverse_engineering" / "both_decompile_checkpoint.json"

def log(message):
    """打印日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def load_checkpoint():
    """加载检查点"""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {
        "android": {"status": "pending", "started": None, "completed": None},
        "pc": {"status": "pending", "started": None, "completed": None}
    }

def save_checkpoint(checkpoint):
    """保存检查点"""
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint, f, indent=2)

def decompile_android():
    """反编译Android APK"""
    log("="*70)
    log("[Android端] 开始反编译APK")
    log("="*70)
    
    if not APK_PATH.exists():
        log(f"✗ APK不存在: {APK_PATH}")
        return False
    
    output_dir = OUTPUT_BASE / "android"
    
    # 清理旧目录
    if output_dir.exists():
        log(f"[清理] 删除旧目录: {output_dir}")
        shutil.rmtree(output_dir)
    
    log(f"APK: {APK_PATH}")
    log(f"大小: {APK_PATH.stat().st_size / 1024 / 1024:.1f} MB")
    log(f"输出: {output_dir}")
    log("")
    
    # 使用apktool
    log("[1/2] 使用apktool反编译...")
    cmd = ["java", "-jar", APKTOOL_PATH, "d", str(APK_PATH), "-o", str(output_dir), "-f"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            log("✓ apktool完成")
        else:
            log(f"⚠ apktool警告: {result.stderr[:200]}")
    except Exception as e:
        log(f"✗ apktool失败: {e}")
        return False
    
    # 使用jadx
    log("[2/2] 使用jadx反编译...")
    sources_dir = output_dir / "jadx_sources"
    cmd = [JADX_PATH, "-d", str(sources_dir), "--show-bad-code", "--no-res", str(APK_PATH)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
        if sources_dir.exists() and any(sources_dir.iterdir()):
            log("✓ jadx完成")
        else:
            log("⚠ jadx未生成源代码")
    except Exception as e:
        log(f"✗ jadx失败: {e}")
    
    # 统计结果
    if output_dir.exists():
        smali_count = sum(1 for _ in (output_dir / "smali").rglob("*.smali") if (output_dir / "smali").exists())
        log(f"\n[结果] smali文件数: {smali_count}")
    
    log("✓ Android端反编译完成\n")
    return True

def decompile_pc():
    """分析PC版游戏"""
    log("="*70)
    log("[PC端] 分析游戏文件")
    log("="*70)
    
    if not PC_PATH.exists():
        log(f"✗ PC版路径不存在: {PC_PATH}")
        return False
    
    output_dir = OUTPUT_BASE / "pc"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log(f"PC版路径: {PC_PATH}")
    
    # 1. 分析目录结构
    log("\n[1/3] 分析目录结构...")
    structure_file = output_dir / "directory_structure.txt"
    with open(structure_file, 'w', encoding='utf-8') as f:
        f.write("PC版迷你世界目录结构\n")
        f.write("="*70 + "\n\n")
        
        for root, dirs, files in os.walk(PC_PATH):
            level = root.replace(str(PC_PATH), '').count(os.sep)
            indent = ' ' * 2 * level
            f.write(f"{indent}{os.path.basename(root)}/\n")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:10]:  # 只显示前10个文件
                f.write(f"{subindent}{file}\n")
            if len(files) > 10:
                f.write(f"{subindent}... 还有 {len(files) - 10} 个文件\n")
    
    log(f"✓ 目录结构已保存: {structure_file}")
    
    # 2. 查找关键文件
    log("\n[2/3] 查找关键文件...")
    key_files = {
        "exe": [],
        "dll": [],
        "config": [],
        "log": []
    }
    
    for root, dirs, files in os.walk(PC_PATH):
        for file in files:
            file_lower = file.lower()
            if file_lower.endswith('.exe'):
                key_files["exe"].append(os.path.join(root, file))
            elif file_lower.endswith('.dll'):
                key_files["dll"].append(os.path.join(root, file))
            elif file_lower.endswith(('.json', '.xml', '.ini', '.cfg')):
                key_files["config"].append(os.path.join(root, file))
            elif file_lower.endswith('.log'):
                key_files["log"].append(os.path.join(root, file))
    
    key_files_file = output_dir / "key_files.json"
    with open(key_files_file, 'w', encoding='utf-8') as f:
        json.dump(key_files, f, indent=2)
    
    log(f"✓ 找到 {len(key_files['exe'])} 个EXE文件")
    log(f"✓ 找到 {len(key_files['dll'])} 个DLL文件")
    log(f"✓ 找到 {len(key_files['config'])} 个配置文件")
    log(f"✓ 关键文件列表已保存: {key_files_file}")
    
    # 3. 分析日志文件
    log("\n[3/3] 分析日志文件...")
    log_analysis = output_dir / "log_analysis.txt"
    with open(log_analysis, 'w', encoding='utf-8') as f:
        f.write("日志文件分析\n")
        f.write("="*70 + "\n\n")
        
        for log_file in key_files["log"][:5]:  # 分析前5个日志
            f.write(f"\n文件: {log_file}\n")
            f.write("-"*70 + "\n")
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as lf:
                    lines = lf.readlines()[:50]  # 前50行
                    for line in lines:
                        f.write(line)
            except Exception as e:
                f.write(f"读取失败: {e}\n")
            f.write("\n")
    
    log(f"✓ 日志分析已保存: {log_analysis}")
    
    log("\n✓ PC端分析完成\n")
    return True

def analyze_both():
    """对比分析双端"""
    log("="*70)
    log("[对比分析] Android vs PC")
    log("="*70)
    
    output_dir = OUTPUT_BASE / "comparison"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 检查AndroidManifest
    log("\n[1/2] 分析Android端信息...")
    android_info = {}
    manifest_path = OUTPUT_BASE / "android" / "AndroidManifest.xml"
    if manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # 提取包名
            import re
            match = re.search(r'package="([^"]+)"', content)
            if match:
                android_info["package"] = match.group(1)
            # 提取版本
            match = re.search(r'android:versionName="([^"]+)"', content)
            if match:
                android_info["version"] = match.group(1)
    
    log(f"  包名: {android_info.get('package', '未知')}")
    log(f"  版本: {android_info.get('version', '未知')}")
    
    # 2. 检查PC端版本
    log("\n[2/2] 分析PC端信息...")
    pc_info = {}
    
    # 查找版本文件
    version_files = list((OUTPUT_BASE / "pc").rglob("*version*"))
    pc_info["version_files"] = [str(f) for f in version_files]
    
    log(f"  版本文件数: {len(version_files)}")
    
    # 3. 生成对比报告
    report_file = output_dir / "platform_comparison.json"
    comparison = {
        "android": android_info,
        "pc": pc_info,
        "analysis_time": datetime.now().isoformat()
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    log(f"\n✓ 对比报告已保存: {report_file}")
    
    return True

def main():
    """主函数"""
    print("="*70)
    print("迷你世界双端反编译工具")
    print("Android APK + PC版")
    print("="*70)
    print()
    
    checkpoint = load_checkpoint()
    
    # 检查文件
    log("[检查] 检查文件...")
    if APK_PATH.exists():
        log(f"✓ Android APK: {APK_PATH.name} ({APK_PATH.stat().st_size/1024/1024:.1f} MB)")
    else:
        log(f"✗ Android APK不存在")
    
    if PC_PATH.exists():
        log(f"✓ PC版: {PC_PATH}")
    else:
        log(f"✗ PC版不存在")
    
    log("")
    
    # 反编译Android
    if APK_PATH.exists():
        checkpoint["android"]["started"] = datetime.now().isoformat()
        save_checkpoint(checkpoint)
        
        if decompile_android():
            checkpoint["android"]["status"] = "completed"
            checkpoint["android"]["completed"] = datetime.now().isoformat()
        else:
            checkpoint["android"]["status"] = "failed"
        
        save_checkpoint(checkpoint)
    
    # 分析PC
    if PC_PATH.exists():
        checkpoint["pc"]["started"] = datetime.now().isoformat()
        save_checkpoint(checkpoint)
        
        if decompile_pc():
            checkpoint["pc"]["status"] = "completed"
            checkpoint["pc"]["completed"] = datetime.now().isoformat()
        else:
            checkpoint["pc"]["status"] = "failed"
        
        save_checkpoint(checkpoint)
    
    # 对比分析
    if (OUTPUT_BASE / "android").exists() and (OUTPUT_BASE / "pc").exists():
        analyze_both()
    
    # 完成
    log("="*70)
    log("双端分析完成")
    log(f"输出目录: {OUTPUT_BASE}")
    log("="*70)

if __name__ == "__main__":
    main()
