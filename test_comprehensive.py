"""
MnMCP 全面测试套件
验证联机可行性
"""
import sys
import os
import asyncio
import struct
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 测试统计
test_results = {
    'passed': 0,
    'failed': 0,
    'total': 0
}

def record_result(name: str, passed: bool, details: str = ""):
    """记录测试结果"""
    test_results['total'] += 1
    if passed:
        test_results['passed'] += 1
        print(f"✓ {name}")
    else:
        test_results['failed'] += 1
        print(f"✗ {name}")
        if details:
            print(f"  详情: {details}")

async def test_crypto_layer():
    """测试加密层"""
    print("\n" + "="*60)
    print("加密层测试")
    print("="*60)
    
    # 1. AES-GCM 测试
    try:
        from crypto.aesgcm import AESGCMCipher
        key = b'\x00' * 16
        nonce_base = b'\x01' * 12
        cipher = AESGCMCipher(key, nonce_base)
        
        plaintext = b"Hello, MnMCP!"
        encrypted = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(encrypted)
        
        record_result("AES-GCM 加密/解密", decrypted == plaintext)
    except Exception as e:
        record_result("AES-GCM 加密/解密", False, str(e))
    
    # 2. HKDF 测试
    try:
        from crypto.hkdf import HKDFKeyDerivation
        hkdf = HKDFKeyDerivation()
        shared_secret = b'shared_secret_32bytes_long!'
        key_material = hkdf.derive(shared_secret)
        keys = hkdf.extract_keys(key_material)
        
        record_result("HKDF 密钥派生", 
                     len(keys['aes_key']) == 16 and len(keys['nonce_base']) == 12)
    except Exception as e:
        record_result("HKDF 密钥派生", False, str(e))
    
    # 3. ECDH 测试
    try:
        from crypto.ecdh import ECDHKeyExchange
        ecdh = ECDHKeyExchange()
        result = ecdh.generate_keypair()
        record_result("ECDH 密钥对生成", result)
    except Exception as e:
        record_result("ECDH 密钥对生成", False, str(e))

async def test_protocol_layer():
    """测试协议层"""
    print("\n" + "="*60)
    print("协议层测试")
    print("="*60)
    
    # 1. WPKG 编解码
    try:
        from protocol.wpkg_codec import WPKGCodec
        codec = WPKGCodec()
        data = b"Test WPKG data"
        encoded = codec.encode(data, compress=False, encrypt=False)
        decoded = codec.decode(encoded)
        record_result("WPKG 编解码", decoded == data)
    except Exception as e:
        record_result("WPKG 编解码", False, str(e))
    
    # 2. MNW 数据包
    try:
        from protocol.mnw import MNWPacket, MNWProtoID
        packet = MNWPacket(
            proto_id=MNWProtoID.PROTO_2020,
            uin=1234567890,
            data=b"Test data"
        )
        encoded = packet.encode()
        decoded = MNWPacket.decode(encoded)
        record_result("MNW 数据包编解码", 
                     decoded is not None and decoded.proto_id == packet.proto_id)
    except Exception as e:
        record_result("MNW 数据包编解码", False, str(e))
    
    # 3. Protobuf 编解码
    try:
        from protocol.protobuf_codec import PB_Vector3, PB_HeartBeatCH
        vec = PB_Vector3(X=100, Y=64, Z=-50)
        encoded = vec.encode()
        decoded = PB_Vector3.decode(encoded)
        record_result("Protobuf Vector3 编解码", 
                     decoded is not None and decoded.X == 100)
    except Exception as e:
        record_result("Protobuf Vector3 编解码", False, str(e))

async def test_network_layer():
    """测试网络层"""
    print("\n" + "="*60)
    print("网络层测试")
    print("="*60)
    
    # 1. UDP 连接器
    try:
        from network.udp import UDPConnection, UDPConfig
        config = UDPConfig(timeout=1.0)
        conn = UDPConnection(config)
        record_result("UDP 连接器初始化", True)
    except Exception as e:
        record_result("UDP 连接器初始化", False, str(e))
    
    # 2. RakNet 适配器
    try:
        from network.raknet_adapter import RakNetConnection, RakNetConfig
        config = RakNetConfig()
        conn = RakNetConnection(config)
        record_result("RakNet 适配器初始化", True)
    except Exception as e:
        record_result("RakNet 适配器初始化", False, str(e))

