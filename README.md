# Minecraft and MiniWorld Cross-Platform CrossPlay (MnMCP)

**版本**: 26w14a_dev_26.1.1  
**状态**: Phase 1 - 基础框架建立中

---

## 项目简介

MnMCP 是一个跨平台的 Minecraft 与迷你世界互通项目，允许 Minecraft 玩家和迷你世界玩家在同一个世界中游戏。

### 核心功能
- ✅ 协议转换 (Minecraft Bedrock ↔ 迷你世界)
- ✅ 加密通信 (ECDH + AES-GCM)
- ✅ 方块/实体/物品映射
- ✅ 玩家状态同步
- ✅ 聊天消息互通

---

## 架构

```
src/
├── protocol/      # 协议层 (iLink/mmtls/RakNet)
├── crypto/        # 加密层 (ECDH/AES-GCM)
├── network/       # 网络层 (UDP/TCP)
├── mapping/       # 映射层 (方块/实体/物品)
└── utils/         # 工具层
```

---

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行测试
```bash
pytest tests/
```

---

## 开发进度

- [x] Phase 1: 基础框架
- [ ] Phase 2: 加密层
- [ ] Phase 3: 网络层
- [ ] Phase 4: 业务层
- [ ] Phase 5: 客户端

---

## 贡献指南

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 许可证

MIT License

---

## 联系方式

- 项目主页: https://github.com/StarsailsClover/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay
- 问题反馈: https://github.com/StarsailsClover/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/issues
