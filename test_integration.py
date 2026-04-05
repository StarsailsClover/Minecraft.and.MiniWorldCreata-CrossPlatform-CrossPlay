#!/usr/bin/env python3
"""
集成测试 - 完整流程
"""

import sys
sys.path.insert(0, '.')


def test_all_modules():
    """测试所有模块"""
    print("\n=== Testing All Modules ===")
    
    # 1. 配置模块
    print("\n1. Config Module")
    from src.config import get_game_server, get_api_server, get_all_servers
    game = get_game_server()
    api = get_api_server()
    print(f"   ✓ Game Server: {game.host}:{game.port}")
    print(f"   ✓ API Server: {api.host}:{api.port}")
    
    # 2. 加密模块
    print("\n2. Crypto Module")
    from src.crypto import ECDHKeyExchange, HKDFKeyDerivation, AESGCMCipher, CRYPTO_BACKEND
    print(f"   ✓ Backend: {CRYPTO_BACKEND}")
    
    # 3. 协议模块
    print("\n3. Protocol Module")
    from src.protocol import BusinessProtocol, BusinessCmdID
    from src.protocol.mc_java import MCJavaProtocol
    bp = BusinessProtocol()
    mjp = MCJavaProtocol()
    print(f"   ✓ Business Protocol: OK")
    print(f"   ✓ MC Java Protocol: OK")
    
    # 4. 网络模块
    print("\n4. Network Module")
    from src.network import UDPConnection, SessionManager
    print(f"   ✓ UDP Connection: OK")
    print(f"   ✓ Session Manager: OK")
    
    # 5. 映射模块
    print("\n5. Mapping Module")
    from src.mapping import CoordinateConverter, BlockMapper, EntityMapper
    cc = CoordinateConverter()
    bm = BlockMapper()
    em = EntityMapper()
    print(f"   ✓ Coordinate Converter: OK")
    print(f"   ✓ Block Mapper: {bm.count} blocks")
    print(f"   ✓ Entity Mapper: {em.count} entities")
    
    # 6. 认证模块
    print("\n6. Auth Module")
    from src.auth import MiniWorldLogin
    login = MiniWorldLogin()
    print(f"   ✓ Login API: {login.API_BASE}")
    
    # 7. 房间模块
    print("\n7. Room Module")
    from src.room import RoomManager
    rm = RoomManager(uin=123456, token="test")
    print(f"   ✓ Room Manager: OK")
    
    # 8. 客户端模块
    print("\n8. Client Module")
    from src.client import MiniWorldClient, MiniWorldClientConfig
    config = MiniWorldClientConfig(username="test", password="test")
    print(f"   ✓ Client Config: OK")
    
    # 9. 桥接器模块
    print("\n9. Bridge Module")
    from src.bridge_v2 import MnMCPBridgeV2, BridgeV2Config
    bridge_config = BridgeV2Config()
    print(f"   ✓ Bridge V2 Config: OK")
    
    print("\n✓ All modules imported successfully")


def test_data_flow():
    """测试数据流"""
    print("\n=== Testing Data Flow ===")
    
    # 坐标转换
    from src.mapping import CoordinateConverter, Vec3
    cc = CoordinateConverter()
    mc_pos = Vec3(100.5, 64.0, -200.3)
    mnw_pos = cc.mc_to_mnw(mc_pos)
    back = cc.mnw_to_mc(mnw_pos)
    assert abs(back.x - mc_pos.x) < 0.01
    print(f"   ✓ Coordinate conversion: OK")
    
    # 方块映射
    from src.mapping import BlockMapper
    bm = BlockMapper()
    mc_block = 1  # stone
    mnw_block, _ = bm.get_mnw_block(mc_block)
    back_block, _ = bm.get_mc_block(mnw_block)
    assert back_block == mc_block
    print(f"   ✓ Block mapping: OK")
    
    # 业务消息
    from src.protocol import BusinessProtocol, BusinessCmdID
    bp = BusinessProtocol()
    msg = bp.create_chat_message(123456, "Hello")
    assert msg.cmd_id == BusinessCmdID.CHAT_MESSAGE
    print(f"   ✓ Business message: OK")
    
    print("\n✓ Data flow test passed")


def test_version():
    """测试版本"""
    print("\n=== Testing Version ===")
    
    from src import __version__
    print(f"   Version: {__version__}")
    
    # 解析版本
    parts = __version__.split('_')
    print(f"   Week: {parts[0]}")
    print(f"   Branch: {parts[1]}")
    print(f"   Version: {parts[2]}")
    
    print("\n✓ Version test passed")


def main():
    """主函数"""
    print("=" * 60)
    print("MnMCP Integration Test")
    print("=" * 60)
    
    try:
        test_all_modules()
        test_data_flow()
        test_version()
        
        print("\n" + "=" * 60)
        print("All integration tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
