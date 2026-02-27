#!/usr/bin/env python3
"""
MnMCP 桥接服务启动器
整合 Java服务器 + MNW连接 + 协议翻译
"""

import asyncio
import sys
import signal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.java_server_manager import JavaServerManager, ServerConfig
from core.mnw_connection import MiniWorldConnection
from utils.logger import setup_logger
from utils.config_manager import ConfigManager

logger = setup_logger("MnMCP-Bridge")


class MnMCPBridge:
    """MnMCP桥接服务"""
    
    def __init__(self):
        self.config = ConfigManager("config.deploy.json")
        
        # Java服务器
        self.java_manager: JavaServerManager = None
        
        # MNW连接
        self.mnw_connection: MiniWorldConnection = None
        
        # 运行状态
        self.running = False
        
        logger.info("MnMCP桥接服务初始化")
    
    async def start(self):
        """启动桥接服务"""
        logger.info("=" * 70)
        logger.info(" MnMCP 桥接服务")
        logger.info(" Minecraft ↔ MiniWorld 全端互通")
        logger.info("=" * 70)
        
        try:
            # 1. 启动Java服务器
            await self._start_java_server()
            
            # 2. 连接MNW服务器
            await self._connect_mnw()
            
            # 3. 设置信号处理
            self._setup_signal_handlers()
            
            self.running = True
            
            logger.info("\n🚀 桥接服务启动完成！")
            logger.info("等待客户端连接...")
            logger.info("按 Ctrl+C 停止服务\n")
            
            # 保持运行
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"启动失败: {e}")
            await self.stop()
            raise
    
    async def _start_java_server(self):
        """启动Java服务器"""
        logger.info("\n[1/3] 启动Java服务器...")
        
        server_dir = Path("C:/MnMCP/server")
        
        config = ServerConfig(
            server_jar="paper-1.20.6-151.jar",
            min_memory="1G",
            max_memory="2G",
            server_port=25566,
            online_mode=False,
            motd="MnMCP Bridge Server",
            max_players=100
        )
        
        self.java_manager = JavaServerManager(server_dir, config)
        
        # 注册玩家回调
        self.java_manager.register_player_callback(self._on_java_player_event)
        
        if not await self.java_manager.start():
            raise RuntimeError("Java服务器启动失败")
        
        logger.info("✅ Java服务器启动成功")
    
    async def _connect_mnw(self):
        """连接迷你世界"""
        logger.info("\n[2/3] 连接迷你世界...")
        
        self.mnw_connection = MiniWorldConnection(region="CN")
        
        # 注册消息回调
        self.mnw_connection.register_message_callback(self._on_mnw_message)
        
        # 连接到游戏服务器
        if not await self.mnw_connection.connect_to_game():
            logger.warning("⚠️ 迷你世界连接失败（这是正常的，需要真实账号）")
            logger.info("提示: 需要先实现登录流程才能连接")
        else:
            logger.info("✅ 迷你世界连接成功")
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(sig, frame):
            logger.info(f"\n收到信号 {sig}")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _on_java_player_event(self, event: str, player):
        """处理Java服务器玩家事件"""
        logger.info(f"[Java] 玩家事件: {event}, 玩家: {player.username}")
        
        # TODO: 转发到MNW
        if event == "join":
            # 玩家加入，需要同步到MNW
            pass
        elif event == "leave":
            # 玩家离开
            pass
    
    def _on_mnw_message(self, msg_type: str, message: str):
        """处理MNW消息"""
        logger.info(f"[MNW] 消息: {msg_type}, 内容: {message}")
        
        # TODO: 转发到Java服务器
        pass
    
    async def stop(self):
        """停止桥接服务"""
        if not self.running:
            return
        
        logger.info("\n🛑 正在停止桥接服务...")
        self.running = False
        
        # 停止Java服务器
        if self.java_manager:
            await self.java_manager.stop()
        
        # 断开MNW连接
        if self.mnw_connection:
            await self.mnw_connection.disconnect()
        
        logger.info("\n✅ 桥接服务已停止")
    
    def get_stats(self) -> dict:
        """获取服务统计"""
        stats = {
            "running": self.running,
            "java_server": self.java_manager.get_stats() if self.java_manager else None,
            "mnw_connection": self.mnw_connection.get_stats() if self.mnw_connection else None
        }
        return stats


async def main():
    """主函数"""
    bridge = MnMCPBridge()
    
    try:
        await bridge.start()
    except KeyboardInterrupt:
        logger.info("\n收到键盘中断")
    except Exception as e:
        logger.error(f"运行时错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bridge.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"启动失败: {e}")
        sys.exit(1)
