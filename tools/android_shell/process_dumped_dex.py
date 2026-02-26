#!/usr/bin/env python3
"""
处理BlackDex脱壳产出的DEX文件
自动反编译并提取关键信息
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime

# 配置
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent.parent
EXTERNAL_DIR = PROJECT_DIR.parent / "MnMCPResources"
DUMPED_DIR = EXTERNAL_DIR / "packs_downloads" / "dumped_dex" / "com.minitech.miniworld"
JADX_PATH = PROJECT_DIR / "tools" / "jadx" / "bin" / "jadx.bat"
OUTPUT_DIR = DUMPED_DIR / "sources"
ANALYSIS_DIR = DUMPED_DIR / "analysis"

def check_dumped_files():
    """检查脱壳文件是否存在"""
    print("[*] 检查脱壳DEX文件...")
    
    if not DUMPED_DIR.exists():
        print(f"[-] 脱壳目录不存在: {DUMPED_DIR}")
        print("[!] 请先将BlackDex产出复制到此位置")
        print(f"[!] 期望路径: {DUMPED_DIR}")
        return None
    
    # 查找所有DEX文件
    dex_files = list(DUMPED_DIR.glob("dump_*.dex"))
    
    if not dex_files:
        print("[-] 未找到DEX文件!")
        print(f"[!] 期望文件: {DUMPED_DIR}/dump_0.dex")
        return None
    
    print(f"[+] 找到 {len(dex_files)} 个DEX文件:")
    total_size = 0
    for dex_file in sorted(dex_files):
        size = dex_file.stat().st_size
        total_size += size
        print(f"    - {dex_file.name}: {size / (1024*1024):.2f} MB")
    
    print(f"[+] 总大小: {total_size / (1024*1024):.2f} MB")
    
    if total_size < 50 * 1024 * 1024:  # 小于50MB可能脱壳不完整
        print("[!] 警告: 总大小小于50MB，脱壳可能不完整")
    
    return dex_files

def decompile_dex(dex_files):
    """使用jadx反编译DEX文件"""
    print("\n[*] 使用jadx反编译DEX文件...")
    
    if not JADX_PATH.exists():
        print(f"[-] 未找到jadx: {JADX_PATH}")
        return False
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 反编译所有DEX文件
    for i, dex_file in enumerate(dex_files):
        print(f"\n[{i+1}/{len(dex_files)}] 反编译 {dex_file.name}...")
        
        # 为每个DEX创建单独的输出目录
        dex_output = OUTPUT_DIR / f"dex_{i}"
        dex_output.mkdir(exist_ok=True)
        
        cmd = [
            str(JADX_PATH),
            "-d", str(dex_output),
            "--show-bad-code",
            "--no-imports",
            str(dex_file)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                print(f"    [+] 成功: {dex_output}")
            else:
                print(f"    [!] 警告: 出现错误")
                if "error" in result.stderr.lower():
                    print(f"    [!] 错误: {result.stderr[:200]}")
        
        except subprocess.TimeoutExpired:
            print(f"    [-] 超时（10分钟）")
        except Exception as e:
            print(f"    [-] 错误: {e}")
    
    print(f"\n[+] 反编译完成!")
    print(f"[*] 输出目录: {OUTPUT_DIR}")
    return True

def analyze_sources():
    """分析反编译后的源代码"""
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
        "key_strings": []
    }
    
    # 搜索关键模式
    patterns = {
        "network": [
            r"class.*Network",
            r"class.*Socket",
            r"class.*Connection",
            r"class.*Client",
            r"class.*Server",
            r"socket\.",
            r"java\.net\.",
            r"okhttp",
            r"netty"
        ],
        "protocol": [
            r"class.*Protocol",
            r"class.*Packet",
            r"class.*Message",
            r"class.*Handler",
            r"protocol",
            r"packet",
            r"opcode",
            r"cmd"
        ],
        "crypto": [
            r"class.*Crypto",
            r"class.*Encrypt",
            r"class.*AES",
            r"class.*RSA",
            r"javax\.crypto",
            r"AES",
            r"encrypt",
            r"decrypt",
            r"cipher"
        ],
        "login": [
            r"class.*Login",
            r"class.*Auth",
            r"class.*Account",
            r"login",
            r"auth",
            r"token",
            r"session",
            r"password"
        ]
    }
    
    # 遍历所有Java文件
    java_files = list(OUTPUT_DIR.rglob("*.java"))
    findings["total_java_files"] = len(java_files)
    
    print(f"[*] 找到 {len(java_files)} 个Java文件")
    
    # 分析前1000个文件（避免太慢）
    for i, java_file in enumerate(java_files[:1000]):
        if i % 100 == 0:
            print(f"    进度: {i}/{min(len(java_files), 1000)}")
        
        try:
            with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                class_name = java_file.stem
                
                # 检查网络相关
                for pattern in patterns["network"]:
                    if re.search(pattern, content, re.IGNORECASE):
                        findings["network_classes"].append({
                            "class": class_name,
                            "file": str(java_file.relative_to(OUTPUT_DIR)),
                            "pattern": pattern
                        })
                        break
                
                # 检查协议相关
                for pattern in patterns["protocol"]:
                    if re.search(pattern, content, re.IGNORECASE):
                        findings["protocol_classes"].append({
                            "class": class_name,
                            "file": str(java_file.relative_to(OUTPUT_DIR)),
                            "pattern": pattern
                        })
                        break
                
                # 检查加密相关
                for pattern in patterns["crypto"]:
                    if re.search(pattern, content, re.IGNORECASE):
                        findings["crypto_classes"].append({
                            "class": class_name,
                            "file": str(java_file.relative_to(OUTPUT_DIR)),
                            "pattern": pattern
                        })
                        break
                
                # 检查登录相关
                for pattern in patterns["login"]:
                    if re.search(pattern, content, re.IGNORECASE):
                        findings["login_classes"].append({
                            "class": class_name,
                            "file": str(java_file.relative_to(OUTPUT_DIR)),
                            "pattern": pattern
                        })
                        break
        
        except Exception as e:
            continue
    
    # 去重
    for key in ["network_classes", "protocol_classes", "crypto_classes", "login_classes"]:
        seen = set()
        unique = []
        for item in findings[key]:
            if item["class"] not in seen:
                seen.add(item["class"])
                unique.append(item)
        findings[key] = unique[:50]  # 限制数量
    
    # 保存分析结果
    analysis_file = ANALYSIS_DIR / "source_analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)
    
    print(f"\n[+] 分析完成!")
    print(f"    Java文件总数: {findings['total_java_files']}")
    print(f"    网络类: {len(findings['network_classes'])}")
    print(f"    协议类: {len(findings['protocol_classes'])}")
    print(f"    加密类: {len(findings['crypto_classes'])}")
    print(f"    登录类: {len(findings['login_classes'])}")
    print(f"[*] 结果保存: {analysis_file}")
    
    return findings

def generate_report(findings):
    """生成分析报告"""
    print("\n[*] 生成分析报告...")
    
    report_file = ANALYSIS_DIR / "ANALYSIS_REPORT.md"
    
    report = f"""# 迷你世界APK脱壳分析报告

