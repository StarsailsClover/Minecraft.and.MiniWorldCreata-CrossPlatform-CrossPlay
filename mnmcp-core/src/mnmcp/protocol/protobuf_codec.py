"""
Protobuf 编解码器

基于逆向分析提取的原始 .proto 定义实现
支持迷你世界国服协议消息
"""

import struct
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import IntEnum

logger = logging.getLogger(__name__)


class WireType(IntEnum):
    """Protobuf Wire Type"""
    VARINT = 0
    FIXED64 = 1
    LENGTH_DELIMITED = 2
    START_GROUP = 3
    END_GROUP = 4
    FIXED32 = 5


def zigzag_encode(n: int) -> int:
    """ZigZag 编码 - 用于有符号整数"""
    return (n << 1) ^ (n >> 63)


def zigzag_decode(n: int) -> int:
    """ZigZag 解码"""
    return (n >> 1) ^ -(n & 1)


def encode_varint(value: int) -> bytes:
    """编码 VarInt"""
    result = []
    while value > 127:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value)
    return bytes(result)


def decode_varint(data: bytes, offset: int = 0) -> tuple:
    """解码 VarInt，返回 (value, new_offset)"""
    value = 0
    shift = 0
    while True:
        if offset >= len(data):
            raise ValueError("Incomplete varint")
        byte = data[offset]
        value |= (byte & 0x7F) << shift
        offset += 1
        if not (byte & 0x80):
            break
        shift += 7
        if shift >= 64:
            raise ValueError("Varint too long")
    return value, offset


def make_tag(field_number: int, wire_type: int) -> int:
    """生成字段标签"""
    return (field_number << 3) | wire_type


def parse_tag(tag: int) -> tuple:
    """解析字段标签，返回 (field_number, wire_type)"""
    return (tag >> 3), (tag & 0x07)


@dataclass
class PB_Vector3:
    """
    3D 向量 (proto_common.proto)
    
    使用 ZigZag 编码的有符号整数
    """
    X: int = 0
    Y: int = 0
    Z: int = 0
    
    @classmethod
    def from_mc_coords(cls, x: float, y: float, z: float) -> 'PB_Vector3':
        """从 Minecraft 坐标转换"""
        # 迷你世界使用整数坐标，需要缩放
        return cls(
            X=int(x * 100),  # 缩放因子
            Y=int(y * 100),
            Z=int(z * 100)
        )
    
    def to_mc_coords(self) -> tuple:
        """转换为 Minecraft 坐标"""
        return (self.X / 100, self.Y / 100, self.Z / 100)
    
    def encode(self) -> bytes:
        """编码为 protobuf 格式"""
        data = b''
        # field 1: X (sint32, ZigZag 编码)
        data += bytes([make_tag(1, WireType.VARINT)]) + encode_varint(zigzag_encode(self.X))
        # field 2: Y (sint32, ZigZag 编码)
        data += bytes([make_tag(2, WireType.VARINT)]) + encode_varint(zigzag_encode(self.Y))
        # field 3: Z (sint32, ZigZag 编码)
        data += bytes([make_tag(3, WireType.VARINT)]) + encode_varint(zigzag_encode(self.Z))
        return data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['PB_Vector3']:
        """从 protobuf 格式解码"""
        try:
            obj = cls()
            offset = 0
            
            while offset < len(data):
                tag, offset = decode_varint(data, offset)
                field_num, wire_type = parse_tag(tag)
                
                if wire_type == WireType.VARINT:
                    value, offset = decode_varint(data, offset)
                    decoded_value = zigzag_decode(value)
                    
                    if field_num == 1:
                        obj.X = decoded_value
                    elif field_num == 2:
                        obj.Y = decoded_value
                    elif field_num == 3:
                        obj.Z = decoded_value
                else:
                    # 跳过未知字段
                    if wire_type == WireType.FIXED64:
                        offset += 8
                    elif wire_type == WireType.FIXED32:
                        offset += 4
                    elif wire_type == WireType.LENGTH_DELIMITED:
                        length, offset = decode_varint(data, offset)
                        offset += length
                    else:
                        break
            
            return obj
        except Exception as e:
            logger.error(f"PB_Vector3 decode error: {e}")
            return None


