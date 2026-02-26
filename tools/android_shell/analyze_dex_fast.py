#!/usr/bin/env python3
"""
快速分析DEX文件
提取关键网络协议信息
"""

import os
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime

# 配置
DEX_DIR = Path(r"C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\dex")
JADX_PATH = Path(r"C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\tools\jadx\bin\jadx.bat")
OUTPUT_DIR = DEX_DIR.parent / "analysis_output"

def find_dex_files():
    """查找所有DEX文件"""
    print("[*] 查找DEX文件...")
    
    dex_files = list(DEX_DIR.rglob("*.dex"))
    print(f"[+] 找到 {len(dex_files)} 个DEX文件")
    
    # 按大小排序，优先分析大文件
    dex_files.sort(key=lambda x: x.stat().st_size, reverse=True)
    
    total_size = sum(f.stat().st_size for f in dex_files) / (1024*1024)
    print(f"[+] 总大小: {total_size:.2f} MB")
    
    return dex_files

def extract_strings_from_dex(dex_file):
    """从DEX提取字符串"""
    print(f"\n[*] 分析 {dex_file.name}...")
    
    findings = {
        "urls": [],
        "ips": [],
        "ports": [],
        "domains": [],
        "api_endpoints": [],
        "crypto_keywords": [],
        "network_keywords": []
    }
    
    try:
        with open(dex_file, 'rb') as f:
            content = f.read()
        
        # 查找URL
        urls = re.findall(rb'https?://[\w\-\.]+/[\w\-/\.]*', content)
        findings["urls"] = list(set([url.decode('ascii', errors='ignore') for url in urls[:100]]))
        
        # 查找IP
        ips = re.findall(rb'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', content)
        unique_ips = []
        for ip in ips:
            ip_str = ip.decode('ascii')
            if not ip_str.startswith(('127.', '192.168.', '10.', '172.')):
                if ip_str not in unique_ips:
                    unique_ips.append(ip_str)
        findings["ips"] = unique_ips[:50]
        
        # 查找域名
        domains = re.findall(rb'[\w\-]+\.(?:com|cn|net|org|io|cc|xyz)[\w\-\.]*', content)
        findings["domains"] = list(set([d.decode('ascii', errors='ignore') for d in domains[:100] if len(d) > 5]))
        
        # 查找API端点
        api_patterns = re.findall(rb'/api/[\w/]+', content)
        findings["api_endpoints"] = list(set([p.decode('ascii', errors='ignore') for p in api_patterns[:50]]))
        
        # 查找加密相关
        crypto = re.findall(rb'AES|RSA|MD5|SHA|encrypt|decrypt|cipher|crypto', content, re.IGNORECASE)
        findings["crypto_keywords"] = list(set([c.decode('ascii', errors='ignore') for c in crypto[:30]]))
        
        # 查找网络相关
        network = re.findall(rb'socket|tcp|udp|http|network|connection|packet|protocol', content, re.IGNORECASE)
        findings["network_keywords"] = list(set([n.decode('ascii', errors='ignore') for n in network[:30]]))
        
    except Exception as e:
        print(f"  [-] 错误: {e}")
    
    return findings

def analyze_top_dex_files(dex_files, top_n=5):
    """分析前N个最大的DEX文件"""
    print(f"\n[*] 分析前{top_n}个最大的DEX文件...")
    
    all_findings = {
        "analysis_time": datetime.now().isoformat(),
        "total_dex": len(dex_files),
        "urls": set(),
        "ips": set(),
        "domains": set(),
        "api_endpoints": set(),
        "crypto_keywords": set(),
        "network_keywords": set()
    }
    
    for i, dex_file in enumerate(dex_files[:top_n]):
        size = dex_file.stat().st_size / (1024*1024)
        print(f"\n[{i+1}/{top_n}] {dex_file.name} ({size:.2f} MB)")
        
        findings = extract_strings_from_dex(dex_file)
        
        # 合并结果
        all_findings["urls"].update(findings["urls"])
        all_findings["ips"].update(findings["ips"])
        all_findings["domains"].update(findings["domains"])
        all_findings["api_endpoints"].update(findings["api_endpoints"])
        all_findings["crypto_keywords"].update(findings["crypto_keywords"])
        all_findings["network_keywords"].update(findings["network_keywords"])
        
        print(f"  URLs: {len(findings['urls'])}")
        print(f"  IPs: {len(findings['ips'])}")
        print(f"  Domains: {len(findings['domains'])}")
    
    # 转换为列表
    for key in ["urls", "ips", "domains", "api_endpoints", "crypto_keywords", "network_keywords"]:
        all_findings[key] = list(all_findings[key])
    
    return all_findings

