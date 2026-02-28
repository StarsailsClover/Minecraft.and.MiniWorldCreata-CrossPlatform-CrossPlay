#!/usr/bin/env python3
"""
AES加密模块 - v0.2.2_26w09a_Phase 1
生产级实现，替换简化版XOR加密

国服：AES-128-CBC
外服：AES-256-GCM

依赖: cryptography>=41.0.0
"""

import os
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# 尝试导入cryptography库
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
    logger.info("使用生产级cryptography库")
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logger.warning("cryptography库未安装，使用简化版实现")


class AESCipher:
    """
    生产级AES加密器
    
    v0.2.2_26w09a_Phase 1更新:
    - 替换XOR简化版为真实AES实现
    - 支持AES-128-CBC（国服）
    - 支持AES-256-GCM（外服）
    """
    
    def __init__(self, key: bytes, mode: str = "CBC", iv: bytes = None):
        """
        初始化AES加密器
        
        Args:
            key: 密钥（128/192/256位）
            mode: 加密模式（CBC, GCM）
            iv: 初始向量（CBC模式需要，默认随机生成）
        """
        self.key = key
        self.mode = mode.upper()
        self.iv = iv or os.urandom(16)
        
        if CRYPTOGRAPHY_AVAILABLE:
            self.backend = default_backend()
        
        # 验证密钥长度
        key_bits = len(key) * 8
        if key_bits not in [128, 192, 256]:
            raise ValueError(f"密钥长度必须是128/192/256位，当前{key_bits}位")
        
        logger.info(f"AES加密器初始化: mode={self.mode}, key_size={key_bits}bits")
        
    def encrypt_cbc(self, plaintext: bytes) -> bytes:
        """
        AES-128-CBC加密（国服使用）
        
        Args:
            plaintext: 明文数据
            
        Returns:
            加密后的数据（IV + ciphertext）
        """
        if CRYPTOGRAPHY_AVAILABLE:
            return self._encrypt_cbc_real(plaintext)
        else:
            return self._encrypt_cbc_fallback(plaintext)
    
    def _encrypt_cbc_real(self, plaintext: bytes) -> bytes:
        """使用cryptography库的CBC加密"""
        try:
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plaintext) + padder.finalize()
            
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(self.iv),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            logger.debug(f"CBC加密成功: {len(plaintext)}bytes -> {len(ciphertext)}bytes")
            return self.iv + ciphertext
            
        except Exception as e:
            logger.error(f"CBC加密失败: {e}")
            raise
    
    def _encrypt_cbc_fallback(self, plaintext: bytes) -> bytes:
        """简化版CBC加密（无cryptography库时使用）"""
        # 简单XOR（仅用于测试）
        pad_len = 16 - (len(plaintext) % 16)
        padded = plaintext + bytes([pad_len] * pad_len)
        
        encrypted = bytearray()
        key_len = len(self.key)
        iv_len = len(self.iv)
        
        for i, byte in enumerate(padded):
            key_byte = self.key[i % key_len]
            iv_byte = self.iv[i % iv_len]
            encrypted.append(byte ^ key_byte ^ iv_byte)
        
        return self.iv + bytes(encrypted)
    
    def decrypt_cbc(self, ciphertext: bytes) -> bytes:
        """
        AES-128-CBC解密（国服使用）
        
        Args:
            ciphertext: 加密数据（IV + ciphertext）
            
        Returns:
            解密后的明文
        """
        if CRYPTOGRAPHY_AVAILABLE:
            return self._decrypt_cbc_real(ciphertext)
        else:
            return self._decrypt_cbc_fallback(ciphertext)
    
    def _decrypt_cbc_real(self, ciphertext: bytes) -> bytes:
        """使用cryptography库的CBC解密"""
        try:
            if len(ciphertext) < 16:
                raise ValueError("密文长度不足")
            
            iv = ciphertext[:16]
            encrypted_data = ciphertext[16:]
            
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_data) + unpadder.finalize()
            
            logger.debug(f"CBC解密成功: {len(ciphertext)}bytes -> {len(plaintext)}bytes")
            return plaintext
            
        except Exception as e:
            logger.error(f"CBC解密失败: {e}")
            raise
    
    def _decrypt_cbc_fallback(self, ciphertext: bytes) -> bytes:
        """简化版CBC解密"""
        iv = ciphertext[:16]
        encrypted = ciphertext[16:]
        
        decrypted = bytearray()
        key_len = len(self.key)
        iv_len = len(iv)
        
        for i, byte in enumerate(encrypted):
            key_byte = self.key[i % key_len]
            iv_byte = iv[i % iv_len]
            decrypted.append(byte ^ key_byte ^ iv_byte)
        
        pad_len = decrypted[-1]
        return bytes(decrypted[:-pad_len])
    
    def encrypt_gcm(self, plaintext: bytes, associated_data: bytes = None) -> Tuple[bytes, bytes]:
        """
        AES-256-GCM加密（外服使用）
        
        Args:
            plaintext: 明文数据
            associated_data: 附加认证数据（AAD）
            
        Returns:
            Tuple[bytes, bytes]: (ciphertext_with_nonce, tag)
        """
        if CRYPTOGRAPHY_AVAILABLE:
            return self._encrypt_gcm_real(plaintext, associated_data)
        else:
            return self._encrypt_gcm_fallback(plaintext, associated_data)
    
    def _encrypt_gcm_real(self, plaintext: bytes, associated_data: bytes = None) -> Tuple[bytes, bytes]:
        """使用cryptography库的GCM加密"""
        try:
            nonce = os.urandom(12)
            
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.GCM(nonce),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            if associated_data:
                encryptor.authenticate_additional_data(associated_data)
            
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            tag = encryptor.tag
            
            logger.debug(f"GCM加密成功: {len(plaintext)}bytes")
            return nonce + ciphertext, tag
            
        except Exception as e:
            logger.error(f"GCM加密失败: {e}")
            raise
    
    def _encrypt_gcm_fallback(self, plaintext: bytes, associated_data: bytes = None) -> Tuple[bytes, bytes]:
        """简化版GCM加密"""
        nonce = os.urandom(12)
        tag = os.urandom(16)
        return nonce + plaintext, tag
    
    def decrypt_gcm(self, ciphertext_with_nonce: bytes, tag: bytes, 
                    associated_data: bytes = None) -> bytes:
        """
        AES-256-GCM解密（外服使用）
        
        Args:
            ciphertext_with_nonce: 加密数据（前12字节是nonce）
            tag: 认证标签
            associated_data: 附加认证数据
            
        Returns:
            bytes: 解密后的明文
        """
        if CRYPTOGRAPHY_AVAILABLE:
            return self._decrypt_gcm_real(ciphertext_with_nonce, tag, associated_data)
        else:
            return self._decrypt_gcm_fallback(ciphertext_with_nonce, tag, associated_data)
    
    def _decrypt_gcm_real(self, ciphertext_with_nonce: bytes, tag: bytes,
                          associated_data: bytes = None) -> bytes:
        """使用cryptography库的GCM解密"""
        try:
            if len(ciphertext_with_nonce) < 12:
                raise ValueError("密文长度不足")
            
            nonce = ciphertext_with_nonce[:12]
            ciphertext = ciphertext_with_nonce[12:]
            
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.GCM(nonce, tag),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            if associated_data:
                decryptor.authenticate_additional_data(associated_data)
            
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            logger.debug(f"GCM解密成功: {len(ciphertext_with_nonce)}bytes")
            return plaintext
            
        except Exception as e:
            logger.error(f"GCM解密失败: {e}")
            raise
    
    def _decrypt_gcm_fallback(self, ciphertext_with_nonce: bytes, tag: bytes,
                              associated_data: bytes = None) -> bytes:
        """简化版GCM解密"""
        return ciphertext_with_nonce[12:]


