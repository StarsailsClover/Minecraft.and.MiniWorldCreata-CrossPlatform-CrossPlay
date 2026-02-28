#!/usr/bin/env python3
"""
配置加载器
支持YAML配置文件
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

# 尝试导入yaml
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None

logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """服务器配置"""
    mnw_host: str = "0.0.0.0"
    mnw_port: int = 8080
    mnw_use_ssl: bool = False
    mc_host: str = "127.0.0.1"
    mc_port: int = 19132
    max_clients: int = 100
    buffer_size: int = 65536
    timeout: float = 30.0


@dataclass
class AuthConfig:
    """认证配置"""
    mode: str = "offline"
    username: str = "MnMCP_User"
    password: str = ""


@dataclass
class MappingConfig:
    """映射配置"""
    block_table: str = "data/mnw_block_mapping_from_go.json"
    coordinate_scale: float = 1.0
    enable_coordinate_conversion: bool = True


@dataclass
class FeaturesConfig:
    """功能配置"""
    enable_translation: bool = True
    enable_compression: bool = False
    enable_encryption: bool = False
    enable_heartbeat: bool = True
    heartbeat_interval: float = 30.0


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    file: str = "logs/mnmcp.log"
    max_size: int = 10485760
    backup_count: int = 5
    console: bool = True
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class Config:
    """主配置"""
    server: ServerConfig = field(default_factory=ServerConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    mapping: MappingConfig = field(default_factory=MappingConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    @classmethod
    def from_yaml(cls, filepath: str) -> 'Config':
        """从YAML文件加载配置"""
        if not YAML_AVAILABLE:
            logger.warning("pyyaml未安装，使用默认配置")
            return cls()
        
        path = Path(filepath)
        
        if not path.exists():
            logger.warning(f"配置文件不存在: {filepath}，使用默认配置")
            return cls()
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                return cls()
            
            config = cls()
            
            # 加载服务器配置
            if 'server' in data:
                server_data = data['server']
                config.server = ServerConfig(
                    mnw_host=server_data.get('mnw_host', config.server.mnw_host),
                    mnw_port=server_data.get('mnw_port', config.server.mnw_port),
                    mnw_use_ssl=server_data.get('mnw_use_ssl', config.server.mnw_use_ssl),
                    mc_host=server_data.get('mc_host', config.server.mc_host),
                    mc_port=server_data.get('mc_port', config.server.mc_port),
                    max_clients=server_data.get('max_clients', config.server.max_clients),
                    buffer_size=server_data.get('buffer_size', config.server.buffer_size),
                    timeout=server_data.get('timeout', config.server.timeout),
                )
            
            # 加载认证配置
            if 'auth' in data:
                auth_data = data['auth']
                config.auth = AuthConfig(
                    mode=auth_data.get('mode', config.auth.mode),
                    username=auth_data.get('username', config.auth.username),
                    password=auth_data.get('password', config.auth.password),
                )
            
            # 加载映射配置
            if 'mapping' in data:
                mapping_data = data['mapping']
                config.mapping = MappingConfig(
                    block_table=mapping_data.get('block_table', config.mapping.block_table),
                    coordinate_scale=mapping_data.get('coordinate_scale', config.mapping.coordinate_scale),
                    enable_coordinate_conversion=mapping_data.get('enable_coordinate_conversion', config.mapping.enable_coordinate_conversion),
                )
            
            # 加载功能配置
            if 'features' in data:
                features_data = data['features']
                config.features = FeaturesConfig(
                    enable_translation=features_data.get('enable_translation', config.features.enable_translation),
                    enable_compression=features_data.get('enable_compression', config.features.enable_compression),
                    enable_encryption=features_data.get('enable_encryption', config.features.enable_encryption),
                    enable_heartbeat=features_data.get('enable_heartbeat', config.features.enable_heartbeat),
                    heartbeat_interval=features_data.get('heartbeat_interval', config.features.heartbeat_interval),
                )
            
            # 加载日志配置
            if 'logging' in data:
                logging_data = data['logging']
                config.logging = LoggingConfig(
                    level=logging_data.get('level', config.logging.level),
                    file=logging_data.get('file', config.logging.file),
                    max_size=logging_data.get('max_size', config.logging.max_size),
                    backup_count=logging_data.get('backup_count', config.logging.backup_count),
                    console=logging_data.get('console', config.logging.console),
                    format=logging_data.get('format', config.logging.format),
                )
            
            logger.info(f"从 {filepath} 加载配置成功")
            return config
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}，使用默认配置")
            return cls()    
    
    def to_proxy_config(self):
        """转换为代理配置"""
        try:
            from ..core.proxy_server_v2 import ProxyConfig
            
            return ProxyConfig(
                mnw_host=self.server.mnw_host,
                mnw_port=self.server.mnw_port,
                mnw_use_ssl=self.server.mnw_use_ssl,
                mc_host=self.server.mc_host,
                mc_port=self.server.mc_port,
                max_clients=self.server.max_clients,
                buffer_size=self.server.buffer_size,
                timeout=self.server.timeout,
                enable_translation=self.features.enable_translation,
                enable_compression=self.features.enable_compression,
                enable_encryption=self.features.enable_encryption,
                log_level=self.logging.level,
                log_file=self.logging.file,
            )
        except ImportError as e:
            logger.error(f"无法导入ProxyConfig: {e}")
            return None
    
    def save_yaml(self, filepath: str):
        """保存为YAML文件"""
        if not YAML_AVAILABLE:
            logger.error("pyyaml未安装，无法保存配置")
            return
        
        data = {
            'server': {
                'mnw_host': self.server.mnw_host,
                'mnw_port': self.server.mnw_port,
                'mnw_use_ssl': self.server.mnw_use_ssl,
                'mc_host': self.server.mc_host,
                'mc_port': self.server.mc_port,
                'max_clients': self.server.max_clients,
                'buffer_size': self.server.buffer_size,
                'timeout': self.server.timeout,
            },
            'auth': {
                'mode': self.auth.mode,
                'username': self.auth.username,
                'password': self.auth.password,
            },
            'mapping': {
                'block_table': self.mapping.block_table,
                'coordinate_scale': self.mapping.coordinate_scale,
                'enable_coordinate_conversion': self.mapping.enable_coordinate_conversion,
            },
            'features': {
                'enable_translation': self.features.enable_translation,
                'enable_compression': self.features.enable_compression,
                'enable_encryption': self.features.enable_encryption,
                'enable_heartbeat': self.features.enable_heartbeat,
                'heartbeat_interval': self.features.heartbeat_interval,
            },
            'logging': {
                'level': self.logging.level,
                'file': self.logging.file,
                'max_size': self.logging.max_size,
                'backup_count': self.logging.backup_count,
                'console': self.logging.console,
                'format': self.logging.format,
            },
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"配置已保存到: {filepath}")
    
    def to_proxy_config(self):
        """转换为代理配置"""
        from ..core.proxy_server_v2 import ProxyConfig
        
        return ProxyConfig(
            mnw_host=self.server.mnw_host,
            mnw_port=self.server.mnw_port,
            mnw_use_ssl=self.server.mnw_use_ssl,
            mc_host=self.server.mc_host,
            mc_port=self.server.mc_port,
            max_clients=self.server.max_clients,
            buffer_size=self.server.buffer_size,
            timeout=self.server.timeout,
            enable_translation=self.features.enable_translation,
            enable_compression=self.features.enable_compression,
            enable_encryption=self.features.enable_encryption,
            log_level=self.logging.level,
            log_file=self.logging.file,
        )
    
    def save_yaml(self, filepath: str):
        """保存为YAML文件"""
        data = {
            'server': {
                'mnw_host': self.server.mnw_host,
                'mnw_port': self.server.mnw_port,
                'mnw_use_ssl': self.server.mnw_use_ssl,
                'mc_host': self.server.mc_host,
                'mc_port': self.server.mc_port,
                'max_clients': self.server.max_clients,
                'buffer_size': self.server.buffer_size,
                'timeout': self.server.timeout,
            },
            'auth': {
                'mode': self.auth.mode,
                'username': self.auth.username,
                'password': self.auth.password,
            },
            'mapping': {
                'block_table': self.mapping.block_table,
                'coordinate_scale': self.mapping.coordinate_scale,
                'enable_coordinate_conversion': self.mapping.enable_coordinate_conversion,
            },
            'features': {
                'enable_translation': self.features.enable_translation,
                'enable_compression': self.features.enable_compression,
                'enable_encryption': self.features.enable_encryption,
                'enable_heartbeat': self.features.enable_heartbeat,
                'heartbeat_interval': self.features.heartbeat_interval,
            },
            'logging': {
                'level': self.logging.level,
                'file': self.logging.file,
                'max_size': self.logging.max_size,
                'backup_count': self.logging.backup_count,
                'console': self.logging.console,
                'format': self.logging.format,
            },
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"配置已保存到: {filepath}")


__all__ = [
    'Config',
    'ServerConfig',
    'AuthConfig',
    'MappingConfig',
    'FeaturesConfig',
    'LoggingConfig',
]
