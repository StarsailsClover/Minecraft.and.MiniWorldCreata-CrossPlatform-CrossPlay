#!/usr/bin/env python3
"""
简化版代理服务器
只做TCP透传，用于测试基本连接
"""

import asyncio
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SimpleProxy")


class SimpleProxy:
    """简化版代理服务器"""
    
    def __init__(self, host="0.0.0.0", port=25565):
        self.host = host
        self.port = port
        self.server = None
        self.connections = 0
        
    async def handle_client(self, reader, writer):
        """处理客户端连接"""
        addr = writer.get_extra_info('peername')
        self.connections += 1
        conn_id = self.connections
        
        logger.info(f"[Conn-{conn_id}] 新连接来自 {addr}")
        
        try:
            while True:
                # 读取数据
                data = await reader.read(4096)
                if not data:
                    logger.info(f"[Conn-{conn_id}] 客户端断开")
                    break
                
                logger.info(f"[Conn-{conn_id}] 收到 {len(data)} bytes")
                logger.info(f"[Conn-{conn_id}] 数据: {data[:30].hex()}...")
                
                # 这里只是记录，不做转发（因为没有真实MNW服务器）
                # 实际项目中这里会转发到MNW服务器
                
                # 发送一个简单的响应（模拟服务器）
                # 在实际项目中不应该这样做
                if len(data) > 0:
                    # 简单的echo响应
                    writer.write(data)
                    await writer.drain()
                    logger.info(f"[Conn-{conn_id}] 发送响应 {len(data)} bytes")
                    
        except asyncio.CancelledError:
            logger.info(f"[Conn-{conn_id}] 任务取消")
        except Exception as e:
            logger.error(f"[Conn-{conn_id}] 错误: {e}")
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except:
                pass
            logger.info(f"[Conn-{conn_id}] 连接关闭")
    
    async def start(self):
        """启动服务器"""
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        logger.info("=" * 60)
        logger.info(" MnMCP 简化版代理服务器")
        logger.info(" 仅用于测试基本连接")
        logger.info("=" * 60)
        logger.info(f"服务器启动: {self.host}:{self.port}")
        logger.info("等待连接... (按 Ctrl+C 停止)\n")
        
        async with self.server:
            await self.server.serve_forever()
    
    async def stop(self):
        """停止服务器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        logger.info("服务器已停止")


async def main():
    """主函数"""
    proxy = SimpleProxy("0.0.0.0", 25565)
    
    try:
        await proxy.start()
    except KeyboardInterrupt:
        logger.info("\n收到中断信号")
    finally:
        await proxy.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"运行时错误: {e}")
