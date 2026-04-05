"""
RakNet 协议适配层

基于 RakNet UDP 协议实现
"""

import struct
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import IntEnum


class RakNetMessageID(IntEnum):
    """RakNet 消息 ID"""
    ID_CONNECTED_PING = 0x00
    ID_UNCONNECTED_PING = 0x01
    ID_CONNECTED_PONG = 0x03
    ID_CONNECTION_REQUEST = 0x09
    ID_CONNECTION_REQUEST_ACCEPTED = 0x10
    ID_DISCONNECTION_NOTIFICATION = 0x15
    ID_CONNECTION_LOST = 0x16
    ID_USER_PACKET_ENUM = 0x86


@dataclass
class RakNetPacket:
    """RakNet 数据包"""
    message_id: int
    data: bytes
    reliability: int = 2  # RELIABLE
    ordering_channel: int = 0
    
    def encode(self) -> bytes:
        """编码数据包"""
        # TODO: 实现 RakNet 编码
        return bytes([self.message_id]) + self.data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['RakNetPacket']:
        """解码数据包"""
        if len(data) < 1:
            return None
        return cls(
            message_id=data[0],
            data=data[1:]
        )


class RakNetCodec:
    """RakNet 编解码器"""
    
    def __init__(self):
        self.packets: List[RakNetPacket] = []
    
    def encode_packet(self, packet: RakNetPacket) -> bytes:
        """编码数据包"""
        return packet.encode()
    
    def decode_packet(self, data: bytes) -> Optional[RakNetPacket]:
        """解码数据包"""
        return RakNetPacket.decode(data)
