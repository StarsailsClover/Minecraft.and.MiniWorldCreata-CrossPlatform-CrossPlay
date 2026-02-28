#!/usr/bin/env python3
"""
协议验证工具 - v0.2.2_26w09a_Phase 1
验证迷你世界协议数据包结构

功能:
1. 验证数据包格式是否符合推测结构
2. 分析抓包文件中的数据包
3. 生成协议验证报告
"""

import struct
import json
import logging
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PacketValidationResult:
    """数据包验证结果"""
    is_valid: bool
    packet_type: Optional[int] = None
    sub_type: Optional[int] = None
    seq_id: Optional[int] = None
    data_length: Optional[int] = None
    error_msg: str = ""
    raw_data: bytes = b""
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = asdict(self)
        result['raw_data'] = self.raw_data.hex() if self.raw_data else ""
        return result


class MiniWorldPacketValidator:
    """
    迷你世界数据包验证器
    
    基于抓包分析推测的数据包结构:
    [1字节: 包类型] [1字节: 子类型] [2字节: 序列号] [4字节: 数据长度] [N字节: 数据] [4字节: 校验和]
    """
    
    # 已知数据包类型
    PACKET_TYPES = {
        0x01: "LOGIN",
        0x02: "GAME",
        0x03: "CHAT",
        0x04: "PLAYER",
        0x05: "WORLD",
        0x06: "ENTITY",
        0x07: "INVENTORY",
        0x08: "BLOCK",
        0xFF: "HEARTBEAT"
    }
    
    def __init__(self):
        self.validation_stats = {
            "total_packets": 0,
            "valid_packets": 0,
            "invalid_packets": 0,
            "by_type": {}
        }
    
    def validate_packet(self, data: bytes) -> PacketValidationResult:
        """
        验证单个数据包
        
        Args:
            data: 原始数据包字节
            
        Returns:
            PacketValidationResult: 验证结果
        """
        self.validation_stats["total_packets"] += 1
        
        # 最小长度检查（头部8字节）
        if len(data) < 8:
            self.validation_stats["invalid_packets"] += 1
            return PacketValidationResult(
                is_valid=False,
                error_msg=f"数据包太短（{len(data)}字节，至少需要8字节）",
                raw_data=data
            )
        
        try:
            stream = BytesIO(data)
            
            # 读取头部
            packet_type = struct.unpack('B', stream.read(1))[0]
            sub_type = struct.unpack('B', stream.read(1))[0]
            seq_id = struct.unpack('>H', stream.read(2))[0]
            data_length = struct.unpack('>I', stream.read(4))[0]
            
            # 验证数据长度
            remaining = len(data) - 8  # 减去头部
            if data_length > remaining:
                self.validation_stats["invalid_packets"] += 1
                return PacketValidationResult(
                    is_valid=False,
                    packet_type=packet_type,
                    sub_type=sub_type,
                    seq_id=seq_id,
                    data_length=data_length,
                    error_msg=f"数据长度不匹配（声明{data_length}字节，实际{remaining}字节）",
                    raw_data=data
                )
            
            # 验证通过
            self.validation_stats["valid_packets"] += 1
            
            # 更新统计
            type_name = self.PACKET_TYPES.get(packet_type, f"UNKNOWN(0x{packet_type:02X})")
            if type_name not in self.validation_stats["by_type"]:
                self.validation_stats["by_type"][type_name] = 0
            self.validation_stats["by_type"][type_name] += 1
            
            return PacketValidationResult(
                is_valid=True,
                packet_type=packet_type,
                sub_type=sub_type,
                seq_id=seq_id,
                data_length=data_length,
                raw_data=data
            )
            
        except struct.error as e:
            self.validation_stats["invalid_packets"] += 1
            return PacketValidationResult(
                is_valid=False,
                error_msg=f"结构解析错误: {e}",
                raw_data=data
            )
        except Exception as e:
            self.validation_stats["invalid_packets"] += 1
            return PacketValidationResult(
                is_valid=False,
                error_msg=f"未知错误: {e}",
                raw_data=data
            )
    
    def validate_pcap_data(self, data: bytes, chunk_size: int = 1024) -> List[PacketValidationResult]:
        """
        验证PCAP抓包数据
        
        Args:
            data: PCAP文件原始数据
            chunk_size: 分块大小
            
        Returns:
            List[PacketValidationResult]: 验证结果列表
        """
        results = []
        
        # 简单的启发式分析：寻找可能的数据包边界
        # 实际应该使用scapy解析PCAP文件
        offset = 0
        while offset < len(data) - 8:
            # 尝试解析数据包
            result = self.validate_packet(data[offset:offset+chunk_size])
            results.append(result)
            
            if result.is_valid and result.data_length:
                # 移动到下一个数据包
                offset += 8 + result.data_length
            else:
                # 无效数据包，移动1字节继续尝试
                offset += 1
        
        return results
    
    def generate_report(self, output_file: str = None) -> str:
        """
        生成验证报告
        
        Args:
            output_file: 输出文件路径（可选）
            
        Returns:
            str: 报告内容
        """
        report = []
        report.append("=" * 70)
        report.append(" 迷你世界协议验证报告")
        report.append(f" 版本: v0.2.2_26w09a_Phase 1")
        report.append("=" * 70)
        report.append("")
        
        # 统计信息
        report.append("【统计信息】")
        report.append(f" 总数据包数: {self.validation_stats['total_packets']}")
        report.append(f" 有效数据包: {self.validation_stats['valid_packets']}")
        report.append(f" 无效数据包: {self.validation_stats['invalid_packets']}")
        
        if self.validation_stats['total_packets'] > 0:
            valid_rate = (self.validation_stats['valid_packets'] / self.validation_stats['total_packets']) * 100
            report.append(f" 有效率: {valid_rate:.2f}%")
        
        report.append("")
        
        # 按类型统计
        if self.validation_stats['by_type']:
            report.append("【数据包类型分布】")
            for type_name, count in sorted(self.validation_stats['by_type'].items(), key=lambda x: -x[1]):
                report.append(f"  {type_name}: {count}")
            report.append("")
        
        # 已知数据包类型
        report.append("【已知数据包类型】")
        for type_id, type_name in self.PACKET_TYPES.items():
            report.append(f"  0x{type_id:02X}: {type_name}")
        report.append("")
        
        # 结论
        report.append("【验证结论】")
        if self.validation_stats['valid_packets'] > 0:
            report.append("  ✓ 发现符合推测格式的数据包")
            report.append("  ✓ 协议结构推测可能正确")
        else:
            report.append("  ⚠ 未发现符合推测格式的数据包")
            report.append("  ⚠ 协议结构可能需要重新分析")
        report.append("")
        
        report.append("=" * 70)
        
        report_text = "\n".join(report)
        
        # 保存到文件
        if output_file:
            Path(output_file).write_text(report_text, encoding='utf-8')
            logger.info(f"报告已保存到: {output_file}")
        
        return report_text


