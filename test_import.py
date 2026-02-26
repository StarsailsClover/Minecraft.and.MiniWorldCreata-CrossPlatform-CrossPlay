#!/usr/bin/env python3
"""测试导入核心模块"""

import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from core.protocol_translator import ProtocolTranslator, MINIWORLD_SERVERS
    print("✅ protocol_translator 导入成功")
    print(f"   认证服务器: {MINIWORLD_SERVERS['auth']['host']}")
    print(f"   游戏服务器数量: {len(MINIWORLD_SERVERS['game_servers'])}")
    
    from core.proxy_server import ProxyServer, ProxyConfig
    print("✅ proxy_server 导入成功")
    
    from core.session_manager import SessionManager, PlayerSession
    print("✅ session_manager 导入成功")
    
    # 测试创建实例
    translator = ProtocolTranslator()
    print("✅ ProtocolTranslator 实例化成功")
    
    config = ProxyConfig()
    print("✅ ProxyConfig 实例化成功")
    
    manager = SessionManager()
    print("✅ SessionManager 实例化成功")
    
    print("\n✅ 所有模块检查通过！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