@dataclass
class PB_HeartBeatCH:
    """
    心跳包 (proto_ch.proto)
    
    用于 UDP 和 WebSocket 链路的高频保活及时间对齐
    """
    BeatCode: int = 0
    server_time: int = 0
    client_time: int = 0
    
    def encode(self) -> bytes:
        """编码为 protobuf 格式"""
        data = b''
        # field 1: BeatCode (uint64)
        data += bytes([make_tag(1, WireType.VARINT)]) + encode_varint(self.BeatCode)
        # field 2: server_time (uint64)
        data += bytes([make_tag(2, WireType.VARINT)]) + encode_varint(self.server_time)
        # field 3: client_time (uint64)
        data += bytes([make_tag(3, WireType.VARINT)]) + encode_varint(self.client_time)
        return data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['PB_HeartBeatCH']:
        """从 protobuf 格式解码"""
        try:
            obj = cls()
            offset = 0
            
            while offset < len(data):
                tag, offset = decode_varint(data, offset)
                field_num, wire_type = parse_tag(tag)
                
                if wire_type == WireType.VARINT:
                    value, offset = decode_varint(data, offset)
                    
                    if field_num == 1:
                        obj.BeatCode = value
                    elif field_num == 2:
                        obj.server_time = value
                    elif field_num == 3:
                        obj.client_time = value
                else:
                    # 跳过未知字段
                    if wire_type == WireType.FIXED64:
                        offset += 8
                    elif wire_type == WireType.FIXED32:
                        offset += 4
                    elif wire_type == WireType.LENGTH_DELIMITED:
                        length, offset = decode_varint(data, offset)
                        offset += length
                    else:
                        break
            
            return obj
        except Exception as e:
            logger.error(f"PB_HeartBeatCH decode error: {e}")
            return None


@dataclass
class PB_RoomInfo:
    """
    房间信息
    """
    room_id: str = ""
    room_name: str = ""
    host_uin: int = 0
    max_players: int = 40
    current_players: int = 0
    game_mode: str = "survival"
    
    def encode(self) -> bytes:
        """编码为 protobuf 格式"""
        data = b''
        # field 1: room_id (string)
        room_id_bytes = self.room_id.encode('utf-8')
        data += bytes([make_tag(1, WireType.LENGTH_DELIMITED)])
        data += encode_varint(len(room_id_bytes)) + room_id_bytes
        
        # field 2: room_name (string)
        room_name_bytes = self.room_name.encode('utf-8')
        data += bytes([make_tag(2, WireType.LENGTH_DELIMITED)])
        data += encode_varint(len(room_name_bytes)) + room_name_bytes
        
        # field 3: host_uin (uint64)
        data += bytes([make_tag(3, WireType.VARINT)]) + encode_varint(self.host_uin)
        
        # field 4: max_players (uint32)
        data += bytes([make_tag(4, WireType.VARINT)]) + encode_varint(self.max_players)
        
        # field 5: current_players (uint32)
        data += bytes([make_tag(5, WireType.VARINT)]) + encode_varint(self.current_players)
        
        # field 6: game_mode (string)
        game_mode_bytes = self.game_mode.encode('utf-8')
        data += bytes([make_tag(6, WireType.LENGTH_DELIMITED)])
        data += encode_varint(len(game_mode_bytes)) + game_mode_bytes
        
        return data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['PB_RoomInfo']:
        """从 protobuf 格式解码"""
        try:
            obj = cls()
            offset = 0
            
            while offset < len(data):
                tag, offset = decode_varint(data, offset)
                field_num, wire_type = parse_tag(tag)
                
                if wire_type == WireType.VARINT:
                    value, offset = decode_varint(data, offset)
                    if field_num == 3:
                        obj.host_uin = value
                    elif field_num == 4:
                        obj.max_players = value
                    elif field_num == 5:
                        obj.current_players = value
                        
                elif wire_type == WireType.LENGTH_DELIMITED:
                    length, offset = decode_varint(data, offset)
                    value = data[offset:offset+length].decode('utf-8')
                    offset += length
                    
                    if field_num == 1:
                        obj.room_id = value
                    elif field_num == 2:
                        obj.room_name = value
                    elif field_num == 6:
                        obj.game_mode = value
                else:
                    # 跳过未知字段
                    if wire_type == WireType.FIXED64:
                        offset += 8
                    elif wire_type == WireType.FIXED32:
                        offset += 4
                    else:
                        break
            
            return obj
        except Exception as e:
            logger.error(f"PB_RoomInfo decode error: {e}")
            return None


