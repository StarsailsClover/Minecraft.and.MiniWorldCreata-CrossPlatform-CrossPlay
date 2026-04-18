#!/usr/bin/env python3
"""
测试迷你世界真实协议
"""

import sys
sys.path.insert(0, '.')

from src.protocol.mnw_real import MNWPacketHeader, MNWProtocolHandler, MNWConnection
from src.config import get_game_server

print("=" * 60)
print("迷你世界真实协议测试")
print("=" * 60)

# 测试头部编解码
print("\n=== 测试头部编解码 ===")
header = MNWPacketHeader(
    opcode=864,
    entity_id=12345,
    x=100000,  # 100.0 * 1000
    y=64000,   # 64.0 * 1000
    z=200000   # 200.0 * 1000
)

encoded = header.to_bytes()
print(f"编码后: {len(encoded)} bytes")
print(f"  Hex: {encoded.hex()}")

decoded = MNWPacketHeader.from_bytes(b'\x00\x00\x00\x00' + encoded)
if decoded:
    print(f"解码成功:")
    print(f"  OpCode: {decoded.opcode}")
    print(f"  Entity ID: {decoded.entity_id}")
    print(f"  Coords: {decoded.get_coords()}")
else:
    print("解码失败")

# 测试协议处理器
print("\n=== 测试协议处理器 ===")
protocol = MNWProtocolHandler()

# 创建位置包
pos_packet = protocol.create_position_packet(12345, 100.5, 64.0, -200.3)
print(f"位置包: {len(pos_packet)} bytes")
print(f"  Hex: {pos_packet.hex()}")

# 解析位置包
parsed = protocol.parse_position_packet(pos_packet)
if parsed:
    print(f"解析成功:")
    print(f"  Seq: {parsed['seq']}")
    print(f"  Entity: {parsed['entity_id']}")
    print(f"  Position: ({parsed['x']}, {parsed['y']}, {parsed['z']})")

# 创建心跳包
heartbeat = protocol.create_heartbeat_packet(1, 1234567890)
print(f"\n心跳包: {len(heartbeat)} bytes")

# 测试连接
print("\n=== 测试连接 ===")
server = get_game_server()
conn = MNWConnection(server.host, server.port)

if conn.connect():
    print(f"✓ 连接到 {server.host}:{server.port}")
    
    # 发送位置
    if conn.send_position(100.5, 64.0, 200.0):
        print("✓ 位置已发送")
    
    # 发送心跳
    if conn.send_heartbeat(1):
        print("✓ 心跳已发送")
    
    # 尝试接收
    print("\n等待响应 (3秒)...")
    import time
    time.sleep(3)
    
    response = conn.receive()
    if response:
        print(f"✓ 收到响应: {response}")
    else:
        print("  无响应 (可能需要正确的握手)")
    
    conn.disconnect()
    print("✓ 连接已关闭")
else:
    print("✗ 连接失败")

print("\n=== 测试完成 ===")
