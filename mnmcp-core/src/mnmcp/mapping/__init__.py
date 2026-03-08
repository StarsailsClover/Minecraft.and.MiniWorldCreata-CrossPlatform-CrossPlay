"""
MnMCP 映射层 — 方块 / 实体 / 物品 / 坐标 / 生物群系
v1.0.0_26w13a

合并自旧项目:
  protocol/block_mapper.py
  protocol/entity_mapper.py
  protocol/item_mapper.py
  protocol/coordinate_converter.py
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

def _get_data_dir() -> Path:
    """查找 data/ 目录 (兼容 editable install 和直接运行)"""
    candidates = [
        Path(__file__).resolve().parent.parent.parent.parent / "data",       # src/mnmcp/mapping/ → ../../../../data
        Path(__file__).resolve().parent.parent.parent.parent.parent / "data", # 多一层
        Path.cwd() / "data",
        Path(__file__).resolve().parent.parent.parent / "data",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]  # fallback

_DATA_DIR = _get_data_dir()


# ═══════════════════════════════════════════════════════════
#  坐标
# ═══════════════════════════════════════════════════════════

@dataclass
class Vec3:
    x: float
    y: float
    z: float

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def from_dict(cls, d: dict) -> "Vec3":
        return cls(d["x"], d["y"], d["z"])


class CoordinateConverter:
    """
    MC ↔ MNW 坐标转换

    规则:
      X 轴取反  (MC 东=+X, MNW 东=-X)
      Y 轴不变
      Z 轴不变
      比例 1:1
    """

    def __init__(self, *, scale: float = 1.0, offset: Vec3 | None = None):
        self.scale = scale
        self.offset = offset or Vec3(0, 0, 0)

    def mc_to_mnw(self, pos: Vec3) -> Vec3:
        return Vec3(
            -(pos.x + self.offset.x) * self.scale,
            (pos.y + self.offset.y) * self.scale,
            (pos.z + self.offset.z) * self.scale,
        )

    def mnw_to_mc(self, pos: Vec3) -> Vec3:
        return Vec3(
            -(pos.x / self.scale) - self.offset.x,
            (pos.y / self.scale) - self.offset.y,
            (pos.z / self.scale) - self.offset.z,
        )


# ═══════════════════════════════════════════════════════════
#  通用 JSON 映射加载器
# ═══════════════════════════════════════════════════════════

def _find_data_file(*candidates: str) -> Optional[Path]:
    for name in candidates:
        p = _DATA_DIR / name
        if p.exists():
            return p
    return None


def _load_json(path: Path) -> dict | list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ═══════════════════════════════════════════════════════════
#  方块映射
# ═══════════════════════════════════════════════════════════

@dataclass
class BlockMapping:
    mc_id: int
    mc_registry: str
    mc_name: str
    mnw_id: int
    mnw_name: str
    verified: bool = False


class BlockMapper:
    """双向方块 ID 映射"""

    def __init__(self, mapping_file: str | None = None):
        self.mc_to_mnw: Dict[int, int] = {}
        self.mnw_to_mc: Dict[int, int] = {}
        self.mappings: Dict[int, BlockMapping] = {}

        if mapping_file:
            self._load(Path(mapping_file))
        else:
            path = _find_data_file(
                "block_mapping_v3_complete.json",
                "block_mapping_unified.json",
                "mnw_block_mapping_from_go.json",
                "mnw_mc_block_mapping_v2.json",
                "block_mappings_extended.json",
                "block_mappings.json",
            )
            if path:
                self._load(path)
            else:
                logger.warning("未找到方块映射文件")

    # ── 公开 API ──

    def get_mnw_id(self, mc_id: int) -> int:
        return self.mc_to_mnw.get(mc_id, mc_id)

    def get_mc_id(self, mnw_id: int) -> int:
        return self.mnw_to_mc.get(mnw_id, mnw_id)

    @property
    def count(self) -> int:
        return len(self.mappings)

    # ── 加载 ──

    def _load(self, path: Path):
        data = _load_json(path)

        # 标准格式 {"mappings": [...]}
        if isinstance(data, dict) and "mappings" in data:
            for m in data["mappings"]:
                mc_id = m.get("mc_id", m.get("mc_block_id", m.get("mc_bedrock_id", -1)))
                mnw_id = m.get("mnw_id", m.get("mnw_block_id", -1))
                if mc_id >= 0 and mnw_id >= 0:
                    self.mc_to_mnw[mc_id] = mnw_id
                    self.mnw_to_mc[mnw_id] = mc_id
                    self.mappings[mc_id] = BlockMapping(
                        mc_id=mc_id,
                        mc_registry=m.get("mc_registry", m.get("mc_name", "")),
                        mc_name=m.get("mc_name", ""),
                        mnw_id=mnw_id,
                        mnw_name=m.get("mnw_name", m.get("mnw_name_cn", "")),
                        verified=m.get("verified", False),
                    )

        # Go 映射格式 [{"mnw_id":..., "mc_name":...}, ...]
        elif isinstance(data, list):
            for i, m in enumerate(data):
                mnw_id = m.get("mnw_id", i)
                mc_name = m.get("mc_name", "")
                self.mc_to_mnw[i] = mnw_id
                self.mnw_to_mc[mnw_id] = i
                self.mappings[i] = BlockMapping(
                    mc_id=i, mc_registry=mc_name, mc_name=mc_name,
                    mnw_id=mnw_id,
                    mnw_name=m.get("mnw_name_cn", m.get("mnw_name_en", "")),
                )

        logger.info(f"方块映射加载完成: {self.count} 条 ← {path.name}")


# ═══════════════════════════════════════════════════════════
#  实体映射
# ═══════════════════════════════════════════════════════════

@dataclass
class EntityMapping:
    mnw_id: int
    mnw_name_cn: str
    mnw_name_en: str
    mc_entity: str
    mc_entity_id: int
    mc_name: str
    match_type: str


class EntityMapper:
    """双向实体 ID 映射"""

    MNW_FALLBACK_ID = 3095          # 卡卡
    MC_FALLBACK_ENTITY = "minecraft:villager"
    MC_FALLBACK_ID = 15

    def __init__(self, mapping_file: str | None = None):
        self.mnw_to_mc: Dict[int, Tuple[str, int]] = {}
        self.mc_to_mnw: Dict[str, int] = {}
        self.mappings: Dict[int, EntityMapping] = {}

        if mapping_file:
            self._load(Path(mapping_file))
        else:
            path = _find_data_file("entity_mapping_v1_complete.json")
            if path:
                self._load(path)
            else:
                logger.warning("未找到实体映射文件")

    def get_mc_entity(self, mnw_id: int) -> Tuple[str, int]:
        return self.mnw_to_mc.get(mnw_id, (self.MC_FALLBACK_ENTITY, self.MC_FALLBACK_ID))

    def get_mnw_id(self, mc_entity: str) -> int:
        return self.mc_to_mnw.get(mc_entity, self.MNW_FALLBACK_ID)

    def _load(self, path: Path):
        data = _load_json(path)
        for m in data.get("mappings", []):
            mnw_id = m.get("mnw_id", -1)
            mc_entity = m.get("mc_entity", "")
            mc_id = m.get("mc_entity_id", -1)
            if mnw_id >= 0 and mc_entity:
                self.mnw_to_mc[mnw_id] = (mc_entity, mc_id)
                self.mc_to_mnw[mc_entity] = mnw_id
                self.mappings[mnw_id] = EntityMapping(
                    mnw_id=mnw_id,
                    mnw_name_cn=m.get("mnw_name_cn", ""),
                    mnw_name_en=m.get("mnw_name_en", ""),
                    mc_entity=mc_entity, mc_entity_id=mc_id,
                    mc_name=m.get("mc_name", ""),
                    match_type=m.get("match_type", ""),
                )
        logger.info(f"实体映射加载完成: {len(self.mappings)} 条 ← {path.name}")


# ═══════════════════════════════════════════════════════════
#  物品映射
# ═══════════════════════════════════════════════════════════

@dataclass
class ItemMapping:
    mnw_id: int
    mnw_name_cn: str
    mnw_name_en: str
    mc_item: str
    mc_item_id: int
    mc_name: str
    match_type: str


class ItemMapper:
    """双向物品 ID 映射"""

    MNW_FALLBACK_NAME = "TerrainEditor"
    MC_FALLBACK_ITEM = "minecraft:wooden_sword"
    MC_FALLBACK_ID = 268

    def __init__(self, mapping_file: str | None = None):
        self.mnw_to_mc: Dict[int, Tuple[str, int]] = {}
        self.mc_to_mnw: Dict[str, int] = {}
        self.mappings: Dict[int, ItemMapping] = {}

        if mapping_file:
            self._load(Path(mapping_file))
        else:
            path = _find_data_file("item_mapping_v1_complete.json")
            if path:
                self._load(path)
            else:
                logger.warning("未找到物品映射文件")

    def get_mc_item(self, mnw_id: int) -> Tuple[str, int]:
        return self.mnw_to_mc.get(mnw_id, (self.MC_FALLBACK_ITEM, self.MC_FALLBACK_ID))

    def get_mnw_id(self, mc_item: str) -> int:
        return self.mc_to_mnw.get(mc_item, -1)

    def _load(self, path: Path):
        data = _load_json(path)
        for m in data.get("mappings", []):
            mnw_id = m.get("mnw_id", -1)
            mc_item = m.get("mc_item", "")
            mc_id = m.get("mc_item_id", -1)
            if mnw_id >= 0 and mc_item:
                self.mnw_to_mc[mnw_id] = (mc_item, mc_id)
                self.mc_to_mnw[mc_item] = mnw_id
                self.mappings[mnw_id] = ItemMapping(
                    mnw_id=mnw_id,
                    mnw_name_cn=m.get("mnw_name_cn", ""),
                    mnw_name_en=m.get("mnw_name_en", ""),
                    mc_item=mc_item, mc_item_id=mc_id,
                    mc_name=m.get("mc_name", ""),
                    match_type=m.get("match_type", ""),
                )
        logger.info(f"物品映射加载完成: {len(self.mappings)} 条 ← {path.name}")
