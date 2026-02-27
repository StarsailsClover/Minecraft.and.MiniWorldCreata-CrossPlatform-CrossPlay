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
        """
        翻译方块变更包
        
        Minecraft方块变更包格式:
        - Position: X(int), Y(int), Z(int) - 打包为Long
        - Block ID: VarInt
        """
        try:
            stream = BytesIO(data)
            
            # 读取位置（打包为Long）
            position = decode_varint(stream)
            
            # 解码位置
            x = (position >> 38) & 0x3FFFFFF
            y = (position >> 26) & 0xFFF
            z = position & 0x3FFFFFF
            
            # 处理有符号数
            if x >= 2**25:
                x -= 2**26
            if y >= 2**11:
                y -= 2**12
            if z >= 2**25:
                z -= 2**26
            
            # 读取方块ID
            block_id = decode_varint(stream)
            
            logger.debug(f"MC方块变更: ({x}, {y}, {z}) ID={block_id}")
            
            # 方块ID映射
            mnw_block_id, _ = self.block_mapper.mc_to_mnw_block(block_id)
            
            # 坐标转换（X轴取反）
            mc_pos = Vector3(float(x), float(y), float(z))
            mnw_pos = self.coord_converter.mc_to_mnw_position(mc_pos)
            
            # 创建迷你世界方块放置包
            mnw_block = self.mnw_codec.create_block_place(
                x=int(mnw_pos.x),
                y=int(mnw_pos.y),
                z=int(mnw_pos.z),
                block_id=mnw_block_id
            )
            
            self.packets_translated += 1
            return mnw_block
            
        except Exception as e:
            logger.error(f"翻译方块包失败: {e}")
            return None
    
    def _translate_player_digging(self, data: bytes) -> Optional[bytes]:
        """
        翻译玩家挖掘包（方块破坏）
        
        Minecraft挖掘包格式:
        - Status: Byte (0=start, 1=cancel, 2=finish)
        - Position: Long (打包的X,Y,Z)
        - Face: Byte
        """
        try:
            stream = BytesIO(data)
            
            # 读取状态
            status = struct.unpack('B', stream.read(1))[0]
            
            # 读取位置
            position = decode_varint(stream)
            x = (position >> 38) & 0x3FFFFFF
            y = (position >> 26) & 0xFFF
            z = position & 0x3FFFFFF
            
            if x >= 2**25:
                x -= 2**26
            if y >= 2**11:
                y -= 2**12
            if z >= 2**25:
                z -= 2**26
            
            # 读取面
            face = struct.unpack('B', stream.read(1))[0]
            
            logger.debug(f"MC挖掘: ({x}, {y}, {z}) 状态={status} 面={face}")
            
            # 只处理完成挖掘（status=2）
            if status != 2:
                return None
            
            # 坐标转换
            mc_pos = Vector3(float(x), float(y), float(z))
            mnw_pos = self.coord_converter.mc_to_mnw_position(mc_pos)
            
            # 创建迷你世界方块破坏包
            mnw_break = self.mnw_codec.create_block_break(
                x=int(mnw_pos.x),
                y=int(mnw_pos.y),
                z=int(mnw_pos.z)
            )
            
            self.packets_translated += 1
            return mnw_break
            
        except Exception as e:
            logger.error(f"翻译挖掘包失败: {e}")
            return None
    
    def _translate_player_block_placement(self, data: bytes) -> Optional[bytes]:
        """
        翻译玩家方块放置包
        
        Minecraft放置包格式:
        - Hand: VarInt
        - Position: Long (打包的X,Y,Z)
        - Face: VarInt
        - Cursor X/Y/Z: Float
        - Inside block: Boolean
        """
        try:
            stream = BytesIO(data)
            
            # 读取手
            hand = decode_varint(stream)
            
            # 读取位置
            position = decode_varint(stream)
            x = (position >> 38) & 0x3FFFFFF
            y = (position >> 26) & 0xFFF
            z = position & 0x3FFFFFF
            
            if x >= 2**25:
                x -= 2**26
            if y >= 2**11:
                y -= 2**12
            if z >= 2**25:
                z -= 2**26
            
            # 读取面
            face = decode_varint(stream)
            
            logger.debug(f"MC放置: ({x}, {y}, {z}) 手={hand} 面={face}")
            
            # 坐标转换
            mc_pos = Vector3(float(x), float(y), float(z))
            mnw_pos = self.coord_converter.mc_to_mnw_position(mc_pos)
            
            # TODO: 获取玩家手中的方块ID
            # 暂时使用石头（ID=1）
            block_id = 1
            mnw_block_id, _ = self.block_mapper.mc_to_mnw_block(block_id)
            
            # 创建迷你世界方块放置包
            mnw_place = self.mnw_codec.create_block_place(
                x=int(mnw_pos.x),
                y=int(mnw_pos.y),
                z=int(mnw_pos.z),
                block_id=mnw_block_id
            )
            
            self.packets_translated += 1
            return mnw_place
            
        except Exception as e:
            logger.error(f"翻译放置包失败: {e}")
            return None
    
    def create_mc_login_success(self, username: str, uuid_str: str) -> bytes:
        """
        创建Minecraft登录成功包
        
        Args:
            username: 用户名
            uuid_str: UUID字符串
            
        Returns:
            编码后的登录成功包
        """
        try:
            from codec.mc_codec import encode_string
            import uuid
            
            data = BytesIO()
            
            # UUID
            uuid_bytes = uuid.UUID(uuid_str).bytes
            data.write(uuid_bytes)
            
            # 用户名
            data.write(encode_string(username))
            
            # 属性数量（0）
            data.write(encode_varint(0))
            
            return self.mc_codec.encode_packet(PacketType.MC_LOGIN_SUCCESS, data.getvalue())
            
        except Exception as e:
            logger.error(f"创建登录成功包失败: {e}")
            return b''
    
    def create_mc_keep_alive(self, keep_alive_id: int) -> bytes:
        """创建Minecraft心跳包"""
        return self.mc_codec.create_keep_alive(keep_alive_id)
    
    def create_mc_chat_message(self, message: str) -> bytes:
        """创建Minecraft聊天消息包"""
        return self.mc_codec.create_chat_message(message)
    
    def create_mc_player_position(self, x: float, y: float, z: float, 
                                  yaw: float = 0.0, pitch: float = 0.0,
                                  on_ground: bool = True) -> bytes:
        """
        创建Minecraft玩家位置包
        
        Args:
            x, y, z: 坐标
            yaw: 水平旋转
            pitch: 垂直旋转
            on_ground: 是否在地面上
            
        Returns:
            编码后的位置包
        """
        try:
            data = BytesIO()
            data.write(struct.pack('>d', x))
            data.write(struct.pack('>d', y))
            data.write(struct.pack('>d', z))
            data.write(struct.pack('>f', yaw))
            data.write(struct.pack('>f', pitch))
            data.write(struct.pack('>?', on_ground))
            
            return self.mc_codec.encode_packet(PacketType.MC_PLAYER_POSITION, data.getvalue())
            
        except Exception as e:
            logger.error(f"创建位置包失败: {e}")
            return b''
    
    def create_mc_block_change(self, x: int, y: int, z: int, block_id: int) -> bytes:
        """
        创建Minecraft方块变更包
        
        Args:
            x, y, z: 坐标
            block_id: 方块ID
            
        Returns:
            编码后的方块变更包
        """
        try:
            # 打包位置
            position = ((x & 0x3FFFFFF) << 38) | ((y & 0xFFF) << 26) | (z & 0x3FFFFFF)
            
            data = BytesIO()
            data.write(encode_varint(position))
            data.write(encode_varint(block_id))
            
            return self.mc_codec.encode_packet(PacketType.MC_BLOCK_CHANGE, data.getvalue())
            
        except Exception as e:
            logger.error(f"创建方块变更包失败: {e}")
            return b''
    
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
            yaw = move_data.get("yaw", 0.0)
            pitch = move_data.get("pitch", 0.0)
            
            # 坐标转换（X轴取反）
            mnw_pos = Vector3(x, y, z)
            mc_pos = self.coord_converter.mnw_to_mc_position(mnw_pos)
            
            logger.debug(f"移动: MNW({x:.2f}, {y:.2f}, {z:.2f}) -> MC({mc_pos.x:.2f}, {mc_pos.y:.2f}, {mc_pos.z:.2f})")
            
            # 创建MC位置更新包
            mc_position = self.create_mc_player_position(
                x=mc_pos.x,
                y=mc_pos.y,
                z=mc_pos.z,
                yaw=yaw,
                pitch=pitch
            )
            
            self.packets_translated += 1
            return mc_position
            
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
            mc_block_id, _ = self.block_mapper.mnw_to_mc_block(block_id)
            
            # 坐标转换
            mnw_pos = Vector3(float(x), float(y), float(z))
            mc_pos = self.coord_converter.mnw_to_mc_position(mnw_pos)
            
            logger.debug(f"方块: MNW({x}, {y}, {z}) ID={block_id} -> MC({int(mc_pos.x)}, {int(mc_pos.y)}, {int(mc_pos.z)}) ID={mc_block_id}")
            
            # 创建MC方块变更包
            mc_block = self.create_mc_block_change(
                x=int(mc_pos.x),
                y=int(mc_pos.y),
                z=int(mc_pos.z),
                block_id=mc_block_id
            )
            
            self.packets_translated += 1
            return mc_block
            
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
