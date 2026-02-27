#!/usr/bin/env python3
"""
外部资源库打包工具
将 MnMCPResources 打包供用户二次开发使用
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
RESOURCES_DIR = Path("C:/Users/Sails/Documents/Coding/MnMCPResources")
OUTPUT_DIR = PROJECT_ROOT / "releases"

# 需要打包的资源列表
RESOURCE_MANIFEST = {
    "name": "MnMCPResources",
    "version": "1.0.0",
    "description": "MnMCP项目外部资源库",
    "contents": {
        "analysis": {
            "description": "分析结果数据",
            "files": [
                "Resources/analysis/dex_analysis/",
                "Resources/analysis/pcap_analysis/"
            ]
        },
        "decompiled": {
            "description": "反编译结果",
            "files": [
                "Resources/decompiled/"
            ]
        },
        "backups": {
            "description": "项目备份",
            "files": [
                "Buckup/Step_1.8.1/"
            ]
        },
        "documentation": {
            "description": "会话文档",
            "files": [
                "backupdocs/"
            ]
        }
    },
    "excluded": [
        "*.apk",
        "*.exe",
        "*.dll",
        "packs_downloads/dumped_dex/dex/",
        "packs_downloads/dumped_dex/java_sources/"
    ]
}

def should_exclude(path: Path, exclude_patterns: list) -> bool:
    """检查是否应该排除"""
    path_str = str(path)
    for pattern in exclude_patterns:
        if pattern in path_str:
            return True
        if path.match(pattern):
            return True
    return False

def copy_resources(src: Path, dst: Path, manifest: dict) -> bool:
    """复制资源文件"""
    print(f"[*] 复制资源文件...")
    
    exclude_patterns = manifest.get("excluded", [])
    copied_count = 0
    
    for category, info in manifest.get("contents", {}).items():
        print(f"  [{category}] {info.get('description', '')}")
        
        for file_pattern in info.get("files", []):
            src_path = RESOURCES_DIR / file_pattern
            
            if not src_path.exists():
                print(f"    [!] 不存在: {file_pattern}")
                continue
            
            if src_path.is_file():
                # 复制单个文件
                if should_exclude(src_path, exclude_patterns):
                    continue
                
                dst_path = dst / file_pattern
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
                copied_count += 1
                
            elif src_path.is_dir():
                # 复制目录
                for item in src_path.rglob("*"):
                    if should_exclude(item, exclude_patterns):
                        continue
                    
                    if item.is_file():
                        rel_path = item.relative_to(RESOURCES_DIR)
                        dst_path = dst / rel_path
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dst_path)
                        copied_count += 1
    
    print(f"[+] 已复制 {copied_count} 个文件")
    return True

def create_manifest(dst: Path, manifest: dict):
    """创建清单文件"""
    manifest_file = dst / "MANIFEST.json"
    
    package_info = {
        "name": manifest.get("name"),
        "version": manifest.get("version"),
        "description": manifest.get("description"),
        "created_at": datetime.now().isoformat(),
        "contents": list(manifest.get("contents", {}).keys()),
        "usage": {
            "description": "此资源包用于MnMCP项目的二次开发",
            "note": "请勿将此资源包用于商业用途或重新分发",
            "license": "与主项目相同 (MIT)"
        }
    }
    
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(package_info, f, indent=2, ensure_ascii=False)
    
    print(f"[+] 清单文件已创建: {manifest_file}")

def create_archive(src: Path, output_file: Path) -> bool:
    """创建ZIP压缩包"""
    print(f"[*] 创建压缩包...")
    
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in src.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(src)
                    zf.write(file_path, arcname)
        
        print(f"[+] 压缩包已创建: {output_file}")
        print(f"    大小: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
        return True
        
    except Exception as e:
        print(f"[!] 创建压缩包失败: {e}")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='外部资源库打包工具')
    parser.add_argument('--output', '-o', default='MnMCPResources.zip',
                       help='输出文件名')
    parser.add_argument('--no-zip', action='store_true',
                       help='只复制文件，不创建压缩包')
    
    args = parser.parse_args()
    
    print("="*60)
    print("MnMCP 外部资源库打包工具")
    print("="*60)
    print()
    
    # 检查资源目录
    if not RESOURCES_DIR.exists():
        print(f"[!] 资源目录不存在: {RESOURCES_DIR}")
        print("[*] 请确认 MnMCPResources 路径正确")
        sys.exit(1)
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 创建临时目录
    temp_dir = OUTPUT_DIR / "temp_resources"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    
    try:
        # 复制资源
        if not copy_resources(RESOURCES_DIR, temp_dir, RESOURCE_MANIFEST):
            print("[!] 复制资源失败")
            sys.exit(1)
        
        # 创建清单
        create_manifest(temp_dir, RESOURCE_MANIFEST)
        
        if not args.no_zip:
            # 创建压缩包
            output_file = OUTPUT_DIR / args.output
            if create_archive(temp_dir, output_file):
                print()
                print("="*60)
                print("打包完成!")
                print("="*60)
                print(f"输出文件: {output_file}")
                print()
                print("使用说明:")
                print("1. 将压缩包解压到项目根目录")
                print("2. 确保目录结构为: MnMCPResources/")
                print("3. 运行 check_and_fix_components.py 验证")
            else:
                sys.exit(1)
        else:
            print()
            print(f"[+] 资源已复制到: {temp_dir}")
            print("[*] 跳过压缩步骤")
        
    finally:
        # 清理临时目录
        if temp_dir.exists() and not args.no_zip:
            shutil.rmtree(temp_dir)
            print(f"[*] 清理临时文件")

if __name__ == "__main__":
    main()