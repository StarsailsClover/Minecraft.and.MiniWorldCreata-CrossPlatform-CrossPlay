#!/usr/bin/env python3
"""
组件完整性检查和修复脚本
检查大文件移动后是否有问题，并修复引用
"""

import os
import sys
import shutil
import json
from pathlib import Path

# 配置
PROJECT_DIR = r"C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay"
EXTERNAL_DIR = r"C:\Users\Sails\Documents\Coding\MnMCPResources"

# 关键文件检查列表
CRITICAL_FILES = {
    # 工具文件
    "tools": {
        "apktool.jar": {"min_size": 20*1024*1024, "description": "APK反编译工具"},
        "apktool.bat": {"min_size": 1000, "description": "APK工具脚本"},
        "jadx/": {"type": "dir", "description": "Java反编译器"},
        "frida-server.xz": {"min_size": 10*1024*1024, "description": "Frida服务端"},
    },
    # 服务端文件
    "server/paper": {
        "paper-1.20.6-151.jar": {"min_size": 40*1024*1024, "description": "PaperMC服务端"},
        "paper.jar": {"min_size": 40*1024*1024, "description": "PaperMC软链接"},
        "eula.txt": {"min_size": 10, "description": "EULA协议"},
        "server.properties": {"min_size": 10, "description": "服务器配置"},
    },
    "server/plugins": {
        "Geyser-Spigot.jar": {"min_size": 10*1024*1024, "description": "GeyserMC插件"},
        "floodgate-spigot.jar": {"min_size": 1*1024*1024, "description": "Floodgate插件"},
    },
    "server/fabric": {
        "fabric-installer.jar": {"min_size": 50000, "description": "Fabric安装器"},
    },
    "server/mods": {
        "fabric-api-0.98.0.jar": {"min_size": 1*1024*1024, "description": "Fabric API"},
    },
}

def check_file_exists(filepath, min_size=0, file_type="file"):
    """检查文件是否存在且满足最小大小"""
    full_path = os.path.join(PROJECT_DIR, filepath)
    
    if file_type == "dir":
        return os.path.isdir(full_path)
    
    if not os.path.exists(full_path):
        return False
    
    if os.path.getsize(full_path) < min_size:
        return False
    
    return True

def scan_all_files():
    """扫描所有文件"""
    print("="*70)
    print("扫描项目文件完整性")
    print("="*70)
    
    issues = []
    warnings = []
    
    for category, files in CRITICAL_FILES.items():
        print(f"\n[检查] {category}")
        for filename, info in files.items():
            filepath = os.path.join(category, filename)
            file_type = info.get("type", "file")
            min_size = info.get("min_size", 0)
            description = info.get("description", "")
            
            if check_file_exists(filepath, min_size, file_type):
                print(f"  ✓ {filename} ({description})")
            else:
                print(f"  ✗ {filename} 缺失或损坏 ({description})")
                issues.append({
                    "filepath": filepath,
                    "description": description,
                    "category": category
                })
    
    return issues, warnings

def check_large_files():
    """检查大文件是否被错误移动"""
    print("\n" + "="*70)
    print("检查大文件位置")
    print("="*70)
    
    large_files_issues = []
    
    # 检查项目目录中是否还有超过100MB的文件
    for root, dirs, files in os.walk(PROJECT_DIR):
        # 跳过.git目录
        if '.git' in root:
            continue
        
        for file in files:
            filepath = os.path.join(root, file)
            try:
                size = os.path.getsize(filepath)
                if size > 100 * 1024 * 1024:  # 100MB
                    rel_path = os.path.relpath(filepath, PROJECT_DIR)
                    print(f"  ⚠ 发现大文件: {rel_path} ({size/1024/1024:.2f} MB)")
                    large_files_issues.append({
                        "filepath": filepath,
                        "rel_path": rel_path,
                        "size": size
                    })
            except:
                pass
    
    if not large_files_issues:
        print("  ✓ 项目目录中没有超过100MB的文件")
    
    return large_files_issues

