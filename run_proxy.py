#!/usr/bin/env python3
"""
代理服务器启动脚本
简化版，用于测试
"""

import sys
import asyncio
import signal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.proxy_server import ProxyServer
from core.session_manager import SessionManager
from core.protocol_translator import ProtocolTranslator
from utils.config_manager import ConfigManager
from utils.logger import setup_logger

logger = setup_logger("ProxyRunner")


class ProxyRunner:
    """代理服务器运行器"""
    
    def __init__(self):
        self.config = ConfigManager("config.json")
        self.session_manager = SessionManager()
        self.translator = ProtocolTranslator(region="CN")
        self.server = None
        self.running = False
        
    async def start(self):
        """启动代理服务器"""
        logger.info("=" * 70)
        logger.info(" MnMCP 代理服务器")
        logger.info(" Minecraft ↔ MiniWorld 跨平台联机代理")
        logger.info("=" * 70)
        
        host = self.config.get("server.host", "0.0.0.0")
        port = self.config.get("server.port", 25565)
        
        logger.info(f"配置加载完成: {self.config.config_path}")
        logger.info(f"监听地址: {host}:{port}")
        logger.info(f"方块映射: {self.translator.block_mapper.get_stats()}")
        
        # 创建代理服务器
        self.server = ProxyServer(
            host=host,
            port=port,
            session_manager=self.session_manager,
            config=self.config
        )
        
        # 设置信号处理
        self._setup_signal_handlers()
        
        # 启动服务器
        self.running = True
        logger.info("\n🚀 启动代理服务器...")
        logger.info("等待 Minecraft 客户端连接...")
        logger.info("按 Ctrl+C 停止服务器\n")
        
        try:
            await self.server.start()
        except Exception as e:
            logger.error(f"服务器启动失败: {e}")
            self.running = False
            raise
    
    async def stop(self):
        """停止代理服务器"""
        if not self.running:
            return
            
        logger.info("\n🛑 正在停止代理服务器...")
        self.running = False
        
        if self.server:
            await self.server.stop()
        
        # 打印统计
        stats = self.server.get_stats() if self.server else {}
        logger.info(f"\n服务器统计:")
        logger.info(f"  总连接数: {stats.get('total_connections', 0)}")
        logger.info(f"  活跃连接: {stats.get('active_connections', 0)}")
        logger.info(f"  翻译包数: {self.translator.packets_translated}")
        
        logger.info("\n✅ 代理服务器已停止")
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(sig, frame):
            logger.info(f"\n收到信号 {sig}")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """主函数"""
    runner = ProxyRunner()
    
    try:
        await runner.start()
    except KeyboardInterrupt:
        logger.info("\n收到键盘中断")
    finally:
        await runner.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"运行时错误: {e}")
        sys.exit(1)
