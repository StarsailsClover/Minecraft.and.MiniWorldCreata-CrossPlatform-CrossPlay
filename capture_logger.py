#!/usr/bin/env python3
"""
简化版数据包记录器
记录所有接收到的数据包到文件
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('packet_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CaptureLogger")


class SimpleCaptureProxy:
    """简化版捕获代理"""
    
    def __init__(self, host="0.0.0.0", port=25565):
        self.host = host
        self.port = port
        self.server = None
        self.running = False
        self.packet_count = 0
        self.log_file = Path("captured_packets.txt")
        
    def log_packet(self, direction, addr, data):
        """记录数据包"""
        self.packet_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        log_entry = f"\n{'='*70}\n"
        log_entry += f"[{timestamp}] Packet #{self.packet_count}\n"
        log_entry += f"Direction: {direction}\n"
        log_entry += f"Address: {addr}\n"
        log_entry += f"Length: {len(data)} bytes\n"
        log_entry += f"Hex: {data.hex()}\n"
        log_entry += f"ASCII: {self._to_ascii(data)}\n"
        
        # 写入文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # 控制台输出
        logger.info(f"[{direction}] {len(data)} bytes from {addr}")
        logger.info(f"  Hex: {data[:50].hex()}...")
    
    def _to_ascii(self, data):
        """转换为可打印ASCII"""
        result = ""
        for b in data:
            if 32 <= b < 127:
                result += chr(b)
            else:
                result += "."
        return result
    
    async def handle_client(self, reader, writer):
        """处理客户端连接"""
        addr = writer.get_extra_info('peername')
        logger.info(f"[连接] 新客户端: {addr}")
        
        try:
            while self.running:
                data = await reader.read(65536)
                if not data:
                    break
                
                # 记录数据包
                self.log_packet("C->S", addr, data)
                
                # Echo回客户端
                writer.write(data)
                await writer.drain()
                
                # 记录响应
                self.log_packet("S->C", addr, data)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"[错误] {e}")
        finally:
            writer.close()
            logger.info(f"[断开] 客户端: {addr}")
    
    async def start(self):
        """启动代理"""
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        self.running = True
        
        print("=" * 70)
        print(" MnMCP 数据包记录代理")
        print("=" * 70)
        print(f"代理服务器: {self.host}:{self.port}")
        print(f"日志文件: {self.log_file.absolute()}")
        print("按 Ctrl+C 停止\n")
        
        async with self.server:
            await self.server.serve_forever()
    
    async def stop(self):
        """停止代理"""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        print("\n" + "=" * 70)
        print(" 记录完成")
        print("=" * 70)
        print(f"总数据包: {self.packet_count}")
        print(f"日志文件: {self.log_file.absolute()}")
        print("=" * 70)


async def main():
    """主函数"""
    proxy = SimpleCaptureProxy("0.0.0.0", 25565)
    
    try:
        await proxy.start()
    except KeyboardInterrupt:
        print("\n收到中断信号")
    finally:
        await proxy.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"运行时错误: {e}")
