#!/usr/bin/env python3
"""
协议翻译器
负责Minecraft协议和迷你世界协议之间的转换
"""

import struct
import json
import logging
from typing import Dict, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enum import IntEnum, Enum
from io import BytesIO

from codec.mc_codec import MinecraftCodec, encode_varint, decode_varint, encode_string, decode_string
from codec.mnw_codec import MiniWorldCodec, MNWPacket
from protocol.block_mapper import BlockMapper
from protocol.coordinate_converter import CoordinateConverter, Vector3
from crypto.aes_crypto import MiniWorldEncryption

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """连接状态"""
    HANDSHAKE = "handshake"
    STATUS = "status"
    LOGIN = "login"
    PLAY = "play"
    DISCONNECTED = "disconnected"


class PacketType(IntEnum):
    """数据包类型"""
    # Minecraft 协议包类型
    MC_HANDSHAKE = 0x00
    MC_STATUS_REQUEST = 0x00
    MC_STATUS_RESPONSE = 0x00
    MC_LOGIN_START = 0x00
    MC_LOGIN_SUCCESS = 0x02
    MC_KEEP_ALIVE = 0x24
    MC_CHAT_MESSAGE = 0x05
    MC_PLAYER_POSITION = 0x1A
    MC_BLOCK_CHANGE = 0x09
    
    # 迷你世界协议包类型
    MNW_LOGIN = 0x01
    MNW_GAME = 0x02
    MNW_CHAT = 0x03
    MNW_MOVE = 0x04
    MNW_BLOCK = 0x05
    MNW_ROOM = 0x10
    MNW_HEARTBEAT = 0xFF


@dataclass
class TranslationContext:
    """翻译上下文"""
    mc_username: str = ""
    mc_uuid: str = ""
    mnw_account_id: str = ""
    mnw_token: str = ""
    room_id: str = ""
    state: ConnectionState = ConnectionState.HANDSHAKE
    compression_enabled: bool = False
    encryption_enabled: bool = False


