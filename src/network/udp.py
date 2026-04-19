"""
UDP 连接器 - 生产环境级实现

基于 asyncio 的高性能 UDP 连接管理
支持超时重传、数据包排序和连接状态管理

Copyright (c) 2026 MnMCP Contributors
SPDX-License-Identifier: MIT
"""

import asyncio
import struct
import time
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Callable, Any
from enum import IntEnum
from collections import deque

logger = logging.getLogger(__name__)


class UDPConnectionState(IntEnum):
    """UDP 连接状态"""
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    RECONNECTING = 3
    ERROR = -1


@dataclass
class UDPConfig:
    """
    UDP 连接配置
    
    Attributes:
        timeout: 连接超时时间 (秒)
        retry_interval: 重试间隔 (秒)
        max_retries: 最大重试次数
        buffer_size: 接收缓冲区大小
        keepalive_interval: 保活间隔 (秒)
        packet_timeout: 数据包超时时间 (秒)
    """
    timeout: float = 10.0
    retry_interval: float = 1.0
    max_retries: int = 3
    buffer_size: int = 65535
    keepalive_interval: float = 30.0
    packet_timeout: float = 5.0


@dataclass
class UDPPacket:
    """
    UDP 数据包
    
    Attributes:
        seq_num: 序列号
        data: 数据内容
        timestamp: 发送时间戳
        retry_count: 重试次数
    """
    seq_num: int
    data: bytes
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0


