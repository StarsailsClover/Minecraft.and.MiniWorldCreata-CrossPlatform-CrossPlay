"""
物品映射

Minecraft 与迷你世界物品 ID 映射
"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class ItemMapper:
    """物品映射器"""
    
    # 基础物品映射表
    BASIC_MAPPING = {
        # Minecraft 物品 ID -> 迷你世界物品 ID
        "minecraft:stone": (1, "Stone"),
        "minecraft:grass": (2, "Grass"),
        "minecraft:dirt": (3, "Dirt"),
        "minecraft:cobblestone": (4, "Cobblestone"),
        "minecraft:planks": (5, "Planks"),
        "minecraft:sapling": (6, "Sapling"),
        "minecraft:bedrock": (7, "Bedrock"),
        "minecraft:sand": (12, "Sand"),
        "minecraft:gravel": (13, "Gravel"),
        "minecraft:gold_ore": (14, "Gold Ore"),
        "minecraft:iron_ore": (15, "Iron Ore"),
        "minecraft:coal_ore": (16, "Coal Ore"),
        "minecraft:log": (17, "Log"),
        "minecraft:leaves": (18, "Leaves"),
        "minecraft:glass": (20, "Glass"),
        "minecraft:lapis_ore": (21, "Lapis Ore"),
        "minecraft:lapis_block": (22, "Lapis Block"),
        "minecraft:sandstone": (24, "Sandstone"),
        "minecraft:bed": (26, "Bed"),
        "minecraft:golden_rail": (27, "Powered Rail"),
        "minecraft:detector_rail": (28, "Detector Rail"),
        "minecraft:sticky_piston": (29, "Sticky Piston"),
        "minecraft:web": (30, "Web"),
        "minecraft:tallgrass": (31, "Tall Grass"),
        "minecraft:deadbush": (32, "Dead Bush"),
        "minecraft:piston": (33, "Piston"),
        "minecraft:wool": (35, "Wool"),
        "minecraft:yellow_flower": (37, "Dandelion"),
        "minecraft:red_flower": (38, "Poppy"),
        "minecraft:brown_mushroom": (39, "Brown Mushroom"),
        "minecraft:red_mushroom": (40, "Red Mushroom"),
        "minecraft:gold_block": (41, "Gold Block"),
        "minecraft:iron_block": (42, "Iron Block"),
        "minecraft:stone_slab": (44, "Stone Slab"),
        "minecraft:brick_block": (45, "Brick Block"),
        "minecraft:tnt": (46, "TNT"),
        "minecraft:bookshelf": (47, "Bookshelf"),
        "minecraft:mossy_cobblestone": (48, "Mossy Cobblestone"),
        "minecraft:obsidian": (49, "Obsidian"),
        "minecraft:torch": (50, "Torch"),
        "minecraft:fire": (51, "Fire"),
        "minecraft:mob_spawner": (52, "Mob Spawner"),
        "minecraft:oak_stairs": (53, "Oak Stairs"),
        "minecraft:chest": (54, "Chest"),
        "minecraft:diamond_ore": (56, "Diamond Ore"),
        "minecraft:diamond_block": (57, "Diamond Block"),
        "minecraft:crafting_table": (58, "Crafting Table"),
        "minecraft:furnace": (61, "Furnace"),
        "minecraft:ladder": (65, "Ladder"),
        "minecraft:rail": (66, "Rail"),
        "minecraft:stone_stairs": (67, "Cobblestone Stairs"),
        "minecraft:lever": (69, "Lever"),
        "minecraft:stone_pressure_plate": (70, "Stone Pressure Plate"),
        "minecraft:wooden_pressure_plate": (72, "Wooden Pressure Plate"),
        "minecraft:redstone_ore": (73, "Redstone Ore"),
        "minecraft:redstone_torch": (76, "Redstone Torch"),
        "minecraft:stone_button": (77, "Stone Button"),
        "minecraft:snow_layer": (78, "Snow"),
        "minecraft:ice": (79, "Ice"),
        "minecraft:snow": (80, "Snow Block"),
        "minecraft:cactus": (81, "Cactus"),
        "minecraft:clay": (82, "Clay"),
        "minecraft:reeds": (83, "Sugar Cane"),
        "minecraft:fence": (85, "Fence"),
        "minecraft:pumpkin": (86, "Pumpkin"),
        "minecraft:netherrack": (87, "Netherrack"),
        "minecraft:soul_sand": (88, "Soul Sand"),
        "minecraft:glowstone": (89, "Glowstone"),
        "minecraft:lit_pumpkin": (91, "Jack o'Lantern"),
        "minecraft:trapdoor": (96, "Trapdoor"),
        "minecraft:stonebrick": (98, "Stone Bricks"),
        "minecraft:brown_mushroom_block": (99, "Brown Mushroom Block"),
        "minecraft:red_mushroom_block": (100, "Red Mushroom Block"),
        "minecraft:iron_bars": (101, "Iron Bars"),
        "minecraft:glass_pane": (102, "Glass Pane"),
        "minecraft:melon_block": (103, "Melon"),
        "minecraft:vine": (106, "Vines"),
        "minecraft:fence_gate": (107, "Fence Gate"),
        "minecraft:brick_stairs": (108, "Brick Stairs"),
        "minecraft:stone_brick_stairs": (109, "Stone Brick Stairs"),
        "minecraft:mycelium": (110, "Mycelium"),
        "minecraft:waterlily": (111, "Lily Pad"),
        "minecraft:nether_brick": (112, "Nether Brick"),
        "minecraft:nether_brick_fence": (113, "Nether Brick Fence"),
        "minecraft:nether_brick_stairs": (114, "Nether Brick Stairs"),
        "minecraft:enchanting_table": (116, "Enchanting Table"),
        "minecraft:end_portal": (119, "End Portal"),
        "minecraft:end_portal_frame": (120, "End Portal Frame"),
        "minecraft:end_stone": (121, "End Stone"),
        "minecraft:dragon_egg": (122, "Dragon Egg"),
        "minecraft:redstone_lamp": (123, "Redstone Lamp"),
        "minecraft:ender_chest": (130, "Ender Chest"),
        "minecraft:emerald_ore": (129, "Emerald Ore"),
        "minecraft:emerald_block": (133, "Emerald Block"),
        "minecraft:beacon": (138, "Beacon"),
        "minecraft:cobblestone_wall": (139, "Cobblestone Wall"),
        "minecraft:flower_pot": (140, "Flower Pot"),
        "minecraft:carrots": (141, "Carrots"),
        "minecraft:potatoes": (142, "Potatoes"),
        "minecraft:wooden_button": (143, "Wooden Button"),
        "minecraft:skull": (144, "Mob Head"),
        "minecraft:anvil": (145, "Anvil"),
        "minecraft:trapped_chest": (146, "Trapped Chest"),
        "minecraft:light_weighted_pressure_plate": (147, "Weighted Pressure Plate (Light)"),
        "minecraft:heavy_weighted_pressure_plate": (148, "Weighted Pressure Plate (Heavy)"),
        "minecraft:quartz_ore": (153, "Nether Quartz Ore"),
        "minecraft:hopper": (154, "Hopper"),
        "minecraft:quartz_block": (155, "Quartz Block"),
        "minecraft:quartz_stairs": (156, "Quartz Stairs"),
        "minecraft:activator_rail": (157, "Activator Rail"),
        "minecraft:dropper": (158, "Dropper"),
        "minecraft:stained_hardened_clay": (159, "Stained Clay"),
        "minecraft:stained_glass_pane": (160, "Stained Glass Pane"),
        "minecraft:leaves2": (161, "Leaves"),
        "minecraft:log2": (162, "Log"),
        "minecraft:acacia_stairs": (163, "Acacia Stairs"),
        "minecraft:dark_oak_stairs": (164, "Dark Oak Stairs"),
        "minecraft:hay_block": (170, "Hay Bale"),
        "minecraft:carpet": (171, "Carpet"),
        "minecraft:hardened_clay": (172, "Hardened Clay"),
        "minecraft:coal_block": (173, "Coal Block"),
        "minecraft:packed_ice": (174, "Packed Ice"),
        "minecraft:double_plant": (175, "Large Flowers"),
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
        
        logger.info(f"Loaded {len(self.BASIC_MAPPING)} basic item mappings")
    
    def get_mnw_item(self, mc_item_id: str) -> Tuple[int, str]:
        """
        获取对应的迷你世界物品
        
        返回: (mnw_item_id, mnw_item_name)
        """
        return self.mc_to_mnw.get(mc_item_id, (0, "Unknown"))
    
    def get_mc_item(self, mnw_item_id: int) -> Tuple[str, str]:
        """
        获取对应的 Minecraft 物品
        
        返回: (mc_item_id, mc_item_name)
        """
        return self.mnw_to_mc.get(mnw_item_id, ("minecraft:unknown", "Unknown"))
    
    @property
    def count(self) -> int:
        """获取映射数量"""
        return len(self.mc_to_mnw)
