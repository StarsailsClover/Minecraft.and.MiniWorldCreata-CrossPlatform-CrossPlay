#!/usr/bin/env python3
"""
性能监控器 - Phase 5
监控代理服务器的性能指标
"""

import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import deque
from statistics import mean, median

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: float
    latency_ms: float
    throughput_pps: float  # packets per second
    throughput_bps: float  # bytes per second
    memory_mb: float
    cpu_percent: float


class PerformanceMonitor:
    """
    性能监控器
    
    功能:
    - 实时监控延迟、吞吐量
    - 内存和CPU使用监控
    - 性能数据统计
    - 告警触发
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        
        # 统计计数器
        self.total_packets = 0
        self.total_bytes = 0
        self.start_time = time.time()
        
        # 告警阈值
        self.latency_threshold_ms = 100.0
        self.memory_threshold_mb = 500.0
        self.cpu_threshold_percent = 80.0
        
        # 告警回调
        self._alert_callbacks: List[callable] = []
        
        logger.info("性能监控器初始化完成")
    
    def record_packet(self, packet_size: int, latency_ms: float):
        """记录数据包处理"""
        self.total_packets += 1
        self.total_bytes += packet_size
        
        # 检查是否需要触发告警
        if latency_ms > self.latency_threshold_ms:
            self._trigger_alert(
                "high_latency",
                f"延迟过高: {latency_ms:.2f}ms > {self.latency_threshold_ms}ms"
            )
    
    def record_metrics(self, latency_ms: float, memory_mb: float, cpu_percent: float):
        """记录性能指标"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # 计算吞吐量
        throughput_pps = self.total_packets / elapsed if elapsed > 0 else 0
        throughput_bps = self.total_bytes / elapsed if elapsed > 0 else 0
        
        metrics = PerformanceMetrics(
            timestamp=current_time,
            latency_ms=latency_ms,
            throughput_pps=throughput_pps,
            throughput_bps=throughput_bps,
            memory_mb=memory_mb,
            cpu_percent=cpu_percent
        )
        
        self.metrics_history.append(metrics)
        
        # 检查告警
        if memory_mb > self.memory_threshold_mb:
            self._trigger_alert(
                "high_memory",
                f"内存使用过高: {memory_mb:.2f}MB > {self.memory_threshold_mb}MB"
            )
        
        if cpu_percent > self.cpu_threshold_percent:
            self._trigger_alert(
                "high_cpu",
                f"CPU使用过高: {cpu_percent:.2f}% > {self.cpu_threshold_percent}%"
            )
    
    def get_current_stats(self) -> Dict:
        """获取当前统计"""
        if not self.metrics_history:
            return {
                "status": "no_data",
                "message": "暂无性能数据"
            }
        
        latest = self.metrics_history[-1]
        
        return {
            "status": "ok",
            "current": {
                "latency_ms": round(latest.latency_ms, 2),
                "throughput_pps": round(latest.throughput_pps, 2),
                "throughput_mbps": round(latest.throughput_bps / 1024 / 1024, 2),
                "memory_mb": round(latest.memory_mb, 2),
                "cpu_percent": round(latest.cpu_percent, 2),
            },
            "totals": {
                "total_packets": self.total_packets,
                "total_mb": round(self.total_bytes / 1024 / 1024, 2),
                "uptime_seconds": round(time.time() - self.start_time, 2),
            }
        }
    
    def get_statistics(self, window_size: int = 100) -> Dict:
        """获取统计数据"""
        if len(self.metrics_history) < 2:
            return {"status": "insufficient_data"}
        
        # 获取最近window_size个数据点
        recent = list(self.metrics_history)[-window_size:]
        
        latencies = [m.latency_ms for m in recent]
        throughputs_pps = [m.throughput_pps for m in recent]
        throughputs_bps = [m.throughput_bps for m in recent]
        memories = [m.memory_mb for m in recent]
        cpus = [m.cpu_percent for m in recent]
        
        return {
            "status": "ok",
            "window_size": len(recent),
            "latency_ms": {
                "min": round(min(latencies), 2),
                "max": round(max(latencies), 2),
                "mean": round(mean(latencies), 2),
                "median": round(median(latencies), 2),
            },
            "throughput_pps": {
                "min": round(min(throughputs_pps), 2),
                "max": round(max(throughputs_pps), 2),
                "mean": round(mean(throughputs_pps), 2),
            },
            "throughput_mbps": {
                "min": round(min(throughputs_bps) / 1024 / 1024, 2),
                "max": round(max(throughputs_bps) / 1024 / 1024, 2),
                "mean": round(mean(throughputs_bps) / 1024 / 1024, 2),
            },
            "memory_mb": {
                "min": round(min(memories), 2),
                "max": round(max(memories), 2),
                "mean": round(mean(memories), 2),
            },
            "cpu_percent": {
                "min": round(min(cpus), 2),
                "max": round(max(cpus), 2),
                "mean": round(mean(cpus), 2),
            },
        }
    
    def on_alert(self, callback: callable):
        """注册告警回调"""
        self._alert_callbacks.append(callback)
    
    def _trigger_alert(self, alert_type: str, message: str):
        """触发告警"""
        logger.warning(f"[ALERT] {alert_type}: {message}")
        
        for callback in self._alert_callbacks:
            try:
                callback(alert_type, message)
            except Exception as e:
                logger.error(f"告警回调失败: {e}")
    
    def set_thresholds(self, latency_ms: float = None, memory_mb: float = None, 
                      cpu_percent: float = None):
        """设置告警阈值"""
        if latency_ms is not None:
            self.latency_threshold_ms = latency_ms
        if memory_mb is not None:
            self.memory_threshold_mb = memory_mb
        if cpu_percent is not None:
            self.cpu_threshold_percent = cpu_percent
        
        logger.info(f"告警阈值更新: 延迟={self.latency_threshold_ms}ms, "
                   f"内存={self.memory_threshold_mb}MB, "
                   f"CPU={self.cpu_threshold_percent}%")
    
    def reset_counters(self):
        """重置计数器"""
        self.total_packets = 0
        self.total_bytes = 0
        self.start_time = time.time()
        self.metrics_history.clear()
        logger.info("性能计数器已重置")


# 全局监控器实例
_global_monitor: Optional[PerformanceMonitor] = None


def get_monitor() -> PerformanceMonitor:
    """获取全局监控器"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def set_monitor(monitor: PerformanceMonitor):
    """设置全局监控器"""
    global _global_monitor
    _global_monitor = monitor


__all__ = [
    'PerformanceMonitor',
    'PerformanceMetrics',
    'get_monitor',
    'set_monitor',
]
