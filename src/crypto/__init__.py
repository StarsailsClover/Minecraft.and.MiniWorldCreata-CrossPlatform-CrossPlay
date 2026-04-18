"""
加密层 - Crypto Layer

包含:
- ECDH 密钥交换
- HKDF 密钥派生
- AES-GCM 加密/解密
"""

import logging

logger = logging.getLogger(__name__)

# 优先使用真实加密实现（基于标准库）
try:
    from .real_crypto import (
        RealECDHKeyExchange as ECDHKeyExchange,
        RealHKDFKeyDerivation as HKDFKeyDerivation,
        RealAESGCMCipher as AESGCMCipher
    )
    _REAL_CRYPTO = True
    CRYPTO_BACKEND = 'real_stdlib'
    logger.info("Using real cryptography backend (stdlib)")
    
except ImportError as e:
    logger.error(f"Failed to import real_crypto: {e}")
    # 降级到模拟实现
    from .mock_crypto import (
        MockECDHKeyExchange as ECDHKeyExchange,
        MockHKDFKeyDerivation as HKDFKeyDerivation,
        MockAESGCMCipher as AESGCMCipher
    )
    _REAL_CRYPTO = False
    CRYPTO_BACKEND = 'mock'
    logger.warning("Using mock cryptography backend")

__all__ = [
    'ECDHKeyExchange',
    'HKDFKeyDerivation',
    'AESGCMCipher',
    'CRYPTO_BACKEND',
]
