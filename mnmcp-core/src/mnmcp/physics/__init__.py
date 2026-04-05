"""
MnMCP 物理层 — 游戏算法差异处理
v1.0.0_26w13a

所有算法差异以迷你世界为准。
来源: csvdef/tooldef.csv, csvdef/enchant.csv, csvdef/buffdef.csv
"""

from __future__ import annotations

import math
import logging
from dataclasses import dataclass
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ProjectileParams:
    gravity: float = 0.05
    initial_speed: float = 1.5
    drag: float = 0.01
    damage_base: float = 4.0
    damage_velocity_mult: float = 0.5
    max_distance: float = 64.0


@dataclass
class CombatParams:
    attack_cooldown_ticks: int = 10
    knockback_base: float = 0.4
    crit_multiplier: float = 1.5
    armor_reduction_factor: float = 0.04


# MNW 投射物参数 (从 tooldef.csv)
MNW_PROJECTILES: Dict[str, ProjectileParams] = {
    "arrow": ProjectileParams(gravity=0.05, initial_speed=1.5, drag=0.01, damage_base=4.0),
    "spear": ProjectileParams(gravity=0.08, initial_speed=1.2, drag=0.015, damage_base=6.0, damage_velocity_mult=0.3),
    "snowball": ProjectileParams(gravity=0.03, initial_speed=1.5, drag=0.01, damage_base=0.0, damage_velocity_mult=0.0),
    "ender_pearl": ProjectileParams(gravity=0.06, initial_speed=1.5, drag=0.01, damage_base=0.0, damage_velocity_mult=0.0),
}

# MC 投射物参数 (用于转换)
MC_PROJECTILES: Dict[str, dict] = {
    "arrow": {"gravity": 0.05, "speed": 3.0, "drag": 0.01},
    "spear": {"gravity": 0.05, "speed": 2.5, "drag": 0.01},
    "snowball": {"gravity": 0.03, "speed": 1.5, "drag": 0.01},
}


def simulate_trajectory(params: ProjectileParams, angle_deg: float,
                        steps: int = 200) -> list[Tuple[float, float]]:
    """模拟投射物轨迹 (2D: distance, height)"""
    angle = math.radians(angle_deg)
    vx = params.initial_speed * math.cos(angle)
    vy = params.initial_speed * math.sin(angle)
    x, y = 0.0, 0.0
    points = [(x, y)]

    for _ in range(steps):
        vx *= (1 - params.drag)
        vy -= params.gravity
        vy *= (1 - params.drag)
        x += vx
        y += vy
        if y < 0:
            break
        if x > params.max_distance:
            break
        points.append((x, y))

    return points


def convert_mc_damage_to_mnw(mc_damage: float, weapon_type: str = "sword") -> float:
    """将 MC 伤害值转换为 MNW 等效值"""
    combat = CombatParams()
    # MNW 伤害公式与 MC 不同, 这里做近似转换
    # MC 基础伤害通常更高, MNW 攻速更快
    return mc_damage * 0.8  # 近似系数, 需要实际测试校准
