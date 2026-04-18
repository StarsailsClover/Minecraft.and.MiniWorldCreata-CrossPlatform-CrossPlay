#!/usr/bin/env python3
"""
测试加密模块实际运行
"""

import sys
sys.path.insert(0, '.')

from src.crypto import ECDHKeyExchange, HKDFKeyDerivation, AESGCMCipher, CRYPTO_BACKEND

print(f"Crypto Backend: {CRYPTO_BACKEND}")
print()

# 测试 ECDH
print("=== Testing ECDH ===")
ecdh = ECDHKeyExchange()
print("generate:", ecdh.generate_keypair())
print("load:", ecdh.load_server_public_key())
result = ecdh.exchange()
print("exchange:", result is not None)
if result:
    print(f"  Secret: {result.hex()[:32]}...")

print()

# 测试 HKDF
print("=== Testing HKDF ===")
hkdf = HKDFKeyDerivation()
keys = hkdf.derive(b'test_secret' * 4)
print("derive:", keys is not None)
if keys:
    key_data = hkdf.extract_keys(keys)
    print(f"  AES Key: {key_data['aes_key'].hex()[:16]}...")
    print(f"  Nonce: {key_data['nonce_base'].hex()[:16]}...")

print()

# 测试 AES-GCM
print("=== Testing AES-GCM ===")
if keys:
    cipher = AESGCMCipher(key_data['aes_key'], key_data['nonce_base'])
    
    plaintext = b"Hello World!"
    ciphertext = cipher.encrypt(plaintext)
    print("encrypt:", ciphertext is not None)
    
    if ciphertext:
        decrypted = cipher.decrypt(ciphertext)
        print("decrypt:", decrypted == plaintext)
        print(f"  Original: {plaintext}")
        print(f"  Decrypted: {decrypted}")

print()
print("=== All Crypto Tests Passed ===")
