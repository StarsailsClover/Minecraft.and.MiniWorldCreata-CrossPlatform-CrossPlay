# MnMCP API 文档

## 核心模块

### ProxyServer

代理服务器主类

```python
from core.proxy_server import ProxyServer
from core.session_manager import SessionManager

# 创建会话管理器
session_manager = SessionManager()

# 创建代理服务器
server = ProxyServer(
    host="0.0.0.0",
    port=25565,
    session_manager=session_manager
)

# 启动服务器
await server.start()

# 停止服务器
await server.stop()
```

#### 方法

##### `start()`
启动代理服务器

##### `stop()`
停止代理服务器

##### `get_stats()`
获取服务器统计信息

**返回**: `dict`
```python
{
    "total_connections": 10,
    "active_connections": 5,
    "uptime": "running"
}
```

---

### ProtocolTranslator

协议翻译器

```python
from core.protocol_translator import ProtocolTranslator

# 创建翻译器
translator = ProtocolTranslator(region="CN")

# MC -> MNW 翻译
mnw_packet = translator.mc_to_mnw(mc_packet)

# MNW -> MC 翻译
mc_packet = translator.mnw_to_mc(mnw_packet)
```

#### 方法

##### `mc_to_mnw(mc_packet: bytes) -> Optional[bytes]`
将Minecraft数据包翻译为迷你世界数据包

**参数**:
- `mc_packet`: Minecraft原始数据包

**返回**: 迷你世界数据包或None

##### `mnw_to_mc(mnw_packet: bytes) -> Optional[bytes]`
将迷你世界数据包翻译为Minecraft数据包

**参数**:
- `mnw_packet`: 迷你世界原始数据包

**返回**: Minecraft数据包或None

##### `get_stats() -> dict`
获取翻译统计

**返回**:
```python
{
    "packets_translated": 100,
    "errors": 5,
    "state": "play",
    "mc_username": "Player",
    "mnw_account_id": "12345678"
}
```

---

## 编解码器

### MinecraftCodec

Minecraft协议编解码器

```python
from codec.mc_codec import MinecraftCodec

codec = MinecraftCodec()

# 创建握手包
handshake = codec.create_handshake(
    protocol_version=766,
    server_address="localhost",
    server_port=25565,
    next_state=2
)

# 创建登录包
login = codec.create_login_start("PlayerName")

# 创建聊天包
chat = codec.create_chat_message("Hello!")

# 编码数据包
packet = codec.encode_packet(packet_id=0x00, data=data)

# 解码数据包
decoded = codec.decode_packet(data)
```

#### 方法

##### `create_handshake(protocol_version, server_address, server_port, next_state) -> bytes`
创建握手包

##### `create_login_start(username, uuid_str=None) -> bytes`
创建登录开始包

##### `create_keep_alive(keep_alive_id) -> bytes`
创建心跳包

##### `create_chat_message(message) -> bytes`
创建聊天消息包

##### `encode_packet(packet_id, data) -> bytes`
编码数据包

##### `decode_packet(data) -> Optional[MCPacket]`
解码数据包

---

### MiniWorldCodec

迷你世界协议编解码器

```python
from codec.mnw_codec import MiniWorldCodec

codec = MiniWorldCodec()

# 创建登录请求
login = codec.create_login_request(
    account_id="12345678",
    token="access_token"
)

# 创建聊天消息
chat = codec.create_chat_message("Hello!", room_id="room_001")

# 创建移动包
move = codec.create_move_packet(x=100.0, y=64.0, z=200.0)

# 创建方块放置包
block = codec.create_block_place(x=10, y=20, z=30, block_id=1)
```

#### 方法

##### `create_login_request(account_id, token, version="1.53.1") -> bytes`
创建登录请求包

##### `create_heartbeat() -> bytes`
创建心跳包

##### `create_chat_message(message, room_id="") -> bytes`
创建聊天消息包

##### `create_move_packet(x, y, z, yaw=0.0, pitch=0.0) -> bytes`
创建移动包

##### `create_block_place(x, y, z, block_id, meta=0) -> bytes`
创建方块放置包

##### `create_block_break(x, y, z) -> bytes`
创建方块破坏包

---

## 加密模块

### MiniWorldEncryption

迷你世界加密管理器

```python
from crypto.aes_crypto import MiniWorldEncryption

# 创建加密管理器（国服）
encryption = MiniWorldEncryption(region="CN")

# 设置会话密钥
encryption.set_session_key(b'1234567890123456')

# 加密数据
encrypted = encryption.encrypt(b"Hello, MiniWorld!")

# 解密数据
decrypted = encryption.decrypt(encrypted)
```

#### 方法

##### `set_session_key(key: bytes)`
设置会话密钥

##### `encrypt(data: bytes) -> bytes`
加密数据

##### `decrypt(data: bytes) -> bytes`
解密数据

---

## 协议模块

### BlockMapper

