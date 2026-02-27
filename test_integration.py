#!/usr/bin/env python3
"""
集成测试脚本
测试协议翻译和加密模块
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
from codec.mc_codec import MinecraftCodec
from codec.mnw_codec import MiniWorldCodec
from crypto.aes_crypto import AESCipher, MiniWorldEncryption, hash_password
from core.protocol_translator import ProtocolTranslator, ConnectionState
from utils.logger import setup_logger

logger = setup_logger("IntegrationTest")


def test_crypto():
    """测试加密模块"""
    logger.info("=" * 60)
    logger.info("测试加密模块")
    logger.info("=" * 60)
    
    # 测试AES-128-CBC（国服）
    logger.info("\n测试 AES-128-CBC（国服）...")
    key = b'1234567890123456'  # 16字节密钥
    cipher = AESCipher(key, mode="CBC")
    
    plaintext = b"Hello, MiniWorld CN!"
    encrypted = cipher.encrypt_cbc(plaintext)
    decrypted = cipher.decrypt_cbc(encrypted)
    
    assert decrypted == plaintext, "CBC解密失败"
    logger.info(f"原始数据: {plaintext}")
    logger.info(f"加密后: {encrypted.hex()[:32]}...")
    logger.info(f"解密后: {decrypted}")
    logger.info("✅ AES-128-CBC 测试通过")
    
    # 测试AES-256-GCM（外服）
    logger.info("\n测试 AES-256-GCM（外服）...")
    key = b'12345678901234567890123456789012'  # 32字节密钥
    cipher = AESCipher(key, mode="GCM")
    
    plaintext = b"Hello, MiniWorld Global!"
    ciphertext, tag = cipher.encrypt_gcm(plaintext)
    decrypted = cipher.decrypt_gcm(ciphertext, tag)
    
    assert decrypted == plaintext, "GCM解密失败"
    logger.info(f"原始数据: {plaintext}")
    logger.info(f"加密后: {ciphertext.hex()[:32]}...")
    logger.info(f"Tag: {tag.hex()}")
    logger.info(f"解密后: {decrypted}")
    logger.info("✅ AES-256-GCM 测试通过")
    
    # 测试MiniWorld加密管理器
    logger.info("\n测试 MiniWorldEncryption...")
    mw_crypto = MiniWorldEncryption(region="CN")
    session_key = b'1234567890123456'
    mw_crypto.set_session_key(session_key)
    
    data = b"Test data for MiniWorld"
    encrypted = mw_crypto.encrypt(data)
    decrypted = mw_crypto.decrypt(encrypted)
    
    assert decrypted == data, "MiniWorld加密失败"
    logger.info("✅ MiniWorldEncryption 测试通过")
    
    # 测试密码哈希
    logger.info("\n测试密码哈希...")
    password = "test_password_123"
    hashed = hash_password(password, method="md5_double")
    logger.info(f"密码: {password}")
    logger.info(f"哈希: {hashed}")
    logger.info("✅ 密码哈希测试通过")


def test_protocol_translation():
    """测试协议翻译"""
    logger.info("\n" + "=" * 60)
    logger.info("测试协议翻译")
    logger.info("=" * 60)
    
    translator = ProtocolTranslator(region="CN")
    mc_codec = MinecraftCodec()
    
    # 测试握手包翻译
    logger.info("\n测试握手包翻译...")
    handshake = mc_codec.create_handshake(
        protocol_version=766,
        server_address="localhost",
        server_port=25565,
        next_state=2
    )
    result = translator.mc_to_mnw(handshake)
    logger.info(f"握手包翻译结果: {result}")
    assert result is None, "握手包不应转发"
    assert translator.context.state == ConnectionState.LOGIN
    logger.info("✅ 握手包翻译测试通过")
    
    # 测试登录包翻译
    logger.info("\n测试登录包翻译...")
    login = mc_codec.create_login_start("TestPlayer")
    result = translator.mc_to_mnw(login)
    logger.info(f"登录包翻译结果: {result is not None}")
    assert result is not None, "登录包翻译失败"
    logger.info("✅ 登录包翻译测试通过")
    
    # 测试聊天包翻译
    logger.info("\n测试聊天包翻译...")
    chat = mc_codec.create_chat_message("Hello, MiniWorld!")
    result = translator.mc_to_mnw(chat)
    logger.info(f"聊天包翻译结果: {result is not None}")
    assert result is not None, "聊天包翻译失败"
    logger.info("✅ 聊天包翻译测试通过")
    
    # 测试统计
    stats = translator.get_stats()
    logger.info(f"\n翻译统计: {stats}")
    assert stats["packets_translated"] >= 2
    logger.info("✅ 协议翻译测试全部通过")


def test_block_mapping():
    """测试方块映射"""
    logger.info("\n" + "=" * 60)
    logger.info("测试方块映射")
    logger.info("=" * 60)
    
    from protocol.block_mapper import BlockMapper
    
    mapper = BlockMapper()
    
    # 测试基础映射
    logger.info("\n测试基础方块映射...")
    test_cases = [
        (1, 1),   # 石头
        (2, 2),   # 草方块
        (3, 3),   # 泥土
    ]
    
    for mc_id, expected_mnw_id in test_cases:
        mnw_id, _ = mapper.mc_to_mnw_block(mc_id)
        logger.info(f"MC ID {mc_id} -> MNW ID {mnw_id}")
        assert mnw_id == expected_mnw_id, f"方块映射错误: {mc_id} -> {mnw_id}"
    
    logger.info("✅ 方块映射测试通过")


def test_coordinate_conversion():
    """测试坐标转换"""
    logger.info("\n" + "=" * 60)
    logger.info("测试坐标转换")
    logger.info("=" * 60)
    
    from protocol.coordinate_converter import CoordinateConverter, Vector3
    
    converter = CoordinateConverter()
    
    # 测试坐标转换（X轴取反）
    logger.info("\n测试坐标转换...")
    mc_pos = Vector3(100.0, 64.0, 200.0)
    mnw_pos = converter.mc_to_mnw_position(mc_pos)
    back_to_mc = converter.mnw_to_mc_position(mnw_pos)
    
    logger.info(f"MC位置: ({mc_pos.x}, {mc_pos.y}, {mc_pos.z})")
    logger.info(f"MNW位置: ({mnw_pos.x}, {mnw_pos.y}, {mnw_pos.z})")
    logger.info(f"转回MC: ({back_to_mc.x}, {back_to_mc.y}, {back_to_mc.z})")
    
    # 由于浮点精度，使用近似相等
    assert abs(back_to_mc.x - mc_pos.x) < 0.01
    assert abs(back_to_mc.y - mc_pos.y) < 0.01
    assert abs(back_to_mc.z - mc_pos.z) < 0.01
    
    logger.info("✅ 坐标转换测试通过")


async def test_proxy_server():
    """测试代理服务器"""
    logger.info("\n" + "=" * 60)
    logger.info("测试代理服务器")
    logger.info("=" * 60)
    
    from core.proxy_server import ProxyServer
    from core.session_manager import SessionManager
    
    session_manager = SessionManager()
    server = ProxyServer(
        host="127.0.0.1",
        port=25566,  # 使用非标准端口避免冲突
        session_manager=session_manager
    )
    
    logger.info(f"代理服务器创建成功")
    logger.info(f"统计: {server.get_stats()}")
    
    # 注意：这里不实际启动服务器，只是测试创建
    logger.info("✅ 代理服务器测试通过")


def run_all_tests():
    """运行所有测试"""
    try:
        test_crypto()
        test_protocol_translation()
        test_block_mapping()
        test_coordinate_conversion()
        
        # 异步测试
        asyncio.run(test_proxy_server())
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 所有集成测试通过！")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
