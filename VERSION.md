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

### 下一阶段（阶段2）v0.3.0_26w10a
**目标**: 实现完整协议翻译逻辑，完成真实登录认证流程

**关键任务**:
1. ✅ 修正方块ID映射（基于EZ整理的ID分类）
2. 🔍 ACE反作弊绕过验证
3. 🚧 协议翻译核心实现
4. 🚧 登录认证流程
5. 🚧 端到端测试

**详细计划**: 参见 `docs/Phase2_Plan.md`

---

## 历史版本

### v0.1.0 - 原型阶段
- 基础架构设计
- 协议分析文档
- 初步代码框架
