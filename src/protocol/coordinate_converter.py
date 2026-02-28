#!/usr/bin/env python3
"""
坐标转换器
处理Minecraft和迷你世界之间的坐标转换
"""

import struct
import logging
from typing import Tuple, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Vector3:
    """三维向量"""
    x: float
    y: float
    z: float
    
    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Vector3':
        return cls(data["x"], data["y"], data["z"])

class CoordinateConverter:
    """坐标转换器"""
    
    def __init__(self):
        # 坐标比例因子（待确认实际值）
        # Minecraft: 1 block = 1 unit
        # 迷你世界: 可能不同
        self.scale_factor = 1.0  # 默认1:1
        
        # 坐标偏移（世界原点差异）
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.offset_z = 0.0
        
        # Y轴方向（Minecraft Y向上，待确认迷你世界）
        self.y_inverted = False
    
    def mc_to_mnw_position(self, mc_pos: Vector3) -> Vector3:
        """
        将Minecraft坐标转换为迷你世界坐标
        
        转换规则:
        - X轴取反 (Minecraft东=+X, 迷你世界东=-X)
        - Y轴保持不变
        - Z轴保持不变
        
        Args:
            mc_pos: Minecraft坐标 (x, y, z)
            
        Returns:
            迷你世界坐标
        """
        try:
            # X轴取反
            mnw_x = -(mc_pos.x + self.offset_x) * self.scale_factor
            mnw_y = (mc_pos.y + self.offset_y) * self.scale_factor
            mnw_z = (mc_pos.z + self.offset_z) * self.scale_factor
            
            if self.y_inverted:
                mnw_y = -mnw_y
            
            return Vector3(mnw_x, mnw_y, mnw_z)
        except Exception as e:
            logger.error(f"坐标转换失败 (MC->MNW): {e}")
            # 返回原始坐标作为fallback
            return mc_pos
    
    def mnw_to_mc_position(self, mnw_pos: Vector3) -> Vector3:
        """
        将迷你世界坐标转换为Minecraft坐标
        
        转换规则:
        - X轴取反 (与mc_to_mnw_position相反)
        - Y轴保持不变
        - Z轴保持不变
        
        Args:
            mnw_pos: 迷你世界坐标
            
        Returns:
            Minecraft坐标
        """
        try:
            # X轴取反
            mc_x = -(mnw_pos.x / self.scale_factor) - self.offset_x
            mc_y = (mnw_pos.y / self.scale_factor) - self.offset_y
            mc_z = (mnw_pos.z / self.scale_factor) - self.offset_z
            
            if self.y_inverted:
                mc_y = -mc_y
            
            return Vector3(mc_x, mc_y, mc_z)
        except Exception as e:
            logger.error(f"坐标转换失败 (MNW->MC): {e}")
            return mnw_pos  # fallback到原坐标
    
    def mc_to_mnw_rotation(self, mc_yaw: float, mc_pitch: float) -> Tuple[float, float]:
        """
        转换旋转角度
        
        Args:
            mc_yaw: Minecraft水平旋转 (-180 to 180)
            mc_pitch: Minecraft垂直旋转 (-90 to 90)
            
        Returns:
            (mnw_yaw, mnw_pitch)
        """
        # 角度格式可能相同，直接传递
        # 如果方向相反，需要调整
        mnw_yaw = mc_yaw
        mnw_pitch = mc_pitch
        
        return (mnw_yaw, mnw_pitch)
    
    def mc_to_mnw_velocity(self, mc_vel: Vector3) -> Vector3:
        """转换速度向量"""
        # 速度使用相同的比例因子
        return self.mc_to_mnw_position(mc_vel)
    
    def serialize_position_mnw(self, pos: Vector3) -> bytes:
        """
        序列化迷你世界位置数据
        
        假设格式: [x (float)] [y (float)] [z (float)]
        """
        # 使用小端浮点数
        return struct.pack('<fff', pos.x, pos.y, pos.z)
    
    def deserialize_position_mnw(self, data: bytes) -> Vector3:
        """反序列化迷你世界位置数据"""
        if len(data) < 12:
            raise ValueError("数据长度不足")
        
        x, y, z = struct.unpack('<fff', data[:12])
        return Vector3(x, y, z)
    
    def set_calibration(self, mc_point1: Vector3, mnw_point1: Vector3,
                       mc_point2: Vector3, mnw_point2: Vector3):
        """
        通过两个校准点设置转换参数
        
        Args:
            mc_point1: Minecraft参考点1
            mnw_point1: 迷你世界参考点1
            mc_point2: Minecraft参考点2
            mnw_point2: 迷你世界参考点2
        """
        # 计算比例因子
        mc_dist = ((mc_point2.x - mc_point1.x)**2 + 
                   (mc_point2.y - mc_point1.y)**2 + 
                   (mc_point2.z - mc_point1.z)**2) ** 0.5
        
        mnw_dist = ((mnw_point2.x - mnw_point1.x)**2 + 
                    (mnw_point2.y - mnw_point1.y)**2 + 
                    (mnw_point2.z - mnw_point1.z)**2) ** 0.5
        
        if mc_dist > 0 and mnw_dist > 0:
            self.scale_factor = mnw_dist / mc_dist
            logger.info(f"[*] 设置比例因子: {self.scale_factor}")
        
        # 计算偏移
        self.offset_x = mnw_point1.x / self.scale_factor - mc_point1.x
        self.offset_y = mnw_point1.y / self.scale_factor - mc_point1.y
        self.offset_z = mnw_point1.z / self.scale_factor - mc_point1.z
        
        logger.info(f"[*] 设置坐标偏移: ({self.offset_x}, {self.offset_y}, {self.offset_z})")

