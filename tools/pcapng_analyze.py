#!/usr/bin/env python3
"""
PCAPNG 完整分析工具
"""

import struct
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set


def analyze_pcapng_full(filepath: str):
    """完整分析 PCAPNG 文件"""
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"File: {filepath}")
    print(f"Size: {len(data)} bytes")
    print()
    
    # 统计信息
    block_types = defaultdict(int)
    packets = []
    servers: Set[Tuple[str, int]] = set()
    
    # 解析所有块
    offset = 0
    block_count = 0
    
    while offset < len(data):
        if offset + 8 > len(data):
            break
        
        block_type = struct.unpack('<I', data[offset:offset+4])[0]
        block_len = struct.unpack('<I', data[offset+4:offset+8])[0]
        
        if block_len <= 0 or block_len > 10000000:
            break
        
        block_types[block_type] += 1
        
        # 解析增强型数据包
        if block_type == 0x00000006 and block_len >= 28:
            cap_len = struct.unpack('<I', data[offset+20:offset+24])[0]
            
            if cap_len >= 14 and offset + 28 + cap_len <= len(data):
                pkt_data = data[offset+28:offset+28+cap_len]
                
                if len(pkt_data) >= 14:
                    eth_type = struct.unpack('>H', pkt_data[12:14])[0]
                    
                    if eth_type == 0x0800 and len(pkt_data) >= 34:
                        ip_data = pkt_data[14:]
                        protocol = ip_data[9]
                        src_ip = '.'.join(str(b) for b in ip_data[12:16])
                        dst_ip = '.'.join(str(b) for b in ip_data[16:20])
                        
                        if protocol == 6 and len(ip_data) >= 40:  # TCP
                            tcp_data = ip_data[20:]
                            src_port = struct.unpack('>H', tcp_data[0:2])[0]
                            dst_port = struct.unpack('>H', tcp_data[2:4])[0]
                            
                            packets.append({
                                'src_ip': src_ip,
                                'src_port': src_port,
                                'dst_ip': dst_ip,
                                'dst_port': dst_port,
                                'size': cap_len
                            })
                            
                            # 记录服务器
                            if dst_port in [80, 443, 8080, 19921, 19601, 19701]:
                                servers.add((dst_ip, dst_port))
                            if src_port in [80, 443, 8080, 19921, 19601, 19701]:
                                servers.add((src_ip, src_port))
        
        offset += block_len
        block_count += 1
        
        # 显示进度
        if block_count % 10000 == 0:
            print(f"  Parsed {block_count} blocks... ({offset}/{len(data)} bytes)")
    
    print()
    print("=" * 50)
    print("Analysis Results")
    print("=" * 50)
    
    # 块类型统计
    print(f"\nTotal Blocks: {block_count}")
    print("\nBlock Types:")
    type_names = {
        0x0A0D0D0A: "Section Header",
        0x00000001: "Interface Description",
        0x00000002: "Packet",
        0x00000003: "Simple Packet",
        0x00000004: "Name Resolution",
        0x00000005: "Interface Statistics",
        0x00000006: "Enhanced Packet",
    }
    
    for block_type, count in sorted(block_types.items()):
        name = type_names.get(block_type, f"Unknown (0x{block_type:08X})")
        print(f"  {name}: {count}")
    
    # 数据包统计
    print(f"\nTotal TCP Packets: {len(packets)}")
    
    if packets:
        # 端口统计
        port_stats = defaultdict(int)
        for pkt in packets:
            port_stats[pkt['src_port']] += 1
            port_stats[pkt['dst_port']] += 1
        
        print("\nTop 10 Ports:")
        for port, count in sorted(port_stats.items(), key=lambda x: -x[1])[:10]:
            print(f"  Port {port}: {count} packets")
        
        # 服务器信息
        if servers:
            print("\nDetected Servers:")
            for ip, port in sorted(servers):
                print(f"  {ip}:{port}")
        
        # IP 统计
        ip_stats = defaultdict(int)
        for pkt in packets:
            ip_stats[pkt['src_ip']] += 1
            ip_stats[pkt['dst_ip']] += 1
        
        print("\nTop 10 IPs:")
        for ip, count in sorted(ip_stats.items(), key=lambda x: -x[1])[:10]:
            print(f"  {ip}: {count} packets")
    
    print("=" * 50)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: pcapng_analyze.py <pcapng_file>")
        sys.exit(1)
    
    analyze_pcapng_full(sys.argv[1])
