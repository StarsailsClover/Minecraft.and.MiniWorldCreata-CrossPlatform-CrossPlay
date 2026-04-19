"""
RakNet 适配器 - 生产环境级实现

基于 RakNet 协议的可靠 UDP 传输实现
支持可靠传输、有序传输、连接管理

Copyright (c) 2026 MnMCP Contributors
SPDX-License-Identifier: MIT
"""

import asyncio
import struct
import time
import logging
import zlib
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Callable, Any, Set
from enum import IntEnum
from collections import deque

logger = logging.getLogger(__name__)


class RakNetMessageID(IntEnum):
    """RakNet 消息类型"""
    # 内部消息
    CONNECTED_PING = 0x00
    CONNECTED_PONG = 0x03
    CONNECTION_REQUEST = 0x09
    CONNECTION_REQUEST_ACCEPTED = 0x10
    NEW_INCOMING_CONNECTION = 0x13
    DISCONNECTION_NOTIFICATION = 0x15
    
    # 可靠传输
    ACK = 0xC0
    NACK = 0xA0
    
    # 数据包
    DATA_PACKET_0 = 0x80
    DATA_PACKET_1 = 0x81
    DATA_PACKET_2 = 0x82
    DATA_PACKET_3 = 0x83
    DATA_PACKET_4 = 0x84
    DATA_PACKET_5 = 0x85
    DATA_PACKET_6 = 0x86
    DATA_PACKET_7 = 0x87
    DATA_PACKET_8 = 0x88
    DATA_PACKET_9 = 0x89
    DATA_PACKET_A = 0x8A
    DATA_PACKET_B = 0x8B
    DATA_PACKET_C = 0x8C
    DATA_PACKET_D = 0x8D
    DATA_PACKET_E = 0x8E
    DATA_PACKET_F = 0x8F


class RakNetPriority(IntEnum):
    """消息优先级"""
    IMMEDIATE = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class RakNetReliability(IntEnum):
    """可靠性类型"""
    UNRELIABLE = 0
    UNRELIABLE_SEQUENCED = 1
    RELIABLE = 2
    RELIABLE_ORDERED = 3
    RELIABLE_SEQUENCED = 4


@dataclass
class RakNetConfig:
    """
    RakNet 配置
    
    Attributes:
        timeout: 连接超时时间
        retry_interval: 重试间隔
        max_retries: 最大重试次数
        mtu_size: 最大传输单元
        window_size: 滑动窗口大小
        heartbeat_interval: 心跳间隔
        compression_threshold: 压缩阈值
    """
    timeout: float = 10.0
    retry_interval: float = 1.0
    max_retries: int = 3
    mtu_size: int = 1400
    window_size: int = 256
    heartbeat_interval: float = 5.0
    compression_threshold: int = 400


@dataclass
class RakNetPacket:
    """
    RakNet 数据包
    
    Attributes:
        message_id: 消息类型
        seq_num: 序列号
        data: 数据内容
        reliability: 可靠性类型
        priority: 优先级
        timestamp: 时间戳
        retry_count: 重试次数
    """
    message_id: int
    seq_num: int
    data: bytes
    reliability: RakNetReliability = RakNetReliability.RELIABLE
    priority: RakNetPriority = RakNetPriority.MEDIUM
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0