class MovementHandler:
    """移动处理器"""
    
    def __init__(self):
        self.coordinate_converter = CoordinateConverter()
    
    def convert_mc_movement_packet(self, mc_packet_data: bytes) -> bytes:
        """
        转换Minecraft移动数据包为迷你世界格式
        
        Minecraft格式（简化）:
        [x (double)] [y (double)] [z (double)] [yaw (float)] [pitch (float)] [onGround (bool)]
        """
        try:
            # 解析Minecraft数据
            if len(mc_packet_data) < 25:
                raise ValueError("数据长度不足")
            
            x, y, z = struct.unpack('<ddd', mc_packet_data[:24])
            yaw, pitch = struct.unpack('<ff', mc_packet_data[24:32])
            
            mc_pos = Vector3(x, y, z)
            
            # 转换坐标
            mnw_pos = self.coordinate_converter.mc_to_mnw_position(mc_pos)
            mnw_yaw, mnw_pitch = self.coordinate_converter.mc_to_mnw_rotation(yaw, pitch)
            
            # 构建迷你世界数据包
            # 假设格式: [command (1)] [length (1)] [x (float)] [y (float)] [z (float)] [yaw (float)] [pitch (float)]
            mnw_packet = struct.pack('<BB', 0x04, 20)  # command=move, length=20
            mnw_packet += self.coordinate_converter.serialize_position_mnw(mnw_pos)
            mnw_packet += struct.pack('<ff', mnw_yaw, mnw_pitch)
            
            return mnw_packet
        
        except Exception as e:
            logger.error(f"[-] 移动数据包转换错误: {e}")
            return b''

# 测试代码
if __name__ == "__main__":
    converter = CoordinateConverter()
    
    # 测试坐标转换
    mc_pos = Vector3(100.5, 64.0, -200.3)
    mnw_pos = converter.mc_to_mnw_position(mc_pos)
    
    print(f"Minecraft坐标: ({mc_pos.x}, {mc_pos.y}, {mc_pos.z})")
    print(f"迷你世界坐标: ({mnw_pos.x}, {mnw_pos.y}, {mnw_pos.z})")
    
    # 测试反向转换
    mc_pos_back = converter.mnw_to_mc_position(mnw_pos)
    print(f"转换回MC: ({mc_pos_back.x}, {mc_pos_back.y}, {mc_pos_back.z})")
    
    # 测试序列化
    serialized = converter.serialize_position_mnw(mnw_pos)
    print(f"序列化数据: {serialized.hex()}")
    
    deserialized = converter.deserialize_position_mnw(serialized)
    print(f"反序列化: ({deserialized.x}, {deserialized.y}, {deserialized.z})")
