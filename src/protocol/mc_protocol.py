#!/usr/bin/env python3
"""
Minecraft Bedrock版协议实现 - v0.4.0_26w11a_Phase 3

功能:
1. 数据包序列化/反序列化
2. 变长整数编码 (VarInt)
3. NBT数据处理
4. 基础数据包类型

参考:
- https://wiki.vg/Bedrock_Protocol
"""

import struct
import json
import logging
from typing import Dict, List, Optional, Tuple, Union, BinaryIO
from dataclasses import dataclass, field
from enum import IntEnum
from io import BytesIO

logger = logging.getLogger(__name__)


class PacketID(IntEnum):
    """Minecraft Bedrock版数据包ID"""
    # 登录相关
    LOGIN = 0x01
    PLAY_STATUS = 0x02
    SERVER_TO_CLIENT_HANDSHAKE = 0x03
    CLIENT_TO_SERVER_HANDSHAKE = 0x04
    DISCONNECT = 0x05
    
    # 世界数据
    RESOURCE_PACKS_INFO = 0x06
    RESOURCE_PACK_STACK = 0x07
    RESOURCE_PACK_CLIENT_RESPONSE = 0x08
    TEXT = 0x09
    SET_TIME = 0x0A
    START_GAME = 0x0B
    ADD_PLAYER = 0x0C
    ADD_ENTITY = 0x0D
    REMOVE_ENTITY = 0x0E
    ADD_ITEM_ENTITY = 0x0F
    
    # 玩家交互
    MOVE_PLAYER = 0x13
    RIDER_JUMP = 0x14
    UPDATE_BLOCK = 0x15
    ADD_PAINTING = 0x16
    TICK_SYNC = 0x17
    
    # 方块操作
    LEVEL_SOUND_EVENT = 0x18
    LEVEL_EVENT = 0x19
    BLOCK_EVENT = 0x1A
    ENTITY_EVENT = 0x1B
    MOB_EFFECT = 0x1C
    UPDATE_ATTRIBUTES = 0x1D
    INVENTORY_TRANSACTION = 0x1E
    MOB_EQUIPMENT = 0x1F
    
    # 交互
    INTERACT = 0x21
    BLOCK_PICK_REQUEST = 0x22
    ENTITY_PICK_REQUEST = 0x23
    PLAYER_ACTION = 0x24
    
    # 聊天
    TEXT_MESSAGE = 0x25  # 聊天消息
    
    # 世界数据
    SET_SPAWN_POSITION = 0x2B
    ANIMATE = 0x2C
    RESPAWN = 0x2D
    CONTAINER_OPEN = 0x2E
    CONTAINER_CLOSE = 0x2F
    
    # 库存
    INVENTORY_CONTENT = 0x31
    INVENTORY_SLOT = 0x32
    CONTAINER_SET_DATA = 0x33
    CRAFTING_DATA = 0x34
    CRAFTING_EVENT = 0x35
    GUI_DATA_PICK_ITEM = 0x36
    ADVENTURE_SETTINGS = 0x37
    
    # 区块
    LEVEL_CHUNK = 0x3A
    
    # 游戏状态
    SET_DIFFICULTY = 0x3C
    CHANGE_DIMENSION = 0x3D
    SET_PLAYER_GAME_TYPE = 0x3E
    PLAYER_LIST = 0x3F
    
    # 事件
    EVENT = 0x41
    SPAWN_EXPERIENCE_ORB = 0x42
    
    # 地图
    MAP_INFO_REQUEST = 0x44
    REQUEST_CHUNK_RADIUS = 0x45
    CHUNK_RADIUS_UPDATED = 0x46
    
    # 游戏状态
    GAME_RULES_CHANGED = 0x48
    CAMERA = 0x49
    BOSS_EVENT = 0x4A
    SHOW_CREDITS = 0x4B
    
    # 命令
    AVAILABLE_COMMANDS = 0x4C
    COMMAND_REQUEST = 0x4D
    COMMAND_BLOCK_UPDATE = 0x4E
    
    # 交易
    UPDATE_TRADE = 0x50
    UPDATE_EQUIPMENT = 0x51
    
    # 资源包
    RESOURCE_PACK_DATA_INFO = 0x52
    RESOURCE_PACK_CHUNK_DATA = 0x53
    RESOURCE_PACK_CHUNK_REQUEST = 0x54
    
    # 玩家
    TRANSFER = 0x55
    PLAY_SOUND = 0x56
    STOP_SOUND = 0x57
    SET_TITLE = 0x58
    ADD_BEHAVIOR_TREE = 0x59
    STRUCTURE_BLOCK_UPDATE = 0x5A
    SHOW_STORE_OFFER = 0x5B
    PURCHASE_RECEIPT = 0x5C
    
    # 皮肤
    PLAYER_SKIN = 0x5D
    
    # 世界
    SUB_CLIENT_LOGIN = 0x5E
    
    # 初始化
    INITIATE_WEB_SOCKET_CONNECTION = 0x5F
    SET_LAST_HURT_BY = 0x60
    BOOK_EDIT = 0x61
    NPC_REQUEST = 0x62
    
    # 多人
    MODAL_FORM_REQUEST = 0x64
    MODAL_FORM_RESPONSE = 0x65
    SERVER_SETTINGS_REQUEST = 0x66
    SERVER_SETTINGS_RESPONSE = 0x67
    
    # 显示
    SHOW_PROFILE = 0x68
    SET_DEFAULT_GAME_TYPE = 0x69
    
    # 网络
    NETWORK_LATENCY = 0x9A


