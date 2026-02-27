#!/usr/bin/env python3
"""
最终测试 - 验证所有组件工作正常
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from codec.mc_codec import MinecraftCodec
from codec.mnw_codec import MiniWorldCodec
from core.protocol_translator import ProtocolTranslator
from protocol.block_mapper import BlockMapper
from protocol.coordinate_converter import CoordinateConverter
from utils.logger import setup_logger

logger = setup_logger("FinalTest")


def test_all_components():
    """测试所有组件"""
    logger.info("=" * 70)
    logger.info(" MnMCP 最终组件测试")
    logger.info("=" * 70)
    
    all_passed = True
    
    # 1. 测试Minecraft编解码器
    logger.info("\n[1/8] 测试 Minecraft 编解码器...")
    try:
        mc_codec = MinecraftCodec()
        handshake = mc_codec.create_handshake(766, "localhost", 25565, 2)
        assert len(handshake) > 0
        logger.info("✅ Minecraft编解码器测试通过")
    except Exception as e:
        logger.error(f"❌ Minecraft编解码器测试失败: {e}")
        all_passed = False
    
    # 2. 测试迷你世界编解码器
    logger.info("\n[2/8] 测试 迷你世界 编解码器...")
    try:
        mnw_codec = MiniWorldCodec()
        login = mnw_codec.create_login_request("123456", "test_token")
        assert len(login) > 0
        logger.info("✅ 迷你世界编解码器测试通过")
    except Exception as e:
        logger.error(f"❌ 迷你世界编解码器测试失败: {e}")
        all_passed = False
    
    # 3. 测试方块映射器
    logger.info("\n[3/8] 测试 方块映射器...")
    try:
        mapper = BlockMapper()
        mnw_id, _ = mapper.mc_to_mnw_block(1)  # 石头
        assert mnw_id == 1
        stats = mapper.get_stats()
        assert stats["total_mappings"] > 0
        logger.info(f"✅ 方块映射器测试通过 (映射数: {stats['total_mappings']})")
    except Exception as e:
        logger.error(f"❌ 方块映射器测试失败: {e}")
        all_passed = False
    
    # 4. 测试坐标转换器
    logger.info("\n[4/8] 测试 坐标转换器...")
    try:
        from protocol.coordinate_converter import Vector3
        converter = CoordinateConverter()
        mc_pos = Vector3(100.0, 64.0, 200.0)
        mnw_pos = converter.mc_to_mnw_position(mc_pos)
        back_to_mc = converter.mnw_to_mc_position(mnw_pos)
        assert abs(back_to_mc.x - mc_pos.x) < 0.01
        assert abs(back_to_mc.y - mc_pos.y) < 0.01
        assert abs(back_to_mc.z - mc_pos.z) < 0.01
        logger.info("✅ 坐标转换器测试通过")
    except Exception as e:
        logger.error(f"❌ 坐标转换器测试失败: {e}")
        all_passed = False
    
    # 5. 测试协议翻译器
    logger.info("\n[5/8] 测试 协议翻译器...")
    try:
        translator = ProtocolTranslator(region="CN")
        
        # 测试MC→MNW翻译
        import struct
        from io import BytesIO
        from codec.mc_codec import encode_varint, encode_string
        
        # 创建握手包数据
        data = BytesIO()
        data.write(encode_varint(766))  # protocol version
        data.write(encode_string("localhost"))
        data.write(struct.pack('>H', 25565))  # port
        data.write(encode_varint(2))  # next state (login)
        handshake_data = data.getvalue()
        
        # 翻译
        result = translator._translate_handshake(handshake_data)
        # 握手包应该返回None（不转发到MNW）
        assert result is None
        assert translator.context.state.value == "login"
        
        logger.info("✅ 协议翻译器测试通过")
    except Exception as e:
        logger.error(f"❌ 协议翻译器测试失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # 6. 测试加密模块
    logger.info("\n[6/8] 测试 加密模块...")
    try:
        from crypto.aes_crypto import AESCipher, MiniWorldEncryption
        
        # 测试AES-128-CBC
        key = b'1234567890123456'
        cipher = AESCipher(key, mode="CBC")
        plaintext = b"Hello, MiniWorld!"
        encrypted = cipher.encrypt_cbc(plaintext)
        decrypted = cipher.decrypt_cbc(encrypted)
        assert decrypted == plaintext
        
        # 测试MiniWorld加密管理器
        mw_crypto = MiniWorldEncryption(region="CN")
        mw_crypto.set_session_key(key)
        data = b"Test data"
        enc = mw_crypto.encrypt(data)
        dec = mw_crypto.decrypt(enc)
        assert dec == data
        
        logger.info("✅ 加密模块测试通过")
    except Exception as e:
        logger.error(f"❌ 加密模块测试失败: {e}")
        all_passed = False
    
    # 7. 测试配置管理器
    logger.info("\n[7/8] 测试 配置管理器...")
    try:
        from utils.config_manager import ConfigManager
        config = ConfigManager("test_config.json")
        config.set("test.key", "test_value")
        value = config.get("test.key")
        assert value == "test_value"
        config.save()
        
        # 清理
        import os
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        
        logger.info("✅ 配置管理器测试通过")
    except Exception as e:
        logger.error(f"❌ 配置管理器测试失败: {e}")
        all_passed = False
    
    # 8. 测试日志系统
    logger.info("\n[8/8] 测试 日志系统...")
    try:
        from utils.logger import setup_logger
        test_logger = setup_logger("TestLogger")
        test_logger.info("Test message")
        test_logger.debug("Debug message")
        test_logger.warning("Warning message")
        test_logger.error("Error message")
        logger.info("✅ 日志系统测试通过")
    except Exception as e:
        logger.error(f"❌ 日志系统测试失败: {e}")
        all_passed = False
    
    # 总结
    logger.info("\n" + "=" * 70)
    if all_passed:
        logger.info("🎉 所有组件测试通过！")
    else:
        logger.info("⚠️ 部分组件测试失败")
    logger.info("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    try:
        success = test_all_components()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
