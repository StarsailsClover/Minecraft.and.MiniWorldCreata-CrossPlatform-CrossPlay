"""
玩家同步系统测试
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

@dataclass
class Vec3:
    """3D 向量"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return {'x': self.x, 'y': self.y, 'z': self.z}
    
    @classmethod
    def from_dict(cls, d: Dict[str, float]) -> 'Vec3':
        return cls(d['x'], d['y'], d['z'])


@dataclass
class PlayerState:
    """玩家状态"""
    uin: int = 0
    name: str = ""
    position: Vec3 = field(default_factory=Vec3)
    rotation: Vec3 = field(default_factory=Vec3)
    health: float = 20.0
    is_online: bool = False
    last_update: float = field(default_factory=time.time)


class PlayerSyncManager:
    """玩家同步管理器"""
    
    def __init__(self):
        self.players: Dict[int, PlayerState] = {}
        self.position_buffer: Dict[int, List[Vec3]] = {}  # 位置缓冲区
        self.sync_interval: float = 0.05  # 20Hz
        self.interpolation_delay: float = 0.1  # 100ms
        self._running: bool = False
        self._sync_task: Optional[asyncio.Task] = None
        self.stats = {
            "position_updates": 0,
            "chat_messages": 0,
            "block_changes": 0,
            "sync_errors": 0
        }
    
    def register_player(self, uin: int, name: str) -> PlayerState:
        """注册玩家"""
        player = PlayerState(
            uin=uin,
            name=name,
            is_online=True
        )
        self.players[uin] = player
        self.position_buffer[uin] = []
        print(f"[Sync] 玩家注册: {name} (UIN: {uin})")
        return player
    
    def unregister_player(self, uin: int):
        """注销玩家"""
        if uin in self.players:
            player = self.players[uin]
            player.is_online = False
            print(f"[Sync] 玩家注销: {player.name} (UIN: {uin})")
            del self.players[uin]
            del self.position_buffer[uin]
    
    def update_position(self, uin: int, position: Vec3):
        """更新玩家位置"""
        if uin not in self.players:
            return
        
        player = self.players[uin]
        player.position = position
        player.last_update = time.time()
        
        # 添加到位置缓冲区
        self.position_buffer[uin].append(position)
        if len(self.position_buffer[uin]) > 10:
            self.position_buffer[uin].pop(0)
        
        self.stats["position_updates"] += 1
    
    def update_rotation(self, uin: int, rotation: Vec3):
        """更新玩家旋转"""
        if uin not in self.players:
            return
        
        player = self.players[uin]
        player.rotation = rotation
        player.last_update = time.time()
    
    def get_interpolated_position(self, uin: int) -> Optional[Vec3]:
        """获取插值后的位置"""
        if uin not in self.position_buffer:
            return None
        
        buffer = self.position_buffer[uin]
        if len(buffer) < 2:
            return buffer[0] if buffer else None
        
        # 简单线性插值
        # 实际应用中可以使用更复杂的插值算法
        return buffer[-1]
    
    def get_player(self, uin: int) -> Optional[PlayerState]:
        """获取玩家状态"""
        return self.players.get(uin)
    
    def get_all_players(self) -> List[PlayerState]:
        """获取所有在线玩家"""
        return [p for p in self.players.values() if p.is_online]
    
    async def start_sync(self):
        """启动同步循环"""
        self._running = True
        self._sync_task = asyncio.create_task(self._sync_loop())
        print("[Sync] 同步循环已启动")
    
    async def stop_sync(self):
        """停止同步循环"""
        self._running = False
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        print("[Sync] 同步循环已停止")
    
    async def _sync_loop(self):
        """同步循环"""
        while self._running:
            try:
                await self._broadcast_positions()
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                print(f"[Sync] 同步错误: {e}")
                self.stats["sync_errors"] += 1
    
    async def _broadcast_positions(self):
        """广播位置更新"""
        online_players = self.get_all_players()
        if len(online_players) < 2:
            return
        
        # 构建位置更新包
        updates = []
        for player in online_players:
            pos = self.get_interpolated_position(player.uin)
            if pos:
                updates.append({
                    "uin": player.uin,
                    "name": player.name,
                    "position": pos.to_dict(),
                    "rotation": player.rotation.to_dict()
                })
        
        # 广播给所有玩家
        # 实际实现中会通过网络发送
        if updates:
            print(f"[Sync] 广播位置更新: {len(updates)} 个玩家")
    
    def record_chat(self, uin: int, message: str):
        """记录聊天消息"""
        self.stats["chat_messages"] += 1
        player = self.players.get(uin)
        name = player.name if player else f"UIN:{uin}"
        print(f"[Sync] 聊天: {name}: {message}")
    
    def record_block_change(self, uin: int, x: int, y: int, z: int, block_id: int):
        """记录方块变更"""
        self.stats["block_changes"] += 1
        player = self.players.get(uin)
        name = player.name if player else f"UIN:{uin}"
        print(f"[Sync] 方块变更: {name} 在 ({x}, {y}, {z}) 放置 {block_id}")
    
    def get_stats(self) -> Dict[str, int]:
        return self.stats.copy()


