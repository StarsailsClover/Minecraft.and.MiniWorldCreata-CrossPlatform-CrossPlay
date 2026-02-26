#!/usr/bin/env python3
"""
处理Frida脱壳产出的DEX文件
"""

import os
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime

# 配置
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent.parent
EXTERNAL_DIR = PROJECT_DIR.parent / "MnMCPResources"
DEX_DIR = EXTERNAL_DIR / "packs_downloads" / "dumped_dex"
JADX_PATH = PROJECT_DIR / "tools" / "jadx" / "bin" / "jadx.bat"
OUTPUT_DIR = DEX_DIR / "frida_sources"
ANALYSIS_DIR = DEX_DIR / "frida_analysis"

def check_dex_files():
    """检查DEX文件"""
    print("[*] 检查Frida脱壳DEX文件...")
    
    # Frida产出在rar中，需要手动解压
    rar_file = DEX_DIR / "dex.rar"
    if rar_file.exists():
        size = rar_file.stat().st_size / (1024*1024)
        print(f"[+] 找到Frida产出: dex.rar ({size:.2f} MB)")
        print(f"[!] 请手动解压 {rar_file} 到 {DEX_DIR}")
        print("[!] 解压后应该包含 classes.dex, classes02.dex, ... 等文件")
        return False
    
    # 检查是否已解压
    dex_files = list(DEX_DIR.glob("classes*.dex"))
    if not dex_files:
        print("[-] 未找到DEX文件")
        return False
    
    print(f"[+] 找到 {len(dex_files)} 个DEX文件:")
    total_size = 0
    for dex in sorted(dex_files):
        size = dex.stat().st_size / (1024*1024)
        total_size += size
        print(f"    - {dex.name}: {size:.2f} MB")
    
    print(f"[+] 总大小: {total_size:.2f} MB")
    return dex_files

def decompile_dex_files(dex_files):
    """反编译DEX文件"""
    print("\n[*] 反编译DEX文件...")
    
    if not JADX_PATH.exists():
        print(f"[-] 未找到jadx: {JADX_PATH}")
        return False
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 反编译最大的几个DEX文件（通常包含主要代码）
    dex_files_sorted = sorted(dex_files, key=lambda x: x.stat().st_size, reverse=True)
    
    for i, dex_file in enumerate(dex_files_sorted[:5]):  # 只处理前5个最大的
        print(f"\n[{i+1}/5] 反编译 {dex_file.name}...")
        
        dex_output = OUTPUT_DIR / f"{dex_file.stem}_sources"
        dex_output.mkdir(exist_ok=True)
        
        cmd = [
            str(JADX_PATH),
            "-d", str(dex_output),
            "--show-bad-code",
            str(dex_file)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"    [+] 成功: {dex_output}")
            else:
                print(f"    [!] 警告: 部分错误")
        except Exception as e:
            print(f"    [-] 错误: {e}")
    
    return True

def analyze_sources():
    """分析源码"""
    print("\n[*] 分析反编译源码...")
    
    if not OUTPUT_DIR.exists():
        print("[-] 源码目录不存在")
        return None
    
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    findings = {
        "analysis_time": datetime.now().isoformat(),
        "total_java_files": 0,
        "network_classes": [],
        "protocol_classes": [],
        "crypto_classes": [],
        "login_classes": [],
        "server_urls": [],
        "api_endpoints": []
    }
    
    # 搜索关键模式
    patterns = {
        "network": [r"class.*Network", r"class.*Socket", r"class.*Connection", r"socket\.", r"java\.net\."],
        "protocol": [r"class.*Protocol", r"class.*Packet", r"class.*Message", r"protocol", r"packet"],
        "crypto": [r"class.*Crypto", r"class.*Encrypt", r"class.*AES", r"AES", r"encrypt", r"cipher"],
        "login": [r"class.*Login", r"class.*Auth", r"login", r"auth", r"token"]
    }
    
    # 遍历所有Java文件
    java_files = list(OUTPUT_DIR.rglob("*.java"))
    findings["total_java_files"] = len(java_files)
    
    print(f"[*] 找到 {len(java_files)} 个Java文件")
    
    # 分析文件
    for i, java_file in enumerate(java_files[:500]):  # 限制数量
        if i % 100 == 0:
            print(f"    进度: {i}/{min(len(java_files), 500)}")
        
        try:
            with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                class_name = java_file.stem
                
                # 检查各类模式
                for category, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        if re.search(pattern, content, re.IGNORECASE):
                            if category == "network":
                                findings["network_classes"].append({"class": class_name, "file": str(java_file.relative_to(OUTPUT_DIR))})
                            elif category == "protocol":
                                findings["protocol_classes"].append({"class": class_name, "file": str(java_file.relative_to(OUTPUT_DIR))})
                            elif category == "crypto":
                                findings["crypto_classes"].append({"class": class_name, "file": str(java_file.relative_to(OUTPUT_DIR))})
                            elif category == "login":
                                findings["login_classes"].append({"class": class_name, "file": str(java_file.relative_to(OUTPUT_DIR))})
                            break
                
                # 查找URL
                urls = re.findall(r'https?://[\w\-\.]+/[\w\-/\.]*', content)
                for url in urls[:5]:
                    if url not in findings["server_urls"]:
                        findings["server_urls"].append(url)
        
        except:
            continue
    
    # 去重
    for key in ["network_classes", "protocol_classes", "crypto_classes", "login_classes"]:
        seen = set()
        unique = []
        for item in findings[key]:
            if item["class"] not in seen:
                seen.add(item["class"])
                unique.append(item)
        findings[key] = unique[:30]
    
    # 保存分析结果
    analysis_file = ANALYSIS_DIR / "frida_analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)
    
    print(f"\n[+] 分析完成!")
    print(f"    Java文件总数: {findings['total_java_files']}")
    print(f"    网络类: {len(findings['network_classes'])}")
    print(f"    协议类: {len(findings['protocol_classes'])}")
    print(f"    加密类: {len(findings['crypto_classes'])}")
    print(f"    登录类: {len(findings['login_classes'])}")
    print(f"    服务器URL: {len(findings['server_urls'])}")
    
    return findings

