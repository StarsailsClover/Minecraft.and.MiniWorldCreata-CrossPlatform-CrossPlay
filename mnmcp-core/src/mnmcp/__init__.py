"""MnMCP - Minecraft & MiniWorld Cross-Platform Protocol Engine"""

__version__ = "1.1.0_26w13a_Phase3"

from .protocol.mnw_protocol import MNWMsgType, MNWCodec
from .protocol import GameAction, UnifiedPacket, ProtocolTranslator
from .mapping import BlockMapper, EntityMapper, ItemMapper, CoordinateConverter
from .crypto import AESCipher, PasswordHasher, SessionCrypto
from .network import ProxyServer, RelayServer, SessionManager
from .utils import Config, StructuredLogger, setup_logging

__all__ = [
    # 版本
    "__version__",
    # 协议
    "MNWMsgType",
    "MNWCodec",
    "GameAction",
    "UnifiedPacket",
    "ProtocolTranslator",
    # 映射
    "BlockMapper",
    "EntityMapper",
    "ItemMapper",
    "CoordinateConverter",
    # 加密
    "AESCipher",
    "PasswordHasher",
    "SessionCrypto",
    # 网络
    "ProxyServer",
    "RelayServer",
    "SessionManager",
    # 工具
    "Config",
    "StructuredLogger",
    "setup_logging",
]
