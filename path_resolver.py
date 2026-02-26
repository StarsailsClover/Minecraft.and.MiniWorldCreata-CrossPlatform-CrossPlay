#!/usr/bin/env python3
"""
路径解析工具
统一处理项目文件路径，支持外部资源目录
"""

import os
import sys

# 项目根目录
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTERNAL_DIR = r"C:\Users\Sails\Documents\Coding\MnMCPResources"

def resolve_path(rel_path):
    """
    解析文件路径
    优先检查项目目录，如果不存在则检查外部目录
    对于大文件，检查.location文件
    """
    # 1. 检查项目目录
    project_path = os.path.join(PROJECT_DIR, rel_path)
    if os.path.exists(project_path):
        return project_path
    
    # 2. 检查.location文件
    location_file = project_path + ".location"
    if os.path.exists(location_file):
        with open(location_file, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                actual_path = lines[1].strip()
                if os.path.exists(actual_path):
                    return actual_path
    
    # 3. 检查外部目录
    external_path = os.path.join(EXTERNAL_DIR, rel_path)
    if os.path.exists(external_path):
        return external_path
    
    # 4. 返回项目目录路径（即使不存在）
    return project_path

def get_apk_path(apk_name):
    """获取APK文件路径"""
    # 优先检查外部目录
    external_apk = os.path.join(EXTERNAL_DIR, "apk_downloads", apk_name)
    if os.path.exists(external_apk):
        return external_apk
    
    # 检查项目目录
    project_apk = os.path.join(PROJECT_DIR, "apk_downloads", apk_name)
    if os.path.exists(project_apk):
        return project_apk
    
    # 检查.location文件
    location_file = project_apk + ".location"
    if os.path.exists(location_file):
        with open(location_file, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                return lines[1].strip()
    
    return None

def get_tool_path(tool_name):
    """获取工具路径"""
    return os.path.join(PROJECT_DIR, "tools", tool_name)

def get_server_path(server_file):
    """获取服务端文件路径"""
    return os.path.join(PROJECT_DIR, "server", server_file)

# 便捷函数
APKTOOL_JAR = get_tool_path("apktool.jar")
JADX_BIN = get_tool_path(r"jadx\bin\jadx.bat")
JADX_GUI_BIN = get_tool_path(r"jadx\bin\jadx-gui.bat")
PAPER_JAR = get_server_path(r"paper\paper.jar")
MINIWORLD_CN_APK = get_apk_path("miniworld_cn_1.53.1.apk")

if __name__ == "__main__":
    print("路径解析工具")
    print(f"项目目录: {PROJECT_DIR}")
    print(f"外部目录: {EXTERNAL_DIR}")
    print()
    print("关键路径:")
    print(f"  apktool: {APKTOOL_JAR}")
    print(f"  jadx: {JADX_BIN}")
    print(f"  paper: {PAPER_JAR}")
    print(f"  miniworld_cn_apk: {MINIWORLD_CN_APK}")
