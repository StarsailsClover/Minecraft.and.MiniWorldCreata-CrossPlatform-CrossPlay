"""
TCP 连接器测试 - 模拟登录流程
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import struct
import asyncio
from dataclasses import dataclass, field
from typing import Optional
from enum import IntEnum

# 模拟消息类型
class MNWMsgType(IntEnum):
    LOGIN_REQ = 3001
    LOGIN_RESP = 3002
    HEARTBEAT = 3003
    ROLE_ENTER_WORLD = 1001

@dataclass
class MNWSessionInfo:
    jwt_token: str = ""
    uin: str = ""
    device_id: str = ""
    session_key: Optional[bytes] = None
    game_server_ip: str = ""
    game_server_port: int = 4012
    room_id: str = ""
    player_id: int = 0
    player_name: str = ""
    crypto_enabled: bool = False

class MNWTCPConnector:
    """模拟 TCP 连接器"""
    
    def __init__(self):
        self.session: Optional[MNWSessionInfo] = None
        self._connected = False
        self._seq = 0
        self._buffer = b""
    
    async def connect(self, host: str, port: int) -> bool:
        print(f"[TCP] 连接到 {host}:{port}...")
        self._connected = True
        print(f"[TCP] 连接成功!")
        return True
    
    async def disconnect(self):
        print("[TCP] 断开连接")
        self._connected = False
    
    async def send(self, data: bytes) -> bool:
        if not self._connected:
            return False
        print(f"[TCP] 发送 {len(data)} bytes")
        return True
    
    async def send_message(self, msg_type: int, data: bytes) -> bool:
        """发送协议消息"""
        header = struct.pack('>HI', msg_type, len(data))
        return await self.send(header + data)
    
    async def receive(self) -> Optional[bytes]:
        """模拟接收数据"""
        # 模拟 LOGIN_RESP
        if self._seq == 0:
            self._seq += 1
            # 构建 LOGIN_RESP: msg_type (2) + payload_len (4) + payload
            result = 0  # 成功
            session_key = b'simulated_session_key_32bytes!'
            
            # payload: result (4) + key_len (4) + session_key
            payload = struct.pack('>I', result)
            payload += struct.pack('>I', len(session_key))
            payload += session_key
            
            # 完整消息: msg_type (2) + payload_len (4) + payload
            data = struct.pack('>H', MNWMsgType.LOGIN_RESP)
            data += struct.pack('>I', len(payload))
            data += payload
            
            print(f"  [Debug] 构建 LOGIN_RESP: {len(data)} bytes")
            return data
        return None
    
    async def receive_message(self) -> Optional[tuple]:
        """接收协议消息"""
        data = await self.receive()
        if not data:
            return None
        if len(data) < 6:
            print(f"  [Debug] 数据长度不足: {len(data)} bytes")
            return None
        msg_type = struct.unpack('>H', data[:2])[0]
        data_len = struct.unpack('>I', data[2:6])[0]
        if len(data) < 6 + data_len:
            print(f"  [Debug] payload 长度不足: {len(data)} < {6 + data_len}")
            return None
        payload = data[6:6+data_len]
        return (msg_type, payload)


class MNWAuthClient:
    """模拟认证客户端"""
    
    async def login(self, uin: str, password: str, device_id: str) -> Optional[str]:
        print(f"[Auth] 登录 UIN: {uin}")
        # 模拟 JWT token
        jwt = f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.{uin}.{device_id}"
        print(f"[Auth] 登录成功，获取 JWT")
        return jwt
    
    async def alloc_room(self, jwt_token: str) -> Optional[dict]:
        print("[Auth] 分配房间...")
        room_info = {
            "room_id": "room_12345",
            "game_server_ip": "cn-logic1.mini1.cn",
            "game_server_port": 4012
        }
        print(f"[Auth] 房间分配成功: {room_info['room_id']}")
        return room_info


class MNWConnection:
    """完整连接管理器"""
    
    def __init__(self):
        self.tcp = MNWTCPConnector()
        self.auth = MNWAuthClient()
        self.session: Optional[MNWSessionInfo] = None
    
    async def login(self, uin: str, password: str, device_id: str) -> bool:
        print("\n" + "=" * 50)
        print("开始登录流程")
        print("=" * 50)
        
        # Step 1: HTTPS 认证
        print("\n[Step 1] HTTPS 认证...")
        jwt_token = await self.auth.login(uin, password, device_id)
        if not jwt_token:
            print("✗ 认证失败")
            return False
        print("✓ 认证成功")
        
        # Step 2: 分配房间
        print("\n[Step 2] 分配房间...")
        room_info = await self.auth.alloc_room(jwt_token)
        if not room_info:
            print("✗ 房间分配失败")
            return False
        print("✓ 房间分配成功")
        
        # 创建会话
        self.session = MNWSessionInfo(
            jwt_token=jwt_token,
            uin=uin,
            device_id=device_id,
            room_id=room_info["room_id"],
            game_server_ip=room_info["game_server_ip"],
            game_server_port=room_info["game_server_port"]
        )
        
        # Step 3: TCP 连接
        print("\n[Step 3] TCP 连接...")
        if not await self.tcp.connect(
            self.session.game_server_ip,
            self.session.game_server_port
        ):
            print("✗ TCP 连接失败")
            return False
        print("✓ TCP 连接成功")
        
        # Step 4: 发送 LOGIN_REQ
        print("\n[Step 4] 发送 LOGIN_REQ...")
        await self._send_login_req()
        print("✓ LOGIN_REQ 发送成功")
        
        # Step 5: 接收 LOGIN_RESP
        print("\n[Step 5] 接收 LOGIN_RESP...")
        if not await self._receive_login_resp():
            print("✗ 登录响应失败")
            return False
        print("✓ 登录响应成功")
        
        print("\n" + "=" * 50)
        print("登录流程完成!")
        print("=" * 50)
        return True
    
    async def _send_login_req(self):
        """发送登录请求"""
        jwt_bytes = self.session.jwt_token.encode('utf-8')
        payload = struct.pack('>I', len(jwt_bytes)) + jwt_bytes
        await self.tcp.send_message(MNWMsgType.LOGIN_REQ, payload)
    
    async def _receive_login_resp(self) -> bool:
        """接收登录响应"""
        message = await self.tcp.receive_message()
        if not message:
            return False
        
        msg_type, data = message
        if msg_type != MNWMsgType.LOGIN_RESP:
            print(f"  意外的消息类型: {msg_type}")
            return False
        
        # 解析响应: result (4) + key_len (4) + session_key
        if len(data) < 8:
            print(f"  数据长度不足: {len(data)} bytes")
            return False
        
        result = struct.unpack('>I', data[:4])[0]
        if result != 0:
            print(f"  登录失败，错误码: {result}")
            return False
        
        key_len = struct.unpack('>I', data[4:8])[0]
        if len(data) < 8 + key_len:
            print(f"  session_key 长度不足")
            return False
        
        session_key = data[8:8+key_len]
        
        self.session.session_key = session_key
        self.session.crypto_enabled = True
        
        print(f"  获取 session_key: {session_key[:20]}...")
        print("  加密已激活")
        return True
    
    async def logout(self):
        print("\n[Logout] 登出...")
        await self.tcp.disconnect()
        self.session = None
        print("✓ 登出完成")


async def test_login_flow():
    print("\n" + "=" * 60)
    print("TCP 连接器登录流程测试")
    print("=" * 60)
    
    conn = MNWConnection()
    
    # 测试登录
    success = await conn.login(
        uin="2056826320",
        password="test_password",
        device_id="WIN9e40eedc04a71931ece88472bb778bc4"
    )
    
    if success:
        print("\n✓ 登录流程测试通过")
        
        # 验证会话信息
        print("\n会话信息:")
        print(f"  UIN: {conn.session.uin}")
        print(f"  Room ID: {conn.session.room_id}")
        print(f"  Game Server: {conn.session.game_server_ip}:{conn.session.game_server_port}")
        print(f"  Crypto Enabled: {conn.session.crypto_enabled}")
        print(f"  Session Key: {conn.session.session_key[:20]}...")
    else:
        print("\n✗ 登录流程测试失败")
    
    # 登出
    await conn.logout()
    
    return success


async def main():
    try:
        success = await test_login_flow()
        
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