class VarInt:
    """变长整数编码"""
    
    @staticmethod
    def encode(value: int) -> bytes:
        """编码整数为VarInt"""
        result = bytearray()
        while True:
            byte = value & 0x7F
            value >>= 7
            if value != 0:
                byte |= 0x80
            result.append(byte)
            if value == 0:
                break
        return bytes(result)
    
    @staticmethod
    def decode(data: bytes, offset: int = 0) -> Tuple[int, int]:
        """解码VarInt，返回(值, 新偏移量)"""
        value = 0
        shift = 0
        while True:
            if offset >= len(data):
                raise ValueError("VarInt解码失败: 数据不足")
            
            byte = data[offset]
            value |= (byte & 0x7F) << shift
            offset += 1
            
            if (byte & 0x80) == 0:
                break
            
            shift += 7
            if shift >= 35:  # 防止溢出
                raise ValueError("VarInt解码失败: 值过大")
        
        return value, offset
    
    @staticmethod
    def encode_zigzag(value: int) -> bytes:
        """使用ZigZag编码有符号整数"""
        return VarInt.encode((value << 1) ^ (value >> 31))
    
    @staticmethod
    def decode_zigzag(data: bytes, offset: int = 0) -> Tuple[int, int]:
        """解码ZigZag编码的整数"""
        value, offset = VarInt.decode(data, offset)
        return (value >> 1) ^ -(value & 1), offset


