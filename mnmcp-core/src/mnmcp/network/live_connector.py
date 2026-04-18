"""
MnMCP Phase 3 真实联机支持
v1.1.0_26w13a - 生产环境级实现

本模块实现迷你世界国服的真实联机连接功能
基于逆向工程分析和抓包数据实现

Copyright (c) 2026 MnMCP Contributors
SPDX-License-Identifier: MIT
"""

import struct
import asyncio
import json
import logging
import hashlib
import ssl
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any, List, Tuple
from enum import IntEnum
from urllib.parse import urlencode

import aiohttp
import websockets

from ..protocol.mnw_constants import MNWMsgType
from ..protocol.protobuf_codec import (
    PB_Vector3, PB_HeartBeatCH, PB_RoomInfo, PB_ActorOperationCH,
    encode_pb_heartbeat, decode_pb_heartbeat
)
from ..crypto.aesgcm import AESGCMCipher
from ..crypto.ecdh import ECDHKeyExchange
from ..crypto.hkdf import HKDFKeyDerivation
from ..utils.config import Config
from ..utils.logging import get_logger

logger = get_logger(__name__)


class MNWConnectionPhase(IntEnum):
    """
    MNW 连接阶段
    
    表示连接状态机的各个阶段
    """
    DISCONNECTED = 0
    CONNECTING = 1           # TCP 连接中
    HANDSHAKING = 2          # 发送 LOGIN_REQ
    AUTHENTICATING = 3       # 等待 LOGIN_RESP
    ENCRYPTED = 4            # 激活 AES 加密
    IN_GAME = 5              # 进入游戏世界
    ERROR = -1


class MNWError(Exception):
    """MNW 连接错误基类"""
    pass


class MNWAuthError(MNWError):
    """认证错误"""
    pass


class MNWConnectionError(MNWError):
    """连接错误"""
    pass


class MNWProtocolError(MNWError):
    """协议错误"""
    pass


@dataclass(frozen=True)
class MNWSessionInfo:
    """
    MNW 会话信息
    
    包含认证信息、会话密钥、游戏状态等
    
    Attributes:
        jwt_token: JWT 认证令牌
        uin: 用户唯一标识号
        device_id: 设备ID
        session_key: 会话密钥
        session_iv: 会话IV
        game_server_ip: 游戏服务器IP
        game_server_port: 游戏服务器端口
        chatpush_ws_url: 聊天WebSocket URL
        room_id: 房间ID
        world_id: 世界ID
        player_id: 玩家ID
        player_name: 玩家名称
        position: 玩家位置
        crypto_enabled: 加密是否启用
        cipher: AES-GCM 加密器
        phase: 连接阶段
    """
    jwt_token: str = ""
    uin: str = ""
    device_id: str = ""
    
    session_key: Optional[bytes] = None
    session_iv: Optional[bytes] = None
    
    game_server_ip: str = ""
    game_server_port: int = 4012
    chatpush_ws_url: str = "wss://chatpush.mini1.cn:19701"
    
    room_id: str = ""
    world_id: str = ""
    
    player_id: int = 0
    player_name: str = ""
    position: Tuple[float, float, float] = (0.0, 64.0, 0.0)
    
    crypto_enabled: bool = False
    cipher: Optional[AESGCMCipher] = None
    
    phase: MNWConnectionPhase = MNWConnectionPhase.DISCONNECTED
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.phase == MNWConnectionPhase.IN_GAME
    
    def is_encrypted(self) -> bool:
        """检查是否已加密"""
        return self.crypto_enabled and self.cipher is not None


@dataclass(frozen=True)
class MNWConnectionConfig:
    """
    MNW 连接配置
    
    生产环境级配置参数
    
    Attributes:
        auth_host: 认证服务器主机
        auth_port: 认证服务器端口
        room_host: 房间分配服务器主机
        room_port: 房间分配服务器端口
        game_port: 游戏服务器端口
        chat_host: 聊天服务器主机
        chat_port: 聊天服务器端口
        connect_timeout: 连接超时时间
        auth_timeout: 认证超时时间
        heartbeat_interval: 心跳间隔
        max_retries: 最大重试次数
        retry_delay: 重试延迟
    """
    # 认证服务器
    auth_host: str = "certification.mini1.cn"
    auth_port: int = 19921
    
    # 房间分配服务器
    room_host: str = "openroom.mini1.cn"
    room_port: int = 8080
    
    # 游戏服务器
    game_port: int = 4012
    
    # 聊天服务器
    chat_host: str = "chatpush.mini1.cn"
    chat_port: int = 19701
    
    # 超时配置
    connect_timeout: float = 10.0
    auth_timeout: float = 30.0
    heartbeat_interval: float = 30.0
    
    # 重试配置
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # SSL 配置
    verify_ssl: bool = True
    ssl_context: Optional[ssl.SSLContext] = None