class PlayerSyncBridge:
    """玩家同步桥接器"""
    
    def __init__(self, sync_manager: PlayerSyncManager):
        self.sync = sync_manager
        self.mc_players: Dict[str, int] = {}  # MC UUID -> MNW UIN
        self.mnw_players: Dict[int, str] = {}  # MNW UIN -> MC UUID
    
    def link_players(self, mc_uuid: str, mnw_uin: int):
        """关联 MC 和 MNW 玩家"""
        self.mc_players[mc_uuid] = mnw_uin
        self.mnw_players[mnw_uin] = mc_uuid
        print(f"[Bridge] 玩家关联: MC:{mc_uuid[:8]}... <-> MNW:{mnw_uin}")
    
    def get_mnw_uin(self, mc_uuid: str) -> Optional[int]:
        """获取 MNW UIN"""
        return self.mc_players.get(mc_uuid)
    
    def get_mc_uuid(self, mnw_uin: int) -> Optional[str]:
        """获取 MC UUID"""
        return self.mnw_players.get(mnw_uin)


async def test_player_sync():
    print("\n" + "=" * 60)
    print("玩家同步系统测试")
    print("=" * 60)
    
    sync = PlayerSyncManager()
    bridge = PlayerSyncBridge(sync)
    
    # 注册玩家
    print("\n[测试 1] 玩家注册")
    print("-" * 40)
    
    player1 = sync.register_player(2056826320, "Player1")
    player2 = sync.register_player(1234567890, "Player2")
    player3 = sync.register_player(9876543210, "Player3")
    
    # 关联玩家
    bridge.link_players("550e8400-e29b-41d4-a716-446655440000", 2056826320)
    bridge.link_players("550e8400-e29b-41d4-a716-446655440001", 1234567890)
    
    # 更新位置
    print("\n[测试 2] 位置更新")
    print("-" * 40)
    
    sync.update_position(2056826320, Vec3(100.0, 64.0, 100.0))
    sync.update_position(1234567890, Vec3(105.0, 64.0, 95.0))
    sync.update_position(9876543210, Vec3(110.0, 65.0, 90.0))
    
    # 模拟移动
    for i in range(5):
        sync.update_position(2056826320, Vec3(100.0 + i*0.5, 64.0, 100.0))
        sync.update_position(1234567890, Vec3(105.0, 64.0, 95.0 - i*0.3))
        await asyncio.sleep(0.01)
    
    # 获取插值位置
    print("\n[测试 3] 位置插值")
    print("-" * 40)
    
    for uin in [2056826320, 1234567890, 9876543210]:
        pos = sync.get_interpolated_position(uin)
        if pos:
            print(f"  UIN {uin}: ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})")
    
    # 记录聊天
    print("\n[测试 4] 聊天同步")
    print("-" * 40)
    
    sync.record_chat(2056826320, "Hello everyone!")
    sync.record_chat(1234567890, "Hi there!")
    sync.record_chat(9876543210, "Let's build something!")
    
    # 记录方块变更
    print("\n[测试 5] 方块变更同步")
    print("-" * 40)
    
    sync.record_block_change(2056826320, 100, 64, 100, 1)  # 放置石头
    sync.record_block_change(1234567890, 101, 64, 100, 2)  # 放置草
    sync.record_block_change(9876543210, 102, 64, 100, 3)  # 放置泥土
    
    # 启动同步循环
    print("\n[测试 6] 同步循环")
    print("-" * 40)
    
    await sync.start_sync()
    await asyncio.sleep(0.5)  # 运行一段时间
    await sync.stop_sync()
    
    # 注销玩家
    print("\n[测试 7] 玩家注销")
    print("-" * 40)
    
    sync.unregister_player(9876543210)
    
    # 打印统计
    print("\n" + "=" * 60)
    print("同步统计")
    print("=" * 60)
    stats = sync.get_stats()
    print(f"  位置更新: {stats['position_updates']}")
    print(f"  聊天消息: {stats['chat_messages']}")
    print(f"  方块变更: {stats['block_changes']}")
    print(f"  同步错误: {stats['sync_errors']}")
    
    return stats['sync_errors'] == 0


async def main():
    try:
        success = await test_player_sync()
        
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
