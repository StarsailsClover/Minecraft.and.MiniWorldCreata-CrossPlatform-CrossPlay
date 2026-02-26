#!/usr/bin/env python3
"""
迷你世界国服APK反编译脚本
使用path_resolver自动处理路径
"""

import os
import subprocess
import shutil
import sys

# 获取项目根目录（脚本的上级目录）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
EXTERNAL_DIR = os.path.join(os.path.dirname(PROJECT_DIR), "MnMCPResources")

# 配置
APK_NAME = "miniworld_cn_1.53.1.apk"

# 动态解析APK路径
def get_apk_path():
    """获取APK路径，优先外部目录，其次检查location文件"""
    # 1. 检查外部目录
    external_path = os.path.join(EXTERNAL_DIR, "apk_downloads", APK_NAME)
    if os.path.exists(external_path):
        return external_path
    
    # 2. 检查项目目录
    project_path = os.path.join(PROJECT_DIR, "apk_downloads", APK_NAME)
    if os.path.exists(project_path):
        return project_path
    
    # 3. 检查.location文件
    location_file = project_path + ".location"
    if os.path.exists(location_file):
        with open(location_file, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                actual_path = lines[1].strip()
                if os.path.exists(actual_path):
                    return actual_path
    
    return None

APK_PATH = get_apk_path()
OUTPUT_DIR = os.path.join(os.path.dirname(APK_PATH) if APK_PATH else EXTERNAL_DIR, "miniworld_cn_decompiled")
TOOLS_DIR = os.path.join(PROJECT_DIR, "tools")
APKTOOL_PATH = os.path.join(TOOLS_DIR, "apktool.jar")
JADX_PATH = os.path.join(TOOLS_DIR, "jadx", "bin", "jadx.bat")
JADX_GUI_PATH = os.path.join(TOOLS_DIR, "jadx", "bin", "jadx-gui.bat")"

def check_apk():
    """检查APK文件是否存在"""
    print("="*70)
    print(f"[检查] APK文件")
    print("="*70)
    
    if os.path.exists(APK_PATH):
        size = os.path.getsize(APK_PATH) / 1024 / 1024 / 1024
        print(f"✓ 找到APK文件")
        print(f"  路径: {APK_PATH}")
        print(f"  大小: {size:.2f} GB")
        return True
    else:
        print(f"✗ APK文件不存在: {APK_PATH}")
        return False

def check_tools():
    """检查工具是否存在"""
    print("\n[检查] 反编译工具")
    
    tools_ok = True
    
    if os.path.exists(APKTOOL_PATH):
        print(f"✓ apktool: {APKTOOL_PATH}")
    else:
        print(f"✗ apktool未找到")
        tools_ok = False
    
    if os.path.exists(JADX_PATH):
        print(f"✓ jadx: {JADX_PATH}")
    else:
        print(f"✗ jadx未找到")
        tools_ok = False
    
    return tools_ok

def decompile_apktool():
    """使用apktool反编译"""
    print("\n" + "="*70)
    print("[步骤1] 使用apktool反编译")
    print("="*70)
    
    # 清理旧目录
    if os.path.exists(OUTPUT_DIR):
        print(f"[清理] 删除旧目录: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    
    # 执行反编译
    cmd = [
        "java", "-jar", APKTOOL_PATH,
        "d", APK_PATH,
        "-o", OUTPUT_DIR,
        "-f"
    ]
    
    print(f"[执行] {' '.join(cmd)}")
    print("[提示] 这可能需要几分钟时间，请耐心等待...")
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, timeout=600)
        
        if result.returncode == 0:
            print("\n✓ apktool反编译成功")
            return True
        else:
            print(f"\n✗ apktool失败，返回码: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n✗ 反编译超时（超过10分钟）")
        return False
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        return False

def decompile_jadx():
    """使用jadx反编译"""
    print("\n" + "="*70)
    print("[步骤2] 使用jadx反编译")
    print("="*70)
    
    sources_dir = os.path.join(OUTPUT_DIR, "jadx_sources")
    
    # 清理旧目录
    if os.path.exists(sources_dir):
        print(f"[清理] 删除旧目录: {sources_dir}")
        shutil.rmtree(sources_dir)
    
    # 执行反编译
    cmd = [
        JADX_PATH,
        "-d", sources_dir,
        "--show-bad-code",
        "--no-res",
        APK_PATH
    ]
    
    print(f"[执行] {' '.join(cmd[:5])} ...")
    print("[提示] 这可能需要较长时间，请耐心等待...")
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, timeout=1200)
        
        # jadx即使返回非零也可能成功生成部分代码
        if os.path.exists(sources_dir) and len(os.listdir(sources_dir)) > 0:
            print("\n✓ jadx反编译完成")
            print(f"  源代码目录: {sources_dir}")
            return True
        else:
            print("\n✗ jadx未生成源代码")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n✗ 反编译超时（超过20分钟）")
        return False
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        return False

