#!/usr/bin/env python3
"""
方块映射器 - 完整版
处理Minecraft和迷你世界之间的方块ID映射

支持:
1. 标准格式: {mc_id, mc_registry, mc_name, mnw_id, mnw_name, verified}
2. Go映射格式: {mnw_id, mnw_name_cn, mnw_name_en, mc_name, texture, source}
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
        
        # 如果未指定映射文件，尝试查找默认文件（优先使用Go映射）
        if mapping_file is None:
            possible_paths = [
                Path(__file__).parent.parent.parent / "data" / "mnw_block_mapping_from_go.json",
                Path("data/mnw_block_mapping_from_go.json"),
                Path(__file__).parent.parent.parent / "data" / "mnw_mc_block_mapping_v2.json",
                Path("data/mnw_mc_block_mapping_v2.json"),
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
    
    def _load_from_file(self, filepath: str):
        """从JSON文件加载映射"""
        try:
            path = Path(filepath)
            if not path.exists():
                logger.warning(f"映射文件不存在: {filepath}")
                self._load_default_mapping()
                return
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            mappings_data = data.get('mappings', [])
            if not mappings_data:
                logger.warning("映射文件为空")
                self._load_default_mapping()
                return
            
            # 检测文件格式
            first_item = mappings_data[0]
            
            if 'mnw_id' in first_item and 'mc_name' in first_item and 'mc_id' not in first_item:
                logger.info("检测到Go映射格式")
                self._load_go_format(mappings_data)
            elif 'mc_id' in first_item:
                logger.info("检测到标准映射格式")
                self._load_standard_format(mappings_data)
            else:
                logger.warning("未知的映射格式")
                self._load_default_mapping()
            
        except Exception as e:
            logger.error(f"加载映射文件失败: {e}")
            self._load_default_mapping()
    
    def _load_go_format(self, mappings_data: list):
        """加载Go映射格式"""
        for item in mappings_data:
            mnw_id = item.get('mnw_id')
            mc_name = item.get('mc_name', 'stone')
            mnw_name = item.get('mnw_name_cn', '')
            source = item.get('source', 'fallback')
            
            if mnw_id is None:
                continue
            
            mc_id = self._mc_name_to_id(mc_name)
            
            mapping = BlockMapping(
                mc_id=mc_id,
                mc_registry=f"minecraft:{mc_name}",
                mc_name=mc_name,
                mnw_id=mnw_id,
                mnw_name=mnw_name,
                verified=(source == 'community')
            )
            
            self.mappings[mc_id] = mapping
            self.mc_to_mnw[mc_id] = mnw_id
            self.mnw_to_mc[mnw_id] = mc_id
    
    def _load_standard_format(self, mappings_data: list):
        """加载标准映射格式"""
        for item in mappings_data:
            mc_id = item.get('mc_id')
            mnw_id = item.get('mnw_id')
            
            if mc_id is None or mnw_id is None:
                continue
            
            mapping = BlockMapping(
                mc_id=mc_id,
                mc_registry=item.get('mc_registry', ''),
                mc_name=item.get('mc_name', ''),
                mnw_id=mnw_id,
                mnw_name=item.get('mnw_name', ''),
                verified=item.get('verified', False)
            )
            
            self.mappings[mc_id] = mapping
            self.mc_to_mnw[mc_id] = mnw_id
            self.mnw_to_mc[mnw_id] = mc_id
    
    def _load_default_mapping(self):
        """加载默认映射"""
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
    
    def _mc_name_to_id(self, mc_name: str) -> int:
        """从MC名称推断MC ID"""
        name_to_id = {
            'air': 0, 'stone': 1, 'granite': 2, 'diorite': 3, 'andesite': 4,
            'grass_block': 5, 'dirt': 6, 'coarse_dirt': 7, 'podzol': 8,
            'cobblestone': 9, 'oak_planks': 10, 'spruce_planks': 11, 'birch_planks': 12,
            'jungle_planks': 13, 'acacia_planks': 14, 'dark_oak_planks': 15,
            'bedrock': 16, 'water': 17, 'flowing_water': 18, 'lava': 19,
            'flowing_lava': 20, 'sand': 21, 'red_sand': 22, 'gravel': 23,
            'gold_ore': 24, 'iron_ore': 25, 'coal_ore': 26, 'oak_log': 27,
            'spruce_log': 28, 'birch_log': 29, 'jungle_log': 30, 'acacia_log': 31,
            'dark_oak_log': 32, 'oak_leaves': 33, 'spruce_leaves': 34, 'birch_leaves': 35,
            'jungle_leaves': 36, 'acacia_leaves': 37, 'dark_oak_leaves': 38,
            'glass': 39, 'lapis_ore': 40, 'lapis_block': 41, 'sandstone': 42,
            'chiseled_sandstone': 43, 'cut_sandstone': 44, 'note_block': 45,
            'powered_rail': 46, 'detector_rail': 47, 'sticky_piston': 48,
            'cobweb': 49, 'short_grass': 50, 'fern': 51, 'dead_bush': 52,
            'piston': 53, 'white_wool': 54, 'orange_wool': 55, 'magenta_wool': 56,
            'light_blue_wool': 57, 'yellow_wool': 58, 'lime_wool': 59,
            'pink_wool': 60, 'gray_wool': 61, 'light_gray_wool': 62,
            'cyan_wool': 63, 'purple_wool': 64, 'blue_wool': 65, 'brown_wool': 66,
            'green_wool': 67, 'red_wool': 68, 'black_wool': 69, 'dandelion': 70,
            'poppy': 71, 'blue_orchid': 72, 'allium': 73, 'azure_bluet': 74,
            'red_tulip': 75, 'orange_tulip': 76, 'white_tulip': 77,
            'pink_tulip': 78, 'oxeye_daisy': 79, 'brown_mushroom': 80,
            'red_mushroom': 81, 'gold_block': 82, 'iron_block': 83,
            'stone_slab': 84, 'smooth_stone_slab': 85, 'sandstone_slab': 86,
            'petrified_oak_slab': 87, 'cobblestone_slab': 88, 'brick_slab': 89,
            'stone_brick_slab': 90, 'nether_brick_slab': 91, 'quartz_slab': 92,
            'bricks': 93, 'tnt': 94, 'bookshelf': 95, 'mossy_cobblestone': 96,
            'obsidian': 97, 'torch': 98, 'fire': 99, 'spawner': 100,
            'oak_stairs': 101, 'chest': 102, 'diamond_ore': 103,
            'diamond_block': 104, 'crafting_table': 105, 'wheat': 106,
            'farmland': 107, 'furnace': 108, 'oak_sign': 109, 'oak_door': 110,
            'ladder': 111, 'rail': 112, 'cobblestone_stairs': 113,
            'oak_wall_sign': 114, 'lever': 115, 'stone_pressure_plate': 116,
            'iron_door': 117, 'oak_pressure_plate': 118, 'redstone_ore': 119,
            'redstone_torch': 120, 'stone_button': 121, 'snow': 122,
            'ice': 123, 'snow_block': 124, 'cactus': 125, 'clay': 126,
            'sugar_cane': 127, 'jukebox': 128, 'oak_fence': 129,
            'pumpkin': 130, 'netherrack': 131, 'soul_sand': 132,
            'glowstone': 133, 'nether_portal': 134, 'jack_o_lantern': 135,
            'cake': 136, 'repeater': 137, 'white_stained_glass': 138,
            'oak_trapdoor': 139, 'monster_egg': 140, 'stone_bricks': 141,
            'mossy_stone_bricks': 142, 'cracked_stone_bricks': 143,
            'chiseled_stone_bricks': 144, 'iron_bars': 145, 'glass_pane': 146,
            'melon': 147, 'vine': 148, 'oak_fence_gate': 149,
            'brick_stairs': 150, 'stone_brick_stairs': 151, 'mycelium': 152,
            'lily_pad': 153, 'nether_bricks': 154, 'nether_brick_fence': 155,
            'nether_brick_stairs': 156, 'nether_wart': 157, 'enchanting_table': 158,
            'brewing_stand': 159, 'cauldron': 160, 'end_portal': 161,
            'end_portal_frame': 162, 'end_stone': 163, 'dragon_egg': 164,
            'redstone_lamp': 165, 'dropper': 166, 'activator_rail': 167,
            'cocoa': 168, 'sandstone_stairs': 169, 'emerald_ore': 170,
            'ender_chest': 171, 'tripwire_hook': 172, 'emerald_block': 173,
            'spruce_stairs': 174, 'birch_stairs': 175, 'jungle_stairs': 176,
            'command_block': 177, 'beacon': 178, 'cobblestone_wall': 179,
            'flower_pot': 180, 'carrots': 181, 'potatoes': 182,
            'oak_button': 183, 'skull': 184, 'anvil': 185, 'trapped_chest': 186,
            'light_weighted_pressure_plate': 187, 'heavy_weighted_pressure_plate': 188,
            'comparator': 189, 'daylight_detector': 190, 'redstone_block': 191,
            'quartz_ore': 192, 'hopper': 193, 'quartz_block': 194,
            'quartz_stairs': 195, 'activator_rail_dup': 196, 'dropper_dup': 197,
            'white_terracotta': 198, 'white_stained_glass_pane': 199,
            'acacia_leaves': 200, 'acacia_log': 201, 'acacia_stairs': 202,
            'dark_oak_stairs': 203, 'slime_block': 204, 'barrier': 205,
            'iron_trapdoor': 206, 'prismarine': 207, 'sea_lantern': 208,
            'hay_block': 209, 'carpet': 210, 'hardened_clay': 211,
            'coal_block': 212, 'packed_ice': 213, 'double_plant': 214,
            'standing_banner': 215, 'wall_banner': 216,
            'daylight_detector_inverted': 217, 'red_sandstone': 218,
            'red_sandstone_stairs': 219, 'spruce_fence_gate': 220,
            'birch_fence_gate': 221, 'jungle_fence_gate': 222,
            'dark_oak_fence_gate': 223, 'acacia_fence_gate': 224,
            'spruce_fence': 225, 'birch_fence': 226, 'jungle_fence': 227,
            'dark_oak_fence': 228, 'acacia_fence': 229, 'spruce_door': 230,
            'birch_door': 231, 'jungle_door': 232, 'acacia_door': 233,
            'dark_oak_door': 234, 'end_rod': 235, 'chorus_plant': 236,
            'chorus_flower': 237,
        }
        return name_to_id.get(mc_name, 1)
    
    def mc_to_mnw_block(self, mc_id: int, mc_meta: int = 0) -> Tuple[int, int]:
        """MC方块ID转MNW"""
        if mc_id < 0 or mc_id > 65535:
            logger.warning(f"无效的MC方块ID: {mc_id}")
            return (1, mc_meta)
        
        mnw_id = self.mc_to_mnw.get(mc_id, mc_id)
        return (mnw_id, mc_meta)
    
    def mnw_to_mc_block(self, mnw_id: int, mnw_meta: int = 0) -> Tuple[int, int]:
        """MNW方块ID转MC"""
        mc_id = self.mnw_to_mc.get(mnw_id, mnw_id)
        return (mc_id, mnw_meta)
    
    def get_mapping_info(self, mc_id: int) -> Optional[BlockMapping]:
        """获取映射信息"""
        return self.mappings.get(mc_id)
    
    def is_verified(self, mc_id: int) -> bool:
        """检查是否已验证"""
        mapping = self.mappings.get(mc_id)
        return mapping.verified if mapping else False
