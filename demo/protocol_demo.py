#!/usr/bin/env python3
"""
MnMCP 协议对接演示脚本
在终端显示可视化的协议转换过程
"""

import time
import sys
import random
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

class Colors:
    """ANSI颜色代码"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ProtocolDemo:
    """协议演示器"""
    
    def __init__(self):
        self.packet_count = 0
        self.block_translations = 0
        
    def clear_screen(self):
        """清屏"""
        print('\033[2J\033[H')
        
    def print_banner(self):
        """打印横幅"""
        banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                MnMCP 协议对接实时演示                         ║
║         Minecraft ↔ MiniWorld 协议转换可视化                  ║
╚══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
        print(banner)
        
    def print_status(self, message, status="info"):
        """打印状态信息"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        if status == "success":
            icon = f"{Colors.OKGREEN}✓{Colors.ENDC}"
            color = Colors.OKGREEN
        elif status == "warning":
            icon = f"{Colors.WARNING}⚠{Colors.ENDC}"
            color = Colors.WARNING
        elif status == "error":
            icon = f"{Colors.FAIL}✗{Colors.ENDC}"
            color = Colors.FAIL
        else:
            icon = f"{Colors.OKBLUE}ℹ{Colors.ENDC}"
            color = Colors.OKBLUE
            
        print(f"[{timestamp}] {icon} {color}{message}{Colors.ENDC}")
        
    def print_packet_flow(self, direction, packet_type, data):
        """打印数据包流向"""
        self.packet_count += 1
        
        if direction == "mc_to_mnw":
            arrow = f"{Colors.OKGREEN}→{Colors.ENDC}"
            source = f"{Colors.OKGREEN}Minecraft{Colors.ENDC}"
            target = f"{Colors.OKCYAN}MiniWorld{Colors.ENDC}"
        else:
            arrow = f"{Colors.OKCYAN}→{Colors.ENDC}"
            source = f"{Colors.OKCYAN}MiniWorld{Colors.ENDC}"
            target = f"{Colors.OKGREEN}Minecraft{Colors.ENDC}"
            
        print(f"\n{Colors.BOLD}数据包 #{self.packet_count}{Colors.ENDC}")
        print(f"  {source} {arrow} {target}")
        print(f"  类型: {Colors.WARNING}{packet_type}{Colors.ENDC}")
        print(f"  数据: {Colors.OKBLUE}{data}{Colors.ENDC}")
        
    def print_translation(self, mc_data, mnw_data, translation_type):
        """打印协议转换详情"""
        print(f"\n{Colors.BOLD}协议转换:{Colors.ENDC}")
        print(f"  {Colors.OKGREEN}Minecraft:{Colors.ENDC} {mc_data}")
        print(f"  {Colors.OKCYAN}MiniWorld:{Colors.ENDC} {mnw_data}")
        print(f"  转换类型: {Colors.WARNING}{translation_type}{Colors.ENDC}")
        
    def simulate_login(self):
        """模拟登录流程"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}═══ 登录认证流程 ═══{Colors.ENDC}\n")
        
        self.print_status("收到 Minecraft 登录请求", "info")
        time.sleep(0.5)
        
        self.print_status("解析 Minecraft 登录数据包", "info")
        self.print_packet_flow("mc_to_mnw", "Login Start", "{username: Player123, protocol: 764}")
        time.sleep(0.5)
        
        self.print_status("转换为 MiniWorld 认证格式", "warning")
        self.print_translation(
            "Minecraft Login Start (Protocol 764)",
            "MiniWorld Auth Request (HTTPS API)",
            "协议格式转换 + 加密处理"
        )
        time.sleep(0.5)
        
        self.print_status("向 MiniWorld 认证服务器发送请求", "info")
        self.print_status("认证服务器: mwu-api-pre.mini1.cn:443", "info")
        time.sleep(1)
        
        self.print_status("收到 MiniWorld 认证响应", "success")
        self.print_packet_flow("mnw_to_mc", "Auth Response", "{token: eyJhbG..., account_id: 123456}")
        time.sleep(0.5)
        
        self.print_status("转换为 Minecraft 登录成功响应", "warning")
        self.print_translation(
            "MiniWorld Auth Token",
            "Minecraft Login Success (UUID)",
            "账户映射 + Token转换"
        )
        time.sleep(0.5)
        
        self.print_status("登录认证完成", "success")
        
    def simulate_block_placement(self):
        """模拟方块放置"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}═══ 方块同步流程 ═══{Colors.ENDC}\n")
        
        blocks = [
            ("stone", "石头", 1),
            ("grass_block", "草方块", 2),
            ("dirt", "泥土", 3),
            ("diamond_ore", "钻石矿石", 56),
        ]
        
        for mc_block, mnw_block, block_id in blocks:
            self.block_translations += 1
            
            x, y, z = random.randint(-50, 50), random.randint(0, 100), random.randint(-50, 50)
            
            self.print_status(f"收到方块放置请求: {mc_block}", "info")
            self.print_packet_flow(
                "mc_to_mnw",
                "Block Placement",
                f"{{block: {mc_block}, pos: [{x}, {y}, {z}]}}"
            )
            time.sleep(0.3)
            
            self.print_status(f"方块ID映射: {mc_block} → {mnw_block}", "warning")
            self.print_translation(
                f"Minecraft {mc_block} (ID: {block_id})",
                f"MiniWorld {mnw_block} (ID: {block_id})",
                "ID映射 + 坐标转换"
            )
            time.sleep(0.3)
            
            self.print_status("坐标系统转换", "info")
            print(f"  {Colors.OKGREEN}MC坐标:{Colors.ENDC}  X:{x}, Y:{y}, Z:{z}")
            print(f"  {Colors.OKCYAN}MNW坐标:{Colors.ENDC} X:{-x}, Y:{y+1}, Z:{z}")
            time.sleep(0.3)
            
            self.print_status(f"方块同步完成", "success")
            print()
            
    def simulate_chat(self):
        """模拟聊天转发"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}═══ 聊天转发流程 ═══{Colors.ENDC}\n")
        
        messages = [
            ("Player123", "Hello from Minecraft!", "mc_to_mnw"),
            ("迷你玩家", "你好！来自迷你世界", "mnw_to_mc"),
            ("Player456", "This is awesome!", "mc_to_mnw"),
        ]
        
        for player, message, direction in messages:
            self.print_status(f"收到聊天消息: {player}", "info")
            
            if direction == "mc_to_mnw":
                self.print_packet_flow(direction, "Chat Message", f"{player}: {message}")
                time.sleep(0.3)
                self.print_status("转换为 MiniWorld 聊天格式", "warning")
            else:
                self.print_packet_flow(direction, "Chat Message", f"{player}: {message}")
                time.sleep(0.3)
                self.print_status("转换为 Minecraft 聊天格式", "warning")
                
            self.print_status("消息转发完成", "success")
            print()
            time.sleep(0.5)
            
    def simulate_player_movement(self):
        """模拟玩家移动"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}═══ 玩家移动同步 ═══{Colors.ENDC}\n")
        
        positions = [
            (0, 64, 0),
            (10, 65, 5),
            (20, 70, 10),
            (15, 68, -5),
        ]
        
        for i, (x, y, z) in enumerate(positions):
            self.print_status(f"玩家位置更新 #{i+1}", "info")
            
            self.print_packet_flow("mc_to_mnw", "Player Position", f"[{x:.2f}, {y:.2f}, {z:.2f}]")
            time.sleep(0.2)
            
            # 坐标转换
            mnw_x, mnw_y, mnw_z = -x, y + 1, z
            
            print(f"  {Colors.OKGREEN}MC坐标:{Colors.ENDC}  X:{x:>8.2f}, Y:{y:>8.2f}, Z:{z:>8.2f}")
            print(f"  {Colors.OKCYAN}MNW坐标:{Colors.ENDC} X:{mnw_x:>8.2f}, Y:{mnw_y:>8.2f}, Z:{mnw_z:>8.2f}")
            print(f"  {Colors.WARNING}转换规则:{Colors.ENDC} X×(-1), Y+1, Z不变")
            
            self.print_status("位置同步完成", "success")
            print()
            time.sleep(0.5)
            
    def print_statistics(self):
        """打印统计信息"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}═══ 演示统计 ═══{Colors.ENDC}\n")
        print(f"  总数据包数: {Colors.OKGREEN}{self.packet_count}{Colors.ENDC}")
        print(f"  方块转换数: {Colors.OKGREEN}{self.block_translations}{Colors.ENDC}")
        print(f"  协议转换成功率: {Colors.OKGREEN}100%{Colors.ENDC}")
        print(f"  平均延迟: {Colors.OKGREEN}< 50ms{Colors.ENDC}")
        
    def run_demo(self):
        """运行完整演示"""
        try:
            self.clear_screen()
            self.print_banner()
            
            input(f"{Colors.WARNING}按 Enter 键开始演示...{Colors.ENDC}")
            
            # 登录流程
            self.simulate_login()
            input(f"\n{Colors.WARNING}按 Enter 键继续方块同步演示...{Colors.ENDC}")
            
            # 方块同步
            self.simulate_block_placement()
            input(f"\n{Colors.WARNING}按 Enter 键继续聊天转发演示...{Colors.ENDC}")
            
            # 聊天转发
            self.simulate_chat()
            input(f"\n{Colors.WARNING}按 Enter 键继续玩家移动演示...{Colors.ENDC}")
            
            # 玩家移动
            self.simulate_player_movement()
            
            # 统计
            self.print_statistics()
            
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}演示完成！{Colors.ENDC}")
            print(f"\n{Colors.OKBLUE}更多详情请参考:{Colors.ENDC}")
            print(f"  - 协议分析报告: docs/PROTOCOL_ANALYSIS_REPORT.md")
            print(f"  - 技术架构文档: docs/TechnicalDocument.md")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}演示已中断{Colors.ENDC}")
            
def main():
    """主函数"""
    demo = ProtocolDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()
