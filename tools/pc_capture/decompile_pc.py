#!/usr/bin/env python3
"""
反编译PC版迷你世界
提取IL代码和网络相关逻辑
"""

import os
import subprocess
from pathlib import Path

# 配置
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent.parent
EXTERNAL_DIR = PROJECT_DIR.parent / "MnMCPResources"
PC_DIR = EXTERNAL_DIR / "packs_downloads" / "miniworldPC_CN" / "miniworldLauncher"
OUTPUT_DIR = EXTERNAL_DIR / "packs_downloads" / "pc_source"

def analyze_exe_files():
    """分析EXE文件"""
    print("[*] 分析PC版EXE文件...")
    
    exe_files = list(PC_DIR.glob("*.exe"))
    print(f"[+] 找到 {len(exe_files)} 个EXE文件:")
    
    for exe in exe_files:
        size = exe.stat().st_size / (1024*1024)
        print(f"    - {exe.name}: {size:.2f} MB")
    
    return exe_files

def analyze_dll_files():
    """分析DLL文件"""
    print("\n[*] 分析DLL文件...")
    
    dll_files = list(PC_DIR.glob("*.dll"))
    print(f"[+] 找到 {len(dll_files)} 个DLL文件")
    
    # 查找可能的网络相关DLL
    network_keywords = ['net', 'socket', 'http', 'tcp', 'udp', 'network', 'connection']
    network_dlls = []
    
    for dll in dll_files:
        dll_name = dll.name.lower()
        for keyword in network_keywords:
            if keyword in dll_name:
                network_dlls.append(dll)
                break
    
    if network_dlls:
        print(f"\n[+] 可能的网络相关DLL ({len(network_dlls)}个):")
        for dll in network_dlls[:10]:
            size = dll.stat().st_size / (1024*1024)
            print(f"    - {dll.name}: {size:.2f} MB")
    
    return dll_files

def extract_strings_from_exe(exe_path):
    """从EXE提取字符串"""
    print(f"\n[*] 从 {exe_path.name} 提取字符串...")
    
    # 使用powershell的strings等效功能
    try:
        # 读取文件并提取可打印字符串
        with open(exe_path, 'rb') as f:
            content = f.read()
        
        # 提取URL/IP/端口相关字符串
        import re
        
        # 查找URL
        urls = re.findall(rb'https?://[\w\-\.]+/[\w\-/\.]*', content)
        unique_urls = set([url.decode('ascii', errors='ignore') for url in urls[:50]])
        
        # 查找IP地址
        ips = re.findall(rb'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', content)
        unique_ips = set([ip.decode('ascii') for ip in ips[:50] if not ip.startswith(b'127.') and not ip.startswith(b'192.168.')])
        
        # 查找端口号（常见游戏端口范围）
        ports = re.findall(rb':(\d{4,5})', content)
        common_ports = [int(p) for p in ports if 1000 <= int(p) <= 65535]
        unique_ports = set(common_ports[:20])
        
        print(f"    找到 {len(unique_urls)} 个URL")
        print(f"    找到 {len(unique_ips)} 个IP地址")
        print(f"    找到 {len(unique_ports)} 个端口号")
        
        return {
            'urls': list(unique_urls)[:20],
            'ips': list(unique_ips)[:20],
            'ports': list(unique_ports)[:10]
        }
    
    except Exception as e:
        print(f"    [-] 提取失败: {e}")
        return {'urls': [], 'ips': [], 'ports': []}

def analyze_config_files():
    """分析配置文件"""
    print("\n[*] 分析配置文件...")
    
    config_files = []
    for ext in ['.json', '.xml', '.ini', '.cfg', '.config']:
        config_files.extend(PC_DIR.rglob(f'*{ext}'))
    
    print(f"[+] 找到 {len(config_files)} 个配置文件")
    
    findings = {
        'server_urls': [],
        'api_endpoints': [],
        'ports': []
    }
    
    for config in config_files[:10]:
        try:
            with open(config, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # 查找服务器相关配置
                if 'server' in content.lower() or 'host' in content.lower():
                    print(f"    [+] 可能包含服务器配置: {config.name}")
        except:
            pass
    
    return findings

def main():
    """主函数"""
    print("=" * 60)
    print("PC版迷你世界分析工具")
    print("=" * 60)
    
    if not PC_DIR.exists():
        print(f"[-] PC版目录不存在: {PC_DIR}")
        return False
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 分析EXE文件
    exe_files = analyze_exe_files()
    
    # 分析DLL文件
    dll_files = analyze_dll_files()
    
    # 从主EXE提取字符串
    main_exe = PC_DIR / "iworldpc.exe"
    if main_exe.exists():
        exe_info = extract_strings_from_exe(main_exe)
    else:
        exe_info = {'urls': [], 'ips': [], 'ports': []}
    
    # 分析配置文件
    config_info = analyze_config_files()
    
    # 生成报告
    report_path = OUTPUT_DIR / "PC_ANALYSIS_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# PC版迷你世界分析报告\n\n")
        f.write("## EXE文件\n\n")
        for exe in exe_files:
            size = exe.stat().st_size / (1024*1024)
            f.write(f"- {exe.name}: {size:.2f} MB\n")
        
        f.write("\n## 网络相关字符串\n\n")
        f.write("### URL\n")
        for url in exe_info['urls']:
            f.write(f"- {url}\n")
        
        f.write("\n### IP地址\n")
        for ip in exe_info['ips']:
            f.write(f"- {ip}\n")
        
        f.write("\n### 端口\n")
        for port in exe_info['ports']:
            f.write(f"- {port}\n")
    
    print(f"\n[+] 报告保存: {report_path}")
    
    print("\n" + "=" * 60)
    print("分析完成!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    main()
