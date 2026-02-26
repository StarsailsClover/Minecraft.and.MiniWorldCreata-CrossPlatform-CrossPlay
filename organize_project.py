#!/usr/bin/env python3
"""
整理项目文件夹结构
将不需要上传到Github的文件移到外部资源文件夹
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

# 路径配置
PROJECT_DIR = Path(r"C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay")
RESOURCES_DIR = Path(r"C:\Users\Sails\Documents\Coding\MnMCPResources")
BACKUP_DIR = RESOURCES_DIR / "Buckup" / "Step_1.8.1"
RESOURCES_NEW = RESOURCES_DIR / "Resources"
BACKUP_DOCS = RESOURCES_DIR / "backupdocs"

def create_directories():
    """创建必要的目录结构"""
    print("[*] 创建目录结构...")
    
    dirs = [
        BACKUP_DIR,
        BACKUP_DOCS,
        RESOURCES_NEW / "apks",
        RESOURCES_NEW / "pc_versions",
        RESOURCES_NEW / "decompiled",
        RESOURCES_NEW / "captures",
        RESOURCES_NEW / "tools",
        RESOURCES_NEW / "libs",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  [+] {d}")
    
    return True

def backup_current_version():
    """备份当前版本到Buckup/Step_1.8.1"""
    print("\n[*] 备份当前版本到 Buckup/Step_1.8.1...")
    
    # 备份关键文件
    files_to_backup = [
        "src",
        "docs",
        "tools",
        "README.md",
        "PROJECT_OVERVIEW.md",
        "ToDo.md",
        "TechnicalDocument.md",
    ]
    
    for item in files_to_backup:
        src = PROJECT_DIR / item
        dst = BACKUP_DIR / item
        
        if src.exists():
            if src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"  [+] 备份目录: {item}")
            else:
                shutil.copy2(src, dst)
                print(f"  [+] 备份文件: {item}")
    
    print(f"[+] 备份完成: {BACKUP_DIR}")
    return True

def move_session_files():
    """移动SESSION文件到backupdocs"""
    print("\n[*] 移动SESSION文件到 backupdocs...")
    
    session_files = list(PROJECT_DIR.glob("SESSION_*.md"))
    
    for f in session_files:
        dst = BACKUP_DOCS / f.name
        shutil.move(str(f), str(dst))
        print(f"  [+] 移动: {f.name}")
    
    return True

def move_large_files():
    """移动大文件到Resources"""
    print("\n[*] 移动大文件到 Resources...")
    
    # 移动APK文件
    apk_files = [
        RESOURCES_DIR / "packs_downloads" / "miniworldMini-wp.apk",
        RESOURCES_DIR / "packs_downloads" / "miniworld_en_1.7.15.apk",
    ]
    
    for apk in apk_files:
        if apk.exists():
            dst = RESOURCES_NEW / "apks" / apk.name
            shutil.move(str(apk), str(dst))
            print(f"  [+] 移动APK: {apk.name}")
    
    # 移动PC版本
    pc_dirs = [
        RESOURCES_DIR / "packs_downloads" / "miniworldPC_CN",
        RESOURCES_DIR / "packs_downloads" / "miniworldPC_Global",
    ]
    
    for pc_dir in pc_dirs:
        if pc_dir.exists():
            dst = RESOURCES_NEW / "pc_versions" / pc_dir.name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.move(str(pc_dir), str(dst))
            print(f"  [+] 移动PC版: {pc_dir.name}")
    
    # 移动抓包文件
    captures_dir = RESOURCES_DIR / "packs_downloads" / "captures"
    if captures_dir.exists():
        dst = RESOURCES_NEW / "captures"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.move(str(captures_dir), str(dst))
        print(f"  [+] 移动抓包文件")
    
    # 移动DEX文件
    dex_dir = RESOURCES_DIR / "packs_downloads" / "dumped_dex"
    if dex_dir.exists():
        dst = RESOURCES_NEW / "decompiled" / "android_dex"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.move(str(dex_dir), str(dst))
        print(f"  [+] 移动DEX文件")
    
    return True

def clean_packs_downloads():
    """清理packs_downloads目录"""
    print("\n[*] 清理packs_downloads目录...")
    
    packs_dir = RESOURCES_DIR / "packs_downloads"
    
    if packs_dir.exists():
        # 保留目录但清空内容
        for item in packs_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        print(f"  [+] 清理完成: {packs_dir}")
    
    return True

def update_project_structure():
    """更新项目结构文档"""
    print("\n[*] 更新项目结构...")
    
    structure = {
        "version": "1.8.2",
        "date": datetime.now().isoformat(),
        "github_repo": {
            "src": "核心源代码",
            "docs": "文档",
            "tools": "工具脚本",
            "tests": "测试",
            "config": "配置文件",
        },
        "external_resources": {
            "apks": "APK文件",
            "pc_versions": "PC版游戏",
            "decompiled": "反编译输出",
            "captures": "抓包数据",
            "tools": "外部工具",
            "libs": "依赖库",
        },
        "backup": {
            "Buckup": "版本备份",
            "backupdocs": "会话记录",
        }
    }
    
    structure_file = PROJECT_DIR / "PROJECT_STRUCTURE.json"
    with open(structure_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    print(f"  [+] 结构文档: {structure_file}")
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("项目文件夹整理工具")
    print("=" * 60)
    print(f"\n项目目录: {PROJECT_DIR}")
    print(f"资源目录: {RESOURCES_DIR}")
    print(f"备份版本: Step 1.8.1")
    
    # 执行整理
    create_directories()
    backup_current_version()
    move_session_files()
    move_large_files()
    clean_packs_downloads()
    update_project_structure()
    
    print("\n" + "=" * 60)
    print("整理完成!")
    print("=" * 60)
    print(f"\n备份位置: {BACKUP_DIR}")
    print(f"资源位置: {RESOURCES_NEW}")
    print(f"文档备份: {BACKUP_DOCS}")
    
    return True

if __name__ == "__main__":
    main()
