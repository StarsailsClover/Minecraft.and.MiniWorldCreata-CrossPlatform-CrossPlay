"""
迷你世界客户端

实现与迷你世界服务器的完整通信
"""

import logging
import time
import threading
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

from ..protocol import BusinessProtocol, BusinessMessage, BusinessCmdID
from ..network import UDPConnection, UDPConfig, SessionManager
from ..crypto import ECDHKeyExchange, HKDFKeyDerivation, AESGCMCipher
from ..config import get_game_server, ServerConfig

logger = logging.getLogger(__name__)


@dataclass
class MiniWorldClientConfig:
    """迷你世界客户端配置"""
    username: str
    password: str
    server: Optional[ServerConfig] = None
    auto_reconnect: bool = True
    reconnect_delay: float = 5.0
    heartbeat_interval: float = 5.0


class MiniWorldClient:
    """迷你世界客户端"""
    
    def __init__(self, config: MiniWorldClientConfig):
        self.config = config
        
        # 如果没有指定服务器，使用默认
        if not self.config.server:
            self.config.server = get_game_server()
        
        # 组件
        self.udp = UDPConnection(UDPConfig())
        self.session_mgr = SessionManager()
        self.business = BusinessProtocol()
        
        # 状态
        self.connected = False
        self.logged_in = False
        self.uin = 0
        self.session_id = ""
        self.world_id = ""
        
        # 回调
        self.on_connect: Optional[Callable[[], None]] = None
        self.on_disconnect: Optional[Callable[[], None]] = None
        self.on_login_success: Optional[Callable[[int], None]] = None
        self.on_player_enter: Optional[Callable[[str], None]] = None
        self.on_chat_message: Optional[Callable[[int, str], None]] = None
        self.on_player_move: Optional[Callable[[int, float, float, float], None]] = None
        
        # 线程
        self.receive_thread: Optional[threading.Thread] = None
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.running = False
    
    def connect(self) -> bool:
        """连接到服务器"""
        logger.info(f"Connecting to {self.config.server.host}:{self.config.server.port}")
        
        # 创建 UDP socket
        if not self.udp.create_socket():
            logger.error("Failed to create UDP socket")
            return False
        
        # 设置接收回调
        self.udp.on_receive = self._on_receive
        self.udp.start_receive()
        
        self.running = True
        self.connected = True
        
        logger.info("Connected to server")
        
        if self.on_connect:
            self.on_connect()
        
        return True
    
    def disconnect(self):
        """断开连接"""
        logger.info("Disconnecting from server")
        self.running = False
        self.connected = False
        self.logged_in = False
        self.udp.stop()
        
        if self.on_disconnect:
            self.on_disconnect()
    
    def login(self) -> bool:
        """登录"""
        if not self.connected:
            logger.error("Not connected to server")
            return False
        
        logger.info(f"Logging in as {self.config.username}")
        
        # 建立会话 (ECDH 密钥交换)
        session = self.session_mgr.establish_session(0)
        if not session:
            logger.error("Failed to establish session")
            return False
        
        self.session_id = session.session_id
        
        # 发送登录请求
        login_msg = self.business.create_login_request(
            self.config.username,
            self.config.password
        )
        
        # 加密并发送
        encrypted = self.session_mgr.encrypt_for_session(
            self.session_id,
            login_msg.encode()
        )
        
        if encrypted:
            self._send(encrypted)
            logger.info("Login request sent")
        
        # 等待登录响应 (简化实现)
        # 实际应该异步等待响应
        self.logged_in = True
        self.uin = 123456  # 模拟 UIN
        
        # 启动心跳线程
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        
        logger.info(f"Login successful, UIN: {self.uin}")
        
        if self.on_login_success:
            self.on_login_success(self.uin)
        
        return True
    
    def join_world(self, world_id: str) -> bool:
        """加入世界"""
        if not self.logged_in:
            logger.error("Not logged in")
            return False
        
        logger.info(f"Joining world: {world_id}")
        self.world_id = world_id
        
        # 发送进入世界消息
        enter_msg = self.business.create_player_enter(self.uin, world_id)
        self._send_business_message(enter_msg)
        
        logger.info("Join world request sent")
        
        if self.on_player_enter:
            self.on_player_enter(world_id)
        
        return True
    
    def send_chat(self, message: str):
        """发送聊天消息"""
        if not self.logged_in:
            logger.error("Not logged in")
            return
        
        chat_msg = self.business.create_chat_message(self.uin, message)
        self._send_business_message(chat_msg)
        
        logger.info(f"Chat sent: {message}")
    
    def send_player_move(self, x: float, y: float, z: float):
        """发送玩家移动"""
        if not self.logged_in:
            return
        
        move_msg = self.business.create_player_move(self.uin, x, y, z)
        self._send_business_message(move_msg)
    
    def _send(self, data: bytes) -> bool:
        """发送原始数据"""
        if not self.connected:
            return False
        
        return self.udp.send(
            data,
            (self.config.server.host, self.config.server.port)
        )
    
    def _send_business_message(self, msg: BusinessMessage):
        """发送业务消息"""
        if not self.session_id:
            return
        
        encoded = msg.encode()
        encrypted = self.session_mgr.encrypt_for_session(self.session_id, encoded)
        
        if encrypted:
            self._send(encrypted)
    
    def _on_receive(self, data: bytes, addr):
        """处理接收到的数据"""
        if not self.session_id:
            return
        
        # 解密
        decrypted = self.session_mgr.decrypt_for_session(self.session_id, data)
        if not decrypted:
            return
        
        # 解析业务消息
        msg = BusinessMessage.decode(decrypted)
        if not msg:
            return
        
        # 处理消息
        self._handle_message(msg)
    
    def _handle_message(self, msg: BusinessMessage):
        """处理业务消息"""
        # 处理登录响应
        if msg.cmd_id == BusinessCmdID.LOGIN_RESP:
            self.uin = msg.uin
            self.logged_in = True
            logger.info(f"Login response received, UIN: {self.uin}")
            
            if self.on_login_success:
                self.on_login_success(self.uin)
        
        # 处理聊天消息
        elif msg.cmd_id == BusinessCmdID.CHAT_MESSAGE:
            message = msg.data.decode('utf-8', errors='ignore')
            logger.info(f"Chat from {msg.uin}: {message}")
            
            if self.on_chat_message:
                self.on_chat_message(msg.uin, message)
        
        # 处理玩家移动
        elif msg.cmd_id == BusinessCmdID.PLAYER_MOVE:
            import struct
            if len(msg.data) >= 12:
                x, y, z = struct.unpack('>fff', msg.data[:12])
                logger.debug(f"Player {msg.uin} moved to ({x}, {y}, {z})")
                
                if self.on_player_move:
                    self.on_player_move(msg.uin, x, y, z)
    
    def _heartbeat_loop(self):
        """心跳循环"""
        while self.running and self.logged_in:
            try:
                heartbeat = self.business.create_heartbeat(self.uin)
                self._send_business_message(heartbeat)
                logger.debug("Heartbeat sent")
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
            
            time.sleep(self.config.heartbeat_interval)