方块映射器

```python
from protocol.block_mapper import BlockMapper

# 创建映射器
mapper = BlockMapper("data/block_mappings.json")

# MC -> MNW 转换
mnw_id, meta = mapper.mc_to_mnw_block(mc_id=1, mc_meta=0)

# MNW -> MC 转换
mc_id, meta = mapper.mnw_to_mc_block(mnw_id=1, mnw_meta=0)

# 获取方块名称
name = mapper.get_mc_block_name(1)  # "石头"

# 获取统计
stats = mapper.get_stats()
```

#### 方法

##### `mc_to_mnw_block(mc_id, mc_meta=0) -> Tuple[int, int]`
将Minecraft方块ID转换为迷你世界方块ID

##### `mnw_to_mc_block(mnw_id, mnw_meta=0) -> Tuple[int, int]`
将迷你世界方块ID转换为Minecraft方块ID

##### `get_mc_block_name(mc_id) -> str`
获取Minecraft方块名称

##### `get_mnw_block_name(mnw_id) -> str`
获取迷你世界方块名称

##### `get_stats() -> dict`
获取映射统计

---

### CoordinateConverter

坐标转换器

```python
from protocol.coordinate_converter import CoordinateConverter, Vector3

converter = CoordinateConverter()

# MC -> MNW 坐标转换
mc_pos = Vector3(100.0, 64.0, 200.0)
mnw_pos = converter.mc_to_mnw_position(mc_pos)

# MNW -> MC 坐标转换
back_to_mc = converter.mnw_to_mc_position(mnw_pos)
```

#### 方法

##### `mc_to_mnw_position(mc_pos: Vector3) -> Vector3`
将Minecraft坐标转换为迷你世界坐标

##### `mnw_to_mc_position(mnw_pos: Vector3) -> Vector3`
将迷你世界坐标转换为Minecraft坐标

---

## 工具模块

### ConfigManager

配置管理器

```python
from utils.config_manager import ConfigManager

# 加载配置
config = ConfigManager("config.json")

# 获取配置值
port = config.get("server.port", 25565)
host = config.get("server.host", "0.0.0.0")

# 设置配置值
config.set("server.port", 25566)

# 保存配置
config.save()

# 获取所有配置
all_config = config.get_all()
```

#### 方法

##### `get(key, default=None) -> Any`
获取配置值

##### `set(key, value)`
设置配置值

##### `save()`
保存配置到文件

##### `get_all() -> dict`
获取所有配置

---

### Logger

日志管理器

```python
from utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("MyModule", level="INFO")

# 使用日志
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

---

## 数据类型

### Vector3

三维向量

```python
from protocol.coordinate_converter import Vector3

# 创建向量
pos = Vector3(x=100.0, y=64.0, z=200.0)

# 访问分量
print(pos.x, pos.y, pos.z)
```

### MCPacket

Minecraft数据包

```python
from codec.mc_codec import MCPacket

packet = MCPacket(packet_id=0x00, data=b"...")

# 编码
encoded = packet.encode()

# 解码
decoded = MCPacket.decode(data)
```

### MNWPacket

迷你世界数据包

```python
from codec.mnw_codec import MNWPacket

packet = MNWPacket(
    packet_type=0x01,
    sub_type=0x01,
    data=b"...",
    seq_id=1
)

# 编码
encoded = packet.encode()

# 解码
decoded = MNWPacket.decode(data)
```

---

## 常量

### Minecraft 协议版本

```python
from codec.mc_codec import MinecraftCodec

print(MinecraftCodec.PROTOCOL_VERSION)  # 766
```

### 迷你世界 包类型

```python
from codec.mnw_codec import MiniWorldCodec

print(MiniWorldCodec.PACKET_LOGIN)      # 0x01
print(MiniWorldCodec.PACKET_GAME)       # 0x02
print(MiniWorldCodec.PACKET_CHAT)       # 0x03
print(MiniWorldCodec.PACKET_MOVE)       # 0x04
print(MiniWorldCodec.PACKET_BLOCK)      # 0x05
print(MiniWorldCodec.PACKET_HEARTBEAT)  # 0xFF
```

---

## 示例

### 完整示例

```python
import asyncio
from core.proxy_server import ProxyServer
from core.session_manager import SessionManager
from utils.config_manager import ConfigManager
from utils.logger import setup_logger

logger = setup_logger("Example")

async def main():
    # 加载配置
    config = ConfigManager("config.json")
    
    # 创建会话管理器
    session_manager = SessionManager()
    
    # 创建代理服务器
    server = ProxyServer(
        host=config.get("server.host"),
        port=config.get("server.port"),
        session_manager=session_manager,
        config=config
    )
    
    # 启动服务器
    logger.info("Starting server...")
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 更多信息

- [使用指南](USAGE.md)
- [协议分析](PROTOCOL.md)
- [常见问题](FAQ.md)
