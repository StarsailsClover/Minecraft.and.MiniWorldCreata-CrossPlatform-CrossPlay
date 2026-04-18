#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from src.crypto.real_crypto import RealECDHKeyExchange
e = RealECDHKeyExchange()
methods = [m for m in dir(e) if not m.startswith('_')]
print("Methods:", methods)
print("Has load_server_public_key:", 'load_server_public_key' in methods)
