"""
增强日志系统 - Phase 3 准备
支持: 文件轮转、JSON 格式、结构化日志
"""

import json
import logging
import logging.handlers
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import queue
import threading


class JSONFormatter(logging.Formatter):
    """JSON 格式日志 - 便于机器解析"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # 添加额外字段
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = traceback.format_exception(*record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


class AsyncHandler(logging.Handler):
    """
    异步日志处理器
    
    避免日志 IO 阻塞主线程
    """
    
    def __init__(self, handler: logging.Handler, max_queue: int = 10000):
        super().__init__()
        self._handler = handler
        self._queue = queue.Queue(maxsize=max_queue)
        self._thread = threading.Thread(target=self._process, daemon=True)
        self._thread.start()
        self._closed = False
    
    def _process(self) -> None:
        """后台处理线程"""
        while not self._closed:
            try:
                record = self._queue.get(timeout=0.1)
                if record is None:  # 关闭信号
                    break
                self._handler.emit(record)
            except queue.Empty:
                continue
            except Exception:
                pass  # 忽略处理错误
    
    def emit(self, record: logging.LogRecord) -> None:
        """提交日志到队列"""
        try:
            self._queue.put_nowait(record)
        except queue.Full:
            # 队列满，丢弃旧日志
            pass
    
    def close(self) -> None:
        """关闭处理器"""
        self._closed = True
        self._queue.put(None)
        self._thread.join(timeout=5.0)
        self._handler.close()
        super().close()


class StructuredLogger:
    """
    结构化日志包装器
    
    Example:
        logger = StructuredLogger("mnmcp.network")
        logger.info("Connection established", 
                   extra={"client_ip": "127.0.0.1", "port": 4012})
    """
    
    def __init__(self, name: str, extra: Optional[Dict[str, Any]] = None):
        self._logger = logging.getLogger(name)
        self._default_extra = extra or {}
    
    def _log(self, level: int, msg: str, 
            extra: Optional[Dict[str, Any]] = None,
            exc_info: bool = False) -> None:
        """内部日志方法"""
        merged_extra = {**self._default_extra}
        if extra:
            merged_extra.update(extra)
        
        # 创建 LogRecord
        record = self._logger.makeRecord(
            self._logger.name, level, "", 0, msg, (), None
        )
        record.extra = merged_extra
        
        if exc_info:
            record.exc_info = sys.exc_info()
        
        self._logger.handle(record)
    
    def debug(self, msg: str, **extra) -> None:
        self._log(logging.DEBUG, msg, extra or None)
    
    def info(self, msg: str, **extra) -> None:
        self._log(logging.INFO, msg, extra or None)
    
    def warning(self, msg: str, **extra) -> None:
        self._log(logging.WARNING, msg, extra or None)
    
    def error(self, msg: str, exc_info: bool = True, **extra) -> None:
        self._log(logging.ERROR, msg, extra or None, exc_info)
    
    def critical(self, msg: str, exc_info: bool = True, **extra) -> None:
        self._log(logging.CRITICAL, msg, extra or None, exc_info)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    async_mode: bool = True,
) -> None:
    """
    设置增强日志系统
    
    Args:
        level: 日志级别
        log_file: 日志文件路径
        json_format: 是否使用 JSON 格式
        max_bytes: 单个日志文件最大大小
        backup_count: 备份文件数量
        async_mode: 是否异步写入
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 格式化器
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(name)-20s] %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # 控制台处理器
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root_logger.addHandler(console)
    
    # 文件处理器
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        
        if async_mode:
            file_handler = AsyncHandler(file_handler)
        
        root_logger.addHandler(file_handler)


__all__ = [
    "JSONFormatter",
    "AsyncHandler",
    "StructuredLogger",
    "setup_logging",
]
