"""
分析 MnMCPResources 资源文件
提取有用的开发信息
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any

# 资源路径
RESOURCES_DIR = Path("D:/Coding/BlockConnect/BlockConnect-MnMCP/MnMCPResources")

def analyze_memory_dump():
    """分析内存dump文件"""
    print("\n" + "="*60)
    print("内存Dump分析")
    print("="*60)
    
    dump_dir = RESOURCES_DIR / "dumpingmem" / "2603140044"
    
    # 分析 found_keys.json
    found_keys_path = dump_dir / "found_keys.json"
    if found_keys_path.exists():
        with open(found_keys_path, 'r', encoding='utf-8') as f:
            keys = json.load(f)
        
        print(f"\n找到 {len(keys)} 个密钥/敏感信息:")
        
        key_types = {}
        for key in keys:
            pattern = key.get('pattern', '')
            if pattern not in key_types:
                key_types[pattern] = 0
            key_types[pattern] += 1
        
        for pattern, count in sorted(key_types.items(), key=lambda x: -x[1]):
            print(f"  - {pattern}: {count} 次")
    
    # 分析 miniworld_strings.json
    strings_path = dump_dir / "miniworld_strings.json"
    if strings_path.exists():
        print("\n迷你世界字符串分析:")
        print("  - 包含 UI 路径、资源路径、配置信息等")
        print("  - 可用于理解游戏内部结构")

def analyze_block_mappings():
    """分析方块映射"""
    print("\n" + "="*60)
    print("方块映射分析")
    print("="*60)
    
    data_dir = Path("D:/Coding/BlockConnect/BlockConnect-MnMCP/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/mnmcp-core/data")
    
    mapping_files = [
        "block_mappings.json",
        "block_mapping_v3_complete.json",
        "mnw_mc_block_mapping_v2.json",
    ]
    
    for filename in mapping_files:
        filepath = data_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                print(f"\n{filename}:")
                print(f"  - 条目数: {len(data)}")
                
                # 显示前5个映射
                for i, (k, v) in enumerate(list(data.items())[:5]):
                    print(f"  - {k} -> {v}")

def analyze_protocol_docs():
    """分析协议文档"""
    print("\n" + "="*60)
    print("协议文档分析")
    print("="*60)
    
    docs_dir = RESOURCES_DIR / "reverse-engineering"
    
    protocol_docs = [
        "captures/Resources/analysis/pcap_analysis/DEEP_ANALYSIS_REPORT.md",
        "apk-resources/packs_downloads/pc_source/PC_ANALYSIS_REPORT.md",
    ]
    
    for doc_path in protocol_docs:
        full_path = docs_dir / doc_path
        if full_path.exists():
            print(f"\n找到协议文档: {doc_path}")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取关键信息
            if "TLS" in content:
                print("  - 包含 TLS/加密信息")
            if "port" in content.lower():
                print("  - 包含端口信息")
            if "server" in content.lower():
                print("  - 包含服务器信息")

def extract_server_info():
    """提取服务器信息"""
    print("\n" + "="*60)
    print("服务器信息提取")
    print("="*60)
    
    # 从内存分析中提取
    dump_dir = RESOURCES_DIR / "dumpingmem" / "2603140044"
    strings_path = dump_dir / "miniworld_strings.json"
    
    if strings_path.exists():
        with open(strings_path, 'r', encoding='utf-8') as f:
            strings = json.load(f)
        
        # 查找 URL 和 IP
        urls = set()
        ips = set()
        
        for item in strings:
            context = item.get('context', '')
            
            # 查找 URL
            if 'http' in context:
                # 简单提取 URL
                import re
                url_matches = re.findall(r'https?://[^\s"<>]+', context)
                urls.update(url_matches)
            
            # 查找 IP:端口
            ip_matches = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', context)
            ips.update(ip_matches)
        
        if urls:
            print(f"\n找到 {len(urls)} 个 URL:")
            for url in list(urls)[:10]:
                print(f"  - {url}")
        
        if ips:
            print(f"\n找到 {len(ips)} 个 IP:端口:")
            for ip in list(ips)[:10]:
                print(f"  - {ip}")

def generate_development_plan():
    """生成开发计划"""
    print("\n" + "="*60)
    print("基于资源的开发计划")
    print("="*60)
    
    print("""
基于资源分析，建议以下开发方向:

1. **加密算法优化** (基于 found_keys.json)
   - 实现完整的证书验证
   - 添加 RSA/DSA/EC 密钥支持
   - 实现 XXTEA 加密

2. **协议完善** (基于抓包分析)
   - 完善 TLS 握手流程
   - 实现所有消息类型
   - 添加协议版本检测

3. **服务器发现** (基于内存字符串)
   - 动态服务器列表
   - 负载均衡支持
   - 故障转移

4. **UI/资源映射** (基于 miniworld_strings)
   - 完整的资源路径映射
   - UI 元素识别
   - 配置文件解析

5. **方块映射完善** (基于 mapping JSON)
   - 验证所有方块映射
   - 添加缺失的方块
   - 版本兼容性
""")

def main():
    print("\n" + "="*60)
    print("MnMCPResources 资源分析")
    print("="*60)
    
    analyze_memory_dump()
    analyze_block_mappings()
    analyze_protocol_docs()
    extract_server_info()
    generate_development_plan()
    
    print("\n" + "="*60)
    print("分析完成!")
    print("="*60)

if __name__ == "__main__":
    main()
