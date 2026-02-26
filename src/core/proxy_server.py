#!/usr/bin/env python3
"""
代理服务器核心
负责Minecraft客户端和迷你世界服务器之间的连接转发
"""

import asyncio
import socket
import logging
from typing import Optional, Callable
from dataclasses import dataclass
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProxyConfig:
    """代理配置"""
    # Minecraft 监听配置
    mc_host: str = "0.0.0.0"
    mc_port: int = 25565  # 标准Minecraft端口
    
    # 迷你世界服务器配置
    mnw_host: str = ""  # 动态获取
    mnw_port: int = 0   # 动态获取
    
    # 协议版本
    protocol_version: int = 1
    
    # 超时设置
    connect_timeout: float = 30.0
    read_timeout: float = 60.0
    
    # 缓冲区大小
    buffer_size: int = 65536

class ProxyConnection:
    """单个代理连接"""
    
    def __init__(self, client_socket: socket.socket, config: ProxyConfig):
        self.client_socket = client_socket
        self.config = config
        self.server_socket: Optional[socket.socket] = None
        self.connected = False
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # 统计信息
        self.bytes_sent = 0
        self.bytes_received = 0
        self.start_time = datetime.now()
    
    async def connect_to_mnw(self, host: str, port: int) -> bool:
        """连接到迷你世界服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.settimeout(self.config.connect_timeout)
            self.server_socket.connect((host, port))
            self.connected = True
            logger.info(f"[{self.session_id}] 已连接到迷你世界服务器 {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"[{self.session_id}] 连接迷你世界服务器失败: {e}")
            return False
    
    async def relay_client_to_server(self):
        """转发客户端到服务器"""
        try:
            while self.connected:
                data = self.client_socket.recv(self.config.buffer_size)
                if not data:
                    break
                
                # TODO: 协议转换（Minecraft -> 迷你世界）
                translated_data = await self.translate_mc_to_mnw(data)
                
                self.server_socket.sendall(translated_data)
                self.bytes_sent += len(translated_data)
                
                logger.debug(f"[{self.session_id}] C->S: {len(data)} bytes")
        
        except Exception as e:
            logger.error(f"[{self.session_id}] 客户端转发错误: {e}")
        finally:
            self.connected = False
    
    async def relay_server_to_client(self):
        """转发服务器到客户端"""
        try:
            while self.connected:
                data = self.server_socket.recv(self.config.buffer_size)
                if not data:
                    break
                
                # TODO: 协议转换（迷你世界 -> Minecraft）
                translated_data = await self.translate_mnw_to_mc(data)
                
                self.client_socket.sendall(translated_data)
                self.bytes_received += len(translated_data)
                
                logger.debug(f"[{self.session_id}] S->C: {len(data)} bytes")
        
        except Exception as e:
            logger.error(f"[{self.session_id}] 服务器转发错误: {e}")
        finally:
            self.connected = False
    
    async def translate_mc_to_mnw(self, data: bytes) -> bytes:
        """Minecraft协议转迷你世界协议"""
        # TODO: 实现协议转换逻辑
        # 第一阶段：直接转发（透明代理）
        return data
    
    async def translate_mnw_to_mc(self, data: bytes) -> bytes:
        """迷你世界协议转Minecraft协议"""
        # TODO: 实现协议转换逻辑
        # 第一阶段：直接转发（透明代理）
        return data
    
    def close(self):
        """关闭连接"""
        self.connected = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        duration = (datetime.now() - self.start_time).total_seconds()
        logger.info(f"[{self.session_id}] 连接关闭 - "
                   f"持续时间: {duration:.2f}s, "
                   f"发送: {self.bytes_sent} bytes, "
                   f"接收: {self.bytes_received} bytes")

class ProxyServer:
    """代理服务器主类"""
    
    def __init__(self, config: Optional[ProxyConfig] = None):
        self.config = config or ProxyConfig()
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.connections: list[ProxyConnection] = []
        self.connection_handler: Optional[Callable] = None
    
    async def start(self):
        """启动代理服务器"""
        logger.info("=" * 60)
        logger.info("MnMCP 代理服务器启动")
        logger.info("=" * 60)
        logger.info(f"监听地址: {self.config.mc_host}:{self.config.mc_port}")
        logger.info(f"协议版本: {self.config.protocol_version}")
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.config.mc_host, self.config.mc_port))
            self.server_socket.listen(100)
            self.running = True
            
            logger.info("[+] 代理服务器已启动，等待连接...")
            
            while self.running:
                client_socket, client_addr = self.server_socket.accept()
                logger.info(f"[+] 新连接: {client_addr}")
                
                # 创建新连接处理
                asyncio.create_task(
                    self.handle_connection(client_socket, client_addr)
                )
        
        except Exception as e:
            logger.error(f"[-] 服务器错误: {e}")
        finally:
            self.stop()
    
    async def handle_connection(self, client_socket: socket.socket, client_addr):
        """处理单个连接"""
        connection = ProxyConnection(client_socket, self.config)
        self.connections.append(connection)
        
        try:
            # TODO: 从抓包分析中获取实际的服务器地址
            # 临时使用已知的服务器地址
            mnw_host = "mwu-api-pre.mini1.cn"  # 从抓包分析获得
            mnw_port = 80  # 临时端口，需要从抓包确认
            
            # 连接到迷你世界服务器
            if await connection.connect_to_mnw(mnw_host, mnw_port):
                # 启动双向转发
                await asyncio.gather(
                    connection.relay_client_to_server(),
                    connection.relay_server_to_client()
                )
        
        except Exception as e:
            logger.error(f"[-] 连接处理错误: {e}")
        finally:
            connection.close()
            if connection in self.connections:
                self.connections.remove(connection)
    
    def stop(self):
        """停止代理服务器"""
        logger.info("[*] 正在停止代理服务器...")
        self.running = False
        
        # 关闭所有连接
        for conn in self.connections:
            conn.close()
        self.connections.clear()
        
        # 关闭服务器socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("[+] 代理服务器已停止")
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "running": self.running,
            "active_connections": len(self.connections),
            "total_bytes_sent": sum(c.bytes_sent for c in self.connections),
            "total_bytes_received": sum(c.bytes_received for c in self.connections)
        }

# 测试代码
if __name__ == "__main__":
    config = ProxyConfig(
        mc_host="127.0.0.1",
        mc_port=25565
    )
    
    server = ProxyServer(config)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("\n[!] 用户中断")
        server.stop()
