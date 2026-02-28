#!/usr/bin/env python3
"""
密码哈希模块 - v0.2.2_26w09a_Phase 1
处理迷你世界登录密码的哈希计算

国服密码算法：基于MD5的双重哈希
"""

import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PasswordHasher:
    """
    密码哈希器
    
    实现迷你世界国服密码加密算法
    基于逆向分析推测的双重MD5哈希
    """
    
    @staticmethod
    def hash_password_cn(password: str, salt: Optional[str] = None) -> str:
        """
        国服密码哈希（双重MD5）
        
        算法推测：
        1. 第一次MD5：原始密码
        2. 第二次MD5：第一次结果 + salt（如果有）
        
        Args:
            password: 原始密码
            salt: 可选的盐值
            
        Returns:
            32位小写十六进制哈希字符串
        """
        try:
            # 第一次MD5：原始密码
            first_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
            
            # 第二次MD5：第一次结果 + salt
            if salt:
                second_input = first_hash + salt
            else:
                second_input = first_hash
            
            final_hash = hashlib.md5(second_input.encode('utf-8')).hexdigest()
            
            logger.debug(f"密码哈希完成: {len(password)}字符 -> 32位哈希")
            
            return final_hash
            
        except Exception as e:
            logger.error(f"密码哈希失败: {e}")
            raise
    
    @staticmethod
    def hash_password_simple(password: str) -> str:
        """
        简单MD5哈希（备用方案）
        
        Args:
            password: 原始密码
            
        Returns:
            32位小写十六进制哈希字符串
        """
        try:
            hash_result = hashlib.md5(password.encode('utf-8')).hexdigest()
            logger.debug(f"简单哈希完成: {len(password)}字符 -> 32位哈希")
            return hash_result
        except Exception as e:
            logger.error(f"简单哈希失败: {e}")
            raise
    
    @staticmethod
    def verify_password(password: str, hashed: str, salt: Optional[str] = None) -> bool:
        """
        验证密码
        
        Args:
            password: 原始密码
            hashed: 存储的哈希值
            salt: 可选的盐值
            
        Returns:
            bool: 密码是否匹配
        """
        try:
            computed_hash = PasswordHasher.hash_password_cn(password, salt)
            is_valid = computed_hash.lower() == hashed.lower()
            
            logger.debug(f"密码验证: {'成功' if is_valid else '失败'}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False


class TokenHasher:
    """
    Token哈希器
    
    处理会话Token的哈希和验证
    """
    
    @staticmethod
    def hash_token(token: str) -> str:
        """
        计算Token哈希
        
        Args:
            token: 会话Token
            
        Returns:
            SHA256哈希字符串
        """
        try:
            hash_result = hashlib.sha256(token.encode('utf-8')).hexdigest()
            logger.debug(f"Token哈希完成")
            return hash_result
        except Exception as e:
            logger.error(f"Token哈希失败: {e}")
            raise
    
    @staticmethod
    def generate_session_key(user_id: str, timestamp: int, secret: str) -> str:
        """
        生成会话密钥
        
        Args:
            user_id: 用户ID
            timestamp: 时间戳
            secret: 服务器密钥
            
        Returns:
            HMAC-SHA256会话密钥
        """
        try:
            import hmac
            
            message = f"{user_id}:{timestamp}".encode('utf-8')
            key = secret.encode('utf-8')
            
            session_key = hmac.new(key, message, hashlib.sha256).hexdigest()
            
            logger.debug(f"会话密钥生成完成")
            return session_key
            
        except Exception as e:
            logger.error(f"会话密钥生成失败: {e}")
            raise


# 便捷函数
def hash_password(password: str, salt: Optional[str] = None) -> str:
    """
    便捷函数：哈希密码
    
    Args:
        password: 原始密码
        salt: 可选的盐值
        
    Returns:
        哈希字符串
    """
    return PasswordHasher.hash_password_cn(password, salt)


def verify_password(password: str, hashed: str, salt: Optional[str] = None) -> bool:
    """
    便捷函数：验证密码
    
    Args:
        password: 原始密码
        hashed: 存储的哈希值
        salt: 可选的盐值
        
    Returns:
        bool: 密码是否匹配
    """
    return PasswordHasher.verify_password(password, hashed, salt)


__all__ = [
    'PasswordHasher',
    'TokenHasher',
    'hash_password',
    'verify_password'
]