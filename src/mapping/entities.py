"""
实体映射

Minecraft 与迷你世界实体 ID 映射
"""

import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class EntityMapper:
    """实体映射器"""
    
    # 基础实体映射表
    BASIC_MAPPING = {
        # Minecraft 实体 ID -> 迷你世界实体 ID
        "minecraft:player": (1, "Player"),
        "minecraft:zombie": (2, "Zombie"),
        "minecraft:skeleton": (3, "Skeleton"),
        "minecraft:creeper": (4, "Creeper"),
        "minecraft:spider": (5, "Spider"),
        "minecraft:enderman": (6, "Enderman"),
        "minecraft:witch": (7, "Witch"),
        "minecraft:villager": (8, "Villager"),
        "minecraft:cow": (9, "Cow"),
        "minecraft:pig": (10, "Pig"),
        "minecraft:sheep": (11, "Sheep"),
        "minecraft:chicken": (12, "Chicken"),
        "minecraft:item": (13, "ItemEntity"),
        "minecraft:arrow": (14, "Arrow"),
        "minecraft:snowball": (15, "Snowball"),
        "minecraft:egg": (16, "Egg"),
        "minecraft:painting": (17, "Painting"),
        "minecraft:boat": (18, "Boat"),
        "minecraft:minecart": (19, "Minecart"),
    }
    
    def __init__(self):
        self.mc_to_mnw: Dict[str, Tuple[int, str]] = {}
        self.mnw_to_mc: Dict[int, Tuple[str, str]] = {}
        self._load_basic_mapping()
    
    def _load_basic_mapping(self):
        """加载基础映射"""
        for mc_id, (mnw_id, mnw_name) in self.BASIC_MAPPING.items():
            self.mc_to_mnw[mc_id] = (mnw_id, mnw_name)
            self.mnw_to_mc[mnw_id] = (mc_id, mnw_name)
        
        logger.info(f"Loaded {len(self.BASIC_MAPPING)} basic entity mappings")
    
    def get_mnw_entity(self, mc_entity_id: str) -> Tuple[int, str]:
        """
        获取对应的迷你世界实体
        
        返回: (mnw_entity_id, mnw_entity_name)
        """
        return self.mc_to_mnw.get(mc_entity_id, (0, "Unknown"))
    
    def get_mc_entity(self, mnw_entity_id: int) -> Tuple[str, str]:
        """
        获取对应的 Minecraft 实体
        
        返回: (mc_entity_id, mc_entity_name)
        """
        return self.mnw_to_mc.get(mnw_entity_id, ("minecraft:unknown", "Unknown"))
    
    @property
    def count(self) -> int:
        """获取映射数量"""
        return len(self.mc_to_mnw)
