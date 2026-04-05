"""
MnMCP 协议层
v1.0.0_26w13a

统一的数据包定义 + MC/MNW 协议 + 翻译器

合并自旧项目:
  protocol/mc_protocol.py
  protocol/mnw_protocol.py
  protocol/packet_translator.py
  multiplayer/common/protocol_bridge.py
  (消除了 codec 缺失问题)
"""

from __future__ import annotations

import struct
import logging
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, Optional, Callable, Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
#  统一数据包
# ═══════════════════════════════════════════════════════════

class GameAction(IntEnum):
    """平台无关的游戏操作类型"""
    PLAYER_MOVE = 0x01
    PLAYER_LOOK = 0x02
    BLOCK_PLACE = 0x03
    BLOCK_BREAK = 0x04
    CHAT_MESSAGE = 0x05
    PLAYER_JOIN = 0x06
    PLAYER_LEAVE = 0x07
    ENTITY_SPAWN = 0x08
    ENTITY_MOVE = 0x09
    ENTITY_REMOVE = 0x0A
    INVENTORY_CHANGE = 0x0B
    HEALTH_UPDATE = 0x0C
    WORLD_TIME = 0x0D
    CHUNK_DATA = 0x0E
    LOGIN = 0x10
    LOGIN_RESPONSE = 0x11
    DISCONNECT = 0x12
    HEARTBEAT = 0xFF


@dataclass
class UnifiedPacket:
    """
    统一数据包: MC/MNW 先解码为此格式, 再编码为目标协议。
    消除了旧项目中 codec 模块缺失的问题。
    """
    action: GameAction
    timestamp: float = field(default_factory=time.time)
    seq_id: int = 0
    source: str = ""  # "mc" | "mnw"

    # 玩家
    player_name: str = ""
    player_uuid: str = ""

    # 位置
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    yaw: float = 0.0
    pitch: float = 0.0

    # 方块
    block_id: int = 0
    block_meta: int = 0

    # 聊天
    message: str = ""

    # 实体
    entity_id: int = 0
    entity_type: int = 0

    # 原始数据 (无法翻译时保留)
    raw: bytes = b""

    # 扩展
    extra: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
#  Minecraft Bedrock 协议
# ═══════════════════════════════════════════════════════════

class MCPacketID(IntEnum):
    """MC Bedrock 数据包 ID (已修复重复值冲突)"""
    LOGIN = 0x01
    PLAY_STATUS = 0x02
    DISCONNECT = 0x05
    RESOURCE_PACKS_INFO = 0x06
    RESOURCE_PACK_STACK = 0x07
    TEXT = 0x09
    SET_TIME = 0x0A
    START_GAME = 0x0B
    ADD_PLAYER = 0x0C
    ADD_ENTITY = 0x0D
    REMOVE_ENTITY = 0x0E
    ADD_ITEM_ENTITY = 0x0F
    TAKE_ITEM_ENTITY = 0x11
    MOVE_ENTITY_ABSOLUTE = 0x12
    MOVE_PLAYER = 0x13
    RIDER_JUMP = 0x14
    UPDATE_BLOCK = 0x15
    UPDATE_BLOCK_SYNCED = 0x16
    EXPLODE = 0x17
    LEVEL_SOUND_EVENT = 0x18
    LEVEL_EVENT = 0x19
    BLOCK_EVENT = 0x1A
    ENTITY_EVENT = 0x1B
    MOB_EFFECT = 0x1C
    UPDATE_ATTRIBUTES = 0x1D
    INVENTORY_TRANSACTION = 0x1E
    MOB_EQUIPMENT = 0x1F
    MOB_ARMOR_EQUIPMENT = 0x20
    INTERACT = 0x21
    BLOCK_PICK_REQUEST = 0x22
    ENTITY_PICK_REQUEST = 0x23
    PLAYER_ACTION = 0x24
    TICK_SYNC = 0x17  # 注意: 与 EXPLODE 共用, 运行时按上下文区分


class VarInt:
    """Minecraft VarInt 编解码"""

    @staticmethod
    def encode(value: int) -> bytes:
        result = bytearray()
        while True:
            byte = value & 0x7F
            value >>= 7
            if value:
                byte |= 0x80
            result.append(byte)
            if not value:
                break
        return bytes(result)

    @staticmethod
    def decode(data: bytes, offset: int = 0) -> tuple[int, int]:
        """返回 (value, bytes_read)"""
        result = 0
        shift = 0
        for i in range(5):
            if offset + i >= len(data):
                raise ValueError("VarInt 数据不足")
            byte = data[offset + i]
            result |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                return result, i + 1
            shift += 7
        raise ValueError("VarInt 过长")


