#!/usr/bin/env python3
"""
数据包捕获和记录工具
捕获并保存Minecraft/迷你世界数据包用于分析
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import struct

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PacketCapture")


class PacketCapture:
    """数据包捕获器"""
    
    def __init__(self, output_dir: str = "captures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.captured_packets: List[Dict] = []
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"数据包捕获器初始化完成")
        logger.info(f"输出目录: {self.output_dir}")
        logger.info(f"会话ID: {self.session_id}")
    
    def capture_packet(self, direction: str, data: bytes, 
                      source: str = "", dest: str = ""):
        """
        捕获数据包
        
        Args:
            direction: 方向 (C->S 或 S->C)
            data: 原始数据
            source: 源地址
            dest: 目标地址
        """
        timestamp = datetime.now().isoformat()
        
        # 分析数据包
        analysis = self._analyze_packet(data)
        
        packet_info = {
            "timestamp": timestamp,
            "session_id": self.session_id,
            "direction": direction,
            "source": source,
            "dest": dest,
            "length": len(data),
            "hex": data.hex(),
            "analysis": analysis
        }
        
        self.captured_packets.append(packet_info)
        
        # 实时日志
        logger.info(f"[{direction}] {len(data)} bytes | "
                   f"MC: {analysis.get('is_minecraft', False)} | "
                   f"Type: {analysis.get('packet_type', 'Unknown')}")
        
        # 保存到文件（实时）
        self._save_packet(packet_info)
    
    def _analyze_packet(self, data: bytes) -> Dict:
        """分析数据包"""
        analysis = {
            "is_minecraft": False,
            "is_miniworld": False,
            "packet_type": "Unknown",
            "packet_name": "Unknown"
        }
        
        if len(data) < 2:
            return analysis
        
        # 尝试解析Minecraft协议
        try:
            # Minecraft数据包以VarInt长度开头
            length, offset = self._read_varint(data, 0)
            if length > 0 and length < len(data):
                packet_id, _ = self._read_varint(data, offset)
                analysis["is_minecraft"] = True
                analysis["packet_type"] = f"0x{packet_id:02X}"
                analysis["packet_name"] = self._get_mc_packet_name(packet_id)
                analysis["length"] = length
        except:
            pass
        
        # 尝试解析迷你世界协议
        if not analysis["is_minecraft"]:
            packet_type = data[0]
            if packet_type in [0x01, 0x02, 0x03, 0x04, 0x05, 0x10, 0xFF]:
                analysis["is_miniworld"] = True
                analysis["packet_type"] = f"0x{packet_type:02X}"
                analysis["packet_name"] = self._get_mnw_packet_name(packet_type)
        
        return analysis
    
    def _read_varint(self, data: bytes, offset: int) -> tuple:
        """读取VarInt"""
        result = 0
        shift = 0
        while True:
            if offset >= len(data):
                raise ValueError("Unexpected end of data")
            byte = data[offset]
            result |= (byte & 0x7F) << shift
            offset += 1
            if not (byte & 0x80):
                break
            shift += 7
            if shift >= 35:
                raise ValueError("VarInt too large")
        return result, offset
    
    def _get_mc_packet_name(self, packet_id: int) -> str:
        """获取Minecraft数据包名称"""
        packet_names = {
            0x00: "Handshake",
            0x01: "Status Request",
            0x02: "Login Start",
            0x03: "Chat Message",
            0x04: "Client Status",
            0x05: "Client Settings",
            0x0A: "Plugin Message",
            0x0B: "Keep Alive",
            0x11: "Player Position",
            0x12: "Player Position And Look",
            0x13: "Player Look",
            0x14: "Player",
            0x1A: "Player Abilities",
            0x1B: "Player Digging",
            0x1C: "Entity Action",
            0x2C: "Held Item Change",
            0x2E: "Creative Inventory Action",
            0x47: "Teleport Confirm",
        }
        return packet_names.get(packet_id, f"Unknown(0x{packet_id:02X})")
    
    def _get_mnw_packet_name(self, packet_type: int) -> str:
        """获取迷你世界数据包名称"""
        packet_names = {
            0x01: "Login",
            0x02: "Game",
            0x03: "Chat",
            0x04: "Move",
            0x05: "Block",
            0x10: "Room",
            0xFF: "Heartbeat"
        }
        return packet_names.get(packet_type, f"Unknown(0x{packet_type:02X})")
    
    def _save_packet(self, packet_info: Dict):
        """保存单个数据包到文件"""
        filename = f"capture_{self.session_id}.jsonl"
        filepath = self.output_dir / filename
        
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(packet_info, ensure_ascii=False) + '\n')
    
    def save_summary(self):
        """保存捕获摘要"""
        summary = {
            "session_id": self.session_id,
            "start_time": self.session_start.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_packets": len(self.captured_packets),
            "mc_packets": sum(1 for p in self.captured_packets 
                            if p["analysis"].get("is_minecraft")),
            "mnw_packets": sum(1 for p in self.captured_packets 
                             if p["analysis"].get("is_miniworld")),
            "packets": self.captured_packets
        }
        
        filename = f"summary_{self.session_id}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"摘要已保存: {filepath}")
        return summary


class CaptureProxy:
    """带捕获功能的代理服务器"""
    
    def __init__(self, host="0.0.0.0", port=25565):
        self.host = host
        self.port = port
        self.capture = PacketCapture()
        self.server = None
        self.running = False
    
    async def handle_client(self, reader, writer):
        """处理客户端连接"""
        addr = writer.get_extra_info('peername')
        logger.info(f"[代理] 新连接: {addr}")
        
        try:
            while self.running:
                data = await reader.read(65536)
                if not data:
                    break
                
                # 捕获数据包
                self.capture.capture_packet(
                    direction="C->S",
                    data=data,
                    source=str(addr),
                    dest=f"{self.host}:{self.port}"
                )
                
                # Echo回客户端
                writer.write(data)
                await writer.drain()
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"[代理] 错误: {e}")
        finally:
            writer.close()
            logger.info(f"[代理] 连接关闭: {addr}")
    
    async def start(self):
        """启动代理"""
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        self.running = True
        
        logger.info("=" * 70)
        logger.info(" MnMCP 数据包捕获代理")
        logger.info(" 捕获并记录Minecraft/迷你世界数据包")
        logger.info("=" * 70)
        logger.info(f"代理服务器: {self.host}:{self.port}")
        logger.info("按 Ctrl+C 停止\n")
        
        async with self.server:
            await self.server.serve_forever()
    
    async def stop(self):
        """停止代理"""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        # 保存摘要
        summary = self.capture.save_summary()
        
        logger.info("\n" + "=" * 70)
        logger.info(" 捕获完成")
        logger.info("=" * 70)
        logger.info(f"总会话: {summary['session_id']}")
        logger.info(f"总数据包: {summary['total_packets']}")
        logger.info(f"Minecraft包: {summary['mc_packets']}")
        logger.info(f"MiniWorld包: {summary['mnw_packets']}")
        logger.info("=" * 70)


async def main():
    """主函数"""
    proxy = CaptureProxy("0.0.0.0", 25565)
    
    try:
        await proxy.start()
    except KeyboardInterrupt:
        logger.info("\n收到中断信号")
    finally:
        await proxy.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"运行时错误: {e}")
