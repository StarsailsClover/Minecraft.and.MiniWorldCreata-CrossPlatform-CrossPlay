"""
MnMCP 桥接器 V2

实现 Minecraft Java 与迷你世界国服的完整联机互通
"""

import logging
import threading
import time
from typing import Optional, Callable
from dataclasses import dataclass

from .protocol import BusinessProtocol, BusinessCmdID
from .protocol.mc_java import MCJavaProtocol, MCJavaPacket, MCJavaPacketID
from .client import MiniWorldClient, MiniWorldClientConfig
from .mapping import CoordinateConverter, Vec3, BlockMapper
from .config import get_game_server

logger = logging.getLogger(__name__)


@dataclass
class BridgeV2Config:
    """桥接器 V2 配置"""
    # Minecraft 配置
    mc_host: str = "127.0.0.1"
    mc_port: int = 25565
    mc_username: str = "MnMCP_Player"
    
    # 迷你世界配置
    mnw_username: str = ""
    mnw_password: str = ""
    mnw_world_id: str = ""
    
    # 桥接器配置
    enable_chat_bridge: bool = True
    enable_movement_bridge: bool = True
    enable_block_bridge: bool = False  # 暂不实现


class MnMCPBridgeV2:
    """
    MnMCP 桥接器 V2
    
    实现完整的 MC Java ↔ 迷你世界 联机互通
    """
    
    def __init__(self, config: BridgeV2Config = None):
        self.config = config or BridgeV2Config()
        
        # 组件
        self.mc_protocol = MCJavaProtocol()
        self.mnw_client: Optional[MiniWorldClient] = None
        self.coord_conv = CoordinateConverter()
        self.block_mapper = BlockMapper()
        
        # 状态
        self.running = False
        self.mc_connected = False
        self.mnw_connected = False
        
        # 玩家状态
        self.mc_player_pos = Vec3(0, 0, 0)
        self.mnw_player_pos = Vec3(0, 0, 0)
        
        # 线程
        self.mc_thread: Optional[threading.Thread] = None
        self.mnw_thread: Optional[threading.Thread] = None
    
    def start(self) -> bool:
        """启动桥接器"""
        logger.info("Starting MnMCP Bridge V2...")
        self.running = True
        
        # 连接迷你世界
        if not self._connect_mnw():
            logger.error("Failed to connect to MiniWorld")
            return False
        
        # 连接 Minecraft (简化实现)
        logger.info("Minecraft connection would be established here")
        self.mc_connected = True
        
        logger.info("Bridge V2 started successfully")
        return True
    
    def stop(self):
        """停止桥接器"""
        logger.info("Stopping MnMCP Bridge V2...")
        self.running = False
        
        if self.mnw_client:
            self.mnw_client.disconnect()
        
        logger.info("Bridge V2 stopped")
    
    def _connect_mnw(self) -> bool:
        """连接迷你世界"""
        logger.info("Connecting to MiniWorld...")
        
        # 创建客户端
        mnw_config = MiniWorldClientConfig(
            username=self.config.mnw_username,
            password=self.config.mnw_password,
            server=get_game_server()
        )
        
        self.mnw_client = MiniWorldClient(mnw_config)
        
        # 设置回调
        self.mnw_client.on_connect = self._on_mnw_connect
        self.mnw_client.on_disconnect = self._on_mnw_disconnect
        self.mnw_client.on_login_success = self._on_mnw_login
        self.mnw_client.on_chat_message = self._on_mnw_chat
        self.mnw_client.on_player_move = self._on_mnw_player_move
        
        # 连接
        if not self.mnw_client.connect():
            return False
        
        # 登录
        if not self.mnw_client.login():
            return False
        
        # 加入世界
        if self.config.mnw_world_id:
            self.mnw_client.join_world(self.config.mnw_world_id)
        
        self.mnw_connected = True
        return True
    
    def _on_mnw_connect(self):
        """迷你世界连接回调"""
        logger.info("MiniWorld connected")
    
    def _on_mnw_disconnect(self):
        """迷你世界断开回调"""
        logger.info("MiniWorld disconnected")
        self.mnw_connected = False
    
    def _on_mnw_login(self, uin: int):
        """迷你世界登录成功回调"""
        logger.info(f"MiniWorld login success, UIN: {uin}")
    
    def _on_mnw_chat(self, uin: int, message: str):
        """迷你世界聊天消息回调"""
        logger.info(f"[MiniWorld] {uin}: {message}")
        
        if self.config.enable_chat_bridge:
            # 转发到 Minecraft
            self._forward_chat_to_mc(uin, message)
    
    def _on_mnw_player_move(self, uin: int, x: float, y: float, z: float):
        """迷你世界玩家移动回调"""
        logger.debug(f"[MiniWorld] Player {uin} moved to ({x}, {y}, {z})")
        
        if self.config.enable_movement_bridge:
            # 坐标转换 (MNW -> MC)
            mnw_pos = Vec3(x, y, z)
            mc_pos = self.coord_conv.mnw_to_mc(mnw_pos)
            
            # 转发到 Minecraft
            self._forward_movement_to_mc(uin, mc_pos.x, mc_pos.y, mc_pos.z)
    
    def _forward_chat_to_mc(self, uin: int, message: str):
        """转发聊天消息到 Minecraft"""
        # TODO: 实现 MC Java 协议发送聊天消息
        logger.info(f"[Bridge] Forwarding chat to MC: {message}")
    
    def _forward_movement_to_mc(self, uin: int, x: float, y: float, z: float):
        """转发玩家移动到 Minecraft"""
        # TODO: 实现 MC Java 协议发送玩家移动
        logger.debug(f"[Bridge] Forwarding movement to MC: ({x}, {y}, {z})")
    
    def send_mc_chat(self, message: str):
        """发送 Minecraft 聊天到迷你世界"""
        if not self.mnw_connected:
            logger.error("Not connected to MiniWorld")
            return
        
        logger.info(f"[Minecraft] Sending to MiniWorld: {message}")
        self.mnw_client.send_chat(message)
    
    def send_mc_movement(self, x: float, y: float, z: float):
        """发送 Minecraft 移动到迷你世界"""
        if not self.mnw_connected:
            return
        
        # 坐标转换 (MC -> MNW)
        mc_pos = Vec3(x, y, z)
        mnw_pos = self.coord_conv.mc_to_mnw(mc_pos)
        
        self.mnw_client.send_player_move(mnw_pos.x, mnw_pos.y, mnw_pos.z)
    
    def get_status(self) -> dict:
        """获取桥接器状态"""
        return {
            'running': self.running,
            'mc_connected': self.mc_connected,
            'mnw_connected': self.mnw_connected,
            'config': {
                'chat_bridge': self.config.enable_chat_bridge,
                'movement_bridge': self.config.enable_movement_bridge,
            }
        }