def generate_report(findings):
    """生成报告"""
    print("\n[*] 生成分析报告...")
    
    report_file = ANALYSIS_DIR / "FRIDA_ANALYSIS_REPORT.md"
    
    report = f"""# Frida脱壳分析报告

## 分析时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 概览

- **Java文件总数**: {findings['total_java_files']}
- **网络相关类**: {len(findings['network_classes'])}
- **协议相关类**: {len(findings['protocol_classes'])}
- **加密相关类**: {len(findings['crypto_classes'])}
- **登录相关类**: {len(findings['login_classes'])}

## 网络通信类 (Top 20)
"""
    
    for i, cls in enumerate(findings['network_classes'][:20], 1):
        report += f"{i}. `{cls['class']}` - {cls['file']}\n"
    
    report += "\n## 协议处理类 (Top 20)\n"
    for i, cls in enumerate(findings['protocol_classes'][:20], 1):
        report += f"{i}. `{cls['class']}` - {cls['file']}\n"
    
    report += "\n## 加密相关类 (Top 20)\n"
    for i, cls in enumerate(findings['crypto_classes'][:20], 1):
        report += f"{i}. `{cls['class']}` - {cls['file']}\n"
    
    report += "\n## 登录认证类 (Top 20)\n"
    for i, cls in enumerate(findings['login_classes'][:20], 1):
        report += f"{i}. `{cls['class']}` - {cls['file']}\n"
    
    report += "\n## 发现的服务器URL\n"
    for url in findings['server_urls'][:20]:
        report += f"- `{url}`\n"
    
    report += """
## 下一步分析建议

1. **重点分析网络类**
   - 查找Socket连接建立代码
   - 分析数据发送/接收逻辑
   - 识别服务器地址和端口

2. **分析协议类**
   - 查找数据包结构定义
   - 识别协议版本号
   - 分析命令码（opcode）定义

3. **分析加密类**
   - 查找AES密钥生成逻辑
   - 分析加密模式（CBC/GCM）
   - 识别IV生成方式

4. **分析登录类**
   - 查找登录请求格式
   - 分析Token获取流程
   - 识别认证服务器

## 文件位置

- 反编译源码: `dumped_dex/frida_sources/`
- 详细分析: `dumped_dex/frida_analysis/frida_analysis.json`
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[+] 报告保存: {report_file}")
    return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("Frida脱壳DEX处理工具")
    print("=" * 60)
    
    # 检查DEX文件
    dex_files = check_dex_files()
    if not dex_files:
        print("\n[!] 请先解压 dex.rar 文件")
        print(f"[!] 解压到: {DEX_DIR}")
        return False
    
    # 反编译
    if not decompile_dex_files(dex_files):
        print("[-] 反编译失败")
        return False
    
    # 分析
    findings = analyze_sources()
    if not findings:
        print("[-] 分析失败")
        return False
    
    # 生成报告
    report_file = generate_report(findings)
    
    print("\n" + "=" * 60)
    print("处理完成!")
    print("=" * 60)
    print(f"\n反编译源码: {OUTPUT_DIR}")
    print(f"分析报告: {report_file}")
    
    return True

if __name__ == "__main__":
    main()
