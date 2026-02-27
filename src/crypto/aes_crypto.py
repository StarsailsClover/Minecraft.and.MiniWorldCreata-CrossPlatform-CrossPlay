#!/usr/bin/env python3
"""
AES加密模块
处理迷你世界国服和外服的加密通信

国服：AES-128-CBC
外服：AES-256-GCM
"""

import os
import logging
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import hashlib
import base64

logger = logging.getLogger(__name__)


class AESCipher:
    """AES加密器"""
    
    def __init__(self, key: bytes, mode: str = "CBC", iv: bytes = None):
        """
        初始化AES加密器
        
        Args:
            key: 密钥（128/192/256位）
            mode: 加密模式（CBC, GCM）
            iv: 初始向量（CBC模式需要）
        """
        self.key = key
        self.mode = mode.upper()
        self.iv = iv or os.urandom(16)
        self.backend = default_backend()
        
    def encrypt_cbc(self, plaintext: bytes) -> bytes:
        """
        AES-128-CBC加密（国服使用）
        
        Args:
            plaintext: 明文数据
            
        Returns:
            加密后的数据（IV + ciphertext）
        """
        try:
            # PKCS7填充
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plaintext) + padder.finalize()
            
            # 创建加密器
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(self.iv),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            # 加密
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # 返回IV + ciphertext
            return self.iv + ciphertext
            
        except Exception as e:
            logger.error(f"CBC加密失败: {e}")
            raise
    
    def decrypt_cbc(self, ciphertext: bytes) -> bytes:
        """
        AES-128-CBC解密（国服使用）
        
        Args:
            ciphertext: 加密数据（IV + ciphertext）
            
        Returns:
            解密后的明文
        """
        try:
            # 提取IV
            iv = ciphertext[:16]
            encrypted_data = ciphertext[16:]
            
            # 创建解密器
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            # 解密
            padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # 去除填充
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_data) + unpadder.finalize()
            
            return plaintext
            
        except Exception as e:
            logger.error(f"CBC解密失败: {e}")
            raise
    
    def encrypt_gcm(self, plaintext: bytes, associated_data: bytes = None) -> Tuple[bytes, bytes]:
        """
        AES-256-GCM加密（外服使用）
        
        Args:
            plaintext: 明文数据
            associated_data: 附加认证数据（AAD）
            
        Returns:
            (ciphertext, tag) 元组
        """
        try:
            # 生成随机nonce
            nonce = os.urandom(12)
            
            # 创建加密器
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.GCM(nonce),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            # 添加AAD
            if associated_data:
                encryptor.authenticate_additional_data(associated_data)
            
            # 加密
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            tag = encryptor.tag
            
            # 返回 nonce + ciphertext + tag
            return nonce + ciphertext, tag
            
        except Exception as e:
            logger.error(f"GCM加密失败: {e}")
            raise
    
    def decrypt_gcm(self, ciphertext: bytes, tag: bytes, associated_data: bytes = None) -> bytes:
        """
        AES-256-GCM解密（外服使用）
        
        Args:
            ciphertext: 加密数据（nonce + ciphertext）
            tag: 认证标签
            associated_data: 附加认证数据
            
        Returns:
            解密后的明文
        """
        try:
            # 提取nonce
            nonce = ciphertext[:12]
            encrypted_data = ciphertext[12:]
            
            # 创建解密器
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.GCM(nonce, tag),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            # 添加AAD
            if associated_data:
                decryptor.authenticate_additional_data(associated_data)
            
            # 解密
            plaintext = decryptor.update(encrypted_data) + decryptor.finalize()
            
            return plaintext
            
        except Exception as e:
            logger.error(f"GCM解密失败: {e}")
            raise


class MiniWorldEncryption:
    """迷你世界加密管理器"""
    
    def __init__(self, region: str = "CN"):
        """
        初始化加密管理器
        
        Args:
            region: 区域（CN=国服, GLOBAL=外服）
        """
        self.region = region.upper()
        self.cipher: Optional[AESCipher] = None
        self.session_key: Optional[bytes] = None
        
    def derive_key(self, password: str, salt: bytes = None) -> bytes:
        """
        从密码派生密钥
        
        Args:
            password: 密码
            salt: 盐值
            
        Returns:
            派生的密钥
        """
        if salt is None:
            salt = os.urandom(16)
        
        # 使用PBKDF2派生密钥
        if self.region == "CN":
            # 国服：AES-128-CBC，需要128位密钥
            key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 10000, dklen=16)
        else:
            # 外服：AES-256-GCM，需要256位密钥
            key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 10000, dklen=32)
        
        return key
    
    def set_session_key(self, key: bytes):
        """
        设置会话密钥
        
        Args:
            key: 会话密钥
        """
        self.session_key = key
        self.cipher = AESCipher(key, mode="CBC" if self.region == "CN" else "GCM")
        logger.info(f"[{self.region}] 会话密钥已设置")
    
    def encrypt(self, data: bytes) -> bytes:
        """
        加密数据
        
        Args:
            data: 明文数据
            
        Returns:
            加密后的数据
        """
        if not self.cipher:
            raise ValueError("会话密钥未设置")
        
        if self.region == "CN":
            return self.cipher.encrypt_cbc(data)
        else:
            ciphertext, tag = self.cipher.encrypt_gcm(data)
            return ciphertext + tag
    
    def decrypt(self, data: bytes) -> bytes:
        """
        解密数据
        
        Args:
            data: 加密数据
            
        Returns:
            解密后的明文
        """
        if not self.cipher:
            raise ValueError("会话密钥未设置")
        
        if self.region == "CN":
            return self.cipher.decrypt_cbc(data)
        else:
            # GCM模式：分离tag
            tag = data[-16:]
            ciphertext = data[:-16]
            return self.cipher.decrypt_gcm(ciphertext, tag)


def generate_random_key(size: int = 16) -> bytes:
    """
    生成随机密钥
    
    Args:
        size: 密钥大小（字节）
        
    Returns:
        随机密钥
    """
    return os.urandom(size)


def hash_password(password: str, method: str = "md5_double") -> str:
    """
    密码哈希（推测的迷你世界密码算法）
    
    Args:
        password: 明文密码
        method: 哈希方法
        
    Returns:
        哈希后的密码
    """
    if method == "md5_double":
        # 双重MD5（常见做法）
        first = hashlib.md5(password.encode()).hexdigest()
        second = hashlib.md5(first.encode()).hexdigest()
        return second
    elif method == "md5_salt":
        # MD5 + 盐（需要知道盐值）
        # TODO: 从DEX中确认实际算法
        salted = password + "miniworld_salt"
        return hashlib.md5(salted.encode()).hexdigest()
    else:
        # 默认SHA256
        return hashlib.sha256(password.encode()).hexdigest()
