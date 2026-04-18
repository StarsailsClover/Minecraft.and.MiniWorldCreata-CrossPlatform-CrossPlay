"""
Protobuf 协议定义

基于逆向分析提取的原始 .proto 定义
"""

from dataclasses import dataclass
from typing import Optional, List
import struct


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
        """编码为 protobuf 格式 (简化)"""
        # 使用 ZigZag 编码
        def zigzag_encode(n: int) -> int:
            return (n << 1) ^ (n >> 31)
        
        data = b''
        # field 1: X
        data += b'\x08' + self._encode_varint(zigzag_encode(self.X))
        # field 2: Y
        data += b'\x10' + self._encode_varint(zigzag_encode(self.Y))
        # field 3: Z
        data += b'\x18' + self._encode_varint(zigzag_encode(self.Z))
        return data
    
    @classmethod
    def decode(cls, data: bytes) -> 'PB_Vector3':
        """从 protobuf 格式解码"""
        def zigzag_decode(n: int) -> int:
            return (n >> 1) ^ -(n & 1)
        
        # 简化解码
        return cls()  # TODO: 完整实现
    
    @staticmethod
    def _encode_varint(value: int) -> bytes:
        """编码 varint"""
        result = []
        while value > 127:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value)
        return bytes(result)


@dataclass
class PB_HeartBeatCH:
    """
    心跳包 (proto_ch.proto)
    
    用于 UDP 和 WebSocket 链路的高频保活及时间对齐
    """
    BeatCode: int = 0      # 心跳序列号
    server_time: int = 0   # 服务器毫秒级时间戳
    client_time: int = 0   # 客户端毫秒级时间戳
    
    def encode(self) -> bytes:
        """编码"""
        data = b''
        # field 1: BeatCode (uint64)
        data += b'\x08' + self._encode_varint(self.BeatCode)
        # field 2: server_time (uint64)
        data += b'\x10' + self._encode_varint(self.server_time)
        # field 3: client_time (uint64)
        data += b'\x18' + self._encode_varint(self.client_time)
        return data
    
    @staticmethod
    def _encode_varint(value: int) -> bytes:
        """编码 varint"""
        result = []
        while value > 127:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value)
        return bytes(result)


@dataclass
class PB_ThornBallCH:
    """
    荆棘球/战斗 (proto_ch_ver2.proto)
    
    承载核心战斗逻辑
    """
    atkpoints: int = 0     # 攻击力/伤害点数
    num: int = 0           # 触发数量
    dir: int = 0           # 作用方向
    
    def encode(self) -> bytes:
        """编码"""
        data = b''
        # field 1: atkpoints (int32)
        data += b'\x08' + self._encode_varint(self.atkpoints)
        # field 2: num (int32)
        data += b'\x10' + self._encode_varint(self.num)
        # field 3: dir (int32)
        data += b'\x18' + self._encode_varint(self.dir)
        return data
    
    @staticmethod
    def _encode_varint(value: int) -> bytes:
        """编码 varint"""
        result = []
        while value > 127:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value)
        return bytes(result)


@dataclass
class PB_ActorOperationCH:
    """
    实体操作 (proto_ch_ver2.proto)
    
    同步玩家的位移、挖掘、建筑等实时操作
    """
    blockid: int = 0       # 操作目标方块ID
    operation_type: int = 0  # 操作类型 (扩展)
    position: Optional[PB_Vector3] = None  # 位置
    
    # 操作类型枚举
    OP_MOVE = 0
    OP_DIG = 1
    OP_BUILD = 2
    OP_INTERACT = 3
    
    def encode(self) -> bytes:
        """编码"""
        data = b''
        # field 1: blockid (int32)
        data += b'\x08' + self._encode_varint(self.blockid)
        return data
    
    @staticmethod
    def _encode_varint(value: int) -> bytes:
        """编码 varint"""
        result = []
        while value > 127:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value)
        return bytes(result)


@dataclass
class PB_RoomInfo:
    """
    房间信息 (proto_room.proto)
    
    用于联机大厅及房间状态同步
    """
    OwnerUin: int = 0          # 房主唯一识别码
    PlayerCount: int = 0       # 当前房间人数
    MaxPlayerCount: int = 0    # 房间上限
    GameType: int = 0          # 玩法模式 (0=生存, 1=创造, 2=冒险)
    
    def encode(self) -> bytes:
        """编码"""
        data = b''
        # field 1: OwnerUin (uint32)
        data += b'\x08' + self._encode_varint(self.OwnerUin)
        # field 2: PlayerCount (int32)
        data += b'\x10' + self._encode_varint(self.PlayerCount)
        # field 3: MaxPlayerCount (int32)
        data += b'\x18' + self._encode_varint(self.MaxPlayerCount)
        # field 4: GameType (int32)
        data += b'\x20' + self._encode_varint(self.GameType)
        return data
    
    @staticmethod
    def _encode_varint(value: int) -> bytes:
        """编码 varint"""
        result = []
        while value > 127:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value)
        return bytes(result)


@dataclass
class PB_ItemDataComponent:
    """
    物品/组件数据 (proto_common.proto)
    """
    name: str = ""           # 物品/组件唯一名称
    data: bytes = b''        # 序列化后的组件私有数据
    
    def encode(self) -> bytes:
        """编码"""
        data = b''
        # field 1: name (string)
        name_bytes = self.name.encode('utf-8')
        data += b'\x0a' + self._encode_varint(len(name_bytes)) + name_bytes
        # field 2: data (bytes)
        data += b'\x12' + self._encode_varint(len(self.data)) + self.data
        return data
    
    @staticmethod
    def _encode_varint(value: int) -> bytes:
        """编码 varint"""
        result = []
        while value > 127:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value)
        return bytes(result)
