"""
XXTEA 加密测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from crypto.xxtea import XXTEACipher, xxtea_encrypt, xxtea_decrypt

def test_xxtea_basic():
    """基本加密解密测试"""
    print("="*60)
    print("XXTEA 基本测试")
    print("="*60)
    
    key = b'0123456789abcdef'
    cipher = XXTEACipher(key)
    
    test_data = [
        b"Hello, World!",
        b"MiniWorld XXTEA Test",
        b"A" * 100,
        b"Binary\x00Data\xff\xfe",
    ]
    
    for data in test_data:
        print(f"\n原始数据: {data[:50]}...")
        print(f"长度: {len(data)} bytes")
        
        encrypted = cipher.encrypt(data)
        print(f"加密后: {encrypted[:50].hex()}...")
        print(f"长度: {len(encrypted)} bytes")
        
        decrypted = cipher.decrypt(encrypted)
        print(f"解密后: {decrypted[:50]}...")
        
        if decrypted == data:
            print("✓ 通过")
        else:
            print("✗ 失败")
            return False
    
    return True


def test_xxtea_rounds():
    """不同轮数测试"""
    print("\n" + "="*60)
    print("XXTEA 轮数测试")
    print("="*60)
    
    key = b'0123456789abcdef'
    data = b"Test data for different rounds"
    
    for rounds in [6, 10, 16, 32]:
        print(f"\n轮数: {rounds}")
        
        cipher = XXTEACipher(key, rounds)
        encrypted = cipher.encrypt(data)
        decrypted = cipher.decrypt(encrypted)
        
        if decrypted == data:
            print(f"  ✓ 通过")
        else:
            print(f"  ✗ 失败")
            return False
    
    return True


def test_xxtea_convenience():
    """便捷函数测试"""
    print("\n" + "="*60)
    print("XXTEA 便捷函数测试")
    print("="*60)
    
    key = b'0123456789abcdef'
    data = b"Convenience function test"
    
    encrypted = xxtea_encrypt(data, key)
    decrypted = xxtea_decrypt(encrypted, key)
    
    print(f"原始: {data}")
    print(f"加密: {encrypted.hex()[:50]}...")
    print(f"解密: {decrypted}")
    
    if decrypted == data:
        print("✓ 通过")
        return True
    else:
        print("✗ 失败")
        return False


def test_xxtea_key_generation():
    """密钥生成测试"""
    print("\n" + "="*60)
    print("XXTEA 密钥生成测试")
    print("="*60)
    
    for i in range(3):
        key = XXTEACipher.generate_key()
        print(f"\n密钥 {i+1}: {key.hex()}")
        print(f"长度: {len(key)} bytes")
        
        cipher = XXTEACipher(key)
        data = b"Test with generated key"
        
        encrypted = cipher.encrypt(data)
        decrypted = cipher.decrypt(encrypted)
        
        if decrypted == data:
            print("  ✓ 通过")
        else:
            print("  ✗ 失败")
            return False
    
    return True


def test_xxtea_performance():
    """性能测试"""
    print("\n" + "="*60)
    print("XXTEA 性能测试")
    print("="*60)
    
    import time
    
    key = b'0123456789abcdef'
    cipher = XXTEACipher(key)
    
    # 测试不同大小的数据
    sizes = [64, 256, 1024, 4096, 16384]
    
    for size in sizes:
        data = b'X' * size
        iterations = 1000
        
        # 加密性能
        start = time.time()
        for _ in range(iterations):
            encrypted = cipher.encrypt(data)
        encrypt_time = time.time() - start
        
        # 解密性能
        start = time.time()
        for _ in range(iterations):
            decrypted = cipher.decrypt(encrypted)
        decrypt_time = time.time() - start
        
        throughput = (iterations * size) / (encrypt_time + decrypt_time) / 1024 / 1024
        
        print(f"\n数据大小: {size} bytes")
        print(f"  加密: {encrypt_time*1000/iterations:.3f} ms/op")
        print(f"  解密: {decrypt_time*1000/iterations:.3f} ms/op")
        print(f"  吞吐量: {throughput:.2f} MB/s")
    
    return True


def main():
    print("\n" + "="*60)
    print("XXTEA 加密测试套件")
    print("="*60)
    
    tests = [
        ("基本测试", test_xxtea_basic),
        ("轮数测试", test_xxtea_rounds),
        ("便捷函数测试", test_xxtea_convenience),
        ("密钥生成测试", test_xxtea_key_generation),
        ("性能测试", test_xxtea_performance),
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
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"测试结果: {passed}/{len(tests)} 通过, {failed}/{len(tests)} 失败")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
