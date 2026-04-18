"""
迷你世界真实协议实现

基于逆向分析的实际协议实现
"""

import struct
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MNWPacketHeader:
    """
    迷你世界数据包头部
    
    基于 GRAND_MASTER_DECREE_FINAL.md 的协议定义
    """
    # UDP 60009 端口物理坐标包格式
    # 偏移 04-07: OpCode (32位小端)
    # 偏移 08-11: Entity ID (32位小端)
    # 偏移 12-23: X, Y, Z 坐标 (32位小端，千分之一精度)
    
    opcode: int
    entity_id: int
    x: int  # 千分之一精度
    y: int
    z: int
    
    @classmethod
    def from_bytes(cls, data: bytes) -> Optional['MNWPacketHeader']:
        """从字节解析头部"""
        if len(data) < 24:
            return None
        
        try:
            opcode = struct.unpack('<I', data[4:8])[0]
            entity_id = struct.unpack('<I', data[8:12])[0]
            x = struct.unpack('<i', data[12:16])[0]  # 有符号整数
            y = struct.unpack('<i', data[16:20])[0]
            z = struct.unpack('<i', data[20:24])[0]
            
            return cls(opcode=opcode, entity_id=entity_id, x=x, y=y, z=z)
        except Exception as e:
            logger.error(f"Failed to parse header: {e}")
            return None
    
    def to_bytes(self) -> bytes:
        """转换为字节"""
        data = b''
        data += struct.pack('<I', self.opcode)
        data += struct.pack('<I', self.entity_id)
        data += struct.pack('<i', self.x)
        data += struct.pack('<i', self.y)
        data += struct.pack('<i', self.z)
        return data
    
    def get_coords(self) -> Tuple[float, float, float]:
        """获取实际坐标 (除以1000)"""
        return (self.x / 1000.0, self.y / 1000.0, self.z / 1000.0)
    
    def set_coords(self, x: float, y: float, z: float):
        """设置坐标 (乘以1000)"""
        self.x = int(x * 1000)
        self.y = int(y * 1000)
        self.z = int(z * 1000)


class MNWProtocolHandler:
    """
    迷你世界协议处理器
    
    处理实际的协议编解码
    """
    
    # 消息 ID 定义 (来自逆向分析)
    MSG_COMMAND = 129           # 主业务指令集
    MSG_MODIFY_ARRAY = 149      # 世界状态快照
    MSG_GMODULE = 160           # 系统热保活
    
    # 操作码定义
    OP_FULL_SYNC = 864          # 全量位移同步
    
    def __init__(self):
        self.seq = 0
    
    def create_position_packet(self, entity_id: int, x: float, y: float, z: float) -> bytes:
        """
        创建位置同步包
        
        用于 UDP 60009 端口
        """
        header = MNWPacketHeader(
            opcode=self.OP_FULL_SYNC,
            entity_id=entity_id,
            x=0, y=0, z=0
        )
        header.set_coords(x, y, z)
        
        # 添加序列号前缀 (84 [Sequence] 00 00)
        self.seq = (self.seq + 1) % 256
        prefix = bytes([0x84, self.seq, 0x00, 0x00])
        
        return prefix + header.to_bytes()
    
    def parse_position_packet(self, data: bytes) -> Optional[Dict]:
        """解析位置同步包"""
        if len(data) < 28:
            return None
        
        # 检查前缀
        if data[0] != 0x84:
            return None
        
        seq = data[1]
        header = MNWPacketHeader.from_bytes(data[4:])
        
        if not header:
            return None
        
        x, y, z = header.get_coords()
        
        return {
            'seq': seq,
            'opcode': header.opcode,
            'entity_id': header.entity_id,
            'x': x,
            'y': y,
            'z': z,
        }
    
    def create_heartbeat_packet(self, beat_code: int, client_time: int) -> bytes:
        """
        创建心跳包
        
        基于 proto_ch.proto PB_HeartBeatCH
        """
        # 简化的 msgpack 格式
        # 实际应该使用 msgpack 库
        data = b''
        data += b'\x83'  # fixmap with 3 elements
        
        # BeatCode
        data += b'\xa9BeatCode'  # fixstr "BeatCode"
        data += struct.pack('>Q', beat_code)  # uint64
        
        # server_time (占位)
        data += b'\xabserver_time'
        data += struct.pack('>Q', 0)
        
        # client_time
        data += b'\xabclient_time'
        data += struct.pack('>Q', client_time)
        
        return data
    
    def create_command_packet(self, cmd_id: int, params: Dict) -> bytes:
        """
        创建命令包
        
        用于 MSG_COMMAND (129)
        """
        # 简化的命令包格式
        header = struct.pack('<I', cmd_id)
        
        # 参数序列化 (简化)
        param_bytes = str(params).encode('utf-8')
        
        return header + param_bytes


import socket


class MNWConnection:
    """
    迷你世界连接管理
    
    管理实际的网络连接
    """
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.protocol = MNWProtocolHandler()
        self.connected = False
        self.entity_id = 0
        self.sock = None
    
    def connect(self) -> bool:
        """建立连接"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(5.0)
            self.connected = True
            logger.info(f"Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def send_position(self, x: float, y: float, z: float) -> bool:
        """发送位置更新"""
        if not self.connected:
            return False
        
        try:
            packet = self.protocol.create_position_packet(
                self.entity_id, x, y, z
            )
            self.sock.sendto(packet, (self.host, self.port))
            return True
        except Exception as e:
            logger.error(f"Send position failed: {e}")
            return False
    
    def send_heartbeat(self, beat_code: int) -> bool:
        """发送心跳"""
        if not self.connected:
            return False
        
        try:
            import time
            packet = self.protocol.create_heartbeat_packet(
                beat_code, int(time.time() * 1000)
            )
            self.sock.sendto(packet, (self.host, self.port))
            return True
        except Exception as e:
            logger.error(f"Send heartbeat failed: {e}")
            return False
    
    def receive(self) -> Optional[Dict]:
        """接收数据"""
        if not self.connected:
            return None
        
        try:
            data, addr = self.sock.recvfrom(1024)
            
            # 尝试解析为位置包
            result = self.protocol.parse_position_packet(data)
            if result:
                return result
            
            # 其他类型的包...
            return {'raw': data.hex(), 'addr': addr}
            
        except socket.timeout:
            return None
        except Exception as e:
            logger.error(f"Receive error: {e}")
            return None
    
    def disconnect(self):
        """断开连接"""
        if self.connected:
            self.sock.close()
            self.connected = False
            logger.info("Disconnected")