class MCDataTypes:
    """Minecraft数据类型"""
    
    @staticmethod
    def write_string(stream: BinaryIO, value: str):
        """写入字符串"""
        encoded = value.encode('utf-8')
        stream.write(VarInt.encode(len(encoded)))
        stream.write(encoded)
    
    @staticmethod
    def read_string(stream: BinaryIO) -> str:
        """读取字符串"""
        length_data = stream.read(1)
        while length_data[-1] & 0x80:
            length_data += stream.read(1)
        
        length, _ = VarInt.decode(length_data)
        return stream.read(length).decode('utf-8')
    
    @staticmethod
    def write_int(stream: BinaryIO, value: int):
        """写入32位有符号整数"""
        stream.write(struct.pack('>i', value))
    
    @staticmethod
    def read_int(stream: BinaryIO) -> int:
        """读取32位有符号整数"""
        return struct.unpack('>i', stream.read(4))[0]
    
    @staticmethod
    def write_uint(stream: BinaryIO, value: int):
        """写入32位无符号整数"""
        stream.write(struct.pack('>I', value))
    
    @staticmethod
    def read_uint(stream: BinaryIO) -> int:
        """读取32位无符号整数"""
        return struct.unpack('>I', stream.read(4))[0]
    
    @staticmethod
    def write_long(stream: BinaryIO, value: int):
        """写入64位有符号整数"""
        stream.write(struct.pack('>q', value))
    
    @staticmethod
    def read_long(stream: BinaryIO) -> int:
        """读取64位有符号整数"""
        return struct.unpack('>q', stream.read(8))[0]
    
    @staticmethod
    def write_float(stream: BinaryIO, value: float):
        """写入32位浮点数"""
        stream.write(struct.pack('>f', value))
    
    @staticmethod
    def read_float(stream: BinaryIO) -> float:
        """读取32位浮点数"""
        return struct.unpack('>f', stream.read(4))[0]
    
    @staticmethod
    def write_double(stream: BinaryIO, value: float):
        """写入64位浮点数"""
        stream.write(struct.pack('>d', value))
    
    @staticmethod
    def read_double(stream: BinaryIO) -> float:
        """读取64位浮点数"""
        return struct.unpack('>d', stream.read(8))[0]
    
    @staticmethod
    def write_bool(stream: BinaryIO, value: bool):
        """写入布尔值"""
        stream.write(b'\x01' if value else b'\x00')
    
    @staticmethod
    def read_bool(stream: BinaryIO) -> bool:
        """读取布尔值"""
        return stream.read(1) != b'\x00'
    
    @staticmethod
    def write_byte(stream: BinaryIO, value: int):
        """写入字节"""
        stream.write(struct.pack('b', value))
    
    @staticmethod
    def read_byte(stream: BinaryIO) -> int:
        """读取字节"""
        return struct.unpack('b', stream.read(1))[0]
    
    @staticmethod
    def write_ubyte(stream: BinaryIO, value: int):
        """写入无符号字节"""
        stream.write(struct.pack('B', value))
    
    @staticmethod
    def read_ubyte(stream: BinaryIO) -> int:
        """读取无符号字节"""
        return struct.unpack('B', stream.read(1))[0]
    
    @staticmethod
    def write_short(stream: BinaryIO, value: int):
        """写入16位有符号整数"""
        stream.write(struct.pack('>h', value))
    
    @staticmethod
    def read_short(stream: BinaryIO) -> int:
        """读取16位有符号整数"""
        return struct.unpack('>h', stream.read(2))[0]
    
    @staticmethod
    def write_ushort(stream: BinaryIO, value: int):
        """写入16位无符号整数"""
        stream.write(struct.pack('>H', value))
    
    @staticmethod
    def read_ushort(stream: BinaryIO) -> int:
        """读取16位无符号整数"""
        return struct.unpack('>H', stream.read(2))[0]


@dataclass
class MCPacket:
    """Minecraft数据包基类"""
    packet_id: int
    data: bytes = b''
    
    def to_bytes(self) -> bytes:
        """转换为字节"""
        return VarInt.encode(self.packet_id) + self.data
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'MCPacket':
        """从字节解析"""
        packet_id, offset = VarInt.decode(data)
        return cls(packet_id=packet_id, data=data[offset:])
    
    def encode(self) -> bytes:
        """编码（子类可重写）"""
        return self.to_bytes()
    
    def decode(self):
        """解码（子类可重写）"""
        pass


@dataclass
class TextPacket(MCPacket):
    """聊天消息数据包 (0x09)"""
    type: int = 0  # 0=raw, 1=chat, 2=translation, 3=popup, 4=jukebox_popup, 5=tip, 6=system, 7=whisper, 8=announcement
    needs_translation: bool = False
    source_name: str = ""
    message: str = ""
    parameters: List[str] = field(default_factory=list)
    xbox_user_id: str = ""
    platform_chat_id: str = ""
    
    def __post_init__(self):
        self.packet_id = PacketID.TEXT
    
    def encode(self) -> bytes:
        """编码聊天消息"""
        stream = BytesIO()
        MCDataTypes.write_byte(stream, self.type)
        MCDataTypes.write_bool(stream, self.needs_translation)
        MCDataTypes.write_string(stream, self.source_name)
        MCDataTypes.write_string(stream, self.message)
        
        # 参数列表
        MCDataTypes.write_varint(stream, len(self.parameters))
        for param in self.parameters:
            MCDataTypes.write_string(stream, param)
        
        MCDataTypes.write_string(stream, self.xbox_user_id)
        MCDataTypes.write_string(stream, self.platform_chat_id)
        
        self.data = stream.getvalue()
        return self.to_bytes()
    
    @classmethod
    def decode(cls, data: bytes) -> 'TextPacket':
        """解码聊天消息"""
        stream = BytesIO(data)
        packet = cls()
        packet.type = MCDataTypes.read_byte(stream)
        packet.needs_translation = MCDataTypes.read_bool(stream)
        packet.source_name = MCDataTypes.read_string(stream)
        packet.message = MCDataTypes.read_string(stream)
        
        # 参数列表
        param_count = MCDataTypes.read_varint(stream)
        packet.parameters = []
        for _ in range(param_count):
            packet.parameters.append(MCDataTypes.read_string(stream))
        
        packet.xbox_user_id = MCDataTypes.read_string(stream)
        packet.platform_chat_id = MCDataTypes.read_string(stream)
        
        return packet


