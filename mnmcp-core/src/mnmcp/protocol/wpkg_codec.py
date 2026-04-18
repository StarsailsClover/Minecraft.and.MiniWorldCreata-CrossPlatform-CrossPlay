"""
WPKG 编解码器

基于逆向工程分析实现:
- 来源: GRAND_MASTER_DECREE_FINAL.md, udp_package_report.md
- 协议: ilink-network v2.3.2.f3 (基于 Mars/mmtls)
- 加密: ECDH + HKDF + AES-128-GCM
- 压缩: ZLIB / LZ4 / None

包结构:
    offset  len  field
    0       2    Magic/Version
    2       2    CmdID
    4       4    SeqNo
    8       4    BodyLen
    12      1    EncryptAlgo (0=HybridEcdh, 1=AesGcm)
    13      1    CompressAlgo (0=none, 1/4=zlib, 2=lz4)
    14      1    CompressVersion
    15      1    HeaderEnd/Flags
    16      12   Nonce (GCM IV, 96-bit)
    28      N    Ciphertext
    28+N    16   GCM Tag
"""

import struct
import zlib
import logging
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import IntEnum

logger = logging.getLogger(__name__)


class EncryptAlgo(IntEnum):
    """加密算法"""
    HYBRID_ECDH = 0    # 一次性 Hybrid-ECDH 握手加密
    AES_GCM = 1        # AES-128-GCM


class CompressAlgo(IntEnum):
    """压缩算法"""
    NONE = 0
    ZLIB = 1
    LZ4 = 2
    ZLIB_ALT = 4       # 替代 ZLIB 标识


@dataclass
class WPKGHeader:
    """WPKG 包头"""
    magic: int = 0x0001          # 2 bytes: Magic/Version
    cmd_id: int = 0              # 2 bytes: 命令 ID
    seq_no: int = 0              # 4 bytes: 序列号
    body_len: int = 0            # 4 bytes:  body 长度
    encrypt_algo: EncryptAlgo = EncryptAlgo.AES_GCM   # 1 byte
    compress_algo: CompressAlgo = CompressAlgo.NONE   # 1 byte
    compress_version: int = 0    # 1 byte
    flags: int = 0               # 1 byte: HeaderEnd/Flags
    
    HEADER_SIZE = 16
    
    def to_bytes(self) -> bytes:
        """编码包头"""
        return struct.pack('<HHII BBBB',
            self.magic,
            self.cmd_id,
            self.seq_no,
            self.body_len,
            self.encrypt_algo,
            self.compress_algo,
            self.compress_version,
            self.flags
        )
    
    @classmethod
    def from_bytes(cls, data: bytes) -> Optional['WPKGHeader']:
        """解码包头"""
        if len(data) < cls.HEADER_SIZE:
            return None
        
        try:
            magic, cmd_id, seq_no, body_len, encrypt_algo, compress_algo, \
                compress_version, flags = struct.unpack('<HHII BBBB', data[:cls.HEADER_SIZE])
            
            return cls(
                magic=magic,
                cmd_id=cmd_id,
                seq_no=seq_no,
                body_len=body_len,
                encrypt_algo=EncryptAlgo(encrypt_algo),
                compress_algo=CompressAlgo(compress_algo),
                compress_version=compress_version,
                flags=flags
            )
        except Exception as e:
            logger.error(f"Failed to parse WPKG header: {e}")
            return None


@dataclass
class WPKGPacket:
    """WPKG 数据包"""
    header: WPKGHeader
    nonce: bytes                 # 12 bytes for GCM
    ciphertext: bytes
    tag: bytes                   # 16 bytes GCM tag
    
    def to_bytes(self) -> bytes:
        """编码完整数据包"""
        return self.header.to_bytes() + self.nonce + self.ciphertext + self.tag
    
    @classmethod
    def from_bytes(cls, data: bytes) -> Optional['WPKGPacket']:
        """解码完整数据包"""
        if len(data) < WPKGHeader.HEADER_SIZE + 12 + 16:
            return None
        
        try:
            header = WPKGHeader.from_bytes(data)
            if not header:
                return None
            
            offset = WPKGHeader.HEADER_SIZE
            nonce = data[offset:offset+12]
            offset += 12
            
            # ciphertext + tag
            ciphertext_len = header.body_len - 16  # 减去 tag 长度
            ciphertext = data[offset:offset+ciphertext_len]
            offset += ciphertext_len
            
            tag = data[offset:offset+16]
            
            return cls(
                header=header,
                nonce=nonce,
                ciphertext=ciphertext,
                tag=tag
            )
        except Exception as e:
            logger.error(f"Failed to parse WPKG packet: {e}")
            return None


