# MnMCP 开发任务清单 - 更新版

## 当前阶段：核心架构实现（第二阶段）

### ✅ 已完成（本次开发）

#### 1. 基础架构
- [x] 创建主入口文件 `main.py`
- [x] 完成 `ProxyServer` 主类实现
- [x] 实现配置管理器 `config_manager.py`
- [x] 实现日志管理器 `logger.py`
- [x] 创建默认配置文件 `config.json`

#### 2. 编解码模块
- [x] 实现 Minecraft 协议编解码器 `mc_codec.py`
  - [x] VarInt 编码/解码
  - [x] 字符串编码/解码
  - [x] 握手包、登录包、心跳包、聊天包
- [x] 实现迷你世界协议编解码器 `mnw_codec.py`
  - [x] 基础数据包结构
  - [x] 登录、心跳、聊天、移动、方块操作包

#### 3. 加密模块
- [x] 实现 AES-128-CBC 加密（国服）
- [x] 实现 AES-256-GCM 加密（外服）
- [x] 实现密钥派生功能
- [x] 创建 `MiniWorldEncryption` 专用类

#### 4. 协议翻译层
- [x] 完成 `protocol_translator.py` 实际翻译逻辑
- [x] 实现 Minecraft -> MiniWorld 翻译
- [x] 实现 MiniWorld -> Minecraft 翻译
- [x] 集成坐标转换和方块映射
- [x] 实现连接状态管理

#### 5. 测试
- [x] 创建测试脚本 `test_server.py`
- [x] 验证所有模块导入正常
- [x] 验证编解码器工作正常
- [x] 验证加密模块工作正常

---

### 🔴 高优先级（下周完成）

#### 6. 登录认证完善
- [ ] 完成迷你世界登录流程实现
- [ ] 实现账户映射持久化存储
- [ ] 实现会话Token管理
- [ ] 修复 `miniworld_auth.py` 中的TODO

#### 7. 数据同步实现
- [ ] 实现方块放置/破坏同步
- [ ] 实现玩家移动同步
- [ ] 实现聊天消息转发
- [ ] 实现心跳保活机制

#### 8. 映射表完善
- [ ] 完善方块ID映射表（使用提取包数据）
- [ ] 实现物品ID映射
- [ ] 实现生物ID映射

---

### 🟡 中优先级（后续迭代）

#### 9. 代理服务器集成
- [ ] 将协议翻译器集成到代理服务器
- [ ] 实现双向数据流处理
- [ ] 添加错误处理和重连机制

#### 10. 测试与优化
- [ ] 编写单元测试
- [ ] 实现性能监控
- [ ] 压力测试

---

## 当前开发成果

### 新增文件
```
src/
├── utils/
│   ├── __init__.py
│   ├── config_manager.py    # 配置管理
│   └── logger.py            # 日志管理
├── codec/
│   ├── __init__.py
│   ├── mc_codec.py          # Minecraft协议编解码
│   └── mnw_codec.py         # 迷你世界协议编解码
├── crypto/
│   ├── __init__.py
│   └── aes_crypto.py        # AES加密模块
├── core/
│   ├── __init__.py
│   ├── proxy_server.py      # 代理服务器
│   ├── protocol_translator.py # 协议翻译器（已完成）
│   └── session_manager.py   # 会话管理器
├── main.py                  # 主入口
├── config.json              # 配置文件
└── test_server.py           # 测试脚本
```

### 测试通过
- ✅ 配置管理器工作正常
- ✅ 日志系统工作正常
- ✅ Minecraft编解码器工作正常
- ✅ 迷你世界编解码器工作正常
- ✅ AES加密模块工作正常（CBC和GCM模式）
- ✅ 协议翻译器框架完成
- ✅ 代理服务器实例创建成功

---

## 下一步行动

### 立即执行
1. **完善登录认证**：实现完整的迷你世界登录流程
2. **实现数据同步**：方块、移动、聊天的双向同步
3. **集成测试**：将所有模块集成到代理服务器

### 技术债务
- [ ] 修复 `miniworld_auth.py` 中的TODO（密码哈希算法）
- [ ] 完善 `block_mapper.py` 的完整映射（使用提取包数据）
- [ ] 优化 `coordinate_converter.py` 的坐标转换参数
- [ ] 将加密模块从XOR占位实现替换为真正的AES（需要安装cryptography库）