@dataclass
class MovePlayerPacket(MCPacket):
    """玩家移动数据包 (0x13)"""
    entity_id: int = 0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0
    head_yaw: float = 0.0
    mode: int = 0  # 0=normal, 1=reset, 2=teleport, 3=rotation
    on_ground: bool = True
    riding_eid: int = 0
    
    def __post_init__(self):
        self.packet_id = PacketID.MOVE_PLAYER
    
    def encode(self) -> bytes:
        """编码玩家移动"""
        stream = BytesIO()
        MCDataTypes.write_varlong(stream, self.entity_id)
        MCDataTypes.write_float(stream, self.x)
        MCDataTypes.write_float(stream, self.y)
        MCDataTypes.write_float(stream, self.z)
        MCDataTypes.write_float(stream, self.pitch)
        MCDataTypes.write_float(stream, self.yaw)
        MCDataTypes.write_float(stream, self.head_yaw)
        MCDataTypes.write_byte(stream, self.mode)
        MCDataTypes.write_bool(stream, self.on_ground)
        MCDataTypes.write_varlong(stream, self.riding_eid)
        
        self.data = stream.getvalue()
        return self.to_bytes()


@dataclass
class UpdateBlockPacket(MCPacket):
    """方块更新数据包 (0x15)"""
    x: int = 0
    y: int = 0
    z: int = 0
    block_id: int = 0
    block_data: int = 0
    flags: int = 0  # 0x01=neighbors, 0x02=network, 0x04=lighting, 0x08=entity
    
    def __post_init__(self):
        self.packet_id = PacketID.UPDATE_BLOCK
    
    def encode(self) -> bytes:
        """编码方块更新"""
        stream = BytesIO()
        
        # 坐标使用VarInt
        stream.write(VarInt.encode(self.x))
        stream.write(VarInt.encode(self.y))
        stream.write(VarInt.encode(self.z))
        
        # 方块ID和数据
        stream.write(VarInt.encode(self.block_id))
        MCDataTypes.write_ushort(stream, (self.block_data << 8) | self.flags)
        
        self.data = stream.getvalue()
        return self.to_bytes()


class MCPacketFactory:
    """Minecraft数据包工厂"""
    
    PACKET_CLASSES = {
        PacketID.TEXT: TextPacket,
        PacketID.MOVE_PLAYER: MovePlayerPacket,
        PacketID.UPDATE_BLOCK: UpdateBlockPacket,
    }
    
    @classmethod
    def create_packet(cls, packet_id: int, data: bytes = b'') -> MCPacket:
        """创建数据包实例"""
        packet_class = cls.PACKET_CLASSES.get(packet_id, MCPacket)
        return packet_class(packet_id=packet_id, data=data)
    
    @classmethod
    def parse_packet(cls, data: bytes) -> MCPacket:
        """解析数据包"""
        packet_id, offset = VarInt.decode(data)
        packet_data = data[offset:]
        
        packet_class = cls.PACKET_CLASSES.get(packet_id, MCPacket)
        
        if packet_class != MCPacket and hasattr(packet_class, 'decode'):
            return packet_class.decode(packet_data)
        else:
            return packet_class(packet_id=packet_id, data=packet_data)


# 便捷函数
def encode_varint(value: int) -> bytes:
    """编码VarInt"""
    return VarInt.encode(value)


def decode_varint(data: bytes, offset: int = 0) -> Tuple[int, int]:
    """解码VarInt"""
    return VarInt.decode(data, offset)


__all__ = [
    'PacketID',
    'VarInt',
    'MCDataTypes',
    'MCPacket',
    'TextPacket',
    'MovePlayerPacket',
    'UpdateBlockPacket',
    'MCPacketFactory',
    'encode_varint',
    'decode_varint',
]
