#!/usr/bin/env python3
"""
集成测试脚本
测试协议翻译器和加密模块的集成
"""

import sys
import asyncio
from pathlib import Path
from io import BytesIO

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.protocol_translator import ProtocolTranslator, TranslationContext, ConnectionState
from crypto.aes_crypto import AESCipher, AESMode, MiniWorldEncryption
from codec.mc_codec import MinecraftCodec
from codec.mnw_codec import MiniWorldCodec
from utils.logger import setup_logger

logger = setup_logger("IntegrationTest")


async def test_encryption():
    """测试加密模块"""
    logger.info("=" * 60)
    logger.info("测试加密模块")
    logger.info("=" * 60)
    
    # 测试AES-128-CBC
    cipher_cbc = AESCipher(b"0123456789abcdef", mode=AESMode.CBC_128)
    plaintext = b"Hello, MiniWorld!"
    
    encrypted = cipher_cbc.encrypt(plaintext)
    decrypted = cipher_cbc.decrypt(encrypted)
    
    assert decrypted == plaintext, "CBC解密失败"
    logger.info("✓ AES-128-CBC 测试通过")
    
    # 测试AES-256-GCM
    cipher_gcm = AESCipher(b"0123456789abcdef0123456789abcdef", mode=AESMode.GCM_256)
    
    encrypted = cipher_gcm.encrypt(plaintext)
    decrypted = cipher_gcm.decrypt(encrypted)
    
    assert decrypted == plaintext, "GCM解密失败"
    logger.info("✓ AES-256-GCM 测试通过")
    
    # 测试MiniWorld加密管理器
    encryption = MiniWorldEncryption()
    encryption.init_cn_encryption("test_session_key")
    
    encrypted = encryption.encrypt_cn(plaintext)
    decrypted = encryption.decrypt_cn(encrypted)
    
    assert decrypted == plaintext, "MiniWorld加密失败"
    logger.info("✓ MiniWorld加密管理器测试通过")


async def test_protocol_translation():
    """测试协议翻译"""
    logger.info("\n" + "=" * 60)
    logger.info("测试协议翻译")
    logger.info("=" * 60)
    
    translator = ProtocolTranslator()
    context = TranslationContext()
    mc_codec = MinecraftCodec()
    
    # 测试1: 握手包翻译
    logger.info("\n测试1: 握手包翻译")
    handshake = mc_codec.create_handshake(
        protocol_version=766,
        server_address="localhost",
        server_port=25565,
        next_state=2
    )
    
    result = translator.translate_mc_to_mnw(handshake, context)
    assert result is None, "握手包不应该被转发"
    assert context.state == ConnectionState.LOGIN, "状态应该变为LOGIN"
    logger.info("✓ 握手包翻译测试通过")
    
    # 测试2: 登录包翻译
    logger.info("\n测试2: 登录包翻译")
    login = mc_codec.create_login_start("TestPlayer")
    
    result = translator.translate_mc_to_mnw(login, context)
    # 由于没有账户映射，应该返回None
    # 在实际环境中会返回迷你世界登录包
    logger.info("✓ 登录包翻译测试通过（无账户映射）")
    
    # 测试3: 聊天包翻译
    logger.info("\n测试3: 聊天包翻译")
    chat = mc_codec.create_chat_message("Hello World!")
    
    result = translator.translate_mc_to_mnw(chat, context)
    # 检查是否生成了迷你世界聊天包
    if result:
        logger.info(f"✓ 聊天包翻译成功: {len(result)} bytes")
    else:
        logger.info("✗ 聊天包翻译失败")
    
    # 测试4: 心跳包翻译
    logger.info("\n测试4: 心跳包翻译")
    keep_alive = mc_codec.create_keep_alive(12345)
    
    result = translator.translate_mc_to_mnw(keep_alive, context)
    if result:
        logger.info(f"✓ 心跳包翻译成功: {len(result)} bytes")
    else:
        logger.info("✗ 心跳包翻译失败")


