"""
迷你世界业务协议 (MNW Protocol)

基于逆向分析实现，用于与迷你世界国服服务器通信

Copyright (c) 2026 MnMCP Contributors
SPDX-License-Identifier: MIT
"""

import struct
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Callable
from enum import IntEnum

from .protobuf_codec import (
    PB_Vector3, PB_HeartBeatCH, PB_RoomInfo, PB_ActorOperationCH,
    encode_pb_vector3, decode_pb_vector3,
    encode_pb_heartbeat, decode_pb_heartbeat
)


class MNWProtoID(IntEnum):
    """
    迷你世界协议码
    
    基于抓包分析和逆向工程提取的消息类型
    """
    # 登录相关
    PROTO_2003 = 0x7D3
    PROTO_2004 = 0x7D4
    
    # 房间相关
    PROTO_2005 = 0x7D5
    PROTO_2006 = 0x7D6
    PROTO_2007 = 0x7D7
    PROTO_2008 = 0x7D8
    PROTO_2009 = 0x7D9
    PROTO_2010 = 0x7DA
    PROTO_2011 = 0x7DB
    PROTO_2012 = 0x7DC
    PROTO_2013 = 0x7DD
    PROTO_2014 = 0x7DE
    PROTO_2015 = 0x7DF
    
    # 玩家相关
    PROTO_2016 = 0x7E0  # PLAYER_MOVE
    PROTO_2017 = 0x7E1
    PROTO_2018 = 0x7E2
    PROTO_2019 = 0x7E3
    PROTO_2020 = 0x7E4  # Vector3
    PROTO_2021 = 0x7E5
    PROTO_2022 = 0x7E6  # ActorOperation
    PROTO_2023 = 0x7E7
    PROTO_2024 = 0x7E8
    PROTO_2025 = 0x7E9
    PROTO_2026 = 0x7EA  # CHAT_MESSAGE
    PROTO_2027 = 0x7EB
    PROTO_2028 = 0x7EC
    PROTO_2029 = 0x7ED  # HEARTBEAT
    PROTO_2030 = 0x7EE
    PROTO_2031 = 0x7EF
    PROTO_2032 = 0x7F0  # RoomInfo
    PROTO_2033 = 0x7F1
    PROTO_2034 = 0x7F2  # 角色进入世界
    PROTO_2035 = 0x7F3


@dataclass(frozen=True)
class MNWPacket:
    """
    迷你世界数据包
    
    PB_PACKDATA_CLIENT 格式:
    - proto_id (2 bytes, big-endian)
    - uin (8 bytes, big-endian)
    - data_len (4 bytes, big-endian)
    - data (variable)
    
    Attributes:
        proto_id: 协议类型ID
        uin: 用户唯一标识号
        data: 有效载荷数据
        target_uin: 目标用户UIN (可选，用于私信)
    """
    proto_id: int
    uin: int
    data: bytes
    target_uin: Optional[int] = None
    
    def encode(self) -> bytes:
        """
        编码数据包
        
        Returns:
            编码后的字节流
        """
        header = struct.pack('>HQ', self.proto_id, self.uin)
        data_len = len(self.data)
        return header + struct.pack('>I', data_len) + self.data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['MNWPacket']:
        """
        解码数据包
        
        Args:
            data: 原始字节数据
            
        Returns:
            解码后的 MNWPacket 实例，失败返回 None
        """
        if len(data) < 14:  # 2 + 8 + 4
            return None
        
        try:
            proto_id, uin = struct.unpack('>HQ', data[:10])
            data_len = struct.unpack('>I', data[10:14])[0]
            
            if len(data) < 14 + data_len:
                return None
            
            payload = data[14:14+data_len]
            
            return cls(
                proto_id=proto_id,
                uin=uin,
                data=payload
            )
        except struct.error:
            return None
    
    def parse_as_vector3(self) -> Optional[PB_Vector3]:
        """
        解析数据为 PB_Vector3
        
        Returns:
            PB_Vector3 实例，如果不是 Vector3 类型返回 None
        """
        if self.proto_id == MNWProtoID.PROTO_2020:
            return PB_Vector3.decode(self.data)
        return None
    
    def parse_as_heartbeat(self) -> Optional[PB_HeartBeatCH]:
        """
        解析数据为 PB_HeartBeatCH
        
        Returns:
            PB_HeartBeatCH 实例，如果不是心跳包返回 None
        """
        if self.proto_id == MNWProtoID.PROTO_2029:
            return PB_HeartBeatCH.decode(self.data)
        return None
    
    def parse_as_room_info(self) -> Optional[PB_RoomInfo]:
        """
        解析数据为 PB_RoomInfo
        
        Returns:
            PB_RoomInfo 实例，如果不是房间信息返回 None
        """
        if self.proto_id == MNWProtoID.PROTO_2032:
            return PB_RoomInfo.decode(self.data)
        return None
    
    def parse_as_actor_operation(self) -> Optional[PB_ActorOperationCH]:
        """
        解析数据为 PB_ActorOperationCH
        
        Returns:
            PB_ActorOperationCH 实例，如果不是玩家操作返回 None
        """
        if self.proto_id == MNWProtoID.PROTO_2022:
            return PB_ActorOperationCH.decode(self.data)
        return None
    
    def get_proto_name(self) -> str:
        """
        获取协议名称
        
        Returns:
            协议类型的可读名称
        """
        proto_names = {
            MNWProtoID.PROTO_2020: "PB_Vector3",
            MNWProtoID.PROTO_2029: "PB_HeartBeatCH",
            MNWProtoID.PROTO_2032: "PB_RoomInfo",
            MNWProtoID.PROTO_2022: "PB_ActorOperationCH",
            MNWProtoID.PROTO_2026: "PB_ChatMessage",
            MNWProtoID.PROTO_2016: "PB_PlayerMove",
            MNWProtoID.PROTO_2034: "PB_RoleEnterWorld",
        }
        return proto_names.get(self.proto_id, f"Unknown({hex(self.proto_id)})")