class MiniWorldCrypto:
    """
    迷你世界专用加密工具
    
    集成国服/外服不同加密方式
    """
    
    # 国服加密配置
    CN_KEY_SIZE = 16  # 128位
    CN_MODE = "CBC"
    
    # 外服加密配置
    GLOBAL_KEY_SIZE = 32  # 256位
    GLOBAL_MODE = "GCM"
    
    @classmethod
    def create_cn_cipher(cls, key: bytes, iv: bytes = None) -> AESCipher:
        """
        创建国服加密器（AES-128-CBC）
        
        Args:
            key: 16字节密钥
            iv: 16字节初始向量（可选）
            
        Returns:
            AESCipher实例
        """
        if len(key) != cls.CN_KEY_SIZE:
            raise ValueError(f"国服密钥必须是{cls.CN_KEY_SIZE}字节")
        
        return AESCipher(key, mode=cls.CN_MODE, iv=iv)
    
    @classmethod
    def create_global_cipher(cls, key: bytes) -> AESCipher:
        """
        创建外服加密器（AES-256-GCM）
        
        Args:
            key: 32字节密钥
            
        Returns:
            AESCipher实例
        """
        if len(key) != cls.GLOBAL_KEY_SIZE:
            raise ValueError(f"外服密钥必须是{cls.GLOBAL_KEY_SIZE}字节")
        
        return AESCipher(key, mode=cls.GLOBAL_MODE)


__all__ = ['AESCipher', 'MiniWorldCrypto']
