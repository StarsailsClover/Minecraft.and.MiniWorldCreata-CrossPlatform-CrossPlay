"""
AES-GCM 加密/解密

基于 AES-128-GCM
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class AESGCMCipher:
    """AES-GCM 加密器"""
    
    def __init__(self, key: bytes, nonce_base: bytes):
        self.key = key
        self.nonce_base = nonce_base
        self.seq = 0
    
    def _get_nonce(self) -> bytes:
        """获取下一个 nonce (12 bytes for GCM)"""
        # 基于 seq 生成 nonce: nonce_base XOR seq
        import struct
        seq_bytes = struct.pack('<Q', self.seq)  # 8 bytes
        # 将 seq_bytes 扩展到 12 bytes
        seq_extended = seq_bytes + b'\x00\x00\x00\x00'  # 12 bytes
        # XOR with nonce_base
        nonce = bytes(a ^ b for a, b in zip(self.nonce_base, seq_extended))
        return nonce
    
    def encrypt(self, plaintext: bytes, aad: Optional[bytes] = None) -> Optional[bytes]:
        """加密数据，返回 ciphertext + tag"""
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            
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
        except ImportError:
            logger.error("cryptography library not installed")
            return None
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None
    
    def decrypt(self, ciphertext_with_tag: bytes, aad: Optional[bytes] = None) -> Optional[bytes]:
        """解密数据 (ciphertext_with_tag = ciphertext + tag)"""
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            
            if len(ciphertext_with_tag) < 16:
                logger.error("Ciphertext too short")
                return None
            
            # 分离 ciphertext 和 tag
            ciphertext = ciphertext_with_tag[:-16]
            tag = ciphertext_with_tag[-16:]
            
            nonce = self._get_nonce()
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
    
    def reset_seq(self):
        """重置序列号"""
        self.seq = 0
