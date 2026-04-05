"""
业务协议层

迷你世界业务消息处理
"""

import struct
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import IntEnum

logger = logging.getLogger(__name__)


class BusinessCmdID(IntEnum):
    """业务命令 ID (从逆向分析获取)"""
    # 登录相关
    LOGIN_REQ = 0x7D3
    LOGIN_RESP = 0x7D4
    
    # 房间相关
    ROOM_CREATE = 0x7D5
    ROOM_JOIN = 0x7D6
    ROOM_LEAVE = 0x7D7
    ROOM_LIST = 0x7D8
    
    # 玩家相关
    PLAYER_ENTER = 0x7F2  # PROTO_2034 - 角色进入世界
    PLAYER_LEAVE = 0x7F3
    PLAYER_MOVE = 0x7E0
    PLAYER_ACTION = 0x7E1
    
    # 聊天相关
    CHAT_MESSAGE = 0x7EA
    CHAT_BROADCAST = 0x7EB
    
    # 方块相关
    BLOCK_PLACE = 0x7E5
    BLOCK_BREAK = 0x7E6
    BLOCK_UPDATE = 0x7E7
    
    # 心跳
    HEARTBEAT = 0x7ED


@dataclass
class BusinessMessage:
    """业务消息"""
    cmd_id: int
    uin: int
    data: bytes
    target_uin: Optional[int] = None
    seq: int = 0
    
    def encode(self) -> bytes:
        """编码消息"""
        # 简化编码：cmd_id (2) + uin (4) + seq (4) + data_len (4) + data
        header = struct.pack('>HII', self.cmd_id, self.uin, self.seq)
        data_len = len(self.data)
        return header + struct.pack('>I', data_len) + self.data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['BusinessMessage']:
        """解码消息"""
        if len(data) < 10:
            return None
        
        try:
            cmd_id, uin, seq = struct.unpack('>HII', data[:10])
            data_len = struct.unpack('>I', data[10:14])[0]
            payload = data[14:14+data_len]
            
            return cls(
                cmd_id=cmd_id,
                uin=uin,
                data=payload,
                seq=seq
            )
        except Exception as e:
            logger.error(f"Decode error: {e}")
            return None


class BusinessProtocol:
    """业务协议处理器"""
    
    def __init__(self):
        self.cmd_handlers: Dict[int, callable] = {}
        self.seq = 0
        self._register_handlers()
    
    def _register_handlers(self):
        """注册命令处理器"""
        self.cmd_handlers[BusinessCmdID.LOGIN_REQ] = self._handle_login_req
        self.cmd_handlers[BusinessCmdID.LOGIN_RESP] = self._handle_login_resp
        self.cmd_handlers[BusinessCmdID.PLAYER_ENTER] = self._handle_player_enter
        self.cmd_handlers[BusinessCmdID.PLAYER_MOVE] = self._handle_player_move
        self.cmd_handlers[BusinessCmdID.CHAT_MESSAGE] = self._handle_chat_message
        self.cmd_handlers[BusinessCmdID.HEARTBEAT] = self._handle_heartbeat
    
    def create_login_request(self, username: str, password: str) -> BusinessMessage:
        """创建登录请求"""
        # 简化：直接发送用户名密码（实际需要加密）
        data = f"{username}:{password}".encode('utf-8')
        self.seq += 1
        return BusinessMessage(
            cmd_id=BusinessCmdID.LOGIN_REQ,
            uin=0,  # 登录前 UIN 为 0
            data=data,
            seq=self.seq
        )
    
    def create_player_enter(self, uin: int, world_id: str) -> BusinessMessage:
        """创建玩家进入世界消息"""
        data = world_id.encode('utf-8')
        self.seq += 1
        return BusinessMessage(
            cmd_id=BusinessCmdID.PLAYER_ENTER,
            uin=uin,
            data=data,
            seq=self.seq
        )
    
    def create_player_move(self, uin: int, x: float, y: float, z: float) -> BusinessMessage:
        """创建玩家移动消息"""
        data = struct.pack('>fff', x, y, z)
        self.seq += 1
        return BusinessMessage(
            cmd_id=BusinessCmdID.PLAYER_MOVE,
            uin=uin,
            data=data,
            seq=self.seq
        )
    
    def create_chat_message(self, uin: int, message: str) -> BusinessMessage:
        """创建聊天消息"""
        data = message.encode('utf-8')
        self.seq += 1
        return BusinessMessage(
            cmd_id=BusinessCmdID.CHAT_MESSAGE,
            uin=uin,
            data=data,
            seq=self.seq
        )
    
    def create_heartbeat(self, uin: int) -> BusinessMessage:
        """创建心跳消息"""
        self.seq += 1
        return BusinessMessage(
            cmd_id=BusinessCmdID.HEARTBEAT,
            uin=uin,
            data=b'',
            seq=self.seq
        )
    
    def handle_message(self, msg: BusinessMessage) -> Optional[Any]:
        """处理消息"""
        handler = self.cmd_handlers.get(msg.cmd_id)
        if handler:
            return handler(msg)
        else:
            logger.warning(f"No handler for cmd_id: 0x{msg.cmd_id:04X}")
            return None
    
    def _handle_login_req(self, msg: BusinessMessage):
        """处理登录请求"""
        logger.info(f"Login request: UIN={msg.uin}")
        return {"type": "login_req", "uin": msg.uin}
    
    def _handle_login_resp(self, msg: BusinessMessage):
        """处理登录响应"""
        logger.info(f"Login response: UIN={msg.uin}")
        return {"type": "login_resp", "uin": msg.uin}
    
    def _handle_player_enter(self, msg: BusinessMessage):
        """处理玩家进入"""
        world_id = msg.data.decode('utf-8')
        logger.info(f"Player enter: UIN={msg.uin}, World={world_id}")
        return {"type": "player_enter", "uin": msg.uin, "world": world_id}
    
    def _handle_player_move(self, msg: BusinessMessage):
        """处理玩家移动"""
        if len(msg.data) >= 12:
            x, y, z = struct.unpack('>fff', msg.data[:12])
            logger.info(f"Player move: UIN={msg.uin}, Pos=({x}, {y}, {z})")
            return {"type": "player_move", "uin": msg.uin, "x": x, "y": y, "z": z}
        return None
    
    def _handle_chat_message(self, msg: BusinessMessage):
        """处理聊天消息"""
        message = msg.data.decode('utf-8')
        logger.info(f"Chat: UIN={msg.uin}, Msg={message}")
        return {"type": "chat", "uin": msg.uin, "message": message}
    
    def _handle_heartbeat(self, msg: BusinessMessage):
        """处理心跳"""
        logger.debug(f"Heartbeat: UIN={msg.uin}")
        return {"type": "heartbeat", "uin": msg.uin}
