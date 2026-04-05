#!/usr/bin/env python3
"""
Minecraft Java 协议测试
"""

import sys
sys.path.insert(0, '.')

from src.protocol.mc_java import MCJavaProtocol, MCJavaPacket, MCJavaPacketID


def test_varint_encoding():
    """测试 varint 编解码"""
    print("\n=== Testing VarInt Encoding ===")
    
    protocol = MCJavaProtocol()
    
    test_values = [0, 1, 127, 128, 255, 300, 25565, 2097151]
    
    for value in test_values:
        encoded = protocol._encode_varint(value)
        decoded, _ = MCJavaPacket._decode_varint(encoded + b'\x00', 0)
        assert decoded == value, f"VarInt mismatch: {value} != {decoded}"
        print(f"✓ VarInt {value} -> {encoded.hex()} -> {decoded}")
    
    print("✓ VarInt encoding test passed")


def test_packet_encoding():
    """测试数据包编解码"""
    print("\n=== Testing Packet Encoding ===")
    
    # 创建数据包
    packet = MCJavaPacket(
        packet_id=MCJavaPacketID.KEEP_ALIVE,
        data=b'\x00\x00\x00\x00\x00\x00\x00\x01'  # keep_alive_id = 1
    )
    
    # 编码
    encoded = packet.encode()
    print(f"✓ Encoded packet: {len(encoded)} bytes")
    print(f"  Hex: {encoded.hex()}")
    
    # 解码
    decoded = MCJavaPacket.decode(encoded)
    assert decoded is not None, "Decode failed"
    assert decoded.packet_id == packet.packet_id, "Packet ID mismatch"
    assert decoded.data == packet.data, "Data mismatch"
    
    print(f"✓ Decoded packet: ID=0x{decoded.packet_id:02X}, Data={decoded.data.hex()}")
    print("✓ Packet encoding test passed")


def test_protocol_packets():
    """测试协议数据包创建"""
    print("\n=== Testing Protocol Packets ===")
    
    protocol = MCJavaProtocol()
    
    # 握手包
    handshake = protocol.create_handshake("localhost", 25565)
    print(f"✓ Handshake packet: {len(handshake.encode())} bytes")
    
    # 登录开始包
    login_start = protocol.create_login_start("TestPlayer")
    print(f"✓ Login start packet: {len(login_start.encode())} bytes")
    
    # 心跳包
    keep_alive = protocol.create_keep_alive(12345)
    print(f"✓ Keep alive packet: {len(keep_alive.encode())} bytes")
    
    # 聊天消息包
    chat = protocol.create_chat_message("Hello World!")
    print(f"✓ Chat packet: {len(chat.encode())} bytes")
    
    # 玩家位置包
    position = protocol.create_player_position(100.5, 64.0, -200.3, True)
    print(f"✓ Position packet: {len(position.encode())} bytes")
    
    print("✓ Protocol packets test passed")


def main():
    """主函数"""
    print("=" * 50)
    print("Minecraft Java Protocol Test")
    print("=" * 50)
    
    try:
        test_varint_encoding()
        test_packet_encoding()
        test_protocol_packets()
        
        print("\n" + "=" * 50)
        print("All Minecraft Java tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
