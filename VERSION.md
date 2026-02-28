# MnMCP 版本记录

## v0.2.2_26w09a_Phase 1 - 基础实现阶段
**发布日期**: 2026-02-28
**状态**: ✅ 已完成

### 本阶段目标
完成基础技术债务，实现核心加密、方块映射和协议验证

### 已完成
- [x] 生产级AES加密模块（AES-128-CBC/AES-256-GCM）
- [x] 扩展方块ID映射表（29个 → 120个）
- [x] 协议数据包结构验证工具
- [x] 密码哈希算法实现（MD5双重哈希）
- [x] 阶段1测试脚本（6项测试）

### 技术债务修复详情

#### 1. 加密模块升级
- 文件: `src/crypto/aes_crypto.py`
- 改进: 替换XOR简化版为真实AES实现（cryptography库）
- 新增: AES-128-CBC（国服）和AES-256-GCM（外服）完整支持
- 新增: `MiniWorldCrypto`专用工具类

#### 2. 密码哈希模块
- 文件: `src/crypto/password_hasher.py`（新增）
- 功能: 双重MD5哈希、Token哈希、会话密钥生成
- 用途: 迷你世界登录认证

#### 3. 方块ID映射扩展
- 文件: `data/block_mappings_extended.json`（新增）
- 数量: 29个 → 120个方块映射
- 分类: basic, wood, ore, mineral, decoration, functional, redstone, plant, crop, nether, end, ocean, liquid, natural, lighting

#### 4. 协议验证工具
- 文件: `tools/protocol_validator.py`（新增）
- 功能: 数据包格式验证、PCAP分析、验证报告生成

### 已知限制（移至阶段2）
- 方块ID映射需要运行时验证（需要Root设备运行Frida）
- 协议格式基于推测，需要真实抓包数据验证
- 外服OAuth登录流程未实现

## v0.3.0_26w10a_Phase 2 - 协议实现阶段
**发布日期**: 2026-02-28  
**状态**: ✅ 已完成

### 本阶段目标
实现完整的协议翻译逻辑，完成真实登录认证流程，进行端到端连接测试

### 已完成
- [x] ACE绕过工具 (`tools/ace_bypass.py`)
- [x] Frida Hook脚本 (`tools/frida_blockid_hook.js`)
- [x] 协议翻译核心 (`src/protocol/packet_translator.py`)
- [x] 连接管理器 (`src/core/connection_manager.py`)
- [x] 阶段2测试脚本 (`test_phase2.py`)
- [x] **外服APK BlockID映射分析**
- [x] **Go语言映射文件集成** (2228个映射，ID 111已修复为stone)
- [x] **方块映射器多格式支持** (标准格式 + Go格式)

### 技术实现

#### 1. ACE绕过工具
- 修改`md5filesdata.dat`绕过文件校验
- 禁用ACE驱动加载
- 创建绕过启动器

#### 2. Frida Hook脚本
- Hook方块创建/获取函数
- 记录运行时BlockID映射
- 网络数据包拦截

#### 3. 协议翻译器
- 双向数据包翻译（MNW <-> MC）
- 位置坐标转换
- 方块ID映射
- 聊天消息翻译

#### 4. 连接管理器
- WebSocket连接管理
- 心跳机制
- 断线重连
- 多路复用

### 阶段2总结
阶段2核心协议翻译功能已完成，所有测试通过（6/6）。
主要成果包括ACE绕过工具、Frida Hook脚本、协议翻译核心、连接管理器和Go语言BlockID映射集成。

---

## v0.4.0_26w11a_Phase 3 - 连接测试与优化阶段
**发布日期**: 2026-02-28  
**状态**: 🚧 进行中

### 本阶段目标
实现端到端连接，完成性能优化，准备Beta测试

### 已完成
- [x] **Minecraft Bedrock版协议基础** (`src/protocol/mc_protocol.py`)
  - [x] VarInt编码/解码
  - [x] 数据包序列化/反序列化
  - [x] 基础数据包类型 (Text, MovePlayer, UpdateBlock)
- [x] **代理服务器v2** (`src/core/proxy_server_v2.py`)
  - [x] 异步架构
  - [x] 多客户端支持
  - [x] 会话管理
  - [x] 双向转发
- [x] **配置系统** (`src/utils/config_loader.py`, `config.yaml`)
  - [x] YAML配置文件
  - [x] 配置加载器
  - [x] 启动脚本 (`start.py`)

### 进行中
- [ ] Minecraft协议完整实现
- [ ] 端到端连接测试
- [ ] 性能优化

### 待开始
- [ ] 本地测试服务器搭建
- [ ] Docker部署支持
- [ ] 监控面板

### 详细计划
参见 `docs/Phase3_Plan.md`

---

## 历史版本

### v0.1.0 - 原型阶段
- 基础架构设计
- 协议分析文档
- 初步代码框架