## 分析时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 概览

- **Java文件总数**: {findings['total_java_files']}
- **网络相关类**: {len(findings['network_classes'])}
- **协议相关类**: {len(findings['protocol_classes'])}
- **加密相关类**: {len(findings['crypto_classes'])}
- **登录相关类**: {len(findings['login_classes'])}

## 关键发现

### 网络通信类 (前20个)
"""
    
    for i, cls in enumerate(findings['network_classes'][:20], 1):
        report += f"{i}. `{cls['class']}` - {cls['file']}\n"
    
    report += "\n### 协议处理类 (前20个)\n"
    for i, cls in enumerate(findings['protocol_classes'][:20], 1):
        report += f"{i}. `{cls['class']}` - {cls['file']}\n"
    
    report += "\n### 加密相关类 (前20个)\n"
    for i, cls in enumerate(findings['crypto_classes'][:20], 1):
        report += f"{i}. `{cls['class']}` - {cls['file']}\n"
    
    report += "\n### 登录认证类 (前20个)\n"
    for i, cls in enumerate(findings['login_classes'][:20], 1):
        report += f"{i}. `{cls['class']}` - {cls['file']}\n"
    
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

- 反编译源码: `dumped_dex/com.minitech.miniworld/sources/`
- 详细分析: `dumped_dex/com.minitech.miniworld/analysis/source_analysis.json`
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[+] 报告保存: {report_file}")
    return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("迷你世界APK脱壳处理工具")
    print("处理BlackDex脱壳产出")
    print("=" * 60)
    
    # 检查脱壳文件
    dex_files = check_dumped_files()
    if not dex_files:
        print("\n[!] 请确保：")
        print("1. BlackDex已成功脱壳APK")
        print("2. DEX文件已复制到：")
        print(f"   {DUMPED_DIR}")
        print("\n[!] 复制命令：")
        print(f"   adb pull /sdcard/Download/BlackDex/com.minitech.miniworld \"{DUMPED_DIR.parent}\"")
        return False
    
    # 反编译DEX
    if not decompile_dex(dex_files):
        print("[-] 反编译失败")
        return False
    
    # 分析源码
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
    print("\n下一步：")
    print("1. 查看分析报告，识别关键类")
    print("2. 使用jadx-gui查看完整源码")
    print("3. 分析网络通信和加密逻辑")
    
    return True

if __name__ == "__main__":
    main()
