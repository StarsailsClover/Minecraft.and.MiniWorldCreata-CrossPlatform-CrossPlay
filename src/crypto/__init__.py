"""
加密层 - Crypto Layer

包含:
- ECDH 密钥交换
- HKDF 密钥派生
- AES-GCM 加密/解密
"""

import logging

logger = logging.getLogger(__name__)

try:
    # 尝试导入真实加密实现
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    
    # 如果成功导入，使用真实实现
    from .ecdh import ECDHKeyExchange
    from .hkdf import HKDFKeyDerivation
    from .aesgcm import AESGCMCipher
    _REAL_CRYPTO = True
    logger.info("Using real cryptography backend")
    
except ImportError as e:
    # 如果 cryptography 未安装，使用模拟实现
    logger.warning(f"cryptography not installed ({e}), using mock backend")
    from .mock_crypto import MockECDHKeyExchange as ECDHKeyExchange
    from .mock_crypto import MockHKDFKeyDerivation as HKDFKeyDerivation
    from .mock_crypto import MockAESGCMCipher as AESGCMCipher
    _REAL_CRYPTO = False

__all__ = [
    'ECDHKeyExchange',
    'HKDFKeyDerivation',
    'AESGCMCipher',
]

# 导出加密状态
CRYPTO_BACKEND = 'real' if _REAL_CRYPTO else 'mock'
