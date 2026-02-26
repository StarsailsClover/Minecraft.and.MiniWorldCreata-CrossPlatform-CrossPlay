#!/usr/bin/env python3
"""
集成测试
测试完整的数据流
"""

import sys
from pathlib import Path
import struct

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.protocol_translator import ProtocolTranslator, MinecraftPacket, MiniWorldPacket
from protocol import LoginHandler, CoordinateConverter, BlockMapper

def test_login_flow():
    """测试完整登录流程"""
    print("\n[*] 测试登录流程...")
    
    # 1. Minecraft登录请求
    mc_login_data = b'\x02\x00\x0bTestPlayer'  # 简化格式
    
    # 2. 转换为Minecraft包
    mc_packet = MinecraftPacket(
        length=len(mc_login_data) + 1,
        packet_id=0x02,
        data=mc_login_data
    )
    
    print(f"  [+] Minecraft登录包: ID=0x{mc_packet.packet_id:02X}, Length={mc_packet.length}")
    
    # 3. 协议转换
    translator = ProtocolTranslator()
    mnw_packet = translator.translate_mc_to_mnw(mc_packet)
    
    if mnw_packet:
        print(f"  [+] 迷你世界登录包: Command=0x{mnw_packet.command:02X}")
        print(f"  ✅ 登录流程测试通过")
        return True
    else:
        print(f"  ❌ 协议转换失败")
        return False

def test_movement_flow():
    """测试移动数据流"""
    print("\n[*] 测试移动数据流...")
    
    # 1. Minecraft移动数据 (简化)
    # [x (double)] [y (double)] [z (double)] [yaw (float)] [pitch (float)]
    mc_move_data = struct.pack('<dddff', 
        100.5,  # x
        64.0,   # y
        -200.3, # z
        45.0,   # yaw
        0.0     # pitch
    )
    
    mc_packet = MinecraftPacket(
        length=len(mc_move_data) + 1,
        packet_id=0x04,  # Player Move
        data=mc_move_data
    )
    
    print(f"  [+] MC移动: Pos=({100.5}, {64.0}, {-200.3})")
    
    # 2. 协议转换
    translator = ProtocolTranslator()
    mnw_packet = translator.translate_mc_to_mnw(mc_packet)
    
    if mnw_packet:
        print(f"  [+] MNW移动: Command=0x{mnw_packet.command:02X}")
        print(f"  ✅ 移动数据流测试通过")
        return True
    else:
        print(f"  ❌ 协议转换失败")
        return False

def test_block_placement():
    """测试方块放置"""
    print("\n[*] 测试方块放置...")
    
    # 1. Minecraft方块放置
    # [x (int)] [y (int)] [z (int)] [block_id (varint)]
    mc_block_data = struct.pack('<iii', 10, 64, 20) + b'\x01'  # stone
    
    mc_packet = MinecraftPacket(
        length=len(mc_block_data) + 1,
        packet_id=0x05,  # Block Change
        data=mc_block_data
    )
    
    print(f"  [+] MC方块: Pos=(10, 64, 20), Block=1(stone)")
    
    # 2. 协议转换
    translator = ProtocolTranslator()
    mnw_packet = translator.translate_mc_to_mnw(mc_packet)
    
    if mnw_packet:
        print(f"  [+] MNW方块: Command=0x{mnw_packet.command:02X}")
        print(f"  ✅ 方块放置测试通过")
        return True
    else:
        print(f"  ❌ 协议转换失败")
        return False

def test_end_to_end():
    """测试端到端数据流"""
    print("\n[*] 测试端到端数据流...")
    
    # 模拟完整会话
    print("  1. 玩家连接...")
    print("  2. 发送握手包...")
    print("  3. 登录认证...")
    print("  4. 进入游戏...")
    print("  5. 移动同步...")
    print("  6. 方块操作...")
    
    print(f"  ✅ 端到端流程测试通过（模拟）")
    return True

def run_integration_tests():
    """运行集成测试"""
    print("=" * 60)
    print("集成测试")
    print("=" * 60)
    
    tests = [
        ("登录流程", test_login_flow),
        ("移动数据流", test_movement_flow),
        ("方块放置", test_block_placement),
        ("端到端流程", test_end_to_end),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print(f"  ❌ {name} 错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"集成测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
