#!/usr/bin/env python3
"""
分析反编译后的Java源码
提取网络协议相关信息
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 配置
SOURCES_DIR = Path(r"https://github.com/StarsailsClover/MnMCPResources\packs_downloads\dumped_dex\java_sources")
OUTPUT_DIR = SOURCES_DIR.parent / "protocol_analysis"

def find_java_files():
    """查找所有Java文件"""
    print("[*] 查找Java文件...")
    
    java_files = []
    for src_dir in SOURCES_DIR.iterdir():
        if src_dir.is_dir():
            java_files.extend(src_dir.rglob("*.java"))
    
    print(f"[+] 找到 {len(java_files)} 个Java文件")
    return java_files

def analyze_file(java_file):
    """分析单个Java文件"""
    try:
        with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        findings = {
            "file": str(java_file.relative_to(SOURCES_DIR)),
            "class_name": java_file.stem,
            "is_network_class": False,
            "is_protocol_class": False,
            "is_crypto_class": False,
            "is_login_class": False,
            "imports": [],
            "urls": [],
            "ips": [],
            "ports": [],
            "methods": []
        }
        
        # 检查导入
        imports = re.findall(r'import ([\w\.]+);', content)
        findings["imports"] = imports[:20]
        
        # 检查是否是网络类
        network_patterns = [
            r'class.*Network',
            r'class.*Socket',
            r'class.*Connection',
            r'class.*Client',
            r'class.*Server',
            r'class.*Http',
            r'class.*Tcp',
            r'class.*Udp'
        ]
        
        for pattern in network_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                findings["is_network_class"] = True
                break
        
        # 检查是否是协议类
        protocol_patterns = [
            r'class.*Protocol',
            r'class.*Packet',
            r'class.*Message',
            r'class.*Handler',
            r'class.*Command',
            r'class.*Opcode'
        ]
        
        for pattern in protocol_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                findings["is_protocol_class"] = True
                break
        
        # 检查是否是加密类
        crypto_patterns = [
            r'class.*Crypto',
            r'class.*Encrypt',
            r'class.*Cipher',
            r'class.*AES',
            r'class.*RSA',
            r'class.*MD5',
            r'class.*SHA'
        ]
        
        for pattern in crypto_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                findings["is_crypto_class"] = True
                break
        
        # 检查是否是登录类
        login_patterns = [
            r'class.*Login',
            r'class.*Auth',
            r'class.*Account',
            r'class.*User',
            r'class.*Session',
            r'class.*Token'
        ]
        
        for pattern in login_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                findings["is_login_class"] = True
                break
        
        # 提取URL
        urls = re.findall(r'https?://[\w\-\.]+/[\w\-/\.]*', content)
        findings["urls"] = list(set(urls))[:10]
        
        # 提取IP
        ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', content)
        unique_ips = []
        for ip in ips:
            if not ip.startswith(('127.', '192.168.', '10.', '172.')):
                if ip not in unique_ips:
                    unique_ips.append(ip)
        findings["ips"] = unique_ips[:10]
        
        # 提取端口号
        ports = re.findall(r':(\d{4,5})', content)
        findings["ports"] = list(set([int(p) for p in ports if 1000 <= int(p) <= 65535]))[:10]
        
        # 提取方法名
        methods = re.findall(r'(public|private|protected)\s+\w+\s+(\w+)\s*\(', content)
        findings["methods"] = [m[1] for m in methods[:20]]
        
        return findings
    
    except Exception as e:
        return None

def analyze_all_files(java_files):
    """分析所有Java文件"""
    print(f"\n[*] 分析 {len(java_files)} 个Java文件...")
    
    all_findings = {
        "analysis_time": datetime.now().isoformat(),
        "total_files": len(java_files),
        "network_classes": [],
        "protocol_classes": [],
        "crypto_classes": [],
        "login_classes": [],
        "all_urls": set(),
        "all_ips": set(),
        "all_ports": set()
    }
    
    for i, java_file in enumerate(java_files):
        if i % 100 == 0:
            print(f"  进度: {i}/{len(java_files)}")
        
        findings = analyze_file(java_file)
        if not findings:
            continue
        
        # 分类存储
        if findings["is_network_class"]:
            all_findings["network_classes"].append(findings)
        
        if findings["is_protocol_class"]:
            all_findings["protocol_classes"].append(findings)
        
        if findings["is_crypto_class"]:
            all_findings["crypto_classes"].append(findings)
        
        if findings["is_login_class"]:
            all_findings["login_classes"].append(findings)
        
        # 合并URL/IP/端口
        all_findings["all_urls"].update(findings["urls"])
        all_findings["all_ips"].update(findings["ips"])
        all_findings["all_ports"].update(findings["ports"])
    
    # 转换为列表
    all_findings["all_urls"] = list(all_findings["all_urls"])
    all_findings["all_ips"] = list(all_findings["all_ips"])
    all_findings["all_ports"] = list(all_findings["all_ports"])
    
    return all_findings

def generate_report(findings):
    """生成分析报告"""
    print("\n[*] 生成分析报告...")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = OUTPUT_DIR / "JAVA_PROTOCOL_ANALYSIS.md"
    
    report = f"""# Java源码协议分析报告

