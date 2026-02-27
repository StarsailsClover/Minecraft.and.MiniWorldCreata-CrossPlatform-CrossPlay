#!/usr/bin/env python3
"""
MiniWorld 协议编解码器
处理迷你世界协议的数据包编码和解码

基于抓包分析结果实现
"""

import struct
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from io import BytesIO
import json

logger = logging.getLogger(__name__)


@dataclass
class MNWPacket:
    """迷你世界数据包"""
    packet_type: int
    sub_type: int
    data: bytes
    seq_id: int = 0
    
    def encode(self) -> bytes:
        """编码数据包"""
        # 迷你世界协议格式（推测）:
        # [魔数/头部] [包类型] [子类型] [序列号] [长度] [数据] [校验]
        header = struct.pack('>BBH', self.packet_type, self.sub_type, self.seq_id)
        length = struct.pack('>I', len(self.data))
        
        # TODO: 添加校验和
        checksum = b'\x00\x00\x00\x00'  # 占位
        
        return header + length + self.data + checksum
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['MNWPacket']:
        """解码数据包"""
        try:
            if len(data) < 8:
                return None
            
            stream = BytesIO(data)
            
            # 读取头部
            packet_type = struct.unpack('B', stream.read(1))[0]
            sub_type = struct.unpack('B', stream.read(1))[0]
            seq_id = struct.unpack('>H', stream.read(2))[0]
            
            # 读取长度
            length = struct.unpack('>I', stream.read(4))[0]
            
            # 读取数据
            packet_data = stream.read(length)
            
            # TODO: 验证校验和
            
            return cls(
                packet_type=packet_type,
                sub_type=sub_type,
                seq_id=seq_id,
                data=packet_data
            )
        except Exception as e:
            logger.error(f"解码迷你世界数据包失败: {e}")
            return None


