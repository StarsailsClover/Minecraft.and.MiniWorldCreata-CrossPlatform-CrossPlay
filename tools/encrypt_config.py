#!/usr/bin/env python3
"""
配置文件加密工具
用于加密敏感信息（API密钥、服务器地址等）
"""

import os
import sys
import json
import base64
import getpass
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
CONFIG_DIR = PROJECT_ROOT / "config"
ENCRYPTED_DIR = CONFIG_DIR / "encrypted"
SALT_FILE = ENCRYPTED_DIR / ".salt"

def generate_key(password: str, salt: bytes = None) -> tuple:
    """从密码生成加密密钥"""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_data(data: str, password: str) -> tuple:
    """加密数据"""
    key, salt = generate_key(password)
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    return encrypted, salt

def decrypt_data(encrypted_data: bytes, password: str, salt: bytes) -> str:
    """解密数据"""
    key, _ = generate_key(password, salt)
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_data)
    return decrypted.decode()

def encrypt_config(config_file: Path, password: str) -> bool:
    """加密配置文件"""
    try:
        # 读取原始配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = f.read()
        
        # 加密
        encrypted, salt = encrypt_data(config_data, password)
        
        # 确保目录存在
        ENCRYPTED_DIR.mkdir(parents=True, exist_ok=True)
        
        # 保存加密文件
        output_file = ENCRYPTED_DIR / f"{config_file.stem}.enc"
        with open(output_file, 'wb') as f:
            f.write(salt + b'\n' + encrypted)
        
        # 保存salt（用于后续解密）
        with open(SALT_FILE, 'wb') as f:
            f.write(salt)
        
        print(f"[+] 配置已加密: {config_file} -> {output_file}")
        return True
        
    except Exception as e:
        print(f"[!] 加密失败: {e}")
        return False

def decrypt_config_file(encrypted_file: Path, password: str, output_file: Path = None) -> bool:
    """解密配置文件"""
    try:
        # 读取加密文件
        with open(encrypted_file, 'rb') as f:
            lines = f.readlines()
        
        salt = lines[0].strip()
        encrypted_data = b''.join(lines[1:])
        
        # 解密
        decrypted = decrypt_data(encrypted_data, password, salt)
        
        # 保存解密后的文件
        if output_file is None:
            output_file = CONFIG_DIR / f"{encrypted_file.stem}.json"
        
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(decrypted)
        
        print(f"[+] 配置已解密: {encrypted_file} -> {output_file}")
        return True
        
    except Exception as e:
        print(f"[!] 解密失败: {e}")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='配置文件加密/解密工具')
    parser.add_argument('action', choices=['encrypt', 'decrypt'], help='操作类型')
    parser.add_argument('--file', '-f', help='要处理的文件')
    parser.add_argument('--password', '-p', help='密码（建议交互式输入）')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    # 获取密码
    password = args.password
    if not password:
        if args.action == 'encrypt':
            password = getpass.getpass("请输入加密密码: ")
            confirm = getpass.getpass("请再次输入密码确认: ")
            if password != confirm:
                print("[!] 密码不匹配")
                sys.exit(1)
        else:
            password = getpass.getpass("请输入解密密码: ")
    
    if args.action == 'encrypt':
        if not args.file:
            # 加密默认配置文件
            config_file = CONFIG_DIR / "config.json"
            if not config_file.exists():
                print(f"[!] 配置文件不存在: {config_file}")
                print("[*] 创建示例配置文件...")
                create_sample_config()
                sys.exit(0)
            encrypt_config(config_file, password)
        else:
            encrypt_config(Path(args.file), password)
            
    elif args.action == 'decrypt':
        if not args.file:
            # 解密默认加密文件
            encrypted_file = ENCRYPTED_DIR / "config.enc"
            if not encrypted_file.exists():
                print(f"[!] 加密文件不存在: {encrypted_file}")
                sys.exit(1)
            decrypt_config_file(encrypted_file, password, 
                              Path(args.output) if args.output else None)
        else:
            decrypt_config_file(Path(args.file), password,
                              Path(args.output) if args.output else None)

def create_sample_config():
    """创建示例配置文件"""
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
        },
        "security": {
            "encryption_key": "YOUR_ENCRYPTION_KEY_HERE",
            "api_secret": "YOUR_API_SECRET_HERE"
        }
    }
    
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config_file = CONFIG_DIR / "config.json"
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2, ensure_ascii=False)
    
    print(f"[+] 示例配置文件已创建: {config_file}")
    print("[*] 请编辑此文件，替换敏感信息后运行加密命令:")
    print(f"   python tools/encrypt_config.py encrypt -f {config_file}")

if __name__ == "__main__":
    main()