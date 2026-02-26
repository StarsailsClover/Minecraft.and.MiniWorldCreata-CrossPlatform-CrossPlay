# 第一阶段：核心架构设计

## 完成时间：2026-02-26

---

## 一、架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                     MnMCP 协议翻译层                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Minecraft  │───▶│   Proxy      │───▶│  MiniWorld   │  │
│  │   Client     │◀───│   Server     │◀───│   Server     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  MC Protocol │    │  Translator  │    │ MNW Protocol │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                             │                              │
│                             ▼                              │
│                      ┌──────────────┐                      │
│                      │   Session    │                      │
│                      │   Manager    │                      │
│                      └──────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、核心组件

### 1. ProxyServer（代理服务器）

**文件**：`src/core/proxy_server.py`

**职责**：
- 监听Minecraft客户端连接（端口25565）
- 建立与迷你世界服务器的连接
- 管理双向数据流转发
- 维护连接统计信息

**关键类**：
- `ProxyConfig`：代理配置
- `ProxyConnection`：单个连接管理
- `ProxyServer`：主服务器类

**状态**：✅ 已完成框架，待填充协议细节

---

### 2. ProtocolTranslator（协议翻译器）

**文件**：`src/core/protocol_translator.py`

**职责**：
- Minecraft协议包解析
- 迷你世界协议包解析
- 双向协议转换
- 状态管理

**关键类**：
- `MinecraftPacket`：MC数据包结构
- `MiniWorldPacket`：MNW数据包结构
- `ProtocolTranslator`：翻译器主类

**状态**：✅ 已完成框架，待从抓包确认协议细节

**待确认**：
- [ ] 迷你世界数据包结构（需要抓包分析）
- [ ] 协议映射表（MC <-> MNW）
- [ ] 加密/解密逻辑

---

### 3. SessionManager（会话管理器）

**文件**：`src/core/session_manager.py`

**职责**：
- 管理玩家会话生命周期
- 维护MC用户名与MNW账号映射
- 房间管理
- 统计信息收集

**关键类**：
- `SessionState`：会话状态枚举
- `PlayerSession`：玩家会话数据
- `SessionManager`：会话管理器

**状态**：✅ 已完成

---

## 三、数据流

### 连接建立流程

```
1. Minecraft客户端 ──连接──▶ ProxyServer (25565端口)
2. ProxyServer ──创建──▶ PlayerSession
3. ProxyServer ──连接──▶ MiniWorld服务器
4. 双向数据流建立，开始协议翻译
```

### 数据包处理流程

```
Minecraft ──▶ ProxyServer ──▶ ProtocolTranslator ──▶ MiniWorld
   │              │                    │
   │              │                    ├── 解析MC数据包
   │              │                    ├── 协议转换
   │              │                    ├── 构建MNW数据包
   │              │                    └── 发送
   │              │
   │              └── 更新Session统计
   │
   └── 玩家操作（移动、放置方块等）
```

---

## 四、配置参数

### 代理服务器配置

```python
ProxyConfig(
    mc_host="0.0.0.0",        # Minecraft监听地址
    mc_port=25565,             # Minecraft标准端口
    mnw_host="",               # 迷你世界服务器（动态获取）
    mnw_port=0,                # 迷你世界端口（动态获取）
    protocol_version=1,        # 协议版本
    connect_timeout=30.0,      # 连接超时
    read_timeout=60.0,         # 读取超时
    buffer_size=65536          # 缓冲区大小
)
```

### 会话管理配置

```python
session_timeout_minutes = 30   # 会话超时时间
max_sessions = 100             # 最大并发会话数
```

---

## 五、关键发现（从分析中获得）

### 服务器信息

| 类型 | 国服 | 外服 |
|------|------|------|
| API服务器 | mwu-api-pre.mini1.cn | 待抓包确认 |
| CDN服务器 | mwu-cdn-pre.mini1.cn | mwu-cdn2.miniworldgame.com |

### 登录认证

| 类型 | 国服 | 外服 |
|------|------|------|
| 方式 | 迷你号/手机号 | Google/Facebook/Apple/Twitter |
| 加密 | AES-128-CBC（预期） | AES-256-GCM（预期） |

### APK差异

| 项目 | 国服 | 外服 |
|------|------|------|
| 大小 | 1641 MB | 1011 MB |
| 登录SDK | 国内SDK | Google/Firebase |

---

## 六、待完成任务

### 高优先级（阻塞第二阶段）

- [ ] 完成PC端抓包分析（正在进行）
- [ ] 识别迷你世界服务器IP和端口
- [ ] 确认数据包结构
- [ ] 完成Frida脱壳（Android协议）

### 中优先级

- [ ] 实现协议转换逻辑
- [ ] 实现登录认证转换
- [ ] 实现坐标系统转换
- [ ] 实现方块ID映射

### 低优先级

- [ ] 性能优化
- [ ] 错误处理完善
- [ ] 日志系统增强

---

## 七、文件清单

### 核心模块

```
src/core/
├── __init__.py              # 模块初始化
├── proxy_server.py          # 代理服务器（✅ 框架完成）
├── protocol_translator.py   # 协议翻译器（✅ 框架完成）
└── session_manager.py       # 会话管理器（✅ 完成）
```

### 抓包工具

```
tools/pc_capture/
├── auto_capture.py          # 自动抓包工具（✅ 完成）
├── analyze_pcap.py          # 抓包分析工具（✅ 完成）
└── capture_cn_updated.bat   # 抓包启动脚本（✅ 完成）
```

---

## 八、下一阶段计划

### 第二阶段：协议实现

1. **抓包分析**（依赖当前抓包结果）
   - 识别服务器IP和端口
   - 分析数据包结构
   - 识别加密方式

2. **协议转换实现**
   - 填充ProtocolTranslator映射表
   - 实现登录认证转换
   - 实现游戏数据转换

3. **集成测试**
   - 连接测试
   - 登录测试
   - 游戏同步测试

---

## 九、技术栈

- **语言**：Python 3.11+
- **异步**：asyncio
- **网络**：socket + asyncio
- **抓包**：Wireshark/tshark
- **反编译**：jadx

---

## 十、总结

第一阶段已完成核心架构设计，包括：

✅ **代理服务器框架**：可接受MC连接并转发
✅ **协议翻译器框架**：定义了转换接口
✅ **会话管理器**：完整的会话生命周期管理
✅ **抓包工具链**：自动化抓包和分析

**当前阻塞**：等待抓包结果确认协议细节

**下一步**：抓包完成后立即填充协议转换逻辑
