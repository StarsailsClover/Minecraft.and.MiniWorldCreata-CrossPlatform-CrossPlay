#!/usr/bin/env python3
"""
AES加密模块（简化版，使用纯Python实现）
处理迷你世界国服和外服的加密通信

国服：AES-128-CBC
外服：AES-256-GCM

注意：生产环境应使用cryptography库
"""

import os
import logging
from typing import Optional, Tuple
import hashlib
import base64

logger = logging.getLogger(__name__)


class AESCipher:
    """AES加密器（简化版，仅用于测试）"""
    
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
        
        logger.warning("使用简化版AES加密器，生产环境请安装cryptography库")
        
    def encrypt_cbc(self, plaintext: bytes) -> bytes:
        """
        AES-128-CBC加密（国服使用）
        
        注意：这是简化版，仅用于测试
        """
        try:
            # 简化版：使用XOR加密（仅用于测试）
            # 实际应使用：from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            
            # PKCS7填充
            pad_len = 16 - (len(plaintext) % 16)
            padded = plaintext + bytes([pad_len] * pad_len)
            
            # 简化的XOR加密（仅用于测试！）
            encrypted = bytearray()
            key_len = len(self.key)
            iv_len = len(self.iv)
            
            for i, byte in enumerate(padded):
                key_byte = self.key[i % key_len]
                iv_byte = self.iv[i % iv_len]
                encrypted.append(byte ^ key_byte ^ iv_byte)
            
            # 返回IV + ciphertext
            return self.iv + bytes(encrypted)
            
        except Exception as e:
            logger.error(f"CBC加密失败: {e}")
            raise
    
    def decrypt_cbc(self, ciphertext: bytes) -> bytes:
        """
        AES-128-CBC解密（国服使用）
        
        注意：这是简化版，仅用于测试
        """
        try:
            # 提取IV
            iv = ciphertext[:16]
            encrypted = ciphertext[16:]
            
            # 简化的XOR解密
            decrypted = bytearray()
            key_len = len(self.key)
            iv_len = len(iv)
            
            for i, byte in enumerate(encrypted):
                key_byte = self.key[i % key_len]
                iv_byte = iv[i % iv_len]
                decrypted.append(byte ^ key_byte ^ iv_byte)
            
            # 去除PKCS7填充
            pad_len = decrypted[-1]
            if pad_len > 0 and pad_len <= 16:
                decrypted = decrypted[:-pad_len]
            
            return bytes(decrypted)
            
        except Exception as e:
            logger.error(f"CBC解密失败: {e}")
            raise
    
    def encrypt_gcm(self, plaintext: bytes, associated_data: bytes = None) -> Tuple[bytes, bytes]:
        """
        AES-256-GCM加密（外服使用）
        
        注意：这是简化版，仅用于测试
        """
        # 简化版：返回明文 + 模拟tag
        nonce = os.urandom(12)
        tag = os.urandom(16)
        return nonce + plaintext, tag
    
    def decrypt_gcm(self, ciphertext: bytes, tag: bytes, associated_data: bytes = None) -> bytes:
        """
        AES-256-GCM解密（外服使用）
        
        注意：这是简化版，仅用于测试
        """
        # 简化版：提取nonce后的数据
        return ciphertext[12:]


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
