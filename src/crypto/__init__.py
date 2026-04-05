"""
加密层 - Crypto Layer

包含:
- ECDH 密钥交换
- HKDF 密钥派生
- AES-GCM 加密/解密
"""

try:
    # 尝试导入真实加密实现
    from .ecdh import ECDHKeyExchange
    from .hkdf import HKDFKeyDerivation
    from .aesgcm import AESGCMCipher
    _REAL_CRYPTO = True
except ImportError:
    # 如果 cryptography 未安装，使用模拟实现
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
