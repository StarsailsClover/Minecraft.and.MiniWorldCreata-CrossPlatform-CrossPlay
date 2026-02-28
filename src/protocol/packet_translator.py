#!/usr/bin/env python3
"""
协议翻译器 - v0.3.0_26w10a_Phase 2
在Minecraft和迷你世界协议之间进行双向翻译

架构:
- PacketTranslator: 主翻译器
- MCPacketHandler: Minecraft协议处理器
- MNWPacketHandler: 迷你世界协议处理器
"""

import struct
import json
import logging
from typing import Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path

from .block_mapper import BlockMapper
from .coordinate_converter import CoordinateConverter

logger = logging.getLogger(__name__)


class PacketType(IntEnum):
    """数据包类型"""
    # 迷你世界
    MNW_LOGIN = 0x01
    MNW_GAME = 0x02
    MNW_CHAT = 0x03
    MNW_PLAYER = 0x04
    MNW_WORLD = 0x05
    MNW_ENTITY = 0x06
    MNW_INVENTORY = 0x07
    MNW_BLOCK = 0x08
    MNW_HEARTBEAT = 0xFF
    
    # Minecraft
    MC_HANDSHAKE = 0x00
    MC_STATUS = 0x01
    MC_LOGIN = 0x02
    MC_PLAY = 0x03


@dataclass
class Packet:
    """通用数据包结构"""
    packet_type: int
    sub_type: int
    seq_id: int
    data: bytes
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    
    def to_bytes(self) -> bytes:
        """转换为字节"""
        header = struct.pack('>BBHI', 
            self.packet_type,
            self.sub_type,
            self.seq_id,
            len(self.data)
        )
        # 添加简单的校验和（实际应该使用CRC32）
        checksum = sum(header + self.data) & 0xFFFFFFFF
        return header + self.data + struct.pack('>I', checksum)
    
    @classmethod
    def from_bytes(cls, data: bytes) -> Optional['Packet']:
        """从字节解析"""
        if len(data) < 8:
            return None
        
        try:
            packet_type = struct.unpack('B', data[0:1])[0]
            sub_type = struct.unpack('B', data[1:2])[0]
            seq_id = struct.unpack('>H', data[2:4])[0]
            data_length = struct.unpack('>I', data[4:8])[0]
            
            if len(data) < 8 + data_length + 4:
                return None
            
            payload = data[8:8+data_length]
            # 校验和验证（可选）
            # stored_checksum = struct.unpack('>I', data[8+data_length:8+data_length+4])[0]
            
            return cls(packet_type, sub_type, seq_id, payload)
        except struct.error:
            return None


@dataclass
class PlayerPosition:
    """玩家位置"""
    x: float
    y: float
    z: float
    yaw: float = 0.0
    pitch: float = 0.0
    on_ground: bool = True
    
    def to_mnw(self) -> Dict:
        """转换为迷你世界格式"""
        return {
            'x': int(self.x * 100),  # 迷你世界使用整数坐标（乘以100）
            'y': int(self.y * 100),
            'z': int(self.z * 100),
            'yaw': int(self.yaw * 256 / 360),  # 转换为字节角度
            'pitch': int(self.pitch * 256 / 360),
        }
    
    @classmethod
    def from_mnw(cls, data: Dict) -> 'PlayerPosition':
        """从迷你世界格式解析"""
        return cls(
            x=data.get('x', 0) / 100.0,
            y=data.get('y', 0) / 100.0,
            z=data.get('z', 0) / 100.0,
            yaw=data.get('yaw', 0) * 360 / 256,
            pitch=data.get('pitch', 0) * 360 / 256,
        )


@dataclass
class BlockUpdate:
    """方块更新"""
    x: int
    y: int
    z: int
    block_id: int
    block_data: int = 0
    
    def to_mnw(self, block_mapper: BlockMapper) -> Dict:
        """转换为迷你世界格式"""
        mnw_id = block_mapper.mc_to_mnw.get(self.block_id, self.block_id)
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'id': mnw_id,
            'data': self.block_data,
        }
    
    @classmethod
    def from_mnw(cls, data: Dict, block_mapper: BlockMapper) -> 'BlockUpdate':
        """从迷你世界格式解析"""
        mnw_id = data.get('id', 0)
        mc_id = block_mapper.mnw_to_mc.get(mnw_id, mnw_id)
        return cls(
            x=data.get('x', 0),
            y=data.get('y', 0),
            z=data.get('z', 0),
            block_id=mc_id,
            block_data=data.get('data', 0),
        )