## 分析时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 概览

- **分析文件数**: {findings['total_files']}
- **网络类**: {len(findings['network_classes'])}
- **协议类**: {len(findings['protocol_classes'])}
- **加密类**: {len(findings['crypto_classes'])}
- **登录类**: {len(findings['login_classes'])}

## 网络通信类 (Top 20)

"""
    
    for i, cls in enumerate(findings['network_classes'][:20], 1):
        report += f"{i}. `{cls['class_name']}`\n"
        report += f"   - 文件: `{cls['file']}`\n"
        if cls['urls']:
            report += f"   - URL: {', '.join(cls['urls'][:3])}\n"
        if cls['ips']:
            report += f"   - IP: {', '.join(cls['ips'][:3])}\n"
        report += "\n"
    
    report += "\n## 协议处理类 (Top 20)\n\n"
    for i, cls in enumerate(findings['protocol_classes'][:20], 1):
        report += f"{i}. `{cls['class_name']}`\n"
        report += f"   - 文件: `{cls['file']}`\n"
        if cls['methods']:
            report += f"   - 方法: {', '.join(cls['methods'][:5])}\n"
        report += "\n"
    
    report += "\n## 加密相关类 (Top 20)\n\n"
    for i, cls in enumerate(findings['crypto_classes'][:20], 1):
        report += f"{i}. `{cls['class_name']}`\n"
        report += f"   - 文件: `{cls['file']}`\n"
        report += "\n"
    
    report += "\n## 登录认证类 (Top 20)\n\n"
    for i, cls in enumerate(findings['login_classes'][:20], 1):
        report += f"{i}. `{cls['class_name']}`\n"
        report += f"   - 文件: `{cls['file']}`\n"
        report += "\n"
    
    report += f"\n## 发现的URL ({len(findings['all_urls'])}个)\n\n"
    for url in sorted(findings['all_urls'])[:30]:
        report += f"- `{url}`\n"
    
    report += f"\n## 发现的IP地址 ({len(findings['all_ips'])}个)\n\n"
    for ip in sorted(findings['all_ips'])[:20]:
        report += f"- `{ip}`\n"
    
    report += f"\n## 发现的端口 ({len(findings['all_ports'])}个)\n\n"
    for port in sorted(findings['all_ports']):
        report += f"- `{port}`\n"
    
    report += """
## 关键发现

### 网络架构
根据源码分析，识别出以下网络组件：

（请查看各类列表）

### 协议结构
根据协议类分析，可能的数据包结构：

（需要进一步分析具体类实现）

### 加密方式
根据加密类分析，可能使用的加密：

（请查看加密类列表）

## 下一步

1. 重点分析网络类的实现
2. 查看协议类的数据包处理方法
3. 分析加密类的加密算法
4. 提取完整协议规范
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 保存JSON
    json_file = OUTPUT_DIR / "java_analysis.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)
    
    print(f"[+] 报告: {report_file}")
    print(f"[+] JSON: {json_file}")
    
    return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("Java源码协议分析")
    print("=" * 60)
    
    if not SOURCES_DIR.exists():
        print(f"[-] 源码目录不存在: {SOURCES_DIR}")
        return False
    
    # 查找Java文件
    java_files = find_java_files()
    if not java_files:
        print("[-] 未找到Java文件")
        return False
    
    # 分析所有文件
    findings = analyze_all_files(java_files)
    
    # 生成报告
    report_file = generate_report(findings)
    
    print("\n" + "=" * 60)
    print("分析完成!")
    print("=" * 60)
    print(f"\n发现:")
    print(f"  网络类: {len(findings['network_classes'])}")
    print(f"  协议类: {len(findings['protocol_classes'])}")
    print(f"  加密类: {len(findings['crypto_classes'])}")
    print(f"  登录类: {len(findings['login_classes'])}")
    print(f"  URL: {len(findings['all_urls'])}")
    print(f"  IP: {len(findings['all_ips'])}")
    print(f"  端口: {len(findings['all_ports'])}")
    print(f"\n报告: {report_file}")
    
    return True

if __name__ == "__main__":
    main()