class ProtocolTester:
    """协议测试器"""
    
    def __init__(self):
        self.validator = MiniWorldPacketValidator()
    
    def test_sample_packets(self) -> None:
        """测试示例数据包"""
        logger.info("=" * 70)
        logger.info(" 协议验证测试 - v0.2.2_26w09a_Phase 1")
        logger.info("=" * 70)
        
        # 测试用例1: 有效的登录包
        login_packet = struct.pack('>BBHI', 0x01, 0x00, 0x0001, 0x10) + b'\x00' * 16 + b'\x00' * 4
        result = self.validator.validate_packet(login_packet)
        logger.info(f"\n[测试1] 登录数据包")
        logger.info(f"  结果: {'✓ 有效' if result.is_valid else '✗ 无效'}")
        logger.info(f"  类型: 0x{result.packet_type:02X} ({self.validator.PACKET_TYPES.get(result.packet_type, 'UNKNOWN')})")
        logger.info(f"  子类型: 0x{result.sub_type:02X}")
        logger.info(f"  序列号: {result.seq_id}")
        logger.info(f"  数据长度: {result.data_length}")
        
        # 测试用例2: 太短的包
        short_packet = b'\x01\x02\x00\x01'
        result = self.validator.validate_packet(short_packet)
        logger.info(f"\n[测试2] 过短数据包")
        logger.info(f"  结果: {'✓ 有效' if result.is_valid else '✗ 无效'}")
        logger.info(f"  错误: {result.error_msg}")
        
        # 测试用例3: 长度不匹配
        bad_length_packet = struct.pack('>BBHI', 0x02, 0x01, 0x0002, 0x100) + b'\x00' * 8
        result = self.validator.validate_packet(bad_length_packet)
        logger.info(f"\n[测试3] 长度不匹配数据包")
        logger.info(f"  结果: {'✓ 有效' if result.is_valid else '✗ 无效'}")
        logger.info(f"  错误: {result.error_msg}")
        
        # 测试用例4: 游戏数据包
        game_packet = struct.pack('>BBHI', 0x02, 0x05, 0x0010, 0x20) + b'\xAB' * 32 + b'\x00' * 4
        result = self.validator.validate_packet(game_packet)
        logger.info(f"\n[测试4] 游戏数据包")
        logger.info(f"  结果: {'✓ 有效' if result.is_valid else '✗ 无效'}")
        logger.info(f"  类型: 0x{result.packet_type:02X} ({self.validator.PACKET_TYPES.get(result.packet_type, 'UNKNOWN')})")
        
        # 生成报告
        logger.info("\n" + "=" * 70)
        report = self.validator.generate_report()
        print(report)


def main():
    """主函数"""
    tester = ProtocolTester()
    tester.test_sample_packets()


if __name__ == "__main__":
    main()