def generate_report(findings):
    """生成分析报告"""
    print("\n[*] 生成分析报告...")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = OUTPUT_DIR / "DEX_STRINGS_ANALYSIS.md"
    
    report = f"""# DEX文件字符串分析报告

## 分析时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 概览

- **分析的DEX文件数**: {findings['total_dex']}
- **分析的TOP文件**: 5个最大文件

## 发现的URL ({len(findings['urls'])}个)

"""
    
    for url in sorted(findings['urls'])[:50]:
        report += f"- `{url}`\n"
    
    report += f"\n## 发现的IP地址 ({len(findings['ips'])}个)\n\n"
    for ip in sorted(findings['ips'])[:30]:
        report += f"- `{ip}`\n"
    
    report += f"\n## 发现的域名 ({len(findings['domains'])}个)\n\n"
    for domain in sorted(findings['domains'])[:50]:
        report += f"- `{domain}`\n"
    
    report += f"\n## API端点 ({len(findings['api_endpoints'])}个)\n\n"
    for api in sorted(findings['api_endpoints'])[:30]:
        report += f"- `{api}`\n"
    
    report += f"\n## 加密关键词 ({len(findings['crypto_keywords'])}个)\n\n"
    for keyword in sorted(findings['crypto_keywords']):
        report += f"- `{keyword}`\n"
    
    report += f"\n## 网络关键词 ({len(findings['network_keywords'])}个)\n\n"
    for keyword in sorted(findings['network_keywords']):
        report += f"- `{keyword}`\n"
    
    report += """
## 关键发现

### 服务器信息
根据字符串分析，识别出以下可能的服务器：

（请查看URL和IP列表）

### 加密方式
根据关键词分析，可能使用的加密：

（请查看加密关键词列表）

### 网络协议
根据关键词分析，可能使用的协议：

（请查看网络关键词列表）

## 下一步

1. 使用jadx反编译DEX文件获取完整代码
2. 分析网络通信类
3. 识别协议结构
4. 提取加密算法
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 保存JSON格式
    json_file = OUTPUT_DIR / "dex_analysis.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)
    
    print(f"[+] 报告: {report_file}")
    print(f"[+] JSON: {json_file}")
    
    return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("DEX文件快速分析工具")
    print("=" * 60)
    
    if not DEX_DIR.exists():
        print(f"[-] DEX目录不存在: {DEX_DIR}")
        return False
    
    # 查找DEX文件
    dex_files = find_dex_files()
    if not dex_files:
        print("[-] 未找到DEX文件")
        return False
    
    # 分析前5个最大的文件
    findings = analyze_top_dex_files(dex_files, top_n=5)
    
    # 生成报告
    report_file = generate_report(findings)
    
    print("\n" + "=" * 60)
    print("分析完成!")
    print("=" * 60)
    print(f"\n发现:")
    print(f"  URLs: {len(findings['urls'])}")
    print(f"  IPs: {len(findings['ips'])}")
    print(f"  Domains: {len(findings['domains'])}")
    print(f"  API端点: {len(findings['api_endpoints'])}")
    print(f"\n报告: {report_file}")
    
    return True

if __name__ == "__main__":
    main()
