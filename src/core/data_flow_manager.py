#!/usr/bin/env python3
"""
数据流管理器
实现MC <-> MNW的端到端数据流转

Phase 3: 连接实现
Phase 4: 功能完善
"""

import asyncio
import json
import logging
from typing import Optional, Dict, List, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from codec.mc_codec import MinecraftCodec
from codec.mnw_codec import MiniWorldCodec
from protocol.block_mapper import BlockMapper
from protocol.coordinate_converter import CoordinateConverter, Vector3
from protocol.mnw_login import MiniWorldLogin, MiniWorldAccount

logger = logging.getLogger(__name__)


@dataclass
class DataFlowStats:
    """数据流统计"""
    mc_to_mnw_packets: int = 0
    mnw_to_mc_packets: int = 0
    mc_to_mnw_bytes: int = 0
    mnw_to_mc_bytes: int = 0
    errors: int = 0
    start_time: datetime = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()


class DataFlowManager:
    """
    数据流管理器
    
    处理双向数据流:
    MC Client -> Proxy -> Translator -> MNW Server
    MNW Server -> Translator -> Proxy -> MC Client
    """
    
    def __init__(self):
        # 编解码器
        self.mc_codec = MinecraftCodec()
        self.mnw_codec = MiniWorldCodec()
        
        # 映射器
        self.block_mapper = BlockMapper()
        self.coord_converter = CoordinateConverter()
        
        # 统计
        self.stats = DataFlowStats()
        
        # 回调
        self.mc_packet_callbacks: List[Callable] = []
        self.mnw_packet_callbacks: List[Callable] = []
        
        # 玩家映射
        self.player_mapping: Dict[str, str] = {}  # MC UUID -> MNW Account ID
        
        logger.info("数据流管理器初始化")
    
    async def process_mc_to_mnw(self, mc_packet: bytes) -> Optional[bytes]:
        """
        处理MC到MNW的数据包
        
        Phase 3: 连接实现
        
        Args:
            mc_packet: Minecraft原始数据包
            
        Returns:
            迷你世界数据包或None
        """
        try:
            # 解析MC数据包
            packet = self.mc_codec.decode_packet(mc_packet)
            if not packet:
                return None
            
            self.stats.mc_to_mnw_packets += 1
            self.stats.mc_to_mnw_bytes += len(mc_packet)
            
            # 根据包ID处理
            if packet.packet_id == 0x00:  # Handshake
                return await self._handle_mc_handshake(packet.data)
            elif packet.packet_id == 0x00:  # Login Start
                return await self._handle_mc_login(packet.data)
            elif packet.packet_id == 0x03:  # Chat Message
                return await self._handle_mc_chat(packet.data)
            elif packet.packet_id == 0x11:  # Player Position
                return await self._handle_mc_position(packet.data)
            elif packet.packet_id == 0x1B:  # Player Digging
                return await self._handle_mc_digging(packet.data)
            elif packet.packet_id == 0x1C:  # Block Place
                return await self._handle_mc_block_place(packet.data)
            else:
                # 未实现的包类型
                logger.debug(f"未处理的MC包类型: 0x{packet.packet_id:02X}")
                return None
                
        except Exception as e:
            logger.error(f"MC->MNW处理失败: {e}")
            self.stats.errors += 1
            return None
    
    async def process_mnw_to_mc(self, mnw_packet: bytes) -> Optional[bytes]:
        """
        处理MNW到MC的数据包
        
        Phase 3: 连接实现
        
        Args:
            mnw_packet: 迷你世界原始数据包
            
        Returns:
            Minecraft数据包或None
        """
        if not mnw_packet or len(mnw_packet) < 2:
            logger.warning("收到空的MNW数据包")
            return None
            
        try:
            # 解析MNW数据包
            packet = self.mnw_codec.decode_packet(mnw_packet, decrypt=False)
            if not packet:
                logger.debug("MNW数据包解析失败")
                return None
            
            self.stats.mnw_to_mc_packets += 1
            self.stats.mnw_to_mc_bytes += len(mnw_packet)
            
            # 根据包类型处理
            try:
                if packet.packet_type == 0x01:  # Login
                    return await self._handle_mnw_login(packet)
                elif packet.packet_type == 0x03:  # Chat
                    return await self._handle_mnw_chat(packet)
                elif packet.packet_type == 0x04:  # Move
                    return await self._handle_mnw_move(packet)
                elif packet.packet_type == 0x05:  # Block
                    return await self._handle_mnw_block(packet)
                else:
                    logger.debug(f"未处理的MNW包类型: 0x{packet.packet_type:02X}")
                    return None
            except Exception as handler_error:
                logger.error(f"处理MNW包类型 0x{packet.packet_type:02X} 时出错: {handler_error}")
                return None
                
        except Exception as e:
            logger.error(f"MNW->MC处理失败: {e}", exc_info=True)
            self.stats.errors += 1
            return None
    
    # Phase 3: MC -> MNW 处理函数
    
    async def _handle_mc_handshake(self, data: bytes) -> Optional[bytes]:
        """处理MC握手包"""
        # 握手包不需要转发到MNW
        logger.debug("MC握手包处理")
        return None
    
    async def _handle_mc_login(self, data: bytes) -> Optional[bytes]:
        """处理MC登录包"""
        try:
            from io import BytesIO
            from codec.mc_codec import decode_string
            
            stream = BytesIO(data)
            username = decode_string(stream)
            
            logger.info(f"MC玩家登录: {username}")
            
            # 创建MNW登录请求
            # TODO: 需要真实的MNW账号映射
            mnw_login = self.mnw_codec.create_login_request(
                account_id=username,  # 临时使用MC用户名
                token="temp_token"
            )
            
            return mnw_login
            
        except Exception as e:
            logger.error(f"处理MC登录失败: {e}")
            return None
    
    async def _handle_mc_chat(self, data: bytes) -> Optional[bytes]:
        """处理MC聊天包"""
        try:
            from io import BytesIO
            from codec.mc_codec import decode_string
            
            stream = BytesIO(data)
            message = decode_string(stream)
            
            logger.info(f"MC聊天: {message}")
            
            # 转换为MNW聊天包
            mnw_chat = self.mnw_codec.create_chat_message(
                message=message,
                room_id=""  # 当前房间
            )
            
            return mnw_chat
            
        except Exception as e:
            logger.error(f"处理MC聊天失败: {e}")
            return None
    
    async def _handle_mc_position(self, data: bytes) -> Optional[bytes]:
        """处理MC位置包"""
        try:
            import struct
            
            # 解析位置数据
            x = struct.unpack('>d', data[0:8])[0]
            y = struct.unpack('>d', data[8:16])[0]
            z = struct.unpack('>d', data[16:24])[0]
            
            # 坐标转换 (X轴取反)
            mc_pos = Vector3(x, y, z)
            mnw_pos = self.coord_converter.mc_to_mnw_position(mc_pos)
            
            logger.debug(f"MC位置: ({x:.2f}, {y:.2f}, {z:.2f}) -> MNW: ({mnw_pos.x:.2f}, {mnw_pos.y:.2f}, {mnw_pos.z:.2f})")
            
            # 创建MNW移动包
            mnw_move = self.mnw_codec.create_move_packet(
                x=mnw_pos.x,
                y=mnw_pos.y,
                z=mnw_pos.z
            )
            
            return mnw_move
            
        except Exception as e:
            logger.error(f"处理MC位置失败: {e}")
            return None
    
    async def _handle_mc_digging(self, data: bytes) -> Optional[bytes]:
        """处理MC挖掘包"""
        try:
            import struct
            from io import BytesIO
            
            stream = BytesIO(data)
            status = struct.unpack('B', stream.read(1))[0]
            
            if status != 2:  # 只处理完成挖掘
                return None
            
            # 解析位置 (简化版，不使用VarInt)
            # 位置数据在字节2-9 (8字节long)
            position_bytes = stream.read(8)
            if len(position_bytes) < 8:
                logger.warning("位置数据不足")
                return None
            
            position = struct.unpack('>q', position_bytes)[0]
            
            # 解码位置
            x = (position >> 38) & 0x3FFFFFF
            y = (position >> 26) & 0xFFF
            z = position & 0x3FFFFFF
            
            # 处理有符号数
            if x >= 2**25:
                x -= 2**26
            if y >= 2**11:
                y -= 2**12
            if z >= 2**25:
                z -= 2**26
            
            # 坐标转换
            mc_pos = Vector3(float(x), float(y), float(z))
            mnw_pos = self.coord_converter.mc_to_mnw_position(mc_pos)
            
            logger.debug(f"MC挖掘: ({x}, {y}, {z}) -> MNW: ({int(mnw_pos.x)}, {int(mnw_pos.y)}, {int(mnw_pos.z)})")
            
            # 创建MNW方块破坏包
            mnw_break = self.mnw_codec.create_block_break(
                x=int(mnw_pos.x),
                y=int(mnw_pos.y),
                z=int(mnw_pos.z)
            )
            
            return mnw_break
            
        except Exception as e:
            logger.error(f"处理MC挖掘失败: {e}")
            return None
    
    async def _handle_mc_block_place(self, data: bytes) -> Optional[bytes]:
        """处理MC方块放置包"""
        try:
            import struct
            from codec.mc_codec import decode_varint
            from io import BytesIO
            
            stream = BytesIO(data)
            
            # 解析位置
            position = decode_varint(stream)
            x = (position >> 38) & 0x3FFFFFF
            y = (position >> 26) & 0xFFF
            z = position & 0x3FFFFFF
            
            if x >= 2**25:
                x -= 2**26
            if y >= 2**11:
                y -= 2**12
            if z >= 2**25:
                z -= 2**26
            
            # TODO: 获取方块ID
            mc_block_id = 1  # 临时使用石头
            
            # 方块ID映射
            mnw_block_id, _ = self.block_mapper.mc_to_mnw_block(mc_block_id)
            
            # 坐标转换
            mc_pos = Vector3(float(x), float(y), float(z))
            mnw_pos = self.coord_converter.mc_to_mnw_position(mc_pos)
            
            logger.debug(f"MC放置: ({x}, {y}, {z}) ID={mc_block_id} -> MNW: ({int(mnw_pos.x)}, {int(mnw_pos.y)}, {int(mnw_pos.z)}) ID={mnw_block_id}")
            
            # 创建MNW方块放置包
            mnw_place = self.mnw_codec.create_block_place(
                x=int(mnw_pos.x),
                y=int(mnw_pos.y),
                z=int(mnw_pos.z),
                block_id=mnw_block_id
            )
            
            return mnw_place
            
        except Exception as e:
            logger.error(f"处理MC放置失败: {e}")
            return None
    
    # Phase 3: MNW -> MC 处理函数
    
    async def _handle_mnw_login(self, packet) -> Optional[bytes]:
        """处理MNW登录响应"""
        try:
            response = self.mnw_codec.parse_login_response(packet.data)
            
            if response.get("success"):
                logger.info(f"MNW登录成功: {response.get('nickname', 'Unknown')}")
                
                # TODO: 创建MC登录成功包
                # 暂时返回None
                return None
            else:
                logger.error(f"MNW登录失败: {response.get('error', 'Unknown')}")
                return None
                
        except Exception as e:
            logger.error(f"处理MNW登录失败: {e}")
            return None
    
    async def _handle_mnw_chat(self, packet) -> Optional[bytes]:
        """处理MNW聊天包"""
        try:
            chat_data = self.mnw_codec.parse_chat_message(packet.data)
            message = chat_data.get("message", "")
            
            logger.info(f"MNW聊天: {message}")
            
            # 创建MC聊天包 (使用系统消息格式)
            # MC系统消息格式: JSON字符串
            chat_json = json.dumps({
                "text": f"[MNW] {message}"
            })
            
            # 编码为MC数据包
            from codec.mc_codec import encode_string
            chat_data = encode_string(chat_json)
            
            # 使用系统消息包ID (0x0F = System Chat Message)
            mc_chat = self.mc_codec.encode_packet(0x0F, chat_data)
            
            return mc_chat
            
        except Exception as e:
            logger.error(f"处理MNW聊天失败: {e}")
            return None
    
    async def _handle_mnw_move(self, packet) -> Optional[bytes]:
        """处理MNW移动包"""
        try:
            move_data = self.mnw_codec.parse_move_data(packet.data)
            
            x = move_data.get("x", 0)
            y = move_data.get("y", 0)
            z = move_data.get("z", 0)
            yaw = move_data.get("yaw", 0.0)
            pitch = move_data.get("pitch", 0.0)
            
            # 坐标转换
            mnw_pos = Vector3(x, y, z)
            mc_pos = self.coord_converter.mnw_to_mc_position(mnw_pos)
            
            logger.debug(f"MNW移动: ({x:.2f}, {y:.2f}, {z:.2f}) -> MC: ({mc_pos.x:.2f}, {mc_pos.y:.2f}, {mc_pos.z:.2f})")
            
            # TODO: 创建MC位置更新包
            return None
            
        except Exception as e:
            logger.error(f"处理MNW移动失败: {e}")
            return None
    
    async def _handle_mnw_block(self, packet) -> Optional[bytes]:
        """处理MNW方块包"""
        try:
            block_data = self.mnw_codec.parse_block_data(packet.data)
            
            x = block_data.get("x", 0)
            y = block_data.get("y", 0)
            z = block_data.get("z", 0)
            block_id = block_data.get("block_id", 0)
            
            # 方块ID映射
            mc_block_id, _ = self.block_mapper.mnw_to_mc_block(block_id)
            
            # 坐标转换
            mnw_pos = Vector3(float(x), float(y), float(z))
            mc_pos = self.coord_converter.mnw_to_mc_position(mnw_pos)
            
            logger.debug(f"MNW方块: ({x}, {y}, {z}) ID={block_id} -> MC: ({int(mc_pos.x)}, {int(mc_pos.y)}, {int(mc_pos.z)}) ID={mc_block_id}")
            
            # TODO: 创建MC方块变更包
            return None
            
        except Exception as e:
            logger.error(f"处理MNW方块失败: {e}")
            return None
    
    # Phase 4: 高级功能
    
    async def sync_player_list(self, mc_players: List[Dict], mnw_players: List[Dict]):
        """
        同步玩家列表
        
        Phase 4: 功能完善
        """
        logger.info(f"同步玩家列表: MC={len(mc_players)}, MNW={len(mnw_players)}")
        
        # TODO: 实现玩家列表同步
        pass
    
    async def sync_world_state(self, mc_world: Dict, mnw_world: Dict):
        """
        同步世界状态
        
        Phase 4: 功能完善
        """
        logger.info("同步世界状态")
        
        # TODO: 实现世界状态同步
        # - 时间同步
        # - 天气同步
        # - 区块加载
        pass
    
    async def sync_inventory(self, mc_inventory: Dict, mnw_inventory: Dict):
        """
        同步背包
        
        Phase 4: 功能完善
        """
        logger.info("同步背包")
        
        # TODO: 实现背包同步
        pass
    
    def get_stats(self) -> Dict:
        """获取统计"""
        duration = datetime.now() - self.stats.start_time
        return {
            "uptime": str(duration),
            "mc_to_mnw_packets": self.stats.mc_to_mnw_packets,
            "mnw_to_mc_packets": self.stats.mnw_to_mc_packets,
            "mc_to_mnw_bytes": self.stats.mc_to_mnw_bytes,
            "mnw_to_mc_bytes": self.stats.mnw_to_mc_bytes,
            "total_packets": self.stats.mc_to_mnw_packets + self.stats.mnw_to_mc_packets,
            "total_bytes": self.stats.mc_to_mnw_bytes + self.stats.mnw_to_mc_bytes,
            "errors": self.stats.errors
        }