class MCCodec:
    """MC Bedrock 编解码器 (替代缺失的 codec.mc_codec)"""

    @staticmethod
    def decode_packet(data: bytes) -> Optional[UnifiedPacket]:
        """将 MC 原始数据包解码为 UnifiedPacket"""
        if len(data) < 1:
            return None
        try:
            pkt_id, consumed = VarInt.decode(data)
            payload = data[consumed:]

            if pkt_id == MCPacketID.MOVE_PLAYER and len(payload) >= 28:
                # runtime_id(varint) + x,y,z(float LE) + pitch,yaw(float LE)
                x = struct.unpack_from("<f", payload, 0)[0]
                y = struct.unpack_from("<f", payload, 4)[0]
                z = struct.unpack_from("<f", payload, 8)[0]
                pitch = struct.unpack_from("<f", payload, 12)[0]
                yaw = struct.unpack_from("<f", payload, 16)[0]
                return UnifiedPacket(
                    action=GameAction.PLAYER_MOVE, source="mc",
                    x=x, y=y, z=z, pitch=pitch, yaw=yaw, raw=data,
                )

            if pkt_id == MCPacketID.TEXT and len(payload) > 2:
                # 简化: 跳过类型字节, 读 VarInt 长度 + UTF-8
                msg_type = payload[0]
                try:
                    str_len, sc = VarInt.decode(payload, 1)
                    message = payload[1 + sc: 1 + sc + str_len].decode("utf-8", errors="replace")
                    return UnifiedPacket(
                        action=GameAction.CHAT_MESSAGE, source="mc",
                        message=message, raw=data,
                    )
                except Exception:
                    pass

            if pkt_id == MCPacketID.UPDATE_BLOCK and len(payload) >= 12:
                # position(BlockPos) + block_runtime_id(varint)
                return UnifiedPacket(
                    action=GameAction.BLOCK_PLACE, source="mc", raw=data,
                )

            # 未识别的包 → 保留原始数据
            return UnifiedPacket(
                action=GameAction.HEARTBEAT, source="mc", raw=data,
                extra={"packet_id": pkt_id},
            )
        except Exception as e:
            logger.debug("MC 解码失败: %s", e)
            return None

    @staticmethod
    def encode_packet(pkt: UnifiedPacket) -> bytes:
        """将 UnifiedPacket 编码为 MC 原始数据包"""
        if pkt.action == GameAction.CHAT_MESSAGE:
            msg_bytes = pkt.message.encode("utf-8")
            payload = bytes([0x01]) + VarInt.encode(len(msg_bytes)) + msg_bytes
            return VarInt.encode(MCPacketID.TEXT) + payload

        if pkt.action == GameAction.PLAYER_MOVE:
            payload = struct.pack("<fffff", pkt.x, pkt.y, pkt.z, pkt.pitch, pkt.yaw)
            return VarInt.encode(MCPacketID.MOVE_PLAYER) + payload

        # 默认: 返回原始数据
        return pkt.raw


# ═══════════════════════════════════════════════════════════
#  迷你世界协议 (Protobuf over TCP)
# ═══════════════════════════════════════════════════════════

class MNWMsgType(IntEnum):
    """
    迷你世界消息类型 (基于 PROTOCOL_IMPLEMENTATION_GUIDE.md)
    数据包格式: [length(4B LE)] [msg_type(4B LE)] [Protobuf payload]
    """
    # 角色/世界
    ROLE_ENTER_WORLD = 1001
    ROLE_LEAVE_WORLD = 1002
    CREATE_BLOCK = 1010
    DESTROY_BLOCK = 1011
    MOVE_ROLE = 1020
    # 聊天
    CHAT = 2001
    SYSTEM_MSG = 2002
    # 登录
    LOGIN_REQ = 3001
    LOGIN_RESP = 3002
    HEARTBEAT = 3003
    DISCONNECT = 3004