class ProtocolTranslator:
    """
    协议翻译器
    实现Minecraft和迷你世界协议之间的双向翻译
    """
    
    def __init__(self, region: str = "CN"):
        self.mc_codec = MinecraftCodec()
        self.mnw_codec = MiniWorldCodec()
        self.block_mapper = BlockMapper()
        self.coord_converter = CoordinateConverter()
        self.encryption = MiniWorldEncryption(region=region)
        
        # 翻译上下文
        self.context = TranslationContext()
        
        # 统计
        self.packets_translated = 0
        self.errors = 0
        
        logger.info("协议翻译器初始化完成")
    
    def mc_to_mnw(self, mc_packet: bytes) -> Optional[bytes]:
        """
        将Minecraft数据包翻译为迷你世界数据包
        
        Args:
            mc_packet: Minecraft原始数据包
            
        Returns:
            迷你世界数据包或None
        """
        try:
            # 解析Minecraft数据包
            packet = self.mc_codec.decode_packet(mc_packet)
            if not packet:
                return None
            
            # 根据包ID进行翻译
            if packet.packet_id == PacketType.MC_HANDSHAKE:
                return self._translate_handshake(packet.data)
            elif packet.packet_id == PacketType.MC_LOGIN_START:
                return self._translate_login_start(packet.data)
            elif packet.packet_id == PacketType.MC_CHAT_MESSAGE:
                return self._translate_chat_message(packet.data)
            elif packet.packet_id == PacketType.MC_PLAYER_POSITION:
                return self._translate_player_position(packet.data)
            elif packet.packet_id == PacketType.MC_BLOCK_CHANGE:
                return self._translate_block_change(packet.data)
            else:
                # 未实现的包类型，记录日志
                logger.debug(f"未实现的MC包类型: 0x{packet.packet_id:02X}")
                return None
                
        except Exception as e:
            logger.error(f"MC→MNW翻译失败: {e}")
            self.errors += 1
            return None
    
    def mnw_to_mc(self, mnw_packet: bytes) -> Optional[bytes]:
        """
        将迷你世界数据包翻译为Minecraft数据包
        
        Args:
            mnw_packet: 迷你世界原始数据包
            
        Returns:
            Minecraft数据包或None
        """
        try:
            # 解密（如果需要）
            if self.context.encryption_enabled:
                mnw_packet = self.encryption.decrypt(mnw_packet)
            
            # 解析迷你世界数据包
            packet = self.mnw_codec.decode_packet(mnw_packet, decrypt=False)
            if not packet:
                return None
            
            # 根据包类型进行翻译
            if packet.packet_type == PacketType.MNW_LOGIN:
                return self._translate_mnw_login(packet)
            elif packet.packet_type == PacketType.MNW_CHAT:
                return self._translate_mnw_chat(packet)
            elif packet.packet_type == PacketType.MNW_MOVE:
                return self._translate_mnw_move(packet)
            elif packet.packet_type == PacketType.MNW_BLOCK:
                return self._translate_mnw_block(packet)
            else:
                logger.debug(f"未实现的MNW包类型: 0x{packet.packet_type:02X}")
                return None
                
        except Exception as e:
            logger.error(f"MNW→MC翻译失败: {e}")
            self.errors += 1
            return None
    
    def _translate_handshake(self, data: bytes) -> Optional[bytes]:
        """翻译握手包"""
        try:
            stream = BytesIO(data)
            protocol_version = decode_varint(stream)
            server_address = decode_string(stream)
            
            # 检查是否有足够的数据读取端口
            port_data = stream.read(2)
            if len(port_data) < 2:
                logger.warning("握手包数据不完整，缺少端口")
                return None
            
            server_port = struct.unpack('>H', port_data)[0]
            next_state = decode_varint(stream)
            
            logger.info(f"握手: 协议={protocol_version}, 地址={server_address}:{server_port}, 状态={next_state}")
            
            # 更新上下文状态
            if next_state == 1:
                self.context.state = ConnectionState.STATUS
            elif next_state == 2:
                self.context.state = ConnectionState.LOGIN
            
            # 握手包不需要转发到迷你世界，直接返回空
            return None
            
        except Exception as e:
            logger.error(f"翻译握手包失败: {e}")
            return None
    
    def _translate_login_start(self, data: bytes) -> Optional[bytes]:
        """翻译登录开始包"""
        try:
            stream = BytesIO(data)
            username = decode_string(stream)
            
            logger.info(f"MC登录: 用户名={username}")
            self.context.mc_username = username
            
            # TODO: 从账户映射表获取迷你号
            # 暂时使用用户名作为迷你号
            self.context.mnw_account_id = username
            
            # 创建迷你世界登录请求
            mnw_login = self.mnw_codec.create_login_request(
                account_id=self.context.mnw_account_id,
                token="temp_token",  # TODO: 实现真实Token获取
                version="1.53.1"
            )
            
            self.packets_translated += 1
            return mnw_login
            
        except Exception as e:
            logger.error(f"翻译登录包失败: {e}")
            return None
    
    def _translate_chat_message(self, data: bytes) -> Optional[bytes]:
        """翻译聊天消息包"""
        try:
            stream = BytesIO(data)
            message = decode_string(stream)
            
            logger.info(f"MC聊天: {message}")
            
            # 转换为迷你世界聊天包
            mnw_chat = self.mnw_codec.create_chat_message(
                message=message,
                room_id=self.context.room_id
            )
            
            self.packets_translated += 1
            return mnw_chat
            
        except Exception as e:
            logger.error(f"翻译聊天包失败: {e}")
            return None
    
    def _translate_player_position(self, data: bytes) -> Optional[bytes]:
        """翻译玩家位置包"""
        try:
            # Minecraft位置格式: X(double), Y(double), Z(double), yaw(float), pitch(float), on_ground(bool)
            if len(data) < 25:
                return None
            
            x = struct.unpack('>d', data[0:8])[0]
            y = struct.unpack('>d', data[8:16])[0]
            z = struct.unpack('>d', data[16:24])[0]
            
            # 坐标转换（X轴取反）
            mc_pos = Vector3(x, y, z)
            mnw_pos = self.coord_converter.mc_to_mnw_position(mc_pos)
            
            logger.debug(f"位置: MC({x:.2f}, {y:.2f}, {z:.2f}) -> MNW({mnw_pos.x:.2f}, {mnw_pos.y:.2f}, {mnw_pos.z:.2f})")
            
            # 创建迷你世界移动包
            mnw_move = self.mnw_codec.create_move_packet(
                x=mnw_pos.x,
                y=mnw_pos.y,
                z=mnw_pos.z
            )
            
            self.packets_translated += 1
            return mnw_move
            
        except Exception as e:
            logger.error(f"翻译位置包失败: {e}")
            return None
    
    def _translate_block_change(self, data: bytes) -> Optional[bytes]:
        """翻译方块变更包"""
        try:
            # 简化处理，实际需要解析完整格式
            # TODO: 实现完整的方块变更解析
            logger.debug("方块变更包翻译（待实现）")
            return None
            
        except Exception as e:
            logger.error(f"翻译方块包失败: {e}")
            return None
    
    def _translate_mnw_login(self, packet: MNWPacket) -> Optional[bytes]:
        """翻译迷你世界登录响应"""
        try:
            response = self.mnw_codec.parse_login_response(packet.data)
            
            if response.get("success"):
                logger.info(f"MNW登录成功: {response.get('nickname', 'Unknown')}")
                self.context.state = ConnectionState.PLAY
                
                # 创建MC登录成功包
                # TODO: 实现完整的登录成功包
                return None
            else:
                logger.error(f"MNW登录失败: {response.get('error', 'Unknown')}")
                return None
                
        except Exception as e:
            logger.error(f"翻译MNW登录包失败: {e}")
            return None
    
    def _translate_mnw_chat(self, packet: MNWPacket) -> Optional[bytes]:
        """翻译迷你世界聊天消息"""
        try:
            chat_data = self.mnw_codec.parse_chat_message(packet.data)
            message = chat_data.get("message", "")
            
            logger.info(f"MNW聊天: {message}")
            
            # 创建MC聊天包
            mc_chat = self.mc_codec.create_chat_message(message)
            
            self.packets_translated += 1
            return mc_chat
            
        except Exception as e:
            logger.error(f"翻译MNW聊天包失败: {e}")
            return None
    
    def _translate_mnw_move(self, packet: MNWPacket) -> Optional[bytes]:
        """翻译迷你世界移动数据"""
        try:
            move_data = self.mnw_codec.parse_move_data(packet.data)
            
            x = move_data.get("x", 0)
            y = move_data.get("y", 0)
            z = move_data.get("z", 0)
            
            # 坐标转换（X轴取反）
            mnw_pos = Vector3(x, y, z)
            mc_pos = self.coord_converter.mnw_to_mc_position(mnw_pos)
            
            logger.debug(f"移动: MNW({x:.2f}, {y:.2f}, {z:.2f}) -> MC({mc_pos.x:.2f}, {mc_pos.y:.2f}, {mc_pos.z:.2f})")
            
            # TODO: 创建MC位置更新包
            return None
            
        except Exception as e:
            logger.error(f"翻译MNW移动包失败: {e}")
            return None
    
    def _translate_mnw_block(self, packet: MNWPacket) -> Optional[bytes]:
        """翻译迷你世界方块操作"""
        try:
            block_data = self.mnw_codec.parse_block_data(packet.data)
            
            x = block_data.get("x", 0)
            y = block_data.get("y", 0)
            z = block_data.get("z", 0)
            block_id = block_data.get("block_id", 0)
            
            # 方块ID映射
            mc_block_id = self.block_mapper.mnw_to_mc_block(block_id)
            
            logger.debug(f"方块: MNW({x}, {y}, {z}) ID={block_id} -> MC ID={mc_block_id}")
            
            # TODO: 创建MC方块变更包
            return None
            
        except Exception as e:
            logger.error(f"翻译MNW方块包失败: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取翻译统计"""
        return {
            "packets_translated": self.packets_translated,
            "errors": self.errors,
            "state": self.context.state.value,
            "mc_username": self.context.mc_username,
            "mnw_account_id": self.context.mnw_account_id
        }