class MiniWorldCodec:
    """迷你世界协议编解码器"""
    
    # 数据包类型（基于抓包分析）
    PACKET_LOGIN = 0x01       # 登录认证
    PACKET_GAME = 0x02        # 游戏数据
    PACKET_CHAT = 0x03        # 聊天消息
    PACKET_MOVE = 0x04        # 移动同步
    PACKET_BLOCK = 0x05       # 方块操作
    PACKET_ROOM = 0x10        # 房间管理
    PACKET_HEARTBEAT = 0xFF   # 心跳包
    
    # 子类型
    SUB_LOGIN_REQUEST = 0x01
    SUB_LOGIN_RESPONSE = 0x02
    SUB_GAME_START = 0x01
    SUB_GAME_ACTION = 0x02
    SUB_CHAT_MESSAGE = 0x01
    SUB_MOVE_POSITION = 0x01
    SUB_MOVE_ROTATION = 0x02
    SUB_BLOCK_PLACE = 0x01
    SUB_BLOCK_BREAK = 0x02
    SUB_ROOM_CREATE = 0x01
    SUB_ROOM_JOIN = 0x02
    SUB_ROOM_LEAVE = 0x03
    
    def __init__(self):
        self.seq_id = 0
        self.encryption_enabled = True
        
    def _get_next_seq_id(self) -> int:
        """获取下一个序列号"""
        self.seq_id = (self.seq_id + 1) % 65536
        return self.seq_id
    
    def encode_packet(self, packet_type: int, sub_type: int, 
                     data: bytes, encrypt: bool = True) -> bytes:
        """
        编码数据包
        
        Args:
            packet_type: 数据包类型
            sub_type: 子类型
            data: 包数据
            encrypt: 是否加密
            
        Returns:
            编码后的字节数据
        """
        packet = MNWPacket(
            packet_type=packet_type,
            sub_type=sub_type,
            seq_id=self._get_next_seq_id(),
            data=data
        )
        
        encoded = packet.encode()
        
        # 如果需要加密
        if encrypt and self.encryption_enabled:
            encoded = self._encrypt(encoded)
        
        return encoded
    
    def decode_packet(self, data: bytes, decrypt: bool = True) -> Optional[MNWPacket]:
        """
        解码数据包
        
        Args:
            data: 原始字节数据
            decrypt: 是否解密
            
        Returns:
            MNWPacket对象或None
        """
        # 如果需要解密
        if decrypt and self.encryption_enabled:
            try:
                data = self._decrypt(data)
            except Exception as e:
                logger.error(f"解密失败: {e}")
                return None
        
        return MNWPacket.decode(data)
    
    def _encrypt(self, data: bytes) -> bytes:
        """
        加密数据
        
        TODO: 实现AES加密（国服AES-128-CBC，外服AES-256-GCM）
        """
        # 暂时返回明文
        return data
    
    def _decrypt(self, data: bytes) -> bytes:
        """
        解密数据
        
        TODO: 实现AES解密
        """
        # 暂时返回明文
        return data
    
    def create_login_request(self, account_id: str, token: str, 
                            version: str = "1.53.1") -> bytes:
        """
        创建登录请求包
        
        Args:
            account_id: 迷你号
            token: 登录Token
            version: 客户端版本
            
        Returns:
            编码后的登录请求包
        """
        login_data = {
            "account_id": account_id,
            "token": token,
            "version": version,
            "platform": "android",
            "device_id": f"MN-{account_id}"
        }
        
        data = json.dumps(login_data).encode('utf-8')
        return self.encode_packet(
            self.PACKET_LOGIN,
            self.SUB_LOGIN_REQUEST,
            data
        )
    
    def create_heartbeat(self) -> bytes:
        """
        创建心跳包
        
        Returns:
            编码后的心跳包
        """
        # 心跳包通常只包含时间戳
        timestamp = struct.pack('>Q', int(__import__('time').time() * 1000))
        return self.encode_packet(
            self.PACKET_HEARTBEAT,
            0x00,
            timestamp
        )
    
    def create_chat_message(self, message: str, room_id: str = "") -> bytes:
        """
        创建聊天消息包
        
        Args:
            message: 聊天消息
            room_id: 房间ID
            
        Returns:
            编码后的聊天包
        """
        chat_data = {
            "message": message,
            "room_id": room_id,
            "timestamp": int(__import__('time').time())
        }
        
        data = json.dumps(chat_data).encode('utf-8')
        return self.encode_packet(
            self.PACKET_CHAT,
            self.SUB_CHAT_MESSAGE,
            data
        )
    
    def create_move_packet(self, x: float, y: float, z: float,
                          yaw: float = 0.0, pitch: float = 0.0) -> bytes:
        """
        创建移动包
        
        Args:
            x, y, z: 坐标
            yaw: 水平旋转角度
            pitch: 垂直旋转角度
            
        Returns:
            编码后的移动包
        """
        # 位置数据
        pos_data = struct.pack('>fff', x, y, z)
        
        # 旋转数据
        rot_data = struct.pack('>ff', yaw, pitch)
        
        return self.encode_packet(
            self.PACKET_MOVE,
            self.SUB_MOVE_POSITION,
            pos_data + rot_data
        )
    
    def create_block_place(self, x: int, y: int, z: int, 
                          block_id: int, meta: int = 0) -> bytes:
        """
        创建方块放置包
        
        Args:
            x, y, z: 方块坐标
            block_id: 方块ID
            meta: 方块元数据
            
        Returns:
            编码后的方块放置包
        """
        # 坐标和方块数据
        block_data = struct.pack('>iiihh', x, y, z, block_id, meta)
        
        return self.encode_packet(
            self.PACKET_BLOCK,
            self.SUB_BLOCK_PLACE,
            block_data
        )
    
    def create_block_break(self, x: int, y: int, z: int) -> bytes:
        """
        创建方块破坏包
        
        Args:
            x, y, z: 方块坐标
            
        Returns:
            编码后的方块破坏包
        """
        # 坐标数据
        coord_data = struct.pack('>iii', x, y, z)
        
        return self.encode_packet(
            self.PACKET_BLOCK,
            self.SUB_BLOCK_BREAK,
            coord_data
        )
    
    def create_room_join(self, room_id: str, password: str = "") -> bytes:
        """
        创建加入房间包
        
        Args:
            room_id: 房间ID
            password: 房间密码
            
        Returns:
            编码后的加入房间包
        """
        room_data = {
            "room_id": room_id,
            "password": password
        }
        
        data = json.dumps(room_data).encode('utf-8')
        return self.encode_packet(
            self.PACKET_ROOM,
            self.SUB_ROOM_JOIN,
            data
        )
    
    def parse_login_response(self, data: bytes) -> Dict[str, Any]:
        """
        解析登录响应
        
        Args:
            data: 响应数据
            
        Returns:
            解析后的字典
        """
        try:
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            logger.error(f"解析登录响应失败: {e}")
            return {}
    
    def parse_chat_message(self, data: bytes) -> Dict[str, Any]:
        """
        解析聊天消息
        
        Args:
            data: 消息数据
            
        Returns:
            解析后的字典
        """
        try:
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            logger.error(f"解析聊天消息失败: {e}")
            return {}
    
    def parse_move_data(self, data: bytes) -> Dict[str, float]:
        """
        解析移动数据
        
        Args:
            data: 移动数据
            
        Returns:
            包含坐标和旋转的字典
        """
        try:
            if len(data) >= 12:
                x, y, z = struct.unpack('>fff', data[:12])
                result = {"x": x, "y": y, "z": z}
                
                if len(data) >= 20:
                    yaw, pitch = struct.unpack('>ff', data[12:20])
                    result["yaw"] = yaw
                    result["pitch"] = pitch
                
                return result
        except Exception as e:
            logger.error(f"解析移动数据失败: {e}")
        
        return {}
    
    def parse_block_data(self, data: bytes) -> Dict[str, Any]:
        """
        解析方块数据
        
        Args:
            data: 方块数据
            
        Returns:
            包含方块信息的字典
        """
        try:
            if len(data) >= 14:
                x, y, z, block_id, meta = struct.unpack('>iiihh', data[:14])
                return {
                    "x": x,
                    "y": y,
                    "z": z,
                    "block_id": block_id,
                    "meta": meta
                }
        except Exception as e:
            logger.error(f"解析方块数据失败: {e}")
        
        return {}
