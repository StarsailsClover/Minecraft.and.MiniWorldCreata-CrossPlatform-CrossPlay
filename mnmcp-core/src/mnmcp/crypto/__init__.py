"""
MnMCP 加密层
v1.0.0_26w13a

强制依赖 cryptography — 不提供 XOR 降级。

合并自旧项目:
  crypto/aes_crypto.py
  crypto/aes_crypto_real.py
  crypto/password_hasher.py
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from typing import Optional, Tuple

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
#  AES 加密
# ═══════════════════════════════════════════════════════════

class AESCipher:
    """
    生产级 AES 加密器

    国服: AES-128-CBC  (PKCS7, IV 前置)
    外服: AES-256-GCM  (12-byte nonce, 16-byte tag 后置)
    """

    def __init__(self, key: bytes, *, iv: bytes | None = None):
        key_bits = len(key) * 8
        if key_bits not in (128, 192, 256):
            raise ValueError(f"密钥长度必须为 128/192/256 位, 当前 {key_bits} 位")
        self.key = key
        self.iv = iv or os.urandom(16)
        self._backend = default_backend()
        logger.debug("AES 初始化: key=%d bits", key_bits)

    # ── CBC ──

    def encrypt_cbc(self, plaintext: bytes) -> bytes:
        """AES-CBC 加密 → IV(16) + ciphertext"""
        padder = sym_padding.PKCS7(128).padder()
        padded = padder.update(plaintext) + padder.finalize()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), self._backend)
        ct = cipher.encryptor().update(padded) + cipher.encryptor().finalize()
        # 重新创建 encryptor 以确保正确
        enc = cipher.encryptor()
        ct = enc.update(padded) + enc.finalize()
        return self.iv + ct

    def decrypt_cbc(self, data: bytes) -> bytes:
        """AES-CBC 解密 (data = IV(16) + ciphertext)"""
        iv, ct = data[:16], data[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), self._backend)
        dec = cipher.decryptor()
        padded = dec.update(ct) + dec.finalize()
        unpadder = sym_padding.PKCS7(128).unpadder()
        return unpadder.update(padded) + unpadder.finalize()

    # ── GCM ──

    def encrypt_gcm(self, plaintext: bytes, aad: bytes | None = None) -> bytes:
        """AES-GCM 加密 → nonce(12) + ciphertext + tag(16)"""
        nonce = os.urandom(12)
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(nonce), self._backend)
        enc = cipher.encryptor()
        if aad:
            enc.authenticate_additional_data(aad)
        ct = enc.update(plaintext) + enc.finalize()
        return nonce + ct + enc.tag

    def decrypt_gcm(self, data: bytes, aad: bytes | None = None) -> bytes:
        """AES-GCM 解密 (data = nonce(12) + ciphertext + tag(16))"""
        nonce, ct, tag = data[:12], data[12:-16], data[-16:]
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(nonce, tag), self._backend)
        dec = cipher.decryptor()
        if aad:
            dec.authenticate_additional_data(aad)
        return dec.update(ct) + dec.finalize()


# ═══════════════════════════════════════════════════════════
#  密码哈希
# ═══════════════════════════════════════════════════════════

class PasswordHasher:
    """迷你世界密码哈希 (国服: 双重 MD5)"""

    @staticmethod
    def hash_cn(password: str, salt: str | None = None) -> str:
        """国服: MD5(MD5(password) + salt)"""
        h1 = hashlib.md5(password.encode("utf-8")).hexdigest()
        h2_input = (h1 + salt) if salt else h1
        return hashlib.md5(h2_input.encode("utf-8")).hexdigest()

    @staticmethod
    def hash_simple(password: str) -> str:
        return hashlib.md5(password.encode("utf-8")).hexdigest()

    @staticmethod
    def verify(password: str, hashed: str, salt: str | None = None) -> bool:
        return PasswordHasher.hash_cn(password, salt) == hashed


# ═══════════════════════════════════════════════════════════
#  认证令牌
# ═══════════════════════════════════════════════════════════

class TokenHasher:
    """auth 参数签名 (推测: MD5(uin + ts + secret))"""

    @staticmethod
    def generate_auth(uin: str, timestamp: int, secret: str = "") -> str:
        raw = f"{uin}{timestamp}{secret}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def hmac_challenge(challenge: bytes, key: bytes) -> bytes:
        """HMAC-SHA256 挑战响应"""
        return hmac.new(key, challenge, hashlib.sha256).digest()


# ═══════════════════════════════════════════════════════════
#  会话加密管理器
# ═══════════════════════════════════════════════════════════

class SessionCrypto:
    """
    管理一个连接的加密生命周期

    1. 握手阶段: 明文
    2. 登录成功后: 使用 session_key 初始化 AES
    3. 后续通信: 加密
    """

    def __init__(self, region: str = "CN"):
        self.region = region.upper()
        self._cipher: Optional[AESCipher] = None
        self._session_key: Optional[bytes] = None
        self.encrypted = False

    def activate(self, session_key: bytes):
        """用服务器下发的 session_key 激活加密"""
        self._session_key = session_key
        self._cipher = AESCipher(session_key)
        self.encrypted = True
        logger.info("会话加密已激活: %s", "CBC" if self.region == "CN" else "GCM")

    def encrypt(self, data: bytes) -> bytes:
        if not self.encrypted or not self._cipher:
            return data
        if self.region == "CN":
            return self._cipher.encrypt_cbc(data)
        return self._cipher.encrypt_gcm(data)

    def decrypt(self, data: bytes) -> bytes:
        if not self.encrypted or not self._cipher:
            return data
        if self.region == "CN":
            return self._cipher.decrypt_cbc(data)
        return self._cipher.decrypt_gcm(data)
