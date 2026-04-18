"""
iLink/mmtls 协议实现

基于腾讯 iLink Network v2.3.2.f3 逆向分析
"""

import struct
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

try:
    from .wpkg_codec import WPKGCodec, WPKGPacket, WPKGHeader
    from ..crypto.ecdh import ECDHKeyExchange
    from ..crypto.hkdf import HKDFKeyDerivation
    from ..crypto.aesgcm import AESGCMCipher
except ImportError:
    # 直接导入，用于测试
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from protocol.wpkg_codec import WPKGCodec, WPKGPacket, WPKGHeader
    from crypto.ecdh import ECDHKeyExchange
    from crypto.hkdf import HKDFKeyDerivation
    from crypto.aesgcm import AESGCMCipher

logger = logging.getLogger(__name__)


@dataclass
class ILinkSession:
    """iLink 会话管理"""
    
    # 服务端公钥 (PEM格式)
    SERVER_PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEp4e24GoKyeS4utp998HyD9MJzsR1
h8R74SnoKmwW8nz8qZHaAynxU8P5dd29ORHGQEGUW4IFUVsg5I3XTdjRdQ==
-----END PUBLIC KEY-----"""
    
    def __init__(self):
        self.session_key: Optional[bytes] = None
        self.nonce_base: Optional[bytes] = None
        self.seq_counter: int = 0
        self.ecdh: Optional[ECDHKeyExchange] = None
        self.hkdf: Optional[HKDFKeyDerivation] = None
        self.cipher: Optional[AESGCMCipher] = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """初始化会话组件"""
        try:
            self.ecdh = ECDHKeyExchange()
            self.hkdf = HKDFKeyDerivation()
            
            # 生成客户端密钥对
            if not self.ecdh.generate_keypair():
                logger.error("Failed to generate ECDH keypair")
                return False
            
            # 加载服务端公钥
            if not self.ecdh.load_server_public_key():
                logger.error("Failed to load server public key")
                return False
            
            self._initialized = True
            logger.info("iLink session initialized")
            return True
            
        except Exception as e:
            logger.error(f"Session initialization failed: {e}")
            return False
    
    def perform_key_exchange(self) -> bool:
        """执行 ECDH 密钥交换并派生会话密钥"""
        if not self._initialized:
            if not self.initialize():
                return False
        
        try:
            # 执行 ECDH 密钥交换
            shared_secret = self.ecdh.complete_exchange()
            if not shared_secret:
                logger.error("ECDH key exchange failed")
                return False
            
            # 使用 HKDF 派生密钥
            key_material = self.hkdf.derive(shared_secret, length=48)
            if not key_material:
                logger.error("HKDF key derivation failed")
                return False
            
            # 提取密钥组件
            keys = self.hkdf.extract_keys(key_material)
            self.session_key = keys['aes_key']
            self.nonce_base = keys['nonce_base']
            
            # 创建 AES-GCM 加密器
            self.cipher = AESGCMCipher(self.session_key, self.nonce_base)
            
            logger.info("ECDH key exchange completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Key exchange failed: {e}")
            return False
    
    def get_cipher(self) -> Optional[AESGCMCipher]:
        """获取加密器"""
        return self.cipher


class ILinkCodec:
    """iLink 编解码器 - 基于 WPKG"""
    
    def __init__(self, session: ILinkSession):
        self.session = session
        self.wpkg_codec: Optional[WPKGCodec] = None
        self._update_codec()
    
    def _update_codec(self):
        """更新 WPKG 编解码器"""
        cipher = self.session.get_cipher()
        self.wpkg_codec = WPKGCodec(cipher)
    
    def encode(self, data: bytes, compress: bool = False, encrypt: bool = True) -> bytes:
        """
        编码数据包
        
        Args:
            data: 原始数据
            compress: 是否压缩
            encrypt: 是否加密
        
        Returns:
            编码后的数据包
        """
        if encrypt and not self.session.cipher:
            logger.warning("Encryption requested but cipher not available")
            encrypt = False
        
        result = self.wpkg_codec.encode(data, compress=compress, encrypt=encrypt)
        if result is None:
            logger.error("WPKG encoding failed")
            return data
        return result
    
    def decode(self, data: bytes) -> Optional[bytes]:
        """
        解码数据包
        
        Args:
            data: 编码后的数据包
        
        Returns:
            解码后的原始数据
        """
        result = self.wpkg_codec.decode(data)
        if result is None:
            logger.error("WPKG decoding failed")
        return result
    
    def encode_packet(self, payload: bytes, msg_type: int = 0) -> bytes:
        """
        编码完整协议包
        
        格式: WPKG 包体 + 业务数据
        """
        # 添加消息类型前缀 (2 bytes)
        data_with_type = struct.pack('>H', msg_type) + payload
        return self.encode(data_with_type)
    
    def decode_packet(self, data: bytes) -> Optional[tuple]:
        """
        解码完整协议包
        
        Returns:
            (msg_type, payload) 或 None
        """
        decoded = self.decode(data)
        if not decoded or len(decoded) < 2:
            return None
        
        msg_type = struct.unpack('>H', decoded[:2])[0]
        payload = decoded[2:]
        return (msg_type, payload)
