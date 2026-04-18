#!/usr/bin/env python3
"""
测试真实加密实现
"""

import sys
sys.path.insert(0, '.')

# 测试真实加密实现
try:
    from src.crypto.real_crypto import RealECDHKeyExchange
    ecdh = RealECDHKeyExchange()
    print('RealECDHKeyExchange imported')
    methods = [m for m in dir(ecdh) if not m.startswith('_')]
    print('Methods:', methods)
    
    # 测试生成密钥对
    result = ecdh.generate_keypair()
    print('generate_keypair:', result)
    
    # 测试加载服务器公钥
    result = ecdh.load_server_public_key()
    print('load_server_public_key:', result)
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
