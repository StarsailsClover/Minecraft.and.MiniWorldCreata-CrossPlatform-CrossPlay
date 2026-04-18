"""
WPKG 编解码器测试 - 独立测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 直接导入，避免 __init__.py 的循环导入
from crypto.aesgcm import AESGCMCipher

# 手动定义 WPKG 相关类
import struct
import zlib
import logging
from dataclasses import dataclass
from typing import Optional
from enum import IntEnum

logger = logging.getLogger(__name__)

class WPKGFlags(IntEnum):
    NONE = 0x00
    ENCRYPTED = 0x01
    COMPRESSED = 0x02
    HAS_AAD = 0x04

class WPKGCompressAlgo(IntEnum):
    NONE = 0x00
    ZLIB = 0x01
    LZ4 = 0x02

class WPKGEncryptAlgo(IntEnum):
    NONE = 0x00
    AES_GCM = 0x01
    HYBRID_ECDH = 0x02

@dataclass
class WPKGHeader:
    MAGIC = 0xABCD
    VERSION = 0x01
    HEADER_LEN = 16
    
    flags: int = 0
    compress_algo: int = WPKGCompressAlgo.NONE
    encrypt_algo: int = WPKGEncryptAlgo.NONE
    payload_len: int = 0
    seq_num: int = 0
    
    def encode(self) -> bytes:
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
        if len(data) < cls.HEADER_LEN:
            return None
        try:
            magic, version, flags, compress_algo, header_len, payload_len, seq_num = \
                struct.unpack('>HBBHHII', data[:cls.HEADER_LEN])
            if magic != cls.MAGIC:
                return None
            return cls(
                flags=flags,
                compress_algo=compress_algo,
                encrypt_algo=WPKGEncryptAlgo.NONE,
                payload_len=payload_len,
                seq_num=seq_num
            )
        except:
            return None

@dataclass
class WPKGPacket:
    header: 'WPKGHeader'
    payload: bytes
    aad: Optional[bytes] = None
    tag: Optional[bytes] = None
    
    def encode(self) -> bytes:
        header_bytes = self.header.encode()
        if self.aad:
            aad_len = len(self.aad)
            header_bytes += struct.pack('>I', aad_len) + self.aad
        payload = self.payload
        if self.tag:
            payload += self.tag
        return header_bytes + payload

class WPKGCodec:
    def __init__(self, cipher: Optional[AESGCMCipher] = None):
        self.cipher = cipher
        self.seq_counter = 0
    
    def encode(self, payload: bytes, compress: bool = False, encrypt: bool = False, aad: Optional[bytes] = None) -> Optional[bytes]:
        try:
            flags = 0
            compress_algo = WPKGCompressAlgo.NONE
            encrypt_algo = WPKGEncryptAlgo.NONE
            
            if compress:
                payload = zlib.compress(payload)
                flags |= WPKGFlags.COMPRESSED
                compress_algo = WPKGCompressAlgo.ZLIB
            
            tag = None
            if encrypt and self.cipher:
                encrypted = self.cipher.encrypt(payload, aad)
                if encrypted is None:
                    return None
                tag = encrypted[-16:]
                payload = encrypted[:-16]
                flags |= WPKGFlags.ENCRYPTED
                encrypt_algo = WPKGEncryptAlgo.AES_GCM
            
            if aad:
                flags |= WPKGFlags.HAS_AAD
            
            header = WPKGHeader(
                flags=flags,
                compress_algo=compress_algo,
                encrypt_algo=encrypt_algo,
                payload_len=len(payload) + (len(tag) if tag else 0),
                seq_num=self._next_seq()
            )
            
            packet = WPKGPacket(
                header=header,
                payload=payload,
                aad=aad,
                tag=tag
            )
            return packet.encode()
        except Exception as e:
            logger.error(f"WPKG encode error: {e}")
            return None
    
    def decode(self, data: bytes, verify_aad: bool = True) -> Optional[bytes]:
        try:
            header = WPKGHeader.decode(data)
            if not header:
                return None
            
            offset = WPKGHeader.HEADER_LEN
            aad = None
            
            if header.flags & WPKGFlags.HAS_AAD:
                if len(data) < offset + 4:
                    return None
                aad_len = struct.unpack('>I', data[offset:offset+4])[0]
                offset += 4
                aad = data[offset:offset+aad_len]
                offset += aad_len
            
            payload_end = offset + header.payload_len
            payload = data[offset:payload_end]
            
            tag = None
            if header.flags & WPKGFlags.ENCRYPTED:
                if len(payload) >= 16:
                    tag = payload[-16:]
                    payload = payload[:-16]
            
            if header.flags & WPKGFlags.ENCRYPTED:
                if not self.cipher:
                    return None
                ciphertext_with_tag = payload
                if tag:
                    ciphertext_with_tag += tag
                decrypted = self.cipher.decrypt(ciphertext_with_tag, aad if verify_aad else None)
                if decrypted is None:
                    return None
                payload = decrypted
            
            if header.flags & WPKGFlags.COMPRESSED:
                try:
                    payload = zlib.decompress(payload)
                except:
                    return None
            
            return payload
        except Exception as e:
            logger.error(f"WPKG decode error: {e}")
            return None
    
    def _next_seq(self) -> int:
        seq = self.seq_counter
        self.seq_counter = (self.seq_counter + 1) & 0xFFFFFFFF
        return seq


def test_wpkg_header():
    print("=" * 50)
    print("测试 WPKGHeader 编解码")
    print("=" * 50)
    
    header = WPKGHeader(
        flags=WPKGFlags.ENCRYPTED | WPKGFlags.COMPRESSED,
        compress_algo=WPKGCompressAlgo.ZLIB,
        encrypt_algo=WPKGEncryptAlgo.AES_GCM,
        payload_len=100,
        seq_num=1
    )
    
    encoded = header.encode()
    print(f"编码后的包头: {encoded.hex()}")
    print(f"包头长度: {len(encoded)} bytes")
    
    decoded = WPKGHeader.decode(encoded)
    if decoded:
        print(f"解码成功!")
        print(f"  flags: {decoded.flags}")
        print(f"  compress_algo: {decoded.compress_algo}")
        print(f"  payload_len: {decoded.payload_len}")
        print(f"  seq_num: {decoded.seq_num}")
        return True
    else:
        print("解码失败!")
        return False


def test_wpkg_codec_without_encryption():
    print("\n" + "=" * 50)
    print("测试 WPKG 编解码 (无加密)")
    print("=" * 50)
    
    codec = WPKGCodec()
    test_data = b"Hello, MnMCP! This is a test message."
    print(f"原始数据: {test_data}")
    
    encoded = codec.encode(test_data, compress=False, encrypt=False)
    if not encoded:
        print("编码失败!")
        return False
    
    print(f"编码后长度: {len(encoded)} bytes")
    
    decoded = codec.decode(encoded)
    if not decoded:
        print("解码失败!")
        return False
    
    print(f"解码后数据: {decoded}")
    if decoded == test_data:
        print("✓ 数据匹配!")
        return True
    else:
        print("✗ 数据不匹配!")
        return False


def test_wpkg_codec_with_compression():
    print("\n" + "=" * 50)
    print("测试 WPKG 编解码 (带压缩)")
    print("=" * 50)
    
    codec = WPKGCodec()
    test_data = b"Hello, MnMCP! " * 100
    original_len = len(test_data)
    print(f"原始数据长度: {original_len} bytes")
    
    encoded = codec.encode(test_data, compress=True, encrypt=False)
    if not encoded:
        print("编码失败!")
        return False
    
    print(f"编码后长度: {len(encoded)} bytes")
    print(f"压缩率: {(1 - len(encoded)/original_len)*100:.1f}%")
    
    decoded = codec.decode(encoded)
    if not decoded:
        print("解码失败!")
        return False
    
    if decoded == test_data:
        print("✓ 数据匹配!")
        return True
    else:
        print("✗ 数据不匹配!")
        return False


def test_wpkg_codec_with_encryption():
    print("\n" + "=" * 50)
    print("测试 WPKG 编解码 (带加密)")
    print("=" * 50)
    
    key = b'\x00' * 16
    nonce_base = b'\x01' * 12
    cipher = AESGCMCipher(key, nonce_base)
    codec = WPKGCodec(cipher)
    
    test_data = b"Secret message for MnMCP!"
    print(f"原始数据: {test_data}")
    
    encoded = codec.encode(test_data, compress=False, encrypt=True)
    if not encoded:
        print("编码失败!")
        return False
    
    print(f"编码后长度: {len(encoded)} bytes")
    
    decoded = codec.decode(encoded)
    if not decoded:
        print("解码失败!")
        return False
    
    print(f"解码后数据: {decoded}")
    if decoded == test_data:
        print("✓ 数据匹配!")
        return True
    else:
        print("✗ 数据不匹配!")
        return False


def main():
    print("\n" + "=" * 60)
    print("WPKG 编解码器测试套件")
    print("=" * 60)
    
    tests = [
        ("WPKGHeader 编解码", test_wpkg_header),
        ("WPKG 无加密", test_wpkg_codec_without_encryption),
        ("WPKG 带压缩", test_wpkg_codec_with_compression),
        ("WPKG 带加密", test_wpkg_codec_with_encryption),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✓ {name} - 通过")
            else:
                failed += 1
                print(f"\n✗ {name} - 失败")
        except Exception as e:
            failed += 1
            print(f"\n✗ {name} - 异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{len(tests)} 通过, {failed}/{len(tests)} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