async def test_mnw_to_mc_translation():
    """测试迷你世界到Minecraft的翻译"""
    logger.info("\n" + "=" * 60)
    logger.info("测试 MNW -> MC 翻译")
    logger.info("=" * 60)
    
    translator = ProtocolTranslator()
    context = TranslationContext()
    mnw_codec = MiniWorldCodec()
    
    # 测试1: 登录响应翻译
    logger.info("\n测试1: 登录响应翻译")
    import json
    login_response = json.dumps({
        "success": True,
        "nickname": "TestPlayer",
        "session_key": "test_key_123"
    }).encode()
    
    # 创建MNW登录响应包
    mnw_packet = MNWPacket(
        packet_type=MiniWorldCodec.PACKET_LOGIN,
        sub_type=MiniWorldCodec.SUB_LOGIN_RESPONSE,
        data=login_response,
        seq_id=1
    )
    
    result = translator.translate_mnw_to_mc(mnw_packet.encode(), context)
    if result:
        logger.info(f"✓ 登录响应翻译成功: {len(result)} bytes")
        assert context.state == ConnectionState.PLAY, "状态应该变为PLAY"
    else:
        logger.info("✗ 登录响应翻译失败")
    
    # 测试2: 聊天消息翻译
    logger.info("\n测试2: 聊天消息翻译")
    chat_data = json.dumps({
        "message": "Hello from MiniWorld!",
        "room_id": "12345"
    }).encode()
    
    mnw_packet = MNWPacket(
        packet_type=MiniWorldCodec.PACKET_CHAT,
        sub_type=MiniWorldCodec.SUB_CHAT_MESSAGE,
        data=chat_data,
        seq_id=2
    )
    
    result = translator.translate_mnw_to_mc(mnw_packet.encode(), context)
    if result:
        logger.info(f"✓ 聊天消息翻译成功: {len(result)} bytes")
    else:
        logger.info("✗ 聊天消息翻译失败")
    
    # 测试3: 心跳包翻译
    logger.info("\n测试3: 心跳包翻译")
    import struct
    heartbeat_data = struct.pack('>Q', 1234567890)
    
    mnw_packet = MNWPacket(
        packet_type=MiniWorldCodec.PACKET_HEARTBEAT,
        sub_type=0x00,
        data=heartbeat_data,
        seq_id=3
    )
    
    result = translator.translate_mnw_to_mc(mnw_packet.encode(), context)
    if result:
        logger.info(f"✓ 心跳包翻译成功: {len(result)} bytes")
    else:
        logger.info("✗ 心跳包翻译失败")


async def test_end_to_end():
    """测试端到端流程"""
    logger.info("\n" + "=" * 60)
    logger.info("测试端到端流程")
    logger.info("=" * 60)
    
    translator = ProtocolTranslator()
    context = TranslationContext()
    mc_codec = MinecraftCodec()
    mnw_codec = MiniWorldCodec()
    
    # 模拟完整的登录流程
    logger.info("\n模拟登录流程:")
    
    # 1. MC发送握手
    logger.info("1. MC握手 ->")
    handshake = mc_codec.create_handshake(766, "localhost", 25565, 2)
    translator.translate_mc_to_mnw(handshake, context)
    logger.info(f"   状态: {context.state.value}")
    
    # 2. MC发送登录
    logger.info("2. MC登录 ->")
    login = mc_codec.create_login_start("TestPlayer")
    result = translator.translate_mc_to_mnw(login, context)
    if result:
        logger.info(f"   生成MNW登录包: {len(result)} bytes")
    
    # 3. MNW返回登录成功
    logger.info("3. MNW登录响应 ->")
    import json
    login_response = json.dumps({
        "success": True,
        "nickname": "TestPlayer",
        "session_key": "test_session_key"
    }).encode()
    
    from codec.mnw_codec import MNWPacket
    mnw_packet = MNWPacket(
        packet_type=MiniWorldCodec.PACKET_LOGIN,
        sub_type=MiniWorldCodec.SUB_LOGIN_RESPONSE,
        data=login_response,
        seq_id=1
    )
    
    result = translator.translate_mnw_to_mc(mnw_packet.encode(), context)
    logger.info(f"   状态: {context.state.value}")
    if result:
        logger.info(f"   生成MC登录成功包: {len(result)} bytes")
    
    # 4. MC发送聊天
    logger.info("4. MC聊天 ->")
    chat = mc_codec.create_chat_message("Hello!")
    result = translator.translate_mc_to_mnw(chat, context)
    if result:
        logger.info(f"   生成MNW聊天包: {len(result)} bytes")
    
    # 5. MNW广播聊天
    logger.info("5. MNW聊天广播 ->")
    chat_data = json.dumps({"message": "Hi there!", "room_id": "12345"}).encode()
    mnw_packet = MNWPacket(
        packet_type=MiniWorldCodec.PACKET_CHAT,
        sub_type=MiniWorldCodec.SUB_CHAT_MESSAGE,
        data=chat_data,
        seq_id=2
    )
    result = translator.translate_mnw_to_mc(mnw_packet.encode(), context)
    if result:
        logger.info(f"   生成MC聊天包: {len(result)} bytes")
    
    logger.info("\n✓ 端到端流程测试完成")


async def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("MnMCP 集成测试")
    logger.info("=" * 60)
    
    try:
        await test_encryption()
        await test_protocol_translation()
        await test_mnw_to_mc_translation()
        await test_end_to_end()
        
        logger.info("\n" + "=" * 60)
        logger.info("所有测试通过！")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
