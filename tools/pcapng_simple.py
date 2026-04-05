#!/usr/bin/env python3
"""
PCAPNG 文件分析工具 - 简单版
"""

import struct
import sys
from pathlib import Path


def analyze_pcapng(filepath: str):
    """分析 PCAPNG 文件"""
    with open(filepath, 'rb') as f:
        data = f.read(2000)
    
    print(f"File: {filepath}")
    print(f"First 2000 bytes analysis:")
    print()
    
    # 检查魔数
    magic = struct.unpack('<I', data[:4])[0]
    print(f"Magic: 0x{magic:08X}")
    
    # 解析前几个块
    offset = 0
    block_count = 0
    
    while offset < len(data) and block_count < 20:
        if offset + 8 > len(data):
            break
        
        block_type = struct.unpack('<I', data[offset:offset+4])[0]
        block_len = struct.unpack('<I', data[offset+4:offset+8])[0]
        
        print(f"Block {block_count}: Offset={offset}, Type=0x{block_type:08X}, Length={block_len}")
        
        # 显示块类型名称
        type_names = {
            0x0A0D0D0A: "Section Header",
            0x00000001: "Interface Description",
            0x00000002: "Packet",
            0x00000003: "Simple Packet",
            0x00000004: "Name Resolution",
            0x00000005: "Interface Statistics",
            0x00000006: "Enhanced Packet",
        }
        
        if block_type in type_names:
            print(f"  -> {type_names[block_type]}")
        
        # 如果是 Section Header，显示字节序信息
        if block_type == 0x0A0D0D0A and block_len >= 28:
            byte_order_magic = struct.unpack('<I', data[offset+8:offset+12])[0]
            major_version = struct.unpack('<H', data[offset+12:offset+14])[0]
            minor_version = struct.unpack('<H', data[offset+14:offset+16])[0]
            section_len = struct.unpack('<Q', data[offset+16:offset+24])[0]
            
            print(f"  Byte Order: 0x{byte_order_magic:08X}")
            print(f"  Version: {major_version}.{minor_version}")
            print(f"  Section Length: {section_len}")
        
        # 如果是 Interface Description，显示链路类型
        if block_type == 0x00000001 and block_len >= 16:
            link_type = struct.unpack('<H', data[offset+8:offset+10])[0]
            print(f"  Link Type: {link_type}")
        
        # 如果是 Enhanced Packet，显示包信息
        if block_type == 0x00000006 and block_len >= 28:
            iface_id = struct.unpack('<I', data[offset+8:offset+12])[0]
            ts_high = struct.unpack('<I', data[offset+12:offset+16])[0]
            ts_low = struct.unpack('<I', data[offset+16:offset+20])[0]
            cap_len = struct.unpack('<I', data[offset+20:offset+24])[0]
            orig_len = struct.unpack('<I', data[offset+24:offset+28])[0]
            
            print(f"  Interface ID: {iface_id}")
            print(f"  Timestamp: {ts_high}:{ts_low}")
            print(f"  Captured Length: {cap_len}")
            print(f"  Original Length: {orig_len}")
            
            # 尝试解析以太网帧
            if cap_len >= 14:
                pkt_data = data[offset+28:offset+28+cap_len]
                eth_type = struct.unpack('>H', pkt_data[12:14])[0]
                print(f"  EtherType: 0x{eth_type:04X}")
                
                # IPv4
                if eth_type == 0x0800 and cap_len >= 34:
                    ip_data = pkt_data[14:]
                    ip_version = (ip_data[0] >> 4) & 0x0F
                    ip_header_len = (ip_data[0] & 0x0F) * 4
                    protocol = ip_data[9]
                    src_ip = '.'.join(str(b) for b in ip_data[12:16])
                    dst_ip = '.'.join(str(b) for b in ip_data[16:20])
                    
                    print(f"  IP Version: {ip_version}")
                    print(f"  IP Header Len: {ip_header_len}")
                    print(f"  Protocol: {protocol}")
                    print(f"  Src IP: {src_ip}")
                    print(f"  Dst IP: {dst_ip}")
                    
                    # UDP
                    if protocol == 17 and len(ip_data) >= ip_header_len + 8:
                        udp_data = ip_data[ip_header_len:]
                        src_port = struct.unpack('>H', udp_data[0:2])[0]
                        dst_port = struct.unpack('>H', udp_data[2:4])[0]
                        udp_len = struct.unpack('>H', udp_data[4:6])[0]
                        
                        print(f"  UDP Src Port: {src_port}")
                        print(f"  UDP Dst Port: {dst_port}")
                        print(f"  UDP Length: {udp_len}")
        
        if block_len <= 0 or block_len > 1000000:
            break
        
        offset += block_len
        block_count += 1
        print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: pcapng_simple.py <pcapng_file>")
        sys.exit(1)
    
    analyze_pcapng(sys.argv[1])
