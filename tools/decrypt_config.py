#!/usr/bin/env python3
"""
配置文件解密工具
部署时用于解密敏感信息
"""

import os
import sys
import base64
import getpass
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
CONFIG_DIR = PROJECT_ROOT / "config"
ENCRYPTED_DIR = CONFIG_DIR / "encrypted"

def generate_key(password: str, salt: bytes) -> bytes:
    """从密码和盐生成密钥"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def decrypt_file(encrypted_path: Path, password: str, output_path: Path) -> bool:
    """解密单个文件"""
    try:
        with open(encrypted_path, 'rb') as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            print(f"[!] 文件格式错误: {encrypted_path}")
            return False
        
        salt = lines[0].strip()
        encrypted_data = b''.join(lines[1:])
        
        key = generate_key(password, salt)
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_data)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(decrypted)
        
        return True
        
    except Exception as e:
        print(f"[!] 解密失败 {encrypted_path}: {e}")
        return False

def decrypt_all(password: str) -> bool:
    """解密所有配置文件"""
    print("[*] 开始解密配置文件...")
    
    if not ENCRYPTED_DIR.exists():
        print(f"[!] 加密目录不存在: {ENCRYPTED_DIR}")
        return False
    
    encrypted_files = list(ENCRYPTED_DIR.glob("*.enc"))
    
    if not encrypted_files:
        print("[!] 没有找到加密文件")
        return False
    
    success_count = 0
    for enc_file in encrypted_files:
        output_file = CONFIG_DIR / f"{enc_file.stem}.json"
        if decrypt_file(enc_file, password, output_file):
            print(f"[+] 已解密: {enc_file.name} -> {output_file.name}")
            success_count += 1
        else:
            print(f"[!] 解密失败: {enc_file.name}")
    
    print(f"\n[*] 解密完成: {success_count}/{len(encrypted_files)} 个文件")
    return success_count == len(encrypted_files)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='配置文件解密工具')
    parser.add_argument('--password', '-p', help='解密密码')
    parser.add_argument('--file', '-f', help='指定要解密的文件')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    # 获取密码
    password = args.password
    if not password:
        password = getpass.getpass("请输入解密密码: ")
    
    if args.file:
        # 解密指定文件
        enc_file = Path(args.file)
        if not enc_file.exists():
            print(f"[!] 文件不存在: {enc_file}")
            sys.exit(1)
        
        output = Path(args.output) if args.output else CONFIG_DIR / f"{enc_file.stem}.json"
        if decrypt_file(enc_file, password, output):
            print(f"[+] 解密成功: {output}")
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        # 解密所有文件
        if decrypt_all(password):
            print("[+] 所有配置文件解密成功")
            sys.exit(0)
        else:
            print("[!] 部分文件解密失败")
            sys.exit(1)

if __name__ == "__main__":
    main()