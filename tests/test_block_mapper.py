#!/usr/bin/env python3
"""
方块映射器真实测试 - Phase 4
测试BlockID映射功能
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol.block_mapper import BlockMapper


class TestBlockMapper:
    """方块映射器测试"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        self.mapper = None
    
    def test(self, name: str, condition: bool, details: str = ""):
        """记录测试结果"""
        if condition:
            self.passed += 1
            status = "✓"
        else:
            self.failed += 1
            status = "✗"
        
        self.tests.append((name, status, details))
        return condition
    
    def run_all(self):
        """运行所有测试"""
        print("=" * 70)
        print(" 方块映射器真实测试")
        print("=" * 70)
        
        # 初始化映射器
        print("\n[初始化] 加载方块映射...")
        try:
            self.mapper = BlockMapper()
            self.test(
                "映射器初始化",
                len(self.mapper.mc_to_mnw) > 0,
                f"加载了 {len(self.mapper.mc_to_mnw)} 个映射"
            )
        except Exception as e:
            self.test("映射器初始化", False, f"异常: {e}")
            self._print_results()
            return
        
        # 测试基本映射
        self._test_basic_mapping()
        
        # 测试关键方块
        self._test_critical_blocks()
        
        # 测试双向映射
        self._test_bidirectional_mapping()
        
        # 测试ID 111修复
        self._test_id_111_fix()
        
        # 打印结果
        self._print_results()
    
    def _test_basic_mapping(self):
        """测试基本映射功能"""
        print("\n[测试] 基本映射功能...")
        
        # 测试MC到MNW
        mc_id = 1  # stone
        mnw_id = self.mapper.mc_to_mnw.get(mc_id)
        self.test(
            "MC->MNW 映射",
            mnw_id is not None,
            f"MC ID {mc_id} -> MNW ID {mnw_id}"
        )
        
        # 测试MNW到MC
        mnw_id = 1
        mc_id = self.mapper.mnw_to_mc.get(mnw_id)
        self.test(
            "MNW->MC 映射",
            mc_id is not None,
            f"MNW ID {mnw_id} -> MC ID {mc_id}"
        )
    
    def _test_critical_blocks(self):
        """测试关键方块"""
        print("\n[测试] 关键方块映射...")
        
        critical_blocks = [
            (0, "air", "空气"),
            (1, "stone", "石头"),
            (5, "grass_block", "草方块"),
            (6, "dirt", "泥土"),
            (16, "bedrock", "基岩"),
            (17, "water", "水"),
            (19, "lava", "岩浆"),
        ]
        
        for mc_id, mc_name, cn_name in critical_blocks:
            mnw_id = self.mapper.mc_to_mnw.get(mc_id)
            success = mnw_id is not None
            
            self.test(
                f"关键方块: {cn_name}",
                success,
                f"MC ID {mc_id} ({mc_name}) -> MNW ID {mnw_id}"
            )
    
    def _test_bidirectional_mapping(self):
        """测试双向映射一致性"""
        print("\n[测试] 双向映射一致性...")
        
        # 测试几个关键ID
        test_ids = [1, 5, 6, 16, 17]
        
        for mc_id in test_ids:
            mnw_id = self.mapper.mc_to_mnw.get(mc_id)
            if mnw_id is not None:
                mc_id_back = self.mapper.mnw_to_mc.get(mnw_id)
                consistent = mc_id_back == mc_id
                
                self.test(
                    f"双向一致性 MC ID {mc_id}",
                    consistent,
                    f"MC {mc_id} -> MNW {mnw_id} -> MC {mc_id_back}"
                )
            else:
                self.test(f"双向一致性 MC ID {mc_id}", False, "无映射")
    
    def _test_id_111_fix(self):
        """测试ID 111修复"""
        print("\n[测试] ID 111修复验证...")
        
        # MNW ID 111应该映射到stone
        mc_id = self.mapper.mnw_to_mc.get(111)
        
        if mc_id is not None:
            mapping = self.mapper.mappings.get(mc_id)
            if mapping:
                self.test(
                    "ID 111映射存在",
                    True,
                    f"MNW ID 111 -> MC ID {mc_id} ({mapping.mc_name})"
                )
                
                self.test(
                    "ID 111映射为stone",
                    mapping.mc_name == "stone",
                    f"MC名称: {mapping.mc_name}"
                )
            else:
                self.test("ID 111映射信息", False, "无映射信息")
        else:
            self.test("ID 111映射", False, "MNW ID 111未映射")
    
    def _print_results(self):
        """打印测试结果"""
        print("\n" + "=" * 70)
        print(" 测试结果")
        print("=" * 70)
        
        for name, status, details in self.tests:
            print(f"  [{status}] {name}")
            if details:
                print(f"       {details}")
        
        print("\n" + "=" * 70)
        print(f" 通过: {self.passed}")
        print(f" 失败: {self.failed}")
        print(f" 总计: {self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n ✓ 所有测试通过!")
        else:
            print(f"\n ✗ {self.failed}个测试失败")
        
        print("=" * 70)


if __name__ == "__main__":
    tester = TestBlockMapper()
    tester.run_all()
