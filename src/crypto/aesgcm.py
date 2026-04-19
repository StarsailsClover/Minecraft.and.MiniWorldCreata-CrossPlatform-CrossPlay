"""
AES-GCM 加密/解密

基于 AES-128-GCM
提供加密/解密功能，支持纯Python回退实现

Copyright (c) 2026 MnMCP Contributors
SPDX-License-Identifier: MIT
"""

import logging
import struct
from typing import Optional

logger = logging.getLogger(__name__)

# 尝试导入 cryptography
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logger.warning("cryptography library not installed, using fallback")


class AESGCMCipher:
    """
    AES-GCM 加密器
    
    支持 AES-128-GCM 加密/解密
    优先使用 cryptography 库，回退到纯 Python 实现
    
    Attributes:
        key: 16字节密钥
        nonce_base: 12字节 nonce 基础值
        seq: 序列计数器
    """
    
    def __init__(self, key: bytes, nonce_base: bytes):
        """
        初始化 AES-GCM 加密器
        
        Args:
            key: 16字节密钥
            nonce_base: 12字节 nonce 基础值
        """
        if len(key) != 16:
            raise ValueError(f"Key must be 16 bytes, got {len(key)}")
        if len(nonce_base) != 12:
            raise ValueError(f"Nonce base must be 12 bytes, got {len(nonce_base)}")
        
        self.key = key
        self.nonce_base = nonce_base
        self.seq = 0
    
    def _get_nonce(self) -> bytes:
        """
        获取下一个 nonce (12 bytes for GCM)
        
        基于 seq 生成 nonce: nonce_base XOR seq
        
        Returns:
            12字节 nonce
        """
        seq_bytes = struct.pack('<Q', self.seq)  # 8 bytes
        # 将 seq_bytes 扩展到 12 bytes
        seq_extended = seq_bytes + b'\x00\x00\x00\x00'  # 12 bytes
        # XOR with nonce_base
        nonce = bytes(a ^ b for a, b in zip(self.nonce_base, seq_extended))
        return nonce
    
    def encrypt(self, plaintext: bytes, aad: Optional[bytes] = None) -> Optional[bytes]:
        """
        加密数据
        
        Args:
            plaintext: 明文数据
            aad: 附加认证数据 (可选)
            
        Returns:
            ciphertext + tag (16 bytes)，失败返回 None
        """
        if CRYPTOGRAPHY_AVAILABLE:
            return self._encrypt_cryptography(plaintext, aad)
        else:
            return self._encrypt_fallback(plaintext, aad)
    
    def _encrypt_cryptography(self, plaintext: bytes, aad: Optional[bytes] = None) -> Optional[bytes]:
        """使用 cryptography 库加密"""
        try:
            nonce = self._get_nonce()
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.GCM(nonce),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            if aad:
                encryptor.authenticate_additional_data(aad)
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            tag = encryptor.tag  # 16 bytes
            self.seq += 1
            # 返回: ciphertext + tag
            return ciphertext + tag
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None
    
    def _encrypt_fallback(self, plaintext: bytes, aad: Optional[bytes] = None) -> Optional[bytes]:
        """
        纯 Python 回退加密 (模拟)
        
        注意: 这不是真正的 AES-GCM，仅用于测试
        生产环境必须使用 cryptography 库
        """
        logger.warning("Using fallback encryption (NOT SECURE)")
        # 简单的 XOR 加密 (仅用于测试)
        nonce = self._get_nonce()
        key_expanded = self.key * (len(plaintext) // 16 + 1)
        key_expanded = key_expanded[:len(plaintext)]
        ciphertext = bytes(p ^ k for p, k in zip(plaintext, key_expanded))
        # 模拟 16-byte tag
        tag = nonce[:16] if len(nonce) >= 16 else nonce + b'\x00' * (16 - len(nonce))
        self.seq += 1
        return ciphertext + tag
    
    def decrypt(self, ciphertext_with_tag: bytes, aad: Optional[bytes] = None) -> Optional[bytes]:
        """
        解密数据
        
        Args:
            ciphertext_with_tag: ciphertext + tag (16 bytes)
            aad: 附加认证数据 (可选)
            
        Returns:
            明文数据，失败返回 None
        """
        if len(ciphertext_with_tag) < 16:
            logger.error("Ciphertext too short")
            return None
        
        if CRYPTOGRAPHY_AVAILABLE:
            return self._decrypt_cryptography(ciphertext_with_tag, aad)
        else:
            return self._decrypt_fallback(ciphertext_with_tag, aad)
    
    def _decrypt_cryptography(self, ciphertext_with_tag: bytes, aad: Optional[bytes] = None) -> Optional[bytes]:
        """使用 cryptography 库解密"""
        try:
            nonce = self._get_nonce()
            # 分离 ciphertext 和 tag
            ciphertext = ciphertext_with_tag[:-16]
            tag = ciphertext_with_tag[-16:]
            
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            if aad:
                decryptor.authenticate_additional_data(aad)
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            self.seq += 1
            return plaintext
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    def _decrypt_fallback(self, ciphertext_with_tag: bytes, aad: Optional[bytes] = None) -> Optional[bytes]:
        """
        纯 Python 回退解密 (模拟)
        
        注意: 这不是真正的 AES-GCM，仅用于测试
        """
        logger.warning("Using fallback decryption (NOT SECURE)")
        # 简单的 XOR 解密
        nonce = self._get_nonce()
        ciphertext = ciphertext_with_tag[:-16]
        key_expanded = self.key * (len(ciphertext) // 16 + 1)
        key_expanded = key_expanded[:len(ciphertext)]
        plaintext = bytes(c ^ k for c, k in zip(ciphertext, key_expanded))
        self.seq += 1
        return plaintext


# 便捷函数
def aes_gcm_encrypt(key: bytes, nonce_base: bytes, plaintext: bytes, aad: Optional[bytes] = None) -> Optional[bytes]:
    """
    便捷加密函数
    
    Args:
        key: 16字节密钥
        nonce_base: 12字节 nonce 基础值
        plaintext: 明文数据
        aad: 附加认证数据
        
    Returns:
        ciphertext + tag
    """
    cipher = AESGCMCipher(key, nonce_base)
    return cipher.encrypt(plaintext, aad)


def aes_gcm_decrypt(key: bytes, nonce_base: bytes, ciphertext_with_tag: bytes, aad: Optional[bytes] = None) -> Optional[bytes]:
    """
    便捷解密函数
    
    Args:
        key: 16字节密钥
        nonce_base: 12字节 nonce 基础值
        ciphertext_with_tag: ciphertext + tag
        aad: 附加认证数据
        
    Returns:
        明文数据
    """
    cipher = AESGCMCipher(key, nonce_base)
    return cipher.decrypt(ciphertext_with_tag, aad)


# 版本信息
__version__ = "1.1.0"
__all__ = [
    'AESGCMCipher',
    'aes_gcm_encrypt',
    'aes_gcm_decrypt',
    'CRYPTOGRAPHY_AVAILABLE'
]
