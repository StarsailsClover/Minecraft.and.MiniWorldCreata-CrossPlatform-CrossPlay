"""
坐标转换

Minecraft 与迷你世界坐标系统转换
"""

import struct
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class Vec3:
    """3D 向量"""
    x: float
    y: float
    z: float
    
    def to_dict(self) -> Dict[str, float]:
        return {'x': self.x, 'y': self.y, 'z': self.z}
    
    @classmethod
    def from_dict(cls, d: Dict[str, float]) -> 'Vec3':
        return cls(d['x'], d['y'], d['z'])
    
    def to_bytes(self) -> bytes:
        """转换为字节 (3 x float32, big-endian)"""
        return struct.pack('>fff', self.x, self.y, self.z)
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'Vec3':
        """从字节解析"""
        x, y, z = struct.unpack('>fff', data[:12])
        return cls(x, y, z)


class CoordinateConverter:
    """坐标转换器"""
    
    def __init__(self, scale: float = 1.0):
        self.scale = scale
    
    def mc_to_mnw(self, pos: Vec3) -> Vec3:
        """
        Minecraft 坐标 -> 迷你世界坐标
        
        转换规则:
        - X 轴取反 (MC 东为正, MNW 西为正)
        - Y 轴相同
        - Z 轴相同
        - 应用缩放
        """
        return Vec3(
            x=-pos.x * self.scale,
            y=pos.y * self.scale,
            z=pos.z * self.scale
        )
    
    def mnw_to_mc(self, pos: Vec3) -> Vec3:
        """
        迷你世界坐标 -> Minecraft 坐标
        
        转换规则:
        - X 轴取反
        - Y 轴相同
        - Z 轴相同
        - 应用缩放
        """
        return Vec3(
            x=-pos.x / self.scale,
            y=pos.y / self.scale,
            z=pos.z / self.scale
        )
    
    def mc_block_to_mnw(self, block_id: int, block_meta: int = 0) -> Tuple[int, int]:
        """
        Minecraft 方块 -> 迷你世界方块
        
        返回: (mnw_block_id, mnw_block_meta)
        """
        # TODO: 实现方块映射
        return (block_id, block_meta)
    
    def mnw_block_to_mc(self, mnw_block_id: int, mnw_block_meta: int = 0) -> Tuple[int, int]:
        """
        迷你世界方块 -> Minecraft 方块
        
        返回: (mc_block_id, mc_block_meta)
        """
        # TODO: 实现方块映射
        return (mnw_block_id, mnw_block_meta)
