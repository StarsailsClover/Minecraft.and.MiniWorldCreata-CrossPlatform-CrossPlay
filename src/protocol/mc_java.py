"""
Minecraft Java 协议适配

实现 Minecraft Java 版协议解析和生成
"""

import struct
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import IntEnum

logger = logging.getLogger(__name__)


class MCJavaPacketID(IntEnum):
    """Minecraft Java 数据包 ID"""
    # Handshake
    HANDSHAKE = 0x00
    
    # Login
    LOGIN_START = 0x00
    LOGIN_SUCCESS = 0x02
    SET_COMPRESSION = 0x03
    LOGIN_PLUGIN_REQUEST = 0x04
    LOGIN_PLUGIN_RESPONSE = 0x02
    
    # Play
    SPAWN_ENTITY = 0x00
    SPAWN_EXPERIENCE_ORB = 0x01
    SPAWN_PLAYER = 0x02
    ENTITY_ANIMATION = 0x03
    STATISTICS = 0x04
    ACKNOWLEDGE_PLAYER_DIGGING = 0x05
    BLOCK_BREAK_ANIMATION = 0x06
    BLOCK_ENTITY_DATA = 0x07
    BLOCK_ACTION = 0x08
    BLOCK_CHANGE = 0x09
    BOSS_BAR = 0x0A
    SERVER_DIFFICULTY = 0x0B
    CHAT_MESSAGE = 0x0E
    MULTI_BLOCK_CHANGE = 0x10
    TAB_COMPLETE = 0x11
    DECLARE_COMMANDS = 0x12
    WINDOW_CONFIRMATION = 0x13
    CLOSE_WINDOW = 0x14
    WINDOW_ITEMS = 0x15
    WINDOW_PROPERTY = 0x16
    SET_SLOT = 0x17
    SET_COOLDOWN = 0x18
    PLUGIN_MESSAGE = 0x19
    NAMED_SOUND_EFFECT = 0x1A
    DISCONNECT = 0x1B
    ENTITY_STATUS = 0x1C
    EXPLOSION = 0x1D
    UNLOAD_CHUNK = 0x1E
    CHANGE_GAME_STATE = 0x1F
    OPEN_HORSE_WINDOW = 0x20
    KEEP_ALIVE = 0x21
    CHUNK_DATA = 0x22
    EFFECT = 0x23
    PARTICLE = 0x24
    UPDATE_LIGHT = 0x25
    JOIN_GAME = 0x26
    MAP_DATA = 0x27
    TRADE_LIST = 0x28
    ENTITY_POSITION = 0x29
    ENTITY_POSITION_AND_ROTATION = 0x2A
    ENTITY_ROTATION = 0x2B
    ENTITY_MOVEMENT = 0x2C
    VEHICLE_MOVE = 0x2D
    OPEN_BOOK = 0x2E
    OPEN_WINDOW = 0x2F
    OPEN_SIGN_EDITOR = 0x30
    CRAFT_RECIPE_RESPONSE = 0x31
    PLAYER_ABILITIES = 0x32
    COMBAT_EVENT = 0x33
    PLAYER_INFO = 0x34
    FACE_PLAYER = 0x35
    PLAYER_POSITION_AND_LOOK = 0x36
    UNLOCK_RECIPES = 0x37
    DESTROY_ENTITIES = 0x38
    REMOVE_ENTITY_EFFECT = 0x39
    RESOURCE_PACK_SEND = 0x3A
    RESPAWN = 0x3B
    ENTITY_HEAD_LOOK = 0x3C
    SELECT_ADVANCEMENT_TAB = 0x3D
    WORLD_BORDER = 0x3E
    CAMERA = 0x3F
    HELD_ITEM_CHANGE = 0x40
    UPDATE_VIEW_POSITION = 0x41
    UPDATE_VIEW_DISTANCE = 0x42
    SPAWN_POSITION = 0x43
    DISPLAY_SCOREBOARD = 0x44
    ENTITY_METADATA = 0x45
    ATTACH_ENTITY = 0x46
    ENTITY_VELOCITY = 0x47
    ENTITY_EQUIPMENT = 0x48
    SET_EXPERIENCE = 0x49
    UPDATE_HEALTH = 0x4A
    SCOREBOARD_OBJECTIVE = 0x4B
    SET_PASSENGERS = 0x4C
    TEAMS = 0x4D
    UPDATE_SCORE = 0x4E
    TIME_UPDATE = 0x52
    TITLE = 0x53
    ENTITY_SOUND_EFFECT = 0x54
    SOUND_EFFECT = 0x55
    STOP_SOUND = 0x56
    PLAYER_LIST_HEADER_AND_FOOTER = 0x57
    NBT_QUERY_RESPONSE = 0x58
    COLLECT_ITEM = 0x59
    ENTITY_TELEPORT = 0x5A
    ADVANCEMENTS = 0x5B
    ENTITY_PROPERTIES = 0x5C
    ENTITY_EFFECT = 0x5D
    DECLARE_RECIPES = 0x5E
    TAGS = 0x5F


