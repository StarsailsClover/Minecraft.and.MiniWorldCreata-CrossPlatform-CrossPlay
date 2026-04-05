#!/usr/bin/env python3
"""
PCAP 抓包分析工具

分析迷你世界的网络流量
"""

import sys
import struct
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.protocol import BusinessMessage, BusinessCmdID


@dataclass
class UDPPacket:
    """UDP 数据包"""
    timestamp: float
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    data: bytes
    
    @property
    def is_mnw_traffic(self) -> bool:
        """判断是否为迷你世界流量"""
        # 迷你世界常用端口
        mnw_ports = [8080, 19921, 19601, 19701, 8081]
        return self.src_port in mnw_ports or self.dst_port in mnw_ports


class PCAPAnalyzer:
    """PCAP 分析器"""
    
    def __init__(self, pcap_path: str):
        self.pcap_path = Path(pcap_path)
        self.packets: List[UDPPacket] = []
        self.mnw_packets: List[UDPPacket] = []
        
    def analyze(self) -> bool:
        """分析 PCAP 文件"""
        try:
            # 尝试使用 scapy
            from scapy.all import rdpcap, UDP, IP
            
            packets = rdpcap(str(self.pcap_path))
            
            for pkt in packets:
                if UDP in pkt and IP in pkt:
                    udp_pkt = UDPPacket(
                        timestamp=float(pkt.time),
                        src_ip=pkt[IP].src,
                        src_port=pkt[UDP].sport,
                        dst_ip=pkt[IP].dst,
                        dst_port=pkt[UDP].dport,
                        data=bytes(pkt[UDP].payload)
                    )
                    
                    self.packets.append(udp_pkt)
                    
                    if udp_pkt.is_mnw_traffic:
                        self.mnw_packets.append(udp_pkt)
            
            print(f"✓ Loaded {len(self.packets)} packets")
            print(f"✓ Found {len(self.mnw_packets)} MiniWorld packets")
            
            return True
            
        except ImportError:
            print("✗ scapy not installed, using manual parser")
            return self._parse_manual()
        except Exception as e:
            print(f"✗ Failed to analyze: {e}")
            return False
    
    def _parse_manual(self) -> bool:
        """手动解析 PCAP"""
        try:
            with open(self.pcap_path, 'rb') as f:
                data = f.read()
            
            # 检查 PCAP 魔数
            if data[:4] == b'\xa1\xb2\xc3\xd4' or data[:4] == b'\xd4\xc3\xb2\xa1':
                print("✓ PCAP format detected")
                # TODO: 实现完整的 PCAP 解析
                print("✗ Full PCAP parsing not implemented")
                return False
            
            # 检查 PCAPNG 魔数
            if data[:4] == b'\x0a\x0d\x0d\x0a':
                print("✓ PCAPNG format detected")
                # TODO: 实现完整的 PCAPNG 解析
                print("✗ Full PCAPNG parsing not implemented")
                return False
            
            return False
            
        except Exception as e:
            print(f"✗ Manual parse failed: {e}")
            return False
    
    def analyze_mnw_packets(self):
        """分析迷你世界数据包"""
        print("\n=== MiniWorld Packet Analysis ===")
        
        # 统计端口
        port_stats: Dict[int, int] = {}
        for pkt in self.mnw_packets:
            port = pkt.src_port if pkt.src_port in [8080, 19921, 19601, 19701, 8081] else pkt.dst_port
            port_stats[port] = port_stats.get(port, 0) + 1
        
        print("\nPort Statistics:")
        for port, count in sorted(port_stats.items()):
            print(f"  Port {port}: {count} packets")
        
        # 分析数据包大小
        sizes = [len(pkt.data) for pkt in self.mnw_packets]
        if sizes:
            print(f"\nPacket Size Statistics:")
            print(f"  Min: {min(sizes)} bytes")
            print(f"  Max: {max(sizes)} bytes")
            print(f"  Avg: {sum(sizes) / len(sizes):.1f} bytes")
        
        # 尝试解析业务消息
        print("\nTrying to parse business messages...")
        parsed_count = 0
        for pkt in self.mnw_packets[:10]:  # 只分析前10个
            msg = BusinessMessage.decode(pkt.data)
            if msg:
                print(f"  ✓ CmdID: 0x{msg.cmd_id:04X}, UIN: {msg.uin}, Data: {len(msg.data)} bytes")
                parsed_count += 1
            else:
                print(f"  ✗ Failed to parse ({len(pkt.data)} bytes)")
        
        print(f"\nParsed {parsed_count}/10 packets")
    
    def extract_server_info(self) -> List[Tuple[str, int]]:
        """提取服务器信息"""
        servers = set()
        
        for pkt in self.mnw_packets:
            if pkt.dst_port in [8080, 19921, 19601, 19701, 8081]:
                servers.add((pkt.dst_ip, pkt.dst_port))
            if pkt.src_port in [8080, 19921, 19601, 19701, 8081]:
                servers.add((pkt.src_ip, pkt.src_port))
        
        return sorted(servers)
    
    def print_summary(self):
        """打印摘要"""
        print("\n" + "=" * 50)
        print("PCAP Analysis Summary")
        print("=" * 50)
        print(f"File: {self.pcap_path}")
        print(f"Total packets: {len(self.packets)}")
        print(f"MiniWorld packets: {len(self.mnw_packets)}")
        
        servers = self.extract_server_info()
        if servers:
            print(f"\nDetected Servers:")
            for ip, port in servers:
                print(f"  {ip}:{port}")
        
        print("=" * 50)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze MiniWorld PCAP files')
    parser.add_argument('pcap_file', help='Path to PCAP file')
    args = parser.parse_args()
    
    analyzer = PCAPAnalyzer(args.pcap_file)
    
    if analyzer.analyze():
        analyzer.analyze_mnw_packets()
        analyzer.print_summary()
        return 0
    else:
        print("✗ Analysis failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
