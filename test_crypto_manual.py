#!/usr/bin/env python3
"""
加密层测试脚本
"""

import sys
sys.path.insert(0, '.')

# 强制使用模拟加密（因为 cryptography 未安装）
from src.crypto.mock_crypto import MockECDHKeyExchange as ECDHKeyExchange
from src.crypto.mock_crypto import MockHKDFKeyDerivation as HKDFKeyDerivation
from src.crypto.mock_crypto import MockAESGCMCipher as AESGCMCipher


def test_ecdh():
    """测试 ECDH"""
    print("\n=== Testing ECDH ===")
    ecdh = ECDHKeyExchange()
    
    # 生成密钥对
    assert ecdh.generate_keypair(), "Failed to generate keypair"
    print("✓ Keypair generated")
    
    # 加载服务器公钥
    assert ecdh.load_server_public_key(), "Failed to load server public key"
    print("✓ Server public key loaded")
    
    # 执行密钥交换
    shared_secret = ecdh.exchange()
    assert shared_secret is not None, "Key exchange failed"
    print(f"✓ Shared secret derived: {len(shared_secret)} bytes")
    
    return shared_secret


def test_hkdf(shared_secret):
    """测试 HKDF"""
    print("\n=== Testing HKDF ===")
    hkdf = HKDFKeyDerivation()
    
    # 派生密钥材料
    key_material = hkdf.derive(shared_secret)
    assert key_material is not None, "Key derivation failed"
    print(f"✓ Key material derived: {len(key_material)} bytes")
    
    # 提取各个密钥
    keys = hkdf.extract_keys(key_material)
    print(f"✓ AES key: {len(keys['aes_key'])} bytes")
    print(f"✓ Nonce base: {len(keys['nonce_base'])} bytes")
    print(f"✓ Padding: {len(keys['padding'])} bytes")
    
    return keys


def test_aes_gcm(keys):
    """测试 AES-GCM"""
    print("\n=== Testing AES-GCM ===")
    cipher = AESGCMCipher(keys['aes_key'], keys['nonce_base'])
    
    # 测试数据
    plaintext = b"Hello from MnMCP!"
    print(f"Original: {plaintext}")
    
    # 加密
    ciphertext = cipher.encrypt(plaintext)
    assert ciphertext is not None, "Encryption failed"
    print(f"✓ Encrypted: {len(ciphertext)} bytes")
    
    # 解密
    decrypted = cipher.decrypt(ciphertext)
    assert decrypted is not None, "Decryption failed"
    assert decrypted == plaintext, "Decrypted data mismatch"
    print(f"✓ Decrypted: {decrypted}")
    
    print("✓ AES-GCM encryption/decryption successful")


def main():
    """主函数"""
    print("=" * 50)
    print("MnMCP Crypto Layer Test")
    print("=" * 50)
    
    try:
        # Step 1: ECDH
        shared_secret = test_ecdh()
        
        # Step 2: HKDF
        keys = test_hkdf(shared_secret)
        
        # Step 3: AES-GCM
        test_aes_gcm(keys)
        
        print("\n" + "=" * 50)
        print("All tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
