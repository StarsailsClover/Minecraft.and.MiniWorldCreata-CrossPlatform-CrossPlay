"""
WPKG 编解码器

基于腾讯 iLink Network v2.3.2.f3 逆向分析实现
WPKG (WeChat Package) 是 iLink 协议的底层传输格式

Copyright (c) 2026 MnMCP Contributors
SPDX-License-Identifier: MIT
"""

import struct
import zlib
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from enum import IntEnum

from ..crypto.aesgcm import AESGCMCipher

logger = logging.getLogger(__name__)


class WPKGFlags(IntEnum):
    """
    WPKG 标志位
    
    用于指示数据包的属性和状态
    """
    NONE = 0x00
    ENCRYPTED = 0x01      # 数据已加密
    COMPRESSED = 0x02     # 数据已压缩
    HAS_AAD = 0x04        # 包含附加认证数据


class WPKGCompressAlgo(IntEnum):
    """
    压缩算法类型
    
    支持的压缩算法枚举
    """
    NONE = 0x00
    ZLIB = 0x01
    LZ4 = 0x02


class WPKGEncryptAlgo(IntEnum):
    """
    加密算法类型
    
    支持的加密算法枚举
    """
    NONE = 0x00
    AES_GCM = 0x01
    HYBRID_ECDH = 0x02


@dataclass(frozen=True)
class WPKGHeader:
    """
    WPKG 包头结构 (16 bytes)
    
    包头格式:
    Offset  Len  Field
    0       2    Magic (0xABCD)
    2       1    Version (0x01)
    3       1    Flags
    4       1    CompressAlgo
    5       1    EncryptAlgo
    6       2    HeaderLen (16)
    8       4    PayloadLen
    12      4    SequenceNum
    
    Attributes:
        flags: 数据包标志位
        compress_algo: 压缩算法
        encrypt_algo: 加密算法
        payload_len: 有效载荷长度
        seq_num: 序列号
    """
    MAGIC: int = 0xABCD
    VERSION: int = 0x01
    HEADER_LEN: int = 16
    
    flags: int = 0
    compress_algo: int = WPKGCompressAlgo.NONE
    encrypt_algo: int = WPKGEncryptAlgo.NONE
    payload_len: int = 0
    seq_num: int = 0
    
    def encode(self) -> bytes:
        """
        编码包头为字节流
        
        Returns:
            16字节的包头数据
        """
        return struct.pack('>HBBHHII',
            self.MAGIC,
            self.VERSION,
            self.flags,
            self.compress_algo,
            self.HEADER_LEN,
            self.payload_len,
            self.seq_num
        )
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['WPKGHeader']:
        """
        从字节流解码包头
        
        Args:
            data: 原始字节数据
            
        Returns:
            解码后的 WPKGHeader 实例，失败返回 None
        """
        if len(data) < cls.HEADER_LEN:
            logger.warning(f"数据长度不足: {len(data)} < {cls.HEADER_LEN}")
            return None
        
        try:
            magic, version, flags, compress_algo, header_len, payload_len, seq_num = \
                struct.unpack('>HBBHHII', data[:cls.HEADER_LEN])
            
            if magic != cls.MAGIC:
                logger.error(f"Invalid magic: {hex(magic)}, expected: {hex(cls.MAGIC)}")
                return None
            
            if version != cls.VERSION:
                logger.warning(f"Unknown version: {version}, expected: {cls.VERSION}")
            
            return cls(
                flags=flags,
                compress_algo=compress_algo,
                encrypt_algo=WPKGEncryptAlgo.NONE,
                payload_len=payload_len,
                seq_num=seq_num
            )
        except struct.error as e:
            logger.error(f"Header decode error: {e}")
            return None


