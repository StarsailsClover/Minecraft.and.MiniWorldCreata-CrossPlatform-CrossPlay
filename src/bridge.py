"""
核心桥接器

实现 Minecraft Java 与迷你世界国服的联机互通
"""

import logging
import threading
import time
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from src.protocol import BusinessProtocol, BusinessMessage, BusinessCmdID
from src.protocol.raknet import RakNetPacket, RakNetCodec, RakNetMessageID
from src.network import UDPConnection, UDPConfig, SessionManager
from src.mapping import CoordinateConverter, Vec3, BlockMapper, EntityMapper

logger = logging.getLogger(__name__)


@dataclass
class BridgeConfig:
    """桥接器配置"""
    # Minecraft 配置
    mc_host: str = "127.0.0.1"
    mc_port: int = 25565
    
    # 迷你世界配置
    mnw_host: str = "127.0.0.1"
    mnw_port: int = 8080
    
    # 桥接器配置
    bridge_host: str = "0.0.0.0"
    bridge_port: int = 19132
    
    # 玩家配置
    player_name: str = "MnMCP_Player"
    player_uin: int = 0


class MnMCPBridge:
    """
    MnMCP 核心桥接器
    
    实现 Minecraft Java 与迷你世界国服的联机互通
    """
    
    def __init__(self, config: BridgeConfig = None):
        self.config = config or BridgeConfig()
        
        # 组件
        self.udp = UDPConnection(UDPConfig(
            host=self.config.bridge_host,
            port=self.config.bridge_port
        ))
        self.session_mgr = SessionManager()
        self.business = BusinessProtocol()
        self.coord_conv = CoordinateConverter()
        self.block_mapper = BlockMapper()
        self.entity_mapper = EntityMapper()
        
        # 状态
        self.running = False
        self.connected_to_mnw = False
        self.player_uin = self.config.player_uin
        
        # 线程
        self.receive_thread: Optional[threading.Thread] = None
        self.heartbeat_thread: Optional[threading.Thread] = None
        
        # 回调
        self.on_mc_packet: Optional[callable] = None
        self.on_mnw_packet: Optional[callable] = None
    
    def start(self) -> bool:
        """启动桥接器"""
        logger.info("Starting MnMCP Bridge...")
        
        # 创建 UDP socket
        if not self.udp.create_socket():
            logger.error("Failed to create UDP socket")
            return False
        
        # 设置接收回调
        self.udp.on_receive = self._on_udp_receive
        self.udp.start_receive()
        
        # 启动心跳线程
        self.running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        
        logger.info(f"Bridge started on {self.config.bridge_host}:{self.config.bridge_port}")
        return True
    
    def stop(self):
        """停止桥接器"""
        logger.info("Stopping MnMCP Bridge...")
        self.running = False
        self.udp.stop()
        
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=2.0)
        
        logger.info("Bridge stopped")
    
    def connect_to_mnw(self, host: str, port: int, username: str, password: str) -> bool:
        """
        连接到迷你世界国服
        
        Args:
            host: 服务器地址
            port: 服务器端口
            username: 用户名
            password: 密码
        
        Returns:
            是否连接成功
        """
        logger.info(f"Connecting to MiniWorld: {host}:{port}")
        
        # 保存服务器地址
        self.config.mnw_host = host
        self.config.mnw_port = port
        
        # 建立会话
        session = self.session_mgr.establish_session(0)  # 登录前 UIN 为 0
        if not session:
            logger.error("Failed to establish session")
            return False
        
        # 发送登录请求
        login_msg = self.business.create_login_request(username, password)
        self._send_to_mnw(login_msg.encode())
        
        # 等待登录响应 (简化实现，实际需要异步处理)
        logger.info("Login request sent, waiting for response...")
        
        # TODO: 实现登录响应处理
        self.connected_to_mnw = True
        return True
    
    def join_world(self, world_id: str) -> bool:
        """加入世界"""
        if not self.connected_to_mnw:
            logger.error("Not connected to MiniWorld")
            return False
        
        logger.info(f"Joining world: {world_id}")
        
        # 发送进入世界消息
        enter_msg = self.business.create_player_enter(self.player_uin, world_id)
        self._send_to_mnw(enter_msg.encode())
        
        return True
    
    def send_chat(self, message: str):
        """发送聊天消息"""
        if not self.connected_to_mnw:
            logger.error("Not connected to MiniWorld")
            return
        
        chat_msg = self.business.create_chat_message(self.player_uin, message)
        self._send_to_mnw(chat_msg.encode())
    
    def send_player_move(self, x: float, y: float, z: float):
        """发送玩家移动"""
        if not self.connected_to_mnw:
            return
        
        # 坐标转换
        mnw_pos = self.coord_conv.mc_to_mnw(Vec3(x, y, z))
        
        move_msg = self.business.create_player_move(
            self.player_uin,
            mnw_pos.x,
            mnw_pos.y,
            mnw_pos.z
        )
        self._send_to_mnw(move_msg.encode())
    
    def _on_udp_receive(self, data: bytes, addr: Tuple[str, int]):
        """处理 UDP 接收"""
        # 判断来源
        if addr[0] == self.config.mc_host and addr[1] == self.config.mc_port:
            # 来自 Minecraft
            self._handle_mc_packet(data)
        elif addr[0] == self.config.mnw_host and addr[1] == self.config.mnw_port:
            # 来自迷你世界
            self._handle_mnw_packet(data)
        else:
            logger.debug(f"Unknown packet from {addr}")
    
    def _handle_mc_packet(self, data: bytes):
        """处理 Minecraft 数据包"""
        logger.debug(f"Received {len(data)} bytes from Minecraft")
        
        # TODO: 解析 Minecraft 协议
        # 这里需要实现 Minecraft Java 协议解析
        
        if self.on_mc_packet:
            self.on_mc_packet(data)
    
    def _handle_mnw_packet(self, data: bytes):
        """处理迷你世界数据包"""
        logger.debug(f"Received {len(data)} bytes from MiniWorld")
        
        # 解密数据
        # TODO: 使用 session 解密
        
        # 解析业务消息
        msg = BusinessMessage.decode(data)
        if msg:
            result = self.business.handle_message(msg)
            logger.debug(f"Handled message: {result}")
        
        if self.on_mnw_packet:
            self.on_mnw_packet(data)
    
    def _send_to_mnw(self, data: bytes) -> bool:
        """发送数据到迷你世界"""
        return self.udp.send(
            data,
            (self.config.mnw_host, self.config.mnw_port)
        )
    
    def _send_to_mc(self, data: bytes) -> bool:
        """发送数据到 Minecraft"""
        return self.udp.send(
            data,
            (self.config.mc_host, self.config.mc_port)
        )
    
    def _heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            if self.connected_to_mnw and self.player_uin > 0:
                # 发送心跳
                heartbeat = self.business.create_heartbeat(self.player_uin)
                self._send_to_mnw(heartbeat.encode())
            
            time.sleep(5.0)  # 每 5 秒发送一次心跳
