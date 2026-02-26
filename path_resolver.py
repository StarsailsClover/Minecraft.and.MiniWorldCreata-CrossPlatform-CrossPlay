#!/usr/bin/env python3
"""
路径解析工具
统一处理项目文件路径，支持外部资源目录
"""

import os
import sys
from pathlib import Path

# 项目根目录
PROJECT_DIR = Path(__file__).parent.resolve()
EXTERNAL_DIR = Path(r"C:\Users\Sails\Documents\Coding\MnMCPResources")

def resolve_path(rel_path):
    """
    解析文件路径
    优先检查项目目录，如果不存在则检查外部目录
    对于大文件，检查.location文件
    """
    # 1. 检查项目目录
    project_path = PROJECT_DIR / rel_path
    if project_path.exists():
        return str(project_path)
    
    # 2. 检查.location文件
    location_file = project_path.with_suffix(project_path.suffix + ".location")
    if location_file.exists():
        with open(location_file, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                actual_path = lines[1].strip()
                if os.path.exists(actual_path):
                    return actual_path
    
    # 3. 检查外部目录（支持新目录结构）
    # 3.1 检查 packs_downloads（新结构）
    external_path = EXTERNAL_DIR / "packs_downloads" / rel_path
    if external_path.exists():
        return str(external_path)
    
    # 3.2 检查 apk_downloads（旧结构，向后兼容）
    external_path = EXTERNAL_DIR / "apk_downloads" / rel_path
    if external_path.exists():
        return str(external_path)
    
    # 4. 返回项目目录路径（即使不存在）
    return str(project_path)

def get_apk_path(apk_name):
    """获取APK文件路径"""
    # 优先检查 packs_downloads（新结构）
    external_apk = EXTERNAL_DIR / "packs_downloads" / apk_name
    if external_apk.exists():
        return str(external_apk)
    
    # 检查 apk_downloads（旧结构）
    external_apk = EXTERNAL_DIR / "apk_downloads" / apk_name
    if external_apk.exists():
        return str(external_apk)
    
    # 检查项目目录
    project_apk = PROJECT_DIR / "apk_downloads" / apk_name
    if project_apk.exists():
        return str(project_apk)
    
    # 检查.location文件
    location_file = project_apk.with_suffix(project_apk.suffix + ".location")
    if location_file.exists():
        with open(location_file, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                return lines[1].strip()
    
    return None

def get_pc_game_path():
    """获取PC版游戏路径"""
    # 检查 packs_downloads
    pc_path = EXTERNAL_DIR / "packs_downloads" / "miniworldPC_CN"
    if pc_path.exists():
        return str(pc_path)
    
    # 检查 apk_downloads（旧结构）
    pc_path = EXTERNAL_DIR / "apk_downloads" / "miniworldPC_CN"
    if pc_path.exists():
        return str(pc_path)
    
    return None

def get_pc_executable():
    """获取PC版可执行文件路径"""
    pc_path = get_pc_game_path()
    if pc_path:
        launcher_path = Path(pc_path) / "miniworldLauncher" / "MicroMiniNew.exe"
        if launcher_path.exists():
            return str(launcher_path)
    
    # 检查安装程序
    installer = EXTERNAL_DIR / "packs_downloads" / "miniworld.exe"
    if installer.exists():
        return str(installer)
    
    return None

def get_tool_path(tool_name):
    """获取工具路径"""
    return str(PROJECT_DIR / "tools" / tool_name)

def get_server_path(server_file):
    """获取服务端文件路径"""
    return str(PROJECT_DIR / "server" / server_file)

def list_available_apks():
    """列出可用的APK文件"""
    apks = []
    
    # 检查 packs_downloads
    packs_dir = EXTERNAL_DIR / "packs_downloads"
    if packs_dir.exists():
        for f in packs_dir.iterdir():
            if f.suffix == ".apk":
                apks.append({
                    "name": f.name,
                    "path": str(f),
                    "size_mb": f.stat().st_size / 1024 / 1024,
                    "location": "packs_downloads"
                })
    
    # 检查 apk_downloads
    apk_dir = EXTERNAL_DIR / "apk_downloads"
    if apk_dir.exists():
        for f in apk_dir.iterdir():
            if f.suffix == ".apk":
                apks.append({
                    "name": f.name,
                    "path": str(f),
                    "size_mb": f.stat().st_size / 1024 / 1024,
                    "location": "apk_downloads"
                })
    
    return apks

# 便捷函数
APKTOOL_JAR = get_tool_path("apktool.jar")
JADX_BIN = get_tool_path(r"jadx\bin\jadx.bat")
JADX_GUI_BIN = get_tool_path(r"jadx\bin\jadx-gui.bat")
PAPER_JAR = get_server_path(r"paper\paper.jar")

# 动态获取APK路径
MINIWORLD_APK = get_apk_path("com.minitech.miniworld.uc.apk")
PC_GAME_PATH = get_pc_game_path()
PC_EXECUTABLE = get_pc_executable()

if __name__ == "__main__":
    print("路径解析工具")
    print(f"项目目录: {PROJECT_DIR}")
    print(f"外部目录: {EXTERNAL_DIR}")
    print()
    
    print("可用APK文件:")
    for apk in list_available_apks():
        print(f"  - {apk['name']} ({apk['size_mb']:.1f} MB) [{apk['location']}]")
    
    print()
    print("PC版游戏:")
    if PC_GAME_PATH:
        print(f"  路径: {PC_GAME_PATH}")
        print(f"  启动器: {PC_EXECUTABLE}")
    else:
        print("  未找到")
    
    print()
    print("关键路径:")
    print(f"  apktool: {APKTOOL_JAR}")
    print(f"  jadx: {JADX_BIN}")
    print(f"  paper: {PAPER_JAR}")
