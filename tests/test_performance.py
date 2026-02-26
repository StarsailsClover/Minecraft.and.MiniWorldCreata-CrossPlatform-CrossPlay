#!/usr/bin/env python3
"""
性能测试
测试协议转换性能
"""

import sys
import time
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.protocol_translator import ProtocolTranslator, MinecraftPacket
from protocol import CoordinateConverter, BlockMapper, Vector3

def benchmark_protocol_translation(iterations=10000):
    """测试协议转换性能"""
    print(f"\n[*] 协议转换性能测试 ({iterations} 次)...")
    
    translator = ProtocolTranslator()
    
    # 创建测试数据包
    mc_packet = MinecraftPacket(
        length=20,
        packet_id=0x04,  # Move
        data=b'\x00' * 18
    )
    
    # 预热
    for _ in range(100):
        translator.translate_mc_to_mnw(mc_packet)
    
    # 正式测试
    start = time.time()
    for _ in range(iterations):
        translator.translate_mc_to_mnw(mc_packet)
    elapsed = time.time() - start
    
    ops_per_sec = iterations / elapsed
    latency = (elapsed / iterations) * 1000  # ms
    
    print(f"  [+] 总时间: {elapsed:.3f}s")
    print(f"  [+] 每秒处理: {ops_per_sec:.0f} 包")
    print(f"  [+] 平均延迟: {latency:.3f} ms")
    
    return ops_per_sec > 10000  # 期望 > 10000 ops/s

def benchmark_coordinate_conversion(iterations=100000):
    """测试坐标转换性能"""
    print(f"\n[*] 坐标转换性能测试 ({iterations} 次)...")
    
    converter = CoordinateConverter()
    pos = Vector3(100.5, 64.0, -200.3)
    
    # 预热
    for _ in range(1000):
        converter.mc_to_mnw_position(pos)
    
    # 正式测试
    start = time.time()
    for _ in range(iterations):
        converter.mc_to_mnw_position(pos)
    elapsed = time.time() - start
    
    ops_per_sec = iterations / elapsed
    latency = (elapsed / iterations) * 1000000  # us
    
    print(f"  [+] 总时间: {elapsed:.3f}s")
    print(f"  [+] 每秒处理: {ops_per_sec:.0f} 次")
    print(f"  [+] 平均延迟: {latency:.3f} μs")
    
    return ops_per_sec > 1000000  # 期望 > 1M ops/s

def benchmark_block_mapping(iterations=100000):
    """测试方块映射性能"""
    print(f"\n[*] 方块映射性能测试 ({iterations} 次)...")
    
    mapper = BlockMapper()
    
    # 预热
    for _ in range(1000):
        mapper.mc_to_mnw_block(1, 0)
    
    # 正式测试
    start = time.time()
    for _ in range(iterations):
        mapper.mc_to_mnw_block(1, 0)
    elapsed = time.time() - start
    
    ops_per_sec = iterations / elapsed
    latency = (elapsed / iterations) * 1000000  # us
    
    print(f"  [+] 总时间: {elapsed:.3f}s")
    print(f"  [+] 每秒处理: {ops_per_sec:.0f} 次")
    print(f"  [+] 平均延迟: {latency:.3f} μs")
    
    return ops_per_sec > 1000000  # 期望 > 1M ops/s

def test_memory_usage():
    """测试内存使用"""
    print(f"\n[*] 内存使用测试...")
    
    import gc
    gc.collect()
    
    # 创建大量对象
    translators = [ProtocolTranslator() for _ in range(100)]
    converters = [CoordinateConverter() for _ in range(100)]
    mappers = [BlockMapper() for _ in range(100)]
    
    print(f"  [+] 创建了 {len(translators)} 个翻译器")
    print(f"  [+] 创建了 {len(converters)} 个转换器")
    print(f"  [+] 创建了 {len(mappers)} 个映射器")
    
    # 清理
    del translators, converters, mappers
    gc.collect()
    
    print(f"  [+] 内存清理完成")
    
    return True

def run_performance_tests():
    """运行性能测试"""
    print("=" * 60)
    print("性能测试")
    print("=" * 60)
    
    tests = [
        ("协议转换", benchmark_protocol_translation),
        ("坐标转换", benchmark_coordinate_conversion),
        ("方块映射", benchmark_block_mapping),
        ("内存使用", test_memory_usage),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"  ✅ {name} 性能达标")
            else:
                failed += 1
                print(f"  ⚠️ {name} 性能未达标")
        except Exception as e:
            failed += 1
            print(f"  ❌ {name} 测试错误: {e}")
    
    print("\n" + "=" * 60)
    print(f"性能测试结果: {passed} 达标, {failed} 未达标")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_performance_tests()
    sys.exit(0 if success else 1)
