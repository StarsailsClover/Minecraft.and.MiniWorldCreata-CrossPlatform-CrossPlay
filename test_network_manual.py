#!/usr/bin/env python3
"""
网络层测试脚本
"""

import sys
import time
sys.path.insert(0, '.')

from src.network import UDPConnection, UDPConfig
from src.network.raknet_adapter import RakNetAdapter, RakNetConfig
from src.network.session import SessionManager


def test_udp():
    """测试 UDP 连接"""
    print("\n=== Testing UDP ===")
    
    # 创建两个 UDP 连接（模拟客户端和服务器）
    config1 = UDPConfig(port=0)  # 自动分配端口
    config2 = UDPConfig(port=0)
    
    conn1 = UDPConnection(config1)
    conn2 = UDPConnection(config2)
    
    # 创建 socket
    assert conn1.create_socket(), "Failed to create socket 1"
    assert conn2.create_socket(), "Failed to create socket 2"
    
    # 获取实际端口
    port1 = conn1.socket.getsockname()[1]
    port2 = conn2.socket.getsockname()[1]
    
    print(f"✓ Socket 1 created on port {port1}")
    print(f"✓ Socket 2 created on port {port2}")
    
    # 设置接收回调
    received = []
    def on_receive(data, addr):
        received.append(data)
        print(f"✓ Received: {data} from {addr}")
    
    conn2.on_receive = on_receive
    conn2.start_receive()
    
    # 发送数据
    test_data = b"Hello UDP!"
    assert conn1.send(test_data, ("127.0.0.1", port2)), "Send failed"
    print(f"✓ Sent: {test_data}")
    
    # 等待接收
    time.sleep(0.5)
    
    assert len(received) == 1, "Data not received"
    assert received[0] == test_data, "Data mismatch"
    
    # 清理
    conn1.stop()
    conn2.stop()
    
    print("✓ UDP test passed")


def test_raknet_adapter():
    """测试 RakNet 适配器"""
    print("\n=== Testing RakNet Adapter ===")
    
    adapter = RakNetAdapter()
    
    # 测试连接请求
    conn_req = adapter.create_connection_request()
    print(f"✓ Connection request created: {len(conn_req)} bytes")
    
    # 测试 ping
    ping = adapter.create_ping()
    print(f"✓ Ping created: {len(ping)} bytes")
    
    # 测试用户数据包编码
    user_data = b"test data"
    encoded = adapter.encode_user_packet(user_data)
    print(f"✓ User packet encoded: {len(encoded)} bytes")
    
    # 测试解码
    decoded = adapter.decode_user_packet(encoded)
    assert decoded == user_data, "Decode mismatch"
    print(f"✓ User packet decoded: {decoded}")
    
    print("✓ RakNet adapter test passed")


def test_session_manager():
    """测试会话管理"""
    print("\n=== Testing Session Manager ===")
    
    manager = SessionManager()
    
    # 建立会话
    uin = 123456
    session = manager.establish_session(uin)
    assert session is not None, "Session establishment failed"
    
    print(f"✓ Session established: {session.session_id}")
    print(f"  - UIN: {session.uin}")
    print(f"  - AES key: {len(session.aes_key)} bytes")
    print(f"  - Nonce base: {len(session.nonce_base)} bytes")
    
    # 测试加密/解密
    plaintext = b"Hello Session!"
    ciphertext = manager.encrypt_for_session(session.session_id, plaintext)
    assert ciphertext is not None, "Encryption failed"
    print(f"✓ Encrypted: {len(ciphertext)} bytes")
    
    decrypted = manager.decrypt_for_session(session.session_id, ciphertext)
    assert decrypted == plaintext, "Decryption mismatch"
    print(f"✓ Decrypted: {decrypted}")
    
    # 关闭会话
    manager.close_session(session.session_id)
    print("✓ Session closed")
    
    print("✓ Session manager test passed")


def main():
    """主函数"""
    print("=" * 50)
    print("MnMCP Network Layer Test")
    print("=" * 50)
    
    try:
        test_udp()
        test_raknet_adapter()
        test_session_manager()
        
        print("\n" + "=" * 50)
        print("All network tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
