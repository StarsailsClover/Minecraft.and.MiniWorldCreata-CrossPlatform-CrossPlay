"""
加密层集成测试

测试 ECDH + HKDF + AES-GCM 完整流程
"""

import unittest
import logging

logging.basicConfig(level=logging.INFO)


class TestCryptoLayer(unittest.TestCase):
    """测试加密层"""
    
    def test_ecdh_key_exchange(self):
        """测试 ECDH 密钥交换"""
        from src.crypto import ECDHKeyExchange
        
        ecdh = ECDHKeyExchange()
        
        # 生成密钥对
        self.assertTrue(ecdh.generate_keypair())
        self.assertIsNotNone(ecdh.private_key)
        self.assertIsNotNone(ecdh.public_key)
        
        # 加载服务器公钥
        self.assertTrue(ecdh.load_server_public_key())
        self.assertIsNotNone(ecdh.server_public_key)
        
        # 执行密钥交换
        shared_secret = ecdh.exchange()
        self.assertIsNotNone(shared_secret)
        self.assertEqual(len(shared_secret), 32)  # P-256 共享秘密为 32 字节
        
        print(f"✓ ECDH key exchange successful, shared secret: {len(shared_secret)} bytes")
    
    def test_hkdf_key_derivation(self):
        """测试 HKDF 密钥派生"""
        from src.crypto import HKDFKeyDerivation
        
        hkdf = HKDFKeyDerivation()
        
        # 模拟共享秘密
        shared_secret = b'x' * 32
        
        # 派生密钥材料
        key_material = hkdf.derive(shared_secret, length=48)
        self.assertIsNotNone(key_material)
        self.assertEqual(len(key_material), 48)
        
        # 提取各个密钥
        keys = hkdf.extract_keys(key_material)
        self.assertEqual(len(keys['aes_key']), 16)
        self.assertEqual(len(keys['nonce_base']), 12)
        self.assertEqual(len(keys['padding']), 20)
        
        print(f"✓ HKDF key derivation successful")
        print(f"  - AES key: {len(keys['aes_key'])} bytes")
        print(f"  - Nonce base: {len(keys['nonce_base'])} bytes")
        print(f"  - Padding: {len(keys['padding'])} bytes")
    
    def test_aes_gcm_encryption(self):
        """测试 AES-GCM 加密/解密"""
        from src.crypto import AESGCMCipher
        
        key = b'x' * 16  # 16 bytes for AES-128
        nonce_base = b'y' * 12  # 12 bytes for GCM nonce
        
        cipher = AESGCMCipher(key, nonce_base)
        
        # 测试数据
        plaintext = b"Hello, MiniWorld!"
        aad = b"additional_data"
        
        # 加密
        ciphertext = cipher.encrypt(plaintext, aad)
        self.assertIsNotNone(ciphertext)
        self.assertGreater(len(ciphertext), len(plaintext))
        
        # 解密
        decrypted = cipher.decrypt(ciphertext, aad)
        self.assertIsNotNone(decrypted)
        self.assertEqual(decrypted, plaintext)
        
        print(f"✓ AES-GCM encryption/decryption successful")
        print(f"  - Plaintext: {plaintext}")
        print(f"  - Ciphertext: {len(ciphertext)} bytes")
    
    def test_full_crypto_flow(self):
        """测试完整加密流程: ECDH -> HKDF -> AES-GCM"""
        from src.crypto import ECDHKeyExchange, HKDFKeyDerivation, AESGCMCipher
        
        print("\n=== Testing Full Crypto Flow ===")
        
        # Step 1: ECDH 密钥交换
        ecdh = ECDHKeyExchange()
        shared_secret = ecdh.complete_exchange()
        self.assertIsNotNone(shared_secret)
        print(f"✓ Step 1: ECDH complete, shared secret: {len(shared_secret)} bytes")
        
        # Step 2: HKDF 密钥派生
        hkdf = HKDFKeyDerivation()
        key_material = hkdf.derive(shared_secret)
        self.assertIsNotNone(key_material)
        keys = hkdf.extract_keys(key_material)
        print(f"✓ Step 2: HKDF complete")
        print(f"  - AES key: {keys['aes_key'].hex()[:16]}...")
        print(f"  - Nonce base: {keys['nonce_base'].hex()[:16]}...")
        
        # Step 3: AES-GCM 加密/解密
        cipher = AESGCMCipher(keys['aes_key'], keys['nonce_base'])
        
        plaintext = b"Hello from MnMCP!"
        ciphertext = cipher.encrypt(plaintext)
        self.assertIsNotNone(ciphertext)
        
        decrypted = cipher.decrypt(ciphertext)
        self.assertIsNotNone(decrypted)
        self.assertEqual(decrypted, plaintext)
        print(f"✓ Step 3: AES-GCM complete")
        print(f"  - Original: {plaintext}")
        print(f"  - Decrypted: {decrypted}")
        
        print("\n=== Full Crypto Flow Successful ===")


if __name__ == '__main__':
    unittest.main(verbosity=2)
