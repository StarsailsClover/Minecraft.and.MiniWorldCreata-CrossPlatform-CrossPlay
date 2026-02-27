#!/usr/bin/env python3
"""
网络监控工具
监控迷你世界的网络流量
"""

import socket
import struct
import logging
from datetime import datetime
from typing import Optional, Tuple
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NetworkMonitor")


class NetworkMonitor:
    """网络监控器"""
    
    def __init__(self):
        self.packets_captured = 0
        self.bytes_captured = 0
        self.connections = {}
        
        # 迷你世界已知服务器
        self.mnw_servers = [
            "183.60.230.67",
            "183.36.42.103",
            "120.236.197.36",
            "mwu-api-pre.mini1.cn",
            "mwu-cdn-pre.mini1.cn"
        ]
    
    def log_connection(self, src_addr: Tuple[str, int], dst_addr: Tuple[str, int], 
                      data_len: int, data_preview: str):
        """记录连接信息"""
        self.packets_captured += 1
        self.bytes_captured += data_len
        
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # 判断是否是迷你世界相关流量
        is_mnw = any(server in dst_addr[0] or server in src_addr[0] 
                     for server in self.mnw_servers)
        
        direction = "->"
        if is_mnw:
            logger.info(f"[{timestamp}] [MNW] {src_addr[0]}:{src_addr[1]} {direction} "
                       f"{dst_addr[0]}:{dst_addr[1]} | {data_len} bytes")
        else:
            logger.debug(f"[{timestamp}] {src_addr[0]}:{src_addr[1]} {direction} "
                        f"{dst_addr[0]}:{dst_addr[1]} | {data_len} bytes")
        
        if data_len > 0:
            logger.debug(f"  Data: {data_preview}")
    
    def analyze_packet(self, data: bytes) -> dict:
        """分析数据包内容"""
        result = {
            "length": len(data),
            "preview": data[:32].hex() if data else "",
            "is_minecraft": False,
            "is_miniworld": False
        }
        
        # 检测Minecraft协议（VarInt开头）
        if len(data) > 0:
            first_byte = data[0]
            # Minecraft数据包通常以VarInt长度开头
            if first_byte < 128:
                result["is_minecraft"] = True
        
        # 检测迷你世界协议（特定头部）
        if len(data) >= 8:
            # 检查是否是迷你世界协议格式
            packet_type = data[0]
            sub_type = data[1]
            if packet_type in [0x01, 0x02, 0x03, 0x04, 0x05, 0x10, 0xFF]:
                result["is_miniworld"] = True
        
        return result
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "packets_captured": self.packets_captured,
            "bytes_captured": self.bytes_captured,
            "active_connections": len(self.connections)
        }


class ProxyWithMonitor:
    """带监控的代理服务器"""
    
    def __init__(self, host="0.0.0.0", port=25565):
        self.host = host
        self.port = port
        self.monitor = NetworkMonitor()
        self.server = None
        self.running = False
        
    async def handle_client(self, client_reader, client_writer):
        """处理客户端连接"""
        client_addr = client_writer.get_extra_info('peername')
        logger.info(f"[代理] 新连接: {client_addr}")
        
        try:
            while self.running:
                # 读取客户端数据
                data = await client_reader.read(65536)
                if not data:
                    break
                
                # 分析数据包
                analysis = self.monitor.analyze_packet(data)
                
                # 记录
                self.monitor.log_connection(
                    client_addr,
                    ("MNW_SERVER", 8080),
                    len(data),
                    analysis["preview"]
                )
                
                # 打印详细信息
                logger.info(f"[数据包] 长度: {analysis['length']} | "
                           f"MC: {analysis['is_minecraft']} | "
                           f"MNW: {analysis['is_miniworld']}")
                logger.info(f"[数据] {data[:50].hex()}...")
                
                # Echo回客户端（测试用）
                client_writer.write(data)
                await client_writer.drain()
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"[代理] 错误: {e}")
        finally:
            client_writer.close()
            logger.info(f"[代理] 连接关闭: {client_addr}")
    
    async def start(self):
        """启动代理"""
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        self.running = True
        
        logger.info("=" * 70)
        logger.info(" MnMCP 网络监控代理")
        logger.info(" 用于捕获和分析迷你世界网络流量")
        logger.info("=" * 70)
        logger.info(f"代理服务器: {self.host}:{self.port}")
        logger.info("请配置迷你世界客户端连接此代理")
        logger.info("按 Ctrl+C 停止\n")
        
        async with self.server:
            await self.server.serve_forever()
    
    async def stop(self):
        """停止代理"""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        stats = self.monitor.get_stats()
        logger.info("\n" + "=" * 70)
        logger.info(" 监控统计")
        logger.info("=" * 70)
        logger.info(f"捕获数据包: {stats['packets_captured']}")
        logger.info(f"捕获字节数: {stats['bytes_captured']}")
        logger.info("=" * 70)


async def main():
    """主函数"""
    proxy = ProxyWithMonitor("0.0.0.0", 25565)
    
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
