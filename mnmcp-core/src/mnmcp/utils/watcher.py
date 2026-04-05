"""
配置热加载系统
支持 YAML 配置文件修改后自动重载
"""

import time
import threading
from pathlib import Path
from typing import Callable, Optional, List
import watchdog.observers
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from .config import Config


class ConfigWatcher(FileSystemEventHandler):
    """
    配置文件监视器
    
    使用 watchdog 监视配置文件变化，自动重载
    
    Example:
        watcher = ConfigWatcher("config.yaml")
        watcher.on_reload = lambda cfg: print(f"Config reloaded: {cfg}")
        watcher.start()
        
        # 稍后...
        watcher.stop()
    """
    
    def __init__(self, config_path: str, cooldown: float = 1.0):
        """
        Args:
            config_path: 配置文件路径
            cooldown: 重载冷却时间（秒），防止频繁触发
        """
        super().__init__()
        self.config_path = Path(config_path).resolve()
        self.cooldown = cooldown
        self._last_reload = 0.0
        self._config: Optional[Config] = None
        self._observer: Optional[watchdog.observers.Observer] = None
        self._lock = threading.RLock()
        self._running = False
        
        # 回调函数
        self.on_reload: Optional[Callable[[Config], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
    
    @property
    def config(self) -> Optional[Config]:
        """获取当前配置（线程安全）"""
        with self._lock:
            return self._config
    
    def load(self) -> Config:
        """手动加载配置"""
        with self._lock:
            self._config = Config(str(self.config_path))
            self._config.load(str(self.config_path))
            self._last_reload = time.time()
            return self._config
    
    def on_modified(self, event):
        """watchdog 回调：文件修改"""
        if not isinstance(event, FileModifiedEvent):
            return
        
        # 检查是否是我们的配置文件
        modified = Path(event.src_path).resolve()
        if modified != self.config_path:
            return
        
        # 冷却检查
        now = time.time()
        if now - self._last_reload < self.cooldown:
            return
        
        try:
            cfg = self.load()
            if self.on_reload:
                self.on_reload(cfg)
        except Exception as e:
            if self.on_error:
                self.on_error(e)
    
    def start(self, blocking: bool = False) -> None:
        """启动监视器"""
        if self._running:
            return
        
        # 先加载一次配置
        self.load()
        
        # 启动 watchdog
        self._observer = watchdog.observers.Observer()
        self._observer.schedule(
            self,
            str(self.config_path.parent),
            recursive=False
        )
        self._observer.start()
        self._running = True
        
        if blocking:
            try:
                while self._running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                self.stop()
    
    def stop(self) -> None:
        """停止监视器"""
        if not self._running:
            return
        
        self._running = False
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None


class ConfigSection:
    """
    配置节包装器
    
    提供对嵌套配置的方便的属性访问，支持动态更新
    
    Example:
        server_cfg = ConfigSection(config, "server")
        print(server_cfg.host)  # 获取 server.host
        server_cfg._update()     # 从配置重新加载
    """
    
    def __init__(self, config: Config, section: str):
        self._config = config
        self._section = section
    
    def _update(self) -> None:
        """更新引用（配置重载后调用）"""
        # 重新获取（Config 是单例，自动更新）
        pass
    
    def __getattr__(self, name: str):
        """点分路径访问: cfg.server.host"""
        return self._config.get(f"{self._section}.{name}")
    
    def get(self, name: str, default=None):
        """安全获取"""
        return self._config.get(f"{self._section}.{name}", default)


# 全局配置管理器
_global_watcher: Optional[ConfigWatcher] = None
_global_lock = threading.Lock()


def setup_config_watcher(config_path: str, on_reload: Optional[Callable] = None) -> ConfigWatcher:
    """
    设置全局配置监视器
    
    Args:
        config_path: 配置文件路径
        on_reload: 重载回调函数
    
    Returns:
        ConfigWatcher 实例
    """
    global _global_watcher
    
    with _global_lock:
        if _global_watcher is not None:
            _global_watcher.stop()
        
        _global_watcher = ConfigWatcher(config_path)
        if on_reload:
            _global_watcher.on_reload = on_reload
        
        return _global_watcher


def get_config_watcher() -> Optional[ConfigWatcher]:
    """获取全局配置监视器"""
    return _global_watcher


def stop_config_watcher() -> None:
    """停止全局配置监视器"""
    global _global_watcher
    
    with _global_lock:
        if _global_watcher:
            _global_watcher.stop()
            _global_watcher = None
