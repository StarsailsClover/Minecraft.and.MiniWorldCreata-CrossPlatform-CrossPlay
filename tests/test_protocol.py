#!/usr/bin/env python3
"""
协议翻译器真实测试 - Phase 4
测试MNW和MC协议之间的翻译
"""

import sys
import struct
from pathlib import Path
from io import BytesIO

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol.packet_translator import PacketTranslator, Packet, PacketType
from protocol.block_mapper import BlockMapper
from protocol.mc_protocol import VarInt, MCDataTypes, TextPacket, MovePlayerPacket


class TestProtocol:
    """协议翻译器测试"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        self.translator = None
    
    def test(self, name: str, condition: bool, details: str = ""):
        """记录测试结果"""
        if condition:
            self.passed += 1
            status = "✓"
        else:
            self.failed += 1
            status = "✗"
        
        self.tests.append((name, status, details))
        return condition
    
    def run_all(self):
        """运行所有测试"""
        print("=" * 70)
        print(" 协议翻译器真实测试")
        print("=" * 70)
        
        # 初始化翻译器
        print("\n[初始化] 加载协议翻译器...")
        try:
            self.translator = PacketTranslator()
            self.test("翻译器初始化", True, "成功")
        except Exception as e:
            self.test("翻译器初始化", False, f"异常: {e}")
            self._print_results()
            return
        
        # 测试VarInt编码
        self._test_varint()
        
        # 测试数据包创建
        self._test_packet_creation()
        
        # 测试协议翻译
        self._test_translation()
        
        # 测试MC数据包
        self._test_mc_packets()
        
        # 打印结果
        self._print_results()
    
    def _test_varint(self):
        """测试VarInt编码"""
        print("\n[测试] VarInt编码...")
        
        test_cases = [
            (0, b'\x00'),
            (1, b'\x01'),
            (127, b'\x7f'),
            (128, b'\x80\x01'),
            (255, b'\xff\x01'),
            (300, b'\xac\x02'),
            (16383, b'\xff\x7f'),
            (16384, b'\x80\x80\x01'),
        ]
        
        for value, expected in test_cases:
            encoded = VarInt.encode(value)
            success = encoded == expected
            
            decoded, _ = VarInt.decode(encoded)
            success = success and decoded == value
            
            self.test(
                f"VarInt {value}",
                success,
                f"编码: {encoded.hex()} == {expected.hex()}"
            )
    
    def _test_packet_creation(self):
        """测试数据包创建"""
        print("\n[测试] 数据包创建...")
        
        # 创建MNW数据包
        try:
            packet = Packet(
                packet_type=PacketType.MNW_BLOCK,
                sub_type=0x01,
                seq_id=1,
                data=b'{"x":10,"y":20,"z":30,"id":1}'
            )
            
            # 转换为字节
            packet_bytes = packet.to_bytes()
            
            # 解析
            parsed = Packet.from_bytes(packet_bytes)
            
            success = (
                parsed is not None and
                parsed.packet_type == packet.packet_type and
                parsed.seq_id == packet.seq_id
            )
            
            self.test(
                "MNW数据包创建/解析",
                success,
                f"类型: {parsed.packet_type}, 序列: {parsed.seq_id}"
            )
            
        except Exception as e:
            self.test("MNW数据包创建", False, f"异常: {e}")
    
    def _test_translation(self):
        """测试协议翻译"""
        print("\n[测试] 协议翻译...")
        
        # 创建MNW数据包
        mnw_packet = Packet(
            packet_type=PacketType.MNW_PLAYER,
            sub_type=0x01,
            seq_id=1,
            data=b'{"x":10000,"y":6400,"z":-5000}'
        )
        
        try:
            # 翻译为MC
            mc_packet = self.translator.translate_mnw_to_mc(mnw_packet)
            
            success = mc_packet is not None
            self.test(
                "MNW->MC 翻译",
                success,
                f"MNW({mnw_packet.packet_type}) -> MC({mc_packet.packet_type if mc_packet else 'None'})"
            )
            
            if mc_packet:
                # 翻译回MNW
                mnw_packet2 = self.translator.translate_mc_to_mnw(mc_packet)
                
                success = mnw_packet2 is not None
                self.test(
                    "MC->MNW 翻译",
                    success,
                    "双向翻译成功"
                )
            
        except Exception as e:
            self.test("协议翻译", False, f"异常: {e}")
    
    def _test_mc_packets(self):
        """测试MC数据包"""
        print("\n[测试] MC数据包...")
        
        # 测试TextPacket
        try:
            text_packet = TextPacket(
                packet_id=0x09,  # TEXT packet ID
                type=1,  # chat
                source_name="TestPlayer",
                message="Hello World!",
            )
            
            # 验证数据包创建成功
            self.test(
                "MC TextPacket 创建",
                text_packet.packet_id == 0x09,
                f"Packet ID: {text_packet.packet_id}, 类型: {text_packet.type}"
            )
            
        except Exception as e:
            self.test("MC TextPacket", False, f"异常: {e}")
        
        # 测试MovePlayerPacket
        try:
            move_packet = MovePlayerPacket(
                packet_id=0x13,  # MOVE_PLAYER packet ID
                entity_id=1,
                x=100.5,
                y=64.0,
                z=-50.25,
                pitch=45.0,
                yaw=90.0,
            )
            
            self.test(
                "MC MovePlayerPacket 创建",
                move_packet.packet_id == 0x13,
                f"位置: ({move_packet.x}, {move_packet.y}, {move_packet.z})"
            )
            
        except Exception as e:
            self.test("MC MovePlayerPacket", False, f"异常: {e}")
    
    def _print_results(self):
        """打印测试结果"""
        print("\n" + "=" * 70)
        print(" 测试结果")
        print("=" * 70)
        
        for name, status, details in self.tests:
            print(f"  [{status}] {name}")
            if details:
                print(f"       {details}")
        
        print("\n" + "=" * 70)
        print(f" 通过: {self.passed}")
        print(f" 失败: {self.failed}")
        print(f" 总计: {self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n ✓ 所有测试通过!")
        else:
            print(f"\n ✗ {self.failed}个测试失败")
        
        print("=" * 70)


if __name__ == "__main__":
    tester = TestProtocol()
    tester.run_all()