@dataclass
class PB_ActorOperationCH:
    """
    玩家操作 (proto_ch.proto)
    """
    actor_id: int = 0
    operation_type: int = 0  # 操作类型
    position: Optional[PB_Vector3] = None
    rotation: Optional[PB_Vector3] = None
    
    def encode(self) -> bytes:
        """编码为 protobuf 格式"""
        data = b''
        # field 1: actor_id (uint64)
        data += bytes([make_tag(1, WireType.VARINT)]) + encode_varint(self.actor_id)
        
        # field 2: operation_type (uint32)
        data += bytes([make_tag(2, WireType.VARINT)]) + encode_varint(self.operation_type)
        
        # field 3: position (PB_Vector3)
        if self.position:
            pos_data = self.position.encode()
            data += bytes([make_tag(3, WireType.LENGTH_DELIMITED)])
            data += encode_varint(len(pos_data)) + pos_data
        
        # field 4: rotation (PB_Vector3)
        if self.rotation:
            rot_data = self.rotation.encode()
            data += bytes([make_tag(4, WireType.LENGTH_DELIMITED)])
            data += encode_varint(len(rot_data)) + rot_data
        
        return data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['PB_ActorOperationCH']:
        """从 protobuf 格式解码"""
        try:
            obj = cls()
            offset = 0
            
            while offset < len(data):
                tag, offset = decode_varint(data, offset)
                field_num, wire_type = parse_tag(tag)
                
                if wire_type == WireType.VARINT:
                    value, offset = decode_varint(data, offset)
                    if field_num == 1:
                        obj.actor_id = value
                    elif field_num == 2:
                        obj.operation_type = value
                        
                elif wire_type == WireType.LENGTH_DELIMITED:
                    length, offset = decode_varint(data, offset)
                    sub_data = data[offset:offset+length]
                    offset += length
                    
                    if field_num == 3:
                        obj.position = PB_Vector3.decode(sub_data)
                    elif field_num == 4:
                        obj.rotation = PB_Vector3.decode(sub_data)
                else:
                    # 跳过未知字段
                    if wire_type == WireType.FIXED64:
                        offset += 8
                    elif wire_type == WireType.FIXED32:
                        offset += 4
                    else:
                        break
            
            return obj
        except Exception as e:
            logger.error(f"PB_ActorOperationCH decode error: {e}")
            return None


class ProtobufCodec:
    """Protobuf 便捷编解码器"""
    
    @staticmethod
    def encode_vector3(x: int, y: int, z: int) -> bytes:
        """编码 3D 向量"""
        return PB_Vector3(X=x, Y=y, Z=z).encode()
    
    @staticmethod
    def decode_vector3(data: bytes) -> Optional[PB_Vector3]:
        """解码 3D 向量"""
        return PB_Vector3.decode(data)
    
    @staticmethod
    def encode_heartbeat(beat_code: int, server_time: int, client_time: int) -> bytes:
        """编码心跳包"""
        return PB_HeartBeatCH(
            BeatCode=beat_code,
            server_time=server_time,
            client_time=client_time
        ).encode()
    
    @staticmethod
    def decode_heartbeat(data: bytes) -> Optional[PB_HeartBeatCH]:
        """解码心跳包"""
        return PB_HeartBeatCH.decode(data)


# 便捷函数
def encode_pb_vector3(x: int, y: int, z: int) -> bytes:
    """便捷编码 3D 向量"""
    return PB_Vector3(X=x, Y=y, Z=z).encode()


def decode_pb_vector3(data: bytes) -> Optional[PB_Vector3]:
    """便捷解码 3D 向量"""
    return PB_Vector3.decode(data)


def encode_pb_heartbeat(beat_code: int, server_time: int, client_time: int) -> bytes:
    """便捷编码心跳包"""
    return PB_HeartBeatCH(
        BeatCode=beat_code,
        server_time=server_time,
        client_time=client_time
    ).encode()


def decode_pb_heartbeat(data: bytes) -> Optional[PB_HeartBeatCH]:
    """便捷解码心跳包"""
    return PB_HeartBeatCH.decode(data)
