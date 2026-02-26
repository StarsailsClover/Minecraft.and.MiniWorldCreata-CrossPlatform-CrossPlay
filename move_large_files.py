#!/usr/bin/env python3
"""
移动大文件脚本
将超过100MB的文件移动到外部资源目录
"""

import os
import shutil
from pathlib import Path

# 配置
SOURCE_DIR = r"C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay"
TARGET_DIR = r"C:\Users\Sails\Documents\Coding\MnMCPResources"
SIZE_THRESHOLD = 100 * 1024 * 1024  # 100MB

# 需要移动的文件类型
LARGE_FILE_TYPES = [
    '.jar',      # Java归档
    '.apk',      # Android安装包
    '.zip',      # 压缩包
    '.xz',       # 压缩文件
    '.exe',      # 可执行文件
    '.msi',      # 安装包
]

def get_file_size(path):
    """获取文件大小（字节）"""
    return os.path.getsize(path)

def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def should_move_file(filepath):
    """判断是否应该移动文件"""
    # 检查文件扩展名
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in LARGE_FILE_TYPES:
        return False
    
    # 检查文件大小
    try:
        size = get_file_size(filepath)
        return size >= SIZE_THRESHOLD
    except:
        return False

def move_file(src, dst):
    """移动文件并创建符号链接"""
    try:
        # 确保目标目录存在
        dst_dir = os.path.dirname(dst)
        os.makedirs(dst_dir, exist_ok=True)
        
        # 移动文件
        print(f"  移动: {os.path.basename(src)}")
        print(f"    大小: {format_size(get_file_size(src))}")
        print(f"    到: {dst}")
        
        shutil.move(src, dst)
        
        # 创建符号链接（Windows需要管理员权限）
        try:
            os.symlink(dst, src)
            print(f"    创建符号链接: ✓")
        except OSError:
            # 没有权限创建符号链接，创建文本文件记录位置
            with open(src + '.location', 'w') as f:
                f.write(f"FILE_MOVED_TO:\n{dst}\n")
            print(f"    创建位置记录文件: ✓")
        
        return True
        
    except Exception as e:
        print(f"    错误: {str(e)}")
        return False

def scan_and_move():
    """扫描并移动大文件"""
    print("="*70)
    print("大文件移动工具")
    print(f"阈值: {format_size(SIZE_THRESHOLD)}")
    print(f"源目录: {SOURCE_DIR}")
    print(f"目标目录: {TARGET_DIR}")
    print("="*70)
    
    moved_files = []
    errors = []
    
    for root, dirs, files in os.walk(SOURCE_DIR):
        # 跳过.git目录
        if '.git' in root:
            continue
            
        for filename in files:
            filepath = os.path.join(root, filename)
            
            # 检查是否应该移动
            if should_move_file(filepath):
                # 计算相对路径
                rel_path = os.path.relpath(filepath, SOURCE_DIR)
                target_path = os.path.join(TARGET_DIR, rel_path)
                
                print(f"\n[发现大文件] {rel_path}")
                
                # 移动文件
                if move_file(filepath, target_path):
                    moved_files.append({
                        'original': filepath,
                        'new': target_path,
                        'size': get_file_size(target_path)
                    })
                else:
                    errors.append(filepath)
    
    # 显示结果
    print("\n" + "="*70)
    print("[移动结果汇总]")
    print("="*70)
    
    if moved_files:
        print(f"\n成功移动 {len(moved_files)} 个文件:")
        total_size = 0
        for info in moved_files:
            print(f"  ✓ {os.path.basename(info['original'])}")
            print(f"    {format_size(info['size'])}")
            total_size += info['size']
        print(f"\n总大小: {format_size(total_size)}")
    else:
        print("\n没有需要移动的文件")
    
    if errors:
        print(f"\n失败 {len(errors)} 个文件:")
        for filepath in errors:
            print(f"  ✗ {filepath}")
    
    return moved_files

def create_resource_links():
    """创建资源目录链接文档"""
    links_file = os.path.join(SOURCE_DIR, "EXTERNAL_RESOURCES.md")
    
    content = f"""# 外部资源目录

由于文件大小限制，以下资源存储在外部目录：

## 外部目录位置
```
{TARGET_DIR}
```

## 目录结构
```
MnMCPResources/
├── server/          # 服务端文件
├── tools/           # 工具文件
├── apk_downloads/   # APK文件
└── ...
```

## 移动的文件类型
- JAR文件 (>100MB)
- APK文件 (>100MB)
- 压缩包 (>100MB)
- 其他大文件

## 如何访问
原始位置的文件已被替换为：
- 符号链接（如有管理员权限）
- 或 .location 文件（记录实际位置）

## 使用说明
在脚本中使用相对路径访问资源时，会自动解析到正确位置。

---
Made with ❤️ by ZCNotFound for cross-platform gaming
"""
    
    with open(links_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n[创建] 外部资源说明: {links_file}")

if __name__ == "__main__":
    # 确保目标目录存在
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    # 扫描并移动文件
    moved = scan_and_move()
    
    # 创建链接文档
    if moved:
        create_resource_links()
    
    print("\n[完成] 大文件移动操作结束")
