#!/usr/bin/env python3
"""
MnMCP 桥接器测试
"""

import sys
import time
sys.path.insert(0, '.')

from src.bridge import MnMCPBridge, BridgeConfig
from src.mapping import CoordinateConverter, Vec3, BlockMapper, EntityMapper


def test_coordinate_conversion():
    """测试坐标转换"""
    print("\n=== Testing Coordinate Conversion ===")
    
    converter = CoordinateConverter()
    
    # MC -> MNW
    mc_pos = Vec3(100.5, 64.0, -200.3)
    mnw_pos = converter.mc_to_mnw(mc_pos)
    print(f"MC -> MNW: ({mc_pos.x}, {mc_pos.y}, {mc_pos.z}) -> ({mnw_pos.x}, {mnw_pos.y}, {mnw_pos.z})")
    
    # MNW -> MC
    back_to_mc = converter.mnw_to_mc(mnw_pos)
    print(f"MNW -> MC: ({mnw_pos.x}, {mnw_pos.y}, {mnw_pos.z}) -> ({back_to_mc.x}, {back_to_mc.y}, {back_to_mc.z})")
    
    # 验证
    assert abs(back_to_mc.x - mc_pos.x) < 0.01
    assert abs(back_to_mc.y - mc_pos.y) < 0.01
    assert abs(back_to_mc.z - mc_pos.z) < 0.01
    print("✓ Coordinate conversion test passed")


def test_block_mapping():
    """测试方块映射"""
    print("\n=== Testing Block Mapping ===")
    
    mapper = BlockMapper()
    print(f"Loaded {mapper.count} block mappings")
    
    # MC -> MNW
    mc_id = 1  # stone
    mnw_id, meta = mapper.get_mnw_block(mc_id)
    print(f"MC block {mc_id} -> MNW block {mnw_id}, meta {meta}")
    
    # MNW -> MC
    back_to_mc, _ = mapper.get_mc_block(mnw_id)
    print(f"MNW block {mnw_id} -> MC block {back_to_mc}")
    
    assert back_to_mc == mc_id
    print("✓ Block mapping test passed")


def test_entity_mapping():
    """测试实体映射"""
    print("\n=== Testing Entity Mapping ===")
    
    mapper = EntityMapper()
    print(f"Loaded {mapper.count} entity mappings")
    
    # MC -> MNW
    mc_entity = "minecraft:zombie"
    mnw_id, mnw_name = mapper.get_mnw_entity(mc_entity)
    print(f"MC entity {mc_entity} -> MNW entity {mnw_id} ({mnw_name})")
    
    # MNW -> MC
    back_to_mc, _ = mapper.get_mc_entity(mnw_id)
    print(f"MNW entity {mnw_id} -> MC entity {back_to_mc}")
    
    assert back_to_mc == mc_entity
    print("✓ Entity mapping test passed")


def test_bridge_basic():
    """测试桥接器基本功能"""
    print("\n=== Testing Bridge Basic Functions ===")
    
    config = BridgeConfig(
        bridge_host="127.0.0.1",
        bridge_port=0,  # 自动分配
        mnw_host="127.0.0.1",
        mnw_port=8080,
        player_name="TestPlayer"
    )
    
    bridge = MnMCPBridge(config)
    
    # 启动桥接器
    assert bridge.start(), "Failed to start bridge"
    actual_port = bridge.udp.socket.getsockname()[1]
    print(f"✓ Bridge started on port {actual_port}")
    
    # 测试坐标转换
    bridge.send_player_move(100.0, 64.0, 200.0)
    print("✓ Player move sent")
    
    # 停止桥接器
    bridge.stop()
    print("✓ Bridge stopped")
    
    print("✓ Bridge basic test passed")


def main():
    """主函数"""
    print("=" * 50)
    print("MnMCP Bridge Test")
    print("=" * 50)
    
    try:
        test_coordinate_conversion()
        test_block_mapping()
        test_entity_mapping()
        test_bridge_basic()
        
        print("\n" + "=" * 50)
        print("All bridge tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
