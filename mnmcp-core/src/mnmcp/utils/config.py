"""
MnMCP 统一日志与配置
v1.0.0_26w13a
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import yaml


# ─── 日志 ────────────────────────────────────────────────

_LOG_FORMAT = "%(asctime)s [%(name)-18s] %(levelname)-7s %(message)s"
_LOG_DATE = "%H:%M:%S"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """获取统一格式的 logger（幂等）"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, _LOG_DATE))
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


# ─── 配置 ────────────────────────────────────────────────

_DEFAULT_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "mc_port": 25565,
        "mnw_port": 19132,
        "ws_port": 8080,
        "api_port": 8081,
        "max_clients": 100,
        "timeout": 30.0,
    },
    "miniworld": {
        "version": "1.53.1",
        "region": "CN",
        "auth_servers": {
            "certification": "certification.mini1.cn:19921",
            "openroom": "openroom.mini1.cn:8080",
            "chatpush_alloc": "chatpush.mini1.cn:19601",
            "chatpush_gate": "chatpush.mini1.cn:19701",
            "community": "shequ.mini1.cn:8081",
        },
    },
    "minecraft": {
        "version": "1.20.6",
        "protocol_version": 766,
    },
    "crypto": {
        "cn_mode": "AES-128-CBC",
        "global_mode": "AES-256-GCM",
    },
    "relay": {
        "heartbeat_interval": 15.0,
        "session_timeout": 3600,
        "max_rooms": 100,
        "max_players_per_room": 40,
    },
    "logging": {
        "level": "INFO",
    },
}


class Config:
    """统一配置管理器（单例）"""

    _instance: Optional["Config"] = None
    _data: dict = {}

    def __new__(cls, path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = dict(_DEFAULT_CONFIG)
        return cls._instance

    def load(self, path: str) -> "Config":
        """从 YAML 文件加载配置（深度合并）"""
        p = Path(path)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                user = yaml.safe_load(f) or {}
            self._merge(self._data, user)
        return self

    @staticmethod
    def _merge(base: dict, override: dict):
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                Config._merge(base[k], v)
            else:
                base[k] = v

    def get(self, dotpath: str, default=None):
        """点分路径取值: config.get('server.mc_port')"""
        keys = dotpath.split(".")
        node = self._data
        for k in keys:
            if isinstance(node, dict) and k in node:
                node = node[k]
            else:
                return default
        return node

    def __getitem__(self, key: str):
        return self._data[key]

    def __repr__(self):
        return f"Config({list(self._data.keys())})"
