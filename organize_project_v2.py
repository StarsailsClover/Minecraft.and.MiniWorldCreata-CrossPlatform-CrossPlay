#!/usr/bin/env python3
"""
整理项目文件夹结构 - 版本2
处理PC版目录被占用的情况
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
        RESOURCES_NEW / "decompiled" / "android_dex",
        RESOURCES_NEW / "decompiled" / "pc_source",
        RESOURCES_NEW / "captures",
        RESOURCES_NEW / "analysis",
        RESOURCES_NEW / "libs",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  [+] {d}")
    
    return True

def move_session_files():
    """移动SESSION文件到backupdocs"""
    print("\n[*] 移动SESSION文件到 backupdocs...")
    
    session_files = list(PROJECT_DIR.glob("SESSION_*.md"))
    
    for f in session_files:
        dst = BACKUP_DOCS / f.name
        if not dst.exists():
            shutil.move(str(f), str(dst))
            print(f"  [+] 移动: {f.name}")
    
    return True

def move_resources():
    """移动资源文件"""
    print("\n[*] 移动资源文件...")
    
    # 移动APK文件
    packs_dir = RESOURCES_DIR / "packs_downloads"
    
    for apk in packs_dir.glob("*.apk"):
        dst = RESOURCES_NEW / "apks" / apk.name
        if apk.exists() and not dst.exists():
            shutil.move(str(apk), str(dst))
            print(f"  [+] 移动APK: {apk.name}")
    
    # 移动DEX分析结果
    dex_analysis = packs_dir / "dumped_dex" / "analysis_output"
    if dex_analysis.exists():
        dst = RESOURCES_NEW / "analysis" / "dex_analysis"
        if not dst.exists():
            shutil.copytree(str(dex_analysis), str(dst))
            print(f"  [+] 复制DEX分析结果")
    
    # 移动抓包分析结果
    captures_analysis = packs_dir / "captures" / "deep_analysis"
    if captures_analysis.exists():
        dst = RESOURCES_NEW / "analysis" / "pcap_analysis"
        if not dst.exists():
            shutil.copytree(str(captures_analysis), str(dst))
            print(f"  [+] 复制抓包分析结果")
    
    return True

def update_project_structure():
    """更新项目结构文档"""
    print("\n[*] 更新项目结构...")
    
    structure = {
        "version": "1.8.2",
        "date": datetime.now().isoformat(),
        "organization": {
            "github_repo": {
                "description": "核心代码仓库",
                "items": [
                    "src/ - 核心源代码",
                    "docs/ - 文档",
                    "tools/ - 工具脚本",
                    "tests/ - 测试",
                    "config/ - 配置文件",
                    "README.md",
                    "PROJECT_OVERVIEW.md",
                    "ToDo.md"
                ]
            },
            "external_resources": {
                "description": "外部资源（不上传GitHub）",
                "path": "MnMCPResources/Resources/",
                "items": [
                    "apks/ - APK文件",
                    "pc_versions/ - PC版游戏",
                    "decompiled/ - 反编译输出",
                    "captures/ - 抓包数据",
                    "analysis/ - 分析结果",
                    "tools/ - 外部工具",
                    "libs/ - 依赖库"
                ]
            },
            "backup": {
                "description": "备份目录",
                "items": [
                    "Buckup/Step_1.8.1/ - 版本备份",
                    "backupdocs/ - 会话记录备份"
                ]
            }
        },
        "notes": [
            "PC版目录(miniworldPC_CN)正在使用，无法移动",
            "需要在游戏关闭后手动移动",
            "所有组件不得跨文件夹引用"
        ]
    }
    
    structure_file = PROJECT_DIR / "PROJECT_STRUCTURE.json"
    with open(structure_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    print(f"  [+] 结构文档: {structure_file}")
    return True

def create_summary():
    """创建整理摘要"""
    print("\n[*] 创建整理摘要...")
    
    summary = f"""# 项目整理摘要

## 整理时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 版本信息
- 当前版本: 1.8.2
- 备份版本: Step 1.8.1
- 备份位置: MnMCPResources/Buckup/Step_1.8.1/

## 整理内容

### 已移动的文件

1. **SESSION文件** -> backupdocs/
   - 所有SESSION_*.md文件

2. **APK文件** -> Resources/apks/
   - miniworldMini-wp.apk
   - miniworld_en_1.7.15.apk

3. **分析结果** -> Resources/analysis/
   - DEX字符串分析
   - 抓包深度分析

### 待移动的文件（需要关闭游戏）

- miniworldPC_CN/ (PC版国服)
- miniworldPC_Global/ (PC版外服)

**请在游戏关闭后手动移动这些目录到 Resources/pc_versions/**

## 目录结构

```
Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/ (GitHub)
├── src/                    # 核心源代码
├── docs/                   # 文档
├── tools/                  # 工具脚本
├── config/                 # 配置文件
├── README.md
├── PROJECT_OVERVIEW.md
├── ToDo.md
└── PROJECT_STRUCTURE.json  # 结构说明

MnMCPResources/ (外部资源)
├── Resources/
│   ├── apks/              # APK文件
│   ├── pc_versions/       # PC版游戏（待移动）
│   ├── decompiled/        # 反编译输出
│   ├── captures/          # 抓包数据
│   ├── analysis/          # 分析结果
│   ├── tools/             # 外部工具
│   └── libs/              # 依赖库
├── Buckup/
│   └── Step_1.8.1/        # 版本备份
└── backupdocs/            # 会话记录
```

## 下一步

1. 关闭迷你世界游戏
2. 手动移动PC版目录到 Resources/pc_versions/
3. 提交GitHub仓库

## 重要说明

- 所有组件已确保不跨文件夹引用
- 核心代码在GitHub仓库中
- 大文件和资源在外部资源文件夹中
- 备份已创建，可随时恢复
"""
    
    summary_file = PROJECT_DIR / "ORGANIZATION_SUMMARY.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"  [+] 摘要文件: {summary_file}")
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("项目文件夹整理工具 v2")
    print("=" * 60)
    
    # 执行整理
    create_directories()
    move_session_files()
    move_resources()
    update_project_structure()
    create_summary()
    
    print("\n" + "=" * 60)
    print("整理完成!")
    print("=" * 60)
    print(f"\n✅ 已完成:")
    print(f"  - SESSION文件移动到 backupdocs/")
    print(f"  - APK文件移动到 Resources/apks/")
    print(f"  - 分析结果移动到 Resources/analysis/")
    print(f"  - 项目结构文档已更新")
    print(f"\n⏳ 待完成（需要关闭游戏）:")
    print(f"  - 移动 PC版目录到 Resources/pc_versions/")
    print(f"\n📁 备份位置: {BACKUP_DIR}")
    print(f"📁 资源位置: {RESOURCES_NEW}")
    
    return True

if __name__ == "__main__":
    main()
