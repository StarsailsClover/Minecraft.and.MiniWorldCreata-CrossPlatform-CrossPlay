# 协议分析模块

本模块用于分析Minecraft和迷你世界的网络协议，构建协议映射表。

## 目录结构

```
protocol_analysis/
├── __init__.py              # 模块初始化
├── packet_analyzer.py       # 数据包分析器
├── wireshark_capture.py     # Wireshark抓包工具（待创建）
├── protocol_mapper.py       # 协议映射器（待创建）
├── id_mapping/              # ID映射表目录
│   ├── blocks.json          # 方块ID映射
│   ├── entities.json        # 实体ID映射
│   └── items.json           # 物品ID映射
└── README.md               # 本文件
```

## 当前状态

### Minecraft Java协议
- ✅ 基础数据包结构定义
- ✅ VarInt解析实现
- ✅ 字符串解析实现
- ✅ 常见数据包类型枚举

### 迷你世界协议
- ⏳ 等待APK反编译完成
- ⏳ 等待网络协议代码分析
- ⏳ 等待数据包结构逆向

### 协议映射
- ⏳ 等待ID映射表构建

## 使用方法

### 分析Minecraft数据包

```python
from protocol_analysis.packet_analyzer import MinecraftJavaProtocol

# 获取数据包信息
packet = MinecraftJavaProtocol.get_packet_info(0x0F)
print(f"Packet: {packet.name}")
print(f"Type: {packet.packet_type.value}")
print(f"Fields: {[f.name for f in packet.fields]}")

# 列出所有聊天相关数据包
chat_packets = MinecraftJavaProtocol.list_packets(PacketType.CHAT)
for p in chat_packets:
    print(f"{hex(p.packet_id)}: {p.name}")

# 解析VarInt
data = bytes([0x7F])  # 127
value, bytes_read = MinecraftJavaProtocol.parse_varint(data)
print(f"Value: {value}, Bytes: {bytes_read}")
```

### 生成协议报告

```python
from protocol_analysis.packet_analyzer import generate_protocol_report
import json

report = generate_protocol_report()
print(json.dumps(report, indent=2))
```

## 下一步工作

1. **APK反编译分析**
   - 等待反编译完成
   - 搜索网络协议相关代码
   - 提取数据包结构定义

2. **Wireshark抓包**
   - 配置抓包环境
   - 捕获真实数据包
   - 分析通信流程

3. **协议对比分析**
   - 对比迷你世界与Minecraft协议差异
   - 构建数据包映射表
   - 设计协议转换逻辑

4. **ID映射表构建**
   - 方块ID映射
   - 实体ID映射
   - 物品ID映射
   - 粒子效果映射

## 参考资料

### Minecraft协议文档
- [Wiki.vg Protocol](https://wiki.vg/Protocol)
- [Minecraft Protocol Version Numbers](https://wiki.vg/Protocol_version_numbers)

### 工具
- Wireshark - 网络抓包分析
- apktool - APK反编译
- jadx - Java反编译
- frida - 动态分析

---
Made with ❤️ by ZCNotFound for cross-platform gaming
