"""
mnmcp-core 基础测试
pytest 标准格式
"""

import struct
import pytest


class TestMapping:
    """映射层测试"""

    def test_coordinate_converter(self):
        from mnmcp.mapping import CoordinateConverter, Vec3
        conv = CoordinateConverter()

        mc_pos = Vec3(100.0, 64.0, 200.0)
        mnw_pos = conv.mc_to_mnw(mc_pos)

        assert mnw_pos.x == -100.0  # X 轴取反
        assert mnw_pos.y == 64.0
        assert mnw_pos.z == 200.0

        # 往返转换
        back = conv.mnw_to_mc(mnw_pos)
        assert abs(back.x - mc_pos.x) < 0.01
        assert abs(back.y - mc_pos.y) < 0.01
        assert abs(back.z - mc_pos.z) < 0.01

    def test_block_mapper_loads(self):
        from mnmcp.mapping import BlockMapper
        mapper = BlockMapper()
        # 应该能加载到映射数据
        assert mapper.count > 0

    def test_block_mapper_bidirectional(self):
        from mnmcp.mapping import BlockMapper
        mapper = BlockMapper()
        if mapper.count == 0:
            pytest.skip("无映射数据")
        # 取第一个映射测试双向
        mc_id = next(iter(mapper.mc_to_mnw.keys()))
        mnw_id = mapper.get_mnw_id(mc_id)
        back = mapper.get_mc_id(mnw_id)
        assert back == mc_id


class TestCrypto:
    """加密层测试"""

    def test_aes_cbc_roundtrip(self):
        from mnmcp.crypto import AESCipher
        key = b"1234567890123456"  # 128-bit
        cipher = AESCipher(key)
        plaintext = b"Hello, MiniWorld! This is a test message."
        encrypted = cipher.encrypt_cbc(plaintext)
        decrypted = cipher.decrypt_cbc(encrypted)
        assert decrypted == plaintext

    def test_aes_gcm_roundtrip(self):
        from mnmcp.crypto import AESCipher
        key = b"12345678901234567890123456789012"  # 256-bit
        cipher = AESCipher(key)
        plaintext = b"Hello, GCM mode!"
        encrypted = cipher.encrypt_gcm(plaintext)
        decrypted = cipher.decrypt_gcm(encrypted)
        assert decrypted == plaintext

    def test_aes_invalid_key_length(self):
        from mnmcp.crypto import AESCipher
        with pytest.raises(ValueError):
            AESCipher(b"short")

    def test_password_hash_cn(self):
        from mnmcp.crypto import PasswordHasher
        h = PasswordHasher.hash_cn("password123")
        assert len(h) == 32  # MD5 hex
        assert h == PasswordHasher.hash_cn("password123")  # 确定性

    def test_password_verify(self):
        from mnmcp.crypto import PasswordHasher
        hashed = PasswordHasher.hash_cn("mypassword", "salt123")
        assert PasswordHasher.verify("mypassword", hashed, "salt123")
        assert not PasswordHasher.verify("wrong", hashed, "salt123")

    def test_session_crypto(self):
        from mnmcp.crypto import SessionCrypto
        sc = SessionCrypto(region="CN")
        assert not sc.encrypted
        # 明文阶段
        data = b"plaintext data"
        assert sc.encrypt(data) == data
        # 激活加密
        sc.activate(b"1234567890123456")
        assert sc.encrypted
        encrypted = sc.encrypt(data)
        assert encrypted != data
        decrypted = sc.decrypt(encrypted)
        assert decrypted == data


class TestProtocol:
    """协议层测试"""

    def test_varint_encode_decode(self):
        from mnmcp.protocol import VarInt
        for value in [0, 1, 127, 128, 255, 300, 25565, 65535]:
            encoded = VarInt.encode(value)
            decoded, consumed = VarInt.decode(encoded)
            assert decoded == value

    def test_mc_codec_chat(self):
        from mnmcp.protocol import MCCodec, MCPacketID, VarInt, GameAction
        # 构造一个聊天包
        msg = "Hello World"
        msg_bytes = msg.encode("utf-8")
        payload = bytes([0x01]) + VarInt.encode(len(msg_bytes)) + msg_bytes
        raw = VarInt.encode(MCPacketID.TEXT) + payload

        pkt = MCCodec.decode_packet(raw)
        assert pkt is not None
        assert pkt.action == GameAction.CHAT_MESSAGE
        assert pkt.message == msg

    def test_mnw_codec_heartbeat(self):
        from mnmcp.protocol import MNWCodec, MNWMsgType, GameAction
        raw = struct.pack("<II", 8, MNWMsgType.HEARTBEAT)
        pkt = MNWCodec.decode_packet(raw)
        assert pkt is not None
        assert pkt.action == GameAction.HEARTBEAT

    def test_translator_init(self):
        from mnmcp.protocol import ProtocolTranslator
        t = ProtocolTranslator()
        assert t.block_mapper.count > 0
        assert t.mc_to_mnw_count == 0


class TestNetwork:
    """网络层测试"""

    @pytest.mark.asyncio
    async def test_session_manager(self):
        from mnmcp.network import SessionManager, Platform
        mgr = SessionManager(max_sessions=5)
        s = await mgr.create(platform=Platform.MC_BEDROCK, addr="127.0.0.1", port=12345)
        assert mgr.count == 1
        assert mgr.get(s.session_id) is s
        mgr.remove(s.session_id)
        assert mgr.count == 0

    @pytest.mark.asyncio
    async def test_session_max_limit(self):
        from mnmcp.network import SessionManager, Platform
        mgr = SessionManager(max_sessions=2)
        await mgr.create(platform=Platform.MC_BEDROCK)
        await mgr.create(platform=Platform.MC_BEDROCK)
        with pytest.raises(RuntimeError):
            await mgr.create(platform=Platform.MC_BEDROCK)

    def test_room_management(self):
        from mnmcp.network import RelayServer, Room
        relay = RelayServer()
        room = relay.create_room("Test Room", "host123")
        assert relay.get_room(room.room_id) is room
        assert len(relay.list_rooms()) == 1
        relay.delete_room(room.room_id)
        assert len(relay.list_rooms()) == 0


class TestConfig:
    """配置测试"""

    def test_default_config(self):
        from mnmcp.utils.config import Config
        # 重置单例
        Config._instance = None
        cfg = Config()
        assert cfg.get("server.mc_port") == 25565
        assert cfg.get("miniworld.version") == "1.53.1"
        assert cfg.get("nonexistent", "default") == "default"
