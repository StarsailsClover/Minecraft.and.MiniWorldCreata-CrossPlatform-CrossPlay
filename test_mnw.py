"""
MNW 协议处理器测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import struct
from dataclasses import dataclass
from typing import Optional
from enum import IntEnum

# 模拟 protobuf 编解码
class WireType:
    VARINT = 0
    FIXED64 = 1
    LENGTH_DELIMITED = 2
    START_GROUP = 3
    END_GROUP = 4
    FIXED32 = 5

def encode_varint(value: int) -> bytes:
    result = []
    while value > 127:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value)
    return bytes(result)

def decode_varint(data: bytes, offset: int = 0) -> tuple:
    value = 0
    shift = 0
    while True:
        if offset >= len(data):
            raise ValueError("Incomplete varint")
        byte = data[offset]
        value |= (byte & 0x7F) << shift
        offset += 1
        if not (byte & 0x80):
            break
        shift += 7
        if shift >= 64:
            raise ValueError("Varint too long")
    return value, offset

def zigzag_encode(n: int) -> int:
    return (n << 1) ^ (n >> 63)

def zigzag_decode(n: int) -> int:
    return (n >> 1) ^ -(n & 1)

def make_tag(field_number: int, wire_type: int) -> int:
    return (field_number << 3) | wire_type

def parse_tag(tag: int) -> tuple:
    return (tag >> 3), (tag & 0x07)

@dataclass
class PB_Vector3:
    X: int = 0
    Y: int = 0
    Z: int = 0
    
    def encode(self) -> bytes:
        data = b''
        data += bytes([make_tag(1, WireType.VARINT)]) + encode_varint(zigzag_encode(self.X))
        data += bytes([make_tag(2, WireType.VARINT)]) + encode_varint(zigzag_encode(self.Y))
        data += bytes([make_tag(3, WireType.VARINT)]) + encode_varint(zigzag_encode(self.Z))
        return data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['PB_Vector3']:
        try:
            obj = cls()
            offset = 0
            while offset < len(data):
                tag, offset = decode_varint(data, offset)
                field_num, wire_type = parse_tag(tag)
                if wire_type == WireType.VARINT:
                    value, offset = decode_varint(data, offset)
                    decoded_value = zigzag_decode(value)
                    if field_num == 1:
                        obj.X = decoded_value
                    elif field_num == 2:
                        obj.Y = decoded_value
                    elif field_num == 3:
                        obj.Z = decoded_value
                else:
                    if wire_type == WireType.FIXED64:
                        offset += 8
                    elif wire_type == WireType.FIXED32:
                        offset += 4
                    elif wire_type == WireType.LENGTH_DELIMITED:
                        length, offset = decode_varint(data, offset)
                        offset += length
                    else:
                        break
            return obj
        except:
            return None

@dataclass
class PB_HeartBeatCH:
    BeatCode: int = 0
    server_time: int = 0
    client_time: int = 0
    
    def encode(self) -> bytes:
        data = b''
        data += bytes([make_tag(1, WireType.VARINT)]) + encode_varint(self.BeatCode)
        data += bytes([make_tag(2, WireType.VARINT)]) + encode_varint(self.server_time)
        data += bytes([make_tag(3, WireType.VARINT)]) + encode_varint(self.client_time)
        return data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['PB_HeartBeatCH']:
        try:
            obj = cls()
            offset = 0
            while offset < len(data):
                tag, offset = decode_varint(data, offset)
                field_num, wire_type = parse_tag(tag)
                if wire_type == WireType.VARINT:
                    value, offset = decode_varint(data, offset)
                    if field_num == 1:
                        obj.BeatCode = value
                    elif field_num == 2:
                        obj.server_time = value
                    elif field_num == 3:
                        obj.client_time = value
                else:
                    if wire_type == WireType.FIXED64:
                        offset += 8
                    elif wire_type == WireType.FIXED32:
                        offset += 4
                    elif wire_type == WireType.LENGTH_DELIMITED:
                        length, offset = decode_varint(data, offset)
                        offset += length
                    else:
                        break
            return obj
        except:
            return None


# MNW 协议定义
class MNWProtoID(IntEnum):
    PROTO_2020 = 0x7E4  # Vector3
    PROTO_2029 = 0x7ED  # HeartBeat
    PROTO_2034 = 0x7F2  # 角色进入世界

@dataclass
class MNWPacket:
    proto_id: int
    uin: int
    data: bytes
    target_uin: Optional[int] = None
    
    def encode(self) -> bytes:
        header = struct.pack('>HQ', self.proto_id, self.uin)
        data_len = len(self.data)
        return header + struct.pack('>I', data_len) + self.data
    
    @classmethod
    def decode(cls, data: bytes) -> Optional['MNWPacket']:
        if len(data) < 14:
            return None
        try:
            proto_id, uin = struct.unpack('>HQ', data[:10])
            data_len = struct.unpack('>I', data[10:14])[0]
            if len(data) < 14 + data_len:
                return None
            payload = data[14:14+data_len]
            return cls(proto_id=proto_id, uin=uin, data=payload)
        except:
            return None


class MNWCodec:
    def __init__(self):
        self.proto_map = {
            MNWProtoID.PROTO_2034: "PB_ROLE_ENTER_WORLD_CH",
            MNWProtoID.PROTO_2020: "PB_Vector3",
            MNWProtoID.PROTO_2029: "PB_HeartBeatCH",
        }
    
    def encode_packet(self, packet: MNWPacket) -> bytes:
        return packet.encode()
    
    def decode_packet(self, data: bytes) -> Optional[MNWPacket]:
        return MNWPacket.decode(data)
    
    def create_vector3_packet(self, uin: int, x: int, y: int, z: int) -> MNWPacket:
        pb = PB_Vector3(X=x, Y=y, Z=z)
        return MNWPacket(
            proto_id=MNWProtoID.PROTO_2020,
            uin=uin,
            data=pb.encode()
        )
    
    def create_heartbeat_packet(self, uin: int, beat_code: int, 
                                server_time: int, client_time: int) -> MNWPacket:
        pb = PB_HeartBeatCH(BeatCode=beat_code, server_time=server_time, client_time=client_time)
        return MNWPacket(
            proto_id=MNWProtoID.PROTO_2029,
            uin=uin,
            data=pb.encode()
        )


def test_mnw_packet():
    print("=" * 50)
    print("测试 MNWPacket 编解码")
    print("=" * 50)
    
    packet = MNWPacket(
        proto_id=MNWProtoID.PROTO_2020,
        uin=2056826320,
        data=b"Hello, MNW!"
    )
    
    encoded = packet.encode()
    print(f"编码后的数据: {encoded.hex()}")
    print(f"数据长度: {len(encoded)} bytes")
    
    decoded = MNWPacket.decode(encoded)
    if decoded:
        print(f"解码成功!")
        print(f"  proto_id: {hex(decoded.proto_id)}")
        print(f"  uin: {decoded.uin}")
        print(f"  data: {decoded.data}")
        return True
    else:
        print("解码失败!")
        return False


def test_mnw_vector3():
    print("\n" + "=" * 50)
    print("测试 MNW Vector3 编解码")
    print("=" * 50)
    
    codec = MNWCodec()
    packet = codec.create_vector3_packet(
        uin=2056826320,
        x=100,
        y=64,
        z=-50
    )
    
    print(f"原始 Vector3: X=100, Y=64, Z=-50")
    print(f"编码后的数据: {packet.encode().hex()}")
    
    # 解码并解析
    decoded = MNWPacket.decode(packet.encode())
    if decoded:
        pb = PB_Vector3.decode(decoded.data)
        if pb:
            print(f"解码后的 Vector3: X={pb.X}, Y={pb.Y}, Z={pb.Z}")
            if pb.X == 100 and pb.Y == 64 and pb.Z == -50:
                print("✓ 数据匹配!")
                return True
            else:
                print("✗ 数据不匹配!")
                return False
        else:
            print("PB_Vector3 解码失败!")
            return False
    else:
        print("MNWPacket 解码失败!")
        return False


def test_mnw_heartbeat():
    print("\n" + "=" * 50)
    print("测试 MNW HeartBeat 编解码")
    print("=" * 50)
    
    codec = MNWCodec()
    packet = codec.create_heartbeat_packet(
        uin=2056826320,
        beat_code=12345,
        server_time=1773418347,
        client_time=1773418348
    )
    
    print(f"原始 HeartBeat: BeatCode=12345, server_time=1773418347, client_time=1773418348")
    print(f"编码后的数据: {packet.encode().hex()}")
    
    decoded = MNWPacket.decode(packet.encode())
    if decoded:
        pb = PB_HeartBeatCH.decode(decoded.data)
        if pb:
            print(f"解码后的 HeartBeat: BeatCode={pb.BeatCode}, server_time={pb.server_time}, client_time={pb.client_time}")
            if pb.BeatCode == 12345 and pb.server_time == 1773418347 and pb.client_time == 1773418348:
                print("✓ 数据匹配!")
                return True
            else:
                print("✗ 数据不匹配!")
                return False
        else:
            print("PB_HeartBeatCH 解码失败!")
            return False
    else:
        print("MNWPacket 解码失败!")
        return False


def main():
    print("\n" + "=" * 60)
    print("MNW 协议处理器测试套件")
    print("=" * 60)
    
    tests = [
        ("MNWPacket 编解码", test_mnw_packet),
        ("MNW Vector3 编解码", test_mnw_vector3),
        ("MNW HeartBeat 编解码", test_mnw_heartbeat),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✓ {name} - 通过")
            else:
                failed += 1
                print(f"\n✗ {name} - 失败")
        except Exception as e:
            failed += 1
            print(f"\n✗ {name} - 异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{len(tests)} 通过, {failed}/{len(tests)} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
