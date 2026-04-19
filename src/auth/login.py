"""
迷你世界登录模块 - 生产环境级实现

基于 aiohttp 的异步登录实现
支持验证码、Token 刷新、多服务器

Copyright (c) 2026 MnMCP Contributors
SPDX-License-Identifier: MIT
"""

import asyncio
import hashlib
import json
import logging
import ssl
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from urllib.parse import urljoin

import aiohttp

from ..config import get_api_server, ServerConfig

logger = logging.getLogger(__name__)


@dataclass
class LoginResult:
    """
    登录结果
    
    Attributes:
        success: 是否成功
        uin: 用户UIN
        token: JWT Token
        session_key: 会话密钥
        error_code: 错误码
        error_message: 错误信息
    """
    success: bool
    uin: int = 0
    token: str = ""
    session_key: str = ""
    error_code: int = 0
    error_message: str = ""


@dataclass
class CaptchaInfo:
    """
    验证码信息
    
    Attributes:
        required: 是否需要验证码
        captcha_id: 验证码ID
        captcha_url: 验证码图片URL
    """
    required: bool
    captcha_id: str = ""
    captcha_url: str = ""


@dataclass
class TokenInfo:
    """
    Token 信息
    
    Attributes:
        access_token: 访问令牌
        refresh_token: 刷新令牌
        expires_in: 过期时间 (秒)
        token_type: 令牌类型
    """
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


class MiniWorldLogin:
    """
    迷你世界登录器
    
    生产环境级登录实现，支持：
    - 异步 HTTP 请求
    - 验证码处理
    - Token 刷新
    - 多服务器支持
    - 自动重试
    
    Example:
        >>> login = MiniWorldLogin()
        >>> result = await login.login_async("username", "password")
        >>> if result.success:
        ...     print(f"Login successful: {result.uin}")
        ... else:
        ...     print(f"Login failed: {result.error_message}")
    """
    
    # API 端点
    ENDPOINTS = {
        'login': '/v2/user/login',
        'verify': '/v2/user/verify',
        'get_token': '/v2/user/token',
        'refresh_token': '/v2/user/refresh',
        'heartbeat': '/v2/user/heartbeat',
        'logout': '/v2/user/logout',
    }
    
    def __init__(self, server: Optional[ServerConfig] = None):
        """
        初始化登录器
        
        Args:
            server: API 服务器配置
        """
        self.server = server or get_api_server()
        self.api_base = f"http://{self.server.host}:{self.server.port}"
        
        # HTTP 会话
        self._session: Optional[aiohttp.ClientSession] = None
        
        # 默认请求头
        self.headers = {
            'User-Agent': 'MiniWorld/1.53.1 (Windows; 10)',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Client-Version': '79105',
            'X-Platform': 'WIN',
        }
        
        # 回调
        self.on_captcha_required: Optional[Callable[[CaptchaInfo], str]] = None
        self.on_2fa_required: Optional[Callable[[str], str]] = None
        
        # 统计
        self._stats = {
            'login_attempts': 0,
            'login_success': 0,
            'captcha_required': 0,
            'token_refreshed': 0,
            'errors': 0
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建 HTTP 会话"""
        if self._session is None or self._session.closed:
            # SSL 配置
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                limit=10,
                limit_per_host=5
            )
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.headers
            )
        
        return self._session
    
    async def close(self):
        """关闭会话"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def login_async(
        self,
        username: str,
        password: str,
        captcha: str = "",
        captcha_id: str = ""
    ) -> LoginResult:
        """
        异步登录
        
        Args:
            username: 用户名
            password: 密码
            captcha: 验证码
            captcha_id: 验证码ID
            
        Returns:
            登录结果
        """
        self._stats['login_attempts'] += 1
        
        try:
            logger.info(f"Starting login for user: {username}")
            
            # 密码哈希 (MD5)
            password_hash = hashlib.md5(password.encode()).hexdigest()
            
            # 构建请求
            url = urljoin(self.api_base, self.ENDPOINTS['login'])
            payload = {
                "username": username,
                "password": password_hash,
                "platform": "WIN",
                "version": "79105",
                "device_id": f"MNW_{int(asyncio.get_event_loop().time())}",
            }
            
            # 添加验证码
            if captcha and captcha_id:
                payload['captcha'] = captcha
                payload['captcha_id'] = captcha_id
            
            session = await self._get_session()
            
            async with session.post(url, json=payload) as response:
                data = await response.json()
                
                if response.status == 200:
                    # 检查是否需要验证码
                    if data.get('need_captcha'):
                        self._stats['captcha_required'] += 1
                        
                        captcha_info = CaptchaInfo(
                            required=True,
                            captcha_id=data.get('captcha_id', ''),
                            captcha_url=data.get('captcha_url', '')
                        )
                        
                        if self.on_captcha_required:
                            # 等待验证码输入
                            captcha_code = await self._call_callback(
                                self.on_captcha_required,
                                captcha_info
                            )
                            
                            # 重试登录
                            return await self.login_async(
                                username,
                                password,
                                captcha=captcha_code,
                                captcha_id=captcha_info.captcha_id
                            )
                        else:
                            return LoginResult(
                                success=False,
                                error_code=1001,
                                error_message="Captcha required but no handler provided"
                            )
                    
                    # 检查登录结果
                    if data.get('success'):
                        self._stats['login_success'] += 1
                        
                        return LoginResult(
                            success=True,
                            uin=data.get('uin', 0),
                            token=data.get('token', ''),
                            session_key=data.get('session_key', '')
                        )
                    else:
                        return LoginResult(
                            success=False,
                            error_code=data.get('error_code', 0),
                            error_message=data.get('message', 'Login failed')
                        )
                else:
                    return LoginResult(
                        success=False,
                        error_code=response.status,
                        error_message=f"HTTP {response.status}"
                    )
                    
        except asyncio.TimeoutError:
            logger.error("Login timeout")
            return LoginResult(
                success=False,
                error_code=-1,
                error_message="Connection timeout"
            )
        except Exception as e:
            logger.error(f"Login error: {e}")
            self._stats['errors'] += 1
            return LoginResult(
                success=False,
                error_code=-2,
                error_message=str(e)
            )
    
    async def refresh_token_async(self, refresh_token: str) -> Optional[TokenInfo]:
        """
        异步刷新 Token
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            Token 信息或 None
        """
        try:
            url = urljoin(self.api_base, self.ENDPOINTS['refresh_token'])
            payload = {
                "refresh_token": refresh_token
            }
            
            session = await self._get_session()
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        self._stats['token_refreshed'] += 1
                        
                        return TokenInfo(
                            access_token=data.get('access_token', ''),
                            refresh_token=data.get('refresh_token', ''),
                            expires_in=data.get('expires_in', 3600)
                        )
                
                return None
                
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None
    
    async def verify_token_async(self, token: str) -> bool:
        """
        异步验证 Token
        
        Args:
            token: 访问令牌
            
        Returns:
            是否有效
        """
        try:
            url = urljoin(self.api_base, self.ENDPOINTS['verify'])
            headers = {
                **self.headers,
                'Authorization': f'Bearer {token}'
            }
            
            session = await self._get_session()
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('valid', False)
                
                return False
                
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return False
    
    async def logout_async(self, token: str) -> bool:
        """
        异步登出
        
        Args:
            token: 访问令牌
            
        Returns:
            是否成功
        """
        try:
            url = urljoin(self.api_base, self.ENDPOINTS['logout'])
            headers = {
                **self.headers,
                'Authorization': f'Bearer {token}'
            }
            
            session = await self._get_session()
            
            async with session.post(url, headers=headers) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    async def _call_callback(self, callback: Callable, *args) -> Any:
        """安全调用回调"""
        try:
            if asyncio.iscoroutinefunction(callback):
                return await callback(*args)
            else:
                return callback(*args)
        except Exception as e:
            logger.error(f"Callback error: {e}")
            return None
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self._stats.copy()


