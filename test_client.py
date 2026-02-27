#!/usr/bin/env python3
"""
测试客户端
模拟Minecraft客户端连接代理服务器
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from codec.mc_codec import MinecraftCodec
from utils.logger import setup_logger

logger = setup_logger("TestClient")


class MockMinecraftClient:
    """模拟Minecraft客户端"""
    
    def __init__(self, host: str = "localhost", port: int = 25565):
        self.host = host
        self.port = port
        self.codec = MinecraftCodec()
        self.reader = None
        self.writer = None
        
    async def connect(self):
        """连接到代理服务器"""
        logger.info(f"连接到代理服务器 {self.host}:{self.port}...")
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            logger.info("✅ 连接成功")
            return True
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            return False
    
    async def send_handshake(self):
        """发送握手包"""
        logger.info("发送握手包...")
        handshake = self.codec.create_handshake(
            protocol_version=766,
            server_address="localhost",
            server_port=25565,
            next_state=2  # 登录模式
        )
        self.writer.write(handshake)
        await self.writer.drain()
        logger.info(f"✅ 握手包已发送 ({len(handshake)} bytes)")
    
    async def send_login(self, username: str = "TestPlayer"):
        """发送登录包"""
        logger.info(f"发送登录包 (用户名: {username})...")
        login = self.codec.create_login_start(username)
        self.writer.write(login)
        await self.writer.drain()
        logger.info(f"✅ 登录包已发送 ({len(login)} bytes)")
    
    async def send_chat(self, message: str = "Hello!"):
        """发送聊天消息"""
        logger.info(f"发送聊天消息: {message}")
        chat = self.codec.create_chat_message(message)
        self.writer.write(chat)
        await self.writer.drain()
        logger.info(f"✅ 聊天包已发送 ({len(chat)} bytes)")
    
    async def send_position(self, x: float = 100.0, y: float = 64.0, z: float = 200.0):
        """发送位置更新"""
        logger.info(f"发送位置更新: ({x}, {y}, {z})")
        # 简化版位置包
        import struct
        data = struct.pack('>ddd', x, y, z)  # X, Y, Z
        data += struct.pack('>ff', 0.0, 0.0)  # yaw, pitch
        data += b'\x01'  # on_ground
        
        # 编码为MC数据包
        packet = self.codec.encode_packet(0x1A, data)  # 0x1A = Player Position
        self.writer.write(packet)
        await self.writer.drain()
        logger.info(f"✅ 位置包已发送 ({len(packet)} bytes)")
    
    async def read_response(self, timeout: float = 5.0):
        """读取服务器响应"""
        try:
            data = await asyncio.wait_for(self.reader.read(4096), timeout=timeout)
            if data:
                logger.info(f"📥 收到响应: {len(data)} bytes")
                logger.info(f"   数据: {data[:50].hex()}...")
                return data
            else:
                logger.info("📥 服务器关闭连接")
                return None
        except asyncio.TimeoutError:
            logger.info("⏱️ 读取超时（正常，服务器可能无响应）")
            return None
    
    async def disconnect(self):
        """断开连接"""
        if self.writer:
            logger.info("断开连接...")
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except:
                pass
            logger.info("✅ 已断开")


async def test_basic_connection():
    """测试基本连接"""
    logger.info("=" * 70)
    logger.info("测试基本连接")
    logger.info("=" * 70)
    
    client = MockMinecraftClient("localhost", 25565)
    
    # 连接
    if not await client.connect():
        return False
    
    try:
        # 发送握手
        await client.send_handshake()
        await asyncio.sleep(0.5)
        
        # 发送登录
        await client.send_login("TestPlayer123")
        await asyncio.sleep(0.5)
        
        # 读取响应
        await client.read_response(timeout=2.0)
        
        # 发送聊天
        await client.send_chat("Hello MiniWorld!")
        await asyncio.sleep(0.5)
        
        # 发送位置
        await client.send_position(100.0, 64.0, 200.0)
        await asyncio.sleep(0.5)
        
        # 再读取一次响应
        await client.read_response(timeout=2.0)
        
        logger.info("\n✅ 基本连接测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试出错: {e}")
        return False
    finally:
        await client.disconnect()


async def test_multiple_packets():
    """测试发送多个数据包"""
    logger.info("\n" + "=" * 70)
    logger.info("测试多发数据包")
    logger.info("=" * 70)
    
    client = MockMinecraftClient("localhost", 25565)
    
    if not await client.connect():
        return False
    
    try:
        # 发送握手
        await client.send_handshake()
        await asyncio.sleep(0.3)
        
        # 发送登录
        await client.send_login("MultiPacketTest")
        await asyncio.sleep(0.3)
        
        # 发送多条聊天
        for i in range(3):
            await client.send_chat(f"Message {i+1}")
            await asyncio.sleep(0.2)
        
        # 发送多个位置更新
        for i in range(3):
            await client.send_position(100.0 + i*10, 64.0, 200.0)
            await asyncio.sleep(0.2)
        
        # 等待响应
        await client.read_response(timeout=3.0)
        
        logger.info("\n✅ 多发数据包测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试出错: {e}")
        return False
    finally:
        await client.disconnect()


async def main():
    """主函数"""
    logger.info("\n" + "🧪" * 35)
    logger.info(" MnMCP 代理服务器测试客户端")
    logger.info(" 🧪" * 35 + "\n")
    
    # 测试1: 基本连接
    success1 = await test_basic_connection()
    
    # 等待一下
    await asyncio.sleep(1.0)
    
    # 测试2: 多发数据包
    success2 = await test_multiple_packets()
    
    # 总结
    logger.info("\n" + "=" * 70)
    logger.info("测试结果总结")
    logger.info("=" * 70)
    logger.info(f"基本连接测试: {'✅ 通过' if success1 else '❌ 失败'}")
    logger.info(f"多发数据包测试: {'✅ 通过' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        logger.info("\n🎉 所有测试通过！")
    else:
        logger.info("\n⚠️ 部分测试失败")
    
    return success1 and success2


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("\n测试被中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"运行时错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