class ConnectionPool:
    """
    连接池管理器
    
    管理多个 TCP 连接，支持连接复用
    """
    
    def __init__(self, max_size: int = 10, timeout: float = 30.0):
        self.max_size = max_size
        self.timeout = timeout
        self._pool: Dict[str, Tuple[asyncio.StreamReader, asyncio.StreamWriter]] = {}
        self._lock = asyncio.Lock()
        self._stats = {'created': 0, 'reused': 0, 'closed': 0}
    
    async def get_connection(self, host: str, port: int) -> Optional[Tuple[asyncio.StreamReader, asyncio.StreamWriter]]:
        """获取连接"""
        key = f"{host}:{port}"
        
        async with self._lock:
            if key in self._pool:
                reader, writer = self._pool[key]
                if not writer.is_closing():
                    self._stats['reused'] += 1
                    return reader, writer
                else:
                    del self._pool[key]
        
        # 创建新连接
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.timeout
            )
            
            async with self._lock:
                if len(self._pool) < self.max_size:
                    self._pool[key] = (reader, writer)
            
            self._stats['created'] += 1
            return reader, writer
            
        except Exception as e:
            logger.error(f"Failed to create connection: {e}")
            return None
    
    async def close_all(self):
        """关闭所有连接"""
        async with self._lock:
            for key, (reader, writer) in list(self._pool.items()):
                try:
                    writer.close()
                    await writer.wait_closed()
                except:
                    pass
            self._pool.clear()
            self._stats['closed'] += len(self._pool)
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self._stats.copy()


class MNWTCPConnector:
    """
    MNW TCP 连接器
    
    生产环境级 TCP 连接管理，支持加密和压缩
    """
    
    def __init__(self, config: MNWConnectionConfig):
        self.config = config
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.session: Optional[MNWSessionInfo] = None
        self._running = False
        self._connected = False
        self._message_handlers: Dict[int, Callable] = {}
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self._stats = {
            'sent': 0,
            'received': 0,
            'errors': 0,
            'bytes_sent': 0,
            'bytes_received': 0
        }
    
    async def connect(self, host: str, port: int) -> bool:
        """
        连接到游戏服务器
        
        Args:
            host: 服务器主机
            port: 服务器端口
            
        Returns:
            连接是否成功
        """
        try:
            logger.info(f"Connecting to {host}:{port}...")
            
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.config.connect_timeout
            )
            
            self._connected = True
            logger.info(f"Connected to {host}:{port}")
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"Connection timeout to {host}:{port}")
            return False
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        self._running = False
        
        # 取消任务
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        # 关闭连接
        if self.writer:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except:
                pass
        
        self.reader = None
        self.writer = None
        self._connected = False
        logger.info("Disconnected")
    
    async def send(self, data: bytes) -> bool:
        """
        发送数据
        
        Args:
            data: 要发送的数据
            
        Returns:
            发送是否成功
        """
        if not self.writer or self.writer.is_closing():
            logger.error("Not connected")
            return False
        
        try:
            # 加密数据
            if self.session and self.session.crypto_enabled and self.session.cipher:
                encrypted = self.session.cipher.encrypt(data)
                if encrypted:
                    data = encrypted
            
            # 发送长度前缀 + 数据
            length = len(data)
            self.writer.write(struct.pack('>I', length) + data)
            await self.writer.drain()
            
            async with self._lock:
                self._stats['sent'] += 1
                self._stats['bytes_sent'] += length + 4
            
            return True
            
        except Exception as e:
            logger.error(f"Send error: {e}")
            self._stats['errors'] += 1
            return False
    
    async def receive(self) -> Optional[bytes]:
        """
        接收数据
        
        Returns:
            接收到的数据，失败返回 None
        """
        if not self.reader:
            logger.error("Not connected")
            return None
        
        try:
            # 读取长度前缀
            length_data = await self.reader.readexactly(4)
            length = struct.unpack('>I', length_data)[0]
            
            if length > 10 * 1024 * 1024:  # 最大 10MB
                logger.error(f"Packet too large: {length} bytes")
                return None
            
            # 读取数据
            data = await self.reader.readexactly(length)
            
            # 解密数据
            if self.session and self.session.crypto_enabled and self.session.cipher:
                decrypted = self.session.cipher.decrypt(data)
                if decrypted:
                    data = decrypted
            
            async with self._lock:
                self._stats['received'] += 1
                self._stats['bytes_received'] += length + 4
            
            return data
            
        except asyncio.IncompleteReadError:
            logger.warning("Connection closed by peer")
            return None
        except Exception as e:
            logger.error(f"Receive error: {e}")
            self._stats['errors'] += 1
            return None
    
    def register_handler(self, msg_type: int, handler: Callable):
        """注册消息处理器"""
        self._message_handlers[msg_type] = handler
    
    async def send_message(self, msg_type: int, data: bytes) -> bool:
        """发送协议消息"""
        header = struct.pack('>HI', msg_type, len(data))
        return await self.send(header + data)
    
    async def receive_message(self) -> Optional[Tuple[int, bytes]]:
        """接收协议消息"""
        data = await self.receive()
        if not data or len(data) < 6:
            return None
        
        msg_type, data_len = struct.unpack('>HI', data[:6])
        payload = data[6:6+data_len]
        
        return (msg_type, payload)
    
    async def start_game_loop(self):
        """启动游戏循环"""
        self._running = True
        self._receive_task = asyncio.create_task(self._receive_loop())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
    
    async def _receive_loop(self):
        """接收循环"""
        while self._running:
            try:
                message = await self.receive_message()
                if not message:
                    break
                
                msg_type, data = message
                
                # 调用处理器
                if msg_type in self._message_handlers:
                    await self._message_handlers[msg_type](data)
                else:
                    logger.debug(f"Unhandled message type: {msg_type}")
                    
            except Exception as e:
                logger.error(f"Receive loop error: {e}")
                break
        
        logger.info("Receive loop ended")
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self._running:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)
                
                # 发送心跳包
                heartbeat = PB_HeartBeatCH(
                    BeatCode=0,
                    server_time=0,
                    client_time=int(asyncio.get_event_loop().time() * 1000)
                )
                await self.send_message(MNWMsgType.HEARTBEAT, heartbeat.encode())
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self._stats.copy()


