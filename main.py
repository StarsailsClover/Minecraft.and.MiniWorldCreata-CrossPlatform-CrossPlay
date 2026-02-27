#!/usr/bin/env python3
"""
MnMCP - Minecraft ↔ MiniWorld 跨平台联机代理
主入口文件

用法:
    python main.py --config config.json
    python main.py --host 0.0.0.0 --port 25565
"""

import asyncio
import argparse
import signal
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.proxy_server import ProxyServer
from core.session_manager import SessionManager
from utils.config_manager import ConfigManager
from utils.logger import setup_logger

logger = setup_logger("MnMCP")


class MnMCPApplication:
    """MnMCP 主应用类"""
    
    def __init__(self, config_path: str = None):
        self.config = ConfigManager(config_path)
        self.session_manager = SessionManager()
        self.proxy_server = None
        self.running = False
        
    async def start(self):
        """启动应用"""
        logger.info("=" * 60)
        logger.info("MnMCP - Minecraft ↔ MiniWorld 跨平台联机代理")
        logger.info("=" * 60)
        
        # 创建代理服务器
        self.proxy_server = ProxyServer(
            host=self.config.get("server.host", "0.0.0.0"),
            port=self.config.get("server.port", 25565),
            session_manager=self.session_manager,
            config=self.config
        )
        
        # 设置信号处理
        self._setup_signal_handlers()
        
        # 启动服务器
        self.running = True
        try:
            await self.proxy_server.start()
        except Exception as e:
            logger.error(f"服务器启动失败: {e}")
            self.running = False
            raise
    
    async def stop(self):
        """停止应用"""
        logger.info("正在关闭服务器...")
        self.running = False
        
        if self.proxy_server:
            await self.proxy_server.stop()
        
        logger.info("服务器已关闭")
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(sig, frame):
            logger.info(f"收到信号 {sig}, 准备关闭...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="MnMCP - Minecraft ↔ MiniWorld 跨平台联机代理"
    )
    parser.add_argument(
        "--config", "-c",
        default="config.json",
        help="配置文件路径 (默认: config.json)"
    )
    parser.add_argument(
        "--host", "-H",
        default="0.0.0.0",
        help="监听地址 (默认: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=25565,
        help="监听端口 (默认: 25565)"
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="启用调试模式"
    )
    return parser.parse_args()


async def main():
    """主函数"""
    args = parse_args()
    
    # 创建应用实例
    app = MnMCPApplication(config_path=args.config)
    
    # 命令行参数覆盖配置
    if args.host:
        app.config.set("server.host", args.host)
    if args.port:
        app.config.set("server.port", args.port)
    if args.debug:
        app.config.set("logging.level", "DEBUG")
    
    # 启动应用
    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("收到键盘中断")
    finally:
        await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
