#!/usr/bin/env python3
"""方块映射器 - 简化版"""
import json
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class BlockMapper:
    """方块映射器"""
    
    def __init__(self):
        self.mc_to_mnw: Dict[int, int] = {}
        self.mnw_to_mc: Dict[int, int] = {}
        self._load_default_mapping()
    
    def _load_default_mapping(self):
        """加载默认映射"""
        default = {
            0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5,
            7: 7, 12: 12, 13: 13, 14: 14, 15: 15,
            16: 16, 17: 17, 18: 18, 20: 20,
        }
        self.mc_to_mnw.update(default)
        self.mnw_to_mc = {v: k for k, v in self.mc_to_mnw.items()}
    
    def mc_to_mnw_block(self, mc_id: int, mc_meta: int = 0) -> Tuple[int, int]:
        """MC方块转MNW"""
        mnw_id = self.mc_to_mnw.get(mc_id, mc_id)
        return (mnw_id, mc_meta)
    
    def mnw_to_mc_block(self, mnw_id: int, mnw_meta: int = 0) -> Tuple[int, int]:
        """MNW方块转MC"""
        mc_id = self.mnw_to_mc.get(mnw_id, mnw_id)
        return (mc_id, mnw_meta)