@dataclass
class WPKGPacket:
    """
    WPKG 完整数据包
    
    包含包头、有效载荷和可选的认证数据
    
    Attributes:
        header: 数据包头部
        payload: 有效载荷
        aad: 附加认证数据 (可选)
        tag: GCM 认证标签 (可选)
    """
    header: WPKGHeader
    payload: bytes
    aad: Optional[bytes] = None
    tag: Optional[bytes] = None
    
    def encode(self) -> bytes:
        """
        编码完整数据包
        
        Returns:
            完整的数据包字节流
        """
        header_bytes = self.header.encode()
        
        # 如果有 AAD，先发送 AAD 长度 + AAD
        if self.aad:
            aad_len = len(self.aad)
            header_bytes += struct.pack('>I', aad_len) + self.aad
        
        # 如果有认证标签，附加到 payload
        payload = self.payload
        if self.tag:
            payload += self.tag
        
        return header_bytes + payload
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['WPKGPacket']:
        """
        从字节流解码完整数据包
        
        Args:
            data: 原始字节数据
            
        Returns:
            解码后的 WPKGPacket 实例，失败返回 None
        """
        header = WPKGHeader.decode(data)
        if not header:
            return None
        
        offset = WPKGHeader.HEADER_LEN
        aad = None
        
        # 解析 AAD (如果存在)
        if header.flags & WPKGFlags.HAS_AAD:
            if len(data) < offset + 4:
                logger.error("AAD length field missing")
                return None
            aad_len = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4
            aad = data[offset:offset+aad_len]
            offset += aad_len
        
        # 提取 payload (包含 GCM tag 如果加密)
        payload_end = offset + header.payload_len
        if payload_end > len(data):
            logger.error(f"Payload exceeds data length: {payload_end} > {len(data)}")
            return None
        
        payload = data[offset:payload_end]
        
        # 如果有加密，最后 16 bytes 是 GCM tag
        tag = None
        if header.flags & WPKGFlags.ENCRYPTED:
            if len(payload) >= 16:
                tag = payload[-16:]
                payload = payload[:-16]
        
        return cls(
            header=header,
            payload=payload,
            aad=aad,
            tag=tag
        )
    
    def is_encrypted(self) -> bool:
        """检查数据包是否加密"""
        return bool(self.header.flags & WPKGFlags.ENCRYPTED)
    
    def is_compressed(self) -> bool:
        """检查数据包是否压缩"""
        return bool(self.header.flags & WPKGFlags.COMPRESSED)