class WPKGCodec:
    """WPKG 编解码器"""
    
    def __init__(self):
        self._seq_counter = 0
    
    def _get_next_seq(self) -> int:
        """获取下一个序列号"""
        self._seq_counter += 1
        return self._seq_counter
    
    def compress(self, data: bytes, algo: CompressAlgo) -> Tuple[bytes, CompressAlgo]:
        """
        压缩数据
        
        Returns:
            (compressed_data, actual_algo)
        """
        if algo == CompressAlgo.NONE:
            return data, CompressAlgo.NONE
        
        elif algo in (CompressAlgo.ZLIB, CompressAlgo.ZLIB_ALT):
            try:
                compressed = zlib.compress(data)
                # 只有压缩后更小才使用压缩
                if len(compressed) < len(data):
                    return compressed, CompressAlgo.ZLIB
                return data, CompressAlgo.NONE
            except Exception as e:
                logger.warning(f"ZLIB compression failed: {e}")
                return data, CompressAlgo.NONE
        
        elif algo == CompressAlgo.LZ4:
            # TODO: 实现 LZ4 压缩
            logger.warning("LZ4 compression not implemented, using none")
            return data, CompressAlgo.NONE
        
        return data, CompressAlgo.NONE
    
    def decompress(self, data: bytes, algo: CompressAlgo) -> Optional[bytes]:
        """解压数据"""
        if algo == CompressAlgo.NONE:
            return data
        
        elif algo in (CompressAlgo.ZLIB, CompressAlgo.ZLIB_ALT):
            try:
                return zlib.decompress(data)
            except Exception as e:
                logger.error(f"ZLIB decompression failed: {e}")
                return None
        
        elif algo == CompressAlgo.LZ4:
            # TODO: 实现 LZ4 解压
            logger.error("LZ4 decompression not implemented")
            return None
        
        return data
    
    def encode_packet(
        self,
        cmd_id: int,
        plaintext: bytes,
        encrypt_fn: Optional[callable] = None,
        compress_algo: CompressAlgo = CompressAlgo.ZLIB,
        encrypt_algo: EncryptAlgo = EncryptAlgo.AES_GCM
    ) -> Optional[WPKGPacket]:
        """
        编码数据包
        
        Args:
            cmd_id: 命令 ID
            plaintext: 明文数据
            encrypt_fn: 加密函数 (plaintext, nonce) -> (ciphertext, tag)
            compress_algo: 压缩算法
            encrypt_algo: 加密算法
        
        Returns:
            WPKGPacket 或 None
        """
        try:
            # 1. 压缩
            compressed, actual_compress = self.compress(plaintext, compress_algo)
            
            # 2. 加密
            if encrypt_algo == EncryptAlgo.AES_GCM and encrypt_fn:
                # 生成 nonce (12 bytes)
                import os
                nonce = os.urandom(12)
                
                # 加密
                ciphertext, tag = encrypt_fn(compressed, nonce)
                if ciphertext is None:
                    return None
            else:
                # 不加密
                nonce = b'\x00' * 12
                ciphertext = compressed
                tag = b'\x00' * 16
            
            # 3. 构建包头
            body_len = len(ciphertext) + len(tag)
            header = WPKGHeader(
                magic=0x0001,
                cmd_id=cmd_id,
                seq_no=self._get_next_seq(),
                body_len=body_len,
                encrypt_algo=encrypt_algo,
                compress_algo=actual_compress,
                compress_version=0,
                flags=0
            )
            
            return WPKGPacket(
                header=header,
                nonce=nonce,
                ciphertext=ciphertext,
                tag=tag
            )
            
        except Exception as e:
            logger.error(f"Failed to encode WPKG packet: {e}")
            return None
    
    def decode_packet(
        self,
        packet: WPKGPacket,
        decrypt_fn: Optional[callable] = None
    ) -> Optional[bytes]:
        """
        解码数据包
        
        Args:
            packet: WPKG 数据包
            decrypt_fn: 解密函数 (ciphertext, nonce, tag) -> plaintext
        
        Returns:
            明文数据或 None
        """
        try:
            # 1. 解密
            if packet.header.encrypt_algo == EncryptAlgo.AES_GCM and decrypt_fn:
                compressed = decrypt_fn(packet.ciphertext, packet.nonce, packet.tag)
                if compressed is None:
                    return None
            else:
                compressed = packet.ciphertext
            
            # 2. 解压
            plaintext = self.decompress(compressed, packet.header.compress_algo)
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Failed to decode WPKG packet: {e}")
            return None


# 便捷函数
def encode_wpkg(
    cmd_id: int,
    plaintext: bytes,
    encrypt_fn: Optional[callable] = None,
    compress: bool = True
) -> Optional[bytes]:
    """
    便捷编码函数
    
    Args:
        cmd_id: 命令 ID
        plaintext: 明文数据
        encrypt_fn: 加密函数
        compress: 是否启用压缩
    
    Returns:
        编码后的字节数据或 None
    """
    codec = WPKGCodec()
    compress_algo = CompressAlgo.ZLIB if compress else CompressAlgo.NONE
    
    packet = codec.encode_packet(
        cmd_id=cmd_id,
        plaintext=plaintext,
        encrypt_fn=encrypt_fn,
        compress_algo=compress_algo
    )
    
    if packet:
        return packet.to_bytes()
    return None


def decode_wpkg(
    data: bytes,
    decrypt_fn: Optional[callable] = None
) -> Optional[Tuple[int, bytes]]:
    """
    便捷解码函数
    
    Args:
        data: 编码后的字节数据
        decrypt_fn: 解密函数
    
    Returns:
        (cmd_id, plaintext) 或 None
    """
    packet = WPKGPacket.from_bytes(data)
    if not packet:
        return None
    
    codec = WPKGCodec()
    plaintext = codec.decode_packet(packet, decrypt_fn)
    
    if plaintext is not None:
        return (packet.header.cmd_id, plaintext)
    return None
