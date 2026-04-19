"""
XXTEA 加密算法实现

基于标准 XXTEA 算法实现
使用 Python 的参考实现确保正确性

Copyright (c) 2026 MnMCP Contributors
SPDX-License-Identifier: MIT
"""

import struct
import os


def _xxtea_encrypt_block(v, k, n=6):
    """XXTEA 加密一个数据块"""
    def MX():
        return ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4)) ^ ((sum_val ^ y) + (k[(p & 3) ^ e] ^ z))
    
    y = v[0]
    z = v[n - 1]
    delta = 0x9E3779B9
    sum_val = 0
    q = 6 + 52 // n
    
    for _ in range(q):
        sum_val = (sum_val + delta) & 0xFFFFFFFF
        e = (sum_val >> 2) & 3
        for p in range(n - 1):
            z = v[p + 1]
            y = v[p] = (v[p] + MX()) & 0xFFFFFFFF
        z = v[0]
        y = v[n - 1] = (v[n - 1] + MX()) & 0xFFFFFFFF
    
    return v


def _xxtea_decrypt_block(v, k, n=6):
    """XXTEA 解密一个数据块"""
    def MX():
        return ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4)) ^ ((sum_val ^ y) + (k[(p & 3) ^ e] ^ z))
    
    y = v[0]
    z = v[n - 1]
    delta = 0x9E3779B9
    q = 6 + 52 // n
    sum_val = (q * delta) & 0xFFFFFFFF
    
    for _ in range(q):
        e = (sum_val >> 2) & 3
        for p in range(n - 1, 0, -1):
            z = v[p - 1]
            y = v[p] = (v[p] - MX()) & 0xFFFFFFFF
        z = v[n - 1]
        y = v[0] = (v[0] - MX()) & 0xFFFFFFFF
        sum_val = (sum_val - delta) & 0xFFFFFFFF
    
    return v


def xxtea_encrypt(data: bytes, key: bytes) -> bytes:
    """
    XXTEA 加密
    
    Args:
        data: 明文数据
        key: 16字节密钥
        
    Returns:
        加密后的数据 (包含4字节长度前缀)
    """
    if len(key) != 16:
        raise ValueError("Key must be 16 bytes")
    
    if not data:
        return struct.pack('<I', 0)
    
    # 保存原始长度
    original_len = len(data)
    
    # 确保至少有8字节
    if len(data) < 8:
        data = data + b'\x00' * (8 - len(data))
    
    # 转换为32位整数数组
    v = []
    for i in range(0, len(data), 4):
        chunk = data[i:i+4]
        if len(chunk) < 4:
            chunk = chunk + b'\x00' * (4 - len(chunk))
        v.append(struct.unpack('<I', chunk)[0])
    
    k = list(struct.unpack('<4I', key))
    n = len(v)
    
    # 加密
    v = _xxtea_encrypt_block(v, k, n)
    
    # 打包结果
    result = struct.pack('<I', original_len)
    result += struct.pack('<' + 'I' * n, *v)
    return result


def xxtea_decrypt(data: bytes, key: bytes) -> bytes:
    """
    XXTEA 解密
    
    Args:
        data: 加密数据 (包含4字节长度前缀)
        key: 16字节密钥
        
    Returns:
        解密后的数据
    """
    if len(key) != 16:
        raise ValueError("Key must be 16 bytes")
    
    if len(data) < 4:
        return b''
    
    # 提取原始长度
    original_len = struct.unpack('<I', data[:4])[0]
    data = data[4:]
    
    if not data:
        return b''
    
    # 转换为32位整数数组
    v = list(struct.unpack('<' + 'I' * (len(data) // 4), data))
    k = list(struct.unpack('<4I', key))
    n = len(v)
    
    # 解密
    v = _xxtea_decrypt_block(v, k, n)
    
    # 打包结果
    result = struct.pack('<' + 'I' * n, *v)
    return result[:original_len]


class XXTEACipher:
    """
    XXTEA 加密器类
    
    Example:
        >>> cipher = XXTEACipher(b'0123456789abcdef')
        >>> encrypted = cipher.encrypt(b'Hello World!')
        >>> decrypted = cipher.decrypt(encrypted)
    """
    
    def __init__(self, key: bytes):
        """
        初始化
        
        Args:
            key: 16字节密钥
        """
        if len(key) != 16:
            raise ValueError("Key must be 16 bytes")
        self.key = key
    
    def encrypt(self, data: bytes) -> bytes:
        """加密"""
        return xxtea_encrypt(data, self.key)
    
    def decrypt(self, data: bytes) -> bytes:
        """解密"""
        return xxtea_decrypt(data, self.key)
    
    @staticmethod
    def generate_key() -> bytes:
        """生成随机密钥"""
        return os.urandom(16)


# 版本信息
__version__ = "1.0.0"
__all__ = [
    'XXTEACipher',
    'xxtea_encrypt',
    'xxtea_decrypt'
]
