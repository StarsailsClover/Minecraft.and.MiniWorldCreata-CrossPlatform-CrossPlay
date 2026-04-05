#!/usr/bin/env python3
"""
PCAPNG 文件解析器

解析 PCAPNG 格式的抓包文件
"""

import struct
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


# PCAPNG Block Types
BLOCK_TYPE_SECTION_HEADER = 0x0A0D0D0A
BLOCK_TYPE_INTERFACE_DESCRIPTION = 0x00000001
BLOCK_TYPE_PACKET = 0x00000002
BLOCK_TYPE_SIMPLE_PACKET = 0x00000003
BLOCK_TYPE_NAME_RESOLUTION = 0x00000004
BLOCK_TYPE_INTERFACE_STATISTICS = 0x00000005
BLOCK_TYPE_ENHANCED_PACKET = 0x00000006
BLOCK_TYPE_IRIG_TIMESTAMP = 0x00000007
BLOCK_TYPE_ARINC_429 = 0x00000008
BLOCK_TYPE_SYSTEMD_JOURNAL_EXPORT = 0x00000009
BLOCK_TYPE_DECRYPTED_SECRETS = 0x0000000A
BLOCK_TYPE_DSB = 0x0000000A  # Same as above
BLOCK_TYPE_CUSTOM = 0x00000BAD
BLOCK_TYPE_CUSTOM_NON_COPY = 0x40000BAD


@dataclass
class PCAPNGBlock:
    """PCAPNG 数据块"""
    block_type: int
    block_total_length: int
    data: bytes
    block_total_length2: int


@dataclass
class UDPPacket:
    """UDP 数据包"""
    timestamp: float
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    data: bytes


