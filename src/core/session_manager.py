#!/usr/bin/env python3
"""
会话管理器
管理Minecraft玩家和迷你世界房间之间的会话映射
"""

import uuid
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class SessionState(Enum):
    """会话状态"""
    CONNECTING = "connecting"
    AUTHENTICATING = "authenticating"
    CONNECTED = "connected"
    IN_GAME = "in_game"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"

@dataclass
class PlayerSession:
    """玩家会话"""
    # 会话ID
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Minecraft 玩家信息
    mc_username: str = ""
    mc_uuid: str = ""
    mc_client_ip: str = ""
    mc_client_port: int = 0
    
    # 迷你世界 账户信息
    mnw_account_id: str = ""  # 迷你号
    mnw_token: str = ""
    mnw_session_key: str = ""
    
    # 房间信息
    room_id: str = ""
    room_name: str = ""
    is_host: bool = False
    
    # 状态
    state: SessionState = SessionState.CONNECTING
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    # 统计
    packets_sent: int = 0
    packets_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    
    def update_activity(self):
        """更新活动时间"""
        self.last_activity = datetime.now()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """检查会话是否过期"""
        timeout = timedelta(minutes=timeout_minutes)
        return datetime.now() - self.last_activity > timeout
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "mc_username": self.mc_username,
            "mc_uuid": self.mc_uuid,
            "mnw_account_id": self.mnw_account_id,
            "room_id": self.room_id,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "packets_sent": self.packets_sent,
            "packets_received": self.packets_received
        }

class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        # 会话存储
        self.sessions: Dict[str, PlayerSession] = {}  # session_id -> session
        self.mc_username_to_session: Dict[str, str] = {}  # mc_username -> session_id
        self.mnw_account_to_session: Dict[str, str] = {}  # mnw_account_id -> session_id
        
        # 配置
        self.session_timeout_minutes = 30
        self.max_sessions = 100
        
        # 统计
        self.total_sessions_created = 0
        self.total_sessions_closed = 0
        
        logger.info("[+] 会话管理器初始化完成")
    
    def create_session(self, mc_username: str, mc_uuid: str, 
                      client_ip: str, client_port: int) -> PlayerSession:
        """创建新会话"""
        # 检查是否已存在
        if mc_username in self.mc_username_to_session:
            old_session_id = self.mc_username_to_session[mc_username]
            logger.warning(f"[*] 用户 {mc_username} 已有会话，关闭旧会话")
            self.close_session(old_session_id)
        
        # 创建新会话
        session = PlayerSession(
            mc_username=mc_username,
            mc_uuid=mc_uuid,
            mc_client_ip=client_ip,
            mc_client_port=client_port
        )
        
        # 存储会话
        self.sessions[session.session_id] = session
        self.mc_username_to_session[mc_username] = session.session_id
        
        self.total_sessions_created += 1
        
        logger.info(f"[+] 创建会话: {session.session_id} (用户: {mc_username})")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[PlayerSession]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def get_session_by_mc_username(self, username: str) -> Optional[PlayerSession]:
        """通过Minecraft用户名获取会话"""
        session_id = self.mc_username_to_session.get(username)
        if session_id:
            return self.sessions.get(session_id)
        return None
    
    def get_session_by_mnw_account(self, account_id: str) -> Optional[PlayerSession]:
        """通过迷你世界账号获取会话"""
        session_id = self.mnw_account_to_session.get(account_id)
        if session_id:
            return self.sessions.get(session_id)
        return None
    
    def update_session_state(self, session_id: str, new_state: SessionState):
        """更新会话状态"""
        session = self.sessions.get(session_id)
        if session:
            old_state = session.state
            session.state = new_state
            session.update_activity()
            logger.info(f"[*] 会话 {session_id} 状态: {old_state.value} -> {new_state.value}")
    
    def bind_mnw_account(self, session_id: str, mnw_account_id: str, token: str):
        """绑定迷你世界账号"""
        session = self.sessions.get(session_id)
        if session:
            session.mnw_account_id = mnw_account_id
            session.mnw_token = token
            self.mnw_account_to_session[mnw_account_id] = session_id
            session.update_activity()
            logger.info(f"[+] 会话 {session_id} 绑定迷你号: {mnw_account_id}")
    
    def join_room(self, session_id: str, room_id: str, room_name: str, is_host: bool = False):
        """加入房间"""
        session = self.sessions.get(session_id)
        if session:
            session.room_id = room_id
            session.room_name = room_name
            session.is_host = is_host
            session.update_activity()
            logger.info(f"[+] 会话 {session_id} 加入房间: {room_name} ({room_id})")
    
    def leave_room(self, session_id: str):
        """离开房间"""
        session = self.sessions.get(session_id)
        if session:
            logger.info(f"[*] 会话 {session_id} 离开房间: {session.room_name}")
            session.room_id = ""
            session.room_name = ""
            session.is_host = False
            session.update_activity()
    
    def update_stats(self, session_id: str, sent: int = 0, received: int = 0, 
                    bytes_sent: int = 0, bytes_received: int = 0):
        """更新统计信息"""
        session = self.sessions.get(session_id)
        if session:
            session.packets_sent += sent
            session.packets_received += received
            session.bytes_sent += bytes_sent
            session.bytes_received += bytes_received
            session.update_activity()
    
    def close_session(self, session_id: str):
        """关闭会话"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        # 更新统计
        self.total_sessions_closed += 1
        
        # 清理映射
        if session.mc_username in self.mc_username_to_session:
            del self.mc_username_to_session[session.mc_username]
        
        if session.mnw_account_id in self.mnw_account_to_session:
            del self.mnw_account_to_session[session.mnw_account_id]
        
        # 删除会话
        del self.sessions[session_id]
        
        logger.info(f"[-] 关闭会话: {session_id} (用户: {session.mc_username})")
    
    def cleanup_expired_sessions(self):
        """清理过期会话"""
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.is_expired(self.session_timeout_minutes):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            logger.info(f"[*] 清理过期会话: {session_id}")
            self.close_session(session_id)
        
        if expired_sessions:
            logger.info(f"[*] 清理了 {len(expired_sessions)} 个过期会话")
    
    def get_all_sessions(self) -> List[PlayerSession]:
        """获取所有会话"""
        return list(self.sessions.values())
    
    def get_active_sessions_count(self) -> int:
        """获取活跃会话数"""
        return len([s for s in self.sessions.values() 
                   if s.state in [SessionState.CONNECTED, SessionState.IN_GAME]])
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": self.get_active_sessions_count(),
            "total_created": self.total_sessions_created,
            "total_closed": self.total_sessions_closed,
            "mc_users": len(self.mc_username_to_session),
            "mnw_accounts": len(self.mnw_account_to_session)
        }
    
    def export_sessions(self) -> List[dict]:
        """导出所有会话信息"""
        return [session.to_dict() for session in self.sessions.values()]

# 测试代码
if __name__ == "__main__":
    manager = SessionManager()
    
    # 创建测试会话
    session = manager.create_session(
        mc_username="TestPlayer",
        mc_uuid="12345678-1234-1234-1234-123456789012",
        client_ip="127.0.0.1",
        client_port=12345
    )
    
    print(f"创建会话: {session.session_id}")
    
    # 绑定迷你世界账号
    manager.bind_mnw_account(session.session_id, "2056574316", "test_token")
    
    # 加入房间
    manager.join_room(session.session_id, "room_123", "测试房间", is_host=True)
    
    # 获取统计
    stats = manager.get_stats()
    print(f"统计: {stats}")
    
    # 关闭会话
    manager.close_session(session.session_id)
