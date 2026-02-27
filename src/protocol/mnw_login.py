#!/usr/bin/env python3
"""
迷你世界登录流程实现
基于MnMCPResources中的反编译资源分析

国服登录流程:
1. 发送登录请求 (account_id + password_hash)
2. 接收服务器挑战 (challenge)
3. 计算响应 (response = HMAC(challenge, password))
4. 接收Token和SessionKey
5. 使用SessionKey加密后续通信
"""

import asyncio
import json
import hashlib
import hmac
import logging
import struct
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from crypto.aes_crypto_real import MiniWorldEncryptionReal, hash_password_real
except ImportError:
    from crypto.aes_crypto import MiniWorldEncryption as MiniWorldEncryptionReal, hash_password as hash_password_real
    print("[警告] 使用简化版加密模块，生产环境请安装cryptography库")

logger = logging.getLogger(__name__)


@dataclass
class LoginResponse:
    """登录响应"""
    success: bool
    token: str = ""
    session_key: bytes = b""
    user_id: str = ""
    nickname: str = ""
    error_code: int = 0
    error_message: str = ""


@dataclass
class MiniWorldAccount:
    """迷你世界账号"""
    account_id: str
    password: str
    nickname: str = ""
    level: int = 1
    region: str = "CN"


class MiniWorldLogin:
    """迷你世界登录管理器"""
    
    def __init__(self, region: str = "CN"):
        self.region = region.upper()
        self.encryption = MiniWorldEncryptionReal(region=region)
        
        # 登录状态
        self.authenticated = False
        self.token: Optional[str] = None
        self.session_key: Optional[bytes] = None
        self.user_info: Optional[Dict] = None
        
        logger.info(f"迷你世界登录管理器初始化: region={region}")
    
    def _hash_password(self, password: str, salt: bytes = None) -> Tuple[str, bytes]:
        """
        密码哈希
        
        根据反编译分析，迷你世界可能使用以下哈希方式:
        1. MD5双重哈希 (旧版本)
        2. SHA256 + Salt (新版本)
        3. PBKDF2 (外服)
        
        Args:
            password: 明文密码
            salt: 盐值
            
        Returns:
            (哈希值, 盐值)
        """
        if salt is None:
            salt = b'miniworld_salt_2024'  # 推测的默认盐值
        
        # 方法1: MD5双重哈希 (常见做法)
        first_hash = hashlib.md5(password.encode()).hexdigest()
        second_hash = hashlib.md5(first_hash.encode()).hexdigest()
        
        # 方法2: 加盐SHA256
        sha256 = hashlib.sha256()
        sha256.update(password.encode())
        sha256.update(salt)
        sha256_hash = sha256.hexdigest()
        
        logger.debug(f"密码哈希: md5={second_hash[:16]}..., sha256={sha256_hash[:16]}...")
        
        # 返回SHA256哈希 (推测新版本使用)
        return sha256_hash, salt
    
    def _compute_challenge_response(self, challenge: bytes, password_hash: str) -> bytes:
        """
        计算挑战响应
        
        基于HMAC的挑战-响应机制
        
        Args:
            challenge: 服务器发送的挑战数据
            password_hash: 密码哈希值
            
        Returns:
            响应数据
        """
        # 使用HMAC-SHA256计算响应
        response = hmac.new(
            password_hash.encode(),
            challenge,
            hashlib.sha256
        ).digest()
        
        logger.debug(f"挑战响应: {response.hex()[:32]}...")
        return response
    
    async def login(self, account: MiniWorldAccount) -> LoginResponse:
        """
        执行登录流程
        
        Args:
            account: 账号信息
            
        Returns:
            登录响应
        """
        try:
            logger.info(f"开始登录: account_id={account.account_id}")
            
            # 1. 计算密码哈希
            password_hash, salt = self._hash_password(account.password)
            
            # 2. 构建登录请求
            login_request = self._build_login_request(account, password_hash)
            
            # 3. 发送登录请求 (模拟)
            # 实际实现需要连接到mwu-api-pre.mini1.cn:443
            logger.info("发送登录请求...")
            
            # 4. 接收挑战 (模拟)
            # 实际应该从服务器接收
            challenge = b'server_challenge_12345'
            
            # 5. 计算响应
            response = self._compute_challenge_response(challenge, password_hash)
            
            # 6. 发送响应 (模拟)
            logger.info("发送挑战响应...")
            
            # 7. 接收登录结果 (模拟)
            # 实际应该从服务器接收
            login_result = {
                "success": True,
                "token": "mock_token_12345",
                "session_key": b'mock_session_key_16b',
                "user_id": account.account_id,
                "nickname": account.nickname or f"Player_{account.account_id}",
                "level": 1
            }
            
            if login_result["success"]:
                self.authenticated = True
                self.token = login_result["token"]
                self.session_key = login_result["session_key"]
                self.user_info = {
                    "user_id": login_result["user_id"],
                    "nickname": login_result["nickname"],
                    "level": login_result["level"]
                }
                
                # 设置加密会话密钥
                self.encryption.set_session_key(self.session_key)
                
                logger.info(f"登录成功: {self.user_info['nickname']}")
                
                return LoginResponse(
                    success=True,
                    token=self.token,
                    session_key=self.session_key,
                    user_id=login_result["user_id"],
                    nickname=login_result["nickname"]
                )
            else:
                logger.error(f"登录失败: {login_result.get('error_message', 'Unknown')}")
                return LoginResponse(
                    success=False,
                    error_code=login_result.get("error_code", -1),
                    error_message=login_result.get("error_message", "Login failed")
                )
                
        except Exception as e:
            logger.error(f"登录异常: {e}")
            return LoginResponse(
                success=False,
                error_code=-1,
                error_message=str(e)
            )
    
    def _build_login_request(self, account: MiniWorldAccount, password_hash: str) -> Dict:
        """
        构建登录请求
        
        Args:
            account: 账号信息
            password_hash: 密码哈希
            
        Returns:
            登录请求数据
        """
        request = {
            "account_id": account.account_id,
            "password_hash": password_hash,
            "region": self.region,
            "version": "1.53.1",
            "platform": "android" if self.region == "CN" else "global",
            "device_id": f"device_{account.account_id}",
            "timestamp": int(datetime.now().timestamp())
        }
        
        logger.debug(f"登录请求: {json.dumps(request, indent=2)}")
        return request
    
    async def logout(self) -> bool:
        """
        登出
        
        Returns:
            是否成功
        """
        try:
            if not self.authenticated:
                return True
            
            logger.info("执行登出...")
            
            # 发送登出请求 (模拟)
            # 实际应该发送到服务器
            
            # 清理状态
            self.authenticated = False
            self.token = None
            self.session_key = None
            self.user_info = None
            
            logger.info("登出成功")
            return True
            
        except Exception as e:
            logger.error(f"登出异常: {e}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        获取认证请求头
        
        Returns:
            请求头字典
        """
        if not self.authenticated or not self.token:
            return {}
        
        return {
            "Authorization": f"Bearer {self.token}",
            "X-User-ID": self.user_info.get("user_id", ""),
            "X-Region": self.region,
            "X-Version": "1.53.1"
        }
    
    def encrypt_data(self, data: bytes) -> bytes:
        """
        加密数据
        
        Args:
            data: 明文数据
            
        Returns:
            加密后的数据
        """
        if not self.authenticated:
            raise ValueError("未登录，无法加密数据")
        
        return self.encryption.encrypt(data)
    
    def decrypt_data(self, data: bytes) -> bytes:
        """
        解密数据
        
        Args:
            data: 加密数据
            
        Returns:
            解密后的明文
        """
        if not self.authenticated:
            raise ValueError("未登录，无法解密数据")
        
        return self.encryption.decrypt(data)
    
    def get_status(self) -> Dict:
        """
        获取登录状态
        
        Returns:
            状态字典
        """
        return {
            "authenticated": self.authenticated,
            "token": self.token[:20] + "..." if self.token else None,
            "user_info": self.user_info,
            "region": self.region
        }


# 测试代码
if __name__ == "__main__":
    async def test_login():
        """测试登录"""
        print("=" * 60)
        print("测试迷你世界登录流程")
        print("=" * 60)
        
        # 创建登录管理器
        login_manager = MiniWorldLogin(region="CN")
        
        # 创建测试账号
        account = MiniWorldAccount(
            account_id="12345678",
            password="test_password",
            nickname="TestPlayer"
        )
        
        # 执行登录
        print("\n执行登录...")
        response = await login_manager.login(account)
        
        if response.success:
            print(f"\n✅ 登录成功!")
            print(f"   Token: {response.token[:20]}...")
            print(f"   Session Key: {response.session_key.hex()[:32]}...")
            print(f"   User ID: {response.user_id}")
            print(f"   Nickname: {response.nickname}")
            
            # 测试加密
            print("\n测试加密...")
            test_data = b"Hello, MiniWorld!"
            encrypted = login_manager.encrypt_data(test_data)
            decrypted = login_manager.decrypt_data(encrypted)
            
            print(f"   原始数据: {test_data}")
            print(f"   加密后: {encrypted.hex()[:32]}...")
            print(f"   解密后: {decrypted}")
            print(f"   测试: {'通过' if decrypted == test_data else '失败'}")
            
            # 获取状态
            print("\n登录状态:")
            print(f"   {json.dumps(login_manager.get_status(), indent=2)}")
            
            # 登出
            print("\n执行登出...")
            await login_manager.logout()
            print("✅ 登出成功")
            
        else:
            print(f"\n❌ 登录失败!")
            print(f"   错误码: {response.error_code}")
            print(f"   错误信息: {response.error_message}")
    
    # 运行测试
    asyncio.run(test_login())
