"""
HKDF 密钥派生

基于 HMAC-SHA256
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class HKDFKeyDerivation:
    """HKDF 密钥派生"""
    
    def __init__(self):
        self.salt = None
        self.info = b"ilink-session"
    
    def derive(self, shared_secret: bytes, length: int = 48) -> Optional[bytes]:
        """派生会话密钥"""
        try:
            from cryptography.hazmat.primitives.kdf.hkdf import HKDF
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.backends import default_backend
            
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=length,
                salt=self.salt,
                info=self.info,
                backend=default_backend()
            )
            key_material = hkdf.derive(shared_secret)
            logger.info(f"Key material derived: {len(key_material)} bytes")
            return key_material
        except ImportError:
            logger.error("cryptography library not installed")
            return None
        except Exception as e:
            logger.error(f"Key derivation failed: {e}")
            return None
    
    def extract_keys(self, key_material: bytes) -> dict:
        """提取各个密钥"""
        if len(key_material) < 48:
            raise ValueError(f"Key material too short: {len(key_material)} bytes, expected 48")
        
        return {
            'aes_key': key_material[:16],           # 16 bytes for AES-128
            'nonce_base': key_material[16:28],      # 12 bytes for GCM nonce
            'padding': key_material[28:48],         # 20 bytes padding/reserved
        }
    
    def derive_with_salt(self, shared_secret: bytes, salt: bytes, length: int = 48) -> Optional[bytes]:
        """使用指定 salt 派生密钥"""
        self.salt = salt
        return self.derive(shared_secret, length)
