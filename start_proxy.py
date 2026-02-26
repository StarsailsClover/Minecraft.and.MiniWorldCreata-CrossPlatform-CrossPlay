#!/usr/bin/env python3
"""
代理服务器启动脚本
"""

import sys
import asyncio
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.proxy_server import ProxyServer, ProxyConfig

def main():
    """主函数"""
    print("=" * 60)
    print("MnMCP 代理服务器启动器")
    print("=" * 60)
    print()
    
    # 创建配置
    config = ProxyConfig(
        mc_host="127.0.0.1",  # 本地监听
        mc_port=25565,         # Minecraft标准端口
        connect_timeout=30.0,
        read_timeout=60.0
    )
    
    print(f"[*] 配置:")
    print(f"    监听地址: {config.mc_host}:{config.mc_port}")
    print(f"    连接超时: {config.connect_timeout}s")
    print(f"    读取超时: {config.read_timeout}s")
    print()
    
    # 创建服务器
    server = ProxyServer(config)
    
    try:
        print("[*] 启动代理服务器...")
        print("[*] 按 Ctrl+C 停止")
        print()
        
        # 启动服务器
        asyncio.run(server.start())
        
    except KeyboardInterrupt:
        print("\n[!] 用户中断")
        server.stop()
    except Exception as e:
        print(f"\n[-] 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
