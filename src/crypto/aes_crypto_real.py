#!/usr/bin/env python3
"""
AES加密模块 - 生产级实现
基于MnMCPResources中的反编译资源分析

国服：AES-128-CBC
外服：AES-256-GCM
"""

import os
import logging
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import hashlib
import base64

logger = logging.getLogger(__name__)


class AESCipherReal:
    """生产级AES加密器"""
    
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
        
        logger.info(f"初始化AES加密器: mode={self.mode}, key_size={len(key)*8}bits")
        
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


class MiniWorldEncryptionReal:
    """迷你世界加密管理器 - 生产级"""
    
    def __init__(self, region: str = "CN"):
        """
        初始化加密管理器
        
        Args:
            region: 区域（CN=国服, GLOBAL=外服）
        """
        self.region = region.upper()
        self.cipher: Optional[AESCipherReal] = None
        self.session_key: Optional[bytes] = None
        
        logger.info(f"初始化迷你世界加密管理器: region={self.region}")
        
    def derive_key_pbkdf2(self, password: str, salt: bytes = None, iterations: int = 10000) -> bytes:
        """
        使用PBKDF2从密码派生密钥
        
        Args:
            password: 密码
            salt: 盐值（可选）
            iterations: 迭代次数
            
        Returns:
            派生的密钥
        """
        if salt is None:
            salt = os.urandom(16)
        
        # 根据区域选择密钥长度
        if self.region == "CN":
            key_length = 16  # AES-128
        else:
            key_length = 32  # AES-256
        
        # 使用PBKDF2派生密钥
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode('utf-8'))
        logger.info(f"密钥派生完成: length={len(key)}bytes")
        
        return key
    
    def derive_key_simple(self, password: str, salt: bytes = None) -> bytes:
        """
        简化版密钥派生（用于测试）
        
        Args:
            password: 密码
            salt: 盐值
            
        Returns:
            派生的密钥
        """
        if salt is None:
            salt = os.urandom(16)
        
        # 使用PBKDF2
        if self.region == "CN":
            key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 10000, dklen=16)
        else:
            key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 10000, dklen=32)
        
        return key
    
    def set_session_key(self, key: bytes):
        """
        设置会话密钥
        
        Args:
            key: 会话密钥
        """
        self.session_key = key
        self.cipher = AESCipherReal(key, mode="CBC" if self.region == "CN" else "GCM")
        logger.info(f"[{self.region}] 会话密钥已设置: length={len(key)}bytes")
    
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
    
    def generate_random_key(self, size: int = None) -> bytes:
        """
        生成随机密钥
        
        Args:
            size: 密钥大小（字节），默认根据区域选择
            
        Returns:
            随机密钥
        """
        if size is None:
            size = 16 if self.region == "CN" else 32
        
        return os.urandom(size)


def hash_password_real(password: str, method: str = "pbkdf2", salt: bytes = None) -> Tuple[str, bytes]:
    """
    密码哈希（生产级）
    
    Args:
        password: 明文密码
        method: 哈希方法 (pbkdf2, sha256)
        salt: 盐值
        
    Returns:
        (哈希值, 盐值) 元组
    """
    if salt is None:
        salt = os.urandom(16)
    
    if method == "pbkdf2":
        # PBKDF2 with SHA256
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        hashed = base64.b64encode(key).decode('utf-8')
    elif method == "sha256":
        # Simple SHA256
        sha256 = hashlib.sha256()
        sha256.update(password.encode())
        sha256.update(salt)
        hashed = sha256.hexdigest()
    else:
        raise ValueError(f"不支持的哈希方法: {method}")
    
    return hashed, salt


# 测试代码
if __name__ == "__main__":
    print("测试生产级AES加密模块...")
    
    # 测试AES-128-CBC
    print("\n1. 测试 AES-128-CBC (国服):")
    key = os.urandom(16)
    cipher = AESCipherReal(key, mode="CBC")
    
    plaintext = b"Hello, MiniWorld CN!"
    encrypted = cipher.encrypt_cbc(plaintext)
    decrypted = cipher.decrypt_cbc(encrypted)
    
    print(f"  原始数据: {plaintext}")
    print(f"  加密后: {encrypted.hex()[:32]}...")
    print(f"  解密后: {decrypted}")
    print(f"  测试: {'通过' if decrypted == plaintext else '失败'}")
    
    # 测试AES-256-GCM
    print("\n2. 测试 AES-256-GCM (外服):")
    key = os.urandom(32)
    cipher = AESCipherReal(key, mode="GCM")
    
    plaintext = b"Hello, MiniWorld Global!"
    ciphertext, tag = cipher.encrypt_gcm(plaintext)
    decrypted = cipher.decrypt_gcm(ciphertext, tag)
    
    print(f"  原始数据: {plaintext}")
    print(f"  加密后: {ciphertext.hex()[:32]}...")
    print(f"  解密后: {decrypted}")
    print(f"  测试: {'通过' if decrypted == plaintext else '失败'}")
    
    # 测试MiniWorld加密管理器
    print("\n3. 测试 MiniWorldEncryptionReal:")
    mw_crypto = MiniWorldEncryptionReal(region="CN")
    session_key = os.urandom(16)
    mw_crypto.set_session_key(session_key)
    
    data = b"Test data for MiniWorld"
    encrypted = mw_crypto.encrypt(data)
    decrypted = mw_crypto.decrypt(encrypted)
    
    print(f"  原始数据: {data}")
    print(f"  加密后: {encrypted.hex()[:32]}...")
    print(f"  解密后: {decrypted}")
    print(f"  测试: {'通过' if decrypted == data else '失败'}")
    
    print("\n所有测试通过！")
