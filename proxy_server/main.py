#!/usr/bin/env python3
"""
迷你世界 ↔ Minecraft 代理服务器
主入口文件
"""

import asyncio
import socket
import threading
from pathlib import Path

class TCPProxy:
    """TCP代理基础类"""
    
    def __init__(self, listen_host, listen_port, target_host, target_port):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.target_host = target_host
        self.target_port = target_port
        self.running = False
    
    def start(self):
        """启动代理"""
        self.running = True
        
        # 创建监听socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.listen_host, self.listen_port))
        server.listen(10)
        
        print(f"[TCP代理] 启动: {self.listen_host}:{self.listen_port} -> {self.target_host}:{self.target_port}")
        
        while self.running:
            try:
                client_sock, client_addr = server.accept()
                print(f"[连接] 来自: {client_addr}")
                
                # 为每个连接创建线程
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_sock,)
                )
                thread.daemon = True
                thread.start()
                
            except Exception as e:
                print(f"[错误] {e}")
        
        server.close()
    
    def handle_client(self, client_sock):
        """处理客户端连接"""
        try:
            # 连接目标服务器
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_sock.connect((self.target_host, self.target_port))
            
            # 创建双向转发线程
            t1 = threading.Thread(target=self.forward, args=(client_sock, target_sock, "C->S"))
            t2 = threading.Thread(target=self.forward, args=(target_sock, client_sock, "S->C"))
            
            t1.daemon = True
            t2.daemon = True
            
            t1.start()
            t2.start()
            
            t1.join()
            t2.join()
            
        except Exception as e:
            print(f"[错误] 处理连接: {e}")
        finally:
            client_sock.close()
            target_sock.close()
    
    def forward(self, source, destination, direction):
        """转发数据"""
        while self.running:
            try:
                data = source.recv(4096)
                if not data:
                    break
                
                print(f"[{direction}] {len(data)} bytes")
                
                # 这里可以添加数据包处理逻辑
                # processed_data = self.process_packet(data, direction)
                
                destination.sendall(data)
                
            except Exception as e:
                print(f"[错误] 转发: {e}")
                break

class MiniWorldMinecraftBridge:
    """迷你世界 ↔ Minecraft 桥接器"""
    
    def __init__(self):
        self.java_server_host = "127.0.0.1"
        self.java_server_port = 25565
        
        # 迷你世界代理端口
        self.miniworld_proxy_port = 25566
        
        # Minecraft基岩版代理端口（通过Geyser）
        self.bedrock_proxy_port = 19133
    
    def start_miniworld_proxy(self):
        """启动迷你世界代理"""
        proxy = TCPProxy(
            listen_host="0.0.0.0",
            listen_port=self.miniworld_proxy_port,
            target_host=self.java_server_host,
            target_port=self.java_server_port
        )
        proxy.start()
    
    def start(self):
        """启动桥接器"""
        print("="*70)
        print("迷你世界 ↔ Minecraft 桥接器")
        print("="*70)
        print()
        print(f"Minecraft Java服务端: {self.java_server_host}:{self.java_server_port}")
        print(f"迷你世界代理端口: {self.miniworld_proxy_port}")
        print()
        print("[状态] 基础TCP代理模式（仅转发，无协议转换）")
        print()
        
        # 启动代理
        self.start_miniworld_proxy()

def test_proxy():
    """测试代理"""
    print("="*70)
    print("代理服务器测试")
    print("="*70)
    
    # 创建简单的echo测试
    proxy = TCPProxy(
        listen_host="127.0.0.1",
        listen_port=25566,
        target_host="127.0.0.1",
        target_port=25565
    )
    
    print("\n[测试] 启动代理...")
    print("  监听: 127.0.0.1:25566")
    print("  目标: 127.0.0.1:25565")
    print()
    print("[提示] 请先启动Minecraft服务端")
    print("[提示] 然后使用迷你世界客户端连接 127.0.0.1:25566")
    print()
    
    try:
        proxy.start()
    except KeyboardInterrupt:
        print("\n[停止] 代理已停止")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_proxy()
    else:
        bridge = MiniWorldMinecraftBridge()
        bridge.start()
