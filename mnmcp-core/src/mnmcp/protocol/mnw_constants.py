"""
MNW 消息类型 - 基于抓包分析 v1.1

来源: mini.pcapng (127MB) 抓包分析
日期: 2026-03-14

重要发现:
  1. 消息类型 1000-1200 主要是 HTTP/TLS 层 (port 19921, 8080)
  2. 消息类型 3000+ 主要是 TCP 游戏层 (port 4012)
  3. 大量 50-byte 包可能是 ACK 或控制包
  4. 1003-byte 包可能是游戏数据
"""

from enum import IntEnum


class MNWMsgType(IntEnum):
    """
    迷你世界消息类型 - 基于抓包校准
    
    来自 127MB 抓包分析 (mini.pcapng)
    """
    
    # ── HTTP/HTTPS 认证层 ──
    # 这些实际上不是游戏消息，而是 HTTP API
    # 但为了完整性保留
    
    # ── TCP 游戏层 (抓取到) ──
    ROLE_ENTER_WORLD = 1001      # 0x03E9 ✅ 找到 1 个, 993 bytes
    
    # 1005, 1007, 1008: 50 bytes (可能是简单状态)
    ROLE_ACTION_1005 = 1005
    ROLE_ACTION_1007 = 1007
    ROLE_ACTION_1008 = 1008
    
    CREATE_BLOCK = 1010          # 0x03F2 ✅ 2 个, 1002 bytes
    DESTROY_BLOCK = 1011         # 0x03F3 ✅ 34 个, 1003 bytes (已知类型！)
    
    # 1014: 50 bytes
    ROLE_ACTION_1014 = 1014
    
    # 50-byte 控制包 (大量，可能是心跳或 ACK)
    HEARTBEAT_SMALL = 3003       # 可能，需要验证
    CONTROL_SMALL = 50           # 字节标记
    
    # 更大消息 (3000+ 区间)
    LOGIN_REQ = 3001
    LOGIN_RESP = 3002
    HEARTBEAT = 3003
    
    # 高频未知消息 (从之前分析)
    HIGH_FREQ_1294 = 1294        # 75480 次, 1294 bytes - 位置同步？
    HIGH_FREQ_1454 = 1454        # 16172 次, 1454 bytes
    HIGH_FREQ_1328 = 1328        # 2701 次, 1015 bytes


class MNWPort(IntEnum):
    """服务器端口"""
    CERTIFICATION_HTTPS = 19921    # 认证 (TLS)
    OPENROOM_HTTPS = 8080          # 房间分配 (TLS)
    CHATPUSH_ALLOC_WSS = 19601     # WebSocket 分配
    CHATPUSH_WSS = 19701           # WebSocket 聊天
    GAME_TCP = 4012                # 游戏服务器 TCP
    
    
class MNWVersion:
    """客户端版本"""
    API_CLIENT_VERSION = "79105"     # 从 JWT payload
    VERSION_STRING = "1.53.1"

# 基于 JWT 分析更新的认证配置

class AuthEndpoints:
    """认证服务端点 - 基于抓包分析"""
    
    # HTTPS API
    CERTIFICATION_LOGIN = "https://certification.mini1.cn:19921/login"
    CERTIFICATION_LOGOUT = "https://certification.mini1.cn:19921/logout"
    
    OPENROOM_ALLOC = "https://openroom.mini1.cn:8080/alloc"
    
    # WebSocket
    CHATPUSH_ALLOC_WS = "wss://chatpush.mini1.cn:19601"
    CHATPUSH_MAIN_WS = "wss://chatpush.mini1.cn:19701"
    
    # TCP
    GAME_SERVER = "cn-logic.mini1.cn"
    GAME_PORT = 4012


class JWTPayload:
    """
    JWT Payload 结构 - 基于实际提取
    
    Example from mini.pcapng:
    {
        "uin": 2056826320,
        "time": 1773484435,      // Unix timestamp
        "flag": 1,              // 认证标志
        "iss": "imserver",        // 签发者
        "env": 0,
        "auth": "web",
        "ts": 1773484434,
        "apiid": 110,
        "cltversion": "79105",
        "src": "login_v3",
        "deviceid": "WIN9e40eedc04a71931ece88472bb778bc4",
        "ip": "117.62.151.241",
        "its": 1773484435
    }
    """
    pass


class LoginFlow:
    """
    完整登录流程 - 基于抓包重建
    
    Step 1: HTTPS POST certification.mini1.cn:19921/login
            ├─ Headers: Content-Type: application/json
            └─ Body: {uin, password, deviceid, appid, version, platform}
            ← Response: {code: 0, data: {token: <JWT>}}
    
    Step 2: HTTPS POST openroom.mini1.cn:8080/alloc
            ├─ Headers: Authorization: Bearer <JWT>
            └─ Body: {room_type, appid, version}
            ← Response: {game_server_ip, game_server_port}
    
    Step 3: TCP Connect game_server:4012
            → Socket connect
    
    Step 4: TCP Send LOGIN_REQ (3001)
            → MNW Header: [length=12+JWT_len][msg_type=3001]
            → Payload: JWT Token (Protobuf encoded)
            ← Receive LOGIN_RESP (3002)
            ← Payload: {success, session_key}
    
    Step 5: Initialize AES
            → session_key → AES-128-CBC
            → IV: first 16 bytes of encrypted packet or derived
    
    Step 6: WebSocket Connect chatpush.mini1.cn:19701
            → wss://chatpush.mini1.cn:19701?token=<JWT>
            ← Connection established
    """
    
    @staticmethod
    def get_step_name(step: int) -> str:
        names = {
            1: "HTTPS Login",
            2: "HTTPS Room Alloc",
            3: "TCP Connect",
            4: "MNW Login Handshake",
            5: "AES Init",
            6: "WebSocket Connect",
        }
        return names.get(step, "Unknown")