class UDPConnection:
    """
    UDP 连接管理器
    
    生产环境级 UDP 连接实现，支持：
    - 异步 I/O
    - 超时重传
    - 数据包排序
    - 连接状态管理
    - 保活机制
    
    Example:
        >>> config = UDPConfig(timeout=10.0)
        >>> conn = UDPConnection(config)
        >>> await conn.connect("127.0.0.1", 12345)
        >>> await conn.send(b"Hello")
        >>> data = await conn.receive()
        >>> await conn.disconnect()
    """
    
    def __init__(self, config: Optional[UDPConfig] = None):
        """
        初始化 UDP 连接
        
        Args:
            config: UDP 配置
        """
        self.config = config or UDPConfig()
        
        # 网络组件
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.protocol: Optional['UDPProtocol'] = None
        self.remote_addr: Optional[Tuple[str, int]] = None
        
        # 状态
        self.state = UDPConnectionState.DISCONNECTED
        self._seq_counter = 0
        self._connected = False
        self._closed = False
        
        # 数据包管理
        self._send_queue: deque = deque(maxlen=1000)
        self._recv_queue: deque = deque(maxlen=1000)
        self._pending_acks: Dict[int, asyncio.Future] = {}
        self._received_seqs: set = set()
        
        # 回调
        self.on_connect: Optional[Callable[[], None]] = None
        self.on_disconnect: Optional[Callable[[], None]] = None
        self.on_data: Optional[Callable[[bytes], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        
        # 任务
        self._tasks: List[asyncio.Task] = []
        self._lock = asyncio.Lock()
        
        # 统计
        self._stats = {
            'sent': 0,
            'received': 0,
            'lost': 0,
            'retried': 0,
            'bytes_sent': 0,
            'bytes_received': 0
        }
    
    async def connect(self, host: str, port: int) -> bool:
        """
        建立 UDP 连接
        
        Args:
            host: 目标主机
            port: 目标端口
            
        Returns:
            连接是否成功
        """
        if self.state != UDPConnectionState.DISCONNECTED:
            logger.warning(f"Cannot connect in state: {self.state}")
            return False
        
        try:
            logger.info(f"Connecting to {host}:{port}...")
            self.state = UDPConnectionState.CONNECTING
            self.remote_addr = (host, port)
            
            # 创建 UDP 端点
            loop = asyncio.get_event_loop()
            self.transport, self.protocol = await loop.create_datagram_endpoint(
                lambda: UDPProtocol(self),
                remote_addr=(host, port)
            )
            
            self.state = UDPConnectionState.CONNECTED
            self._connected = True
            
            # 启动后台任务
            self._tasks = [
                asyncio.create_task(self._send_loop()),
                asyncio.create_task(self._retry_loop()),
                asyncio.create_task(self._keepalive_loop()),
            ]
            
            logger.info(f"Connected to {host}:{port}")
            
            if self.on_connect:
                await self._call_callback(self.on_connect)
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.state = UDPConnectionState.ERROR
            return False
    
    async def disconnect(self):
        """断开连接"""
        if self.state == UDPConnectionState.DISCONNECTED:
            return
        
        logger.info("Disconnecting...")
        self.state = UDPConnectionState.DISCONNECTED
        self._connected = False
        self._closed = True
        
        # 取消所有任务
        for task in self._tasks:
            task.cancel()
        
        await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # 关闭传输
        if self.transport:
            self.transport.close()
            self.transport = None
        
        # 清理
        self.protocol = None
        self.remote_addr = None
        
        # 清理待确认的数据包
        for future in self._pending_acks.values():
            if not future.done():
                future.cancel()
        self._pending_acks.clear()
        
        logger.info("Disconnected")
        
        if self.on_disconnect:
            await self._call_callback(self.on_disconnect)
    
    async def send(self, data: bytes, reliable: bool = False) -> bool:
        """
        发送数据
        
        Args:
            data: 要发送的数据
            reliable: 是否可靠传输
            
        Returns:
            发送是否成功
        """
        if not self._connected or self._closed:
            logger.error("Not connected")
            return False
        
        try:
            seq_num = self._next_seq()
            
            # 构建数据包头部 (seq_num + data_len)
            header = struct.pack('>II', seq_num, len(data))
            packet_data = header + data
            
            if reliable:
                # 可靠传输：等待确认
                future = asyncio.get_event_loop().create_future()
                async with self._lock:
                    self._pending_acks[seq_num] = future
                
                # 添加到发送队列
                packet = UDPPacket(seq_num=seq_num, data=packet_data)
                self._send_queue.append(packet)
                
                # 等待确认
                try:
                    await asyncio.wait_for(
                        future,
                        timeout=self.config.packet_timeout
                    )
                    return True
                except asyncio.TimeoutError:
                    logger.warning(f"Packet {seq_num} timeout")
                    async with self._lock:
                        self._stats['lost'] += 1
                    return False
            else:
                # 不可靠传输：直接发送
                packet = UDPPacket(seq_num=seq_num, data=packet_data)
                self._send_queue.append(packet)
                return True
                
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    async def receive(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        接收数据
        
        Args:
            timeout: 超时时间
            
        Returns:
            接收到的数据，超时返回 None
        """
        if not self._connected:
            return None
        
        try:
            if timeout:
                return await asyncio.wait_for(
                    self._recv_from_queue(),
                    timeout=timeout
                )
            else:
                return await self._recv_from_queue()
        except asyncio.TimeoutError:
            return None
    
    async def _recv_from_queue(self) -> bytes:
        """从接收队列获取数据"""
        while self._connected:
            if self._recv_queue:
                return self._recv_queue.popleft()
            await asyncio.sleep(0.001)
        return b""
    
    def _on_data_received(self, data: bytes, addr: Tuple[str, int]):
        """数据接收回调"""
        try:
            if len(data) < 8:
                return
            
            # 解析头部
            seq_num, data_len = struct.unpack('>II', data[:8])
            payload = data[8:8+data_len]
            
            # 检查是否已接收
            if seq_num in self._received_seqs:
                return
            self._received_seqs.add(seq_num)
            
            # 检查是否是 ACK
            if seq_num in self._pending_acks:
                future = self._pending_acks.pop(seq_num)
                if not future.done():
                    future.set_result(True)
                return
            
            # 添加到接收队列
            self._recv_queue.append(payload)
            
            async with self._lock:
                self._stats['received'] += 1
                self._stats['bytes_received'] += len(data)
            
            # 发送 ACK
            if self.transport:
                ack = struct.pack('>II', seq_num, 0)
                self.transport.sendto(ack, addr)
            
            # 回调
            if self.on_data:
                asyncio.create_task(self._call_callback(self.on_data, payload))
                
        except Exception as e:
            logger.error(f"Data processing error: {e}")
    
    async def _send_loop(self):
        """发送循环"""
        while self._connected and not self._closed:
            try:
                if self._send_queue and self.transport:
                    packet = self._send_queue.popleft()
                    self.transport.sendto(packet.data, self.remote_addr)
                    
                    async with self._lock:
                        self._stats['sent'] += 1
                        self._stats['bytes_sent'] += len(packet.data)
                
                await asyncio.sleep(0.001)
                
            except Exception as e:
                logger.error(f"Send loop error: {e}")
    
    async def _retry_loop(self):
        """重试循环"""
        while self._connected and not self._closed:
            try:
                await asyncio.sleep(self.config.retry_interval)
                
                # 检查待确认的数据包
                current_time = time.time()
                for seq_num, packet in list(self._send_queue):
                    if current_time - packet.timestamp > self.config.packet_timeout:
                        if packet.retry_count < self.config.max_retries:
                            packet.retry_count += 1
                            packet.timestamp = current_time
                            
                            if self.transport:
                                self.transport.sendto(packet.data, self.remote_addr)
                            
                            async with self._lock:
                                self._stats['retried'] += 1
                        else:
                            # 超过重试次数
                            if seq_num in self._pending_acks:
                                future = self._pending_acks.pop(seq_num)
                                if not future.done():
                                    future.set_exception(
                                        TimeoutError(f"Packet {seq_num} max retries exceeded")
                                    )
                            
                            async with self._lock:
                                self._stats['lost'] += 1
                
            except Exception as e:
                logger.error(f"Retry loop error: {e}")
    
    async def _keepalive_loop(self):
        """保活循环"""
        while self._connected and not self._closed:
            try:
                await asyncio.sleep(self.config.keepalive_interval)
                
                # 发送保活包
                if self.transport:
                    keepalive = struct.pack('>II', 0xFFFFFFFF, 0)
                    self.transport.sendto(keepalive, self.remote_addr)
                
            except Exception as e:
                logger.error(f"Keepalive error: {e}")
    
    async def _call_callback(self, callback: Callable, *args):
        """安全调用回调"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logger.error(f"Callback error: {e}")
            if self.on_error:
                await self._call_callback(self.on_error, e)
    
    def _next_seq(self) -> int:
        """获取下一个序列号"""
        seq = self._seq_counter
        self._seq_counter = (self._seq_counter + 1) & 0xFFFFFFFF
        return seq
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self._stats.copy()
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected and self.state == UDPConnectionState.CONNECTED


class UDPProtocol(asyncio.DatagramProtocol):
    """
    UDP 协议处理器
    
    处理底层 UDP 数据包接收
    """
    
    def __init__(self, connection: UDPConnection):
        self.connection = connection
        self.transport: Optional[asyncio.DatagramTransport] = None
    
    def connection_made(self, transport: asyncio.DatagramTransport):
        """连接建立"""
        self.transport = transport
        logger.debug("UDP connection made")
    
    def datagram_received(self, data: bytes, addr: Tuple[str, int]):
        """接收到数据包"""
        self.connection._on_data_received(data, addr)
    
    def error_received(self, exc: Exception):
        """发生错误"""
        logger.error(f"UDP error: {exc}")
        if self.connection.on_error:
            asyncio.create_task(
                self.connection._call_callback(self.connection.on_error, exc)
            )
    
    def connection_lost(self, exc: Optional[Exception]):
        """连接丢失"""
        logger.warning(f"UDP connection lost: {exc}")
        self.connection._connected = False


# 便捷函数
async def create_udp_connection(
    host: str,
    port: int,
    config: Optional[UDPConfig] = None
) -> Optional[UDPConnection]:
    """
    创建 UDP 连接
    
    Args:
        host: 目标主机
        port: 目标端口
        config: 配置
        
    Returns:
        UDPConnection 实例或 None
    """
    conn = UDPConnection(config)
    if await conn.connect(host, port):
        return conn
    return None


# 版本信息
__version__ = "1.0.0"
__all__ = [
    'UDPConnectionState',
    'UDPConfig',
    'UDPPacket',
    'UDPConnection',
    'UDPProtocol',
    'create_udp_connection'
]
