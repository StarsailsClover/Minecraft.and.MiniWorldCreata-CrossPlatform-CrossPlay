#!/usr/bin/env python3
"""DEX处理修复版 - 修复了路径指向MnMCPResources的问题"""
import os
import json
import re
from pathlib import Path
from datetime import datetime

CODING_DIR = Path("C:/Users/Sails/Documents/Coding")
EXTERNAL_DIR = CODING_DIR / "MnMCPResources"
DEX_DIR = EXTERNAL_DIR / "packs_downloads" / "dumped_dex"
ANALYSIS_DIR = EXTERNAL_DIR / "Resources" / "analysis" / "dex_final"

def check_dex():
    print("="*60)
    print("DEX处理工具 v2 - 路径修复")
    print("="*60)
    print(f"[*] DEX目录: {DEX_DIR}")
    
    if not DEX_DIR.exists():
        print(f"[-] 目录不存在")
        return None
    
    dex_files = list(DEX_DIR.glob("*.dex"))
    if dex_files:
        print(f"[+] 找到 {len(dex_files)} 个DEX文件")
        for f in dex_files[:5]:
            size = f.stat().st_size / (1024*1024)
            print(f"    - {f.name}: {size:.2f} MB")
    else:
        print(f"[-] 未找到DEX文件")
    
    return dex_files

def extract_block_ids():
    """从DEX反编译源码中提取方块ID"""
    java_sources = DEX_DIR / "java_sources"
    if not java_sources.exists():
        print(f"[-] 源码目录不存在: {java_sources}")
        return {}
    
    print(f"\n[*] 分析反编译源码...")
    block_ids = {}
    pattern = r'public\s+static\s+final\s+int\s+(\w+)\s*=\s*(\d+)'
    
    java_files = list(java_sources.rglob("*.java"))
    print(f"[*] 共找到 {len(java_files)} 个Java文件")
    
    for java_file in java_files[:200]:  # 限制数量
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')[:5000]
            filename = java_file.name.lower()
            
            # 检查是否是方块相关文件
            if 'block' in content.lower() or 'block' in filename:
                matches = re.findall(pattern, content)
                for name, val in matches:
                    if 'block' in name.lower() and not name.startswith('_'):
                        try:
                            block_ids[name] = int(val)
                        except:
                            pass
        except:
            continue
    
    return block_ids

def generate_block_mapping():
    """生成方块映射模板"""
    mc_blocks = [
        (0, "minecraft:air", "空气"),
        (1, "minecraft:stone", "石头"),
        (2, "minecraft:grass_block", "草方块"),
        (3, "minecraft:dirt", "泥土"),
        (4, "minecraft:cobblestone", "圆石"),
        (5, "minecraft:oak_planks", "橡木木板"),
        (7, "minecraft:bedrock", "基岩"),
        (12, "minecraft:sand", "沙子"),
        (13, "minecraft:gravel", "砾石"),
        (14, "minecraft:gold_ore", "金矿石"),
        (15, "minecraft:iron_ore", "铁矿石"),
        (16, "minecraft:coal_ore", "煤矿石"),
        (17, "minecraft:oak_log", "橡木原木"),
        (18, "minecraft:oak_leaves", "橡树树叶"),
        (20, "minecraft:glass", "玻璃"),
    ]
    
    mapping = {
        "version": "1.0",
        "mc_version": "1.20.6",
        "mnw_version": "1.53.1",
        "generated": datetime.now().isoformat(),
        "blocks": []
    }
    
    for mc_id, mc_name, zh_name in mc_blocks:
        mapping["blocks"].append({
            "mc_id": mc_id,
            "mc_name": mc_name,
            "mc_zh_name": zh_name,
            "mnw_id": None,
            "mnw_name": None
        })
    
    return mapping

def main():
    print("\nMnMCP DEX处理工具 v2\n")
    
    # 检查DEX文件
    dex_files = check_dex()
    
    # 提取方块ID
    block_ids = extract_block_ids()
    print(f"[+] 找到 {len(block_ids)} 个方块ID定义")
    
    # 生成映射模板
    mapping = generate_block_mapping()
    
    # 保存结果
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    if block_ids:
        with open(ANALYSIS_DIR / "extracted_block_ids.json", 'w', encoding='utf-8') as f:
            json.dump(block_ids, f, indent=2, ensure_ascii=False)
    
    with open(ANALYSIS_DIR / "block_mapping_template.json", 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print("处理完成!")
    print(f"{'='*60}")
    print(f"[*] 结果保存到: {ANALYSIS_DIR}")

if __name__ == "__main__":
    main()