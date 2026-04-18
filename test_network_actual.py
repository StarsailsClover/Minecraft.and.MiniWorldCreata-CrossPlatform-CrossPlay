#!/usr/bin/env python3
"""
实际网络连接测试
测试与迷你世界服务器的真实连接
"""

import sys
import socket
import time
sys.path.insert(0, '.')

from src.config import get_game_server
from src.crypto import ECDHKeyExchange, HKDFKeyDerivation, AESGCMCipher

print("=" * 60)
print("实际网络连接测试")
print("=" * 60)

# 获取服务器配置
server = get_game_server()
print(f"\n目标服务器: {server.host}:{server.port}")

# 创建 UDP 套接字
print("\n=== 创建 UDP 套接字 ===")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5.0)
print("✓ UDP socket created")

# 执行密钥交换
print("\n=== 执行密钥交换 ===")
ecdh = ECDHKeyExchange()
shared_secret = ecdh.complete_exchange()
if shared_secret:
    print(f"✓ Key exchange successful")
    print(f"  Secret: {shared_secret.hex()[:32]}...")
else:
    print("✗ Key exchange failed")
    sys.exit(1)

# 派生会话密钥
print("\n=== 派生会话密钥 ===")
hkdf = HKDFKeyDerivation()
key_material = hkdf.derive(shared_secret)
keys = hkdf.extract_keys(key_material)
print(f"✓ Session keys derived")
print(f"  AES Key: {keys['aes_key'].hex()[:16]}...")

# 创建加密器
print("\n=== 创建加密器 ===")
cipher = AESGCMCipher(keys['aes_key'], keys['nonce_base'])
print("✓ Cipher created")

# 测试加密
print("\n=== 测试加密 ===")
test_data = b"Hello MiniWorld!"
encrypted = cipher.encrypt(test_data)
if encrypted:
    print(f"✓ Encryption successful: {len(encrypted)} bytes")
else:
    print("✗ Encryption failed")

# 尝试发送数据到服务器
print("\n=== 尝试连接服务器 ===")
try:
    # 发送测试数据
    sock.sendto(encrypted or b'test', (server.host, server.port))
    print(f"✓ Data sent to {server.host}:{server.port}")
    
    # 尝试接收响应
    try:
        data, addr = sock.recvfrom(1024)
        print(f"✓ Response received from {addr}: {len(data)} bytes")
        print(f"  Data: {data.hex()[:64]}...")
    except socket.timeout:
        print("  No response (timeout) - server may require proper handshake")
    
except Exception as e:
    print(f"✗ Connection error: {e}")

sock.close()
print("\n=== 测试完成 ===")
