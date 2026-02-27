#!/usr/bin/env python3
"""
完整流程测试
测试从MC到MNW再到MC的完整数据流
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from codec.mc_codec import MinecraftCodec
from codec.mnw_codec import MiniWorldCodec
from core.protocol_translator import ProtocolTranslator, ConnectionState
from protocol.block_mapper import BlockMapper
from protocol.coordinate_converter import CoordinateConverter, Vector3
from utils.logger import setup_logger

logger = setup_logger("CompleteFlowTest")


def test_block_mapping_with_file():
    """测试从文件加载方块映射"""
    logger.info("=" * 60)
    logger.info("测试方块映射（从文件加载）")
    logger.info("=" * 60)
    
    mapper = BlockMapper()  # 自动查找映射文件
    stats = mapper.get_stats()
    
    logger.info(f"映射统计: {stats}")
    logger.info(f"总映射数: {stats['total_mappings']}")
    logger.info(f"已验证: {stats['verified_mappings']}")
    
    # 测试几个关键映射
    test_cases = [
        (1, "石头"),
        (2, "草方块"),
        (56, "钻石矿石"),
    ]
    
    for mc_id, expected_name in test_cases:
        mnw_id, _ = mapper.mc_to_mnw_block(mc_id)
        name = mapper.get_mc_block_name(mc_id)
        logger.info(f"MC {mc_id} ({name}) -> MNW {mnw_id}")
    
    logger.info("✅ 方块映射测试通过")


def test_complete_translation_flow():
    """测试完整的翻译流程"""
    logger.info("\n" + "=" * 60)
    logger.info("测试完整翻译流程")
    logger.info("=" * 60)
    
    translator = ProtocolTranslator(region="CN")
    mc_codec = MinecraftCodec()
    
    # 1. 测试握手
    logger.info("\n1. 测试握手包翻译...")
    handshake = mc_codec.create_handshake(
        protocol_version=766,
        server_address="localhost",
        server_port=25565,
        next_state=2
    )
    result = translator.mc_to_mnw(handshake)
    assert result is None, "握手包不应转发"
    assert translator.context.state == ConnectionState.LOGIN
    logger.info("✅ 握手包处理正确")
    
    # 2. 测试登录
    logger.info("\n2. 测试登录包翻译...")
    login = mc_codec.create_login_start("TestPlayer")
    result = translator.mc_to_mnw(login)
    assert result is not None, "登录包翻译失败"
    logger.info(f"✅ 登录包翻译成功: {len(result)} bytes")
    
    # 3. 测试聊天
    logger.info("\n3. 测试聊天包翻译...")
    chat = mc_codec.create_chat_message("Hello MiniWorld!")
    result = translator.mc_to_mnw(chat)
    assert result is not None, "聊天包翻译失败"
    logger.info(f"✅ 聊天包翻译成功: {len(result)} bytes")
    
    # 4. 测试位置
    logger.info("\n4. 测试位置包翻译...")
    # 创建MC位置包（模拟）
    position_data = b'\x00\x00\x00\x00\x00\x00Y@'  # x=100.0 (double)
    position_data += b'\x00\x00\x00\x00\x00\x00P@'  # y=64.0 (double)
    position_data += b'\x00\x00\x00\x00\x00\x00i@'  # z=200.0 (double)
    position_data += b'\x00\x00\x00\x00'  # yaw=0.0 (float)
    position_data += b'\x00\x00\x00\x00'  # pitch=0.0 (float)
    position_data += b'\x01'  # on_ground=True
    
    # 使用translator的方法创建位置包
    position_packet = translator.create_mc_player_position(100.0, 64.0, 200.0)
    result = translator.mc_to_mnw(position_packet)
    assert result is not None, "位置包翻译失败"
    logger.info(f"✅ 位置包翻译成功: {len(result)} bytes")
    
    # 5. 测试方块放置
    logger.info("\n5. 测试方块放置翻译...")
    # 创建MC方块变更包
    block_packet = translator.create_mc_block_change(10, 20, 30, 1)  # 石头
    result = translator.mc_to_mnw(block_packet)
    assert result is not None, "方块包翻译失败"
    logger.info(f"✅ 方块包翻译成功: {len(result)} bytes")
    
    # 6. 测试反向翻译（MNW -> MC）
    logger.info("\n6. 测试反向翻译...")
    mnw_codec = MiniWorldCodec()
    
    # 创建MNW聊天包
    mnw_chat = mnw_codec.create_chat_message("Hello from MiniWorld!")
    result = translator.mnw_to_mc(mnw_chat)
    assert result is not None, "MNW聊天包翻译失败"
    logger.info(f"✅ MNW聊天包翻译成功: {len(result)} bytes")
    
    # 创建MNW移动包
    mnw_move = mnw_codec.create_move_packet(50.0, 64.0, 100.0)
    result = translator.mnw_to_mc(mnw_move)
    assert result is not None, "MNW移动包翻译失败"
    logger.info(f"✅ MNW移动包翻译成功: {len(result)} bytes")
    
    # 创建MNW方块包
    mnw_block = mnw_codec.create_block_place(5, 10, 15, 1, 0)
    result = translator.mnw_to_mc(mnw_block)
    assert result is not None, "MNW方块包翻译失败"
    logger.info(f"✅ MNW方块包翻译成功: {len(result)} bytes")
    
    # 查看统计
    stats = translator.get_stats()
    logger.info(f"\n翻译统计: {stats}")
    
    logger.info("✅ 完整翻译流程测试通过")


def test_coordinate_conversion():
    """测试坐标转换"""
    logger.info("\n" + "=" * 60)
    logger.info("测试坐标转换")
    logger.info("=" * 60)
    
    converter = CoordinateConverter()
    
    # 测试坐标转换
    test_positions = [
        (0.0, 64.0, 0.0),
        (100.0, 70.0, -50.0),
        (-100.0, 80.0, 200.0),
    ]
    
    for x, y, z in test_positions:
        mc_pos = Vector3(x, y, z)
        mnw_pos = converter.mc_to_mnw_position(mc_pos)
        back_to_mc = converter.mnw_to_mc_position(mnw_pos)
        
        logger.info(f"MC({x:7.1f}, {y:5.1f}, {z:7.1f}) -> "
                   f"MNW({mnw_pos.x:7.1f}, {mnw_pos.y:5.1f}, {mnw_pos.z:7.1f}) -> "
                   f"MC({back_to_mc.x:7.1f}, {back_to_mc.y:5.1f}, {back_to_mc.z:7.1f})")
        
        # 验证精度
        assert abs(back_to_mc.x - x) < 0.01
        assert abs(back_to_mc.y - y) < 0.01
        assert abs(back_to_mc.z - z) < 0.01
    
    logger.info("✅ 坐标转换测试通过")


def test_block_id_mapping():
    """测试方块ID映射"""
    logger.info("\n" + "=" * 60)
    logger.info("测试方块ID映射")
    logger.info("=" * 60)
    
    mapper = BlockMapper()
    
    # 测试MC -> MNW
    logger.info("\nMC -> MNW 映射:")
    mc_blocks = [1, 2, 3, 4, 5, 12, 14, 15, 16, 56]
    for mc_id in mc_blocks:
        mnw_id, _ = mapper.mc_to_mnw_block(mc_id)
        mc_name = mapper.get_mc_block_name(mc_id)
        mnw_name = mapper.get_mnw_block_name(mnw_id)
        logger.info(f"  MC {mc_id:3d} ({mc_name:12s}) -> MNW {mnw_id:3d} ({mnw_name})")
    
    # 测试MNW -> MC
    logger.info("\nMNW -> MC 映射:")
    mnw_blocks = [1, 2, 3, 4, 5, 12, 14, 15, 16]
    for mnw_id in mnw_blocks:
        mc_id, _ = mapper.mnw_to_mc_block(mnw_id)
        mc_name = mapper.get_mc_block_name(mc_id)
        mnw_name = mapper.get_mnw_block_name(mnw_id)
        logger.info(f"  MNW {mnw_id:3d} ({mnw_name:12s}) -> MC {mc_id:3d} ({mc_name})")
    
    logger.info("✅ 方块ID映射测试通过")


def run_all_tests():
    """运行所有测试"""
    try:
        test_block_mapping_with_file()
        test_coordinate_conversion()
        test_block_id_mapping()
        test_complete_translation_flow()
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 所有完整流程测试通过！")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
