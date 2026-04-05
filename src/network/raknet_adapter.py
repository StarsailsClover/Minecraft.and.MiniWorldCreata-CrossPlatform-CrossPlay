"""
RakNet 适配器

将 RakNet 协议适配到 MnMCP 网络层
"""

import logging
from typing import Optional, Callable
from dataclasses import dataclass

from ..protocol.raknet import RakNetPacket, RakNetCodec, RakNetMessageID

logger = logging.getLogger(__name__)


@dataclass
class RakNetConfig:
    """RakNet 配置"""
    max_connections: int = 10
    connection_timeout: float = 10.0
    ping_interval: float = 5.0


class RakNetAdapter:
    """RakNet 适配器"""
    
    def __init__(self, config: RakNetConfig = None):
        self.config = config or RakNetConfig()
        self.codec = RakNetCodec()
        self.connected = False
        self.remote_guid: Optional[int] = None
        self.on_packet: Optional[Callable[[RakNetPacket], None]] = None
    
    def create_connection_request(self) -> bytes:
        """创建连接请求包"""
        # ID_CONNECTION_REQUEST
        packet = RakNetPacket(
            message_id=RakNetMessageID.ID_CONNECTION_REQUEST,
            data=b'\x00' * 16  # GUID placeholder
        )
        return self.codec.encode_packet(packet)
    
    def handle_connection_accepted(self, data: bytes) -> bool:
        """处理连接接受"""
        packet = self.codec.decode_packet(data)
        if not packet:
            return False
        
        if packet.message_id == RakNetMessageID.ID_CONNECTION_REQUEST_ACCEPTED:
            self.connected = True
            logger.info("RakNet connection accepted")
            return True
        
        return False
    
    def create_ping(self) -> bytes:
        """创建 ping 包"""
        packet = RakNetPacket(
            message_id=RakNetMessageID.ID_CONNECTED_PING,
            data=b''
        )
        return self.codec.encode_packet(packet)
    
    def handle_pong(self, data: bytes) -> bool:
        """处理 pong 响应"""
        packet = self.codec.decode_packet(data)
        if not packet:
            return False
        
        return packet.message_id == RakNetMessageID.ID_CONNECTED_PONG
    
    def encode_user_packet(self, data: bytes) -> bytes:
        """编码用户数据包"""
        packet = RakNetPacket(
            message_id=RakNetMessageID.ID_USER_PACKET_ENUM,
            data=data
        )
        return self.codec.encode_packet(packet)
    
    def decode_user_packet(self, data: bytes) -> Optional[bytes]:
        """解码用户数据包"""
        packet = self.codec.decode_packet(data)
        if not packet:
            return None
        
        if packet.message_id == RakNetMessageID.ID_USER_PACKET_ENUM:
            return packet.data
        
        return None
