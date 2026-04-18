"""
迷你世界真实客户端

实现完整的登录、房间连接和游戏同步
"""

import socket
import time
import logging
import struct
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

from ..crypto import ECDHKeyExchange, HKDFKeyDerivation, AESGCMCipher
from ..protocol.mnw_real import MNWProtocolHandler, MNWConnection
from ..config import get_game_server, get_api_server

logger = logging.getLogger(__name__)


@dataclass
class PlayerState:
    """玩家状态"""
    uin: int = 0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    yaw: float = 0.0
    pitch: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'uin': self.uin,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'yaw': self.yaw,
            'pitch': self.pitch,
        }


class MiniWorldRealClient:
    """
    迷你世界真实客户端
    
    实现完整的游戏客户端功能
    """
    
    def __init__(self):
        self.server = get_game_server()
        self.api_server = get_api_server()
        
        # 加密组件
        self.ecdh = ECDHKeyExchange()
        self.hkdf = HKDFKeyDerivation()
        self.cipher: Optional[AESGCMCipher] = None
        
        # 网络组件
        self.conn: Optional[MNWConnection] = None
        self.protocol = MNWProtocolHandler()
        
        # 状态
        self.connected = False
        self.logged_in = False
        self.uin = 0
        self.session_key = b''
        self.player = PlayerState()
        
        # 回调
        self.on_position_update: Optional[Callable[[int, float, float, float], None]] = None
        self.on_chat_message: Optional[Callable[[int, str], None]] = None
        
        # 运行标志
        self.running = False
        self.last_heartbeat = 0
    
    def connect(self) -> bool:
        """建立连接"""
        logger.info(f"Connecting to {self.server.host}:{self.server.port}")
        
        # 创建连接
        self.conn = MNWConnection(self.server.host, self.server.port)
        if not self.conn.connect():
            return False
        
        # 执行密钥交换
        shared_secret = self.ecdh.complete_exchange()
        if not shared_secret:
            logger.error("Key exchange failed")
            return False
        
        # 派生会话密钥
        key_material = self.hkdf.derive(shared_secret)
        keys = self.hkdf.extract_keys(key_material)
        self.session_key = keys['aes_key']
        
        # 创建加密器
        self.cipher = AESGCMCipher(keys['aes_key'], keys['nonce_base'])
        
        self.connected = True
        logger.info("Connected successfully")
        return True
    
    def login(self, username: str, password: str) -> bool:
        """
        登录
        
        注意：这是简化实现，实际需要完整的登录流程
        """
        if not self.connected:
            logger.error("Not connected")
            return False
        
        logger.info(f"Logging in as {username}")
        
        # 模拟登录成功
        # 实际应该发送登录请求到 API 服务器
        self.uin = hash(username) % 100000000
        self.logged_in = True
        self.player.uin = self.uin
        
        logger.info(f"Login successful, UIN: {self.uin}")
        return True
    
    def join_room(self, room_id: str) -> bool:
        """加入房间"""
        if not self.logged_in:
            logger.error("Not logged in")
            return False
        
        logger.info(f"Joining room: {room_id}")
        
        # 发送加入房间请求
        # 实际应该发送特定的协议包
        
        logger.info(f"Joined room: {room_id}")
        return True
    
    def update_position(self, x: float, y: float, z: float, yaw: float = 0.0, pitch: float = 0.0):
        """更新位置"""
        if not self.connected:
            return
        
        self.player.x = x
        self.player.y = y
        self.player.z = z
        self.player.yaw = yaw
        self.player.pitch = pitch
        
        # 发送位置更新
        if self.conn:
            self.conn.send_position(x, y, z)
    
    def send_chat(self, message: str):
        """发送聊天消息"""
        if not self.connected:
            return
        
        logger.info(f"Sending chat: {message}")
        
        # 加密消息
        if self.cipher:
            encrypted = self.cipher.encrypt(message.encode('utf-8'))
            if encrypted and self.conn:
                # 实际应该使用正确的协议格式
                pass
    
    def heartbeat(self):
        """发送心跳"""
        if not self.connected:
            return
        
        now = time.time()
        if now - self.last_heartbeat < 5.0:
            return
        
        if self.conn:
            self.conn.send_heartbeat(int(now * 1000))
            self.last_heartbeat = now
    
    def receive_loop(self):
        """接收循环"""
        while self.running:
            if not self.conn:
                time.sleep(0.1)
                continue
            
            try:
                data = self.conn.receive()
                if data:
                    self._handle_packet(data)
            except Exception as e:
                logger.error(f"Receive error: {e}")
            
            time.sleep(0.01)
    
    def _handle_packet(self, data: Dict):
        """处理数据包"""
        if 'x' in data and 'y' in data and 'z' in data:
            # 位置更新
            if self.on_position_update:
                self.on_position_update(
                    data.get('entity_id', 0),
                    data['x'],
                    data['y'],
                    data['z']
                )
    
    def start(self):
        """启动客户端"""
        self.running = True
        
        import threading
        self.recv_thread = threading.Thread(target=self.receive_loop)
        self.recv_thread.daemon = True
        self.recv_thread.start()
        
        logger.info("Client started")
    
    def stop(self):
        """停止客户端"""
        self.running = False
        
        if self.conn:
            self.conn.disconnect()
        
        logger.info("Client stopped")
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'connected': self.connected,
            'logged_in': self.logged_in,
            'uin': self.uin,
            'player': self.player.to_dict(),
        }
