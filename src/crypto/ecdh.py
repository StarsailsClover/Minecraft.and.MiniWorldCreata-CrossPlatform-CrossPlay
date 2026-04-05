"""
ECDH 密钥交换

基于 P-256 (prime256v1) 曲线
"""

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class ECDHKeyExchange:
    """ECDH 密钥交换"""
    
    # 服务端公钥 (PEM格式)
    SERVER_PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEp4e24GoKyeS4utp998HyD9MJzsR1
h8R74SnoKmwW8nz8qZHaAynxU8P5dd29ORHGQEGUW4IFUVsg5I3XTdjRdQ==
-----END PUBLIC KEY-----"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.server_public_key = None
        self.shared_secret = None
    
    def generate_keypair(self) -> bool:
        """生成客户端密钥对"""
        try:
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.hazmat.backends import default_backend
            
            self.private_key = ec.generate_private_key(
                ec.SECP256R1(),  # P-256
                default_backend()
            )
            self.public_key = self.private_key.public_key()
            logger.info("ECDH keypair generated")
            return True
        except ImportError:
            logger.error("cryptography library not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to generate keypair: {e}")
            return False
    
    def load_server_public_key(self) -> bool:
        """加载服务端公钥"""
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            
            self.server_public_key = serialization.load_pem_public_key(
                self.SERVER_PUBLIC_KEY_PEM.encode('utf-8'),
                backend=default_backend()
            )
            logger.info("Server public key loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load server public key: {e}")
            return False
    
    def exchange(self) -> Optional[bytes]:
        """执行密钥交换"""
        if not self.private_key or not self.server_public_key:
            logger.error("Keys not initialized")
            return None
        
        try:
            self.shared_secret = self.private_key.exchange(
                ec.ECDH(),
                self.server_public_key
            )
            logger.info(f"Shared secret derived: {len(self.shared_secret)} bytes")
            return self.shared_secret
        except Exception as e:
            logger.error(f"Key exchange failed: {e}")
            return None
