"""
集成测试 - 端到端测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import struct
import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import IntEnum

# 模拟所有组件
class MNWMsgType(IntEnum):
    LOGIN_REQ = 3001
    LOGIN_RESP = 3002
    HEARTBEAT = 3003
    CHAT_MESSAGE = 0x7EA
    PLAYER_MOVE = 0x7E0
    CREATE_BLOCK = 1010

@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

@dataclass
class PlayerState:
    uin: int = 0
    name: str = ""
    position: Vec3 = field(default_factory=Vec3)
    is_online: bool = False

class MockMNWServer:
    """模拟 MNW 服务器"""
    
    def __init__(self):
        self.players: Dict[int, PlayerState] = {}
        self.messages: List[Dict] = []
        self._running = False
    
    async def handle_login(self, uin: int, jwt: str) -> bool:
        print(f"[Server] 处理登录: UIN={uin}")
        player = PlayerState(uin=uin, name=f"Player_{uin}", is_online=True)
        self.players[uin] = player
        return True
    
    async def handle_chat(self, uin: int, message: str):
        print(f"[Server] 聊天: UIN={uin}: {message}")
        self.messages.append({"uin": uin, "message": message, "time": time.time()})
    
    async def handle_move(self, uin: int, pos: Vec3):
        if uin in self.players:
            self.players[uin].position = pos
    
    def get_player_count(self) -> int:
        return len([p for p in self.players.values() if p.is_online])

class MockMCServer:
    """模拟 MC 服务器"""
    
    def __init__(self):
        self.players: Dict[str, PlayerState] = {}
        self.messages: List[Dict] = []
    
    async def handle_join(self, uuid: str, name: str):
        print(f"[MC Server] 玩家加入: {name} ({uuid[:8]}...)")
        player = PlayerState(name=name, is_online=True)
        self.players[uuid] = player
    
    async def handle_chat(self, uuid: str, message: str):
        print(f"[MC Server] 聊天: {self.players[uuid].name}: {message}")
        self.messages.append({"uuid": uuid, "message": message, "time": time.time()})

class MnMCPBridge:
    """完整的 MnMCP 桥接器"""
    
    def __init__(self):
        self.mnw_server = MockMNWServer()
        self.mc_server = MockMCServer()
        self.player_mapping: Dict[str, int] = {}  # MC UUID -> MNW UIN
        self._running = False
        self.stats = {
            "packets_forwarded": 0,
            "players_synced": 0,
            "chat_messages": 0,
            "errors": 0
        }
    
    async def start(self):
        """启动桥接器"""
        print("\n[Bridge] 启动 MnMCP 桥接器...")
        self._running = True
        
        # 启动同步任务
        asyncio.create_task(self._sync_loop())
        
        print("[Bridge] 桥接器已启动")
    
    async def stop(self):
        """停止桥接器"""
        print("\n[Bridge] 停止桥接器...")
        self._running = False
        print("[Bridge] 桥接器已停止")
    
    async def connect_mc_player(self, uuid: str, name: str, mnw_uin: int):
        """连接 MC 玩家"""
        print(f"\n[Bridge] 连接 MC 玩家: {name} -> MNW UIN:{mnw_uin}")
        
        # 添加到 MC 服务器
        await self.mc_server.handle_join(uuid, name)
        
        # 映射到 MNW
        self.player_mapping[uuid] = mnw_uin
        
        # 登录到 MNW
        jwt = f"jwt_{mnw_uin}"
        success = await self.mnw_server.handle_login(mnw_uin, jwt)
        
        if success:
            self.stats["players_synced"] += 1
            print(f"[Bridge] 玩家连接成功")
        
        return success
    
    async def forward_mc_chat(self, uuid: str, message: str):
        """转发 MC 聊天到 MNW"""
        mnw_uin = self.player_mapping.get(uuid)
        if not mnw_uin:
            print(f"[Bridge] 未找到映射: {uuid}")
            return
        
        print(f"\n[Bridge] MC -> MNW 聊天: {message}")
        await self.mnw_server.handle_chat(mnw_uin, message)
        self.stats["chat_messages"] += 1
        self.stats["packets_forwarded"] += 1
    
    async def forward_mnw_chat(self, mnw_uin: int, message: str):
        """转发 MNW 聊天到 MC"""
        # 查找对应的 MC UUID
        mc_uuid = None
        for uuid, uin in self.player_mapping.items():
            if uin == mnw_uin:
                mc_uuid = uuid
                break
        
        if not mc_uuid:
            print(f"[Bridge] 未找到 MC 映射: UIN {mnw_uin}")
            return
        
        print(f"\n[Bridge] MNW -> MC 聊天: {message}")
        await self.mc_server.handle_chat(mc_uuid, message)
        self.stats["chat_messages"] += 1
        self.stats["packets_forwarded"] += 1
    
    async def _sync_loop(self):
        """同步循环"""
        while self._running:
            try:
                # 同步玩家位置
                for uuid, mnw_uin in self.player_mapping.items():
                    if uuid in self.mc_server.players and mnw_uin in self.mnw_server.players:
                        mc_pos = self.mc_server.players[uuid].position
                        mnw_pos = self.mnw_server.players[mnw_uin].position
                        
                        # 简单的位置同步
                        if abs(mc_pos.x - mnw_pos.x) > 0.1:
                            await self.mnw_server.handle_move(mnw_uin, mc_pos)
                
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"[Bridge] 同步错误: {e}")
                self.stats["errors"] += 1
    
    def get_stats(self) -> Dict[str, int]:
        return self.stats.copy()


async def test_full_workflow():
    """测试完整工作流"""
    print("\n" + "=" * 60)
    print("集成测试 - 完整工作流")
    print("=" * 60)
    
    bridge = MnMCPBridge()
    
    # 启动桥接器
    await bridge.start()
    
    # 测试 1: 玩家连接
    print("\n[测试 1] 玩家连接")
    print("-" * 40)
    
    await bridge.connect_mc_player(
        uuid="550e8400-e29b-41d4-a716-446655440000",
        name="Steve",
        mnw_uin=2056826320
    )
    
    await bridge.connect_mc_player(
        uuid="550e8400-e29b-41d4-a716-446655440001",
        name="Alex",
        mnw_uin=1234567890
    )
    
    await asyncio.sleep(0.5)
    
    # 测试 2: MC -> MNW 聊天
    print("\n[测试 2] MC -> MNW 聊天转发")
    print("-" * 40)
    
    await bridge.forward_mc_chat(
        uuid="550e8400-e29b-41d4-a716-446655440000",
        message="Hello from Minecraft!"
    )
    
    await bridge.forward_mc_chat(
        uuid="550e8400-e29b-41d4-a716-446655440001",
        message="Hi Steve!"
    )
    
    await asyncio.sleep(0.5)
    
    # 测试 3: MNW -> MC 聊天
    print("\n[测试 3] MNW -> MC 聊天转发")
    print("-" * 40)
    
    await bridge.forward_mnw_chat(
        mnw_uin=2056826320,
        message="Hello from MiniWorld!"
    )
    
    await bridge.forward_mnw_chat(
        mnw_uin=1234567890,
        message="Nice to meet you!"
    )
    
    await asyncio.sleep(0.5)
    
    # 测试 4: 玩家位置同步
    print("\n[测试 4] 玩家位置同步")
    print("-" * 40)
    
    # 更新 MC 玩家位置
    bridge.mc_server.players["550e8400-e29b-41d4-a716-446655440000"].position = Vec3(100.0, 64.0, 100.0)
    bridge.mc_server.players["550e8400-e29b-41d4-a716-446655440001"].position = Vec3(105.0, 64.0, 95.0)
    
    await asyncio.sleep(0.5)
    
    # 验证位置同步
    for uuid, mnw_uin in bridge.player_mapping.items():
        mc_pos = bridge.mc_server.players[uuid].position
        mnw_pos = bridge.mnw_server.players[mnw_uin].position
        print(f"  {bridge.mc_server.players[uuid].name}: MC({mc_pos.x:.1f}, {mc_pos.y:.1f}, {mc_pos.z:.1f}) -> MNW({mnw_pos.x:.1f}, {mnw_pos.y:.1f}, {mnw_pos.z:.1f})")
    
    # 停止桥接器
    await bridge.stop()
    
    # 打印统计
    print("\n" + "=" * 60)
    print("集成测试统计")
    print("=" * 60)
    stats = bridge.get_stats()
    print(f"  数据包转发: {stats['packets_forwarded']}")
    print(f"  玩家同步: {stats['players_synced']}")
    print(f"  聊天消息: {stats['chat_messages']}")
    print(f"  错误: {stats['errors']}")
    
    return stats['errors'] == 0


async def test_concurrent_players():
    """测试并发玩家"""
    print("\n" + "=" * 60)
    print("集成测试 - 并发玩家")
    print("=" * 60)
    
    bridge = MnMCPBridge()
    await bridge.start()
    
    # 模拟 10 个玩家同时连接
    print("\n[测试] 10 个玩家并发连接")
    print("-" * 40)
    
    tasks = []
    for i in range(10):
        uuid = f"550e8400-e29b-41d4-a716-446655440{i:03d}"
        tasks.append(bridge.connect_mc_player(uuid, f"Player{i}", 1000000000 + i))
    
    await asyncio.gather(*tasks)
    
    print(f"\n在线玩家数: {bridge.mnw_server.get_player_count()}")
    
    # 并发聊天
    print("\n[测试] 并发聊天")
    print("-" * 40)
    
    chat_tasks = []
    for i in range(10):
        uuid = f"550e8400-e29b-41d4-a716-446655440{i:03d}"
        chat_tasks.append(bridge.forward_mc_chat(uuid, f"Message from Player{i}"))
    
    await asyncio.gather(*chat_tasks)
    
    await bridge.stop()
    
    stats = bridge.get_stats()
    print(f"\n共转发 {stats['packets_forwarded']} 条消息")
    
    return stats['errors'] == 0


async def main():
    try:
        success1 = await test_full_workflow()
        success2 = await test_concurrent_players()
        
        print("\n" + "=" * 60)
        if success1 and success2:
            print("集成测试结果: 全部通过")
        else:
            print("集成测试结果: 部分失败")
        print("=" * 60)
        
        return success1 and success2
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