class PCAPNGParser:
    """PCAPNG 解析器"""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.blocks: List[PCAPNGBlock] = []
        self.packets: List[UDPPacket] = []
        self.little_endian = True
        
    def parse(self) -> bool:
        """解析 PCAPNG 文件"""
        try:
            with open(self.filepath, 'rb') as f:
                data = f.read()
            
            print(f"✓ File size: {len(data)} bytes")
            
            # 检查魔数
            magic = struct.unpack('<I', data[:4])[0]
            if magic != BLOCK_TYPE_SECTION_HEADER:
                print(f"✗ Invalid magic: 0x{magic:08X}")
                return False
            
            print("✓ PCAPNG format confirmed")
            
            # 解析所有块
            offset = 0
            block_count = 0
            
            while offset < len(data):
                block = self._parse_block(data, offset)
                if not block:
                    break
                
                self.blocks.append(block)
                block_count += 1
                
                # 处理增强型数据包块
                if block.block_type == BLOCK_TYPE_ENHANCED_PACKET:
                    self._parse_enhanced_packet(block)
                
                offset += block.block_total_length
            
            print(f"✓ Parsed {block_count} blocks")
            print(f"✓ Extracted {len(self.packets)} packets")
            
            return True
            
        except Exception as e:
            print(f"✗ Parse error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _parse_block(self, data: bytes, offset: int) -> Optional[PCAPNGBlock]:
        """解析单个块"""
        if offset + 12 > len(data):
            return None
        
        try:
            # 读取块类型和长度
            block_type = struct.unpack('<I', data[offset:offset+4])[0]
            block_total_length = struct.unpack('<I', data[offset+4:offset+8])[0]
            
            if block_total_length < 12 or offset + block_total_length > len(data):
                return None
            
            # 读取块数据
            block_data = data[offset+8:offset+block_total_length-4]
            
            # 读取尾部长度（应该与头部相同）
            block_total_length2 = struct.unpack('<I', 
                data[offset+block_total_length-4:offset+block_total_length])[0]
            
            if block_total_length != block_total_length2:
                print(f"⚠ Block length mismatch: {block_total_length} != {block_total_length2}")
            
            return PCAPNGBlock(
                block_type=block_type,
                block_total_length=block_total_length,
                data=block_data,
                block_total_length2=block_total_length2
            )
            
        except Exception as e:
            print(f"✗ Block parse error at offset {offset}: {e}")
            return None
    
    def _parse_enhanced_packet(self, block: PCAPNGBlock):
        """解析增强型数据包块"""
        try:
            data = block.data
            
            # 解析头部 (Interface ID + Timestamp + Captured Len + Original Len)
            # 共 20 字节
            if len(data) < 20:
                return
            
            interface_id = struct.unpack('<I', data[0:4])[0]
            timestamp_high = struct.unpack('<I', data[4:8])[0]
            timestamp_low = struct.unpack('<I', data[8:12])[0]
            captured_len = struct.unpack('<I', data[12:16])[0]
            original_len = struct.unpack('<I', data[16:20])[0]
            
            # 计算时间戳（微秒）
            timestamp = (timestamp_high << 32 | timestamp_low) / 1000000.0
            
            # 获取数据包内容
            if 20 + captured_len > len(data):
                return
            
            packet_data = data[20:20+captured_len]
            
            # 解析以太网帧
            if len(packet_data) < 14:
                return
            
            eth_type = struct.unpack('>H', packet_data[12:14])[0]
            
            # IPv4
            if eth_type == 0x0800:
                ip_header = packet_data[14:]
                
                if len(ip_header) < 20:
                    return
                
                # 解析 IP 头部
                ip_version_ihl = ip_header[0]
                ip_header_len = (ip_version_ihl & 0x0F) * 4
                
                if len(ip_header) < ip_header_len:
                    return
                
                protocol = ip_header[9]
                src_ip = '.'.join(str(b) for b in ip_header[12:16])
                dst_ip = '.'.join(str(b) for b in ip_header[16:20])
                
                # UDP (protocol = 17)
                if protocol == 17:
                    if len(ip_header) < ip_header_len + 8:
                        return
                    
                    udp_header = ip_header[ip_header_len:]
                    src_port = struct.unpack('>H', udp_header[0:2])[0]
                    dst_port = struct.unpack('>H', udp_header[2:4])[0]
                    udp_len = struct.unpack('>H', udp_header[4:6])[0]
                    
                    # UDP 数据
                    udp_data_start = ip_header_len + 8
                    udp_data_end = min(udp_data_start + udp_len - 8, len(ip_header))
                    udp_data = ip_header[udp_data_start:udp_data_end]
                    
                    packet = UDPPacket(
                        timestamp=timestamp,
                        src_ip=src_ip,
                        src_port=src_port,
                        dst_ip=dst_ip,
                        dst_port=dst_port,
                        data=udp_data
                    )
                    
                    self.packets.append(packet)
                    
        except Exception as e:
            # 静默处理解析错误，避免输出过多
            pass
    
    def get_mnw_packets(self) -> List[UDPPacket]:
        """获取迷你世界数据包"""
        mnw_ports = [8080, 19921, 19601, 19701, 8081]
        return [
            pkt for pkt in self.packets
            if pkt.src_port in mnw_ports or pkt.dst_port in mnw_ports
        ]
    
    def analyze(self):
        """分析数据包"""
        print("\n=== Packet Analysis ===")
        
        # 统计端口
        port_stats: Dict[int, int] = {}
        for pkt in self.packets:
            port_stats[pkt.src_port] = port_stats.get(pkt.src_port, 0) + 1
            port_stats[pkt.dst_port] = port_stats.get(pkt.dst_port, 0) + 1
        
        print("\nPort Statistics:")
        for port, count in sorted(port_stats.items(), key=lambda x: -x[1])[:10]:
            print(f"  Port {port}: {count} packets")
        
        # 迷你世界数据包
        mnw_packets = self.get_mnw_packets()
        print(f"\nMiniWorld Packets: {len(mnw_packets)}")
        
        if mnw_packets:
            # 统计 MNW 端口
            mnw_port_stats: Dict[int, int] = {}
            for pkt in mnw_packets:
                port = pkt.src_port if pkt.src_port in [8080, 19921, 19601, 19701, 8081] else pkt.dst_port
                mnw_port_stats[port] = mnw_port_stats.get(port, 0) + 1
            
            print("\nMiniWorld Port Statistics:")
            for port, count in sorted(mnw_port_stats.items()):
                print(f"  Port {port}: {count} packets")
            
            # 提取服务器地址
            servers: Dict[Tuple[str, int], int] = {}
            for pkt in mnw_packets:
                if pkt.dst_port in [8080, 19921, 19601, 19701, 8081]:
                    key = (pkt.dst_ip, pkt.dst_port)
                    servers[key] = servers.get(key, 0) + 1
            
            if servers:
                print("\nDetected Servers:")
                for (ip, port), count in sorted(servers.items(), key=lambda x: -x[1]):
                    print(f"  {ip}:{port} ({count} packets)")
            
            # 数据包大小统计
            sizes = [len(pkt.data) for pkt in mnw_packets]
            print(f"\nPacket Size Statistics:")
            print(f"  Min: {min(sizes)} bytes")
            print(f"  Max: {max(sizes)} bytes")
            print(f"  Avg: {sum(sizes) / len(sizes):.1f} bytes")
            
            # 显示前几个数据包
            print("\nFirst 5 MiniWorld Packets:")
            for i, pkt in enumerate(mnw_packets[:5]):
                print(f"  {i+1}. {pkt.src_ip}:{pkt.src_port} -> {pkt.dst_ip}:{pkt.dst_port}")
                print(f"     Size: {len(pkt.data)} bytes, Data: {pkt.data[:20].hex()}...")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: pcapng_parser.py <pcapng_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    parser = PCAPNGParser(filepath)
    
    if parser.parse():
        parser.analyze()
        print("\n✓ Analysis complete")
        return 0
    else:
        print("\n✗ Analysis failed")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
