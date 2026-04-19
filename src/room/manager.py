"""
房间管理器 - 生产环境级实现

基于 aiohttp 的异步房间管理
支持创建、加入、搜索、管理房间

Copyright (c) 2026 MnMCP Contributors
SPDX-License-Identifier: MIT
"""

import asyncio
import json
import logging
import ssl
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import IntEnum
from urllib.parse import urljoin

import aiohttp

from ..config import get_api_server, ServerConfig

logger = logging.getLogger(__name__)


class RoomMode(IntEnum):
    """房间模式"""
    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2
    SPECTATOR = 3


class RoomPermission(IntEnum):
    """房间权限"""
    PUBLIC = 0
    PRIVATE = 1
    PASSWORD = 2
    INVITE_ONLY = 3


class RoomStatus(IntEnum):
    """房间状态"""
    WAITING = 0
    PLAYING = 1
    PAUSED = 2
    ENDED = 3


@dataclass
class RoomInfo:
    """
    房间信息
    
    Attributes:
        room_id: 房间ID
        name: 房间名称
        owner_uin: 房主UIN
        owner_name: 房主名称
        mode: 游戏模式
        permission: 权限类型
        current_players: 当前玩家数
        max_players: 最大玩家数
        has_password: 是否有密码
        world_id: 世界ID
        ip: 服务器IP
        port: 服务器端口
        status: 房间状态
        tags: 房间标签
    """
    room_id: str
    name: str
    owner_uin: int
    owner_name: str
    mode: RoomMode
    permission: RoomPermission
    current_players: int
    max_players: int
    has_password: bool
    world_id: str
    ip: str
    port: int
    status: RoomStatus = RoomStatus.WAITING
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class PlayerInfo:
    """
    玩家信息
    
    Attributes:
        uin: 用户UIN
        name: 玩家名称
        is_ready: 是否准备
        is_owner: 是否房主
        join_time: 加入时间
    """
    uin: int
    name: str
    is_ready: bool = False
    is_owner: bool = False
    join_time: float = 0.0


