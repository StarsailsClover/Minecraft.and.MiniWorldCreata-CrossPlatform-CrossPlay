from security.crypto_utils import decrypt as D
#!/usr/bin/env python3
"""
Java服务器管理器
管理PaperMC服务器的启动、监控和交互
"""

import asyncio
import subprocess
import logging
import json
from pathlib import Path
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """服务器配置"""
    java_path: str = "java"
    server_jar: str = "paper-1.20.6-151.jar"
    min_memory: str = "1G"
    max_memory: str = "2G"
    server_port: int = 25566
    online_mode: bool = False
    motd: str = "MnMCP Bridge Server"
    max_players: int = 100


@dataclass
class PlayerInfo:
    """玩家信息"""
    username: str
    uuid: str
    ip: str
    is_bedrock: bool = False
    joined_at: datetime = None
    
    def __post_init__(self):
        if self.joined_at is None:
            self.joined_at = datetime.now()


class JavaServerManager:
    """Java服务器管理器"""
    
    def __init__(self, server_dir: Path, config: ServerConfig = None):
        self.server_dir = Path(server_dir)
        self.config = config or ServerConfig()
        
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self.started = False
        
        # 玩家管理
        self.players: Dict[str, PlayerInfo] = {}
        self.player_callbacks: List[Callable] = []
        
        # 服务器状态
        self.tps: float = 20.0
        self.memory_usage: Dict[str, int] = {}
        
        logger.info(f"Java服务器管理器初始化: {self.server_dir}")
    
    async def start(self) -> bool:
        """启动PaperMC服务器"""
        if self.running:
            logger.warning("服务器已在运行")
            return True
        
        try:
            # 检查Java
            java_version = await self._check_java()
            if not java_version:
                logger.error("Java未安装或版本过低")
                return False
            
            logger.info(f"Java版本: {java_version}")
            
            # 检查服务器文件
            jar_path = self.server_dir / self.config.server_jar
            if not jar_path.exists():
                logger.error(f"服务器文件不存在: {jar_path}")
                return False
            
            # 构建启动命令
            cmd = [
                self.config.java_path,
                f"-Xms{self.config.min_memory}",
                f"-Xmx{self.config.max_memory}",
                "-jar", str(jar_path),
                "nogui"
            ]
            
            logger.info(f"启动命令: {' '.join(cmd)}")
            
            # 启动服务器
            self.process = subprocess.Popen(
                cmd,
                cwd=self.server_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.running = True
            
            # 启动日志监控
            asyncio.create_task(self._monitor_logs())
            
            logger.info("PaperMC服务器启动中...")
            
            # 等待服务器启动完成
            await self._wait_for_start()
            
            return True
            
        except Exception as e:
            logger.error(f"启动服务器失败: {e}")
            self.running = False
            return False
    
    async def stop(self) -> bool:
        """停止服务器"""
        if not self.running or not self.process:
            logger.warning("服务器未运行")
            return True
        
        try:
            logger.info("正在停止PaperMC服务器...")
            
            # 发送停止命令
            self.send_command("stop")
            
            # 等待进程结束
            try:
                self.process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                logger.warning("服务器未正常停止，强制终止")
                self.process.terminate()
                self.process.wait(timeout=5)
            
            self.running = False
            self.started = False
            
            logger.info("PaperMC服务器已停止")
            return True
            
        except Exception as e:
            logger.error(f"停止服务器失败: {e}")
            return False
    
    def send_command(self, command: str):
        """发送命令到服务器"""
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(f"{command}\n")
                self.process.stdin.flush()
                logger.debug(f"发送命令: {command}")
            except Exception as e:
                logger.error(f"发送命令失败: {e}")
    
    async def _check_java(self) -> Optional[str]:
        """检查Java版本"""
        try:
            result = subprocess.run(
                [self.config.java_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Java版本信息通常在stderr
            version_line = result.stderr.split('\n')[0]
            
            # 检查版本号
            if '"17.' in version_line or '"21.' in version_line:
                return version_line
            
            return None
            
        except Exception as e:
            logger.error(f"检查Java失败: {e}")
            return None
    
    async def _monitor_logs(self):
        """监控服务器日志"""
        while self.running and self.process:
            try:
                line = self.process.stdout.readline()
                if line:
                    self._parse_log_line(line.strip())
                else:
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"日志监控错误: {e}")
                break
    
    def _parse_log_line(self, line: str):
        """解析日志行"""
        # 检查玩家加入
        if "joined the game" in line:
            self._handle_player_join(line)
        
        # 检查玩家离开
        elif "left the game" in line:
            self._handle_player_leave(line)
        
        # 检查服务器启动完成
        elif "Done" in line and "For help, type" in line:
            self.started = True
            logger.info("PaperMC服务器启动完成！")
        
        # 检查TPS
        elif "TPS" in line:
            self._parse_tps(line)
        
        # 输出日志
        logger.info(f"[PaperMC] {line}")
    
    def _handle_player_join(self, line: str):
        """处理玩家加入"""
        # 解析: "[14:23:15] [Server thread/INFO]: PlayerName[/127.0.0.1:12345] logged in with entity id 123 at ([world]0.0, 64.0, 0.0)"
        try:
            parts = line.split(": ")
            if len(parts) >= 2:
                info = parts[-1]
                username = info.split("[")[0].strip()
                
                # 检查是否是基岩版玩家 (Floodgate会在用户名前加.)
                is_bedrock = username.startswith(".")
                if is_bedrock:
                    username = username[1:]  # 移除前缀
                
                player = PlayerInfo(
                    username=username,
                    uuid="",  # 需要从其他日志获取
                    ip=D("ENC:KTdfUq0aeRP/"),
                    is_bedrock=is_bedrock
                )
                
                self.players[username] = player
                logger.info(f"玩家加入: {username} (基岩版: {is_bedrock})")
                
                # 触发回调
                for callback in self.player_callbacks:
                    try:
                        callback("join", player)
                    except Exception as e:
                        logger.error(f"玩家加入回调错误: {e}")
                        
        except Exception as e:
            logger.error(f"解析玩家加入失败: {e}")
    
    def _handle_player_leave(self, line: str):
        """处理玩家离开"""
        try:
            parts = line.split(": ")
            if len(parts) >= 2:
                username = parts[-1].split(" ")[0].strip()
                
                if username in self.players:
                    player = self.players.pop(username)
                    logger.info(f"玩家离开: {username}")
                    
                    # 触发回调
                    for callback in self.player_callbacks:
                        try:
                            callback("leave", player)
                        except Exception as e:
                            logger.error(f"玩家离开回调错误: {e}")
                            
        except Exception as e:
            logger.error(f"解析玩家离开失败: {e}")
    
    def _parse_tps(self, line: str):
        """解析TPS信息"""
        try:
            # 解析: "TPS from last 1m, 5m, 15m: 20.0, 20.0, 20.0"
            if "TPS from last" in line:
                tps_str = line.split(":")[-1].strip()
                tps_values = [float(x.strip()) for x in tps_str.split(",")]
                self.tps = tps_values[0]  # 使用1分钟TPS
                
        except Exception as e:
            logger.debug(f"解析TPS失败: {e}")
    
    async def _wait_for_start(self, timeout: int = 120):
        """等待服务器启动完成"""
        start_time = asyncio.get_event_loop().time()
        
        while not self.started:
            if asyncio.get_event_loop().time() - start_time > timeout:
                logger.warning("服务器启动超时")
                break
            
            await asyncio.sleep(1)
        
        if self.started:
            logger.info("服务器已就绪")
    
    def get_player_list(self) -> List[PlayerInfo]:
        """获取在线玩家列表"""
        return list(self.players.values())
    
    def get_stats(self) -> Dict:
        """获取服务器统计"""
        return {
            "running": self.running,
            "started": self.started,
            "tps": self.tps,
            "player_count": len(self.players),
            "players": [p.username for p in self.players.values()]
        }
    
    def register_player_callback(self, callback: Callable):
        """注册玩家事件回调"""
        self.player_callbacks.append(callback)
    
    def unregister_player_callback(self, callback: Callable):
        """注销玩家事件回调"""
        if callback in self.player_callbacks:
            self.player_callbacks.remove(callback)


# 测试代码
if __name__ == "__main__":
    import sys
    
    async def test():
        """测试服务器管理器"""
        server_dir = Path("C:/MnMCP/server")
        
        manager = JavaServerManager(server_dir)
        
        # 注册玩家回调
        def on_player_event(event, player):
            print(f"[回调] 事件: {event}, 玩家: {player.username}")
        
        manager.register_player_callback(on_player_event)
        
        # 启动服务器
        if await manager.start():
            print("服务器启动成功！")
            
            # 等待一段时间
            await asyncio.sleep(30)
            
            # 获取统计
            stats = manager.get_stats()
            print(f"服务器统计: {stats}")
            
            # 停止服务器
            await manager.stop()
            print("服务器已停止")
        else:
            print("服务器启动失败")
            sys.exit(1)
    
    # 运行测试
    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        print("\n测试被中断")
