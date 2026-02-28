#!/usr/bin/env python3
"""
方块映射器 - 完整版
处理Minecraft和迷你世界之间的方块ID映射
"""

import json
import logging
from typing import Dict, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BlockMapping:
    """方块映射数据"""
    mc_id: int
    mc_registry: str
    mc_name: str
    mnw_id: int
    mnw_name: str
    verified: bool = False


class BlockMapper:
    """方块映射器"""
    
    def __init__(self, mapping_file: str = None):
        self.mc_to_mnw: Dict[int, int] = {}
        self.mnw_to_mc: Dict[int, int] = {}
        self.mappings: Dict[int, BlockMapping] = {}
        
        # 如果未指定映射文件，尝试查找默认文件（优先使用扩展映射）
        if mapping_file is None:
            # 尝试多个可能的文件路径（优先扩展映射）
            possible_paths = [
                Path(__file__).parent.parent.parent / "data" / "block_mappings_extended.json",
                Path("data/block_mappings_extended.json"),
                Path(__file__).parent.parent.parent / "data" / "block_mappings.json",
                Path("data/block_mappings.json"),
            ]
            
            for path in possible_paths:
                if path.exists():
                    mapping_file = str(path)
                    logger.info(f"找到映射文件: {mapping_file}")
                    break
        
        # 加载映射
        if mapping_file:
            self._load_from_file(mapping_file)
        else:
            logger.warning("未找到映射文件，使用默认映射")
            self._load_default_mapping()
        
        logger.info(f"方块映射器初始化完成，已加载 {len(self.mc_to_mnw)} 个映射")
    
    def _load_default_mapping(self):
        """加载默认映射（基础方块）"""
        default_mappings = [
            BlockMapping(0, "minecraft:air", "空气", 0, "air", True),
            BlockMapping(1, "minecraft:stone", "石头", 1, "stone", True),
            BlockMapping(2, "minecraft:grass_block", "草方块", 2, "grass", True),
            BlockMapping(3, "minecraft:dirt", "泥土", 3, "dirt", True),
            BlockMapping(4, "minecraft:cobblestone", "圆石", 4, "cobblestone", True),
            BlockMapping(5, "minecraft:oak_planks", "橡木木板", 5, "wood_plank", True),
            BlockMapping(7, "minecraft:bedrock", "基岩", 7, "bedrock", True),
            BlockMapping(12, "minecraft:sand", "沙子", 12, "sand", True),
            BlockMapping(13, "minecraft:gravel", "砾石", 13, "gravel", True),
            BlockMapping(14, "minecraft:gold_ore", "金矿石", 14, "gold_ore", True),
            BlockMapping(15, "minecraft:iron_ore", "铁矿石", 15, "iron_ore", True),
            BlockMapping(16, "minecraft:coal_ore", "煤矿石", 16, "coal_ore", True),
            BlockMapping(17, "minecraft:oak_log", "橡木原木", 17, "wood_log", True),
            BlockMapping(18, "minecraft:oak_leaves", "橡木树叶", 18, "leaves", True),
            BlockMapping(20, "minecraft:glass", "玻璃", 20, "glass", True),
        ]
        
        for mapping in default_mappings:
            self.mappings[mapping.mc_id] = mapping
            self.mc_to_mnw[mapping.mc_id] = mapping.mnw_id
            self.mnw_to_mc[mapping.mnw_id] = mapping.mc_id
    
    def _load_from_file(self, filepath: str):
        """
        从JSON文件加载映射
        
        Args:
            filepath: 映射文件路径
        """
        try:
            path = Path(filepath)
            if not path.exists():
                logger.warning(f"映射文件不存在: {filepath}，使用默认映射")
                self._load_default_mapping()
                return
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            mappings_data = data.get('mappings', [])
            for item in mappings_data:
                mapping = BlockMapping(
                    mc_id=item['mc_id'],
                    mc_registry=item['mc_registry'],
                    mc_name=item['mc_name'],
                    mnw_id=item['mnw_id'],
                    mnw_name=item['mnw_name'],
                    verified=item.get('verified', False)
                )
                
                self.mappings[mapping.mc_id] = mapping
                self.mc_to_mnw[mapping.mc_id] = mapping.mnw_id
                self.mnw_to_mc[mapping.mnw_id] = mapping.mc_id
            
            logger.info(f"从文件加载了 {len(self.mappings)} 个方块映射")
            
        except Exception as e:
            logger.error(f"加载映射文件失败: {e}，使用默认映射")
            self._load_default_mapping()
    
    def mc_to_mnw_block(self, mc_id: int, mc_meta: int = 0) -> Tuple[int, int]:
        """
        将Minecraft方块ID转换为迷你世界方块ID
        
        Args:
            mc_id: Minecraft方块ID
            mc_meta: Minecraft方块元数据
            
        Returns:
            (迷你世界方块ID, 元数据)
        """
        try:
            # 检查ID范围
            if mc_id < 0 or mc_id > 65535:
                logger.warning(f"无效的MC方块ID: {mc_id}，使用默认ID 1 (石头)")
                return (1, mc_meta)
            
            mnw_id = self.mc_to_mnw.get(mc_id, mc_id)
            
            if mnw_id != mc_id:
                logger.debug(f"方块映射: MC {mc_id} -> MNW {mnw_id}")
            else:
                logger.debug(f"方块未映射: MC {mc_id}，使用原ID")
            
            return (mnw_id, mc_meta)
            
        except Exception as e:
            logger.error(f"方块映射失败 (MC->MNW): {e}")
            return (mc_id, mc_meta)  # fallback到原ID
    
    def mnw_to_mc_block(self, mnw_id: int, mnw_meta: int = 0) -> Tuple[int, int]:
        """
        将迷你世界方块ID转换为Minecraft方块ID
        
        Args:
            mnw_id: 迷你世界方块ID
            mnw_meta: 迷你世界方块元数据
            
        Returns:
            (Minecraft方块ID, 元数据)
        """
        try:
            # 检查ID范围
            if mnw_id < 0 or mnw_id > 65535:
                logger.warning(f"无效的MNW方块ID: {mnw_id}，使用默认ID 1 (石头)")
                return (1, mnw_meta)
            
            mc_id = self.mnw_to_mc.get(mnw_id, mnw_id)
            
            if mc_id != mnw_id:
                logger.debug(f"方块映射: MNW {mnw_id} -> MC {mc_id}")
            else:
                logger.debug(f"方块未映射: MNW {mnw_id}，使用原ID")
            
            return (mc_id, mnw_meta)
            
        except Exception as e:
            logger.error(f"方块映射失败 (MNW->MC): {e}")
            return (mnw_id, mnw_meta)  # fallback到原ID
    
    def get_mc_block_info(self, mc_id: int) -> Optional[BlockMapping]:
        """
        获取Minecraft方块信息
        
        Args:
            mc_id: Minecraft方块ID
            
        Returns:
            方块映射信息或None
        """
        return self.mappings.get(mc_id)
    
    def get_mc_block_name(self, mc_id: int) -> str:
        """获取Minecraft方块名称"""
        mapping = self.mappings.get(mc_id)
        return mapping.mc_name if mapping else f"未知方块({mc_id})"
    
    def get_mnw_block_name(self, mnw_id: int) -> str:
        """获取迷你世界方块名称"""
        mc_id = self.mnw_to_mc.get(mnw_id)
        if mc_id:
            mapping = self.mappings.get(mc_id)
            return mapping.mnw_name if mapping else f"未知方块({mnw_id})"
        return f"未知方块({mnw_id})"
    
    def add_mapping(self, mc_id: int, mnw_id: int, mc_name: str = "", 
                   mnw_name: str = "", verified: bool = False):
        """
        添加新的方块映射
        
        Args:
            mc_id: Minecraft方块ID
            mnw_id: 迷你世界方块ID
            mc_name: Minecraft方块名称
            mnw_name: 迷你世界方块名称
            verified: 是否已验证
        """
        mapping = BlockMapping(
            mc_id=mc_id,
            mc_registry=f"minecraft:block_{mc_id}",
            mc_name=mc_name or f"方块{mc_id}",
            mnw_id=mnw_id,
            mnw_name=mnw_name or f"block_{mnw_id}",
            verified=verified
        )
        
        self.mappings[mc_id] = mapping
        self.mc_to_mnw[mc_id] = mnw_id
        self.mnw_to_mc[mnw_id] = mc_id
        
        logger.info(f"添加方块映射: MC {mc_id} ({mc_name}) <-> MNW {mnw_id} ({mnw_name})")
    
    def save_to_file(self, filepath: str):
        """
        保存映射到JSON文件
        
        Args:
            filepath: 保存路径
        """
        try:
            data = {
                "version": "1.0.0",
                "mc_version": "1.20.6",
                "mnw_version": "1.53.1",
                "last_updated": "2026-02-27",
                "mappings": []
            }
            
            for mapping in self.mappings.values():
                data["mappings"].append({
                    "mc_id": mapping.mc_id,
                    "mc_registry": mapping.mc_registry,
                    "mc_name": mapping.mc_name,
                    "mnw_id": mapping.mnw_id,
                    "mnw_name": mapping.mnw_name,
                    "verified": mapping.verified
                })
            
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"方块映射已保存到: {filepath}")
            
        except Exception as e:
            logger.error(f"保存映射文件失败: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """获取映射统计"""
        verified_count = sum(1 for m in self.mappings.values() if m.verified)
        return {
            "total_mappings": len(self.mappings),
            "verified_mappings": verified_count,
            "unverified_mappings": len(self.mappings) - verified_count
        }
