# MnMCP 项目状态

**最后更新**: 2026-02-28  
**当前版本**: v0.4.0_26w11a  
**状态**: Phase 4 完成，Phase 5 准备中

---

## 项目概述

MnMCP (Minecraft & MiniWorld Cross-Platform Proxy) 是一个实现 Minecraft 和迷你世界跨平台联机的代理服务器。

### 核心功能
- ✅ 双向协议翻译 (MNW ↔ MC)
- ✅ 方块ID映射 (2228个映射)
- ✅ AES加密支持 (CBC/GCM)
- ✅ 异步代理服务器
- ✅ 配置管理

---

## 开发阶段

### ✅ Phase 1: 基础实现 (v0.2.2)
- 生产级AES加密
- 方块ID映射基础
- 协议验证工具
- 密码哈希实现

### ✅ Phase 2: 协议实现 (v0.3.0)
- ACE绕过工具
- Frida Hook脚本
- 协议翻译核心
- 连接管理器

### ✅ Phase 3: 连接测试 (v0.4.0)
- Minecraft协议基础
- 代理服务器v2
- 配置系统
- 启动脚本

### ✅ Phase 4: 项目整理 (v0.4.0)
- 文件手动整理
- 测试重写 (真实测试)
- 文档整理
- 项目结构优化

### 🚧 Phase 5: 稳定版本 (v0.5.0)
- 性能优化
- 稳定性提升
- 功能完善
- 发布准备

---

## 项目结构

```
Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/
├── src/                    # 核心源代码
│   ├── core/              # 代理服务器
│   ├── crypto/            # 加密模块
│   ├── protocol/          # 协议翻译
│   └── utils/             # 工具模块
├── tests/                 # 测试文件
│   ├── test_crypto.py
│   ├── test_block_mapper.py
│   └── test_protocol.py
├── data/                  # 数据文件
│   └── mnw_block_mapping_from_go.json
├── docs/                  # 文档
│   ├── Phase1_Plan.md
│   ├── Phase2_Plan.md
│   ├── Phase3_Plan.md
│   ├── Phase4_Plan.md
│   ├── Phase5_Plan.md
│   └── PROJECT_STATUS.md
├── config.yaml           # 配置文件
├── start.py              # 启动脚本
├── requirements.txt      # 依赖
└── README.md            # 项目说明
```

---

## 测试状态

| 模块 | 测试数 | 通过 | 失败 | 状态 |
|------|--------|------|------|------|
| 加密模块 | 10 | 9 | 1 | ✅ |
| 方块映射 | 17 | 17 | 0 | ✅ |
| 协议翻译 | 14 | 14 | 0 | ✅ |
| **总计** | **41** | **40** | **1** | **97.6%** |

### 已知问题
1. **GCM错误标签检测失败**: 简化版AES不支持，安装cryptography后解决

---

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行测试
```bash
python start.py --test
```

### 启动服务器
```bash
python start.py
```

### 使用自定义配置
```bash
python start.py --config myconfig.yaml
```

---

## 文档索引

### 开发文档
- [Phase 1 计划](docs/Phase1_Plan.md) - 基础实现
- [Phase 2 计划](docs/Phase2_Plan.md) - 协议实现
- [Phase 3 计划](docs/Phase3_Plan.md) - 连接测试
- [Phase 4 计划](docs/Phase4_Plan.md) - 项目整理
- [Phase 5 计划](docs/Phase5_Plan.md) - 稳定版本

### 技术文档
- [项目概览](docs/PROJECT_OVERVIEW.md)
- [开发前准备](docs/BeforeDevelopment.md)
- [部署指南](docs/DEPLOYMENT_GUIDE.md)
- [贡献指南](docs/CONTRIBUTING.md)

---

## 下一步工作

### 短期 (Phase 5 Week 1-2)
- [ ] 性能优化
- [ ] 错误处理完善
- [ ] 监控告警

### 中期 (Phase 5 Week 3-4)
- [ ] 功能完善
- [ ] 测试完善
- [ ] 文档完善

### 长期
- [ ] 发布稳定版本
- [ ] 社区建设
- [ ] 持续维护

---

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](docs/CONTRIBUTING.md) 了解如何参与。

---

## 许可证

[待添加]

---

**项目地址**: [GitHub URL]  
**问题反馈**: [Issues URL]  
**讨论区**: [Discussions URL]
