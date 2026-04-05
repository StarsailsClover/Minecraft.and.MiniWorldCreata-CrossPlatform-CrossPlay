#!/usr/bin/env python3
"""
性能测试
"""

import sys
import time
sys.path.insert(0, '.')


def test_crypto_performance():
    """测试加密性能"""
    print("\n=== Crypto Performance ===")
    
    from src.crypto import ECDHKeyExchange, HKDFKeyDerivation, AESGCMCipher
    
    # ECDH 性能
    print("\nECDH Key Exchange:")
    ecdh = ECDHKeyExchange()
    start = time.time()
    for _ in range(10):
        ecdh.generate_keypair()
    elapsed = time.time() - start
    if elapsed > 0:
        print(f"  10 keypairs in {elapsed:.3f}s ({10/elapsed:.1f} ops/s)")
    else:
        print(f"  10 keypairs in {elapsed:.3f}s (too fast to measure)")
    
    # HKDF 性能
    print("\nHKDF Key Derivation:")
    hkdf = HKDFKeyDerivation()
    shared_secret = b'x' * 32
    start = time.time()
    for _ in range(100):
        hkdf.derive(shared_secret)
    elapsed = time.time() - start
    if elapsed > 0:
        print(f"  100 derivations in {elapsed:.3f}s ({100/elapsed:.1f} ops/s)")
    else:
        print(f"  100 derivations in {elapsed:.3f}s (too fast to measure)")
    
    # AES-GCM 性能
    print("\nAES-GCM Encryption:")
    key = b'x' * 16
    nonce = b'y' * 12
    cipher = AESGCMCipher(key, nonce)
    plaintext = b"Hello World!" * 100
    
    start = time.time()
    for _ in range(1000):
        ciphertext = cipher.encrypt(plaintext)
        cipher.reset_seq()
    elapsed = time.time() - start
    if elapsed > 0:
        print(f"  1000 encryptions in {elapsed:.3f}s ({1000/elapsed:.1f} ops/s)")
    else:
        print(f"  1000 encryptions in {elapsed:.3f}s (too fast to measure)")
    print(f"  Data size: {len(plaintext)} bytes")


def test_coordinate_performance():
    """测试坐标转换性能"""
    print("\n=== Coordinate Performance ===")
    
    from src.mapping import CoordinateConverter, Vec3
    
    cc = CoordinateConverter()
    
    start = time.time()
    for _ in range(100000):
        pos = Vec3(100.5, 64.0, -200.3)
        mnw_pos = cc.mc_to_mnw(pos)
        back = cc.mnw_to_mc(mnw_pos)
    elapsed = time.time() - start
    if elapsed > 0:
        print(f"  100k conversions in {elapsed:.3f}s ({100000/elapsed:.1f} ops/s)")
    else:
        print(f"  100k conversions in {elapsed:.3f}s (too fast to measure)")


def test_mapping_performance():
    """测试映射性能"""
    print("\n=== Mapping Performance ===")
    
    from src.mapping import BlockMapper, EntityMapper
    
    bm = BlockMapper()
    
    start = time.time()
    for _ in range(10000):
        bm.get_mnw_block(1)
        bm.get_mc_block(1)
    elapsed = time.time() - start
    if elapsed > 0:
        print(f"  10k block lookups in {elapsed:.3f}s ({10000/elapsed:.1f} ops/s)")
    else:
        print(f"  10k block lookups in {elapsed:.3f}s (too fast to measure)")
    print(f"  Loaded blocks: {bm.count}")


def test_protocol_performance():
    """测试协议性能"""
    print("\n=== Protocol Performance ===")
    
    from src.protocol import BusinessProtocol
    
    bp = BusinessProtocol()
    
    start = time.time()
    for _ in range(10000):
        msg = bp.create_chat_message(123456, "Hello World!")
        encoded = msg.encode()
    elapsed = time.time() - start
    if elapsed > 0:
        print(f"  10k message encodes in {elapsed:.3f}s ({10000/elapsed:.1f} ops/s)")
    else:
        print(f"  10k message encodes in {elapsed:.3f}s (too fast to measure)")


def main():
    """主函数"""
    print("=" * 60)
    print("MnMCP Performance Test")
    print("=" * 60)
    
    try:
        test_crypto_performance()
        test_coordinate_performance()
        test_mapping_performance()
        test_protocol_performance()
        
        print("\n" + "=" * 60)
        print("Performance test complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