class MNWCodec:
    """迷你世界编解码器 (替代缺失的 codec.mnw_codec)"""

    HEADER_SIZE = 8  # length(4) + msg_type(4)

    @staticmethod
    def decode_packet(data: bytes) -> Optional[UnifiedPacket]:
        """将 MNW 原始数据包解码为 UnifiedPacket"""
        if len(data) < MNWCodec.HEADER_SIZE:
            return None
        try:
            length = struct.unpack_from("<I", data, 0)[0]
            msg_type = struct.unpack_from("<I", data, 4)[0]
            payload = data[8:length] if length <= len(data) else data[8:]

            if msg_type == MNWMsgType.MOVE_ROLE:
                # Protobuf: field1=role_id, field2=position{x,y,z}
                # 简化解析: 直接读 float
                if len(payload) >= 12:
                    x = struct.unpack_from("<f", payload, 0)[0]
                    y = struct.unpack_from("<f", payload, 4)[0]
                    z = struct.unpack_from("<f", payload, 8)[0]
                    return UnifiedPacket(
                        action=GameAction.PLAYER_MOVE, source="mnw",
                        x=x, y=y, z=z, raw=data,
                    )

            if msg_type == MNWMsgType.CHAT:
                # 简化: 尝试 UTF-8 解码
                try:
                    message = payload.decode("utf-8", errors="replace")
                    return UnifiedPacket(
                        action=GameAction.CHAT_MESSAGE, source="mnw",
                        message=message, raw=data,
                    )
                except Exception:
                    pass

            if msg_type == MNWMsgType.CREATE_BLOCK:
                return UnifiedPacket(
                    action=GameAction.BLOCK_PLACE, source="mnw", raw=data,
                )

            if msg_type == MNWMsgType.DESTROY_BLOCK:
                return UnifiedPacket(
                    action=GameAction.BLOCK_BREAK, source="mnw", raw=data,
                )

            if msg_type == MNWMsgType.HEARTBEAT:
                return UnifiedPacket(action=GameAction.HEARTBEAT, source="mnw", raw=data)

            return UnifiedPacket(
                action=GameAction.HEARTBEAT, source="mnw", raw=data,
                extra={"msg_type": msg_type},
            )
        except Exception as e:
            logger.debug("MNW 解码失败: %s", e)
            return None

    @staticmethod
    def encode_packet(pkt: UnifiedPacket) -> bytes:
        """将 UnifiedPacket 编码为 MNW 原始数据包"""
        if pkt.action == GameAction.CHAT_MESSAGE:
            payload = pkt.message.encode("utf-8")
            header = struct.pack("<II", 8 + len(payload), MNWMsgType.CHAT)
            return header + payload

        if pkt.action == GameAction.PLAYER_MOVE:
            payload = struct.pack("<fff", pkt.x, pkt.y, pkt.z)
            header = struct.pack("<II", 8 + len(payload), MNWMsgType.MOVE_ROLE)
            return header + payload

        if pkt.action == GameAction.HEARTBEAT:
            return struct.pack("<II", 8, MNWMsgType.HEARTBEAT)

        return pkt.raw


# ═══════════════════════════════════════════════════════════
#  协议翻译器 (统一)
# ═══════════════════════════════════════════════════════════

class ProtocolTranslator:
    """
    MC ↔ MNW 双向翻译器

    流程:
      MC raw bytes → MCCodec.decode → UnifiedPacket → 映射转换 → MNWCodec.encode → MNW raw bytes
      MNW raw bytes → MNWCodec.decode → UnifiedPacket → 映射转换 → MCCodec.encode → MC raw bytes
    """

    def __init__(self):
        from ..mapping import BlockMapper, CoordinateConverter
        self.block_mapper = BlockMapper()
        self.coord_converter = CoordinateConverter()
        self.mc_codec = MCCodec()
        self.mnw_codec = MNWCodec()

        # 统计
        self.mc_to_mnw_count = 0
        self.mnw_to_mc_count = 0
        logger.info("协议翻译器初始化完成 (方块映射: %d 条)", self.block_mapper.count)

    def mc_to_mnw(self, mc_data: bytes) -> Optional[bytes]:
        """MC → MNW"""
        pkt = self.mc_codec.decode_packet(mc_data)
        if not pkt:
            return None

        # 坐标转换
        if pkt.action in (GameAction.PLAYER_MOVE, GameAction.BLOCK_PLACE, GameAction.BLOCK_BREAK):
            from ..mapping import Vec3
            converted = self.coord_converter.mc_to_mnw(Vec3(pkt.x, pkt.y, pkt.z))
            pkt.x, pkt.y, pkt.z = converted.x, converted.y, converted.z

        # 方块 ID 转换
        if pkt.action in (GameAction.BLOCK_PLACE,):
            pkt.block_id = self.block_mapper.get_mnw_id(pkt.block_id)

        self.mc_to_mnw_count += 1
        return self.mnw_codec.encode_packet(pkt)

    def mnw_to_mc(self, mnw_data: bytes) -> Optional[bytes]:
        """MNW → MC"""
        pkt = self.mnw_codec.decode_packet(mnw_data)
        if not pkt:
            return None

        # 坐标转换
        if pkt.action in (GameAction.PLAYER_MOVE, GameAction.BLOCK_PLACE, GameAction.BLOCK_BREAK):
            from ..mapping import Vec3
            converted = self.coord_converter.mnw_to_mc(Vec3(pkt.x, pkt.y, pkt.z))
            pkt.x, pkt.y, pkt.z = converted.x, converted.y, converted.z

        # 方块 ID 转换
        if pkt.action in (GameAction.BLOCK_PLACE,):
            pkt.block_id = self.block_mapper.get_mc_id(pkt.block_id)

        self.mnw_to_mc_count += 1
        return self.mc_codec.encode_packet(pkt)
