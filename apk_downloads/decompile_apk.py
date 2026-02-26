#!/usr/bin/env python3
"""
APK反编译脚本
自动使用apktool和jadx反编译APK文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# 动态获取路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
EXTERNAL_DIR = os.path.join(os.path.dirname(PROJECT_DIR), "MnMCPResources")

# 配置
TOOLS_DIR = os.path.join(PROJECT_DIR, "tools")
APKTOOL_PATH = os.path.join(TOOLS_DIR, "apktool.jar")
JADX_PATH = os.path.join(TOOLS_DIR, "jadx", "bin", "jadx.bat")
JADX_GUI_PATH = os.path.join(TOOLS_DIR, "jadx", "bin", "jadx-gui.bat")

# APK文件列表（支持外部目录）
APK_FILES = {
    "miniworld_cn": {
        "filename": "miniworld_cn_1.53.1.apk",
        "output_dir": "miniworld_cn_decompiled",
        "description": "迷你世界国服",
        "external": True  # 标记为外部存储
    },
    "miniworld_en": {
        "filename": "miniworld_en_1.7.15.apk",
        "output_dir": "miniworld_en_decompiled",
        "description": "MiniWorld: Creata外服",
        "external": True
    },
    "minecraft_bedrock": {
        "filename": "minecraft_bedrock_1.20.60.apk",
        "output_dir": "mc_bedrock_decompiled",
        "description": "Minecraft基岩版",
        "external": True
    }
}

def get_apk_path(filename):
    """获取APK路径，优先外部目录"""
    # 1. 检查外部目录
    external_path = os.path.join(EXTERNAL_DIR, "apk_downloads", filename)
    if os.path.exists(external_path):
        return external_path
    
    # 2. 检查项目目录
    project_path = os.path.join(SCRIPT_DIR, filename)
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

def get_output_dir(output_name):
    """获取输出目录，优先外部目录"""
    external_output = os.path.join(EXTERNAL_DIR, "apk_downloads", output_name)
    return external_output"

# APK文件列表
APK_FILES = {
    "miniworld_cn": {
        "filename": "miniworld_cn_1.53.1.apk",
        "output_dir": "miniworld_cn_decompiled",
        "description": "迷你世界国服"
    },
    "miniworld_en": {
        "filename": "miniworld_en_1.7.15.apk",
        "output_dir": "miniworld_en_decompiled",
        "description": "MiniWorld: Creata外服"
    },
    "minecraft_bedrock": {
        "filename": "minecraft_bedrock_1.20.60.apk",
        "output_dir": "mc_bedrock_decompiled",
        "description": "Minecraft基岩版"
    }
}

def check_tools():
    """检查工具是否存在"""
    tools_ok = True
    
    print("[检查] 验证反编译工具...")
    
    if not os.path.exists(APKTOOL_PATH):
        print(f"[错误] 未找到 apktool: {APKTOOL_PATH}")
        tools_ok = False
    else:
        print(f"[OK] apktool: {APKTOOL_PATH}")
    
    if not os.path.exists(JADX_PATH):
        print(f"[错误] 未找到 jadx: {JADX_PATH}")
        tools_ok = False
    else:
        print(f"[OK] jadx: {JADX_PATH}")
    
    return tools_ok

def decompile_with_apktool(apk_path, output_dir):
    """使用apktool反编译APK"""
    print(f"\n[反编译] 使用apktool...")
    print(f"  APK: {apk_path}")
    print(f"  输出: {output_dir}")
    
    # 清理旧目录
    if os.path.exists(output_dir):
        print(f"[清理] 删除旧目录: {output_dir}")
        shutil.rmtree(output_dir)
    
    # 执行反编译
    cmd = [
        "java", "-jar", APKTOOL_PATH,
        "d", apk_path,
        "-o", output_dir,
        "-f"  # 强制覆盖
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"[成功] apktool反编译完成")
            return True
        else:
            print(f"[错误] apktool失败:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[错误] 反编译超时")
        return False
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False

def decompile_with_jadx(apk_path, output_dir):
    """使用jadx反编译APK"""
    print(f"\n[反编译] 使用jadx...")
    print(f"  APK: {apk_path}")
    
    sources_dir = os.path.join(output_dir, "jadx_sources")
    
    # 清理旧目录
    if os.path.exists(sources_dir):
        print(f"[清理] 删除旧目录: {sources_dir}")
        shutil.rmtree(sources_dir)
    
    # 执行反编译
    cmd = [
        JADX_PATH,
        "-d", sources_dir,
        "--show-bad-code",
        "--no-res",  # 不反编译资源（apktool已处理）
        apk_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"[成功] jadx反编译完成")
            print(f"  源代码目录: {sources_dir}")
            return True
        else:
            print(f"[警告] jadx可能有错误，但继续处理")
            print(result.stderr[:500])  # 只显示前500字符
            return True  # jadx即使出错也会生成部分代码
            
    except subprocess.TimeoutExpired:
        print(f"[错误] 反编译超时")
        return False
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False

def open_with_jadx_gui(apk_path):
    """使用jadx GUI打开APK"""
    print(f"\n[启动] jadx GUI...")
    print(f"  APK: {apk_path}")
    
    cmd = [JADX_GUI_PATH, apk_path]
    
    try:
        # 非阻塞启动
        subprocess.Popen(cmd)
        print(f"[成功] jadx GUI已启动")
        return True
    except Exception as e:
        print(f"[错误] 启动失败: {str(e)}")
        return False

def analyze_apk(apk_key, open_gui=False):
    """分析单个APK"""
    if apk_key not in APK_FILES:
        print(f"[错误] 未知的APK: {apk_key}")
        return False
    
    apk_info = APK_FILES[apk_key]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    apk_path = os.path.join(script_dir, apk_info["filename"])
    output_dir = os.path.join(script_dir, apk_info["output_dir"])
    
    print(f"\n{'='*70}")
    print(f"[任务] 反编译 {apk_info['description']}")
    print(f"{'='*70}")
    
    # 检查APK是否存在
    if not os.path.exists(apk_path):
        print(f"[错误] APK文件不存在: {apk_path}")
        print(f"[提示] 请先下载APK文件，参考 MANUAL_DOWNLOAD_GUIDE.md")
        return False
    
    file_size = os.path.getsize(apk_path) / 1024 / 1024
    print(f"[信息] APK大小: {file_size:.2f} MB")
    
    # 反编译
    success = True
    
    # 1. 使用apktool
    if not decompile_with_apktool(apk_path, output_dir):
        success = False
    
    # 2. 使用jadx
    if not decompile_with_jadx(apk_path, output_dir):
        success = False
    
    # 3. 可选：打开GUI
    if open_gui:
        open_with_jadx_gui(apk_path)
    
    return success

def show_analysis_targets():
    """显示分析目标"""
    print("\n[反编译目标]")
    for key, info in APK_FILES.items():
        apk_path = info["filename"]
        exists = "✅ 已下载" if os.path.exists(apk_path) else "❌ 未下载"
        print(f"  {key}: {info['description']}")
        print(f"    文件: {apk_path} {exists}")
        print(f"    输出: {info['output_dir']}/")

def main():
    """主函数"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("="*70)
    print("APK反编译工具")
    print("用于Minecraft与迷你世界协议逆向工程")
    print("="*70)
    
    # 检查工具
    if not check_tools():
        print("\n[错误] 工具检查失败，请确认tools目录已正确配置")
        return
    
    # 显示目标
    show_analysis_targets()
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='APK反编译工具')
    parser.add_argument('target', nargs='?', choices=list(APK_FILES.keys()) + ['all'], 
                       help='要反编译的APK (miniworld_cn/miniworld_en/minecraft_bedrock/all)')
    parser.add_argument('--gui', action='store_true', help='使用jadx GUI打开')
    parser.add_argument('--list', action='store_true', help='列出可用目标')
    
    args = parser.parse_args()
    
    if args.list:
        return
    
    if not args.target:
        # 交互式选择
        print("\n[选择要反编译的APK]")
        print("1. miniworld_cn - 迷你世界国服")
        print("2. miniworld_en - MiniWorld: Creata外服")
        print("3. minecraft_bedrock - Minecraft基岩版")
        print("4. all - 全部")
        print("0. 退出")
        
        choice = input("\n请输入数字 (0-4): ").strip()
        
        if choice == '0':
            return
        elif choice == '1':
            args.target = 'miniworld_cn'
        elif choice == '2':
            args.target = 'miniworld_en'
        elif choice == '3':
            args.target = 'minecraft_bedrock'
        elif choice == '4':
            args.target = 'all'
        else:
            print("[错误] 无效选择")
            return
    
    # 执行反编译
    results = {}
    
    if args.target == 'all':
        for key in APK_FILES:
            results[key] = analyze_apk(key, args.gui)
    else:
        results[args.target] = analyze_apk(args.target, args.gui)
    
    # 显示结果
    print("\n" + "="*70)
    print("[反编译结果汇总]")
    print("="*70)
    for key, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {APK_FILES[key]['description']}: {status}")
    
    print("\n[提示]")
    print("- 反编译后的文件位于对应的 _decompiled 目录")
    print("- 使用jadx GUI查看源代码: ..\\tools\\jadx\\bin\\jadx-gui.bat <apk文件>")
    print("- 分析smali代码: 查看 decompiled/smali/ 目录")
    print("- 查看资源文件: 查看 decompiled/res/ 目录")

if __name__ == "__main__":
    main()