def check_external_references():
    """检查外部引用是否正确"""
    print("\n" + "="*70)
    print("检查外部资源引用")
    print("="*70)
    
    issues = []
    
    # 检查APK位置文件
    apk_location_file = os.path.join(PROJECT_DIR, "apk_downloads", "miniworld_cn_1.53.1.apk.location")
    if os.path.exists(apk_location_file):
        with open(apk_location_file, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                actual_path = lines[1].strip()
                if os.path.exists(actual_path):
                    print(f"  ✓ APK位置文件正确指向: {actual_path}")
                else:
                    print(f"  ✗ APK位置文件指向的路径不存在: {actual_path}")
                    issues.append({"type": "apk_location", "path": actual_path})
    else:
        print(f"  ✗ APK位置文件不存在")
        issues.append({"type": "apk_location_missing", "file": apk_location_file})
    
    return issues

def check_script_references():
    """检查脚本中的路径引用"""
    print("\n" + "="*70)
    print("检查脚本路径引用")
    print("="*70)
    
    issues = []
    
    # 需要检查的脚本
    scripts_to_check = [
        "apk_downloads/decompile_miniworld_cn.py",
        "apk_downloads/decompile_apk.py",
        "server/download_paper.py",
    ]
    
    for script in scripts_to_check:
        script_path = os.path.join(PROJECT_DIR, script)
        if os.path.exists(script_path):
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # 检查是否使用了硬编码的绝对路径
            if "C:\\Users\\Sails\\Documents\\Coding\\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay" in content:
                print(f"  ⚠ {script} 包含硬编码路径")
                issues.append({"script": script, "issue": "hardcoded_path"})
            else:
                print(f"  ✓ {script} 路径引用正常")
    
    return issues

def fix_component_references():
    """修复组件引用"""
    print("\n" + "="*70)
    print("修复组件引用")
    print("="*70)
    
    fixes = []
    
    # 1. 确保外部目录结构完整
    external_dirs = ["server", "tools", "apk_downloads"]
    for dir_name in external_dirs:
        full_path = os.path.join(EXTERNAL_DIR, dir_name)
        if not os.path.exists(full_path):
            os.makedirs(full_path, exist_ok=True)
            print(f"  ✓ 创建外部目录: {full_path}")
            fixes.append(f"创建目录: {dir_name}")
    
    # 2. 创建组件清单文件
    manifest = {
        "project_name": "Minecraft-MiniWorld Protocol Bridge",
        "external_resources_dir": EXTERNAL_DIR,
        "components": {
            "tools": {
                "location": "项目目录/tools",
                "description": "逆向工程工具",
                "files": ["apktool.jar", "apktool.bat", "jadx/", "frida-server.xz"]
            },
            "server": {
                "location": "项目目录/server",
                "description": "Minecraft服务端",
                "files": ["paper/", "plugins/", "fabric/", "mods/"]
            },
            "apks": {
                "location": "外部目录/apk_downloads",
                "description": "APK文件（大文件）",
                "files": ["miniworld_cn_1.53.1.apk"]
            }
        },
        "notes": [
            "超过100MB的文件存储在外部目录",
            "使用.location文件记录实际位置",
            "Git提交时不会包含大文件"
        ]
    }
    
    manifest_path = os.path.join(PROJECT_DIR, "COMPONENT_MANIFEST.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ 创建组件清单: {manifest_path}")
    fixes.append("创建组件清单文件")
    
    # 3. 更新.gitignore（如果不存在）
    gitignore_path = os.path.join(PROJECT_DIR, ".gitignore")
    gitignore_content = """# 大文件目录
MnMCPResources/

# APK文件
*.apk

# 反编译输出（可选）
*_decompiled/

# 日志文件
*.log

# Python缓存
__pycache__/
*.pyc
*.pyo

# IDE
.vscode/
.idea/

# 临时文件
*.tmp
*.temp
"""
    
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print(f"  ✓ 创建.gitignore: {gitignore_path}")
        fixes.append("创建.gitignore")
    
    return fixes

def create_path_resolver():
    """创建路径解析工具"""
    print("\n" + "="*70)
    print("创建路径解析工具")
    print("="*70)
    
    resolver_code = '''#!/usr/bin/env python3
"""
路径解析工具
统一处理项目文件路径，支持外部资源目录
"""

import os
import sys

# 项目根目录
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTERNAL_DIR = r"C:\\Users\\Sails\\Documents\\Coding\\MnMCPResources"

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
JADX_BIN = get_tool_path(r"jadx\\bin\\jadx.bat")
JADX_GUI_BIN = get_tool_path(r"jadx\\bin\\jadx-gui.bat")
PAPER_JAR = get_server_path(r"paper\\paper.jar")
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
'''
    
    resolver_path = os.path.join(PROJECT_DIR, "path_resolver.py")
    with open(resolver_path, 'w', encoding='utf-8') as f:
        f.write(resolver_code)
    
    print(f"  ✓ 创建路径解析工具: {resolver_path}")
    return resolver_path

def main():
    """主函数"""
    print("="*70)
    print("组件完整性检查和修复")
    print("="*70)
    
    # 1. 扫描关键文件
    issues, warnings = scan_all_files()
    
    # 2. 检查大文件位置
    large_issues = check_large_files()
    
    # 3. 检查外部引用
    external_issues = check_external_references()
    
    # 4. 检查脚本引用
    script_issues = check_script_references()
    
    # 5. 显示问题汇总
    print("\n" + "="*70)
    print("问题汇总")
    print("="*70)
    
    all_issues = issues + large_issues + external_issues + script_issues
    
    if not all_issues:
        print("✓ 未发现严重问题")
    else:
        print(f"发现 {len(all_issues)} 个问题:")
        for issue in all_issues:
            print(f"  - {issue}")
    
    # 6. 修复问题
    print("\n" + "="*70)
    print("执行修复")
    print("="*70)
    
    fixes = fix_component_references()
    resolver_path = create_path_resolver()
    
    # 7. 显示修复结果
    print("\n" + "="*70)
    print("修复完成")
    print("="*70)
    
    if fixes:
        print(f"执行了 {len(fixes)} 项修复:")
        for fix in fixes:
            print(f"  ✓ {fix}")
    
    print(f"\n✓ 创建路径解析工具: {resolver_path}")
    
    # 8. 建议
    print("\n" + "="*70)
    print("建议")
    print("="*70)
    print("1. 所有脚本应使用 path_resolver.py 中的函数获取路径")
    print("2. 大文件(>100MB)应存储在外部目录 MnMCPResources/")
    print("3. 提交到GitHub时不会包含大文件和外部目录")
    print("4. 新成员克隆项目后需要手动下载大文件或从外部目录复制")
    
    print("\n✓ 检查和修复完成")

if __name__ == "__main__":
    main()
