#!/usr/bin/env python3
"""
数据包检查器
用于调试和分析数据包
"""

import struct
import binascii
from typing import Dict, Optional

class PacketInspector:
    """数据包检查器"""
    
    @staticmethod
    def inspect_minecraft_packet(data: bytes) -> Dict:
        """检查Minecraft数据包"""
        if len(data) < 2:
            return {"error": "数据太短"}
        
        result = {
            "raw": binascii.hexlify(data[:32]).decode(),
            "length": data[0] if len(data) > 0 else 0,
            "packet_id": data[1] if len(data) > 1 else 0,
            "data_preview": binascii.hexlify(data[2:min(20, len(data))]).decode() if len(data) > 2 else ""
        }
        
        # 解析包ID含义
        packet_names = {
            0x00: "Handshake",
            0x01: "Status",
            0x02: "Login",
            0x03: "Play",
            0x04: "Player Move",
            0x05: "Block Change",
        }
        
        result["packet_name"] = packet_names.get(result["packet_id"], "Unknown")
        
        return result
    
    @staticmethod
    def inspect_miniworld_packet(data: bytes) -> Dict:
        """检查迷你世界数据包"""
        if len(data) < 4:
            return {"error": "数据太短"}
        
        result = {
            "raw": binascii.hexlify(data[:32]).decode(),
            "header": binascii.hexlify(data[:2]).decode() if len(data) >= 2 else "",
            "command": data[2] if len(data) > 2 else 0,
            "length": data[3] if len(data) > 3 else 0,
        }
        
        # 解析命令含义
        command_names = {
            0x01: "Login",
            0x02: "Game",
            0x03: "Chat",
            0x04: "Move",
            0x05: "Block",
            0x10: "Room",
            0xFF: "Heartbeat",
        }
        
        result["command_name"] = command_names.get(result["command"], "Unknown")
        
        return result
    
    @staticmethod
    def compare_packets(mc_data: bytes, mnw_data: bytes):
        """对比两个数据包"""
        print("\n[*] 数据包对比:")
        print("-" * 60)
        
        mc_info = PacketInspector.inspect_minecraft_packet(mc_data)
        mnw_info = PacketInspector.inspect_miniworld_packet(mnw_data)
        
        print(f"Minecraft:")
        print(f"  原始数据: {mc_info.get('raw', 'N/A')}")
        print(f"  包ID: 0x{mc_info.get('packet_id', 0):02X} ({mc_info.get('packet_name', 'Unknown')})")
        print(f"  长度: {mc_info.get('length', 0)}")
        print(f"  数据预览: {mc_info.get('data_preview', 'N/A')}")
        
        print(f"\n迷你世界:")
        print(f"  原始数据: {mnw_info.get('raw', 'N/A')}")
        print(f"  命令: 0x{mnw_info.get('command', 0):02X} ({mnw_info.get('command_name', 'Unknown')})")
        print(f"  长度: {mnw_info.get('length', 0)}")
        print(f"  包头: {mnw_info.get('header', 'N/A')}")
        
        print("-" * 60)

def main():
    """主函数"""
    print("=" * 60)
    print("数据包检查器")
    print("=" * 60)
    
    # 测试数据
    mc_test = b'\x0e\x02\x00\x0bTestPlayer'  # Minecraft登录包
    mnw_test = b'\xaa\xbb\x02\x10' + b'\x00' * 16  # 模拟迷你世界包
    
    inspector = PacketInspector()
    inspector.compare_packets(mc_test, mnw_test)
    
    print("\n[*] 检查器准备就绪")
    print("[*] 可用于调试实际数据包")

if __name__ == "__main__":
    main()
