"""
房间管理

实现迷你世界房间功能
"""

import logging
import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import IntEnum
from urllib import request, parse

from ..config import get_api_server, get_game_server

logger = logging.getLogger(__name__)


class RoomMode(IntEnum):
    """房间模式"""
    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2


class RoomPermission(IntEnum):
    """房间权限"""
    PUBLIC = 0
    PRIVATE = 1
    PASSWORD = 2


@dataclass
class RoomInfo:
    """房间信息"""
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


class RoomManager:
    """房间管理器"""
    
    API_BASE = "http://{}:{}".format(
        get_api_server().host,
        get_api_server().port
    )
    
    ENDPOINTS = {
        'list': '/v2/room/list',
        'create': '/v2/room/create',
        'join': '/v2/room/join',
        'leave': '/v2/room/leave',
        'info': '/v2/room/info',
        'search': '/v2/room/search',
    }
    
    def __init__(self, uin: int, token: str):
        self.uin = uin
        self.token = token
        self.headers = {
            'User-Agent': 'MiniWorld/1.53.1 (Android; 13)',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        
        self.current_room: Optional[RoomInfo] = None
    
    def get_room_list(self, page: int = 1, page_size: int = 20) -> List[RoomInfo]:
        """获取房间列表"""
        logger.info(f"Getting room list, page {page}")
        
        try:
            url = f"{self.API_BASE}{self.ENDPOINTS['list']}"
            params = {
                'page': page,
                'page_size': page_size,
            }
            
            query = parse.urlencode(params)
            full_url = f"{url}?{query}"
            
            req = request.Request(full_url, headers=self.headers, method='GET')
            
            with request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
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
                            max_players=room_data.get('max_players', 10),
                            has_password=room_data.get('has_password', False),
                            world_id=room_data.get('world_id', ''),
                            ip=room_data.get('ip', get_game_server().host),
                            port=room_data.get('port', get_game_server().port),
                        )
                        rooms.append(room)
                    
                    logger.info(f"Got {len(rooms)} rooms")
                    return rooms
                else:
                    logger.error(f"Get room list failed: {response.status}")
                    return []
                
        except Exception as e:
            logger.error(f"Get room list error: {e}")
            return []
    
    def create_room(
        self,
        name: str,
        mode: RoomMode = RoomMode.SURVIVAL,
        permission: RoomPermission = RoomPermission.PUBLIC,
        max_players: int = 10,
        password: str = ""
    ) -> Optional[RoomInfo]:
        """创建房间"""
        logger.info(f"Creating room: {name}")
        
        try:
            url = f"{self.API_BASE}{self.ENDPOINTS['create']}"
            payload = {
                'name': name,
                'mode': int(mode),
                'permission': int(permission),
                'max_players': max_players,
            }
            
            if password:
                payload['password'] = password
            
            data = json.dumps(payload).encode('utf-8')
            req = request.Request(url, data=data, headers=self.headers, method='POST')
            
            with request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    if data.get('success'):
                        room = RoomInfo(
                            room_id=data.get('room_id', ''),
                            name=name,
                            owner_uin=self.uin,
                            owner_name='',
                            mode=mode,
                            permission=permission,
                            current_players=1,
                            max_players=max_players,
                            has_password=bool(password),
                            world_id=data.get('world_id', ''),
                            ip=data.get('ip', get_game_server().host),
                            port=data.get('port', get_game_server().port),
                        )
                        
                        self.current_room = room
                        logger.info(f"Room created: {room.room_id}")
                        return room
                    else:
                        logger.error(f"Create room failed: {data.get('message')}")
                        return None
                else:
                    logger.error(f"Create room failed: {response.status}")
                    return None
                
        except Exception as e:
            logger.error(f"Create room error: {e}")
            return None
    
    def join_room(self, room_id: str, password: str = "") -> Optional[RoomInfo]:
        """加入房间"""
        logger.info(f"Joining room: {room_id}")
        
        try:
            url = f"{self.API_BASE}{self.ENDPOINTS['join']}"
            payload = {
                'room_id': room_id,
            }
            
            if password:
                payload['password'] = password
            
            data = json.dumps(payload).encode('utf-8')
            req = request.Request(url, data=data, headers=self.headers, method='POST')
            
            with request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    if data.get('success'):
                        room = RoomInfo(
                            room_id=room_id,
                            name=data.get('name', ''),
                            owner_uin=data.get('owner_uin', 0),
                            owner_name=data.get('owner_name', ''),
                            mode=RoomMode(data.get('mode', 0)),
                            permission=RoomPermission(data.get('permission', 0)),
                            current_players=data.get('current_players', 1),
                            max_players=data.get('max_players', 10),
                            has_password=data.get('has_password', False),
                            world_id=data.get('world_id', ''),
                            ip=data.get('ip', get_game_server().host),
                            port=data.get('port', get_game_server().port),
                        )
                        
                        self.current_room = room
                        logger.info(f"Joined room: {room_id}")
                        return room
                    else:
                        logger.error(f"Join room failed: {data.get('message')}")
                        return None
                else:
                    logger.error(f"Join room failed: {response.status}")
                    return None
                
        except Exception as e:
            logger.error(f"Join room error: {e}")
            return None
    
    def leave_room(self) -> bool:
        """离开房间"""
        if not self.current_room:
            return True
        
        logger.info(f"Leaving room: {self.current_room.room_id}")
        
        try:
            url = f"{self.API_BASE}{self.ENDPOINTS['leave']}"
            payload = {
                'room_id': self.current_room.room_id,
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = request.Request(url, data=data, headers=self.headers, method='POST')
            
            with request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    self.current_room = None
                    logger.info("Left room")
                    return True
                else:
                    logger.error(f"Leave room failed: {response.status}")
                    return False
                
        except Exception as e:
            logger.error(f"Leave room error: {e}")
            return False
    
    def search_room(self, keyword: str) -> List[RoomInfo]:
        """搜索房间"""
        logger.info(f"Searching room: {keyword}")
        
        try:
            url = f"{self.API_BASE}{self.ENDPOINTS['search']}"
            params = {
                'keyword': keyword,
            }
            
            query = parse.urlencode(params)
            full_url = f"{url}?{query}"
            
            req = request.Request(full_url, headers=self.headers, method='GET')
            
            with request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
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
                            max_players=room_data.get('max_players', 10),
                            has_password=room_data.get('has_password', False),
                            world_id=room_data.get('world_id', ''),
                            ip=room_data.get('ip', get_game_server().host),
                            port=room_data.get('port', get_game_server().port),
                        )
                        rooms.append(room)
                    
                    return rooms
                else:
                    return []
                
        except Exception as e:
            logger.error(f"Search room error: {e}")
            return []