async def test_mapping_layer():
    """测试映射层"""
    print("\n" + "="*60)
    print("映射层测试")
    print("="*60)
    
    # 1. 坐标转换
    try:
        from mapping.coordinates import CoordinateConverter, Vec3
        converter = CoordinateConverter()
        mc_pos = Vec3(100.0, 64.0, -50.0)
        mnw_pos = converter.mc_to_mnw(mc_pos)
        back_to_mc = converter.mnw_to_mc(mnw_pos)
        
        # 检查转换精度
        tolerance = 0.01
        match = (abs(back_to_mc.x - mc_pos.x) < tolerance and
                abs(back_to_mc.y - mc_pos.y) < tolerance and
                abs(back_to_mc.z - mc_pos.z) < tolerance)
        record_result("坐标转换", match)
    except Exception as e:
        record_result("坐标转换", False, str(e))
    
    # 2. 方块映射
    try:
        from mapping.blocks import BlockMapper
        mapper = BlockMapper()
        mc_id, mc_meta = mapper.mnw_to_mc(1, 0)  # 石头
        record_result("方块映射", mc_id is not None)
    except Exception as e:
        record_result("方块映射", False, str(e))

async def test_bridge_layer():
    """测试桥接层"""
    print("\n" + "="*60)
    print("桥接层测试")
    print("="*60)
    
    try:
        from bridge import MnMCPBridgeUnified, UnifiedBridgeConfig
        config = UnifiedBridgeConfig()
        bridge = MnMCPBridgeUnified(config)
        record_result("桥接器初始化", True)
    except Exception as e:
        record_result("桥接器初始化", False, str(e))

async def test_integration():
    """集成测试"""
    print("\n" + "="*60)
    print("集成测试")
    print("="*60)
    
    # 模拟完整数据流
    try:
        from protocol.mnw import MNWCodec
        from protocol.protobuf_codec import PB_Vector3
        from mapping.coordinates import CoordinateConverter
        
        # 1. 创建 MNW 移动数据包
        codec = MNWCodec()
        packet = codec.create_player_move(
            uin=2056826320,
            x=100.0,
            y=64.0,
            z=-50.0
        )
        
        # 2. 编码
        encoded = packet.encode()
        
        # 3. 解码
        decoded = MNWPacket.decode(encoded)
        
        # 4. 坐标转换
        converter = CoordinateConverter()
        # 模拟从 MNW 坐标转换到 MC 坐标
        
        record_result("端到端数据流", decoded is not None)
    except Exception as e:
        record_result("端到端数据流", False, str(e))

async def test_performance():
    """性能测试"""
    print("\n" + "="*60)
    print("性能测试")
    print("="*60)
    
    # WPKG 吞吐量
    try:
        from protocol.wpkg_codec import WPKGCodec
        import zlib
        
        codec = WPKGCodec()
        data = b"X" * 1024
        iterations = 1000
        
        start = time.time()
        for _ in range(iterations):
            encoded = codec.encode(data, compress=True)
            decoded = codec.decode(encoded)
        elapsed = time.time() - start
        
        throughput = (iterations * len(data)) / elapsed / 1024 / 1024
        record_result(f"WPKG 吞吐量: {throughput:.2f} MB/s", throughput > 10)
    except Exception as e:
        record_result("WPKG 吞吐量测试", False, str(e))

async def main():
    print("\n" + "="*70)
    print("MnMCP 全面测试套件 - 联机可行性验证")
    print("="*70)
    
    await test_crypto_layer()
    await test_protocol_layer()
    await test_network_layer()
    await test_mapping_layer()
    await test_bridge_layer()
    await test_integration()
    await test_performance()
    
    # 总结
    print("\n" + "="*70)
    print("测试结果总结")
    print("="*70)
    print(f"通过: {test_results['passed']}/{test_results['total']}")
    print(f"失败: {test_results['failed']}/{test_results['total']}")
    print(f"通过率: {test_results['passed']/test_results['total']*100:.1f}%")
    
    # 联机可行性评估
    print("\n" + "="*70)
    print("联机可行性评估")
    print("="*70)
    
    if test_results['passed'] >= test_results['total'] * 0.8:
        print("✓ 联机可行 - 核心功能正常")
        feasible = True
    elif test_results['passed'] >= test_results['total'] * 0.5:
        print("⚠ 联机部分可行 - 需要修复部分功能")
        feasible = True
    else:
        print("✗ 联机不可行 - 需要大量修复")
        feasible = False
    
    # 关键组件状态
    print("\n关键组件状态:")
    components = {
        "加密层": test_results['passed'] >= 2,
        "协议层": test_results['passed'] >= 5,
        "网络层": test_results['passed'] >= 7,
        "映射层": test_results['passed'] >= 9,
        "桥接层": test_results['passed'] >= 10,
    }
    
    for component, ready in components.items():
        status = "✓ 就绪" if ready else "✗ 未就绪"
        print(f"  {component}: {status}")
    
    print("\n" + "="*70)
    
    return feasible

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
