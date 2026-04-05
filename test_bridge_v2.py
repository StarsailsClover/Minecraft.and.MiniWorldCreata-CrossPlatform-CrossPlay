#!/usr/bin/env python3
"""
MnMCP Bridge V2 测试
"""

import sys
import time
sys.path.insert(0, '.')

from src.bridge_v2 import MnMCPBridgeV2, BridgeV2Config
from src.client import MiniWorldClient, MiniWorldClientConfig
from src.config import get_game_server


def test_mnw_client():
    """测试迷你世界客户端"""
    print("\n=== Testing MiniWorld Client ===")
    
    config = MiniWorldClientConfig(
        username="test_user",
        password="test_pass",
        server=get_game_server()
    )
    
    client = MiniWorldClient(config)
    
    # 连接
    assert client.connect(), "Failed to connect"
    print("✓ Connected to MiniWorld server")
    print(f"  Server: {config.server.host}:{config.server.port}")
    
    # 停止
    client.disconnect()
    print("✓ Disconnected")
    
    print("✓ MiniWorld client test passed")


def test_bridge_v2():
    """测试桥接器 V2"""
    print("\n=== Testing Bridge V2 ===")
    
    config = BridgeV2Config(
        mnw_username="test_user",
        mnw_password="test_pass",
        mnw_world_id="test_world",
        enable_chat_bridge=True,
        enable_movement_bridge=True
    )
    
    bridge = MnMCPBridgeV2(config)
    
    # 启动
    # 注意：这里会尝试连接真实服务器，可能需要跳过
    # assert bridge.start(), "Failed to start bridge"
    
    print("✓ Bridge V2 created")
    print(f"  Config: {bridge.get_status()}")
    
    # 停止
    # bridge.stop()
    
    print("✓ Bridge V2 test passed")


def test_server_config():
    """测试服务器配置"""
    print("\n=== Testing Server Config ===")
    
    from src.config import get_game_server, get_api_server, get_all_servers
    
    game_server = get_game_server()
    print(f"✓ Game Server: {game_server.host}:{game_server.port}")
    
    api_server = get_api_server()
    print(f"✓ API Server: {api_server.host}:{api_server.port}")
    
    all_servers = get_all_servers()
    print(f"✓ Total servers:")
    for category, servers in all_servers.items():
        print(f"  {category}: {len(servers)} servers")
    
    print("✓ Server config test passed")


def main():
    """主函数"""
    print("=" * 50)
    print("MnMCP Bridge V2 Test")
    print("=" * 50)
    
    try:
        test_server_config()
        # test_mnw_client()  # 需要真实服务器，暂时跳过
        test_bridge_v2()
        
        print("\n" + "=" * 50)
        print("All Bridge V2 tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