class PacketTranslator:
    """
    协议翻译器
    
    负责在Minecraft和迷你世界协议之间进行双向翻译
    """
    
    def __init__(self, block_mapper: BlockMapper = None):
        self.block_mapper = block_mapper or BlockMapper()
        self.coord_converter = CoordinateConverter()
        
        # 序列号管理
        self.mnw_seq = 0
        self.mc_seq = 0
        
        # 统计信息
        self.stats = {
            'packets_translated': 0,
            'bytes_translated': 0,
            'errors': 0,
        }
        
        # 翻译器注册表
        self._translators: Dict[Tuple[int, str], Callable] = {}
        self._register_default_translators()
        
        logger.info("协议翻译器初始化完成")
    
    def _register_default_translators(self):
        """注册默认翻译器"""
        # 位置更新
        self.register_translator(PacketType.MNW_PLAYER, 'position', self._translate_position)
        
        # 方块更新
        self.register_translator(PacketType.MNW_BLOCK, 'update', self._translate_block_update)
        
        # 聊天消息
        self.register_translator(PacketType.MNW_CHAT, 'message', self._translate_chat)
        
        # 登录
        self.register_translator(PacketType.MNW_LOGIN, 'auth', self._translate_login)
    
    def register_translator(self, packet_type: int, sub_type: str, 
                           translator: Callable):
        """注册翻译器"""
        self._translators[(packet_type, sub_type)] = translator
        logger.debug(f"注册翻译器: {packet_type}/{sub_type}")
    
    def translate_mnw_to_mc(self, mnw_packet: Packet) -> Optional[Packet]:
        """
        将迷你世界数据包翻译为Minecraft数据包
        
        Args:
            mnw_packet: 迷你世界数据包
            
        Returns:
            Minecraft数据包，或None（如果无法翻译）
        """
        try:
            # 根据包类型选择翻译器
            key = (mnw_packet.packet_type, 'default')
            translator = self._translators.get(key)
            
            if translator:
                mc_packet = translator(mnw_packet, 'mnw_to_mc')
                self.stats['packets_translated'] += 1
                self.stats['bytes_translated'] += len(mnw_packet.data)
                return mc_packet
            else:
                # 默认转发（可能需要修改包类型）
                return self._default_translate(mnw_packet, 'mnw_to_mc')
                
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            self.stats['errors'] += 1
            return None
    
    def translate_mc_to_mnw(self, mc_packet: Packet) -> Optional[Packet]:
        """
        将Minecraft数据包翻译为迷你世界数据包
        
        Args:
            mc_packet: Minecraft数据包
            
        Returns:
            迷你世界数据包，或None（如果无法翻译）
        """
        try:
            key = (mc_packet.packet_type, 'default')
            translator = self._translators.get(key)
            
            if translator:
                mnw_packet = translator(mc_packet, 'mc_to_mnw')
                self.stats['packets_translated'] += 1
                self.stats['bytes_translated'] += len(mc_packet.data)
                return mnw_packet
            else:
                return self._default_translate(mc_packet, 'mc_to_mnw')
                
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            self.stats['errors'] += 1
            return None
    
    def _default_translate(self, packet: Packet, direction: str) -> Packet:
        """默认翻译（仅修改包类型）"""
        # 简单的包类型映射
        type_mapping = {
            # MNW -> MC
            PacketType.MNW_LOGIN: PacketType.MC_LOGIN,
            PacketType.MNW_GAME: PacketType.MC_PLAY,
            PacketType.MNW_CHAT: PacketType.MC_PLAY,
            PacketType.MNW_PLAYER: PacketType.MC_PLAY,
            PacketType.MNW_WORLD: PacketType.MC_PLAY,
            PacketType.MNW_BLOCK: PacketType.MC_PLAY,
            
            # MC -> MNW
            PacketType.MC_LOGIN: PacketType.MNW_LOGIN,
            PacketType.MC_PLAY: PacketType.MNW_GAME,
        }
        
        new_type = type_mapping.get(packet.packet_type, packet.packet_type)
        
        return Packet(
            packet_type=new_type,
            sub_type=packet.sub_type,
            seq_id=self._get_next_seq(direction),
            data=packet.data
        )
    
    def _get_next_seq(self, direction: str) -> int:
        """获取下一个序列号"""
        if direction == 'mnw_to_mc':
            self.mc_seq = (self.mc_seq + 1) & 0xFFFF
            return self.mc_seq
        else:
            self.mnw_seq = (self.mnw_seq + 1) & 0xFFFF
            return self.mnw_seq
    
    def _translate_position(self, packet: Packet, direction: str) -> Packet:
        """翻译位置更新"""
        try:
            # 解析位置数据
            if direction == 'mnw_to_mc':
                # MNW -> MC
                mnw_pos = json.loads(packet.data.decode('utf-8'))
                pos = PlayerPosition.from_mnw(mnw_pos)
                
                # 转换为Minecraft格式
                mc_data = {
                    'x': pos.x,
                    'y': pos.y,
                    'z': pos.z,
                    'yaw': pos.yaw,
                    'pitch': pos.pitch,
                    'onGround': pos.on_ground,
                }
                
                return Packet(
                    packet_type=PacketType.MC_PLAY,
                    sub_type=0x11,  # Player Position And Look
                    seq_id=self._get_next_seq(direction),
                    data=json.dumps(mc_data).encode('utf-8')
                )
            else:
                # MC -> MNW
                mc_pos = json.loads(packet.data.decode('utf-8'))
                pos = PlayerPosition(
                    x=mc_pos.get('x', 0),
                    y=mc_pos.get('y', 0),
                    z=mc_pos.get('z', 0),
                    yaw=mc_pos.get('yaw', 0),
                    pitch=mc_pos.get('pitch', 0),
                )
                
                return Packet(
                    packet_type=PacketType.MNW_PLAYER,
                    sub_type=0x01,  # Position Update
                    seq_id=self._get_next_seq(direction),
                    data=json.dumps(pos.to_mnw()).encode('utf-8')
                )
        except Exception as e:
            logger.error(f"位置翻译失败: {e}")
            return self._default_translate(packet, direction)
    
    def _translate_block_update(self, packet: Packet, direction: str) -> Packet:
        """翻译方块更新"""
        try:
            if direction == 'mnw_to_mc':
                # MNW -> MC
                mnw_block = json.loads(packet.data.decode('utf-8'))
                block = BlockUpdate.from_mnw(mnw_block, self.block_mapper)
                
                mc_data = {
                    'x': block.x,
                    'y': block.y,
                    'z': block.z,
                    'blockId': block.block_id,
                    'blockData': block.block_data,
                }
                
                return Packet(
                    packet_type=PacketType.MC_PLAY,
                    sub_type=0x0B,  # Block Change
                    seq_id=self._get_next_seq(direction),
                    data=json.dumps(mc_data).encode('utf-8')
                )
            else:
                # MC -> MNW
                mc_block = json.loads(packet.data.decode('utf-8'))
                block = BlockUpdate(
                    x=mc_block.get('x', 0),
                    y=mc_block.get('y', 0),
                    z=mc_block.get('z', 0),
                    block_id=mc_block.get('blockId', 0),
                    block_data=mc_block.get('blockData', 0),
                )
                
                return Packet(
                    packet_type=PacketType.MNW_BLOCK,
                    sub_type=0x01,  # Block Update
                    seq_id=self._get_next_seq(direction),
                    data=json.dumps(block.to_mnw(self.block_mapper)).encode('utf-8')
                )
        except Exception as e:
            logger.error(f"方块翻译失败: {e}")
            return self._default_translate(packet, direction)
    
    def _translate_chat(self, packet: Packet, direction: str) -> Packet:
        """翻译聊天消息"""
        try:
            data = json.loads(packet.data.decode('utf-8'))
            
            if direction == 'mnw_to_mc':
                # 转换聊天格式
                mc_data = {
                    'message': data.get('msg', ''),
                    'sender': data.get('from', ''),
                }
                
                return Packet(
                    packet_type=PacketType.MC_PLAY,
                    sub_type=0x0F,  # Chat Message
                    seq_id=self._get_next_seq(direction),
                    data=json.dumps(mc_data).encode('utf-8')
                )
            else:
                mnw_data = {
                    'msg': data.get('message', ''),
                    'from': data.get('sender', ''),
                }
                
                return Packet(
                    packet_type=PacketType.MNW_CHAT,
                    sub_type=0x01,
                    seq_id=self._get_next_seq(direction),
                    data=json.dumps(mnw_data).encode('utf-8')
                )
        except Exception as e:
            logger.error(f"聊天翻译失败: {e}")
            return self._default_translate(packet, direction)
    
    def _translate_login(self, packet: Packet, direction: str) -> Packet:
        """翻译登录数据包"""
        # 登录包通常需要特殊处理
        # 这里仅做简单转发
        return self._default_translate(packet, direction)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'packets_translated': 0,
            'bytes_translated': 0,
            'errors': 0,
        }


# 便捷函数
def create_translator(mapping_file: str = None) -> PacketTranslator:
    """创建协议翻译器"""
    block_mapper = BlockMapper(mapping_file)
    return PacketTranslator(block_mapper)


__all__ = [
    'PacketTranslator',
    'Packet',
    'PacketType',
    'PlayerPosition',
    'BlockUpdate',
    'create_translator',
]
