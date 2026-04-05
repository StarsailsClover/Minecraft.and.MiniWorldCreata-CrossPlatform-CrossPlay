"""
方块映射

Minecraft 与迷你世界方块 ID 映射
"""

import json
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class BlockMapper:
    """方块映射器"""
    
    # 基础方块映射表 (简化版)
    BASIC_MAPPING = {
        # Minecraft ID -> 迷你世界 ID
        0: (0, 0),      # air -> air
        1: (1, 0),      # stone -> stone
        2: (2, 0),      # grass -> grass
        3: (3, 0),      # dirt -> dirt
        4: (4, 0),      # cobblestone -> cobblestone
        5: (5, 0),      # planks -> planks
        7: (7, 0),      # bedrock -> bedrock
        9: (9, 0),      # water -> water
        11: (11, 0),    # lava -> lava
        12: (12, 0),    # sand -> sand
        13: (13, 0),    # gravel -> gravel
        14: (14, 0),    # gold_ore -> gold_ore
        15: (15, 0),    # iron_ore -> iron_ore
        16: (16, 0),    # coal_ore -> coal_ore
        17: (17, 0),    # log -> log
        18: (18, 0),    # leaves -> leaves
        20: (20, 0),    # glass -> glass
        41: (41, 0),    # gold_block -> gold_block
        42: (42, 0),    # iron_block -> iron_block
        43: (43, 0),    # double_stone_slab -> double_stone_slab
        44: (44, 0),    # stone_slab -> stone_slab
        45: (45, 0),    # brick_block -> brick_block
        46: (46, 0),    # tnt -> tnt
        47: (47, 0),    # bookshelf -> bookshelf
        48: (48, 0),    # mossy_cobblestone -> mossy_cobblestone
        49: (49, 0),    # obsidian -> obsidian
        50: (50, 0),    # torch -> torch
        52: (52, 0),    # mob_spawner -> mob_spawner
        54: (54, 0),    # chest -> chest
        56: (56, 0),    # diamond_ore -> diamond_ore
        57: (57, 0),    # diamond_block -> diamond_block
        58: (58, 0),    # crafting_table -> crafting_table
        60: (60, 0),    # farmland -> farmland
        61: (61, 0),    # furnace -> furnace
        73: (73, 0),    # redstone_ore -> redstone_ore
        98: (98, 0),    # stonebrick -> stonebrick
    }
    
    def __init__(self, mapping_file: Optional[Path] = None):
        self.mc_to_mnw: Dict[int, Tuple[int, int]] = {}
        self.mnw_to_mc: Dict[int, Tuple[int, int]] = {}
        
        # 加载基础映射
        self._load_basic_mapping()
        
        # 如果提供了映射文件，加载它
        if mapping_file and mapping_file.exists():
            self._load_from_file(mapping_file)
    
    def _load_basic_mapping(self):
        """加载基础映射"""
        for mc_id, (mnw_id, meta) in self.BASIC_MAPPING.items():
            self.mc_to_mnw[mc_id] = (mnw_id, meta)
            self.mnw_to_mc[mnw_id] = (mc_id, meta)
        
        logger.info(f"Loaded {len(self.BASIC_MAPPING)} basic block mappings")
    
    def _load_from_file(self, path: Path):
        """从文件加载映射"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data.get('mappings', []):
                mc_id = item.get('mc_id', item.get('mc_bedrock_id', -1))
                mnw_id = item.get('mnw_id', -1)
                
                if mc_id >= 0 and mnw_id >= 0:
                    self.mc_to_mnw[mc_id] = (mnw_id, 0)
                    self.mnw_to_mc[mnw_id] = (mc_id, 0)
            
            logger.info(f"Loaded {len(data.get('mappings', []))} mappings from file")
        except Exception as e:
            logger.error(f"Failed to load mapping file: {e}")
    
    def get_mnw_block(self, mc_block_id: int, mc_meta: int = 0) -> Tuple[int, int]:
        """
        获取对应的迷你世界方块
        
        返回: (mnw_block_id, mnw_meta)
        """
        return self.mc_to_mnw.get(mc_block_id, (mc_block_id, mc_meta))
    
    def get_mc_block(self, mnw_block_id: int, mnw_meta: int = 0) -> Tuple[int, int]:
        """
        获取对应的 Minecraft 方块
        
        返回: (mc_block_id, mc_meta)
        """
        return self.mnw_to_mc.get(mnw_block_id, (mnw_block_id, mnw_meta))
    
    def add_mapping(self, mc_id: int, mnw_id: int, mc_meta: int = 0, mnw_meta: int = 0):
        """添加映射"""
        self.mc_to_mnw[mc_id] = (mnw_id, mnw_meta)
        self.mnw_to_mc[mnw_id] = (mc_id, mc_meta)
    
    @property
    def count(self) -> int:
        """获取映射数量"""
        return len(self.mc_to_mnw)
