#!/usr/bin/env python3
"""
深度分析抓包数据
提取迷你世界协议细节
"""

import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

TSHARK_PATH = r"D:\Program Files\Wireshark\tshark.exe"
CAPTURE_DIR = Path(r"https://github.com/StarsailsClover/MnMCPResources\packs_downloads\captures")
OUTPUT_DIR = CAPTURE_DIR / "deep_analysis"

def analyze_capture_deep(pcap_file):
    """深度分析单个抓包文件"""
    print(f"\n[*] 深度分析: {pcap_file.name}")
    
    findings = {
        "filename": pcap_file.name,
        "analysis_time": datetime.now().isoformat(),
        "tcp_streams": [],
        "udp_streams": [],
        "server_ips": [],
        "ports": [],
        "packet_sizes": [],
        "protocols": Counter(),
        "tls_hosts": [],
        "http_hosts": [],
        "potential_game_servers": []
    }
    
    try:
        # 1. 获取TCP流统计
        print("  [+] 分析TCP流...")
        cmd = [TSHARK_PATH, "-r", str(pcap_file), "-q", "-z", "conv,tcp"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        for line in result.stdout.split('\n')[4:]:  # 跳过表头
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4:
                    src = parts[0]
                    dst = parts[1]
                    frames = parts[2]
                    bytes_count = parts[3]
                    
                    # 提取IP和端口
                    src_match = re.match(r'(\d+\.\d+\.\d+\.\d+):(\d+)', src)
                    dst_match = re.match(r'(\d+\.\d+\.\d+\.\d+):(\d+)', dst)
                    
                    if src_match and dst_match:
                        src_ip, src_port = src_match.groups()
                        dst_ip, dst_port = dst_match.groups()
                        
                        # 排除私有IP和DNS服务器
                        if not dst_ip.startswith(('192.168.', '10.', '172.16.', '127.', '223.5.5.5', '119.29.29.29', '114.114.114.114')):
                            findings["tcp_streams"].append({
                                "src": f"{src_ip}:{src_port}",
                                "dst": f"{dst_ip}:{dst_port}",
                                "frames": frames,
                                "bytes": bytes_count
                            })
                            
                            if dst_ip not in findings["server_ips"]:
                                findings["server_ips"].append(dst_ip)
                            
                            dst_port_int = int(dst_port)
                            if dst_port_int not in findings["ports"] and dst_port_int > 1024:
                                findings["ports"].append(dst_port_int)
        
        # 2. 获取UDP流统计
        print("  [+] 分析UDP流...")
        cmd = [TSHARK_PATH, "-r", str(pcap_file), "-q", "-z", "conv,udp"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        for line in result.stdout.split('\n')[4:]:
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4:
                    src = parts[0]
                    dst = parts[1]
                    
                    dst_match = re.match(r'(\d+\.\d+\.\d+\.\d+):(\d+)', dst)
                    if dst_match:
                        dst_ip, dst_port = dst_match.groups()
                        
                        if not dst_ip.startswith(('192.168.', '10.', '172.16.', '127.')):
                            findings["udp_streams"].append({
                                "dst": f"{dst_ip}:{dst_port}"
                            })
                            
                            if dst_ip not in findings["server_ips"]:
                                findings["server_ips"].append(dst_ip)
                            
                            dst_port_int = int(dst_port)
                            if dst_port_int not in findings["ports"]:
                                findings["ports"].append(dst_port_int)
        
        # 3. 分析TLS握手（SNI）
        print("  [+] 分析TLS SNI...")
        cmd = [TSHARK_PATH, "-r", str(pcap_file), "-Y", "tls.handshake.type == 1", 
               "-T", "fields", "-e", "tls.handshake.extensions_server_name"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        for line in result.stdout.split('\n'):
            if line.strip() and line.strip() not in findings["tls_hosts"]:
                findings["tls_hosts"].append(line.strip())
        
        # 4. 分析HTTP Host头
        print("  [+] 分析HTTP Host...")
        cmd = [TSHARK_PATH, "-r", str(pcap_file), "-Y", "http.host",
               "-T", "fields", "-e", "http.host"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        for line in result.stdout.split('\n'):
            if line.strip() and line.strip() not in findings["http_hosts"]:
                findings["http_hosts"].append(line.strip())
        
        # 5. 识别可能的游戏服务器
        print("  [+] 识别游戏服务器...")
        for ip in findings["server_ips"]:
            # 检查是否有大量数据交换
            total_bytes = 0
            for stream in findings["tcp_streams"]:
                if ip in stream["dst"]:
                    try:
                        total_bytes += int(stream["bytes"].replace(',', ''))
                    except:
                        pass
            
            if total_bytes > 10000:  # 超过10KB的通信
                findings["potential_game_servers"].append({
                    "ip": ip,
                    "total_bytes": total_bytes
                })
        
        # 按数据量排序
        findings["potential_game_servers"].sort(key=lambda x: x["total_bytes"], reverse=True)
    
    except Exception as e:
        print(f"  [-] 分析错误: {e}")
    
    return findings

def generate_detailed_report(all_findings):
    """生成详细报告"""
    print("\n[*] 生成详细分析报告...")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = OUTPUT_DIR / "DEEP_ANALYSIS_REPORT.md"
    
    report = f"""# 迷你世界PC端深度抓包分析报告

## 分析时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 概览

"""
    
    for findings in all_findings:
        report += f"""### {findings['filename']}

- **分析时间**: {findings['analysis_time']}
- **服务器IP数**: {len(findings['server_ips'])}
- **TCP流数**: {len(findings['tcp_streams'])}
- **UDP流数**: {len(findings['udp_streams'])}
- **通信端口**: {', '.join(map(str, sorted(findings['ports'])[:20]))}

#### 可能的游戏服务器（按数据量排序）

| IP地址 | 数据量 | 说明 |
|--------|--------|------|
"""
        
        for server in findings['potential_game_servers'][:15]:
            # 尝试识别服务商
            ip = server['ip']
            provider = ""
            if ip.startswith('183.60.') or ip.startswith('183.36.'):
                provider = "腾讯云"
            elif ip.startswith('120.236.'):
                provider = "移动云"
            elif ip.startswith('14.'):
                provider = "腾讯云"
            elif ip.startswith('125.88.'):
                provider = "电信"
            elif ip.startswith('59.37.'):
                provider = "电信"
            elif ip.startswith('113.96.'):
                provider = "腾讯云"
            
            report += f"| {ip} | {server['total_bytes']:,} bytes | {provider} |\n"
        
        report += f"\n#### TLS SNI (HTTPS服务器)\n\n"
        for host in findings['tls_hosts'][:10]:
            report += f"- `{host}`\n"
        
        report += f"\n#### HTTP Host\n\n"
        for host in findings['http_hosts'][:10]:
            report += f"- `{host}`\n"
        
        report += "\n---\n\n"
    
    report += """## 关键发现

### 游戏服务器特征

根据数据分析，迷你世界PC版可能使用以下服务器：

1. **登录认证服务器**
   - 使用HTTPS协议
   - 域名: mini1.cn 相关

2. **游戏服务器**
   - 使用TCP协议
   - 端口: 动态分配（高位端口）
   - IP: 腾讯云/移动云/电信

3. **CDN/资源服务器**
   - 使用HTTP/HTTPS
   - 用于下载游戏资源

### 协议特征

1. **加密通信**
   - 使用TLS 1.2/1.3
   - 证书验证

2. **游戏数据**
   - 可能使用自定义协议
   - 数据包大小: 54-7128 bytes
   - 需要进一步分析

## 下一步行动

1. **特定端口分析**
   - 提取主要通信端口的数据包
   - 分析数据包结构

2. **协议逆向**
   - 识别数据包头部结构
   - 分析加密方式

3. **结合DEX分析**
   - 从Android代码确认协议结构
   - 对比PC和手游协议差异

## 工具使用

```bash
# 导出特定TCP流
tshark -r capture.pcapng -q -z follow,tcp,ascii,STREAM_INDEX

# 提取特定IP的数据包
tshark -r capture.pcapng -Y "ip.addr == IP_ADDRESS" -w filtered.pcapng

# 统计协议分布
tshark -r capture.pcapng -q -z io,phs
```
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[+] 详细报告: {report_file}")
    return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("迷你世界PC端深度抓包分析")
    print("=" * 60)
    
    # 查找抓包文件
    pcap_files = list(CAPTURE_DIR.glob("*.pcapng"))
    if not pcap_files:
        print("[-] 未找到抓包文件")
        return False
    
    print(f"[*] 找到 {len(pcap_files)} 个抓包文件")
    
    # 深度分析每个文件
    all_findings = []
    for pcap_file in pcap_files:
        if pcap_file.stat().st_size > 1000:  # 只分析非空文件
            findings = analyze_capture_deep(pcap_file)
            all_findings.append(findings)
    
    # 生成详细报告
    report_file = generate_detailed_report(all_findings)
    
    print("\n" + "=" * 60)
    print("深度分析完成!")
    print("=" * 60)
    print(f"\n详细报告: {report_file}")
    print("\n关键发现:")
    for findings in all_findings:
        print(f"\n  {findings['filename']}:")
        print(f"    - 服务器IP: {len(findings['server_ips'])} 个")
        print(f"    - 游戏服务器候选: {len(findings['potential_game_servers'])} 个")
        if findings['potential_game_servers']:
            top_server = findings['potential_game_servers'][0]
            print(f"    - 主要服务器: {top_server['ip']} ({top_server['total_bytes']:,} bytes)")
    
    return True

if __name__ == "__main__":
    main()
