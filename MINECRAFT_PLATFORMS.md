# Minecraft平台适配文档

**创建时间**: 2026-02-28  
**阶段**: 第六阶段 - Minecraft平台适配  
**状态**: ✅ Java & Bedrock适配器完成

---

## 📦 新增模块

### 1. Java版适配器 (`src/minecraft/java_adapter.py`)

**功能**:
- Java版协议数据包创建和解析
- 支持1.20.6版本 (协议版本766)
- 玩家位置、聊天、方块操作

**支持的包类型**:
- Handshake (0x00)
- Login Start (0x00)
- Player Position (0x11, 0x12)
- Chat Message (0x05)
- Block Placement (0x2E)
- Player Digging (0x1A)
- Block Change (0x0B)

**关键类**:
```python
JavaAdapter()                    # 主适配器
JavaPlayerPosition(x, y, z)      # 玩家位置
JavaBlock(x, y, z, block_id)     # 方块
```

### 2. Bedrock版适配器 (`src/minecraft/bedrock_adapter.py`)

**功能**:
- Bedrock版协议数据包创建和解析
- 支持1.21.0版本 (协议版本686)
- 小端字节序处理

**支持的包类型**:
- Login (0x01)
- Play Status (0x02)
- Move Player (0x13)
- Text (0x09)
- Player Action (0x24)
- Update Block (0x15)
- Inventory Transaction (0x1E)

**关键类**:
```python
BedrockAdapter()                      # 主适配器
BedrockPlayerPosition(x, y, z)        # 玩家位置
BedrockBlock(x, y, z, block_id)       # 方块
```

### 3. 统一接口层 (`src/minecraft/unified_interface.py`)

**功能**:
- 统一Java和Bedrock的API
- 自动平台转换
- 简化跨平台开发

**关键类**:
```python
MinecraftUnifiedInterface(platform)   # 统一接口
UnifiedPlayerPosition(x, y, z)        # 统一位置
UnifiedBlock(x, y, z, block_id)       # 统一方块
PlatformType.JAVA / PlatformType.BEDROCK  # 平台类型
```

---

## 🚀 使用方法

### 基础用法

```python
from src.minecraft import create_minecraft_interface
from src.minecraft.unified_interface import UnifiedPlayerPosition, UnifiedBlock

# 创建Java版接口
java = create_minecraft_interface("java")

# 创建Bedrock版接口
bedrock = create_minecraft_interface("bedrock")

# 统一位置
pos = UnifiedPlayerPosition(100.5, 64.0, -200.3, yaw=45.0, pitch=0.0)

# Java版位置包
java_packet = java.create_position_packet(pos)

# Bedrock版位置包
bedrock_packet = bedrock.create_position_packet(pos, runtime_id=1)
```

### 创建数据包

```python
# 登录包
login_java = java.create_login_packet("PlayerName")
login_bedrock = bedrock.create_login_packet("PlayerName")

# 聊天包
chat_java = java.create_chat_packet("Hello!")
chat_bedrock = bedrock.create_chat_packet("Hello!")

# 方块放置
block = UnifiedBlock(10, 64, 20, block_id=1)  # 石头
place_java = java.create_block_placement_packet(block, face=0)
place_bedrock = bedrock.create_block_placement_packet(block, face=0)
```

### 解析数据包

```python
# 解析接收到的数据
parsed = java.parse_packet(received_data)
print(parsed["type"])  # "login_success", "chat", "block_change", etc.
```

---

## 📊 协议差异对比

| 特性 | Java版 | Bedrock版 |
|------|--------|-----------|
| 字节序 | 大端 (Big Endian) | 小端 (Little Endian) |
| 整数编码 | Varint | Varint (LEB128) |
| 位置编码 | 长整型 (压缩) | 三个Varint |
| 字符串 | UTF-8 + 长度前缀 | UTF-8 + 长度前缀 |
| 坐标系统 | double (浮点) | float (浮点) |
| 协议版本 | 766 (1.20.6) | 686 (1.21.0) |

---

## 🔧 技术细节

### Varint编码

**Java版 (大端)**:
```python
def encode_varint(value):
    result = []
    while True:
        byte = value & 0x7F
        value >>= 7
        if value != 0:
            byte |= 0x80
        result.append(byte)
        if value == 0:
            break
    return bytes(result)
```

**Bedrock版 (小端 LEB128)**:
```python
# 与Java版相同，但用于小端环境
def encode_varint(value):
    # 实现相同
    ...
```

### 位置编码

**Java版**:
```
位置 = ((X & 0x3FFFFFF) << 38) | ((Z & 0x3FFFFFF) << 12) | (Y & 0xFFF)
```

**Bedrock版**:
```
X: Varint
Y: Varint
Z: Varint
```

---

## ✅ 测试状态

| 测试项 | Java版 | Bedrock版 | 状态 |
|--------|--------|-----------|------|
| 登录包创建 | ✅ | ✅ | 通过 |
| 位置包创建 | ✅ | ✅ | 通过 |
| 聊天包创建 | ✅ | ✅ | 通过 |
| 方块包创建 | ✅ | ✅ | 通过 |
| 包解析 | ✅ | ✅ | 通过 |

---

## 📝 下一步

1. **平台特定测试**
   - 连接真实Java服务器测试
   - 连接真实Bedrock服务器测试

2. **与迷你世界桥接**
   - 实现Java <-> 迷你世界转换
   - 实现Bedrock <-> 迷你世界转换

3. **性能优化**
   - 批量数据包处理
   - 异步I/O优化

---

## 📁 文件清单

```
src/minecraft/
├── __init__.py              # 模块初始化
├── java_adapter.py          # Java版适配器 (12 KB)
├── bedrock_adapter.py       # Bedrock版适配器 (15 KB)
└── unified_interface.py     # 统一接口层 (8 KB)
```

---

**完成时间**: 2026-02-28  
**状态**: ✅ Java & Bedrock适配器开发完成
