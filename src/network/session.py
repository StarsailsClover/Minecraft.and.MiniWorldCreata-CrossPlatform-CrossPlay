"""
会话管理

管理 iLink 会话生命周期
"""

import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

from ..crypto import ECDHKeyExchange, HKDFKeyDerivation, AESGCMCipher
from ..protocol.ilink import ILinkSession

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """会话信息"""
    session_id: str
    uin: int
    aes_key: bytes
    nonce_base: bytes
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    cipher: Optional[AESGCMCipher] = None
    
    def __post_init__(self):
        self.cipher = AESGCMCipher(self.aes_key, self.nonce_base)


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.ecdh = ECDHKeyExchange()
        self.hkdf = HKDFKeyDerivation()
    
    def establish_session(self, uin: int) -> Optional[Session]:
        """建立新会话"""
        logger.info(f"Establishing session for UIN: {uin}")
        
        # Step 1: ECDH 密钥交换
        shared_secret = self.ecdh.complete_exchange()
        if not shared_secret:
            logger.error("ECDH key exchange failed")
            return None
        
        # Step 2: HKDF 密钥派生
        key_material = self.hkdf.derive(shared_secret)
        if not key_material:
            logger.error("HKDF key derivation failed")
            return None
        
        keys = self.hkdf.extract_keys(key_material)
        
        # Step 3: 创建会话
        session_id = f"session_{uin}_{int(time.time())}"
        session = Session(
            session_id=session_id,
            uin=uin,
            aes_key=keys['aes_key'],
            nonce_base=keys['nonce_base']
        )
        
        self.sessions[session_id] = session
        logger.info(f"Session established: {session_id}")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        session = self.sessions.get(session_id)
        if session:
            session.last_activity = time.time()
        return session
    
    def encrypt_for_session(self, session_id: str, plaintext: bytes) -> Optional[bytes]:
        """为会话加密数据"""
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        return session.cipher.encrypt(plaintext)
    
    def decrypt_for_session(self, session_id: str, ciphertext: bytes) -> Optional[bytes]:
        """为会话解密数据"""
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        return session.cipher.decrypt(ciphertext)
    
    def close_session(self, session_id: str):
        """关闭会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session closed: {session_id}")
