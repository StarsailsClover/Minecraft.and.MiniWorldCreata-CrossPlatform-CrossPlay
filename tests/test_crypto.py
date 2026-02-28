#!/usr/bin/env python3
"""
加密模块真实测试 - Phase 4
测试AES加密、密码哈希等功能
"""

import sys
import os
import hashlib
import hmac
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from crypto.aes_crypto import AESCipher, MiniWorldCrypto
from crypto.password_hasher import PasswordHasher, TokenHasher


class TestCrypto:
    """加密模块测试"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name: str, condition: bool, details: str = ""):
        """记录测试结果"""
        if condition:
            self.passed += 1
            status = "✓"
        else:
            self.failed += 1
            status = "✗"
        
        self.tests.append((name, status, details))
        return condition
    
    def run_all(self):
        """运行所有测试"""
        print("=" * 70)
        print(" 加密模块真实测试")
        print("=" * 70)
        
        # 测试AES-128-CBC
        self._test_aes_cbc()
        
        # 测试AES-256-GCM
        self._test_aes_gcm()
        
        # 测试密码哈希
        self._test_password_hash()
        
        # 测试会话密钥
        self._test_session_key()
        
        # 打印结果
        self._print_results()
    
    def _test_aes_cbc(self):
        """测试AES-128-CBC加密"""
        print("\n[测试] AES-128-CBC加密...")
        
        try:
            # 测试数据
            key = b'1234567890123456'  # 16字节
            plaintext = b'Hello, MiniWorld!'
            
            # 创建加密器
            cipher = AESCipher(key, mode="CBC")
            
            # 加密
            ciphertext = cipher.encrypt_cbc(plaintext)
            
            # 解密
            decrypted = cipher.decrypt_cbc(ciphertext)
            
            # 验证
            success = decrypted == plaintext
            self.test(
                "AES-128-CBC 加密/解密",
                success,
                f"原始: {plaintext} -> 加密 -> 解密: {decrypted}"
            )
            
            # 验证IV被正确使用
            cipher2 = AESCipher(key, mode="CBC", iv=cipher.iv)
            decrypted2 = cipher2.decrypt_cbc(ciphertext)
            success2 = decrypted2 == plaintext
            self.test(
                "AES-128-CBC IV一致性",
                success2,
                f"使用相同IV解密成功"
            )
            
        except Exception as e:
            self.test("AES-128-CBC", False, f"异常: {e}")
    
    def _test_aes_gcm(self):
        """测试AES-256-GCM加密"""
        print("\n[测试] AES-256-GCM加密...")
        
        try:
            # 测试数据
            key = b'12345678901234567890123456789012'  # 32字节
            plaintext = b'Hello, MiniWorld Global!'
            aad = b'additional_data'
            
            # 创建加密器
            cipher = AESCipher(key, mode="GCM")
            
            # 加密
            ciphertext, tag = cipher.encrypt_gcm(plaintext, aad)
            
            # 解密
            decrypted = cipher.decrypt_gcm(ciphertext, tag, aad)
            
            # 验证
            success = decrypted == plaintext
            self.test(
                "AES-256-GCM 加密/解密",
                success,
                f"AAD验证成功，数据完整性保护正常"
            )
            
            # 测试错误标签
            try:
                wrong_tag = b'\x00' * len(tag)
                cipher.decrypt_gcm(ciphertext, wrong_tag, aad)
                self.test("AES-256-GCM 错误标签检测", False, "应该抛出异常")
            except Exception:
                self.test("AES-256-GCM 错误标签检测", True, "正确拒绝错误标签")
            
        except Exception as e:
            self.test("AES-256-GCM", False, f"异常: {e}")
    
    def _test_password_hash(self):
        """测试密码哈希"""
        print("\n[测试] 密码哈希...")
        
        try:
            password = "test_password_123"
            salt = "random_salt"
            
            # 哈希
            hashed = PasswordHasher.hash_password_cn(password, salt)
            
            # 验证正确密码
            is_valid = PasswordHasher.verify_password(password, hashed, salt)
            self.test(
                "密码哈希验证（正确密码）",
                is_valid,
                f"哈希值: {hashed[:16]}..."
            )
            
            # 验证错误密码
            is_invalid = PasswordHasher.verify_password("wrong_password", hashed, salt)
            self.test(
                "密码哈希验证（错误密码）",
                not is_invalid,
                "正确拒绝错误密码"
            )
            
            # 验证哈希长度
            self.test(
                "哈希长度验证",
                len(hashed) == 32,
                f"MD5哈希长度: {len(hashed)}"
            )
            
        except Exception as e:
            self.test("密码哈希", False, f"异常: {e}")
    
    def _test_session_key(self):
        """测试会话密钥生成"""
        print("\n[测试] 会话密钥生成...")
        
        try:
            user_id = "12345678"
            timestamp = 1700000000
            secret = "server_secret_key"
            
            # 生成密钥
            session_key = TokenHasher.generate_session_key(user_id, timestamp, secret)
            
            # 验证格式
            self.test(
                "会话密钥格式",
                len(session_key) == 64,
                f"HMAC-SHA256长度: {len(session_key)}"
            )
            
            # 验证确定性
            session_key2 = TokenHasher.generate_session_key(user_id, timestamp, secret)
            self.test(
                "会话密钥确定性",
                session_key == session_key2,
                "相同输入产生相同输出"
            )
            
            # 验证不同输入产生不同输出
            session_key3 = TokenHasher.generate_session_key(user_id, timestamp + 1, secret)
            self.test(
                "会话密钥唯一性",
                session_key != session_key3,
                "不同输入产生不同输出"
            )
            
        except Exception as e:
            self.test("会话密钥", False, f"异常: {e}")
    
    def _print_results(self):
        """打印测试结果"""
        print("\n" + "=" * 70)
        print(" 测试结果")
        print("=" * 70)
        
        for name, status, details in self.tests:
            print(f"  [{status}] {name}")
            if details:
                print(f"       {details}")
        
        print("\n" + "=" * 70)
        print(f" 通过: {self.passed}")
        print(f" 失败: {self.failed}")
        print(f" 总计: {self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n ✓ 所有测试通过!")
        else:
            print(f"\n ✗ {self.failed}个测试失败")
        
        print("=" * 70)


if __name__ == "__main__":
    tester = TestCrypto()
    tester.run_all()
