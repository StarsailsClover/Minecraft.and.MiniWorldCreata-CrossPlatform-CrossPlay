#!/usr/bin/env python3
"""
快速测试 - 验证代理服务器是否可连接
"""

import socket
import sys

def test_server_connection(host="localhost", port=25565, timeout=5):
    """测试服务器连接"""
    print(f"测试连接到 {host}:{port}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        
        if result == 0:
            print("✅ 服务器正在运行，端口可连接")
            sock.close()
            return True
        else:
            print(f"❌ 无法连接到服务器 (错误码: {result})")
            return False
            
    except socket.error as e:
        print(f"❌ 连接错误: {e}")
        return False

if __name__ == "__main__":
    success = test_server_connection()
    sys.exit(0 if success else 1)
