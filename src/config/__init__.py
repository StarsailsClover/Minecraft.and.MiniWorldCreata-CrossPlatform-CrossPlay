"""
配置模块
"""

from .servers import (
    MINIWORLD_SERVERS,
    get_game_server,
    get_api_server,
    get_https_servers,
    get_all_servers,
    ServerConfig,
)

__all__ = [
    'MINIWORLD_SERVERS',
    'get_game_server',
    'get_api_server',
    'get_https_servers',
    'get_all_servers',
    'ServerConfig',
]