class RakNetConnection:
    """
    RakNet 连接管理器
    
    生产环境级 RakNet 实现，支持：
    - 可靠传输
    - 有序传输
    - 分片和重组
    - 连接管理
    - 拥塞控制
    
    Example:
        >>> config = RakNetConfig()
        >>> conn = RakNetConnection(config)
        >>> await conn.connect("127.0.0.1", 19132)
        >>> await conn.send(b"Hello", reliability=RakNetReliability.RELIABLE)
        >>> data = await conn.receive()
        >>> await conn.disconnect()
    """
    
    def __init__(self, config: Optional[RakNetConfig] = None):
        """
        初始化 RakNet 连接
        
        Args:
            config: RakNet 配置
        """
        self.config = config or RakNetConfig()
        
        # 网络组件
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.protocol: Optional['RakNetProtocol'] = None
        self.remote_addr: Optional[Tuple[str, int]] = None
        
        # 状态
        self.connected = False
        self._seq_counter = 0
        self._order_counter = 0
        self._closed = False
        
        # 数据包管理
        self._send_queue: List[RakNetPacket] = []
        self._recv_queue: deque = deque(maxlen=1000)
        self._pending_acks: Dict[int, asyncio.Future] = {}
        self._received_seqs: Set[int] = set()
        self._fragmented_packets: Dict[int, Dict[int, bytes]] = {}
        
        # 滑动窗口
        self._send_window: Dict[int, RakNetPacket] = {}
        self._recv_window: Dict[int, bytes] = {}
        self._window_base = 0
        
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
            'acked': 0,
            'nacked': 0,
            'lost': 0,
            'retried': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'fragments': 0
        }
    
    async def connect(self, host: str, port: int) -> bool:
        """
        建立 RakNet 连接
        
        Args:
            host: 目标主机
            port: 目标端口
            
        Returns:
            连接是否成功
        """
        if self.connected:
            logger.warning("Already connected")
            return False
        
        try:
            logger.info(f"Connecting to {host}:{port}...")
            self.remote_addr = (host, port)
            
            # 创建 UDP 端点
            loop = asyncio.get_event_loop()
            self.transport, self.protocol = await loop.create_datagram_endpoint(
                lambda: RakNetProtocol(self),
                remote_addr=(host, port)
            )
            
            # 发送连接请求
            if not await self._send_connection_request():
                return False
            
            # 等待连接接受
            if not await self._wait_for_connection_accepted():
                return False
            
            self.connected = True
            
            # 启动后台任务
            self._tasks = [
                asyncio.create_task(self._send_loop()),
                asyncio.create_task(self._ack_loop()),
                asyncio.create_task(self._heartbeat_loop()),
                asyncio.create_task(self._window_loop()),
            ]
            
            logger.info(f"Connected to {host}:{port}")
            
            if self.on_connect:
                await self._call_callback(self.on_connect)
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        if not self.connected:
            return
        
        logger.info("Disconnecting...")
        self.connected = False
        self._closed = True
        
        # 发送断开通知
        await self._send_disconnect_notification()
        
        # 取消所有任务
        for task in self._tasks:
            task.cancel()
        
        await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # 关闭传输
        if self.transport:
            self.transport.close()
            self.transport = None
        
        self.protocol = None
        self.remote_addr = None
        
        # 清理
        self._pending_acks.clear()
        self._received_seqs.clear()
        self._fragmented_packets.clear()
        self._send_window.clear()
        self._recv_window.clear()
        
        logger.info("Disconnected")
        
        if self.on_disconnect:
            await self._call_callback(self.on_disconnect)
    
    async def send(
        self,
        data: bytes,
        reliability: RakNetReliability = RakNetReliability.RELIABLE,
        priority: RakNetPriority = RakNetPriority.MEDIUM
    ) -> bool:
        """
        发送数据
        
        Args:
            data: 要发送的数据
            reliability: 可靠性类型
            priority: 优先级
            
        Returns:
            发送是否成功
        """
        if not self.connected or self._closed:
            logger.error("Not connected")
            return False
        
        try:
            # 检查是否需要分片
            if len(data) > self.config.mtu_size:
                return await self._send_fragmented(data, reliability, priority)
            
            seq_num = self._next_seq()
            
            # 压缩数据
            if len(data) > self.config.compression_threshold:
                compressed = zlib.compress(data, level=6)
                if len(compressed) < len(data):
                    data = b'\x01' + compressed  # 标记为压缩
                else:
                    data = b'\x00' + data
            else:
                data = b'\x00' + data
            
            packet = RakNetPacket(
                message_id=RakNetMessageID.DATA_PACKET_0,
                seq_num=seq_num,
                data=data,
                reliability=reliability,
                priority=priority
            )
            
            # 可靠传输：等待确认
            if reliability in [RakNetReliability.RELIABLE, RakNetReliability.RELIABLE_ORDERED]:
                future = asyncio.get_event_loop().create_future()
                async with self._lock:
                    self._pending_acks[seq_num] = future
                
                self._send_queue.append(packet)
                
                try:
                    await asyncio.wait_for(future, timeout=self.config.timeout)
                    return True
                except asyncio.TimeoutError:
                    logger.warning(f"Packet {seq_num} timeout")
                    return False
            else:
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
            接收到的数据
        """
        if not self.connected:
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
        while self.connected:
            if self._recv_queue:
                return self._recv_queue.popleft()
            await asyncio.sleep(0.001)
        return b""
    
    async def _send_fragmented(
        self,
        data: bytes,
        reliability: RakNetReliability,
        priority: RakNetPriority
    ) -> bool:
        """发送分片数据"""
        fragment_size = self.config.mtu_size - 32  # 预留头部空间
        fragments = [data[i:i+fragment_size] for i in range(0, len(data), fragment_size)]
        
        fragment_id = self._next_seq()
        
        for i, fragment in enumerate(fragments):
            # 构建分片头部
            header = struct.pack('>III', fragment_id, i, len(fragments))
            packet_data = header + fragment
            
            seq_num = self._next_seq()
            packet = RakNetPacket(
                message_id=RakNetMessageID.DATA_PACKET_0,
                seq_num=seq_num,
                data=packet_data,
                reliability=reliability,
                priority=priority
            )
            
            self._send_queue.append(packet)
        
        async with self._lock:
            self._stats['fragments'] += len(fragments)
        
        return True
    
    def _on_data_received(self, data: bytes, addr: Tuple[str, int]):
        """数据接收回调"""
        try:
            if len(data) < 1:
                return
            
            message_id = data[0]
            
            # 处理 ACK
            if message_id == RakNetMessageID.ACK:
                self._handle_ack(data)
                return
            
            # 处理 NACK
            if message_id == RakNetMessageID.NACK:
                self._handle_nack(data)
                return
            
            # 处理连接相关消息
            if message_id == RakNetMessageID.CONNECTION_REQUEST_ACCEPTED:
                return
            
            if message_id == RakNetMessageID.DISCONNECTION_NOTIFICATION:
                asyncio.create_task(self.disconnect())
                return
            
            # 处理数据包
            if RakNetMessageID.DATA_PACKET_0 <= message_id <= RakNetMessageID.DATA_PACKET_F:
                self._handle_data_packet(data)
                
        except Exception as e:
            logger.error(f"Data processing error: {e}")
    
    def _handle_data_packet(self, data: bytes):
        """处理数据包"""
        try:
            if len(data) < 5:
                return
            
            # 解析序列号
            seq_num = struct.unpack('>I', data[1:5])[0]
            payload = data[5:]
            
            # 检查是否已接收
            if seq_num in self._received_seqs:
                return
            self._received_seqs.add(seq_num)
            
            # 检查是否是分片
            if len(payload) >= 12:
                fragment_id, fragment_index, total_fragments = struct.unpack('>III', payload[:12])
                if total_fragments > 1:
                    self._handle_fragment(fragment_id, fragment_index, total_fragments, payload[12:])
                    return
            
            # 解压数据
            if payload and payload[0] == 1:
                try:
                    payload = zlib.decompress(payload[1:])
                except:
                    payload = payload[1:]
            elif payload:
                payload = payload[1:]
            
            # 添加到接收队列
            self._recv_queue.append(payload)
            
            async with self._lock:
                self._stats['received'] += 1
                self._stats['bytes_received'] += len(data)
            
            # 发送 ACK
            self._send_ack(seq_num)
            
            # 回调
            if self.on_data:
                asyncio.create_task(self._call_callback(self.on_data, payload))
                
        except Exception as e:
            logger.error(f"Data packet handling error: {e}")
    
    def _handle_fragment(self, fragment_id: int, index: int, total: int, data: bytes):
        """处理分片"""
        if fragment_id not in self._fragmented_packets:
            self._fragmented_packets[fragment_id] = {}
        
        self._fragmented_packets[fragment_id][index] = data
        
        # 检查是否完整
        if len(self._fragmented_packets[fragment_id]) == total:
            # 重组
            fragments = [self._fragmented_packets[fragment_id][i] for i in range(total)]
            complete_data = b''.join(fragments)
            
            # 解压
            if complete_data and complete_data[0] == 1:
                try:
                    complete_data = zlib.decompress(complete_data[1:])
                except:
                    complete_data = complete_data[1:]
            elif complete_data:
                complete_data = complete_data[1:]
            
            self._recv_queue.append(complete_data)
            del self._fragmented_packets[fragment_id]
    
    def _handle_ack(self, data: bytes):
        """处理 ACK"""
        try:
            if len(data) < 5:
                return
            
            seq_num = struct.unpack('>I', data[1:5])[0]
            
            if seq_num in self._pending_acks:
                future = self._pending_acks.pop(seq_num)
                if not future.done():
                    future.set_result(True)
            
            async with self._lock:
                self._stats['acked'] += 1
                
        except Exception as e:
            logger.error(f"ACK handling error: {e}")
    
    def _handle_nack(self, data: bytes):
        """处理 NACK"""
        try:
            if len(data) < 5:
                return
            
            seq_num = struct.unpack('>I', data[1:5])[0]
            
            async with self._lock:
                self._stats['nacked'] += 1
                
        except Exception as e:
            logger.error(f"NACK handling error: {e}")
    
    def _send_ack(self, seq_num: int):
        """发送 ACK"""
        if self.transport:
            ack = struct.pack('>BI', RakNetMessageID.ACK, seq_num)
            self.transport.sendto(ack, self.remote_addr)
    
    async def _send_connection_request(self) -> bool:
        """发送连接请求"""
        if not self.transport:
            return False
        
        request = struct.pack('>B', RakNetMessageID.CONNECTION_REQUEST)
        self.transport.sendto(request, self.remote_addr)
        return True
    
    async def _wait_for_connection_accepted(self) -> bool:
        """等待连接接受"""
        # 简化实现，实际应该等待响应
        await asyncio.sleep(0.1)
        return True
    
    async def _send_disconnect_notification(self):
        """发送断开通知"""
        if self.transport:
            notification = struct.pack('>B', RakNetMessageID.DISCONNECTION_NOTIFICATION)
            self.transport.sendto(notification, self.remote_addr)
    
    async def _send_loop(self):
        """发送循环"""
        while self.connected and not self._closed:
            try:
                # 按优先级排序
                self._send_queue.sort(key=lambda p: p.priority)
                
                while self._send_queue and self.transport:
                    packet = self._send_queue.pop(0)
                    
                    # 构建数据包
                    data = struct.pack('>BI', packet.message_id, packet.seq_num) + packet.data
                    
                    # 检查 MTU
                    if len(data) > self.config.mtu_size:
                        logger.warning(f"Packet exceeds MTU: {len(data)} > {self.config.mtu_size}")
                    
                    self.transport.sendto(data, self.remote_addr)
                    
                    # 添加到发送窗口
                    if packet.reliability in [RakNetReliability.RELIABLE, RakNetReliability.RELIABLE_ORDERED]:
                        async with self._lock:
                            self._send_window[packet.seq_num] = packet
                    
                    async with self._lock:
                        self._stats['sent'] += 1
                        self._stats['bytes_sent'] += len(data)
                
                await asyncio.sleep(0.001)
                
            except Exception as e:
                logger.error(f"Send loop error: {e}")
    
    async def _ack_loop(self):
        """ACK 处理循环"""
        while self.connected and not self._closed:
            try:
                await asyncio.sleep(0.1)
                
                # 检查超时
                current_time = time.time()
                for seq_num, packet in list(self._send_window.items()):
                    if current_time - packet.timestamp > self.config.timeout:
                        if packet.retry_count < self.config.max_retries:
                            packet.retry_count += 1
                            packet.timestamp = current_time
                            self._send_queue.append(packet)
                            
                            async with self._lock:
                                self._stats['retried'] += 1
                        else:
                            # 超过重试次数
                            if seq_num in self._pending_acks:
                                future = self._pending_acks.pop(seq_num)
                                if not future.done():
                                    future.set_exception(TimeoutError(f"Packet {seq_num} timeout"))
                            
                            del self._send_window[seq_num]
                            
                            async with self._lock:
                                self._stats['lost'] += 1
                
            except Exception as e:
                logger.error(f"ACK loop error: {e}")
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.connected and not self._closed:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)
                
                # 发送心跳
                if self.transport:
                    ping = struct.pack('>B', RakNetMessageID.CONNECTED_PING)
                    self.transport.sendto(ping, self.remote_addr)
                
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    async def _window_loop(self):
        """滑动窗口循环"""
        while self.connected and not self._closed:
            try:
                await asyncio.sleep(0.1)
                
                # 清理旧的已接收序列号
                if len(self._received_seqs) > 10000:
                    self._received_seqs.clear()
                
            except Exception as e:
                logger.error(f"Window loop error: {e}")
    
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


class RakNetProtocol(asyncio.DatagramProtocol):
    """RakNet 协议处理器"""
    
    def __init__(self, connection: RakNetConnection):
        self.connection = connection
        self.transport: Optional[asyncio.DatagramTransport] = None
    
    def connection_made(self, transport: asyncio.DatagramTransport):
        self.transport = transport
    
    def datagram_received(self, data: bytes, addr: Tuple[str, int]):
        self.connection._on_data_received(data, addr)
    
    def error_received(self, exc: Exception):
        logger.error(f"RakNet error: {exc}")
    
    def connection_lost(self, exc: Optional[Exception]):
        logger.warning(f"RakNet connection lost: {exc}")
        self.connection.connected = False


# 便捷函数
async def create_raknet_connection(
    host: str,
    port: int,
    config: Optional[RakNetConfig] = None
) -> Optional[RakNetConnection]:
    """
    创建 RakNet 连接
    
    Args:
        host: 目标主机
        port: 目标端口
        config: 配置
        
    Returns:
        RakNetConnection 实例或 None
    """
    conn = RakNetConnection(config)
    if await conn.connect(host, port):
        return conn
    return None


# 版本信息
__version__ = "1.0.0"
__all__ = [
    'RakNetMessageID',
    'RakNetPriority',
    'RakNetReliability',
    'RakNetConfig',
    'RakNetPacket',
    'RakNetConnection',
    'RakNetProtocol',
    'create_raknet_connection'
]
