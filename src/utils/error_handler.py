#!/usr/bin/env python3
"""
错误处理模块 - Phase 5
统一的错误处理和恢复机制
"""

import logging
import traceback
from typing import Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """错误分类"""
    NETWORK = "network"           # 网络错误
    PROTOCOL = "protocol"         # 协议错误
    AUTHENTICATION = "auth"       # 认证错误
    CONFIGURATION = "config"      # 配置错误
    RESOURCE = "resource"         # 资源错误
    UNKNOWN = "unknown"           # 未知错误


class ErrorSeverity(Enum):
    """错误严重程度"""
    DEBUG = "debug"               # 调试信息
    INFO = "info"                 # 信息
    WARNING = "warning"           # 警告
    ERROR = "error"               # 错误
    CRITICAL = "critical"         # 严重错误


@dataclass
class ErrorContext:
    """错误上下文"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    exception: Optional[Exception] = None
    context: dict = None
    recoverable: bool = False
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


class MNWConnectionError(Exception):
    """迷你世界连接错误"""
    def __init__(self, message: str, recoverable: bool = True):
        super().__init__(message)
        self.recoverable = recoverable


class MCConnectionError(Exception):
    """Minecraft连接错误"""
    def __init__(self, message: str, recoverable: bool = True):
        super().__init__(message)
        self.recoverable = recoverable


class TranslationError(Exception):
    """协议翻译错误"""
    def __init__(self, message: str, packet_type: str = None):
        super().__init__(message)
        self.packet_type = packet_type


class AuthenticationError(Exception):
    """认证错误"""
    def __init__(self, message: str, error_code: int = None):
        super().__init__(message)
        self.error_code = error_code


class ConfigurationError(Exception):
    """配置错误"""
    pass


class ErrorHandler:
    """
    错误处理器
    
    功能:
    - 错误分类和记录
    - 错误恢复策略
    - 错误统计
    - 告警触发
    """
    
    def __init__(self):
        self.error_counts: dict = {cat: 0 for cat in ErrorCategory}
        self.error_handlers: dict = {}
        self.recovery_strategies: dict = {}
        self._alert_callback: Optional[Callable] = None
        
        # 注册默认恢复策略
        self._register_default_strategies()
        
        logger.info("错误处理器初始化完成")
    
    def _register_default_strategies(self):
        """注册默认恢复策略"""
        self.recovery_strategies[ErrorCategory.NETWORK] = self._recover_network
        self.recovery_strategies[ErrorCategory.PROTOCOL] = self._recover_protocol
        self.recovery_strategies[ErrorCategory.AUTHENTICATION] = self._recover_auth
    
    def handle(self, error: Exception, context: dict = None) -> ErrorContext:
        """
        处理错误
        
        Args:
            error: 异常对象
            context: 错误上下文
            
        Returns:
            ErrorContext: 错误上下文
        """
        # 分类错误
        error_ctx = self._classify_error(error, context)
        
        # 记录错误
        self._log_error(error_ctx)
        
        # 统计
        self.error_counts[error_ctx.category] += 1
        
        # 尝试恢复
        if error_ctx.recoverable:
            recovered = self._try_recover(error_ctx)
            if recovered:
                logger.info(f"错误已恢复: {error_ctx.message}")
                return error_ctx
        
        # 触发告警
        if error_ctx.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            self._trigger_alert(error_ctx)
        
        return error_ctx
    
    def _classify_error(self, error: Exception, context: dict = None) -> ErrorContext:
        """分类错误"""
        if context is None:
            context = {}
        
        # 根据异常类型分类
        if isinstance(error, MNWConnectionError):
            return ErrorContext(
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.ERROR if not error.recoverable else ErrorSeverity.WARNING,
                message=str(error),
                exception=error,
                context=context,
                recoverable=error.recoverable
            )
        
        elif isinstance(error, MCConnectionError):
            return ErrorContext(
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.ERROR if not error.recoverable else ErrorSeverity.WARNING,
                message=str(error),
                exception=error,
                context=context,
                recoverable=error.recoverable
            )
        
        elif isinstance(error, TranslationError):
            return ErrorContext(
                category=ErrorCategory.PROTOCOL,
                severity=ErrorSeverity.WARNING,
                message=str(error),
                exception=error,
                context=context,
                recoverable=True
            )
        
        elif isinstance(error, AuthenticationError):
            return ErrorContext(
                category=ErrorCategory.AUTHENTICATION,
                severity=ErrorSeverity.ERROR,
                message=str(error),
                exception=error,
                context=context,
                recoverable=False
            )
        
        elif isinstance(error, ConfigurationError):
            return ErrorContext(
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL,
                message=str(error),
                exception=error,
                context=context,
                recoverable=False
            )
        
        # 默认分类
        return ErrorContext(
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.ERROR,
            message=str(error),
            exception=error,
            context=context,
            recoverable=False
        )
    
    def _log_error(self, error_ctx: ErrorContext):
        """记录错误"""
        log_message = f"[{error_ctx.category.value.upper()}] {error_ctx.message}"
        
        if error_ctx.exception:
            log_message += f"\n{traceback.format_exc()}"
        
        if error_ctx.severity == ErrorSeverity.DEBUG:
            logger.debug(log_message)
        elif error_ctx.severity == ErrorSeverity.INFO:
            logger.info(log_message)
        elif error_ctx.severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        elif error_ctx.severity == ErrorSeverity.ERROR:
            logger.error(log_message)
        elif error_ctx.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
    
    def _try_recover(self, error_ctx: ErrorContext) -> bool:
        """尝试恢复错误"""
        strategy = self.recovery_strategies.get(error_ctx.category)
        
        if strategy:
            try:
                return strategy(error_ctx)
            except Exception as e:
                logger.error(f"恢复策略失败: {e}")
        
        return False
    
    def _recover_network(self, error_ctx: ErrorContext) -> bool:
        """网络错误恢复策略"""
        logger.info("尝试恢复网络连接...")
        # 这里可以实现重连逻辑
        return False
    
    def _recover_protocol(self, error_ctx: ErrorContext) -> bool:
        """协议错误恢复策略"""
        logger.info("尝试恢复协议状态...")
        # 这里可以实现协议重置逻辑
        return True
    
    def _recover_auth(self, error_ctx: ErrorContext) -> bool:
        """认证错误恢复策略"""
        logger.info("尝试重新认证...")
        # 这里可以实现重新认证逻辑
        return False
    
    def _trigger_alert(self, error_ctx: ErrorContext):
        """触发告警"""
        if self._alert_callback:
            try:
                self._alert_callback(error_ctx)
            except Exception as e:
                logger.error(f"告警回调失败: {e}")
    
    def on_alert(self, callback: Callable[[ErrorContext], None]):
        """注册告警回调"""
        self._alert_callback = callback
    
    def register_recovery_strategy(self, category: ErrorCategory, 
                                   strategy: Callable[[ErrorContext], bool]):
        """注册恢复策略"""
        self.recovery_strategies[category] = strategy
    
    def get_error_stats(self) -> dict:
        """获取错误统计"""
        return {
            "total": sum(self.error_counts.values()),
            "by_category": {cat.value: count for cat, count in self.error_counts.items()},
        }
    
    def reset_stats(self):
        """重置统计"""
        self.error_counts = {cat: 0 for cat in ErrorCategory}
        logger.info("错误统计已重置")


# 全局错误处理器
_global_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """获取全局错误处理器"""
    global _global_handler
    if _global_handler is None:
        _global_handler = ErrorHandler()
    return _global_handler


def set_error_handler(handler: ErrorHandler):
    """设置全局错误处理器"""
    global _global_handler
    _global_handler = handler


__all__ = [
    'ErrorHandler',
    'ErrorContext',
    'ErrorCategory',
    'ErrorSeverity',
    'MNWConnectionError',
    'MCConnectionError',
    'TranslationError',
    'AuthenticationError',
    'ConfigurationError',
    'get_error_handler',
    'set_error_handler',
]
