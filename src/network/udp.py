"""
UDP 连接管理
"""

import socket
import logging
import threading
import time
from typing import Optional, Callable, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class UDPConfig:
    """UDP 配置"""
    host: str = "0.0.0.0"
    port: int = 0  # 0 = 自动分配
    timeout: float = 5.0
    buffer_size: int = 65535


class UDPConnection:
    """UDP 连接管理"""
    
    def __init__(self, config: UDPConfig = None):
        self.config = config or UDPConfig()
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.receive_thread: Optional[threading.Thread] = None
        self.on_receive: Optional[Callable[[bytes, Tuple[str, int]], None]] = None
    
    def create_socket(self) -> bool:
        """创建 UDP socket"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(self.config.timeout)
            self.socket.bind((self.config.host, self.config.port))
            actual_port = self.socket.getsockname()[1]
            logger.info(f"UDP socket created on port {actual_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to create socket: {e}")
            return False
    
    def send(self, data: bytes, addr: Tuple[str, int]) -> bool:
        """发送数据"""
        if not self.socket:
            logger.error("Socket not created")
            return False
        
        try:
            self.socket.sendto(data, addr)
            return True
        except Exception as e:
            logger.error(f"Send failed: {e}")
            return False
    
    def start_receive(self):
        """开始接收线程"""
        if self.running:
            return
        
        self.running = True
        self.receive_thread = threading.Thread(target=self._receive_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        logger.info("Receive thread started")
    
    def _receive_loop(self):
        """接收循环"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(self.config.buffer_size)
                if self.on_receive:
                    self.on_receive(data, addr)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Receive error: {e}")
    
    def stop(self):
        """停止连接"""
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
        if self.receive_thread:
            self.receive_thread.join(timeout=1.0)
        logger.info("UDP connection stopped")