class MNWCodec:
    """
    迷你世界编解码器
    
    提供便捷的数据包创建和解析功能
    
    Example:
        >>> codec = MNWCodec()
        >>> packet = codec.create_vector3_packet(1234567890, 100, 64, -50)
        >>> encoded = packet.encode()
    """
    
    def __init__(self):
        self._proto_map: Dict[int, str] = {
            MNWProtoID.PROTO_2034: "PB_ROLE_ENTER_WORLD_CH",
            MNWProtoID.PROTO_2020: "PB_Vector3",
            MNWProtoID.PROTO_2029: "PB_HeartBeatCH",
            MNWProtoID.PROTO_2032: "PB_RoomInfo",
            MNWProtoID.PROTO_2022: "PB_ActorOperationCH",
            MNWProtoID.PROTO_2026: "PB_ChatMessage",
            MNWProtoID.PROTO_2016: "PB_PlayerMove",
        }
        self._handlers: Dict[int, Callable] = {}
        self._stats = {
            'encoded': 0,
            'decoded': 0,
            'errors': 0
        }
    
    def encode_packet(self, packet: MNWPacket) -> bytes:
        """
        编码数据包
        
        Args:
            packet: MNWPacket 实例
            
        Returns:
            编码后的字节流
        """
        self._stats['encoded'] += 1
        return packet.encode()
    
    def decode_packet(self, data: bytes) -> Optional[MNWPacket]:
        """
        解码数据包
        
        Args:
            data: 原始字节数据
            
        Returns:
            解码后的 MNWPacket 实例，失败返回 None
        """
        packet = MNWPacket.decode(data)
        if packet:
            self._stats['decoded'] += 1
        else:
            self._stats['errors'] += 1
        return packet
    
    def get_proto_name(self, proto_id: int) -> Optional[str]:
        """
        获取协议名称
        
        Args:
            proto_id: 协议类型ID
            
        Returns:
            协议名称，未知类型返回 None
        """
        return self._proto_map.get(proto_id)
    
    def register_handler(self, proto_id: int, handler: Callable):
        """
        注册协议处理器
        
        Args:
            proto_id: 协议类型ID
            handler: 处理函数
        """
        self._handlers[proto_id] = handler
    
    def handle_packet(self, packet: MNWPacket) -> Any:
        """
        处理数据包
        
        Args:
            packet: MNWPacket 实例
            
        Returns:
            处理结果
        """
        handler = self._handlers.get(packet.proto_id)
        if handler:
            return handler(packet)
        return None
    
    def create_vector3_packet(self, uin: int, x: int, y: int, z: int) -> MNWPacket:
        """
        创建 Vector3 数据包
        
        Args:
            uin: 用户UIN
            x: X坐标
            y: Y坐标
            z: Z坐标
            
        Returns:
            MNWPacket 实例
        """
        pb = PB_Vector3(X=x, Y=y, Z=z)
        return MNWPacket(
            proto_id=MNWProtoID.PROTO_2020,
            uin=uin,
            data=pb.encode()
        )
    
    def create_heartbeat_packet(self, uin: int, beat_code: int, 
                                server_time: int, client_time: int) -> MNWPacket:
        """
        创建心跳包
        
        Args:
            uin: 用户UIN
            beat_code: 心跳码
            server_time: 服务器时间
            client_time: 客户端时间
            
        Returns:
            MNWPacket 实例
        """
        pb = PB_HeartBeatCH(
            BeatCode=beat_code,
            server_time=server_time,
            client_time=client_time
        )
        return MNWPacket(
            proto_id=MNWProtoID.PROTO_2029,
            uin=uin,
            data=pb.encode()
        )
    
    def create_role_enter_world(self, uin: int, role_id: int, 
                                 position: PB_Vector3) -> MNWPacket:
        """
        创建角色进入世界数据包
        
        Args:
            uin: 用户UIN
            role_id: 角色ID
            position: 初始位置
            
        Returns:
            MNWPacket 实例
        """
        # 构建角色进入世界消息
        # 格式: role_id (8) + position (variable)
        data = struct.pack('>Q', role_id)
        data += position.encode()
        
        return MNWPacket(
            proto_id=MNWProtoID.PROTO_2034,
            uin=uin,
            data=data
        )
    
    def create_chat_message(self, uin: int, message: str, 
                           target_uin: Optional[int] = None) -> MNWPacket:
        """
        创建聊天消息数据包
        
        Args:
            uin: 发送者UIN
            message: 消息内容
            target_uin: 目标用户UIN (私信时使用)
            
        Returns:
            MNWPacket 实例
        """
        data = message.encode('utf-8')
        return MNWPacket(
            proto_id=MNWProtoID.PROTO_2026,
            uin=uin,
            data=data,
            target_uin=target_uin
        )
    
    def create_player_move(self, uin: int, x: float, y: float, z: float,
                          yaw: float = 0.0, pitch: float = 0.0) -> MNWPacket:
        """
        创建玩家移动数据包
        
        Args:
            uin: 用户UIN
            x: X坐标
            y: Y坐标
            z: Z坐标
            yaw: 偏航角
            pitch: 俯仰角
            
        Returns:
            MNWPacket 实例
        """
        # 格式: x (4) + y (4) + z (4) + yaw (4) + pitch (4)
        data = struct.pack('>fffff', x, y, z, yaw, pitch)
        
        return MNWPacket(
            proto_id=MNWProtoID.PROTO_2016,
            uin=uin,
            data=data
        )
    
    def get_stats(self) -> Dict[str, int]:
        """
        获取统计信息
        
        Returns:
            统计字典
        """
        return self._stats.copy()
    
    def reset_stats(self):
        """重置统计信息"""
        self._stats = {'encoded': 0, 'decoded': 0, 'errors': 0}


# 便捷函数
def encode_mnw_packet(proto_id: int, uin: int, data: bytes) -> bytes:
    """
    便捷编码函数
    
    Args:
        proto_id: 协议类型ID
        uin: 用户UIN
        data: 有效载荷
        
    Returns:
        编码后的字节流
    """
    packet = MNWPacket(proto_id=proto_id, uin=uin, data=data)
    return packet.encode()


def decode_mnw_packet(data: bytes) -> Optional[MNWPacket]:
    """
    便捷解码函数
    
    Args:
        data: 原始字节数据
        
    Returns:
        解码后的 MNWPacket 实例
    """
    return MNWPacket.decode(data)


# 版本信息
__version__ = "1.0.0"
__all__ = [
    'MNWProtoID',
    'MNWPacket',
    'MNWCodec',
    'encode_mnw_packet',
    'decode_mnw_packet'
]
