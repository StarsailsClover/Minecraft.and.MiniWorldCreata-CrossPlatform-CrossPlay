"""
协议转发器测试 - MC <-> MNW 双向转发
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import struct
import asyncio
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable
from enum import IntEnum

# 模拟 MC Java 协议
class MCJavaPacketID(IntEnum):
    CHAT_MESSAGE = 0x0E
    PLAYER_POSITION = 0x11
    PLAYER_POSITION_AND_ROTATION = 0x12
    BLOCK_CHANGE = 0x09

@dataclass
class MCJavaPacket:
    packet_id: int
    data: bytes
    
    def encode(self) -> bytes:
        # VarInt 长度前缀
        length = len(self.data) + 1
        return self._encode_varint(length) + self._encode_varint(self.packet_id) + self.data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['MCJavaPacket']:
        try:
            length, offset = cls._decode_varint(data, 0)
            packet_id, offset = cls._decode_varint(data, offset)
            payload = data[offset:offset+length-1]
            return cls(packet_id=packet_id, data=payload)
        except:
            return None
    
    @staticmethod
    def _encode_varint(value: int) -> bytes:
        result = []
        while value > 127:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value)
        return bytes(result)
    
    @staticmethod
    def _decode_varint(data: bytes, offset: int) -> tuple:
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
        return value, offset


# 模拟 MNW 协议
class MNWMsgType(IntEnum):
    CHAT_MESSAGE = 0x7EA
    PLAYER_MOVE = 0x7E0
    CREATE_BLOCK = 1010

@dataclass
class MNWPacket:
    proto_id: int
    uin: int
    data: bytes
    
    def encode(self) -> bytes:
        header = struct.pack('>HQ', self.proto_id, self.uin)
        return header + struct.pack('>I', len(self.data)) + self.data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['MNWPacket']:
        if len(data) < 14:
            return None
        try:
            proto_id, uin = struct.unpack('>HQ', data[:10])
            data_len = struct.unpack('>I', data[10:14])[0]
            payload = data[14:14+data_len]
            return cls(proto_id=proto_id, uin=uin, data=payload)
        except:
            return None


@dataclass
class UnifiedPacket:
    """统一数据包格式"""
    source: str  # "mc" or "mnw"
    packet_type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time())


class ProtocolBridge:
    """协议转发器"""
    
    def __init__(self):
        self.mc_to_mnw_handlers: Dict[int, Callable] = {}
        self.mnw_to_mc_handlers: Dict[int, Callable] = {}
        self.stats = {
            "mc_to_mnw": 0,
            "mnw_to_mc": 0,
            "errors": 0
        }
    
    def register_mc_handler(self, packet_id: int, handler: Callable):
        """注册 MC -> MNW 处理器"""
        self.mc_to_mnw_handlers[packet_id] = handler
    
    def register_mnw_handler(self, msg_type: int, handler: Callable):
        """注册 MNW -> MC 处理器"""
        self.mnw_to_mc_handlers[msg_type] = handler
    
    async def mc_to_mnw(self, mc_packet: MCJavaPacket, player_uin: int) -> Optional[MNWPacket]:
        """MC 数据包 -> MNW 数据包"""
        try:
            print(f"[Bridge] MC -> MNW: packet_id=0x{mc_packet.packet_id:02X}")
            
            handler = self.mc_to_mnw_handlers.get(mc_packet.packet_id)
            if not handler:
                print(f"  [Bridge] 无处理器，跳过")
                return None
            
            unified = await handler(mc_packet)
            if not unified:
                return None
            
            # 转换为 MNW 数据包
            mnw_packet = self._unified_to_mnw(unified, player_uin)
            
            self.stats["mc_to_mnw"] += 1
            print(f"  [Bridge] 转发成功 -> MNW proto_id=0x{mnw_packet.proto_id:04X}")
            return mnw_packet
            
        except Exception as e:
            print(f"  [Bridge] 转发失败: {e}")
            self.stats["errors"] += 1
            return None
    
    async def mnw_to_mc(self, mnw_packet: MNWPacket) -> Optional[MCJavaPacket]:
        """MNW 数据包 -> MC 数据包"""
        try:
            print(f"[Bridge] MNW -> MC: proto_id=0x{mnw_packet.proto_id:04X}")
            
            handler = self.mnw_to_mc_handlers.get(mnw_packet.proto_id)
            if not handler:
                print(f"  [Bridge] 无处理器，跳过")
                return None
            
            unified = await handler(mnw_packet)
            if not unified:
                return None
            
            # 转换为 MC 数据包
            mc_packet = self._unified_to_mc(unified)
            
            self.stats["mnw_to_mc"] += 1
            print(f"  [Bridge] 转发成功 -> MC packet_id=0x{mc_packet.packet_id:02X}")
            return mc_packet
            
        except Exception as e:
            print(f"  [Bridge] 转发失败: {e}")
            self.stats["errors"] += 1
            return None
    
    def _unified_to_mnw(self, unified: UnifiedPacket, player_uin: int) -> MNWPacket:
        """统一格式 -> MNW"""
        if unified.packet_type == "chat":
            proto_id = MNWMsgType.CHAT_MESSAGE
            data = unified.data["message"].encode('utf-8')
        elif unified.packet_type == "player_move":
            proto_id = MNWMsgType.PLAYER_MOVE
            pos = unified.data["position"]
            data = struct.pack('>fff', pos['x'], pos['y'], pos['z'])
        else:
            proto_id = 0
            data = b''
        
        return MNWPacket(proto_id=proto_id, uin=player_uin, data=data)
    
    def _unified_to_mc(self, unified: UnifiedPacket) -> MCJavaPacket:
        """统一格式 -> MC"""
        if unified.packet_type == "chat":
            packet_id = MCJavaPacketID.CHAT_MESSAGE
            data = unified.data["message"].encode('utf-8')
        elif unified.packet_type == "block_change":
            packet_id = MCJavaPacketID.BLOCK_CHANGE
            pos = unified.data["position"]
            block_id = unified.data["block_id"]
            data = struct.pack('>iiii', pos['x'], pos['y'], pos['z'], block_id)
        else:
            packet_id = 0
            data = b''
        
        return MCJavaPacket(packet_id=packet_id, data=data)
    
    def get_stats(self) -> Dict[str, int]:
        return self.stats.copy()


# 处理器实现
async def handle_mc_chat(mc_packet: MCJavaPacket) -> Optional[UnifiedPacket]:
    """处理 MC 聊天消息"""
    message = mc_packet.data.decode('utf-8')
    print(f"  [Handler] MC Chat: {message}")
    return UnifiedPacket(
        source="mc",
        packet_type="chat",
        data={"message": message}
    )

async def handle_mc_player_move(mc_packet: MCJavaPacket) -> Optional[UnifiedPacket]:
    """处理 MC 玩家移动"""
    x, y, z = struct.unpack('>ddd', mc_packet.data[:24])
    print(f"  [Handler] MC Player Move: ({x:.2f}, {y:.2f}, {z:.2f})")
    return UnifiedPacket(
        source="mc",
        packet_type="player_move",
        data={"position": {"x": x, "y": y, "z": z}}
    )

async def handle_mnw_chat(mnw_packet: MNWPacket) -> Optional[UnifiedPacket]:
    """处理 MNW 聊天消息"""
    message = mnw_packet.data.decode('utf-8')
    print(f"  [Handler] MNW Chat: {message}")
    return UnifiedPacket(
        source="mnw",
        packet_type="chat",
        data={"message": message}
    )

async def handle_mnw_block_change(mnw_packet: MNWPacket) -> Optional[UnifiedPacket]:
    """处理 MNW 方块变更"""
    x, y, z, block_id = struct.unpack('>iiii', mnw_packet.data[:16])
    print(f"  [Handler] MNW Block Change: ({x}, {y}, {z}) -> {block_id}")
    return UnifiedPacket(
        source="mnw",
        packet_type="block_change",
        data={"position": {"x": x, "y": y, "z": z}, "block_id": block_id}
    )


async def test_protocol_bridge():
    print("\n" + "=" * 60)
    print("协议转发器测试")
    print("=" * 60)
    
    bridge = ProtocolBridge()
    
    # 注册处理器
    bridge.register_mc_handler(MCJavaPacketID.CHAT_MESSAGE, handle_mc_chat)
    bridge.register_mc_handler(MCJavaPacketID.PLAYER_POSITION, handle_mc_player_move)
    bridge.register_mnw_handler(MNWMsgType.CHAT_MESSAGE, handle_mnw_chat)
    bridge.register_mnw_handler(MNWMsgType.CREATE_BLOCK, handle_mnw_block_change)
    
    # 测试 MC -> MNW 转发
    print("\n[测试 1] MC -> MNW 转发")
    print("-" * 40)
    
    mc_chat = MCJavaPacket(
        packet_id=MCJavaPacketID.CHAT_MESSAGE,
        data=b"Hello from Minecraft!"
    )
    mnw_packet = await bridge.mc_to_mnw(mc_chat, player_uin=2056826320)
    
    mc_move = MCJavaPacket(
        packet_id=MCJavaPacketID.PLAYER_POSITION,
        data=struct.pack('>ddd', 100.5, 64.0, -50.25)
    )
    mnw_packet2 = await bridge.mc_to_mnw(mc_move, player_uin=2056826320)
    
    # 测试 MNW -> MC 转发
    print("\n[测试 2] MNW -> MC 转发")
    print("-" * 40)
    
    mnw_chat = MNWPacket(
        proto_id=MNWMsgType.CHAT_MESSAGE,
        uin=1234567890,
        data=b"Hello from MiniWorld!"
    )
    mc_packet = await bridge.mnw_to_mc(mnw_chat)
    
    mnw_block = MNWPacket(
        proto_id=MNWMsgType.CREATE_BLOCK,
        uin=1234567890,
        data=struct.pack('>iiii', 10, 64, 20, 1)
    )
    mc_packet2 = await bridge.mnw_to_mc(mnw_block)
    
    # 测试未注册的消息类型
    print("\n[测试 3] 未注册消息类型")
    print("-" * 40)
    
    mc_unknown = MCJavaPacket(
        packet_id=0xFF,  # 未知类型
        data=b"unknown"
    )
    result = await bridge.mc_to_mnw(mc_unknown, player_uin=2056826320)
    if result is None:
        print("  [Bridge] 未知类型已正确跳过")
    
    # 打印统计
    print("\n" + "=" * 60)
    print("转发统计")
    print("=" * 60)
    stats = bridge.get_stats()
    print(f"  MC -> MNW: {stats['mc_to_mnw']} 条")
    print(f"  MNW -> MC: {stats['mnw_to_mc']} 条")
    print(f"  错误: {stats['errors']} 条")
    
    return stats['errors'] == 0


async def main():
    try:
        success = await test_protocol_bridge()
        
        print("\n" + "=" * 60)
        if success:
            print("测试结果: 通过")
        else:
            print("测试结果: 失败")
        print("=" * 60)
        
        return success
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
