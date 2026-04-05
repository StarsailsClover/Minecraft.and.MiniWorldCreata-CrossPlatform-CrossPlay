"""
错误处理

统一的错误处理机制
"""

import logging
import traceback
from typing import Optional, Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)


class MnMCPError(Exception):
    """MnMCP 基础异常"""
    
    def __init__(self, message: str, code: int = 0, details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class ConnectionError(MnMCPError):
    """连接错误"""
    pass


class AuthenticationError(MnMCPError):
    """认证错误"""
    pass


class ProtocolError(MnMCPError):
    """协议错误"""
    pass


class EncryptionError(MnMCPError):
    """加密错误"""
    pass


class RoomError(MnMCPError):
    """房间错误"""
    pass


def handle_error(func: Callable) -> Callable:
    """错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except MnMCPError as e:
            logger.error(f"MnMCP Error in {func.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            logger.error(traceback.format_exc())
            raise MnMCPError(f"Unexpected error: {e}", code=-1)
    
    return wrapper


def safe_call(func: Callable, *args, default=None, **kwargs) -> Any:
    """安全调用函数"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Safe call failed for {func.__name__}: {e}")
        return default


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.error_callbacks: dict = {}
        self.error_count: dict = {}
    
    def register_callback(self, error_type: type, callback: Callable):
        """注册错误回调"""
        self.error_callbacks[error_type] = callback
    
    def handle(self, error: Exception) -> bool:
        """处理错误"""
        error_type = type(error)
        
        # 记录错误
        self.error_count[error_type.__name__] = self.error_count.get(error_type.__name__, 0) + 1
        
        # 调用回调
        if error_type in self.error_callbacks:
            try:
                self.error_callbacks[error_type](error)
                return True
            except Exception as e:
                logger.error(f"Error callback failed: {e}")
        
        return False
    
    def get_error_stats(self) -> dict:
        """获取错误统计"""
        return dict(self.error_count)


# 全局错误处理器
global_error_handler = ErrorHandler()


def setup_exception_hook():
    """设置全局异常钩子"""
    def exception_hook(exc_type, exc_value, exc_traceback):
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        # 调用原始钩子
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    import sys
    sys.excepthook = exception_hook
