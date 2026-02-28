#!/usr/bin/env python3
"""
MnMCP代理服务器 v2 - v0.4.0_26w11a_Phase 3

功能:
1. 同时监听MNW客户端和MC服务器
2. 双向协议翻译
3. 会话管理
4. 性能优化

架构:
[MNW Client] <--WebSocket--> [Proxy] <--TCP/RakNet--> [MC Server]
"""

import asyncio
import websockets
import socket
import struct
import logging
import time
from typing import Dict, List, Optional, Set, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..protocol.packet_translator import PacketTranslator, Packet
from ..protocol.mc_protocol import MCPacketFactory, PacketID
from ..protocol.block_mapper import BlockMapper
from ..utils.logger import setup_logger

logger = setup_logger("ProxyServerV2")


class ProxyState(Enum):
    """代理状态"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ProxyConfig:
    """代理配置"""
    # MNW监听配置
    mnw_host: str = "0.0.0.0"
    mnw_port: int = 8080
    mnw_use_ssl: bool = False
    
    # MC服务器配置
    mc_host: str = "127.0.0.1"
    mc_port: int = 19132  # Bedrock默认端口
    
    # 性能配置
    max_clients: int = 100
    buffer_size: int = 65536
    timeout: float = 30.0
    
    # 功能开关
    enable_translation: bool = True
    enable_compression: bool = False
    enable_encryption: bool = False
    
    # 日志
    log_level: str = "INFO"
    log_file: Optional[str] = None


@dataclass
class ClientSession:
    """客户端会话"""
    session_id: str
    mnw_ws: Optional[websockets.WebSocketServerProtocol] = None
    mc_socket: Optional[socket.socket] = None
    
    # 状态
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    
    # 统计
    packets_mnw_to_mc: int = 0
    packets_mc_to_mnw: int = 0
    bytes_mnw_to_mc: int = 0
    bytes_mc_to_mnw: int = 0
    
    # 玩家信息
    player_name: str = ""
    player_id: int = 0
    
    def update_activity(self):
        """更新活动时间"""
        self.last_activity = time.time()


class ProxyServerV2:
    """
    MnMCP代理服务器 v2
    
    改进:
    - 异步架构
    - 多客户端支持
    - 更好的错误处理
    - 性能优化
    """
    
    def __init__(self, config: ProxyConfig = None):
        self.config = config or ProxyConfig()
        self.state = ProxyState.STOPPED
        
        # 组件
        self.translator = PacketTranslator()
        self.block_mapper = BlockMapper()
        
        # 会话管理
        self.sessions: Dict[str, ClientSession] = {}
        self.session_counter = 0
        
        # 任务
        self._tasks: Set[asyncio.Task] = set()
        self._stop_event = asyncio.Event()
        
        # 服务器
        self._mnw_server: Optional[websockets.WebSocketServer] = None
        
        # 统计
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'total_packets': 0,
            'total_bytes': 0,
            'errors': 0,
        }
        
        logger.info("代理服务器v2初始化完成")
    
    async def start(self):
        """启动代理服务器"""
        if self.state != ProxyState.STOPPED:
            logger.warning(f"代理服务器状态不正确: {self.state}")
            return
        
        self.state = ProxyState.STARTING
        logger.info("=" * 70)
        logger.info(" 启动 MnMCP 代理服务器 v2")
        logger.info("=" * 70)
        logger.info(f"MNW监听: {self.config.mnw_host}:{self.config.mnw_port}")
        logger.info(f"MC服务器: {self.config.mc_host}:{self.config.mc_port}")
        
        try:
            # 启动WebSocket服务器
            self._mnw_server = await websockets.serve(
                self._handle_mnw_client,
                self.config.mnw_host,
                self.config.mnw_port,
                ping_interval=20,
                ping_timeout=10,
            )
            
            self.state = ProxyState.RUNNING
            logger.info("代理服务器已启动")
            
            # 保持运行
            await self._stop_event.wait()
            
        except Exception as e:
            logger.error(f"启动失败: {e}")
            self.state = ProxyState.ERROR
            raise
    
    async def stop(self):
        """停止代理服务器"""
        if self.state != ProxyState.RUNNING:
            return
        
        self.state = ProxyState.STOPPING
        logger.info("正在停止代理服务器...")
        
        # 触发停止事件
        self._stop_event.set()
        
        # 关闭所有会话
        for session in list(self.sessions.values()):
            await self._close_session(session)
        
        # 关闭服务器
        if self._mnw_server:
            self._mnw_server.close()
            await self._mnw_server.wait_closed()
        
        # 取消所有任务
        for task in self._tasks:
            task.cancel()
        
        self.state = ProxyState.STOPPED
        logger.info("代理服务器已停止")
    
    async def _handle_mnw_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """处理MNW客户端连接"""
        client_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"MNW客户端连接: {client_addr}")
        
        # 检查连接数限制
        if len(self.sessions) >= self.config.max_clients:
            logger.warning(f"连接数达到上限，拒绝连接: {client_addr}")
            await websocket.close(1013, "Server full")
            return
        
        # 创建会话
        self.session_counter += 1
        session_id = f"session_{self.session_counter}_{int(time.time())}"
        session = ClientSession(
            session_id=session_id,
            mnw_ws=websocket
        )
        self.sessions[session_id] = session
        self.stats['total_connections'] += 1
        self.stats['active_connections'] = len(self.sessions)
        
        try:
            # 连接MC服务器
            if not await self._connect_mc_server(session):
                logger.error(f"无法连接MC服务器，关闭会话: {session_id}")
                await websocket.close(1011, "Cannot connect to MC server")
                return
            
            # 启动双向转发
            task1 = asyncio.create_task(self._forward_mnw_to_mc(session))
            task2 = asyncio.create_task(self._forward_mc_to_mnw(session))
            
            self._tasks.add(task1)
            self._tasks.add(task2)
            
            task1.add_done_callback(self._tasks.discard)
            task2.add_done_callback(self._tasks.discard)
            
            # 等待连接关闭
            await asyncio.gather(task1, task2, return_exceptions=True)
            
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"MNW客户端断开: {client_addr}")
        except Exception as e:
            logger.error(f"处理MNW客户端时出错: {e}")
            self.stats['errors'] += 1
        finally:
            await self._close_session(session)
    
    async def _connect_mc_server(self, session: ClientSession) -> bool:
        """连接MC服务器"""
        try:
            # 创建TCP连接
            reader, writer = await asyncio.open_connection(
                self.config.mc_host,
                self.config.mc_port
            )
            
            # 存储连接
            session.mc_reader = reader
            session.mc_writer = writer
            
            logger.info(f"已连接MC服务器: {self.config.mc_host}:{self.config.mc_port}")
            return True
            
        except Exception as e:
            logger.error(f"连接MC服务器失败: {e}")
            return False
    
    async def _forward_mnw_to_mc(self, session: ClientSession):
        """转发MNW到MC"""
        try:
            async for message in session.mnw_ws:
                session.update_activity()
                
                # 解析MNW数据包
                try:
                    mnw_packet = Packet.from_bytes(message)
                except Exception as e:
                    logger.warning(f"解析MNW数据包失败: {e}")
                    continue
                
                # 翻译为MC格式
                if self.config.enable_translation:
                    mc_packet = self.translator.translate_mnw_to_mc(mnw_packet)
                else:
                    mc_packet = mnw_packet
                
                # 发送到MC服务器
                if mc_packet and session.mc_writer:
                    data = mc_packet.to_bytes()
                    session.mc_writer.write(data)
                    await session.mc_writer.drain()
                    
                    session.packets_mnw_to_mc += 1
                    session.bytes_mnw_to_mc += len(data)
                    self.stats['total_packets'] += 1
                    self.stats['total_bytes'] += len(data)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"转发MNW->MC时出错: {e}")
    
    async def _forward_mc_to_mnw(self, session: ClientSession):
        """转发MC到MNW"""
        try:
            while True:
                # 读取MC数据
                data = await session.mc_reader.read(self.config.buffer_size)
                
                if not data:
                    break
                
                session.update_activity()
                
                # 解析MC数据包
                try:
                    mc_packet = MCPacketFactory.parse_packet(data)
                except Exception as e:
                    logger.warning(f"解析MC数据包失败: {e}")
                    continue
                
                # 翻译为MNW格式
                if self.config.enable_translation:
                    mnw_packet = self.translator.translate_mc_to_mnw(mc_packet)
                else:
                    mnw_packet = mc_packet
                
                # 发送到MNW客户端
                if mnw_packet:
                    await session.mnw_ws.send(mnw_packet.to_bytes())
                    
                    session.packets_mc_to_mnw += 1
                    session.bytes_mc_to_mnw += len(data)
                    self.stats['total_packets'] += 1
                    self.stats['total_bytes'] += len(data)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"转发MC->MNW时出错: {e}")
    
    async def _close_session(self, session: ClientSession):
        """关闭会话"""
        if session.session_id not in self.sessions:
            return
        
        logger.info(f"关闭会话: {session.session_id}")
        
        # 关闭MNW连接
        if session.mnw_ws:
            try:
                await session.mnw_ws.close()
            except:
                pass
        
        # 关闭MC连接
        if hasattr(session, 'mc_writer') and session.mc_writer:
            try:
                session.mc_writer.close()
                await session.mc_writer.wait_closed()
            except:
                pass
        
        # 从会话列表移除
        del self.sessions[session.session_id]
        self.stats['active_connections'] = len(self.sessions)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'state': self.state.value,
            'sessions': len(self.sessions),
        }
    
    def get_session_info(self, session_id: str = None) -> List[Dict]:
        """获取会话信息"""
        if session_id:
            session = self.sessions.get(session_id)
            if session:
                return [{
                    'id': session.session_id,
                    'player': session.player_name,
                    'connected_at': session.connected_at,
                    'last_activity': session.last_activity,
                    'packets_mnw_to_mc': session.packets_mnw_to_mc,
                    'packets_mc_to_mnw': session.packets_mc_to_mnw,
                }]
            return []
        else:
            return [
                {
                    'id': s.session_id,
                    'player': s.player_name,
                    'connected_at': s.connected_at,
                    'last_activity': s.last_activity,
                }
                for s in self.sessions.values()
            ]


# 便捷函数
async def create_proxy(config: ProxyConfig = None) -> ProxyServerV2:
    """创建代理服务器"""
    proxy = ProxyServerV2(config)
    return proxy


__all__ = [
    'ProxyServerV2',
    'ProxyConfig',
    'ProxyState',
    'ClientSession',
    'create_proxy',
]
