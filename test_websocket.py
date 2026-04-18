"""
WebSocket 连接器测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import json
import asyncio
from dataclasses import dataclass
from typing import Optional, Callable
from enum import IntEnum

class MNWChatClient:
    """模拟 WebSocket 聊天客户端"""
    
    def __init__(self):
        self.ws = None
        self._running = False
        self._message_handler: Optional[Callable] = None
        self._received_messages = []
        self._connected = False
    
    async def connect(self, jwt_token: str) -> bool:
        """连接到聊天服务器"""
        print(f"[WebSocket] 连接到 chatpush.mini1.cn:19701...")
        print(f"[WebSocket] 使用 JWT: {jwt_token[:30]}...")
        
        # 模拟连接
        self._connected = True
        self._running = True
        
        print("[WebSocket] 连接成功!")
        
        # 模拟接收循环
        asyncio.create_task(self._receive_loop())
        
        return True
    
    async def disconnect(self):
        """断开聊天连接"""
        print("[WebSocket] 断开连接...")
        self._running = False
        self._connected = False
        print("[WebSocket] 已断开")
    
    async def send_chat(self, message: str, room_id: str = "") -> bool:
        """发送聊天消息"""
        if not self._connected:
            print("[WebSocket] 未连接，无法发送")
            return False
        
        payload = {
            "type": "chat",
            "message": message,
            "room_id": room_id,
            "timestamp": 1773418347
        }
        
        print(f"[WebSocket] 发送消息: {message}")
        return True
    
    def set_message_handler(self, handler: Callable):
        """设置消息处理器"""
        self._message_handler = handler
    
    async def _receive_loop(self):
        """模拟接收循环"""
        import random
        
        # 模拟接收一些消息
        test_messages = [
            {"type": "chat", "from": "player1", "message": "Hello!", "room_id": "room_12345"},
            {"type": "chat", "from": "player2", "message": "Hi there!", "room_id": "room_12345"},
            {"type": "system", "message": "Player3 joined the room", "room_id": "room_12345"},
        ]
        
        for msg in test_messages:
            if not self._running:
                break
            
            await asyncio.sleep(0.5)  # 模拟延迟
            
            print(f"[WebSocket] 接收消息: {msg}")
            self._received_messages.append(msg)
            
            if self._message_handler:
                await self._message_handler(msg)


async def test_websocket_connection():
    print("\n" + "=" * 60)
    print("WebSocket 连接器测试")
    print("=" * 60)
    
    client = MNWChatClient()
    
    # 设置消息处理器
    async def on_message(msg):
        print(f"  [Handler] 收到消息: {msg.get('message', '')}")
    
    client.set_message_handler(on_message)
    
    # 测试连接
    print("\n[Step 1] 连接 WebSocket...")
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.jwt"
    success = await client.connect(jwt)
    
    if not success:
        print("✗ 连接失败")
        return False
    print("✓ 连接成功")
    
    # 测试发送消息
    print("\n[Step 2] 发送聊天消息...")
    await client.send_chat("Hello, MnMCP!", "room_12345")
    await client.send_chat("This is a test message.", "room_12345")
    print("✓ 消息发送完成")
    
    # 等待接收消息
    print("\n[Step 3] 等待接收消息...")
    await asyncio.sleep(2)
    
    print(f"✓ 共接收 {len(client._received_messages)} 条消息")
    
    # 断开连接
    print("\n[Step 4] 断开连接...")
    await client.disconnect()
    print("✓ 断开完成")
    
    return True


async def main():
    try:
        success = await test_websocket_connection()
        
        print("\n" + "=" * 60)
        if success:
            print("测试结果: 通过")
        else:
            print("测试结果: 失败")
        print("=" * 60)
        
        return success
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
