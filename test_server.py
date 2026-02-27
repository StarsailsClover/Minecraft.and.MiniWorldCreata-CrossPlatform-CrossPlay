#!/usr/bin/env python3
"""
代理服务器测试脚本
"""

import sys
import asyncio
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.proxy_server import ProxyServer
from core.session_manager import SessionManager
from utils.config_manager import ConfigManager
from utils.logger import setup_logger

logger = setup_logger("Test")


async def test_proxy_server():
    """测试代理服务器"""
    logger.info("=" * 60)
    logger.info("代理服务器测试")
    logger.info("=" * 60)
    
    # 加载配置
    config = ConfigManager("config.json")
    logger.info(f"配置加载完成: {config.config_path}")
    logger.info(f"监听地址: {config.get('server.host')}:{config.get('server.port')}")
    
    # 创建会话管理器
    session_manager = SessionManager()
    logger.info("会话管理器初始化完成")
    
    # 创建代理服务器（只创建，不启动完整服务）
    server = ProxyServer(
        host=config.get("server.host"),
        port=config.get("server.port"),
        session_manager=session_manager,
        config=config
    )
    logger.info("代理服务器实例创建成功")
    
    # 测试编解码器
    logger.info("\n测试编解码器...")
    
    from codec.mc_codec import MinecraftCodec
    from codec.mnw_codec import MiniWorldCodec
    
    mc_codec = MinecraftCodec()
    mnw_codec = MiniWorldCodec()
    
    # 测试Minecraft握手包
    handshake = mc_codec.create_handshake(
        protocol_version=766,
        server_address="localhost",
        server_port=25565,
        next_state=2
    )
    logger.info(f"Minecraft握手包创建成功: {len(handshake)} bytes")
    
    # 测试Minecraft登录包
    login = mc_codec.create_login_start("TestPlayer")
    logger.info(f"Minecraft登录包创建成功: {len(login)} bytes")
    
    # 测试迷你世界登录包
    mnw_login = mnw_codec.create_login_request(
        account_id="12345678",
        token="test_token_12345"
    )
    logger.info(f"迷你世界登录包创建成功: {len(mnw_login)} bytes")
    
    # 测试迷你世界移动包
    move = mnw_codec.create_move_packet(100.0, 64.0, 200.0)
    logger.info(f"迷你世界移动包创建成功: {len(move)} bytes")
    
    # 测试迷你世界方块包
    block = mnw_codec.create_block_place(10, 20, 30, 1, 0)
    logger.info(f"迷你世界方块包创建成功: {len(block)} bytes")
    
    logger.info("\n" + "=" * 60)
    logger.info("所有测试通过！")
    logger.info("=" * 60)
    
    # 打印服务器统计
    stats = server.get_stats()
    logger.info(f"服务器状态: {stats}")


if __name__ == "__main__":
    asyncio.run(test_proxy_server())
