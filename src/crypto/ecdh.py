"""
ECDH 密钥交换

基于 P-256 (prime256v1) 曲线
提供密钥交换功能，支持纯Python回退实现

Copyright (c) 2026 MnMCP Contributors
SPDX-License-Identifier: MIT
"""

import logging
import os
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# 尝试导入 cryptography
try:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logger.warning("cryptography library not installed, using fallback")


class ECDHKeyExchange:
    """
    ECDH 密钥交换
    
    基于 P-256 (prime256v1) 曲线
    优先使用 cryptography 库，回退到模拟实现
    
    Attributes:
        private_key: 私钥
        public_key: 公钥
        server_public_key: 服务器公钥
        shared_secret: 共享密钥
    """
    
    # 服务端公钥 (PEM格式)
    SERVER_PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEp4e24GoKyeS4utp998HyD9MJzsR1
h8R74SnoKmwW8nz8qZHaAynxU8P5dd29ORHGQEGUW4IFUVsg5I3XTdjRdQ==
-----END PUBLIC KEY-----"""
    
    def __init__(self):
        """初始化 ECDH 密钥交换器"""
        self.private_key = None
        self.public_key = None
        self.server_public_key = None
        self.shared_secret = None
        
        # 回退模式使用的模拟密钥
        self._fallback_private = None
        self._fallback_public = None
    
    def generate_keypair(self) -> bool:
        """
        生成客户端密钥对
        
        Returns:
            是否成功
        """
        if CRYPTOGRAPHY_AVAILABLE:
            return self._generate_keypair_cryptography()
        else:
            return self._generate_keypair_fallback()
    
    def _generate_keypair_cryptography(self) -> bool:
        """使用 cryptography 库生成密钥对"""
        try:
            self.private_key = ec.generate_private_key(
                ec.SECP256R1(),  # P-256
                default_backend()
            )
            self.public_key = self.private_key.public_key()
            logger.info("ECDH keypair generated (cryptography)")
            return True
        except Exception as e:
            logger.error(f"Failed to generate keypair: {e}")
            return False
    
    def _generate_keypair_fallback(self) -> bool:
        """
        纯 Python 回退生成密钥对 (模拟)
        
        注意: 这不是真正的 ECDH，仅用于测试
        生成随机数据模拟密钥对
        """
        logger.warning("Using fallback key generation (NOT SECURE)")
        try:
            # 模拟私钥 (32字节)
            self._fallback_private = os.urandom(32)
            # 模拟公钥 (65字节未压缩格式)
            self._fallback_public = b'\x04' + os.urandom(64)
            logger.info("ECDH keypair generated (fallback)")
            return True
        except Exception as e:
            logger.error(f"Failed to generate fallback keypair: {e}")
            return False
    
    def load_server_public_key(self) -> bool:
        """
        加载服务端公钥
        
        Returns:
            是否成功
        """
        if CRYPTOGRAPHY_AVAILABLE:
            return self._load_server_key_cryptography()
        else:
            return self._load_server_key_fallback()
    
    def _load_server_key_cryptography(self) -> bool:
        """使用 cryptography 库加载服务器公钥"""
        try:
            self.server_public_key = serialization.load_pem_public_key(
                self.SERVER_PUBLIC_KEY_PEM.encode('utf-8'),
                backend=default_backend()
            )
            logger.info("Server public key loaded (cryptography)")
            return True
        except Exception as e:
            logger.error(f"Failed to load server public key: {e}")
            return False
    
    def _load_server_key_fallback(self) -> bool:
        """纯 Python 回退加载服务器公钥 (模拟)"""
        logger.warning("Using fallback server key loading (NOT SECURE)")
        # 模拟服务器公钥
        self.server_public_key = b'\x04' + os.urandom(64)
        return True
    
    def exchange(self) -> Optional[bytes]:
        """
        执行密钥交换
        
        Returns:
            共享密钥或 None
        """
        if CRYPTOGRAPHY_AVAILABLE:
            return self._exchange_cryptography()
        else:
            return self._exchange_fallback()
    
    def _exchange_cryptography(self) -> Optional[bytes]:
        """使用 cryptography 库执行密钥交换"""
        if not self.private_key or not self.server_public_key:
            logger.error("Keys not initialized")
            return None
        
        try:
            self.shared_secret = self.private_key.exchange(
                ec.ECDH(),
                self.server_public_key
            )
            logger.info(f"Shared secret derived: {len(self.shared_secret)} bytes")
            return self.shared_secret
        except Exception as e:
            logger.error(f"Key exchange failed: {e}")
            return None
    
    def _exchange_fallback(self) -> Optional[bytes]:
        """
        纯 Python 回退密钥交换 (模拟)
        
        注意: 这不是真正的 ECDH，仅用于测试
        返回模拟的共享密钥
        """
        logger.warning("Using fallback key exchange (NOT SECURE)")
        if not self._fallback_private:
            logger.error("Fallback keys not initialized")
            return None
        
        # 模拟共享密钥 (32字节)
        self.shared_secret = os.urandom(32)
        logger.info(f"Shared secret derived (fallback): {len(self.shared_secret)} bytes")
        return self.shared_secret
    
    def get_public_key_bytes(self) -> Optional[bytes]:
        """
        获取公钥字节表示 (用于发送给服务器)
        
        Returns:
            公钥字节
        """
        if CRYPTOGRAPHY_AVAILABLE:
            return self._get_public_key_cryptography()
        else:
            return self._get_public_key_fallback()
    
    def _get_public_key_cryptography(self) -> Optional[bytes]:
        """使用 cryptography 库获取公钥字节"""
        if not self.public_key:
            return None
        try:
            return self.public_key.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            )
        except Exception as e:
            logger.error(f"Failed to serialize public key: {e}")
            return None
    
    def _get_public_key_fallback(self) -> Optional[bytes]:
        """纯 Python 回退获取公钥字节"""
        return self._fallback_public
    
    def complete_exchange(self) -> Optional[bytes]:
        """
        完整的密钥交换流程
        
        Returns:
            共享密钥或 None
        """
        # 1. 生成密钥对
        if not self.generate_keypair():
            return None
        
        # 2. 加载服务器公钥
        if not self.load_server_public_key():
            return None
        
        # 3. 执行交换
        return self.exchange()


# 便捷函数
def ecdh_exchange() -> Optional[bytes]:
    """
    便捷密钥交换函数
    
    Returns:
        共享密钥
    """
    ecdh = ECDHKeyExchange()
    return ecdh.complete_exchange()


# 版本信息
__version__ = "1.1.0"
__all__ = [
    'ECDHKeyExchange',
    'ecdh_exchange',
    'CRYPTOGRAPHY_AVAILABLE'
]