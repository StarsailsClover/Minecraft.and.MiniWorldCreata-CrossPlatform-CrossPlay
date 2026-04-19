"""
XXTEA 加密测试 (简化版)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from crypto.xxtea import XXTEACipher

def test_basic():
    """基本测试"""
    print("="*60)
    print("XXTEA 基本测试")
    print("="*60)
    
    key = b'0123456789abcdef'
    cipher = XXTEACipher(key)
    
    # 测试8字节数据
    data = b'ABCDEFGH'
    print(f"\n原始数据: {data}")
    print(f"长度: {len(data)}")
    
    encrypted = cipher.encrypt(data)
    print(f"加密后: {encrypted.hex()}")
    
    decrypted = cipher.decrypt(encrypted)
    print(f"解密后: {decrypted}")
    
    # 检查
    if decrypted == data:
        print("✓ 通过")
        return True
    else:
        print("✗ 失败")
        print(f"  预期: {data}")
        print(f"  实际: {decrypted}")
        return False

def test_16_bytes():
    """测试16字节数据"""
    print("\n" + "="*60)
    print("XXTEA 16字节测试")
    print("="*60)
    
    key = b'0123456789abcdef'
    cipher = XXTEACipher(key)
    
    data = b'ABCDEFGHIJKLMNOP'
    print(f"\n原始数据: {data}")
    
    encrypted = cipher.encrypt(data)
    print(f"加密后: {encrypted.hex()}")
    
    decrypted = cipher.decrypt(encrypted)
    print(f"解密后: {decrypted}")
    
    if decrypted == data:
        print("✓ 通过")
        return True
    else:
        print("✗ 失败")
        return False

def main():
    results = []
    results.append(("基本测试", test_basic()))
    results.append(("16字节测试", test_16_bytes()))
    
    print("\n" + "="*60)
    print("测试结果")
    print("="*60)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
    
    passed_count = sum(1 for _, p in results if p)
    print(f"\n总计: {passed_count}/{len(results)} 通过")
    
    return passed_count == len(results)

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
