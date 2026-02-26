#!/usr/bin/env python3
"""
分析Wireshark抓包文件(.pcapng)
提取迷你世界协议信息
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 配置
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent.parent
EXTERNAL_DIR = PROJECT_DIR.parent / "MnMCPResources"
CAPTURE_DIR = EXTERNAL_DIR / "packs_downloads" / "captures"
ANALYSIS_DIR = CAPTURE_DIR / "analysis"
TSHARK_PATH = r"D:\Program Files\Wireshark\tshark.exe"

def check_tshark():
    """检查tshark是否存在"""
    if not Path(TSHARK_PATH).exists():
        print(f"[-] 未找到tshark: {TSHARK_PATH}")
        print("[!] 请检查Wireshark安装路径")
        return False
    return True

def find_capture_files():
    """查找抓包文件"""
    print("[*] 查找抓包文件...")
    
    pcap_files = list(CAPTURE_DIR.glob("*.pcapng")) + list(CAPTURE_DIR.glob("*.pcap"))
    
    if not pcap_files:
        print("[-] 未找到抓包文件")
        print(f"[!] 请将抓包文件保存到: {CAPTURE_DIR}")
        return None
    
    print(f"[+] 找到 {len(pcap_files)} 个抓包文件:")
    for pcap in pcap_files:
        size = pcap.stat().st_size / (1024*1024)
        print(f"    - {pcap.name}: {size:.2f} MB")
    
    return pcap_files

def analyze_pcap(pcap_file):
    """分析单个抓包文件"""
    print(f"\n[*] 分析抓包文件: {pcap_file.name}")
    
    findings = {
        "filename": pcap_file.name,
        "analysis_time": datetime.now().isoformat(),
        "total_packets": 0,
        "unique_ips": [],
        "unique_ports": [],
        "protocols": [],
        "server_communication": [],
        "packet_sizes": [],
        "timeline": []
    }
    
    # 使用tshark提取基本信息
    try:
        # 获取总包数
        cmd = [TSHARK_PATH, "-r", str(pcap_file), "-q", "-z", "io,phs"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # 解析协议统计
        for line in result.stdout.split('\n'):
            if 'packets' in line.lower():
                match = re.search(r'(\d+)\s+packets', line)
                if match:
                    findings["total_packets"] = int(match.group(1))
        
        # 获取IP统计
        cmd = [TSHARK_PATH, "-r", str(pcap_file), "-q", "-z", "ip_hosts,tree"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        for line in result.stdout.split('\n'):
            ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
            if ip_match:
                ip = ip_match.group(1)
                if ip not in findings["unique_ips"]:
                    findings["unique_ips"].append(ip)
        
        # 获取端口统计
        cmd = [TSHARK_PATH, "-r", str(pcap_file), "-q", "-z", "conv,tcp"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        for line in result.stdout.split('\n'):
            port_match = re.search(r':(\d+)', line)
            if port_match:
                port = int(port_match.group(1))
                if port not in findings["unique_ports"] and port > 1024:
                    findings["unique_ports"].append(port)
        
        # 提取特定数据包（迷你世界相关）
        cmd = [
            TSHARK_PATH, "-r", str(pcap_file),
            "-Y", "tcp or udp",
            "-T", "fields",
            "-e", "frame.time_relative",
            "-e", "ip.src",
            "-e", "ip.dst",
            "-e", "tcp.srcport",
            "-e", "tcp.dstport",
            "-e", "udp.srcport",
            "-e", "udp.dstport",
            "-e", "frame.len",
            "-E", "header=y"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # 解析数据包
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            for line in lines[1:1000]:  # 限制数量
                parts = line.split('\t')
                if len(parts) >= 7:
                    try:
                        packet_info = {
                            "time": float(parts[0]),
                            "src_ip": parts[1],
                            "dst_ip": parts[2],
                            "src_port": parts[3] if parts[3] else parts[5],
                            "dst_port": parts[4] if parts[4] else parts[6],
                            "size": int(parts[7]) if len(parts) > 7 else 0
                        }
                        findings["timeline"].append(packet_info)
                        findings["packet_sizes"].append(packet_info["size"])
                    except:
                        pass
        
        # 识别可能的迷你世界服务器通信
        miniworld_ips = []
        for ip in findings["unique_ips"]:
            # 排除私有IP和常见IP
            if not ip.startswith(('192.168.', '10.', '172.16.', '127.')):
                if ip not in miniworld_ips:
                    miniworld_ips.append(ip)
        
        findings["server_communication"] = miniworld_ips[:10]
    
    except subprocess.TimeoutExpired:
        print("    [-] tshark分析超时")
    except Exception as e:
        print(f"    [-] 分析错误: {e}")
    
    return findings

def generate_report(all_findings):
    """生成分析报告"""
    print("\n[*] 生成分析报告...")
    
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = ANALYSIS_DIR / "PCAP_ANALYSIS_REPORT.md"
    
    report = f"""# 迷你世界PC端抓包分析报告

## 分析时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 抓包文件概览

"""
    
    for findings in all_findings:
        report += f"""### {findings['filename']}

- **总包数**: {findings['total_packets']}
- **唯一IP数**: {len(findings['unique_ips'])}
- **通信端口**: {', '.join(map(str, findings['unique_ports'][:10]))}
- **数据包大小范围**: {min(findings['packet_sizes']) if findings['packet_sizes'] else 0} - {max(findings['packet_sizes']) if findings['packet_sizes'] else 0} bytes

**可能的迷你世界服务器IP**:
{chr(10).join(['- `' + ip + '`' for ip in findings['server_communication']]) if findings['server_communication'] else '- 未识别'}

---

"""
    
    report += """## 关键发现

### 服务器通信
根据抓包分析，识别出以下可能的迷你世界服务器：

（待分析完成后填充）

### 协议特征

1. **通信端口**
   - 待识别

2. **数据包大小分布**
   - 待分析

3. **通信频率**
   - 待分析

## 下一步分析

1. **深度包分析**
   - 提取特定端口的数据包
   - 分析数据包内容（如果未加密）
   - 识别协议结构

2. **对比分析**
   - 对比国服/外服抓包差异
   - 对比登录/游戏/退出阶段的通信

3. **协议逆向**
   - 识别数据包格式
   - 分析加密方式
   - 提取关键字段

## 分析工具使用

```bash
# 使用tshark提取特定数据
tshark -r capture.pcapng -Y "tcp.port == PORT" -T fields -e data

# 导出特定流
tshark -r capture.pcapng -q -z follow,tcp,ascii,0
```
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[+] 报告保存: {report_file}")
    return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("迷你世界PC端抓包分析工具")
    print("=" * 60)
    
    # 检查tshark
    if not check_tshark():
        return False
    
    # 查找抓包文件
    pcap_files = find_capture_files()
    if not pcap_files:
        print("\n[!] 请先执行抓包并保存文件到:")
        print(f"    {CAPTURE_DIR}")
        return False
    
    # 分析所有抓包文件
    all_findings = []
    for pcap_file in pcap_files:
        findings = analyze_pcap(pcap_file)
        all_findings.append(findings)
    
    # 生成报告
    report_file = generate_report(all_findings)
    
    print("\n" + "=" * 60)
    print("分析完成!")
    print("=" * 60)
    print(f"\n分析报告: {report_file}")
    print("\n下一步:")
    print("1. 查看分析报告")
    print("2. 识别服务器IP和端口")
    print("3. 分析数据包结构")
    
    return True

if __name__ == "__main__":
    main()
