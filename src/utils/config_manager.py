#!/usr/bin/env python3
"""
配置管理器
管理应用程序配置，支持JSON配置文件
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """配置管理器"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        "server": {
            "host": "0.0.0.0",
            "port": 25565,
            "max_connections": 100,
            "connection_timeout": 30
        },
        "miniworld": {
            "version": "1.53.1",
            "auth_host": "mwu-api-pre.mini1.cn",
            "auth_port": 443,
            "game_servers": [
                {"ip": "183.60.230.67", "provider": "腾讯云"},
                {"ip": "183.36.42.103", "provider": "腾讯云"},
                {"ip": "120.236.197.36", "provider": "移动云"}
            ]
        },
        "minecraft": {
            "version": "1.20.6",
            "protocol_version": 766
        },
        "logging": {
            "level": "INFO",
            "file": "logs/mnmcp.log",
            "max_size": "10MB",
            "backup_count": 5
        },
        "security": {
            "encryption_enabled": True,
            "aes_key_size": 128,
            "session_timeout": 3600
        },
        "features": {
            "auto_reconnect": True,
            "compression": True,
            "keep_alive": True
        }
    }
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config.json"
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        # 从默认配置开始
        self._config = self._deep_copy(self.DEFAULT_CONFIG)
        
        # 如果配置文件存在，合并配置
        config_file = Path(self.config_path)
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                self._merge_config(self._config, user_config)
                print(f"[+] 已加载配置文件: {self.config_path}")
            except Exception as e:
                print(f"[!] 加载配置文件失败: {e}, 使用默认配置")
        else:
            # 创建默认配置文件
            self._create_default_config()
            print(f"[+] 已创建默认配置文件: {self.config_path}")
    
    def _create_default_config(self):
        """创建默认配置文件"""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] 创建默认配置文件失败: {e}")
    
    def _merge_config(self, base: Dict, override: Dict):
        """递归合并配置"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _deep_copy(self, obj: Any) -> Any:
        """深拷贝对象"""
        import copy
        return copy.deepcopy(obj)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔（如 "server.port"）
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """保存配置到文件"""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            print(f"[+] 配置已保存到: {self.config_path}")
        except Exception as e:
            print(f"[!] 保存配置失败: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._deep_copy(self._config)
    
    def update(self, updates: Dict[str, Any]):
        """批量更新配置"""
        self._merge_config(self._config, updates)
