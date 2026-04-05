#!/usr/bin/env python3
"""
业务层测试脚本
"""

import sys
sys.path.insert(0, '.')

from src.protocol import BusinessProtocol, BusinessMessage, BusinessCmdID


def test_business_message():
    """测试业务消息编解码"""
    print("\n=== Testing Business Message ===")
    
    # 创建消息
    msg = BusinessMessage(
        cmd_id=BusinessCmdID.PLAYER_ENTER,
        uin=123456,
        data=b"test_world",
        seq=1
    )
    
    # 编码
    encoded = msg.encode()
    print(f"✓ Encoded: {len(encoded)} bytes")
    
    # 解码
    decoded = BusinessMessage.decode(encoded)
    assert decoded is not None, "Decode failed"
    assert decoded.cmd_id == msg.cmd_id, "CmdID mismatch"
    assert decoded.uin == msg.uin, "UIN mismatch"
    assert decoded.data == msg.data, "Data mismatch"
    assert decoded.seq == msg.seq, "Seq mismatch"
    
    print(f"✓ Decoded: cmd_id=0x{decoded.cmd_id:04X}, uin={decoded.uin}")
    print("✓ Business message test passed")


def test_business_protocol():
    """测试业务协议"""
    print("\n=== Testing Business Protocol ===")
    
    protocol = BusinessProtocol()
    
    # 测试登录请求
    login_msg = protocol.create_login_request("test_user", "test_pass")
    print(f"✓ Login request: cmd_id=0x{login_msg.cmd_id:04X}")
    
    # 测试玩家进入
    enter_msg = protocol.create_player_enter(123456, "world_001")
    print(f"✓ Player enter: cmd_id=0x{enter_msg.cmd_id:04X}, world={enter_msg.data.decode()}")
    
    # 测试玩家移动
    move_msg = protocol.create_player_move(123456, 100.0, 64.0, 200.0)
    print(f"✓ Player move: cmd_id=0x{move_msg.cmd_id:04X}")
    
    # 测试聊天
    chat_msg = protocol.create_chat_message(123456, "Hello World!")
    print(f"✓ Chat: cmd_id=0x{chat_msg.cmd_id:04X}, msg={chat_msg.data.decode()}")
    
    # 测试心跳
    heartbeat_msg = protocol.create_heartbeat(123456)
    print(f"✓ Heartbeat: cmd_id=0x{heartbeat_msg.cmd_id:04X}")
    
    # 测试消息处理
    result = protocol.handle_message(enter_msg)
    assert result is not None, "Handle message failed"
    assert result["type"] == "player_enter", "Wrong handler"
    print(f"✓ Message handled: {result}")
    
    print("✓ Business protocol test passed")


def test_message_roundtrip():
    """测试消息往返"""
    print("\n=== Testing Message Roundtrip ===")
    
    protocol = BusinessProtocol()
    
    # 创建并发送各种消息
    messages = [
        protocol.create_login_request("user1", "pass1"),
        protocol.create_player_enter(123456, "world_001"),
        protocol.create_player_move(123456, 10.5, 64.0, -20.3),
        protocol.create_chat_message(123456, "Hello!"),
        protocol.create_heartbeat(123456),
    ]
    
    for msg in messages:
        # 编码
        encoded = msg.encode()
        
        # 解码
        decoded = BusinessMessage.decode(encoded)
        assert decoded is not None, "Decode failed"
        
        # 处理
        result = protocol.handle_message(decoded)
        assert result is not None, "Handle failed"
        
        print(f"✓ 0x{msg.cmd_id:04X}: {result['type']}")
    
    print("✓ Message roundtrip test passed")


def main():
    """主函数"""
    print("=" * 50)
    print("MnMCP Business Layer Test")
    print("=" * 50)
    
    try:
        test_business_message()
        test_business_protocol()
        test_message_roundtrip()
        
        print("\n" + "=" * 50)
        print("All business tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
