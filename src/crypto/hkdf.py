"""
HKDF 密钥派生

基于 HMAC-SHA256
提供密钥派生功能，支持纯Python回退实现

Copyright (c) 2026 MnMCP Contributors
SPDX-License-Identifier: MIT
"""

import logging
import hashlib
import hmac
from typing import Optional

logger = logging.getLogger(__name__)

# 尝试导入 cryptography
try:
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logger.warning("cryptography library not installed, using fallback")


class HKDFKeyDerivation:
    """
    HKDF 密钥派生
    
    基于 HMAC-SHA256
    优先使用 cryptography 库，回退到纯 Python 实现
    
    Attributes:
        salt: 盐值
        info: 上下文信息
    """
    
    def __init__(self):
        """初始化 HKDF 密钥派生器"""
        self.salt = None
        self.info = b"ilink-session"
    
    def derive(self, shared_secret: bytes, length: int = 48) -> Optional[bytes]:
        """
        派生会话密钥
        
        Args:
            shared_secret: 共享密钥
            length: 派生密钥长度 (默认48字节)
            
        Returns:
            密钥材料或 None
        """
        if CRYPTOGRAPHY_AVAILABLE:
            return self._derive_cryptography(shared_secret, length)
        else:
            return self._derive_fallback(shared_secret, length)
    
    def _derive_cryptography(self, shared_secret: bytes, length: int) -> Optional[bytes]:
        """使用 cryptography 库派生密钥"""
        try:
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=length,
                salt=self.salt,
                info=self.info,
                backend=default_backend()
            )
            key_material = hkdf.derive(shared_secret)
            logger.info(f"Key material derived (cryptography): {len(key_material)} bytes")
            return key_material
        except Exception as e:
            logger.error(f"Key derivation failed: {e}")
            return None
    
    def _derive_fallback(self, shared_secret: bytes, length: int) -> Optional[bytes]:
        """
        纯 Python 回退密钥派生
        
        使用 HMAC-SHA256 实现简化的 HKDF
        注意: 这不是标准的 HKDF，但提供类似功能
        """
        logger.warning("Using fallback key derivation")
        try:
            # 简化的 HKDF 实现
            # 1. Extract
            if self.salt:
                prk = hmac.new(self.salt, shared_secret, hashlib.sha256).digest()
            else:
                prk = hmac.new(b'\x00' * 32, shared_secret, hashlib.sha256).digest()
            
            # 2. Expand
            okm = b''
            previous = b''
            counter = 1
            
            while len(okm) < length:
                counter_bytes = bytes([counter])
                data = previous + self.info + counter_bytes
                previous = hmac.new(prk, data, hashlib.sha256).digest()
                okm += previous
                counter += 1
            
            key_material = okm[:length]
            logger.info(f"Key material derived (fallback): {len(key_material)} bytes")
            return key_material
        except Exception as e:
            logger.error(f"Fallback key derivation failed: {e}")
            return None
    
    def extract_keys(self, key_material: bytes) -> dict:
        """
        提取各个密钥
        
        Args:
            key_material: 密钥材料 (至少48字节)
            
        Returns:
            包含 aes_key, nonce_base, padding 的字典
            
        Raises:
            ValueError: 密钥材料长度不足
        """
        if len(key_material) < 48:
            raise ValueError(f"Key material too short: {len(key_material)} bytes, expected 48")
        
        return {
            'aes_key': key_material[:16],           # 16 bytes for AES-128
            'nonce_base': key_material[16:28],      # 12 bytes for GCM nonce
            'padding': key_material[28:48],         # 20 bytes padding/reserved
        }
    
    def derive_with_salt(self, shared_secret: bytes, salt: bytes, length: int = 48) -> Optional[bytes]:
        """
        使用指定 salt 派生密钥
        
        Args:
            shared_secret: 共享密钥
            salt: 盐值
            length: 派生密钥长度
            
        Returns:
            密钥材料或 None
        """
        self.salt = salt
        return self.derive(shared_secret, length)


# 便捷函数
def hkdf_derive(shared_secret: bytes, salt: Optional[bytes] = None, length: int = 48) -> Optional[bytes]:
    """
    便捷密钥派生函数
    
    Args:
        shared_secret: 共享密钥
        salt: 盐值 (可选)
        length: 派生密钥长度
        
    Returns:
        密钥材料
    """
    hkdf = HKDFKeyDerivation()
    if salt:
        return hkdf.derive_with_salt(shared_secret, salt, length)
    return hkdf.derive(shared_secret, length)


def extract_keys(key_material: bytes) -> dict:
    """
    便捷密钥提取函数
    
    Args:
        key_material: 密钥材料
        
    Returns:
        包含 aes_key, nonce_base, padding 的字典
    """
    hkdf = HKDFKeyDerivation()
    return hkdf.extract_keys(key_material)


# 版本信息
__version__ = "1.1.0"
__all__ = [
    'HKDFKeyDerivation',
    'hkdf_derive',
    'extract_keys',
    'CRYPTOGRAPHY_AVAILABLE'
]