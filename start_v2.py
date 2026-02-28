#!/usr/bin/env python3
"""
MnMCP 智能启动脚本 v2
自动检查并安装依赖，启动服务
"""

import sys
import os
import subprocess
import importlib
import argparse
import asyncio
import json
from pathlib import Path
from typing import List, Tuple, Optional

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_color(text: str, color: str = ""):
    """打印彩色文本"""
    color_code = getattr(Colors, color.upper(), "")
    print(f"{color_code}{text}{Colors.ENDC}")

def check_python_version() -> bool:
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print_color(f"[!] Python版本过低: {version.major}.{version.minor}", "fail")
        print_color("[!] 需要 Python 3.11+", "fail")
        return False
    print_color(f"[✓] Python版本: {version.major}.{version.minor}.{version.micro}", "okgreen")
    return True

def check_and_install_dependencies() -> bool:
    """检查并安装依赖"""
    print_color("\n[1/4] 检查依赖...", "okblue")
    
    # 核心依赖
    core_deps = [
        ("websockets", "websockets>=12.0"),
        ("yaml", "pyyaml>=6.0"),
    ]
    
    # 可选依赖
    optional_deps = [
        ("cryptography", "cryptography>=41.0.0"),
        ("rich", "rich>=13.0.0"),
    ]
    
    all_installed = True
    
    # 检查核心依赖
    for module_name, package_name in core_deps:
        try:
            importlib.import_module(module_name)
            print_color(f"  [✓] {package_name} 已安装", "okgreen")
        except ImportError:
            print_color(f"  [!] {package_name} 未安装，正在安装...", "warning")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print_color(f"  [✓] {package_name} 安装成功", "okgreen")
            except subprocess.CalledProcessError as e:
                print_color(f"  [✗] {package_name} 安装失败: {e}", "fail")
                all_installed = False
    
    # 检查可选依赖
    for module_name, package_name in optional_deps:
        try:
            importlib.import_module(module_name)
            print_color(f"  [✓] {package_name} 已安装 (可选)", "okgreen")
        except ImportError:
            print_color(f"  [!] {package_name} 未安装 (可选)，建议安装以获得更好体验", "warning")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print_color(f"  [✓] {package_name} 安装成功", "okgreen")
            except:
                pass  # 可选依赖安装失败不阻止启动
    
    return all_installed

def check_project_files() -> bool:
    """检查项目文件完整性"""
    print_color("\n[2/4] 检查项目文件...", "okblue")
    
    required_files = [
        ("配置文件", "config.yaml"),
        ("方块映射", "data/mnw_block_mapping_from_go.json"),
        ("启动脚本", "start.py"),
    ]
    
    all_exist = True
    for name, path in required_files:
        if Path(path).exists():
            print_color(f"  [✓] {name}: {path}", "okgreen")
        else:
            print_color(f"  [✗] {name}: {path} 不存在", "fail")
            all_exist = False
    
    return all_exist

def run_tests() -> bool:
    """运行测试"""
    print_color("\n[3/4] 运行测试...", "okblue")
    
    tests = [
        ("加密模块", "tests/test_crypto.py"),
        ("方块映射", "tests/test_block_mapper.py"),
        ("协议翻译", "tests/test_protocol.py"),
    ]
    
    all_passed = True
    for name, test_file in tests:
        if not Path(test_file).exists():
            print_color(f"  [!] {name}: 测试文件不存在", "warning")
            continue
        
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0:
                print_color(f"  [✓] {name}: 通过", "okgreen")
            else:
                print_color(f"  [✗] {name}: 失败", "fail")
                all_passed = False
        except Exception as e:
            print_color(f"  [!] {name}: 运行失败 - {e}", "warning")
    
    return all_passed

def start_server(config_file: str = "config.yaml") -> bool:
    """启动服务器"""
    print_color("\n[4/4] 启动服务器...", "okblue")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from utils.config_loader import Config
        from core.proxy_server_v2 import create_proxy, ProxyConfig
        from utils.logger import setup_logger
        
        # 加载配置
        config = Config.from_yaml(config_file)
        proxy_config = config.to_proxy_config()
        
        if not proxy_config:
            print_color("[!] 配置加载失败，使用默认配置", "warning")
            proxy_config = ProxyConfig()
        
        print_color(f"\n  服务器配置:", "okcyan")
        print_color(f"    MNW监听: {proxy_config.mnw_host}:{proxy_config.mnw_port}", "okcyan")
        print_color(f"    MC目标: {proxy_config.mc_host}:{proxy_config.mc_port}", "okcyan")
        print_color(f"    最大客户端: {proxy_config.max_clients}", "okcyan")
        
        # 创建并启动代理
        print_color(f"\n  正在启动代理服务器...", "okblue")
        
        async def run_server():
            proxy = await create_proxy(proxy_config)
            await proxy.start()
        
        asyncio.run(run_server())
        return True
        
    except KeyboardInterrupt:
        print_color("\n[!] 接收到中断信号，正在停止...", "warning")
        return True
    except Exception as e:
        print_color(f"\n[✗] 启动失败: {e}", "fail")
        import traceback
        traceback.print_exc()
        return False

def show_banner():
    """显示启动横幅"""
    print_color("╔" + "═" * 68 + "╗", "header")
    print_color("║" + " " * 15 + "MnMCP 智能启动器 v2" + " " * 32 + "║", "header")
    print_color("║" + " " * 10 + "Minecraft ↔ MiniWorld 跨平台联机" + " " * 21 + "║", "header")
    print_color("╚" + "═" * 68 + "╝", "header")
    print()

def show_help():
    """显示帮助信息"""
    print_color("\n使用方法:", "okblue")
    print("  python start_v2.py           # 自动检查并启动")
    print("  python start_v2.py --test    # 只运行测试")
    print("  python start_v2.py --check   # 只检查环境")
    print("  python start_v2.py --config  # 使用指定配置")
    print()
    print_color("联机步骤:", "okblue")
    print("  1. 启动代理服务器: python start_v2.py")
    print("  2. 启动Minecraft，连接到 127.0.0.1:19132")
    print("  3. 启动迷你世界，连接到 127.0.0.1:8080")
    print("  4. 开始跨平台联机!")
    print()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MnMCP 智能启动器")
    parser.add_argument("--test", action="store_true", help="只运行测试")
    parser.add_argument("--check", action="store_true", help="只检查环境")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--help-detail", action="store_true", help="显示详细帮助")
    
    args = parser.parse_args()
    
    show_banner()
    
    if args.help_detail:
        show_help()
        return 0
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 检查并安装依赖
    if not check_and_install_dependencies():
        print_color("\n[✗] 依赖安装失败，请手动安装:", "fail")
        print("  pip install websockets pyyaml")
        return 1
    
    # 检查项目文件
    if not check_project_files():
        print_color("\n[✗] 项目文件不完整", "fail")
        return 1
    
    # 如果只检查
    if args.check:
        print_color("\n[✓] 环境检查完成", "okgreen")
        return 0
    
    # 运行测试
    run_tests()
    
    # 如果只测试
    if args.test:
        return 0
    
    # 启动服务器
    print_color("\n" + "=" * 70, "header")
    print_color(" 准备启动服务器", "header")
    print_color("=" * 70, "header")
    print()
    
    if start_server(args.config):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
