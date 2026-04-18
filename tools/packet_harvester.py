#!/usr/bin/env python3
"""
数据包收集器 (基于 Universal GameApp Decryptor)

解析 TCP/UDP 数据包，提取业务逻辑
"""

import struct
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class HarvestedPacket:
    """收集的数据包"""
    protocol: str      # TCP/UDP
    port: int
    index: int
    raw_data: bytes
    decoded_data: Any


class PacketHarvester:
    """
    数据包收集器
    
    基于 Universal GameApp Decryptor 的实现
    """
    
    # 端口映射
    PORTS = {
        'tcp': [19701],
        'udp': [19601, 19701],
    }
    
    def __init__(self, pcap_data: bytes = None):
        self.pcap_data = pcap_data
        self.packets: List[HarvestedPacket] = []
        self.output_log: str = "harvest_log.txt"
    
    def harvest_tcp_19701(self, data: bytes) -> Optional[Dict]:
        """
        收集 TCP 19701 端口数据 (业务逻辑)
        
        格式: 4字节 WebSocket 头 + msgpack 数据
        """
        try:
            if len(data) < 4:
                return None
            
            # 跳过 4 字节 WebSocket 头
            payload = data[4:]
            
            # 尝试解析 msgpack (简化实现)
            # 实际应该使用 msgpack 库
            return self._parse_msgpack_simple(payload)
            
        except Exception as e:
            logger.error(f"TCP 19701 parse error: {e}")
            return None
    
    def harvest_udp_19601(self, data: bytes) -> Optional[Dict]:
        """
        收集 UDP 19601 端口数据 (物理坐标)
        
        格式: 12字节坐标头 + protobuf
        """
        try:
            if len(data) < 12:
                return None
            
            # 解析 12 字节坐标头
            x, y, z = struct.unpack('>iii', data[:12])
            
            # protobuf 数据
            protobuf_data = data[12:]
            
            return {
                'type': 'physical_coords',
                'coords': {
                    'x': x / 100.0,  # 缩放因子
                    'y': y / 100.0,
                    'z': z / 100.0,
                },
                'protobuf_len': len(protobuf_data),
                'raw': protobuf_data.hex()[:50] + '...' if len(protobuf_data) > 25 else protobuf_data.hex()
            }
            
        except Exception as e:
            logger.error(f"UDP 19601 parse error: {e}")
            return None
    
    def harvest_udp_19701(self, data: bytes) -> Optional[Dict]:
        """
        收集 UDP 19701 端口数据 (加密数据)
        
        格式: 加密数据，需要解密
        """
        try:
            # 这里需要实现解密逻辑
            # 基于之前的 ECDH + AES-GCM
            return {
                'type': 'encrypted',
                'len': len(data),
                'raw': data.hex()[:50] + '...' if len(data) > 25 else data.hex()
            }
            
        except Exception as e:
            logger.error(f"UDP 19701 parse error: {e}")
            return None
    
    def _parse_msgpack_simple(self, data: bytes) -> Dict:
        """简化的 msgpack 解析"""
        # 实际应该使用 msgpack 库
        # 这里只是简单返回原始数据
        return {
            'type': 'msgpack',
            'len': len(data),
            'raw': data.hex()[:50] + '...' if len(data) > 25 else data.hex()
        }
    
    def process_packet(self, protocol: str, port: int, data: bytes, index: int = 0) -> Optional[HarvestedPacket]:
        """处理单个数据包"""
        decoded = None
        
        if protocol == 'tcp' and port == 19701:
            decoded = self.harvest_tcp_19701(data)
        elif protocol == 'udp' and port == 19601:
            decoded = self.harvest_udp_19601(data)
        elif protocol == 'udp' and port == 19701:
            decoded = self.harvest_udp_19701(data)
        
        if decoded:
            packet = HarvestedPacket(
                protocol=protocol,
                port=port,
                index=index,
                raw_data=data,
                decoded_data=decoded
            )
            self.packets.append(packet)
            return packet
        
        return None
    
    def generate_report(self) -> str:
        """生成报告"""
        lines = []
        lines.append("=" * 70)
        lines.append("UNIVERSAL PROTOCOL HARVEST REPORT")
        lines.append("=" * 70)
        lines.append(f"Total packets: {len(self.packets)}")
        lines.append("")
        
        # 按端口统计
        port_stats = {}
        for pkt in self.packets:
            key = f"{pkt.protocol}_{pkt.port}"
            port_stats[key] = port_stats.get(key, 0) + 1
        
        lines.append("Port Statistics:")
        for port, count in sorted(port_stats.items()):
            lines.append(f"  {port}: {count} packets")
        lines.append("")
        
        # 详细数据
        lines.append("Packet Details:")
        for i, pkt in enumerate(self.packets[:20]):  # 只显示前20个
            lines.append(f"\n[{i+1}] {pkt.protocol.upper()}:{pkt.port}")
            lines.append(f"  Raw: {len(pkt.raw_data)} bytes")
            lines.append(f"  Decoded: {json.dumps(pkt.decoded_data, indent=2, ensure_ascii=False)}")
        
        return "\n".join(lines)
    
    def save_report(self, filename: str = None):
        """保存报告"""
        if filename is None:
            filename = self.output_log
        
        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Report saved to: {filename}")


def main():
    """测试"""
    # 创建测试数据
    harvester = PacketHarvester()
    
    # 模拟 TCP 19701 数据
    test_tcp = b'\x00\x00\x00\x10' + b'test data msgpack'
    harvester.process_packet('tcp', 19701, test_tcp, 0)
    
    # 模拟 UDP 19601 数据 (坐标)
    test_udp_19601 = struct.pack('>iii', 10000, 6400, 20000) + b'protobuf data'
    harvester.process_packet('udp', 19601, test_udp_19601, 1)
    
    # 模拟 UDP 19701 数据 (加密)
    test_udp_19701 = b'encrypted data here'
    harvester.process_packet('udp', 19701, test_udp_19701, 2)
    
    # 生成报告
    print(harvester.generate_report())


if __name__ == '__main__':
    main()
