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
        """获取下一个 nonce"""
        # TODO: 实现基于 seq 的 nonce 生成
        return self.nonce_base
    
    def encrypt(self, plaintext: bytes, aad: Optional[bytes] = None) -> Optional[bytes]:
        """加密数据"""
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
            self.seq += 1
            return ciphertext + encryptor.tag
        except ImportError:
            logger.error("cryptography library not installed")
            return None
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None
    
    def decrypt(self, ciphertext: bytes, tag: bytes, aad: Optional[bytes] = None) -> Optional[bytes]:
        """解密数据"""
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            
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
