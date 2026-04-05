"""
模拟加密实现 (用于测试框架，无需 cryptography 库)
"""

import hashlib
import os
import struct


class MockECDHKeyExchange:
    """模拟 ECDH 密钥交换"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.server_public_key = None
        self.shared_secret = None
    
    def generate_keypair(self) -> bool:
        """生成模拟密钥对"""
        self.private_key = os.urandom(32)
        self.public_key = os.urandom(65)  # Uncompressed EC point
        return True
    
    def load_server_public_key(self) -> bool:
        """加载模拟服务器公钥"""
        self.server_public_key = os.urandom(65)
        return True
    
    def exchange(self) -> bytes:
        """执行模拟密钥交换"""
        # 模拟共享秘密 = hash(private_key + server_public_key)
        self.shared_secret = hashlib.sha256(
            self.private_key + self.server_public_key
        ).digest()
        return self.shared_secret
    
    def complete_exchange(self) -> bytes:
        """完整的模拟密钥交换"""
        self.generate_keypair()
        self.load_server_public_key()
        return self.exchange()


class MockHKDFKeyDerivation:
    """模拟 HKDF 密钥派生"""
    
    def __init__(self):
        self.salt = None
        self.info = b"ilink-session"
    
    def derive(self, shared_secret: bytes, length: int = 48) -> bytes:
        """模拟密钥派生"""
        # 使用 SHA-256 多次哈希模拟 HKDF
        key_material = b''
        counter = 0
        while len(key_material) < length:
            data = shared_secret + self.info + bytes([counter])
            if self.salt:
                data = self.salt + data
            key_material += hashlib.sha256(data).digest()
            counter += 1
        return key_material[:length]
    
    def extract_keys(self, key_material: bytes) -> dict:
        """提取各个密钥"""
        return {
            'aes_key': key_material[:16],
            'nonce_base': key_material[16:28],
            'padding': key_material[28:48],
        }


class MockAESGCMCipher:
    """模拟 AES-GCM 加密 (实际使用 XOR 模拟)"""
    
    def __init__(self, key: bytes, nonce_base: bytes):
        self.key = key
        self.nonce_base = nonce_base
        self.seq = 0
    
    def _get_nonce(self) -> bytes:
        """获取下一个 nonce"""
        seq_bytes = struct.pack('<Q', self.seq)
        seq_extended = seq_bytes + b'\x00\x00\x00\x00'
        nonce = bytes(a ^ b for a, b in zip(self.nonce_base, seq_extended))
        return nonce
    
    def _xor_encrypt(self, data: bytes, key: bytes) -> bytes:
        """XOR 加密 (模拟)"""
        extended_key = (key * (len(data) // len(key) + 1))[:len(data)]
        return bytes(a ^ b for a, b in zip(data, extended_key))
    
    def encrypt(self, plaintext: bytes, aad: bytes = None) -> bytes:
        """模拟加密"""
        nonce = self._get_nonce()
        # 使用 XOR + nonce 模拟加密
        ciphertext = self._xor_encrypt(plaintext, self.key + nonce)
        # 模拟 16-byte tag
        tag = hashlib.sha256(ciphertext + (aad or b'')).digest()[:16]
        self.seq += 1
        return ciphertext + tag
    
    def decrypt(self, ciphertext_with_tag: bytes, aad: bytes = None) -> bytes:
        """模拟解密"""
        if len(ciphertext_with_tag) < 16:
            return None
        
        ciphertext = ciphertext_with_tag[:-16]
        tag = ciphertext_with_tag[-16:]
        
        # 获取加密时使用的 nonce (seq 需要先减 1)
        self.seq -= 1
        nonce = self._get_nonce()
        
        # 验证 tag (模拟)
        expected_tag = hashlib.sha256(ciphertext + (aad or b'')).digest()[:16]
        if tag != expected_tag:
            self.seq += 1  # 恢复 seq
            return None
        
        plaintext = self._xor_encrypt(ciphertext, self.key + nonce)
        return plaintext
    
    def reset_seq(self):
        """重置序列号"""
        self.seq = 0
