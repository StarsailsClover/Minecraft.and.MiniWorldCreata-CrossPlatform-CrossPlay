#!/usr/bin/env python3
"""
迷你世界国服APK反编译脚本（带进度监控）
"""

import os
import subprocess
import shutil
import sys
import time
from datetime import datetime

# 动态获取路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
EXTERNAL_DIR = os.path.join(os.path.dirname(PROJECT_DIR), "MnMCPResources")

# 配置
APK_NAME = "miniworld_cn_1.53.1.apk"
APK_PATH = os.path.join(EXTERNAL_DIR, "apk_downloads", APK_NAME)
OUTPUT_DIR = os.path.join(EXTERNAL_DIR, "apk_downloads", "miniworld_cn_decompiled")
TOOLS_DIR = os.path.join(PROJECT_DIR, "tools")
APKTOOL_PATH = os.path.join(TOOLS_DIR, "apktool.jar")
JADX_PATH = os.path.join(TOOLS_DIR, "jadx", "bin", "jadx.bat")

# 日志文件
LOG_FILE = os.path.join(PROJECT_DIR, "reverse_engineering", "decompile_log.txt")

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')

def check_apk():
    """检查APK文件"""
    log("="*70)
    log("检查APK文件")
    log("="*70)
    
    if not os.path.exists(APK_PATH):
        log(f"✗ APK文件不存在: {APK_PATH}")
        return False
    
    size_gb = os.path.getsize(APK_PATH) / 1024 / 1024 / 1024
    log(f"✓ 找到APK文件")
    log(f"  路径: {APK_PATH}")
    log(f"  大小: {size_gb:.2f} GB")
    return True

