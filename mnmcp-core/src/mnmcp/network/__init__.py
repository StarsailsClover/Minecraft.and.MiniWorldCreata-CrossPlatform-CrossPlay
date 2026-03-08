"""
MnMCP 网络层
v1.0.0_26w13a

统一的代理服务器 + 中继 + 会话 + 桥接

合并自旧项目 (消除 3 套重复实现):
  core/proxy_server.py + proxy_server_v2.py + local_proxy.py → proxy.py (本文件)
  core/bridge_integrated.py + bridge_v2.py → bridge (本文件)
  core/session_manager.py + multiplayer/common/session.py → session (本文件)
  multiplayer/streamer/relay_server.py → relay (本文件)
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Callable, Any, List

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
#  会话管理 (统一)
# ═══════════════════════════════════════════════════════════

class Platform(Enum):
    MC_JAVA = "mc_java"
    MC_BEDROCK = "mc_bedrock"
    MNW_CN_MOBILE = "mnw_cn_mobile"
    MNW_CN_PC = "mnw_cn_pc"
    MNW_GLOBAL = "mnw_global"


class SessionState(Enum):
    CONNECTING = "connecting"
    AUTHENTICATING = "authenticating"
    CONNECTED = "connected"
    IN_GAME = "in_game"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class PlayerSession:
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    player_name: str = ""
    player_uuid: str = ""
    platform: Platform = Platform.MC_JAVA
    state: SessionState = SessionState.CONNECTING

    # 网络
    remote_addr: str = ""
    remote_port: int = 0
    transport: Any = None

    # 时间
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)

    # 统计
    packets_sent: int = 0
    packets_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0

    # 游戏
    x: float = 0.0
    y: float = 64.0
    z: float = 0.0
    health: float = 20.0
    game_mode: int = 0

    def touch(self):
        self.last_activity = time.time()

    def is_timeout(self, timeout: float = 30.0) -> bool:
        return (time.time() - self.last_activity) > timeout


class SessionManager:
    """统一会话管理器"""

    def __init__(self, *, max_sessions: int = 100, timeout: float = 30.0):
        self._sessions: Dict[str, PlayerSession] = {}
        self.max_sessions = max_sessions
        self.timeout = timeout

    async def create(self, *, platform: Platform, addr: str = "", port: int = 0,
                     transport: Any = None) -> PlayerSession:
        if len(self._sessions) >= self.max_sessions:
            raise RuntimeError(f"会话数已达上限 ({self.max_sessions})")
        session = PlayerSession(platform=platform, remote_addr=addr,
                                remote_port=port, transport=transport)
        self._sessions[session.session_id] = session
        logger.info("新会话: %s (%s) %s:%d", session.session_id, platform.value, addr, port)
        return session

    def get(self, session_id: str) -> Optional[PlayerSession]:
        return self._sessions.get(session_id)

    def remove(self, session_id: str):
        s = self._sessions.pop(session_id, None)
        if s:
            logger.info("移除会话: %s (%s)", s.session_id, s.player_name or "unnamed")

    def all(self) -> List[PlayerSession]:
        return list(self._sessions.values())

    @property
    def count(self) -> int:
        return len(self._sessions)

    async def cleanup_expired(self):
        expired = [sid for sid, s in self._sessions.items() if s.is_timeout(self.timeout)]
        for sid in expired:
            self.remove(sid)
        if expired:
            logger.info("清理 %d 个过期会话", len(expired))


# ═══════════════════════════════════════════════════════════
#  代理服务器 (统一)
# ═══════════════════════════════════════════════════════════

class ProxyState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ProxyConfig:
    host: str = "0.0.0.0"
    mc_port: int = 25565
    mnw_port: int = 19132
    ws_port: int = 8080
    max_clients: int = 100
    buffer_size: int = 65536
    timeout: float = 30.0
    enable_translation: bool = True
    enable_encryption: bool = False


class ProxyServer:
    """
    统一代理服务器

    同时监听:
      - MC TCP (mc_port)
      - MNW WebSocket (ws_port)

    数据流:
      MC Client ←TCP→ Proxy ←WS→ MNW Client/Server
    """

    def __init__(self, config: ProxyConfig | None = None):
        self.config = config or ProxyConfig()
        self.state = ProxyState.STOPPED
        self.sessions = SessionManager(
            max_sessions=self.config.max_clients,
            timeout=self.config.timeout,
        )
        self._mc_server: Optional[asyncio.Server] = None
        self._translator = None  # 延迟初始化

    def _get_translator(self):
        if self._translator is None and self.config.enable_translation:
            from ..protocol import ProtocolTranslator
            self._translator = ProtocolTranslator()
        return self._translator

    async def start(self):
        """启动代理服务器"""
        self.state = ProxyState.STARTING
        logger.info("MnMCP Proxy 启动中...")
        logger.info("  MC  端口: %s:%d", self.config.host, self.config.mc_port)
        logger.info("  WS  端口: %s:%d", self.config.host, self.config.ws_port)

        # MC TCP 监听
        self._mc_server = await asyncio.start_server(
            self._handle_mc_client,
            self.config.host,
            self.config.mc_port,
        )

        self.state = ProxyState.RUNNING
        logger.info("MnMCP Proxy 已启动")

        # 启动心跳清理
        asyncio.create_task(self._heartbeat_loop())

        async with self._mc_server:
            await self._mc_server.serve_forever()

    async def stop(self):
        self.state = ProxyState.STOPPING
        if self._mc_server:
            self._mc_server.close()
            await self._mc_server.wait_closed()
        self.state = ProxyState.STOPPED
        logger.info("MnMCP Proxy 已停止")

    async def _handle_mc_client(self, reader: asyncio.StreamReader,
                                 writer: asyncio.StreamWriter):
        peer = writer.get_extra_info("peername")
        addr, port = peer if peer else ("?", 0)
        session = await self.sessions.create(
            platform=Platform.MC_BEDROCK, addr=addr, port=port, transport=writer,
        )
        try:
            while True:
                data = await asyncio.wait_for(
                    reader.read(self.config.buffer_size),
                    timeout=self.config.timeout,
                )
                if not data:
                    break
                session.touch()
                session.packets_received += 1
                session.bytes_received += len(data)

                # 翻译
                translator = self._get_translator()
                if translator:
                    translated = translator.mc_to_mnw(data)
                    if translated:
                        session.packets_sent += 1
                        session.bytes_sent += len(translated)
                        # TODO: 转发到 MNW 连接
        except asyncio.TimeoutError:
            logger.debug("MC 客户端超时: %s", session.session_id)
        except Exception as e:
            logger.error("MC 客户端错误: %s — %s", session.session_id, e)
        finally:
            writer.close()
            self.sessions.remove(session.session_id)

    async def _heartbeat_loop(self):
        while self.state == ProxyState.RUNNING:
            await asyncio.sleep(15)
            await self.sessions.cleanup_expired()


# ═══════════════════════════════════════════════════════════
#  中继服务器
# ═══════════════════════════════════════════════════════════

@dataclass
class Room:
    room_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    name: str = ""
    host_id: str = ""
    game_mode: str = "creative"
    max_players: int = 40
    players: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


class RelayServer(ProxyServer):
    """
    中继服务器 (继承 ProxyServer)

    额外功能:
      - 房间管理
      - 多客户端广播
      - 跨平台消息转发
    """

    def __init__(self, config: ProxyConfig | None = None):
        super().__init__(config)
        self._rooms: Dict[str, Room] = {}

    def create_room(self, name: str, host_id: str, **kwargs) -> Room:
        room = Room(name=name, host_id=host_id, **kwargs)
        self._rooms[room.room_id] = room
        logger.info("创建房间: %s (%s)", room.room_id, name)
        return room

    def get_room(self, room_id: str) -> Optional[Room]:
        return self._rooms.get(room_id)

    def list_rooms(self) -> List[Room]:
        return list(self._rooms.values())

    def delete_room(self, room_id: str):
        room = self._rooms.pop(room_id, None)
        if room:
            logger.info("删除房间: %s (%s)", room.room_id, room.name)
