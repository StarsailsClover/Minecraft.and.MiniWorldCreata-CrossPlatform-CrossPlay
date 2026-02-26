#!/usr/bin/env python3
"""
WebSocket抓包分析工具
用于从Wireshark/mimtproxy捕获的数据中提取MiniWorld方块ID
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

class WebSocketAnalyzer:
    """分析WebSocket数据包中的方块信息"""
    
    def __init__(self):
        self.packets: List[Dict] = []
        self.block_events: List[Dict] = []
    
    def parse_pcap(self, pcap_file: str) -> List[Dict]:
        """
        解析pcap/pcapng文件
        注意：需要安装pyshark或scapy
        """
        try:
            import pyshark
            
            cap = pyshark.FileCapture(pcap_file, display_filter='websocket')
            packets = []
            
            for pkt in cap:
                if hasattr(pkt, 'websocket'):
                    packet_info = {
                        'timestamp': pkt.sniff_time.isoformat(),
                        'src': pkt.ip.src if hasattr(pkt, 'ip') else 'unknown',
                        'dst': pkt.ip.dst if hasattr(pkt, 'ip') else 'unknown',
                        'payload': self._extract_payload(pkt)
                    }
                    packets.append(packet_info)
            
            return packets
        except ImportError:
            print("[-] pyshark not installed. Install with: pip install pyshark")
            return []
        except Exception as e:
            print(f"[-] Error parsing pcap: {e}")
            return []
    
    def _extract_payload(self, pkt) -> bytes:
        """提取WebSocket payload"""
        try:
            if hasattr(pkt.websocket, 'payload'):
                return bytes.fromhex(pkt.websocket.payload.replace(':', ''))
            return b''
        except:
            return b''
    
    def analyze_payload(self, payload: bytes) -> Optional[Dict]:
        """
        分析数据包payload，寻找方块相关信息
        
        迷你世界WebSocket协议推测：
        - 可能使用二进制协议
        - 可能包含操作类型（放置/破坏方块）
        - 包含坐标和方块ID
        """
        if len(payload) < 4:
            return None
        
        # 尝试不同的解析方式
        result = {
            'raw_hex': payload.hex(),
            'length': len(payload)
        }
        
        # 尝试解析为整数数组
        try:
            int_values = []
            for i in range(0, len(payload), 4):
                if i + 4 <= len(payload):
                    int_values.append(int.from_bytes(payload[i:i+4], 'little'))
            result['as_ints'] = int_values
        except:
            pass
        
        # 尝试解析为小端16位整数（可能包含方块ID）
        try:
            short_values = []
            for i in range(0, len(payload), 2):
                if i + 2 <= len(payload):
                    short_values.append(int.from_bytes(payload[i:i+2], 'little'))
            result['as_shorts'] = short_values
        except:
            pass
        
        # 检查是否包含可能的方块ID（0-500范围内的值）
        potential_block_ids = []
        for i, val in enumerate(result.get('as_shorts', [])):
            if 0 <= val <= 500:
                potential_block_ids.append({'offset': i, 'value': val})
        
        if potential_block_ids:
            result['potential_block_ids'] = potential_block_ids
        
        return result
    
    def find_block_patterns(self, packets: List[Dict]) -> List[Dict]:
        """在数据包中查找方块操作模式"""
        block_events = []
        
        for pkt in packets:
            payload = pkt.get('payload', b'')
            analysis = self.analyze_payload(payload)
            
            if analysis and 'potential_block_ids' in analysis:
                event = {
                    'timestamp': pkt['timestamp'],
                    'src': pkt['src'],
                    'dst': pkt['dst'],
                    'analysis': analysis
                }
                block_events.append(event)
        
        return block_events
    
    def generate_report(self, output_file: str):
        """生成分析报告"""
        report = {
            'total_packets': len(self.packets),
            'block_events_found': len(self.block_events),
            'potential_block_ids': self._extract_unique_block_ids(),
            'events': self.block_events[:100]  # 限制数量
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[+] Report saved to: {output_file}")
    
    def _extract_unique_block_ids(self) -> List[Dict]:
        """提取唯一的方块ID候选"""
        id_counts = {}
        
        for event in self.block_events:
            for block_id in event.get('analysis', {}).get('potential_block_ids', []):
                val = block_id['value']
                if val not in id_counts:
                    id_counts[val] = {'id': val, 'count': 0, 'contexts': []}
                id_counts[val]['count'] += 1
                if len(id_counts[val]['contexts']) < 3:
                    id_counts[val]['contexts'].append(event['timestamp'])
        
        # 按出现频率排序
        sorted_ids = sorted(id_counts.values(), key=lambda x: x['count'], reverse=True)
        return sorted_ids[:50]

def main():
    parser = argparse.ArgumentParser(description='MiniWorld WebSocket Packet Analyzer')
    parser.add_argument('--pcap', required=True, help='Path to pcap/pcapng file')
    parser.add_argument('--output', default='websocket_analysis.json', help='Output JSON file')
    args = parser.parse_args()
    
    print("="*60)
    print("MiniWorld WebSocket Analyzer")
    print("="*60)
    print()
    
    analyzer = WebSocketAnalyzer()
    
    print(f"[*] Parsing pcap file: {args.pcap}")
    packets = analyzer.parse_pcap(args.pcap)
    analyzer.packets = packets
    
    print(f"[+] Found {len(packets)} WebSocket packets")
    
    print("[*] Analyzing for block patterns...")
    block_events = analyzer.find_block_patterns(packets)
    analyzer.block_events = block_events
    
    print(f"[+] Found {len(block_events)} potential block events")
    
    print("[*] Generating report...")
    analyzer.generate_report(args.output)
    
    print()
    print("="*60)
    print("Analysis complete!")
    print("="*60)
    print()
    print("Next steps:")
    print("  1. Review the generated JSON report")
    print("  2. Look for 'potential_block_ids' section")
    print("  3. Correlate IDs with in-game actions")
    print("  4. Update block_mapping_complete.json with verified IDs")

if __name__ == "__main__":
    main()