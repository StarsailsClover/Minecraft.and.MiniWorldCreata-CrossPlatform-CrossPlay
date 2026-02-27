#!/usr/bin/env python3
"""
MnMCP 一键部署脚本
支持 minimal/standard/full 三种部署模式
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.resolve()
CONFIG_DIR = PROJECT_ROOT / "config"
ENCRYPTED_DIR = CONFIG_DIR / "encrypted"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """打印部署横幅"""
    banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              MnMCP 一键部署脚本                               ║
║     Minecraft ↔ MiniWorld 跨平台联机方案                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
    print(banner)

def check_python_version():
    """检查Python版本"""
    print(f"{Colors.OKBLUE}[*] 检查Python版本...{Colors.ENDC}")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"{Colors.FAIL}[!] 需要Python 3.11+，当前版本: {version.major}.{version.minor}{Colors.ENDC}")
        return False
    print(f"{Colors.OKGREEN}[+] Python版本检查通过: {version.major}.{version.minor}.{version.micro}{Colors.ENDC}")
    return True

def check_dependencies():
    """检查依赖"""
    print(f"{Colors.OKBLUE}[*] 检查依赖...{Colors.ENDC}")
    
    required = ["git", "java"]
    missing = []
    
    for cmd in required:
        if shutil.which(cmd) is None:
            missing.append(cmd)
    
    if missing:
        print(f"{Colors.FAIL}[!] 缺少必要依赖: {', '.join(missing)}{Colors.ENDC}")
        print(f"{Colors.WARNING}请安装缺失的依赖后重试{Colors.ENDC}")
        return False
    
    print(f"{Colors.OKGREEN}[+] 所有依赖已安装{Colors.ENDC}")
    return True

def install_python_deps():
    """安装Python依赖"""
    print(f"{Colors.OKBLUE}[*] 安装Python依赖...{Colors.ENDC}")
    
    req_file = PROJECT_ROOT / "requirements.txt"
    if not req_file.exists():
        print(f"{Colors.FAIL}[!] requirements.txt 不存在{Colors.ENDC}")
        return False
    
    try:
        # 先安装/升级 pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      capture_output=True)
        
        # 安装依赖
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"{Colors.OKGREEN}[+] Python依赖安装成功{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.FAIL}[!] 依赖安装失败{Colors.ENDC}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"{Colors.FAIL}[!] 安装出错: {e}{Colors.ENDC}")
        return False

def decrypt_config(password: str) -> bool:
    """解密配置文件"""
    print(f"{Colors.OKBLUE}[*] 解密配置文件...{Colors.ENDC}")
    
    decrypt_script = PROJECT_ROOT / "tools" / "decrypt_config.py"
    if not decrypt_script.exists():
        print(f"{Colors.FAIL}[!] 解密脚本不存在{Colors.ENDC}")
        return False
    
    # 检查cryptography是否安装
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        print(f"{Colors.WARNING}[!] cryptography模块未安装，尝试安装...{Colors.ENDC}")
        subprocess.run([sys.executable, "-m", "pip", "install", "cryptography"], 
                      capture_output=True)
    
    try:
        result = subprocess.run(
            [sys.executable, str(decrypt_script), "--password", password],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )
        if result.returncode == 0:
            print(f"{Colors.OKGREEN}[+] 配置文件解密成功{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.FAIL}[!] 解密失败: {result.stderr}{Colors.ENDC}")
            return False
    except Exception as e:
        print(f"{Colors.FAIL}[!] 解密出错: {e}{Colors.ENDC}")
        return False

def setup_directories():
    """创建必要的目录"""
    print(f"{Colors.OKBLUE}[*] 创建目录结构...{Colors.ENDC}")
    
    dirs = [
        "logs",
        "data",
        "config",
        "server/paper",
        "server/plugins",
        "server/mods"
    ]
    
    for d in dirs:
        (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)
    
    print(f"{Colors.OKGREEN}[+] 目录结构创建完成{Colors.ENDC}")
    return True

def create_sample_config():
    """创建示例配置文件"""
    print(f"{Colors.OKBLUE}[*] 创建示例配置...{Colors.ENDC}")
    
    config_file = CONFIG_DIR / "config.json"
    if config_file.exists():
        print(f"{Colors.OKGREEN}[+] 配置文件已存在{Colors.ENDC}")
        return True
    
    sample_config = {
        "server": {
            "host": "0.0.0.0",
            "port": 25565,
            "max_players": 100
        },
        "miniworld": {
            "auth_server": "mwu-api-pre.mini1.cn",
            "game_servers": [
                "183.60.230.67:4000",
                "125.88.253.199:4000"
            ]
        },
        "minecraft": {
            "version": "1.20.6",
            "server_type": "paper"
        },
        "geyser": {
            "enabled": True,
            "port": 19132
        }
    }
    
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2, ensure_ascii=False)
    
    print(f"{Colors.OKGREEN}[+] 示例配置已创建: {config_file}{Colors.ENDC}")
    print(f"{Colors.WARNING}[!] 请编辑此文件配置敏感信息后，运行加密命令:{Colors.ENDC}")
    print(f"    python tools/encrypt_config.py encrypt")
    return True

def deploy_minimal():
    """最小部署 - 仅代理服务"""
    print(f"{Colors.OKCYAN}{Colors.BOLD}\n>>> 执行最小部署模式 <<<{Colors.ENDC}\n")
    
    steps = [
        ("检查Python版本", check_python_version),
        ("安装Python依赖", install_python_deps),
        ("创建目录结构", setup_directories),
        ("创建示例配置", create_sample_config),
    ]
    
    for name, func in steps:
        print(f"\n{Colors.BOLD}[{name}]{Colors.ENDC}")
        if not func():
            print(f"{Colors.FAIL}部署失败于步骤: {name}{Colors.ENDC}")
            return False
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ 最小部署完成！{Colors.ENDC}")
    print(f"\n启动命令:")
    print(f"  python -m src.core.proxy_server")
    print(f"\n{Colors.WARNING}注意: 如需使用加密配置，请先编辑 config/config.json 并运行:{Colors.ENDC}")
    print(f"  python tools/encrypt_config.py encrypt")
    return True

def deploy_standard():
    """标准部署 - 代理 + PaperMC"""
    print(f"{Colors.OKCYAN}{Colors.BOLD}\n>>> 执行标准部署模式 <<<{Colors.ENDC}\n")
    
    if not deploy_minimal():
        return False
    
    print(f"\n{Colors.BOLD}[安装PaperMC]{Colors.ENDC}")
    print(f"{Colors.WARNING}PaperMC安装需要手动完成，请参考文档:{Colors.ENDC}")
    print(f"  docs/DEPLOYMENT_GUIDE.md")
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ 标准部署完成！{Colors.ENDC}")
    return True

def deploy_full():
    """完整部署 - 代理 + PaperMC + Geyser + Web"""
    print(f"{Colors.OKCYAN}{Colors.BOLD}\n>>> 执行完整部署模式 <<<{Colors.ENDC}\n")
    
    if not deploy_standard():
        return False
    
    print(f"\n{Colors.BOLD}[安装GeyserMC]{Colors.ENDC}")
    print(f"{Colors.WARNING}GeyserMC安装需要手动完成，请参考文档{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}[部署Web界面]{Colors.ENDC}")
    print(f"{Colors.WARNING}Web界面部署需要手动完成，请参考文档{Colors.ENDC}")
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ 完整部署完成！{Colors.ENDC}")
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MnMCP 一键部署脚本')
    parser.add_argument('--mode', choices=['minimal', 'standard', 'full'], 
                       default='minimal', help='部署模式')
    parser.add_argument('--password', help='配置解密密码')
    parser.add_argument('--skip-decrypt', action='store_true', 
                       help='跳过解密步骤')
    
    args = parser.parse_args()
    
    print_banner()
    
    # 检查是否在项目根目录
    if not (PROJECT_ROOT / "src").exists():
        print(f"{Colors.FAIL}[!] 请在项目根目录运行此脚本{Colors.ENDC}")
        sys.exit(1)
    
    # 解密配置（除非跳过）
    if not args.skip_decrypt:
        encrypted_dir = PROJECT_ROOT / "config" / "encrypted"
        if encrypted_dir.exists() and any(encrypted_dir.glob("*.enc")):
            password = args.password or input(f"{Colors.OKBLUE}请输入配置解密密码: {Colors.ENDC}")
            if not decrypt_config(password):
                print(f"{Colors.WARNING}解密失败，将使用默认配置继续...{Colors.ENDC}")
        else:
            print(f"{Colors.OKBLUE}[*] 未发现加密配置文件，跳过解密步骤{Colors.ENDC}")
    
    # 执行部署
    success = False
    if args.mode == 'minimal':
        success = deploy_minimal()
    elif args.mode == 'standard':
        success = deploy_standard()
    elif args.mode == 'full':
        success = deploy_full()
    
    if success:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}部署成功！{Colors.ENDC}")
        print(f"\n查看日志: tail -f logs/server.log")
        print(f"管理界面: http://localhost:8080/admin")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}部署失败！{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()