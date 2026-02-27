#!/usr/bin/env python3
"""
MnMCP 集成桥接器
整合所有组件实现端到端连接

由于Java版本限制，使用纯Python代理模式
"""

import asyncio
import json
import logging
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.proxy_server import ProxyServer, ProxyConnection
from core.protocol_translator import ProtocolTranslator
from core.mnw_connection import MiniWorldConnection
from protocol.mnw_login import MiniWorldLogin, MiniWorldAccount
from utils.logger import setup_logger
from utils.config_manager import ConfigManager

logger = setup_logger("MnMCP-Integrated")


@dataclass
class BridgeStats:
    """桥接统计"""
    start_time: datetime
    mc_connections: int = 0
    mnw_connections: int = 0
    packets_translated: int = 0
    errors: int = 0


class MnMCPIntegratedBridge:
    """
    MnMCP集成桥接器
    
    架构:
    Minecraft Client -> Proxy Server -> Protocol Translator -> MNW Connection -> MiniWorld Server
    """
    
    def __init__(self):
        self.config = ConfigManager("config.deploy.json")
        
        # 组件
        self.proxy: Optional[ProxyServer] = None
        self.translator: Optional[ProtocolTranslator] = None
        self.mnw_conn: Optional[MiniWorldConnection] = None
        self.mnw_login: Optional[MiniWorldLogin] = None
        
        # 状态
        self.running = False
        self.stats = BridgeStats(start_time=datetime.now())
        
        # 回调
        self.mc_player_callbacks: List[Callable] = []
        self.mnw_message_callbacks: List[Callable] = []
        
        logger.info("=" * 70)
        logger.info(" MnMCP 集成桥接器")
        logger.info(" Minecraft ↔ MiniWorld 全端互通")
        logger.info("=" * 70)
    
    async def start(self):
        """启动桥接器"""
        try:
            # 1. 初始化协议翻译器
            logger.info("\n[1/4] 初始化协议翻译器...")
            self.translator = ProtocolTranslator(region="CN")
            logger.info("✅ 协议翻译器初始化完成")
            
            # 2. 初始化MNW连接
            logger.info("\n[2/4] 初始化迷你世界连接...")
            self.mnw_conn = MiniWorldConnection(region="CN")
            self.mnw_login = MiniWorldLogin(region="CN")
            
            # 注册MNW消息回调
            self.mnw_conn.register_message_callback(self._on_mnw_message)
            logger.info("✅ 迷你世界连接初始化完成")
            
            # 3. 启动代理服务器
            logger.info("\n[3/4] 启动代理服务器...")
            host = self.config.get("server.host", "0.0.0.0")
            port = self.config.get("server.port", 25565)
            
            self.proxy = ProxyServer(
                host=host,
                port=port,
                translator=self.translator
            )
            
            # 设置信号处理
            import signal
            def signal_handler(sig, frame):
                logger.info(f"\n收到信号 {sig}")
                asyncio.create_task(self.stop())
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            self.running = True
            
            logger.info("✅ 代理服务器启动完成")
            logger.info(f"   监听: {host}:{port}")
            
            # 4. 启动MNW连接
            logger.info("\n[4/4] 连接迷你世界服务器...")
            if await self._connect_mnw():
                logger.info("✅ 迷你世界连接成功")
            else:
                logger.warning("⚠️ 迷你世界连接失败（需要真实账号）")
            
            logger.info("\n" + "=" * 70)
            logger.info(" 🚀 桥接器启动完成！")
            logger.info("=" * 70)
            logger.info("等待Minecraft客户端连接...")
            logger.info("配置Minecraft连接到: localhost:25565")
            logger.info("按 Ctrl+C 停止服务\n")
            
            # 启动代理服务器（阻塞）
            await self.proxy.start()
            
        except Exception as e:
            logger.error(f"启动失败: {e}")
            await self.stop()
            raise
    
    async def _connect_mnw(self) -> bool:
        """连接迷你世界"""
        try:
            # 连接到游戏服务器
            if not await self.mnw_conn.connect_to_game():
                return False
            
            # 尝试登录（使用测试账号）
            account = MiniWorldAccount(
                account_id="test_account",
                password="test_password",
                nickname="TestPlayer"
            )
            
            login_response = await self.mnw_login.login(account)
            
            if login_response.success:
                logger.info(f"登录成功: {login_response.nickname}")
                return True
            else:
                logger.warning(f"登录失败: {login_response.error_message}")
                return False
                
        except Exception as e:
            logger.error(f"连接MNW失败: {e}")
            return False
    
    def _on_mnw_message(self, msg_type: str, message: str):
        """处理MNW消息"""
        logger.info(f"[MNW] {msg_type}: {message}")
        
        # 转发到MC客户端
        # TODO: 实现转发逻辑
        
        self.stats.packets_translated += 1
    
    def _on_mc_player_join(self, player_info: Dict):
        """处理MC玩家加入"""
        logger.info(f"[MC] 玩家加入: {player_info}")
        self.stats.mc_connections += 1
        
        # 转发到MNW
        # TODO: 实现转发逻辑
    
    async def stop(self):
        """停止桥接器"""
        if not self.running:
            return
        
        logger.info("\n🛑 正在停止桥接器...")
        self.running = False
        
        # 停止代理服务器
        if self.proxy:
            await self.proxy.stop()
        
        # 断开MNW连接
        if self.mnw_conn:
            await self.mnw_conn.disconnect()
        
        # 登出MNW
        if self.mnw_login:
            await self.mnw_login.logout()
        
        # 打印统计
        duration = datetime.now() - self.stats.start_time
        logger.info("\n" + "=" * 70)
        logger.info(" 运行统计")
        logger.info("=" * 70)
        logger.info(f"运行时间: {duration}")
        logger.info(f"MC连接数: {self.stats.mc_connections}")
        logger.info(f"MNW连接数: {self.stats.mnw_connections}")
        logger.info(f"翻译包数: {self.stats.packets_translated}")
        logger.info(f"错误数: {self.stats.errors}")
        logger.info("=" * 70)
        logger.info("✅ 桥接器已停止")
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "running": self.running,
            "stats": {
                "mc_connections": self.stats.mc_connections,
                "mnw_connections": self.stats.mnw_connections,
                "packets_translated": self.stats.packets_translated,
                "errors": self.stats.errors,
                "uptime": str(datetime.now() - self.stats.start_time)
            },
            "components": {
                "proxy": self.proxy is not None,
                "translator": self.translator is not None,
                "mnw_conn": self.mnw_conn is not None,
                "mnw_login": self.mnw_login is not None
            }
        }


async def main():
    """主函数"""
    bridge = MnMCPIntegratedBridge()
    
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
