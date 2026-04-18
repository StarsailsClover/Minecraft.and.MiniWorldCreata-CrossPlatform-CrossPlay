"""
性能测试与优化
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import struct
import zlib
import time
import asyncio
from dataclasses import dataclass
from typing import Optional, List
import gc

# 模拟 WPKG 编解码器
class WPKGCodec:
    def __init__(self):
        self.seq_counter = 0
    
    def encode(self, payload: bytes, compress: bool = False, encrypt: bool = False) -> Optional[bytes]:
        if compress:
            payload = zlib.compress(payload)
        # 简化编码
        header = struct.pack('>HHI', 0xABCD, 0x0103, len(payload))
        self.seq_counter += 1
        return header + payload
    
    def decode(self, data: bytes) -> Optional[bytes]:
        if len(data) < 8:
            return None
        payload_len = struct.unpack('>I', data[4:8])[0]
        payload = data[8:8+payload_len]
        # 检查压缩
        try:
            return zlib.decompress(payload)
        except:
            return payload


class PerformanceTest:
    """性能测试"""
    
    def __init__(self):
        self.results = {}
    
    def test_wpkg_throughput(self):
        """测试 WPKG 编解码吞吐量"""
        print("\n" + "=" * 60)
        print("性能测试: WPKG 编解码吞吐量")
        print("=" * 60)
        
        codec = WPKGCodec()
        test_data = b"Hello, MnMCP! " * 100  # 1.4KB
        iterations = 10000
        
        # 无压缩
        start = time.time()
        for _ in range(iterations):
            encoded = codec.encode(test_data, compress=False)
            decoded = codec.decode(encoded)
        elapsed = time.time() - start
        
        throughput = (iterations * len(test_data)) / elapsed / 1024 / 1024  # MB/s
        print(f"\n无压缩:")
        print(f"  迭代次数: {iterations}")
        print(f"  总数据量: {iterations * len(test_data) / 1024:.1f} KB")
        print(f"  耗时: {elapsed:.3f} s")
        print(f"  吞吐量: {throughput:.2f} MB/s")
        print(f"  平均延迟: {elapsed/iterations*1000:.3f} ms/op")
        
        # 带压缩
        codec2 = WPKGCodec()
        start = time.time()
        for _ in range(iterations):
            encoded = codec2.encode(test_data, compress=True)
            decoded = codec2.decode(encoded)
        elapsed = time.time() - start
        
        throughput = (iterations * len(test_data)) / elapsed / 1024 / 1024
        print(f"\n带压缩:")
        print(f"  迭代次数: {iterations}")
        print(f"  总数据量: {iterations * len(test_data) / 1024:.1f} KB")
        print(f"  耗时: {elapsed:.3f} s")
        print(f"  吞吐量: {throughput:.2f} MB/s")
        print(f"  平均延迟: {elapsed/iterations*1000:.3f} ms/op")
        
        self.results['wpkg_throughput'] = throughput
        return throughput > 10  # 至少 10 MB/s
    
    def test_memory_usage(self):
        """测试内存使用"""
        print("\n" + "=" * 60)
        print("性能测试: 内存使用")
        print("=" * 60)
        
        gc.collect()
        
        # 记录初始内存
        import sys
        initial_objects = len(gc.get_objects())
        
        # 创建大量数据包
        codec = WPKGCodec()
        packets = []
        for i in range(1000):
            data = f"Packet {i}: " + "X" * 100
            encoded = codec.encode(data.encode())
            packets.append(encoded)
        
        # 记录内存使用
        current_objects = len(gc.get_objects())
        
        # 清理
        del packets
        gc.collect()
        
        final_objects = len(gc.get_objects())
        
        print(f"\n内存使用:")
        print(f"  初始对象数: {initial_objects}")
        print(f"  创建1000个数据包后: {current_objects}")
        print(f"  清理后: {final_objects}")
        print(f"  内存泄漏: {final_objects - initial_objects} 个对象")
        
        self.results['memory_leak'] = final_objects - initial_objects
        return final_objects - initial_objects < 100  # 泄漏小于100个对象
    
    def test_concurrent_connections(self):
        """测试并发连接"""
        print("\n" + "=" * 60)
        print("性能测试: 并发连接")
        print("=" * 60)
        
        async def simulate_connection(conn_id: int):
            # 模拟连接和消息交换
            await asyncio.sleep(0.01)  # 模拟连接延迟
            for _ in range(10):
                await asyncio.sleep(0.001)  # 模拟消息间隔
            return conn_id
        
        async def run_test():
            start = time.time()
            tasks = [simulate_connection(i) for i in range(100)]
            await asyncio.gather(*tasks)
            elapsed = time.time() - start
            return elapsed
        
        elapsed = asyncio.run(run_test())
        
        print(f"\n并发连接:")
        print(f"  连接数: 100")
        print(f"  总耗时: {elapsed:.3f} s")
        print(f"  平均每个连接: {elapsed/100*1000:.3f} ms")
        print(f"  并发处理能力: {100/elapsed:.1f} conn/s")
        
        self.results['concurrent_connections'] = 100 / elapsed
        return elapsed < 5  # 100个连接应在5秒内完成
    
    def test_latency(self):
        """测试延迟"""
        print("\n" + "=" * 60)
        print("性能测试: 端到端延迟")
        print("=" * 60)
        
        codec = WPKGCodec()
        
        # 测试不同大小的数据包
        sizes = [64, 256, 1024, 4096, 16384]
        latencies = []
        
        for size in sizes:
            data = b"X" * size
            
            # 预热
            for _ in range(100):
                encoded = codec.encode(data)
                decoded = codec.decode(encoded)
            
            # 测试
            iterations = 1000
            start = time.time()
            for _ in range(iterations):
                encoded = codec.encode(data)
                decoded = codec.decode(encoded)
            elapsed = time.time() - start
            
            avg_latency = elapsed / iterations * 1000  # ms
            latencies.append(avg_latency)
            
            print(f"  数据包大小: {size:5d} bytes -> 延迟: {avg_latency:.3f} ms")
        
        avg_latency = sum(latencies) / len(latencies)
        print(f"\n  平均延迟: {avg_latency:.3f} ms")
        
        self.results['avg_latency'] = avg_latency
        return avg_latency < 1  # 平均延迟小于1ms
    
    def test_batch_processing(self):
        """测试批处理性能"""
        print("\n" + "=" * 60)
        print("性能测试: 批处理")
        print("=" * 60)
        
        codec = WPKGCodec()
        batch_sizes = [1, 10, 50, 100, 500]
        
        for batch_size in batch_sizes:
            data = b"X" * 100
            
            # 单条处理
            start = time.time()
            for _ in range(1000):
                encoded = codec.encode(data)
                decoded = codec.decode(encoded)
            single_time = time.time() - start
            
            # 批处理 (模拟)
            start = time.time()
            batch = []
            for _ in range(1000 // batch_size):
                batch_data = data * batch_size
                encoded = codec.encode(batch_data)
                decoded = codec.decode(encoded)
            batch_time = time.time() - start
            
            speedup = single_time / batch_time
            print(f"  批大小: {batch_size:3d} -> 加速比: {speedup:.2f}x")
        
        return True
    
    def run_all_tests(self):
        """运行所有性能测试"""
        print("\n" + "=" * 60)
        print("MnMCP 性能测试套件")
        print("=" * 60)
        
        tests = [
            ("WPKG 吞吐量", self.test_wpkg_throughput),
            ("内存使用", self.test_memory_usage),
            ("并发连接", self.test_concurrent_connections),
            ("端到端延迟", self.test_latency),
            ("批处理", self.test_batch_processing),
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    print(f"\n✓ {name} - 通过")
                else:
                    failed += 1
                    print(f"\n✗ {name} - 失败")
            except Exception as e:
                failed += 1
                print(f"\n✗ {name} - 异常: {e}")
        
        # 总结
        print("\n" + "=" * 60)
        print("性能测试总结")
        print("=" * 60)
        print(f"  通过: {passed}/{len(tests)}")
        print(f"  失败: {failed}/{len(tests)}")
        
        if self.results:
            print("\n  关键指标:")
            if 'wpkg_throughput' in self.results:
                print(f"    WPKG 吞吐量: {self.results['wpkg_throughput']:.2f} MB/s")
            if 'avg_latency' in self.results:
                print(f"    平均延迟: {self.results['avg_latency']:.3f} ms")
            if 'concurrent_connections' in self.results:
                print(f"    并发处理能力: {self.results['concurrent_connections']:.1f} conn/s")
        
        return failed == 0


def main():
    test = PerformanceTest()
    success = test.run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("性能测试: 全部通过")
    else:
        print("性能测试: 部分失败")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
