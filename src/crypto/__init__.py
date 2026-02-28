"""加密模块"""
try:
    from .aes_crypto_real import AESCipherReal, MiniWorldEncryptionReal, hash_password_real
    __all__ = ['AESCipherReal', 'MiniWorldEncryptionReal', 'hash_password_real']
except ImportError:
    from .aes_crypto import AESCipher, MiniWorldEncryption, hash_password
    AESCipherReal = AESCipher
    MiniWorldEncryptionReal = MiniWorldEncryption
    hash_password_real = hash_password
    __all__ = ['AESCipher', 'MiniWorldEncryption', 'hash_password']