class TokenManager:
    """
    Token 管理器
    
    自动管理 Token 生命周期
    """
    
    def __init__(self, login: MiniWorldLogin):
        self.login = login
        self.token_info: Optional[TokenInfo] = None
        self._refresh_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self, token_info: TokenInfo):
        """启动 Token 管理"""
        self.token_info = token_info
        self._running = True
        
        # 启动自动刷新
        self._refresh_task = asyncio.create_task(self._auto_refresh())
    
    async def stop(self):
        """停止 Token 管理"""
        self._running = False
        
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
    
    async def _auto_refresh(self):
        """自动刷新 Token"""
        while self._running and self.token_info:
            try:
                # 在过期前 5 分钟刷新
                refresh_delay = max(0, self.token_info.expires_in - 300)
                await asyncio.sleep(refresh_delay)
                
                # 刷新 Token
                new_token = await self.login.refresh_token_async(
                    self.token_info.refresh_token
                )
                
                if new_token:
                    self.token_info = new_token
                    logger.info("Token refreshed successfully")
                else:
                    logger.error("Token refresh failed")
                    break
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto refresh error: {e}")
                await asyncio.sleep(60)  # 1分钟后重试
    
    def get_access_token(self) -> Optional[str]:
        """获取访问令牌"""
        if self.token_info:
            return self.token_info.access_token
        return None


# 便捷函数
async def login_miniworld(
    username: str,
    password: str,
    server: Optional[ServerConfig] = None
) -> Optional[LoginResult]:
    """
    便捷登录函数
    
    Args:
        username: 用户名
        password: 密码
        server: 服务器配置
        
    Returns:
        登录结果
    """
    login = MiniWorldLogin(server)
    try:
        result = await login.login_async(username, password)
        return result
    finally:
        await login.close()


# 版本信息
__version__ = "1.0.0"
__all__ = [
    'LoginResult',
    'CaptchaInfo',
    'TokenInfo',
    'MiniWorldLogin',
    'TokenManager',
    'login_miniworld'
]