@dataclass
class MCJavaPacket:
    """Minecraft Java 数据包"""
    packet_id: int
    data: bytes
    
    def encode(self) -> bytes:
        """编码数据包"""
        # 格式: length (varint) + packet_id (varint) + data
        packet_data = self._encode_varint(self.packet_id) + self.data
        length = len(packet_data)
        return self._encode_varint(length) + packet_data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['MCJavaPacket']:
        """解码数据包"""
        try:
            offset = 0
            length, offset = cls._decode_varint(data, offset)
            packet_id, offset = cls._decode_varint(data, offset)
            payload = data[offset:offset+length-1]
            
            return cls(packet_id=packet_id, data=payload)
        except Exception as e:
            logger.error(f"Decode error: {e}")
            return None
    
    @staticmethod
    def _encode_varint(value: int) -> bytes:
        """编码 varint"""
        result = []
        while value > 127:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value)
        return bytes(result)
    
    @staticmethod
    def _decode_varint(data: bytes, offset: int) -> Tuple[int, int]:
        """解码 varint"""
        result = 0
        shift = 0
        while True:
            byte = data[offset]
            offset += 1
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7
        return result, offset


class MCJavaProtocol:
    """Minecraft Java 协议处理器"""
    
    def __init__(self):
        self.compression_threshold = -1  # -1 = 禁用压缩
    
    def create_handshake(self, host: str, port: int, protocol_version: int = 760) -> MCJavaPacket:
        """创建握手包"""
        # 协议版本 (varint) + 服务器地址 (string) + 端口 (unsigned short) + 下一个状态 (varint)
        data = b''
        data += self._encode_varint(protocol_version)
        data += self._encode_string(host)
        data += struct.pack('>H', port)
        data += self._encode_varint(2)  # 2 = login
        
        return MCJavaPacket(packet_id=MCJavaPacketID.HANDSHAKE, data=data)
    
    def create_login_start(self, username: str) -> MCJavaPacket:
        """创建登录开始包"""
        data = self._encode_string(username)
        return MCJavaPacket(packet_id=MCJavaPacketID.LOGIN_START, data=data)
    
    def create_keep_alive(self, keep_alive_id: int) -> MCJavaPacket:
        """创建心跳包"""
        data = struct.pack('>Q', keep_alive_id)
        return MCJavaPacket(packet_id=MCJavaPacketID.KEEP_ALIVE, data=data)
    
    def create_chat_message(self, message: str) -> MCJavaPacket:
        """创建聊天消息包"""
        data = self._encode_string(message)
        return MCJavaPacket(packet_id=MCJavaPacketID.CHAT_MESSAGE, data=data)
    
    def create_player_position(self, x: float, y: float, z: float, on_ground: bool) -> MCJavaPacket:
        """创建玩家位置包"""
        data = struct.pack('>ddd', x, y, z)
        data += b'\x01' if on_ground else b'\x00'
        return MCJavaPacket(packet_id=MCJavaPacketID.PLAYER_POSITION_AND_LOOK, data=data)
    
    def _encode_varint(self, value: int) -> bytes:
        """编码 varint"""
        result = []
        while value > 127:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value)
        return bytes(result)
    
    def _encode_string(self, s: str) -> bytes:
        """编码字符串"""
        encoded = s.encode('utf-8')
        return self._encode_varint(len(encoded)) + encoded
    
    def _decode_string(self, data: bytes, offset: int) -> Tuple[str, int]:
        """解码字符串"""
        length, offset = MCJavaPacket._decode_varint(data, offset)
        s = data[offset:offset+length].decode('utf-8')
        return s, offset + length
