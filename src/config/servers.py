"""
服务器配置

从抓包分析获取的迷你世界服务器地址
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ServerConfig:
    """服务器配置"""
    host: str
    port: int
    protocol: str = "udp"
    description: str = ""


# 从抓包分析获取的服务器列表
MINIWORLD_SERVERS = {
    # 游戏服务器 (核心)
    "game": [
        ServerConfig("116.205.254.229", 19601, "udp", "游戏服务器 1"),
        ServerConfig("116.205.254.229", 19701, "udp", "游戏服务器 2"),
    ],
    
    # HTTP API 服务器
    "api": [
        ServerConfig("117.89.177.75", 8080, "http", "API 服务器 1"),
        ServerConfig("118.89.46.203", 8080, "http", "API 服务器 2"),
    ],
    
    # HTTPS 服务器 (腾讯云)
    "https": [
        ServerConfig("113.96.128.66", 443, "https", "腾讯云 1"),
        ServerConfig("113.96.128.68", 443, "https", "腾讯云 2"),
        ServerConfig("113.96.133.6", 443, "https", "腾讯云 3"),
        ServerConfig("113.96.142.2", 443, "https", "腾讯云 4"),
        ServerConfig("113.96.179.239", 443, "https", "腾讯云 5"),
        ServerConfig("113.96.179.240", 443, "https", "腾讯云 6"),
        ServerConfig("113.96.179.241", 443, "https", "腾讯云 7"),
        ServerConfig("113.96.179.242", 443, "https", "腾讯云 8"),
        ServerConfig("113.96.179.248", 443, "https", "腾讯云 9"),
        ServerConfig("113.105.138.18", 443, "https", "腾讯云 10"),
        ServerConfig("113.105.138.19", 443, "https", "腾讯云 11"),
        ServerConfig("113.105.138.50", 443, "https", "腾讯云 12"),
        ServerConfig("113.105.138.51", 443, "https", "腾讯云 13"),
        ServerConfig("113.105.156.190", 443, "https", "腾讯云 14"),
        ServerConfig("113.105.156.191", 443, "https", "腾讯云 15"),
        ServerConfig("116.205.254.245", 443, "https", "腾讯云 16"),
    ],
}


def get_game_server() -> ServerConfig:
    """获取游戏服务器 (优先返回第一个)"""
    return MINIWORLD_SERVERS["game"][0]


def get_api_server() -> ServerConfig:
    """获取 API 服务器"""
    return MINIWORLD_SERVERS["api"][0]


def get_https_servers() -> List[ServerConfig]:
    """获取所有 HTTPS 服务器"""
    return MINIWORLD_SERVERS["https"]


def get_all_servers() -> Dict[str, List[ServerConfig]]:
    """获取所有服务器"""
    return MINIWORLD_SERVERS