def analyze_structure():
    """分析反编译后的目录结构"""
    print("\n" + "="*70)
    print("[步骤3] 分析目录结构")
    print("="*70)
    
    if not os.path.exists(OUTPUT_DIR):
        print("✗ 反编译目录不存在")
        return
    
    # 统计文件
    total_files = 0
    smali_files = 0
    for root, dirs, files in os.walk(OUTPUT_DIR):
        total_files += len(files)
        if 'smali' in root:
            smali_files += len(files)
    
    print(f"总文件数: {total_files}")
    print(f"smali文件数: {smali_files}")
    
    # 显示关键目录
    key_dirs = [
        "AndroidManifest.xml",
        "smali",
        "smali_classes2",
        "smali_classes3",
        "lib",
        "assets"
    ]
    
    print("\n[关键目录/文件]")
    for item in key_dirs:
        path = os.path.join(OUTPUT_DIR, item)
        if os.path.exists(path):
            if os.path.isdir(path):
                count = len(os.listdir(path))
                print(f"  ✓ {item}/ ({count} 项)")
            else:
                size = os.path.getsize(path) / 1024
                print(f"  ✓ {item} ({size:.1f} KB)")
        else:
            print(f"  ✗ {item}")

def search_key_files():
    """搜索关键文件"""
    print("\n" + "="*70)
    print("[步骤4] 搜索关键协议文件")
    print("="*70)
    
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
        print("✗ smali目录不存在")
        return
    
    print("[搜索关键词]")
    for keyword, desc in keywords:
        # 简单统计包含关键词的文件数
        count = 0
        for root, dirs, files in os.walk(smali_dir):
            for file in files:
                if keyword.lower() in file.lower():
                    count += 1
        
        if count > 0:
            print(f"  {desc} ({keyword}): {count} 个文件")

def main():
    """主函数"""
    print("="*70)
    print("迷你世界国服APK反编译工具")
    print("="*70)
    
    # 检查
    if not check_apk():
        print("\n✗ 请确保APK文件已下载")
        return
    
    if not check_tools():
        print("\n✗ 请确保反编译工具已安装")
        return
    
    # 询问是否继续（非交互模式自动继续）
    print("\n" + "="*70)
    print("[自动模式] 开始反编译...")
    # response = input("是否开始反编译? (y/n): ").strip().lower()
    # if response != 'y':
    #     print("已取消")
    #     return
    response = 'y'  # 自动继续
    print("="*70)
    
    # 执行反编译
    success = True
    
    if not decompile_apktool():
        success = False
    
    if not decompile_jadx():
        success = False
    
    # 分析
    analyze_structure()
    search_key_files()
    
    # 完成
    print("\n" + "="*70)
    if success:
        print("✓ 反编译完成")
        print(f"输出目录: {OUTPUT_DIR}")
        print("\n建议下一步:")
        print("1. 使用jadx GUI查看源代码")
        print(f"   {JADX_GUI_PATH} {APK_PATH}")
        print("2. 分析smali代码中的网络协议")
        print("3. 查找加密算法实现")
    else:
        print("✗ 反编译过程中有错误，请检查日志")
    print("="*70)

if __name__ == "__main__":
    main()