class MNWAuthClient:
    """
    MNW 认证客户端
    
    生产环境级认证和房间分配
    """
    
    def __init__(self, config: MNWConnectionConfig):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._stats = {'login_attempts': 0, 'login_success': 0, 'errors': 0}
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建 HTTP 会话"""
        if self._session is None or self._session.closed:
            ssl_context = self.config.ssl_context
            if ssl_context is None and not self.config.verify_ssl:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            
            self._session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=ssl_context)
            )
        return self._session
    
    async def close(self):
        """关闭会话"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def login(self, uin: str, password: str, device_id: str) -> Optional[str]:
        """
        登录认证
        
        Args:
            uin: 用户UIN
            password: 密码
            device_id: 设备ID
            
        Returns:
            JWT Token 或 None
        """
        url = f"https://{self.config.auth_host}:{self.config.auth_port}/login"
        
        # 密码哈希 (MD5)
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        payload = {
            "uin": uin,
            "password": password_hash,
            "device_id": device_id,
            "platform": "WIN",
            "version": "79105"
        }
        
        self._stats['login_attempts'] += 1
        
        try:
            session = await self._get_session()
            async with session.post(url, json=payload, timeout=self.config.auth_timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    token = data.get("token")
                    if token:
                        self._stats['login_success'] += 1
                        logger.info(f"Login successful for UIN: {uin}")
                        return token
                    else:
                        logger.error("Login response missing token")
                        return None
                else:
                    logger.error(f"Login failed: HTTP {resp.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Login error: {e}")
            self._stats['errors'] += 1
            return None
    
    async def alloc_room(self, jwt_token: str) -> Optional[Dict[str, Any]]:
        """
        分配房间
        
        Args:
            jwt_token: JWT 令牌
            
        Returns:
            房间信息字典或 None
        """
        url = f"https://{self.config.room_host}:{self.config.room_port}/alloc"
        
        headers = {
            "Authorization": f"Bearer {jwt_token}"
        }
        
        try:
            session = await self._get_session()
            async with session.post(url, headers=headers, timeout=self.config.auth_timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info(f"Room allocated: {data.get('room_id')}")
                    return data
                else:
                    logger.error(f"Room allocation failed: HTTP {resp.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Room allocation error: {e}")
            self._stats['errors'] += 1
            return None
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self._stats.copy()


class MNWChatClient:
    """
    MNW 聊天客户端 (WebSocket)
    
    生产环境级 WebSocket 连接管理
    """
    
    def __init__(self, config: MNWConnectionConfig):
        self.config = config
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self._running = False
        self._message_handler: Optional[Callable] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self._stats = {'sent': 0, 'received': 0, 'errors': 0}
    
    async def connect(self, jwt_token: str) -> bool:
        """
        连接到聊天服务器
        
        Args:
            jwt_token: JWT 令牌
            
        Returns:
            连接是否成功
        """
        uri = f"wss://{self.config.chat_host}:{self.config.chat_port}"
        
        try:
            ssl_context = self.config.ssl_context
            if ssl_context is None and not self.config.verify_ssl:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            
            self.ws = await websockets.connect(
                uri,
                extra_headers={"Authorization": f"Bearer {jwt_token}"},
                ssl=ssl_context
            )
            
            self._running = True
            logger.info("Connected to chat server")
            
            # 启动接收循环
            self._receive_task = asyncio.create_task(self._receive_loop())
            
            return True
            
        except Exception as e:
            logger.error(f"Chat connection error: {e}")
            self._stats['errors'] += 1
            return False
    
    async def disconnect(self):
        """断开聊天连接"""
        self._running = False
        
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        if self.ws:
            await self.ws.close()
            self.ws = None
    
    async def send_chat(self, message: str, room_id: str = "") -> bool:
        """
        发送聊天消息
        
        Args:
            message: 消息内容
            room_id: 房间ID
            
        Returns:
            发送是否成功
        """
        if not self.ws:
            return False
        
        try:
            payload = {
                "type": "chat",
                "message": message,
                "room_id": room_id,
                "timestamp": int(asyncio.get_event_loop().time() * 1000)
            }
            
            await self.ws.send(json.dumps(payload))
            
            async with self._lock:
                self._stats['sent'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Send chat error: {e}")
            self._stats['errors'] += 1
            return False
    
    def set_message_handler(self, handler: Callable):
        """设置消息处理器"""
        self._message_handler = handler
    
    async def _receive_loop(self):
        """接收循环"""
        while self._running and self.ws:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                
                async with self._lock:
                    self._stats['received'] += 1
                
                if self._message_handler:
                    await self._message_handler(data)
                    
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Chat connection closed")
                break
            except Exception as e:
                logger.error(f"Chat receive error: {e}")
                self._stats['errors'] += 1
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self._stats.copy()


class MNWConnection:
    """
    MNW 完整连接管理器
    
    整合 TCP 游戏连接、认证和聊天功能
    """
    
    def __init__(self, config: Optional[MNWConnectionConfig] = None):
        self.config = config or MNWConnectionConfig()
        self.tcp = MNWTCPConnector(self.config)
        self.auth = MNWAuthClient(self.config)
        self.chat = MNWChatClient(self.config)
        self.session: Optional[MNWSessionInfo] = None
        self._handlers: Dict[int, Callable] = {}
        self._lock = asyncio.Lock()
        self._stats = {
            'login_attempts': 0,
            'login_success': 0,
            'errors': 0
        }
    
    async def login(self, uin: str, password: str, device_id: str) -> bool:
        """
        完整登录流程
        
        1. HTTPS 认证获取 JWT
        2. 分配房间
        3. TCP 连接游戏服务器
        4. 发送 LOGIN_REQ
        5. 接收 LOGIN_RESP 激活加密
        
        Args:
            uin: 用户UIN
            password: 密码
            device_id: 设备ID
            
        Returns:
            登录是否成功
        """
        self._stats['login_attempts'] += 1
        
        try:
            # Step 1: HTTPS 认证
            logger.info("Step 1: Authenticating...")
            jwt_token = await self.auth.login(uin, password, device_id)
            if not jwt_token:
                raise MNWAuthError("Authentication failed")
            
            # Step 2: 分配房间
            logger.info("Step 2: Allocating room...")
            room_info = await self.auth.alloc_room(jwt_token)
            if not room_info:
                raise MNWConnectionError("Room allocation failed")
            
            # 创建会话
            self.session = MNWSessionInfo(
                jwt_token=jwt_token,
                uin=uin,
                device_id=device_id,
                room_id=room_info.get("room_id", ""),
                game_server_ip=room_info.get("game_server_ip", ""),
                game_server_port=room_info.get("game_server_port", 4012),
                phase=MNWConnectionPhase.CONNECTING
            )
            
            # Step 3: TCP 连接
            logger.info("Step 3: Connecting to game server...")
            if not await self.tcp.connect(
                self.session.game_server_ip,
                self.session.game_server_port
            ):
                raise MNWConnectionError("TCP connection failed")
            
            # Step 4: 发送 LOGIN_REQ
            logger.info("Step 4: Sending LOGIN_REQ...")
            await self._send_login_req()
            
            # Step 5: 接收 LOGIN_RESP
            logger.info("Step 5: Waiting for LOGIN_RESP...")
            if not await self._receive_login_resp():
                raise MNWConnectionError("Login response failed")
            
            # Step 6: 连接聊天服务器
            logger.info("Step 6: Connecting to chat server...")
            await self.chat.connect(jwt_token)
            
            logger.info("Login complete! In game.")
            
            self._stats['login_success'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            self._stats['errors'] += 1
            self.session = None
            return False
    
    async def logout(self):
        """登出"""
        await self.chat.disconnect()
        await self.tcp.disconnect()
        self.session = None
        logger.info("Logged out")
    
    def register_handler(self, msg_type: int, handler: Callable):
        """注册消息处理器"""
        self._handlers[msg_type] = handler
        self.tcp.register_handler(msg_type, handler)
    
    async def send(self, msg_type: int, data: bytes) -> bool:
        """发送消息"""
        return await self.tcp.send_message(msg_type, data)
    
    async def _send_login_req(self):
        """发送登录请求"""
        jwt_bytes = self.session.jwt_token.encode('utf-8')
        payload = struct.pack('>I', len(jwt_bytes)) + jwt_bytes
        await self.tcp.send_message(MNWMsgType.LOGIN_REQ, payload)
    
    async def _receive_login_resp(self) -> bool:
        """接收登录响应并激活加密"""
        data = await self.tcp.receive()
        if not data or len(data) < 6:
            return False
        
        msg_type = struct.unpack('>H', data[:2])[0]
        if msg_type != MNWMsgType.LOGIN_RESP:
            logger.error(f"Expected LOGIN_RESP, got {msg_type}")
            return False
        
        # 解析 LOGIN_RESP
        if len(data) < 10:
            logger.error("LOGIN_RESP too short")
            return False
        
        result = struct.unpack('>I', data[2:6])[0]
        if result != 0:
            logger.error(f"Login failed with result: {result}")
            return False
        
        key_len = struct.unpack('>I', data[6:10])[0]
        if len(data) < 10 + key_len:
            logger.error("Session key too short")
            return False
        
        session_key = data[10:10+key_len]
        
        # 派生密钥
        hkdf = HKDFKeyDerivation()
        key_material = hkdf.derive(session_key, length=48)
        if not key_material:
            logger.error("Key derivation failed")
            return False
        
        keys = hkdf.extract_keys(key_material)
        
        # 创建加密器
        cipher = AESGCMCipher(keys['aes_key'], keys['nonce_base'])
        
        # 更新会话
        self.session = MNWSessionInfo(
            jwt_token=self.session.jwt_token,
            uin=self.session.uin,
            device_id=self.session.device_id,
            room_id=self.session.room_id,
            game_server_ip=self.session.game_server_ip,
            game_server_port=self.session.game_server_port,
            session_key=keys['aes_key'],
            session_iv=keys['nonce_base'],
            crypto_enabled=True,
            cipher=cipher,
            phase=MNWConnectionPhase.ENCRYPTED
        )
        
        self.tcp.session = self.session
        
        logger.info("Encryption activated")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'connection': self._stats.copy(),
            'tcp': self.tcp.get_stats(),
            'auth': self.auth.get_stats(),
            'chat': self.chat.get_stats()
        }


# 便捷函数
async def create_mnw_connection(
    uin: str,
    password: str,
    device_id: str,
    config: Optional[MNWConnectionConfig] = None
) -> Optional[MNWConnection]:
    """
    创建 MNW 连接
    
    Args:
        uin: 用户UIN
        password: 密码
        device_id: 设备ID
        config: 连接配置 (可选)
        
    Returns:
        MNWConnection 实例或 None
    """
    conn = MNWConnection(config)
    if await conn.login(uin, password, device_id):
        return conn
    return None


# 版本信息
__version__ = "1.1.0"
__all__ = [
    'MNWConnectionPhase',
    'MNWError',
    'MNWAuthError',
    'MNWConnectionError',
    'MNWProtocolError',
    'MNWSessionInfo',
    'MNWConnectionConfig',
    'ConnectionPool',
    'MNWTCPConnector',
    'MNWAuthClient',
    'MNWChatClient',
    'MNWConnection',
    'create_mnw_connection'
]
