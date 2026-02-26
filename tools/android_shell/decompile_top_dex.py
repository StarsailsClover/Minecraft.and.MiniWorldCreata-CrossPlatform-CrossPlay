#!/usr/bin/env python3
"""
反编译最大的DEX文件
提取网络协议源码
"""

import subprocess
from pathlib import Path

# 配置
DEX_DIR = Path(r"https://github.com/StarsailsClover/MnMCPResources\packs_downloads\dumped_dex\dex")
JADX_PATH = Path(r"https://github.com/StarsailsClover/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\tools\jadx\bin\jadx.bat")
OUTPUT_DIR = DEX_DIR.parent / "java_sources"

def get_top_dex_files(n=3):
    """获取最大的N个DEX文件"""
    dex_files = list(DEX_DIR.rglob("*.dex"))
    dex_files.sort(key=lambda x: x.stat().st_size, reverse=True)
    return dex_files[:n]

def decompile_dex(dex_file, output_subdir):
    """反编译单个DEX文件"""
    print(f"\n[*] 反编译 {dex_file.name}...")
    
    output_path = OUTPUT_DIR / output_subdir
    output_path.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        str(JADX_PATH),
        "-d", str(output_path),
        "--show-bad-code",
        "--no-imports",
        str(dex_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print(f"  [+] 成功: {output_path}")
            return True
        else:
            print(f"  [!] 警告: 部分错误")
            return True
    except Exception as e:
        print(f"  [-] 错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("反编译TOP DEX文件")
    print("=" * 60)
    
    if not JADX_PATH.exists():
        print(f"[-] 未找到jadx: {JADX_PATH}")
        return False
    
    # 获取最大的3个DEX文件
    top_dex = get_top_dex_files(3)
    print(f"\n[*] 将反编译前3个最大的DEX文件:")
    for i, dex in enumerate(top_dex, 1):
        size = dex.stat().st_size / (1024*1024)
        print(f"  {i}. {dex.name} ({size:.2f} MB)")
    
    # 反编译每个文件
    for i, dex_file in enumerate(top_dex, 1):
        decompile_dex(dex_file, f"dex_{i}_{dex_file.stem}")
    
    print("\n" + "=" * 60)
    print("反编译完成!")
    print("=" * 60)
    print(f"\n源码位置: {OUTPUT_DIR}")
    print("\n下一步:")
    print("1. 使用jadx-gui查看源码")
    print("2. 搜索网络相关类")
    print("3. 分析协议结构")
    
    return True

if __name__ == "__main__":
    main()
