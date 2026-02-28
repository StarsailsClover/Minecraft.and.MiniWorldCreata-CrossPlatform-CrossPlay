from security.crypto_utils import decrypt as D
#!/usr/bin/env python3
"""
代理服务器核心
负责Minecraft客户端和迷你世界服务器之间的连接转发
"""

import asyncio
import logging
from typing import Optional, Dict
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ProxyConfig:
    """代理配置"""
    mc_host: str = D("ENC:KCtYUq0aeQ==")
    mc_port: int = 25565
    mnw_host: str = ""
    mnw_port: int = 0
    protocol_version: int = 1
    connect_timeout: float = 30.0
    read_timeout: float = 60.0
    buffer_size: int = 65536


class ProxyConnection:
    """单个代理连接"""
    
    def __init__(self, client_reader: asyncio.StreamReader, 
                 client_writer: asyncio.StreamWriter, 
                 session_manager=None, translator=None):
        self.client_reader = client_reader
        self.client_writer = client_writer
        self.session_manager = session_manager
        self.translator = translator
        
        # 获取客户端地址
        self.client_addr = client_writer.get_extra_info('peername')
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # 服务器连接
        self.server_reader: Optional[asyncio.StreamReader] = None
        self.server_writer: Optional[asyncio.StreamWriter] = None
        self.connected = False
        
        # 统计信息
        self.bytes_sent = 0
        self.bytes_received = 0
        self.packets_sent = 0
        self.packets_received = 0
        self.start_time = datetime.now()
        
        logger.info(f"[{self.session_id}] 新连接来自 {self.client_addr}")
    
    async def connect_to_mnw(self, host: str, port: int) -> bool:
        """连接到迷你世界服务器"""
        try:
            self.server_reader, self.server_writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=30.0
            )
            self.connected = True
            logger.info(f"[{self.session_id}] 已连接到迷你世界服务器 {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"[{self.session_id}] 连接迷你世界服务器失败: {e}")
            return False
    
    async def relay_client_to_server(self):
        """转发客户端到服务器的数据"""
        try:
            while self.connected:
                # 从客户端读取数据
                data = await self.client_reader.read(65536)
                if not data:
                    logger.info(f"[{self.session_id}] 客户端断开连接")
                    break
                
                self.bytes_received += len(data)
                self.packets_received += 1
                
                # 如果有翻译器，尝试翻译数据包
                if self.translator:
                    try:
                        translated = self.translator.mc_to_mnw(data)
                        if translated:
                            data = translated
                            logger.debug(f"[{self.session_id}] 已翻译MC->MNW数据包")
                    except Exception as e:
                        logger.debug(f"[{self.session_id}] 翻译失败，透传原始数据: {e}")
                
                # 转发到服务器
                if self.server_writer:
                    self.server_writer.write(data)
                    await self.server_writer.drain()
                    self.bytes_sent += len(data)
                    self.packets_sent += 1
                    
                    logger.debug(f"[{self.session_id}] C->S: {len(data)} bytes")
                else:
                    # 如果没有服务器连接，只是记录数据
                    logger.debug(f"[{self.session_id}] 收到客户端数据: {len(data)} bytes (无服务器连接)")
                    
        except asyncio.CancelledError:
            logger.info(f"[{self.session_id}] 客户端转发任务取消")
        except Exception as e:
            logger.error(f"[{self.session_id}] 客户端转发错误: {e}")
        finally:
            self.connected = False
    
    async def relay_server_to_client(self):
        """转发服务器到客户端的数据"""
        try:
            while self.connected:
                # 从服务器读取数据
                data = await self.server_reader.read(65536)
                if not data:
                    logger.info(f"[{self.session_id}] 服务器断开连接")
                    break
                
                # 如果有翻译器，尝试翻译数据包
                if self.translator:
                    try:
                        translated = self.translator.mnw_to_mc(data)
                        if translated:
                            data = translated
                            logger.debug(f"[{self.session_id}] 已翻译MNW->MC数据包")
                    except Exception as e:
                        logger.debug(f"[{self.session_id}] 翻译失败，透传原始数据: {e}")
                
                # 转发到客户端
                self.client_writer.write(data)
                await self.client_writer.drain()
                
                logger.debug(f"[{self.session_id}] S->C: {len(data)} bytes")
                    
        except asyncio.CancelledError:
            logger.info(f"[{self.session_id}] 服务器转发任务取消")
        except Exception as e:
            logger.error(f"[{self.session_id}] 服务器转发错误: {e}")
        finally:
            self.connected = False
    
    async def close(self):
        """关闭连接"""
        self.connected = False
        
        # 关闭服务器连接
        if self.server_writer:
            self.server_writer.close()
            try:
                await self.server_writer.wait_closed()
            except:
                pass
        
        # 关闭客户端连接
        if self.client_writer:
            self.client_writer.close()
            try:
                await self.client_writer.wait_closed()
            except:
                pass
        
        # 记录统计信息
        duration = (datetime.now() - self.start_time).total_seconds()
        logger.info(f"[{self.session_id}] 连接关闭 | "
                   f"时长: {duration:.1f}s | "
                   f"收: {self.bytes_received} bytes | "
                   f"发: {self.bytes_sent} bytes")


class ProxyServer:
    """代理服务器主类"""
    
    def __init__(self, host: str = D("ENC:KCtYUq0aeQ=="), port: int = 25565, 
                 session_manager=None, config=None, translator=None):
        self.host = host
        self.port = port
        self.session_manager = session_manager
        self.config = config
        self.translator = translator
        
        self.server: Optional[asyncio.Server] = None
        self.connections: Dict[str, ProxyConnection] = {}
        self.running = False
        
        # 统计
        self.total_connections = 0
        self.active_connections = 0
        
        logger.info(f"代理服务器初始化完成: {host}:{port}")
    
    async def start(self):
        """启动服务器"""
        self.running = True
        
        # 创建服务器
        self.server = await asyncio.start_server(
            self._handle_client,
            self.host,
            self.port
        )
        
        logger.info(f"代理服务器已启动: {self.host}:{self.port}")
        logger.info("等待Minecraft客户端连接...")
        
        # 保持运行
        async with self.server:
            await self.server.serve_forever()
    
    async def stop(self):
        """停止服务器"""
        logger.info("正在停止代理服务器...")
        self.running = False
        
        # 关闭所有连接
        close_tasks = []
        for conn in self.connections.values():
            close_tasks.append(conn.close())
        
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
        
        # 关闭服务器
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        logger.info("代理服务器已停止")
    
    async def _handle_client(self, reader: asyncio.StreamReader, 
                            writer: asyncio.StreamWriter):
        """处理客户端连接"""
        conn = None
        try:
            # 创建连接对象
            conn = ProxyConnection(
                reader, writer, 
                self.session_manager,
                self.translator
            )
            self.connections[conn.session_id] = conn
            self.total_connections += 1
            self.active_connections += 1
            
            # 创建转发任务
            task1 = asyncio.create_task(conn.relay_client_to_server())
            task2 = asyncio.create_task(conn.relay_server_to_client())
            
            # 等待任一任务完成
            done, pending = await asyncio.wait(
                [task1, task2],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # 取消剩余任务
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
        except Exception as e:
            logger.error(f"处理客户端连接时出错: {e}")
        finally:
            if conn:
                await conn.close()
                if conn.session_id in self.connections:
                    del self.connections[conn.session_id]
                self.active_connections -= 1
    
    def get_stats(self) -> dict:
        """获取服务器统计信息"""
        return {
            "total_connections": self.total_connections,
            "active_connections": self.active_connections,
            "uptime": "running" if self.running else "stopped"
        }