def decompile_apktool():
    """使用apktool反编译"""
    log("\n" + "="*70)
    log("[步骤1/2] 使用apktool反编译")
    log("="*70)
    
    # 清理旧目录
    if os.path.exists(OUTPUT_DIR):
        log(f"[清理] 删除旧目录: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    
    # 执行反编译
    cmd = [
        "java", "-jar", APKTOOL_PATH,
        "d", APK_PATH,
        "-o", OUTPUT_DIR,
        "-f"
    ]
    
    log(f"[执行] apktool反编译")
    log(f"  输出目录: {OUTPUT_DIR}")
    log(f"  预计时间: 5-15分钟（取决于系统性能）")
    log("")
    
    start_time = time.time()
    
    try:
        # 实时输出
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # 实时读取输出
        for line in process.stdout:
            line = line.strip()
            if line:
                log(f"  {line}")
        
        process.wait()
        elapsed = time.time() - start_time
        
        if process.returncode == 0:
            log(f"\n✓ apktool反编译成功")
            log(f"  耗时: {elapsed/60:.1f} 分钟")
            return True
        else:
            log(f"\n✗ apktool失败，返回码: {process.returncode}")
            return False
            
    except Exception as e:
        log(f"\n✗ 错误: {str(e)}")
        return False

def decompile_jadx():
    """使用jadx反编译"""
    log("\n" + "="*70)
    log("[步骤2/2] 使用jadx反编译")
    log("="*70)
    
    sources_dir = os.path.join(OUTPUT_DIR, "jadx_sources")
    
    # 清理旧目录
    if os.path.exists(sources_dir):
        log(f"[清理] 删除旧目录: {sources_dir}")
        shutil.rmtree(sources_dir)
    
    # 执行反编译
    cmd = [
        JADX_PATH,
        "-d", sources_dir,
        "--show-bad-code",
        "--no-res",
        APK_PATH
    ]
    
    log(f"[执行] jadx反编译")
    log(f"  源代码目录: {sources_dir}")
    log(f"  预计时间: 10-30分钟（取决于系统性能）")
    log("")
    
    start_time = time.time()
    
    try:
        # 实时输出
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # 实时读取输出
        for line in process.stdout:
            line = line.strip()
            if line:
                log(f"  {line}")
        
        process.wait()
        elapsed = time.time() - start_time
        
        # 检查是否生成源代码
        if os.path.exists(sources_dir) and len(os.listdir(sources_dir)) > 0:
            log(f"\n✓ jadx反编译完成")
            log(f"  耗时: {elapsed/60:.1f} 分钟")
            log(f"  源代码目录: {sources_dir}")
            return True
        else:
            log(f"\n✗ jadx未生成源代码")
            return False
            
    except Exception as e:
        log(f"\n✗ 错误: {str(e)}")
        return False

def analyze_results():
    """分析反编译结果"""
    log("\n" + "="*70)
    log("分析反编译结果")
    log("="*70)
    
    if not os.path.exists(OUTPUT_DIR):
        log("✗ 反编译目录不存在")
        return
    
    # 统计文件
    total_files = 0
    smali_files = 0
    smali_classes = set()
    
    for root, dirs, files in os.walk(OUTPUT_DIR):
        total_files += len(files)
        if 'smali' in os.path.basename(root):
            smali_files += len(files)
            # 记录smali类别
            if 'smali_classes' in root:
                class_num = root.split('smali_classes')[-1].split(os.sep)[0]
                if class_num.isdigit():
                    smali_classes.add(int(class_num))
    
    log(f"总文件数: {total_files}")
    log(f"smali文件数: {smali_files}")
    log(f"smali类别数: {len(smali_classes) + 1}")  # +1 for main smali
    
    # 显示关键目录
    key_items = [
        ("AndroidManifest.xml", "file"),
        ("smali", "dir"),
        ("smali_classes2", "dir"),
        ("smali_classes3", "dir"),
        ("lib", "dir"),
        ("assets", "dir"),
        ("jadx_sources", "dir"),
    ]
    
    log("\n[关键目录/文件]")
    for item, item_type in key_items:
        path = os.path.join(OUTPUT_DIR, item)
        if os.path.exists(path):
            if item_type == "dir":
                try:
                    count = len(os.listdir(path))
                    log(f"  ✓ {item}/ ({count} 项)")
                except:
                    log(f"  ✓ {item}/")
            else:
                size = os.path.getsize(path) / 1024
                log(f"  ✓ {item} ({size:.1f} KB)")
        else:
            log(f"  ✗ {item}")

def search_protocol_files():
    """搜索协议相关文件"""
    log("\n" + "="*70)
    log("搜索协议相关文件")
    log("="*70)
    
    keywords = [
        ("network", "网络相关"),
        ("socket", "Socket通信"),
        ("tcp", "TCP协议"),
        ("udp", "UDP协议"),
        ("http", "HTTP协议"),
        ("protocol", "协议实现"),
        ("packet", "数据包"),
        ("message", "消息"),
        ("encrypt", "加密"),
        ("decrypt", "解密"),
        ("aes", "AES加密"),
        ("rsa", "RSA加密"),
        ("login", "登录"),
        ("auth", "认证"),
        ("session", "会话"),
    ]
    
    smali_dir = os.path.join(OUTPUT_DIR, "smali")
    
    if not os.path.exists(smali_dir):
        log("✗ smali目录不存在")
        return
    
    log("[搜索关键词]")
    found_keywords = []
    
    for keyword, desc in keywords:
        # 简单统计包含关键词的文件数
        count = 0
        for root, dirs, files in os.walk(smali_dir):
            for file in files:
                if keyword.lower() in file.lower():
                    count += 1
        
        if count > 0:
            log(f"  {desc} ({keyword}): {count} 个文件")
            found_keywords.append((keyword, desc, count))
    
    # 保存结果
    result_file = os.path.join(PROJECT_DIR, "reverse_engineering", "protocol_search_results.txt")
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write("协议相关文件搜索结果\n")
        f.write("="*70 + "\n\n")
        for keyword, desc, count in found_keywords:
            f.write(f"{desc} ({keyword}): {count} 个文件\n")
    
    log(f"\n[保存] 搜索结果已保存到: {result_file}")

def main():
    """主函数"""
    # 清空日志
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("")
    
    log("="*70)
    log("迷你世界国服APK反编译工具")
    log("="*70)
    
    # 检查
    if not check_apk():
        log("\n✗ 请确保APK文件已下载")
        return
    
    # 检查工具
    if not os.path.exists(APKTOOL_PATH):
        log(f"✗ apktool未找到: {APKTOOL_PATH}")
        return
    
    if not os.path.exists(JADX_PATH):
        log(f"✗ jadx未找到: {JADX_PATH}")
        return
    
    log("\n✓ 所有工具已就绪")
    log("[自动模式] 开始反编译...")
    
    # 执行反编译
    success = True
    
    if not decompile_apktool():
        success = False
    
    if not decompile_jadx():
        success = False
    
    # 分析
    analyze_results()
    search_protocol_files()
    
    # 完成
    log("\n" + "="*70)
    if success:
        log("✓ 反编译完成")
        log(f"输出目录: {OUTPUT_DIR}")
        log("\n建议下一步:")
        log("1. 使用jadx GUI查看源代码")
        log(f"   {os.path.join(TOOLS_DIR, 'jadx', 'bin', 'jadx-gui.bat')} {APK_PATH}")
        log("2. 分析smali代码中的网络协议")
        log("3. 查找加密算法实现")
    else:
        log("✗ 反编译过程中有错误")
        log(f"查看日志: {LOG_FILE}")
    log("="*70)

if __name__ == "__main__":
    main()
