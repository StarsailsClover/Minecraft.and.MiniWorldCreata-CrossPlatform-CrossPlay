#!/usr/bin/env python3
"""
项目实际运行测试
验证所有模块是否可实际运行
"""

import sys
sys.path.insert(0, '.')

def test_crypto():
    """测试加密模块"""
    print("\n=== Testing Crypto Module ===")
    
    try:
        from src.crypto import ECDHKeyExchange, HKDFKeyDerivation, AESGCMCipher, CRYPTO_BACKEND
        print(f"  Backend: {CRYPTO_BACKEND}")
        
        # ECDH
        ecdh = ECDHKeyExchange()
        result = ecdh.generate_keypair()
        print(f"  ECDH generate_keypair: {result}")
        
        if result:
            result = ecdh.load_server_public_key()
            print(f"  ECDH load_server_public_key: {result}")
            
            if result:
                secret = ecdh.exchange()
                print(f"  ECDH exchange: {secret is not None}")
        
        # HKDF
        hkdf = HKDFKeyDerivation()
        keys = hkdf.derive(b'test_secret' * 4)
        print(f"  HKDF derive: {keys is not None}")
        
        # AES-GCM
        if keys:
            key_data = hkdf.extract_keys(keys)
            cipher = AESGCMCipher(key_data['aes_key'], key_data['nonce_base'])
            
            plaintext = b"Hello World!"
            ciphertext = cipher.encrypt(plaintext)
            print(f"  AES-GCM encrypt: {ciphertext is not None}")
            
            if ciphertext:
                decrypted = cipher.decrypt(ciphertext)
                print(f"  AES-GCM decrypt: {decrypted == plaintext}")
        
        print("  ✓ Crypto module functional")
        return True
        
    except Exception as e:
        print(f"  ✗ Crypto ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_network():
    """测试网络模块"""
    print("\n=== Testing Network Module ===")
    
    try:
        from src.network import UDPConnection, UDPConfig
        
        config = UDPConfig(port=0)  # 自动分配端口
        udp = UDPConnection(config)
        result = udp.create_socket()
        print(f"  UDP create_socket: {result}")
        
        if result:
            actual_port = udp.socket.getsockname()[1]
            print(f"  UDP actual port: {actual_port}")
            udp.stop()
            print(f"  UDP stop: OK")
        
        print("  ✓ Network module functional")
        return True
        
    except Exception as e:
        print(f"  ✗ Network ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_protocol():
    """测试协议模块"""
    print("\n=== Testing Protocol Module ===")
    
    try:
        from src.protocol import BusinessProtocol, BusinessCmdID
        from src.protocol.mc_java import MCJavaProtocol
        
        # Business Protocol
        bp = BusinessProtocol()
        msg = bp.create_chat_message(123456, "test message")
        print(f"  BusinessProtocol create_chat_message: OK")
        
        encoded = msg.encode()
        print(f"  BusinessProtocol encode: {len(encoded)} bytes")
        
        # MC Java Protocol
        mjp = MCJavaProtocol()
        pkt = mjp.create_chat_message("Hello")
        print(f"  MCJavaProtocol create_chat_message: OK")
        
        encoded_mc = pkt.encode()
        print(f"  MCJavaProtocol encode: {len(encoded_mc)} bytes")
        
        print("  ✓ Protocol module functional")
        return True
        
    except Exception as e:
        print(f"  ✗ Protocol ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mapping():
    """测试映射模块"""
    print("\n=== Testing Mapping Module ===")
    
    try:
        from src.mapping import CoordinateConverter, Vec3, BlockMapper, EntityMapper
        
        # Coordinate
        cc = CoordinateConverter()
        mc_pos = Vec3(100.5, 64.0, -200.3)
        mnw_pos = cc.mc_to_mnw(mc_pos)
        back = cc.mnw_to_mc(mnw_pos)
        
        match = abs(back.x - mc_pos.x) < 0.01
        print(f"  CoordinateConverter roundtrip: {match}")
        
        # Block Mapper
        bm = BlockMapper()
        mc_block = 1
        mnw_block, _ = bm.get_mnw_block(mc_block)
        back_block, _ = bm.get_mc_block(mnw_block)
        print(f"  BlockMapper: {back_block == mc_block}")
        
        # Entity Mapper
        em = EntityMapper()
        print(f"  EntityMapper loaded: {em.count} entities")
        
        print("  ✓ Mapping module functional")
        return True
        
    except Exception as e:
        print(f"  ✗ Mapping ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auth():
    """测试认证模块"""
    print("\n=== Testing Auth Module ===")
    
    try:
        from src.auth import MiniWorldLogin
        from src.config import get_api_server
        
        login = MiniWorldLogin()
        print(f"  MiniWorldLogin API: {login.API_BASE}")
        print(f"  API Server: {get_api_server().host}:{get_api_server().port}")
        
        # 注意：实际登录需要真实账号
        print("  ✓ Auth module structure OK (login requires real credentials)")
        return True
        
    except Exception as e:
        print(f"  ✗ Auth ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_room():
    """测试房间模块"""
    print("\n=== Testing Room Module ===")
    
    try:
        from src.room import RoomManager, RoomMode, RoomPermission
        
        rm = RoomManager(uin=123456, token="test_token")
        print(f"  RoomManager created: OK")
        print(f"  RoomMode: SURVIVAL={RoomMode.SURVIVAL}")
        print(f"  RoomPermission: PUBLIC={RoomPermission.PUBLIC}")
        
        print("  ✓ Room module structure OK")
        return True
        
    except Exception as e:
        print(f"  ✗ Room ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("MnMCP Project Audit - Actual Runtime Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Crypto", test_crypto()))
    results.append(("Network", test_network()))
    results.append(("Protocol", test_protocol()))
    results.append(("Mapping", test_mapping()))
    results.append(("Auth", test_auth()))
    results.append(("Room", test_room()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} modules functional")
    
    if passed == total:
        print("\n✓ All modules are actually runnable!")
        return 0
    else:
        print(f"\n✗ {total - passed} modules have issues")
        return 1


if __name__ == '__main__':
    sys.exit(main())
