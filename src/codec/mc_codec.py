#!/usr/bin/env python3
"""
Minecraft 协议编解码器
处理 Minecraft 1.20.6 协议的数据包编码和解码
"""

import struct
import logging
from typing import Optional, Tuple, List
from dataclasses import dataclass
from io import BytesIO

logger = logging.getLogger(__name__)


@dataclass
class MCPacket:
    """Minecraft 数据包"""
    packet_id: int
    data: bytes
    
    def encode(self) -> bytes:
        """编码数据包"""
        # 数据包格式: [长度(VarInt)] [包ID(VarInt)] [数据]
        packet_data = encode_varint(self.packet_id) + self.data
        length = encode_varint(len(packet_data))
        return length + packet_data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['MCPacket']:
        """解码数据包"""
        try:
            stream = BytesIO(data)
            length = decode_varint(stream)
            packet_id = decode_varint(stream)
            packet_data = stream.read()
            return cls(packet_id=packet_id, data=packet_data)
        except Exception as e:
            logger.error(f"解码Minecraft数据包失败: {e}")
            return None


def encode_varint(value: int) -> bytes:
    """
    编码 VarInt
    Minecraft协议使用的可变长度整数编码
    """
    result = []
    while True:
        byte = value & 0x7F
        value >>= 7
        if value != 0:
            byte |= 0x80
        result.append(byte)
        if value == 0:
            break
    return bytes(result)


def decode_varint(stream) -> int:
    """
    解码 VarInt
    """
    result = 0
    shift = 0
    while True:
        byte = stream.read(1)
        if not byte:
            raise ValueError("Unexpected end of stream")
        byte = byte[0]
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            break
        shift += 7
        if shift >= 35:
            raise ValueError("VarInt too large")
    return result


def encode_string(value: str) -> bytes:
    """编码字符串（UTF-8 + 长度前缀）"""
    encoded = value.encode('utf-8')
    return encode_varint(len(encoded)) + encoded


def decode_string(stream) -> str:
    """解码字符串"""
    length = decode_varint(stream)
    data = stream.read(length)
    return data.decode('utf-8')


def encode_short(value: int) -> bytes:
    """编码短整数（2字节，大端序）"""
    return struct.pack('>H', value)


def decode_short(stream) -> int:
    """解码短整数"""
    data = stream.read(2)
    return struct.unpack('>H', data)[0]


def encode_long(value: int) -> bytes:
    """编码长整数（8字节，大端序）"""
    return struct.pack('>q', value)


def decode_long(stream) -> int:
    """解码长整数"""
    data = stream.read(8)
    return struct.unpack('>q', data)[0]


class MinecraftCodec:
    """Minecraft 协议编解码器"""
    
    # Minecraft 1.20.6 协议版本号
    PROTOCOL_VERSION = 766
    
    # 数据包类型（部分常用包）
    PACKET_HANDSHAKE = 0x00
    PACKET_STATUS_REQUEST = 0x00
    PACKET_STATUS_RESPONSE = 0x00
    PACKET_LOGIN_START = 0x00
    PACKET_LOGIN_SUCCESS = 0x02
    PACKET_LOGIN_DISCONNECT = 0x00
    PACKET_KEEP_ALIVE = 0x24
    PACKET_CHAT_MESSAGE = 0x05
    PACKET_CHUNK_DATA = 0x25
    PACKET_PLAYER_POSITION = 0x1A
    PACKET_BLOCK_CHANGE = 0x09
    
    def __init__(self):
        self.compression_threshold = -1  # 压缩阈值，-1表示不压缩
        
    def encode_packet(self, packet_id: int, data: bytes) -> bytes:
        """
        编码数据包
        
        Args:
            packet_id: 数据包ID
            data: 包数据
            
        Returns:
            编码后的字节数据
        """
        return MCPacket(packet_id=packet_id, data=data).encode()
    
    def decode_packet(self, data: bytes) -> Optional[MCPacket]:
        """
        解码数据包
        
        Args:
            data: 原始字节数据
            
        Returns:
            MCPacket对象或None
        """
        return MCPacket.decode(data)
    
    def read_packet(self, stream) -> Optional[MCPacket]:
        """
        从流中读取一个完整的数据包
        
        Args:
            stream: 字节流对象
            
        Returns:
            MCPacket对象或None
        """
        try:
            # 读取长度
            length = decode_varint(stream)
            
            # 读取数据
            data = stream.read(length)
            if len(data) < length:
                logger.warning(f"数据包不完整: 期望{length}字节，实际{len(data)}字节")
                return None
            
            # 解码数据包
            return self.decode_packet(data)
            
        except Exception as e:
            logger.error(f"读取数据包失败: {e}")
            return None
    
    def create_handshake(self, protocol_version: int, server_address: str, 
                        server_port: int, next_state: int) -> bytes:
        """
        创建握手包
        
        Args:
            protocol_version: 协议版本
            server_address: 服务器地址
            server_port: 服务器端口
            next_state: 下一个状态（1=status, 2=login）
            
        Returns:
            编码后的握手包
        """
        data = BytesIO()
        data.write(encode_varint(protocol_version))
        data.write(encode_string(server_address))
        data.write(encode_short(server_port))
        data.write(encode_varint(next_state))
        
        return self.encode_packet(self.PACKET_HANDSHAKE, data.getvalue())
    
    def create_login_start(self, username: str, uuid_str: str = None) -> bytes:
        """
        创建登录开始包
        
        Args:
            username: 用户名
            uuid_str: UUID字符串（可选）
            
        Returns:
            编码后的登录包
        """
        data = BytesIO()
        data.write(encode_string(username))
        
        if uuid_str:
            # 写入UUID
            import uuid
            uuid_bytes = uuid.UUID(uuid_str).bytes
            data.write(b'\x01')  # 有UUID
            data.write(uuid_bytes)
        else:
            data.write(b'\x00')  # 无UUID
        
        return self.encode_packet(self.PACKET_LOGIN_START, data.getvalue())
    
    def create_keep_alive(self, keep_alive_id: int) -> bytes:
        """
        创建心跳包
        
        Args:
            keep_alive_id: 心跳ID
            
        Returns:
            编码后的心跳包
        """
        data = encode_long(keep_alive_id)
        return self.encode_packet(self.PACKET_KEEP_ALIVE, data)
    
    def create_chat_message(self, message: str) -> bytes:
        """
        创建聊天消息包
        
        Args:
            message: 聊天消息
            
        Returns:
            编码后的聊天包
        """
        data = encode_string(message)
        return self.encode_packet(self.PACKET_CHAT_MESSAGE, data)