@dataclass
class RoomConfig:
    """
    房间配置
    
    Attributes:
        name: 房间名称
        mode: 游戏模式
        permission: 权限类型
        max_players: 最大玩家数
        password: 密码
        world_id: 世界ID
        tags: 标签列表
    """
    name: str
    mode: RoomMode = RoomMode.SURVIVAL
    permission: RoomPermission = RoomPermission.PUBLIC
    max_players: int = 40
    password: str = ""
    world_id: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class RoomManager:
    """
    房间管理器
    
    生产环境级房间管理，支持：
    - 异步 HTTP 请求
    - 房间 CRUD 操作
    - 玩家管理
    - 实时状态同步
    - 事件回调
    
    Example:
        >>> manager = RoomManager(uin=123456, token="jwt_token")
        >>> rooms = await manager.get_room_list()
        >>> room = await manager.create_room(RoomConfig(name="My Room"))
        >>> await manager.join_room(room.room_id)
    """
    
    # API 端点
    ENDPOINTS = {
        'list': '/v2/room/list',
        'create': '/v2/room/create',
        'join': '/v2/room/join',
        'leave': '/v2/room/leave',
        'info': '/v2/room/info',
        'search': '/v2/room/search',
        'players': '/v2/room/players',
        'kick': '/v2/room/kick',
        'transfer': '/v2/room/transfer',
        'update': '/v2/room/update',
        'start': '/v2/room/start',
        'ready': '/v2/room/ready',
    }
    
    def __init__(self, uin: int, token: str, server: Optional[ServerConfig] = None):
        """
        初始化房间管理器
        
        Args:
            uin: 用户UIN
            token: JWT Token
            server: API 服务器配置
        """
        self.uin = uin
        self.token = token
        self.server = server or get_api_server()
        self.api_base = f"http://{self.server.host}:{self.server.port}"
        
        # HTTP 会话
        self._session: Optional[aiohttp.ClientSession] = None
        
        # 请求头
        self.headers = {
            'User-Agent': 'MiniWorld/1.53.1 (Windows; 10)',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        
        # 当前房间
        self.current_room: Optional[RoomInfo] = None
        self.players: Dict[int, PlayerInfo] = {}
        
        # 回调
        self.on_player_join: Optional[Callable[[PlayerInfo], None]] = None
        self.on_player_leave: Optional[Callable[[int], None]] = None
        self.on_room_update: Optional[Callable[[RoomInfo], None]] = None
        self.on_game_start: Optional[Callable[[], None]] = None
        
        # 任务
        self._sync_task: Optional[asyncio.Task] = None
        self._running = False
        
        # 统计
        self._stats = {
            'rooms_created': 0,
            'rooms_joined': 0,
            'rooms_left': 0,
            'players_kicked': 0,
            'errors': 0
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建 HTTP 会话"""
        if self._session is None or self._session.closed:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                limit=10,
                limit_per_host=5
            )
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.headers
            )
        
        return self._session
    
    async def close(self):
        """关闭管理器"""
        self._running = False
        
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get_room_list(
        self,
        page: int = 1,
        page_size: int = 20,
        mode: Optional[RoomMode] = None,
        permission: Optional[RoomPermission] = None
    ) -> List[RoomInfo]:
        """
        获取房间列表
        
        Args:
            page: 页码
            page_size: 每页数量
            mode: 游戏模式筛选
            permission: 权限筛选
            
        Returns:
            房间列表
        """
        try:
            logger.info(f"Getting room list, page {page}")
            
            url = urljoin(self.api_base, self.ENDPOINTS['list'])
            params = {
                'page': page,
                'page_size': page_size,
            }
            
            if mode is not None:
                params['mode'] = mode.value
            if permission is not None:
                params['permission'] = permission.value
            
            session = await self._get_session()
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    rooms = []
                    for room_data in data.get('rooms', []):
                        room = RoomInfo(
                            room_id=room_data.get('room_id', ''),
                            name=room_data.get('name', ''),
                            owner_uin=room_data.get('owner_uin', 0),
                            owner_name=room_data.get('owner_name', ''),
                            mode=RoomMode(room_data.get('mode', 0)),
                            permission=RoomPermission(room_data.get('permission', 0)),
                            current_players=room_data.get('current_players', 0),
                            max_players=room_data.get('max_players', 40),
                            has_password=room_data.get('has_password', False),
                            world_id=room_data.get('world_id', ''),
                            ip=room_data.get('ip', ''),
                            port=room_data.get('port', 0),
                            status=RoomStatus(room_data.get('status', 0)),
                            tags=room_data.get('tags', [])
                        )
                        rooms.append(room)
                    
                    return rooms
                else:
                    logger.error(f"Failed to get room list: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Get room list error: {e}")
            self._stats['errors'] += 1
            return []
    
    async def create_room(self, config: RoomConfig) -> Optional[RoomInfo]:
        """
        创建房间
        
        Args:
            config: 房间配置
            
        Returns:
            房间信息或 None
        """
        try:
            logger.info(f"Creating room: {config.name}")
            
            url = urljoin(self.api_base, self.ENDPOINTS['create'])
            payload = {
                'name': config.name,
                'mode': config.mode.value,
                'permission': config.permission.value,
                'max_players': config.max_players,
                'password': config.password,
                'world_id': config.world_id,
                'tags': config.tags
            }
            
            session = await self._get_session()
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        room = RoomInfo(
                            room_id=data.get('room_id', ''),
                            name=config.name,
                            owner_uin=self.uin,
                            owner_name="",
                            mode=config.mode,
                            permission=config.permission,
                            current_players=1,
                            max_players=config.max_players,
                            has_password=bool(config.password),
                            world_id=config.world_id,
                            ip=data.get('ip', ''),
                            port=data.get('port', 0)
                        )
                        
                        self.current_room = room
                        self._stats['rooms_created'] += 1
                        
                        # 启动状态同步
                        self._start_sync()
                        
                        logger.info(f"Room created: {room.room_id}")
                        return room
                
                logger.error(f"Failed to create room: HTTP {response.status}")
                return None
                
        except Exception as e:
            logger.error(f"Create room error: {e}")
            self._stats['errors'] += 1
            return None
    
    async def join_room(self, room_id: str, password: str = "") -> bool:
        """
        加入房间
        
        Args:
            room_id: 房间ID
            password: 密码
            
        Returns:
            是否成功
        """
        try:
            logger.info(f"Joining room: {room_id}")
            
            url = urljoin(self.api_base, self.ENDPOINTS['join'])
            payload = {
                'room_id': room_id,
                'password': password
            }
            
            session = await self._get_session()
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        # 获取房间信息
                        room = await self.get_room_info(room_id)
                        if room:
                            self.current_room = room
                            self._stats['rooms_joined'] += 1
                            
                            # 启动状态同步
                            self._start_sync()
                            
                            logger.info(f"Joined room: {room_id}")
                            return True
                
                logger.error(f"Failed to join room: HTTP {response.status}")
                return False
                
        except Exception as e:
            logger.error(f"Join room error: {e}")
            self._stats['errors'] += 1
            return False
    
    async def leave_room(self) -> bool:
        """
        离开房间
        
        Returns:
            是否成功
        """
        if not self.current_room:
            return True
        
        try:
            logger.info(f"Leaving room: {self.current_room.room_id}")
            
            url = urljoin(self.api_base, self.ENDPOINTS['leave'])
            payload = {
                'room_id': self.current_room.room_id
            }
            
            session = await self._get_session()
            
            async with session.post(url, json=payload) as response:
                self._stop_sync()
                self.current_room = None
                self.players.clear()
                self._stats['rooms_left'] += 1
                
                logger.info("Left room")
                return True
                
        except Exception as e:
            logger.error(f"Leave room error: {e}")
            self._stats['errors'] += 1
            return False
    
    async def get_room_info(self, room_id: str) -> Optional[RoomInfo]:
        """
        获取房间信息
        
        Args:
            room_id: 房间ID
            
        Returns:
            房间信息或 None
        """
        try:
            url = urljoin(self.api_base, self.ENDPOINTS['info'])
            params = {'room_id': room_id}
            
            session = await self._get_session()
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        room_data = data.get('room', {})
                        return RoomInfo(
                            room_id=room_data.get('room_id', ''),
                            name=room_data.get('name', ''),
                            owner_uin=room_data.get('owner_uin', 0),
                            owner_name=room_data.get('owner_name', ''),
                            mode=RoomMode(room_data.get('mode', 0)),
                            permission=RoomPermission(room_data.get('permission', 0)),
                            current_players=room_data.get('current_players', 0),
                            max_players=room_data.get('max_players', 40),
                            has_password=room_data.get('has_password', False),
                            world_id=room_data.get('world_id', ''),
                            ip=room_data.get('ip', ''),
                            port=room_data.get('port', 0),
                            status=RoomStatus(room_data.get('status', 0)),
                            tags=room_data.get('tags', [])
                        )
                
                return None
                
        except Exception as e:
            logger.error(f"Get room info error: {e}")
            return None
    
    async def search_rooms(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20
    ) -> List[RoomInfo]:
        """
        搜索房间
        
        Args:
            keyword: 关键词
            page: 页码
            page_size: 每页数量
            
        Returns:
            房间列表
        """
        try:
            url = urljoin(self.api_base, self.ENDPOINTS['search'])
            params = {
                'keyword': keyword,
                'page': page,
                'page_size': page_size
            }
            
            session = await self._get_session()
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    rooms = []
                    for room_data in data.get('rooms', []):
                        room = RoomInfo(
                            room_id=room_data.get('room_id', ''),
                            name=room_data.get('name', ''),
                            owner_uin=room_data.get('owner_uin', 0),
                            owner_name=room_data.get('owner_name', ''),
                            mode=RoomMode(room_data.get('mode', 0)),
                            permission=RoomPermission(room_data.get('permission', 0)),
                            current_players=room_data.get('current_players', 0),
                            max_players=room_data.get('max_players', 40),
                            has_password=room_data.get('has_password', False),
                            world_id=room_data.get('world_id', ''),
                            ip=room_data.get('ip', ''),
                            port=room_data.get('port', 0),
                            status=RoomStatus(room_data.get('status', 0))
                        )
                        rooms.append(room)
                    
                    return rooms
                
                return []
                
        except Exception as e:
            logger.error(f"Search rooms error: {e}")
            return []
    
    async def kick_player(self, target_uin: int) -> bool:
        """
        踢出玩家
        
        Args:
            target_uin: 目标玩家UIN
            
        Returns:
            是否成功
        """
        if not self.current_room:
            return False
        
        try:
            url = urljoin(self.api_base, self.ENDPOINTS['kick'])
            payload = {
                'room_id': self.current_room.room_id,
                'target_uin': target_uin
            }
            
            session = await self._get_session()
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    self._stats['players_kicked'] += 1
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Kick player error: {e}")
            return False
    
    async def set_ready(self, ready: bool = True) -> bool:
        """
        设置准备状态
        
        Args:
            ready: 是否准备
            
        Returns:
            是否成功
        """
        if not self.current_room:
            return False
        
        try:
            url = urljoin(self.api_base, self.ENDPOINTS['ready'])
            payload = {
                'room_id': self.current_room.room_id,
                'ready': ready
            }
            
            session = await self._get_session()
            
            async with session.post(url, json=payload) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Set ready error: {e}")
            return False
    
    async def start_game(self) -> bool:
        """
        开始游戏 (房主)
        
        Returns:
            是否成功
        """
        if not self.current_room:
            return False
        
        try:
            url = urljoin(self.api_base, self.ENDPOINTS['start'])
            payload = {
                'room_id': self.current_room.room_id
            }
            
            session = await self._get_session()
            
            async with session.post(url, json=payload) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Start game error: {e}")
            return False
    
    def _start_sync(self):
        """启动状态同步"""
        if not self._running:
            self._running = True
            self._sync_task = asyncio.create_task(self._sync_loop())
    
    def _stop_sync(self):
        """停止状态同步"""
        self._running = False
        if self._sync_task:
            self._sync_task.cancel()
    
    async def _sync_loop(self):
        """状态同步循环"""
        while self._running and self.current_room:
            try:
                await asyncio.sleep(5)  # 每5秒同步一次
                
                # 获取最新房间信息
                room = await self.get_room_info(self.current_room.room_id)
                if room:
                    self.current_room = room
                    
                    if self.on_room_update:
                        await self._call_callback(self.on_room_update, room)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Sync loop error: {e}")
    
    async def _call_callback(self, callback: Callable, *args):
        """安全调用回调"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logger.error(f"Callback error: {e}")
    
    def get_current_room(self) -> Optional[RoomInfo]:
        """获取当前房间"""
        return self.current_room
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self._stats.copy()


# 便捷函数
async def create_room_manager(
    uin: int,
    token: str,
    server: Optional[ServerConfig] = None
) -> RoomManager:
    """
    创建房间管理器
    
    Args:
        uin: 用户UIN
        token: JWT Token
        server: 服务器配置
        
    Returns:
        RoomManager 实例
    """
    return RoomManager(uin, token, server)


# 版本信息
__version__ = "1.0.0"
__all__ = [
    'RoomMode',
    'RoomPermission',
    'RoomStatus',
    'RoomInfo',
    'PlayerInfo',
    'RoomConfig',
    'RoomManager',
    'create_room_manager'
]
