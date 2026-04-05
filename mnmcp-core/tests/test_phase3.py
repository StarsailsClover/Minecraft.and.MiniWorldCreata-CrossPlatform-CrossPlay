"""Phase 3 集成测试"""
import pytest
from mnmcp.protocol.mnw_protocol import MNWMsgType, MNWCodec


class TestMNWProtocolSamples:
    """测试协议样本"""
    
    def test_sample_role_enter_world(self):
        """测试角色进入世界样本"""
        data = bytes.fromhex(
            "1c000000"
            "e9030000"
            "08b960"
            "120f"
            "0d0000c842"
            "1500008042"
            "1d00004843"
        )
        
        result = MNWCodec.decode_packet(data)
        assert result is not None
        assert result["msg_type"] == MNWMsgType.ROLE_ENTER_WORLD
        assert result["fields"].get(1) == 12345


class TestConfigWatcher:
    """测试配置热加载"""
    
    def test_config_section_access(self):
        """测试配置节访问"""
        from mnmcp.utils import Config
        cfg = Config()
        val = cfg.get("server.host")
        assert val == "0.0.0.0"


class TestLogging:
    """测试日志系统"""
    
    def test_structured_logger(self):
        """测试结构化日志"""
        from mnmcp.utils import StructuredLogger
        logger = StructuredLogger("test")
        # 不会抛出异常
        logger.info("Test message", extra_field="value")
