#!/usr/bin/env python3
"""
MnMCP 启动脚本
v0.4.0_26w11a_Phase 3

使用方法:
    python start.py                    # 使用默认配置
    python start.py --config config.yaml   # 使用指定配置
    python start.py --test             # 运行测试
"""

import sys
import asyncio
import argparse
import logging
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.config_loader import Config
from core.proxy_server_v2 import create_proxy, ProxyConfig
from utils.logger import setup_logger


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="MnMCP - Minecraft与迷你世界协议转换代理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                           # 使用默认配置启动
  %(prog)s --config myconfig.yaml    # 使用自定义配置
  %(prog)s --test                    # 运行测试
  %(prog)s --version                 # 显示版本
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        default="config.yaml",
        help="配置文件路径 (默认: config.yaml)"
    )
    
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="运行测试"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="显示版本信息"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="启用调试模式"
    )
    
    return parser.parse_args()


def show_version():
    """显示版本信息"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   MnMCP - Minecraft & MiniWorld Cross-Platform Proxy          ║
║                                                                ║
║   版本: v0.4.0_26w11a_Phase 3                                 ║
║   阶段: 连接测试与优化阶段                                     ║
║                                                                ║
║   功能:                                                        ║
║   • Minecraft Bedrock版协议支持                               ║
║   • 迷你世界协议支持                                           ║
║   • 双向协议翻译                                               ║
║   • 2228个方块ID映射                                          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)


def run_tests():
    """运行测试"""
    print("=" * 70)
    print(" 运行测试")
    print("=" * 70)
    
    import subprocess
    
    tests = [
        ("阶段1测试", "test_phase1.py"),
        ("阶段2测试", "test_phase2.py"),
        ("Go映射测试", "test_go_mapping.py"),
    ]
    
    results = []
    for name, script in tests:
        print(f"\n{name}...")
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True
        )
        success = result.returncode == 0
        results.append((name, success))
        print(f"  {'✓' if success else '✗'} {name}")
    
    print("\n" + "=" * 70)
    print(" 测试结果")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "通过" if success else "失败"
        print(f"  {'✓' if success else '✗'} {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    return passed == total


async def main():
    """主函数"""
    args = parse_args()
    
    # 显示版本
    if args.version:
        show_version()
        return 0
    
    # 运行测试
    if args.test:
        success = run_tests()
        return 0 if success else 1
    
    # 显示版本信息
    show_version()
    
    # 加载配置
    print(f"\n加载配置: {args.config}")
    config = Config.from_yaml(args.config)
    
    # 设置日志
    if args.debug:
        config.logging.level = "DEBUG"
    
    logger = setup_logger("MnMCP", level=config.logging.level)
    
    # 创建并启动代理
    proxy_config = config.to_proxy_config()
    proxy = await create_proxy(proxy_config)
    
    try:
        await proxy.start()
    except KeyboardInterrupt:
        print("\n接收到中断信号，正在停止...")
        await proxy.stop()
    except Exception as e:
        logger.error(f"运行时错误: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n已退出")
        sys.exit(0)