# 测试代码
if __name__ == "__main__":
    async def test():
        """测试数据流"""
        print("=" * 60)
        print("测试数据流管理器")
        print("=" * 60)
        
        manager = DataFlowManager()
        
        # 测试MC->MNW
        print("\n测试 MC -> MNW:")
        
        # 创建测试聊天包
        from codec.mc_codec import encode_string, encode_varint
        from io import BytesIO
        
        chat_data = encode_string("Hello, MiniWorld!")
        mc_chat = manager.mc_codec.encode_packet(0x03, chat_data)
        
        result = await manager.process_mc_to_mnw(mc_chat)
        if result:
            print(f"✅ 聊天包转换成功: {len(result)} bytes")
        else:
            print("⚠️ 聊天包未转换")
        
        # 测试位置转换
        print("\n测试位置转换:")
        import struct
        
        pos_data = struct.pack('>ddd', 100.0, 64.0, 200.0)  # x, y, z
        pos_data += struct.pack('>ff', 0.0, 0.0)  # yaw, pitch
        pos_data += b'\x01'  # on_ground
        
        mc_pos = manager.mc_codec.encode_packet(0x11, pos_data)
        result = await manager.process_mc_to_mnw(mc_pos)
        
        if result:
            print(f"✅ 位置包转换成功: {len(result)} bytes")
        else:
            print("⚠️ 位置包未转换")
        
        # 打印统计
        print("\n统计:")
        print(json.dumps(manager.get_stats(), indent=2))
    
    # 运行测试
    asyncio.run(test())