class WPKGCodec:
    """
    WPKG 编解码器
    
    提供数据包的编码和解码功能，支持压缩和加密
    
    Example:
        >>> from crypto.aesgcm import AESGCMCipher
        >>> cipher = AESGCMCipher(key, nonce_base)
        >>> codec = WPKGCodec(cipher)
        >>> encoded = codec.encode(b"Hello", compress=True, encrypt=True)
        >>> decoded = codec.decode(encoded)
    """
    
    def __init__(self, cipher: Optional[AESGCMCipher] = None):
        """
        初始化编解码器
        
        Args:
            cipher: AES-GCM 加密器实例 (可选)
        """
        self.cipher = cipher
        self._seq_counter = 0
        self._stats = {
            'encoded': 0,
            'decoded': 0,
            'errors': 0
        }
    
    def encode(self, payload: bytes, 
               compress: bool = False,
               encrypt: bool = False,
               aad: Optional[bytes] = None) -> Optional[bytes]:
        """
        编码数据包
        
        Args:
            payload: 原始数据
            compress: 是否压缩
            encrypt: 是否加密
            aad: 附加认证数据 (可选)
        
        Returns:
            编码后的数据包，失败返回 None
        """
        try:
            flags = 0
            compress_algo = WPKGCompressAlgo.NONE
            encrypt_algo = WPKGEncryptAlgo.NONE
            
            # 压缩
            if compress:
                payload = zlib.compress(payload, level=6)
                flags |= WPKGFlags.COMPRESSED
                compress_algo = WPKGCompressAlgo.ZLIB
            
            # 加密
            tag = None
            if encrypt and self.cipher:
                encrypted = self.cipher.encrypt(payload, aad)
                if encrypted is None:
                    logger.error("Encryption failed")
                    return None
                tag = encrypted[-16:]
                payload = encrypted[:-16]
                flags |= WPKGFlags.ENCRYPTED
                encrypt_algo = WPKGEncryptAlgo.AES_GCM
            elif encrypt and not self.cipher:
                logger.warning("Encryption requested but cipher not available")
            
            if aad:
                flags |= WPKGFlags.HAS_AAD
            
            # 构建包头
            header = WPKGHeader(
                flags=flags,
                compress_algo=compress_algo,
                encrypt_algo=encrypt_algo,
                payload_len=len(payload) + (len(tag) if tag else 0),
                seq_num=self._next_seq()
            )
            
            # 构建完整包
            packet = WPKGPacket(
                header=header,
                payload=payload,
                aad=aad,
                tag=tag
            )
            
            self._stats['encoded'] += 1
            return packet.encode()
            
        except Exception as e:
            logger.error(f"WPKG encode error: {e}")
            self._stats['errors'] += 1
            return None
    
    def decode(self, data: bytes, 
               verify_aad: bool = True) -> Optional[bytes]:
        """
        解码数据包
        
        Args:
            data: 编码后的数据包
            verify_aad: 是否验证 AAD
        
        Returns:
            解码后的原始数据，失败返回 None
        """
        try:
            packet = WPKGPacket.decode(data)
            if not packet:
                return None
            
            payload = packet.payload
            
            # 解密
            if packet.header.flags & WPKGFlags.ENCRYPTED:
                if not self.cipher:
                    logger.error("Cipher not available for decryption")
                    return None
                
                ciphertext_with_tag = payload
                if packet.tag:
                    ciphertext_with_tag += packet.tag
                
                decrypted = self.cipher.decrypt(
                    ciphertext_with_tag, 
                    packet.aad if verify_aad else None
                )
                if decrypted is None:
                    logger.error("Decryption failed")
                    return None
                payload = decrypted
            
            # 解压
            if packet.header.flags & WPKGFlags.COMPRESSED:
                try:
                    payload = zlib.decompress(payload)
                except zlib.error as e:
                    logger.error(f"Decompression failed: {e}")
                    return None
            
            self._stats['decoded'] += 1
            return payload
            
        except Exception as e:
            logger.error(f"WPKG decode error: {e}")
            self._stats['errors'] += 1
            return None
    
    def _next_seq(self) -> int:
        """获取下一个序列号"""
        seq = self._seq_counter
        self._seq_counter = (self._seq_counter + 1) & 0xFFFFFFFF
        return seq
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self._stats.copy()
    
    def reset_stats(self):
        """重置统计信息"""
        self._stats = {'encoded': 0, 'decoded': 0, 'errors': 0}


def encode_wpkg(payload: bytes,
                cipher: Optional[AESGCMCipher] = None,
                compress: bool = False,
                encrypt: bool = False,
                aad: Optional[bytes] = None) -> Optional[bytes]:
    """
    便捷编码函数
    
    Args:
        payload: 原始数据
        cipher: AES-GCM 加密器
        compress: 是否压缩
        encrypt: 是否加密
        aad: 附加认证数据
    
    Returns:
        编码后的数据包
    
    Example:
        >>> data = b"Hello, World!"
        >>> encoded = encode_wpkg(data, compress=True)
    """
    codec = WPKGCodec(cipher)
    return codec.encode(payload, compress, encrypt, aad)


def decode_wpkg(data: bytes,
                cipher: Optional[AESGCMCipher] = None,
                verify_aad: bool = True) -> Optional[bytes]:
    """
    便捷解码函数
    
    Args:
        data: 编码后的数据包
        cipher: AES-GCM 加密器
        verify_aad: 是否验证 AAD
    
    Returns:
        解码后的原始数据
    
    Example:
        >>> decoded = decode_wpkg(encoded_data)
    """
    codec = WPKGCodec(cipher)
    return codec.decode(data, verify_aad)


# 版本信息
__version__ = "1.0.0"
__all__ = [
    'WPKGFlags',
    'WPKGCompressAlgo', 
    'WPKGEncryptAlgo',
    'WPKGHeader',
    'WPKGPacket',
    'WPKGCodec',
    'encode_wpkg',
    'decode_wpkg'
]
